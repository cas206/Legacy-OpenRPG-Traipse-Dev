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
import wx #wx.SystemSettings.GetMetric(wx.SYS_VSCROLL_X)
from wx.lib.expando import ExpandoTextCtrl
from orpg.tools.orpg_log import logger, debug

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


class LetterTreeClass(object):

    def __init__(self, singletonKey):
        if not isinstance(singletonKey, _SingletonKey):
            raise invalid_argument(_("Use LetterTree() to get access to singleton"))

        self.rootNode = Letter("",None)                
        self.rootNode.children = {} 

    def updateMostCommon(self, target):
        prev = target.parentNode
        while prev:
            if prev.mostCommon is None:
                prev.mostCommon = target
            else:
                if target.priority > prev.mostCommon.priority:
                    prev.mostCommon = target
            prev = prev.parentNode

    def setWord(self,wordText,priority = 1,sumFlag = 0):
        cur = self.rootNode                     
        for ch in wordText:  
            if cur.children.has_key(ch):
                cur = cur.children[ch] 
            else:  
                newLetter = Letter(ch,cur)
                if cur is self.rootNode:
                    newLetter.parentNode = None
                cur.children[ch] = newLetter
                cur = newLetter  
        if sumFlag: cur.priority += priority
        else: cur.priority = priority 
        self.updateMostCommon(cur) 

    def addWord(self,wordText):
        self.setWord(wordText,priority = 1)

    def incWord(self,wordText):
        self.setWord(wordText,priority = 1, sumFlag = 1)

    def setWordPriority(self,wordText,priority):
        self.setWord(wordText,priority = priority)


    def findWordNode(self,wordText):  
        cur = self.rootNode 
        for ch in wordText: 
            if cur.children.has_key(ch):
                cur = cur.children[ch]
            else: return None  
        return cur  

    def findWordPriority(self,wordText):

        cur = self.findWordNode(wordText) 
        if cur: return cur.priority
        else: return 0 

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

    def getPrediction(self,k,cur):

        if cur.children.has_key(k) : 
            cur = cur.children[k] 
            backtrace = cur.mostCommon
            returnText = ''
            while cur is not backtrace: 
                returnText = backtrace.asciiChar + returnText
                backtrace = backtrace.parentNode 
            return returnText 
        else: 
            return "" 


class _SingletonKey(object):
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '_inst'):
            cls._inst = super(_SingletonKey, cls).__new__(cls, *args, **kwargs)
        return cls._inst

__key = _SingletonKey()
LetterTree = LetterTreeClass(__key)


class predTextCtrl(ExpandoTextCtrl):

    def __init__(self, parent, id = -1, value = "", size = (30,30), style = 0, name = "text", keyHook = None, validator=None):
        if validator:
            ExpandoTextCtrl.__init__(self, parent, id=id, value=value, size=size, style=style, name=name, validator=validator )
        else:
            ExpandoTextCtrl.__init__(self, parent, id=id, value=value, size=size, style=style, name=name)


        self.tree = LetterTree 
        self.parent = parent  
        self.cur = self.tree.rootNode  
        self.keyHook = keyHook  
        ExpandoTextCtrl._wrapLine = self._wrapLine
        

    def _wrapLine(self, line, dc, width):
        pte = dc.GetPartialTextExtents(line)
        width -= wx.SystemSettings.GetMetric(wx.SYS_VSCROLL_X)
        idx = 0
        start = 0
        count = 0
        spc = -1
        while idx < len(pte):
            if line[idx] == ' ': spc = idx
            if pte[idx] - start > width:
                count += 1
                if spc != -1:
                    idx = spc + 1
                    spc = -1
                start = pte[idx]
            else:
                idx += 1
        return count

    def findWord(self, insert, st):
        begin = 0
        for offset in range(insert - 1):
            if st[-(offset + 2)] not in string.ascii_letters:
                begin = insert - (offset + 1)
                break
        return st[begin:insert]

    def OnChar(self,event):

        if(self.keyHook):
            if self.keyHook(event) == 1: 
                self.parent.OnChar(event)
                return
        asciiKey = ""
        if (event.GetKeyCode() < 256) and (event.GetKeyCode() > 19):
            asciiKey = chr(event.GetKeyCode())
        if asciiKey == "":  
            if  event.GetKeyCode() == wx.WXK_TAB: 
                fromPos = toPos = 0 
                (fromPos,toPos) = self.GetSelection()
                if (toPos - fromPos) == 0:  
                    self.parent.OnChar(event)
                    return
                else:   
                    self.SetInsertionPoint(toPos)  
                    self.SetSelection(toPos,toPos) 
                    return

            elif event.GetKeyCode() == wx.WXK_RETURN: 
                st = self.GetValue() 
                newSt = "" 
                (startSel,endSel) = self.GetSelection() 
                self.Remove( startSel, endSel )
                st = string.strip( self.GetValue() )
                for ch in st:
                    if ch not in string.ascii_letters:
                        newSt += " "
                    else:
                        newSt += ch
                for aWord in string.split(newSt):
                    self.tree.incWord(string.lower(aWord))
                self.parent.OnChar(event)
                return

            elif event.GetKeyCode() == wx.WXK_RIGHT:
                (startSel,endSel) = self.GetSelection()
                self.SetInsertionPoint(endSel)
                self.parent.OnChar(event)
                return

            elif event.GetKeyCode() == wx.WXK_LEFT:
                (startSel,endSel) = self.GetSelection()
                self.SetInsertionPoint(startSel)
                self.parent.OnChar(event)
                return
            else:

                self.parent.OnChar(event) 
                return
        elif asciiKey in string.ascii_letters:
            (startSel,endSel) = self.GetSelection() 
            st = self.GetValue() 
            front = st[:startSel]
            back = st[endSel:]  
            st = front + asciiKey + back
            insert = startSel + 1   
            curWord = ""   
            if (len(back) == 0) or (back[0] not in string.ascii_letters):

                curWord = self.findWord(insert,front + asciiKey) 
            else: 
                self.parent.OnChar(event)
                return

            if curWord == "":  
                self.parent.OnChar(event)
                return

            self.cur = self.tree.findWordNode(string.lower(curWord[:-1])) 
            if self.cur is None:
                self.parent.OnChar(event)  
                return
            predictText = self.tree.getPrediction(string.lower(asciiKey),self.cur) 

            if predictText == "":
                self.parent.OnChar(event)  
                return
            front = st[:insert] 
            back = st[insert:]

            st = front + predictText + back 
            self.SetValue(st)   
            self.SetInsertionPoint(insert) 
            self.SetSelection(insert,insert+len(predictText))
            return   
        else:

            self.parent.OnChar(event) 
            return

