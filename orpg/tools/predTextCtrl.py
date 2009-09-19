# Copyright (C) 2001 The OpenRPG Project
#
#   openrpg-dev@lists.sourceforge.net
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
# --
#
# File: predTextCtrl.py
# Author: Andrew Bennett
# Maintainer: Andrew Bennett
# Version:  $id:$
#
# Description: This file contains an extension to the wxPython wx.TextCtrl that provides predictive word completion
#              based on a word file loaded at instantiation.  Also, it learns new words as you type, dynamically
#              adjusting a weight for each word based on how often you type it.
#

##
## Module Loading
##

import string
from orpg.orpg_windows import *
from wx.lib.expando import ExpandoTextCtrl
from orpg.tools.orpg_log import logger

#  This line added to test CVS commit

##
## Class Definitions
##

# This class implements a tree node that represents a letter
#
# Defines:
#   __init__(self,filename)
#
class Letter:
    def __init__(self,asciiCharIn,parentNodeIn):
        self.asciiChar =  asciiCharIn           # should be an ASCII char
        self.parentNode = parentNodeIn          # should be ref to a class Letter
        self.priority = 0                       # should be an int
        self.mostCommon = self                  # should be a ref to a class Letter
        self.children = {}                      # should be a ref to a dictionary of class Letter

    def __str__(self):
        return self.asciiChar


