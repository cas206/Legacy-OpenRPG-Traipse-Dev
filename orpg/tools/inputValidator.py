# Copyright (C) 2000-2001 The OpenRPG Project
#
#        openrpg-dev@lists.sourceforge.net
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
# File: inputValidator.py
# Author: Greg Copeland
# Maintainer:
#
# Description: Contains simple input validators to help reduce the amount of
# user input generated text.
#

__version__ = "$Id: inputValidator.py,v Traipse 'Ornery-Orc' prof.ebral Exp $"


##
## Module Loading
##
from orpg.orpg_wx import *
import string


##
## Text Only input (no numbers allowed)
##
class TextOnlyValidator(wx.PyValidator):
    def __init__( self ):
        wx.PyValidator.__init__( self )
        self.Bind(wx.EVT_CHAR, self.onChar)



    def Clone( self ):
        return TextOnlyValidator()



    def Validate( self, win ):
        tc = self.GetWindow()
        val = tc.GetValue()

        retVal = True
        for x in val:
            if x not in string.letters:
                retVal = False
                break

        return retVal



    def onChar( self, event ):
        key = event.GetKeyCode()
        if key < wx.WXK_SPACE or key == wx.WXK_DELETE or key > 255:
            event.Skip()

        elif chr(key) in string.letters:
            event.Skip()

        else:
            if not wxValidator_IsSilent():
                wxBell()

        # Returning without calling even.  Skip eats the event before it
        # gets to the text control
        return



##
## Number Only input (no text allowed)
##
class NumberOnlyValidator(wx.PyValidator):
    def __init__( self ):
        wx.PyValidator.__init__( self )
        self.Bind(wx.EVT_CHAR, self.onChar)



    def Clone( self ):
        return NumberOnlyValidator()



    def Validate( self, win ):
        tc = self.GetWindow()
        val = tc.GetValue()

        retVal = True
        for x in val:
            if x not in string.digits:
                retVal = False
                break

        return retVal



    def onChar( self, event ):
        key = event.GetKeyCode()
        if key < wx.WXK_SPACE or key == wx.WXK_DELETE or key > 255:
            event.Skip()

        elif chr(key) in string.digits:
            event.Skip()

        else:
            if not wxValidator_IsSilent():
                wxBell()

        # Returning without calling even.  Skip eats the event before it
        # gets to the text control
        return






##
## Math Only input (no text allowed, only numbers of math symbols)
##
class MathOnlyValidator(wx.PyValidator):
    def __init__( self ):
        wx.PyValidator.__init__( self )

        # Build it as part of the class and not per Validate() call
        self.allowedInput = "0123456789()*/+-<>"
        self.Bind(wx.EVT_CHAR, self.onChar)



    def Clone( self ):
        return MathOnlyValidator()



    def Validate( self, win ):
        tc = self.GetWindow()
        val = tc.GetValue()

        retVal = True
        for x in val:
            if x not in self.allowedInput:
                retVal = False
                break

        return retVal



    def onChar( self, event ):
        key = event.GetKeyCode()
        if key < wx.WXK_SPACE or key == wx.WXK_DELETE or key > 255:
            event.Skip()

        elif chr(key) in self.allowedInput:
            event.Skip()

        else:
            if not wxValidator_IsSilent():
                wxBell()

        # Returning without calling even.  Skip eats the event before it
        # gets to the text control
        return






##
## Text and number input but DO NOT allow ANY HTML type input (no numbers allowed)
##
class NoHTMLValidator(wx.PyValidator):
    def __init__( self ):
        wx.PyValidator.__init__( self )

        # Build it as part of the class and not per Validate() call
        self.allowedInput = " 1234567890!@#$%^&*()_-+=`~abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ,[]{}|;:'\",./?\\"
        self.Bind(wx.EVT_CHAR, self.onChar)



    def Clone( self ):
        return NoHTMLValidator()



    def Validate( self, win ):
        tc = self.GetWindow()
        val = tc.GetValue()

        retVal = True
        for x in val:
            if x not in self.allowedInput:
                retVal = False
                break

        return retVal



    def onChar( self, event ):
        key = event.GetKeyCode()
        if key < wx.WXK_SPACE or key == wx.WXK_DELETE or key > 255:
            event.Skip()

        elif chr(key) in self.allowedInput:
            event.Skip()

        else:
            if not wxValidator_IsSilent():
                wxBell()

        # Returning without calling even.  Skip eats the event before it
        # gets to the text control
        return