# This class implements the tree structure to hold the words
#
# Defines:
#    __init__(self,filename)
#    updateMostCommon(self,target)
#    setWord(self,wordText,priority,sumFlag)
#    addWord(self,wordText)
#    setWord(self,wordText)
#    setWordPriority(self,wordText,priority)
#    findWordNode(self,wordText) returns class Letter
#    findWordPriority(self,wordText) returns int
#    getPredition(self,k,cur) returns string
class LetterTreeClass(object):

    # Initialization subroutine.
    #
    # self : instance of self
    # filename : name of word file to use
    #
    # returns None
    #
    # Purpose:  Constructor for LetterTree.  Basically, it initializes itself with a word file, if present.
    def __init__(self, singletonKey):
        if not isinstance(singletonKey, _SingletonKey):
            raise invalid_argument(_("Use LetterTree() to get access to singleton"))

        self.rootNode = Letter("",None)                # rootNode is a class Letter
        self.rootNode.children = {}                    # initialize the children list


    # updateMostCommon subroutine.
    #
    # self : instance of self
    # target : class Letter that was updated
    #
    # Returns None
    #
    # Purpose:  Updates all of the parent nodes of the target, such that their mostCommon member
    #           points to the proper class Letter, based on the newly updated priorities.
    def updateMostCommon(self, target):
                                                # cur is a class Letter
        prev = target.parentNode                # prev is a class Letter
        while prev:
            if prev.mostCommon is None:
                prev.mostCommon = target
            else:
                if target.priority > prev.mostCommon.priority:
                    prev.mostCommon = target
            prev = prev.parentNode



    # setWord subroutine.
    #
    # self : instance of self
    # wordText : string representing word to add
    # priority : integer priority to set the word
    # sumFlag : if True, add the priority to the existing, else assign the priority
    #
    # Returns:  None
    #
    # Purpose:  Sets or increments the priority of a word, adding the word if necessary
    def setWord(self,wordText,priority = 1,sumFlag = 0):

        cur = self.rootNode                     # start from the root

        for ch in wordText:                     # for each character in the word
            if cur.children.has_key(ch):        # check to see if we've found a new word

                cur = cur.children[ch]            # if we haven't found a new word, move to the next letter and try again

            else:                               # in this clause, we're creating a new branch, as the word is new
                newLetter = Letter(ch,cur)        # create a new class Letter using this ascii code and the current letter as a parent

                if cur is self.rootNode:          # special case:  Others expect the top level letters to point to None, not self.rootNode
                    newLetter.parentNode = None

                cur.children[ch] = newLetter      #  add the new letter to the list of children of the current letter
                cur = newLetter                   #  make the new letter the current one for the next time through

        #  at this point, cur is pointing to the last letter of either a new or existing word.

        if sumFlag:                             #  if the caller wants to add to the existing (0 if new)
            cur.priority += priority
        else:                                   #  else, the set the priority directly
            cur.priority = priority

        self.updateMostCommon(cur)              # this will run back through the tree to fix up the mostCommon members


    # addWord subroutine.
    #
    # self : instance of self
    # wordText : string representing word to add
    #
    # Returns:  None
    #
    # Purpose:  Convenience method that wraps setWord.  Used to add words known not to exist.
    def addWord(self,wordText):
        self.setWord(wordText,priority = 1)


    # incWord subroutine.
    #
    # self : instance of self
    # wordText : string representing word to add
    #
    # Returns:  None
    #
    # Purpose:  Convenience method that wraps setWord.  Used to increment the priority of existing words and add new words.
    # Note:     Generally, this method can be used instead of addWord.
    def incWord(self,wordText):
        self.setWord(wordText,priority = 1, sumFlag = 1)


    # setWordPriority subroutine.
    #
    # self : instance of self
    # wordText : string representing word to add
    # priority:  int that is the new priority
    #
    # Returns:  None
    #
    # Purpose:  Convenience method that wraps setWord.  Sets existing words to priority or adds new words with priority = priority
    def setWordPriority(self,wordText,priority):
        self.setWord(wordText,priority = priority)


    # findWordNode subroutine.
    #
    # self : instance of self
    # wordText : string representing word to add
    #
    # Returns:  class Letter or None if word isn't found.
    #
    # Purpose:  Given a word, it returns the class Letter node that corresponds to the word.  Used mostly in prep for a call to
    #           getPrediction()
    def findWordNode(self,wordText):         #returns class Letter that represents the last letter in the word

        cur = self.rootNode                  # start at the root

        for ch in wordText:                  # move through each letter in the word
            if cur.children.has_key(ch):     # if the next letter exists, make cur equal that letter and loop
                cur = cur.children[ch]
            else:
                return None                  # return None if letter not found

        return cur                           # return cur, as this points to the last letter if we got this far


    # findWordPriority subroutine.
    #
    # self : instance of self
    # wordText : string representing word to add
    #
    # Returns:  Int representing the word's priority or 0 if not found.
    #
    # Purpose:  Returns the priority of the given word
    def findWordPriority(self,wordText):

        cur = self.findWordNode(wordText)    #  find the class Letter node that corresponds to this word
        if cur:
            return cur.priority              #  if it was found, return it's priority
        else:
            return 0                         #  else, return 0, meaning word not found


    def printTree(self, current=None):
        letters = []
        if current is None:
            current = self.rootNode

        for l, letter in current.children.iteritems():
            letters.append(str(letter))
            if letter.children != {}:
                m = self.printTree(letter)
                letters.append(m)

        return letters



    # getPrediction subroutine.
    #
    # self : instance of self
    # k : ASCII char that was typed
    # cur : class Letter that points to the current node in LetterTree
    #
    # Returns:  The predicted text or "" if none found
    #
    # Purpose:  This is the meat and potatoes of data structure.  It takes the "current" Letter node and the next key typed
    #           and returns it's guess of the rest of the word, based on the highest priority letter in the rest of the branch.
    def getPrediction(self,k,cur):

        if cur.children.has_key(k) :                            #  check to see if the key typed is a sub branch
                                                                #  If so, make a prediction.  Otherwise, do the else at the bottom of
                                                                #  the method (see below).

            cur = cur.children[k]                               #  set the cur to the typed key's class Letter in the sub-branch

            backtrace = cur.mostCommon                          # backtrace is a class Letter.  It's used as a placeholder to back trace
                                                                # from the last letter of the mostCommon word in the
                                                                # sub-tree up through the tree until we meet ourself at cur.  We'll
                                                                # build the guess text this way

            returnText = ""                                     # returnText is a string.  This will act as a buffer to hold the string
                                                                # we build.

            while cur is not backtrace:                         #  Here's the loop.  We loop until we've snaked our way back to cur

                returnText = backtrace.asciiChar + returnText   #  Create a new string that is the character at backtrace + everything
                                                                #  so far.  So, for "tion"  we'll build "n","on","ion","tion" as we ..

                backtrace = backtrace.parentNode                #  ... climb back towards cur

            return returnText                                   #  And, having reached here, we've met up with cur, and returnText holds
                                                                #  the string we built.  Return it.

        else:                                                   #  This is the else to the original if.
                                                                #  If the letter typed isn't in a sub branch, then
                                                                #  the letter being typed isn't in our tree, so
            return ""                                           #  return the empty string


#  End of class LetterTree!



class _SingletonKey(object):
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '_inst'):
            cls._inst = super(_SingletonKey, cls).__new__(cls, *args, **kwargs)
        return cls._inst

__key = _SingletonKey()
LetterTree = LetterTreeClass(__key)

# This class extends wx.TextCtrl
#
# Extends:  wx.TextCtrl
#
# Overrides:
#    wx.TextCtrl.__init__(self,parent,id,value,size,style,name)
#    wx.TextCtrl.OnChar(self,Event)
#
# Defines:
#    findWord(self,insert,st)
class predTextCtrl(ExpandoTextCtrl):

    # Initialization subroutine.
    #
    # self : instance of self
    # parent:  reference to parent window (wxWindow, me-thinks)
    # id:      new Window Id, default to -1 to create new (I think: see docs for wxPython)
    # value:   String that is the initial value the control holds, defaulting to ""
    # size:    defaults to wx.DefaultSize
    # style:   defaults to 0
    # name:    defaults to "text"
    # keyHook: must be a function pointer that takes self and a GetKeyCode object
    # validator: defaults to None
    #
    # Note:  These parameters are essentially just passed back to the native wx.TextCtrl.
    #        I basically just included (stole) enough of them from chatutils.py to make
    #        it work.  Known missing args are pos and validator, which aren't used by
    #        chatutils.py.
    #
    # Returns:  None
    #
    # Purpose:  Constructor for predTextCtrl.  Calls wx.TextCtrl.__init__ to get default init
    #           behavior and then inits a LetterTree and captures the parent for later use in
    #           passing events up the chain.
    def __init__(self, parent, id = -1, value = "" , size = wx.DefaultSize, style = 0, name = "text",keyHook = None, validator=None):

        #  Call super() for default behavior
        if validator:
            ExpandoTextCtrl.__init__(self, parent, id=id, value=value, size=size, style=style, name=name, validator=validator )
        else:
            ExpandoTextCtrl.__init__(self, parent, id=id, value=value, size=size, style=style, name=name)

        self.tree = LetterTree      #  Instantiate a new LetterTree.
        #  TODO:  make name of word file an argument.




        self.parent = parent                               #  Save parent for later use in passing KeyEvents

        self.cur = self.tree.rootNode                      # self.cur is a short cut placeholder for typing consecutive chars
                                                           # It may be vestigal

        self.keyHook = keyHook                             #  Save the keyHook passed in


    # findWord subroutine.
    #
    # self :  instance of self
    # insert: index of last char in st
    # st :    string from insert to the left
    #
    # Note:  This implementation is about the third one for this method.  Originally,
    #        st was an arbitrary string and insert was the point within
    #        this string to begin looking left.  Since, I finally got it
    #        to work right as it is around 2 in the morning, I'm not touching it, for now.
    #
    # Returns:  String that is the word or "" if none found.  This generally doesn't
    #           happen, as st usually ends in a letter, which will be returned.
    #
    # Purpose:  This function is generally used to figure out the beginning of the
    #           current word being typed, for later use in a LetterTree.getPrediction()
    def findWord(self,insert,st):

    #  Good luck reading this one.  Basically, I started out with an idea, and fiddled with the
    #  constants as best I could until it worked.  It's not a piece of work of which I'm too
    #  proud.  Basically, it's intent is to check each character to the left until it finds one
    #  that isn't a letter.  If it finds such a character, it stops and returns the slice
    #  from that point to insert.  Otherwise, it returns the whole thing, due to begin being
    #  initialized to 0

        begin = 0
        for offset in range(insert - 1):
            if st[-(offset + 2)] not in string.letters:
                begin = insert - (offset + 1)
                break
        return st[begin:insert]


    # OnChar subroutine.
    #
    # self :  instance of self
    # event:  a GetKeyCode object
    #
    # Returns:  None
    #
    # Purpose:  This function is the key event handler for predTextCtrl.  It handles what it
    #           needs to and passes the event on to it's parent's OnChar method.
    def OnChar(self,event):

        #  Before we do anything, call the keyHook handler, if not None
        #    This is currently used to implement the typing/not_typing messages in a manner that
        #         doesn't place the code here.  Maybe I should reconsider that.  :)
        if(self.keyHook):
            if self.keyHook(event) == 1:   #  if the passed in keyHook routine returns a one, it wants no predictive behavior
                self.parent.OnChar(event)
                return



        #  This bit converts the GetKeyCode() return (int) to a char if it's in a certain range
        asciiKey = ""
        if (event.GetKeyCode() < 256) and (event.GetKeyCode() > 19):
            asciiKey = chr(event.GetKeyCode())


        if asciiKey == "":                                 #  If we didn't convert it to a char, then process based on the int GetKeyCodes

            if  event.GetKeyCode() == wx.WXK_TAB:                #  We want to hook tabs to allow the user to signify acceptance of a
                                                           #  predicted word.
                #  Handle Tab key

                fromPos = toPos = 0                        # get the current selection range
                (fromPos,toPos) = self.GetSelection()

                if (toPos - fromPos) == 0:                 # if there is no selection, pass tab on
                    self.parent.OnChar(event)
                    return

                else:                                      #  This means at least one char is selected

                    self.SetInsertionPoint(toPos)          #  move the insertion point to the end of the selection
                    self.SetSelection(toPos,toPos)         #  and set the selection to no chars
                                                           #  The prediction, if any, had been inserted into the text earlier, so
                                                           #  moving the insertion point to the spot directly afterwards is
                                                           #  equivalent to acceptance.  Without this, the next typed key would
                                                           #  clobber the prediction.

                    return                                 #  Don't pass tab on in this case
            elif event.GetKeyCode() == wx.WXK_RETURN and event.ShiftDown():
                logger.exception('Shift + Enter Not completed, 439, predtextCtrl', True)
                st = self.GetValue()
                st += '<br />'
                return


            elif event.GetKeyCode() == wx.WXK_RETURN:            #  We want to hook returns, so that we can update the word list

                st = self.GetValue()                       #  Grab the text from the control
                newSt = ""                                 #  Init a buffer

                #  This block of code, by popular demand, changes the behavior of the control to ignore any prediction that
                #    hasn't been "accepted" when the enter key is struck.
                (startSel,endSel) = self.GetSelection()                 #  get the curren selection

                #
                # Start update
                # Changed the following to allow for more friendly behavior in
                # a multilined predTextCtrl.
                #
                # front = st[:startSel]                                   #  Slice off the text to the front of where we are
                # back = st[endSel:]                                      #  Slice off the text to the end from where we are
                # st = front + back                          #  This expression creates a string that get rid of any selected text.
                # self.SetValue(st)

                self.Remove( startSel, endSel )
                st = string.strip( self.GetValue() )
                #
                # End update
                #

                #  this loop will walk through every character in st and add it to
                #  newSt if it's a letter.  If it's not a letter, (e.g. a comma or
                #  hyphen) a space is added to newSt in it's place.
                for ch in st:
                    if ch not in string.letters:
                        newSt += " "
                    else:
                        newSt += ch

                #  Now that we've got a string of just letter sequences (words) and spaces
                #  split it and to a LetterTree.incWord on the lowercase version of it.
                #  Reminder:  incWord will increment the priority of existing words and add
                #  new ones
                for aWord in string.split(newSt):
                    self.tree.incWord(string.lower(aWord))

                self.parent.OnChar(event)                   #  Now that all of the words are added, pass the event and return
                return

            #  We want to capture the right arrow key to fix a slight UI bug that occurs when one right arrows
            #  out of a selection.  I set the InsertionPoint to the beginning of the selection.  When the default
            #  right arrow event occurs, the selection goes away, but the cursor is in an unexpected location.
            #  This snippet fixes this behavior and then passes on the event.
            elif event.GetKeyCode() == wx.WXK_RIGHT:
                (startSel,endSel) = self.GetSelection()
                self.SetInsertionPoint(endSel)
                self.parent.OnChar(event)
                return

            #  Ditto as wx.WXK_RIGHT, but for completeness sake
            elif event.GetKeyCode() == wx.WXK_LEFT:
                (startSel,endSel) = self.GetSelection()
                self.SetInsertionPoint(startSel)
                self.parent.OnChar(event)
                return


            else:
                #   Handle any other non-ascii events by calling parent's OnChar()
                self.parent.OnChar(event)     #Call super.OnChar to get default behavior
                return


        elif asciiKey in string.letters:
           #  This is the real meat and potatoes of predTextCtrl.  This is where most of the
           #  wx.TextCtrl logic is changed.

            (startSel,endSel) = self.GetSelection()                 #  get the curren selection
            st = self.GetValue()                                    #  and the text in the control
            front = st[:startSel]                                   #  Slice off the text to the front of where we are
            back = st[endSel:]                                      #  Slice off the text to the end from where we are

            st = front + asciiKey + back                            #  This expression creates a string that will insert the
                                                                    #  typed character (asciiKey is generated at the
                                                                    #  beginning of OnChar()) into the text.  If there
                                                                    #  was text selected, that text will not be part
                                                                    #  of the new string, due to the way front and back
                                                                    #  were sliced.

            insert = startSel + 1                                   #  creates an int that denotes where the new InsertionPoint
                                                                    #  should be.

            curWord = ""                                            #  Assume there's a problem with finding the curWord

            if (len(back) == 0) or (back[0] not in string.letters): #  We should only insert a prediction if we are typing
                                                                    #  at the end of a word, not in the middle.  There are
                                                                    #  three cases: we are typing at the end of the string or
                                                                    #  we are typing in the middle of the string and the next
                                                                    #  char is NOT a letter or we are typing in the middle of the
                                                                    #  string and the next char IS a letter.  Only the former two
                                                                    #  cases denote that we should make a prediction
                                                                    #  Note:  The order of the two logical clauses here is important!
                                                                    #         If len(back) == 0, then the expression back[0] will
                                                                    #         blow up with an out of bounds array subscript.  Luckily
                                                                    #         the or operator is a short-circuit operator and in this
                                                                    #         case will only evaluate back[0] if len(back) != 0, in
                                                                    #         which we're safely in bounds.

                curWord = self.findWord(insert,front + asciiKey)    #  Now that we know we're supposed to make a prediction,
                                                                    #  let's find what word root to use in our prediction.
                                                                    #  Note:  This is using the confusing findWord method.  I
                                                                    #         send it insert and the text from the beginning
                                                                    #         of the text through the key just entered.  This is
                                                                    #         NOT the original usage, but it does work.  See
                                                                    #         findWord() for more details.

            else:                                                   #  Here, we've found we're in the middle of a word, so we're
                                                                    #  going to call the parent's event handler.
                self.parent.OnChar(event)
                return

            if curWord == "":                                       #  Here, we do a quick check to make sure we have a good root
                                                                    #  word.  If not, allow the default thing to happen.  Of course,
                                                                    #  now that I'm documenting this, it occurs to me to wonder why
                                                                    #  I didn't do the same thing I just talked about.  Hmmmmmm.

                self.parent.OnChar(event)                           # we're done here
                return

            self.cur = self.tree.findWordNode(string.lower(curWord[:-1]))  #  Still with me?  We're almost done.  At this point, we
                                                                           #  need to convert our word string to a Letter node,
                                                                           #  because that's what getPrediction expects.  Notice
                                                                           #  that we're feeding in the string with the last
                                                                           #  char sliced off.  For developmentally historical
                                                                           #  reasons, getPrediction wants the node just before
                                                                           #  the typed character and the typed char separately.


            if self.cur is None:
                self.parent.OnChar(event)                                  # if there's no word or no match, we're done
                return


            # get the prediction
            predictText = self.tree.getPrediction(string.lower(asciiKey),self.cur)     #  This is the big prediction, as noted above
                                                                                       #  Note the use of string.lower() because we
                                                                                       #  keep the word list in all lower case,but we
                                                                                       #  want to be able to match any capitalization

            if predictText == "":
                self.parent.OnChar(event)                                              # if there's no prediction, we're done
                return

            #  And now for the big finale.  We're going to take the string st
            #  we created earlier and insert the prediction right after the
            #  newly typed character.
            front = st[:insert]                                 #  Grab a new front from st
            back = st[insert:]                                  #  Grab a new back

            st = front + predictText + back                     #  Insert the prediction

            self.SetValue(st)                                   #  Now, overwrite the controls text with the new text
            self.SetInsertionPoint(insert)                      #  Set the proper insertion point, directly behind the
                                                                #  newly typed character and directly in front of the
                                                                #  predicted text.

            self.SetSelection(insert,insert+len(predictText))   #  Very important!  Set the selection to encompass the predicted
                                                                #  text.  This way, the user can ignore the prediction by simply
                                                                #  continuing to type.  Remember, if the user wants the prediction
                                                                #  s/he must strike the tab key at this point.  Of course, one could
                                                                #  just use the right arrow key as well, but that's not as easy to
                                                                #  reach.

            return                                              #  Done!  Do NOT pass the event on at this point, because it's all done.


        else:
            #   Handle every other non-letter ascii (e.g. semicolon) by passing the event on.
            self.parent.OnChar(event)     #Call super.OnChar to get default behavior
            return

#  End of class predTextCtrl!
