# Copyright (C) 2000-2001 The OpenRPG Project
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
# File: toolBars.py
# Author: Greg Copeland
# Maintainer:
#
# Description: Contains all of the toolbars used in the application.
#
#

__version__ = "$Id: toolBars.py,v Traipse 'Ornery-Orc' prof.ebral Exp $"


##
## Module Loading
##
from inputValidator import *
import string
from orpg.dirpath import dir_struct

# DICE stuff
TB_IDC_D4 = wx.NewId()
TB_IDC_D6 = wx.NewId()
TB_IDC_D8 = wx.NewId()
TB_IDC_D10 = wx.NewId()
TB_IDC_D12 = wx.NewId()
TB_IDC_D20 = wx.NewId()
TB_IDC_D100 = wx.NewId()
TB_IDC_NUMDICE = wx.NewId()
TB_IDC_MODS = wx.NewId()

# MAP stuff
TB_MAP_MODE = wx.NewId()
# Caution: the use of wxFRAME_TOOL_WINDOW screws up the window on GTK.  Please don't use!!!

class MapToolBar(wx.Panel):
    """This is where all of the map related tools belong for quick reference."""
    def __init__( self, parent, id=-1, title="Map Tool Bar", size= wx.Size(300, 45), callBack=None ):
        wx.Panel.__init__(self, parent, id, size=size)
        self.callback = callBack
        self.mapmode = 1
        self.modeicons = [dir_struct["icon"]+"move.gif",
            dir_struct["icon"]+"draw.gif",
            dir_struct["icon"]+"tape.gif"]
        # Make a sizer for everything to belong to
        self.sizer = wx.BoxSizer( wx.HORIZONTAL )
        bm = wx.Image(dir_struct["icon"]+"move.gif", wx.BITMAP_TYPE_GIF).ConvertToBitmap()
        self.butt = wx.BitmapButton( self, TB_MAP_MODE, bm )
        self.sizer.Add( self.butt,0, wx.ALIGN_CENTER )
        self.Bind(wx.EVT_BUTTON, self.onToolBarClick, id=TB_MAP_MODE)
        # Build the toolbar now
        # Stubbed, but nothing here yet!
        # Now, attach the sizer to the panel and tell it to do it's magic
        self.SetSizer(self.sizer)
        self.SetAutoLayout(True)
        self.Fit()

    def onToolBarClick(self,evt):
        data = ""
        id = evt.GetId()
        data = ""
        mode = 1
        if id == TB_MAP_MODE:
            mode = 1
            self.mapmode +=1
            if self.mapmode >3: self.mapmode = 1
            bm = wx.Image(self.modeicons[self.mapmode-1],wx.BITMAP_TYPE_GIF).ConvertToBitmap()
            self.butt= wx.BitmapButton(self,TB_MAP_MODE,bm)
            data = self.mapmode
        if self.callback != None: self.callback(mode,data)

class DiceToolBar(wx.Panel):
    """This is where all of the dice related tools belong for quick reference."""
    def __init__( self, parent, id=-1, title="Dice Tool Bar", size=wx.Size(300, 45), callBack=None ):
        wx.Panel.__init__(self, parent, id, size=size)
        # Save our post callback
        self.callBack = callBack
        # Make a sizer for everything to belong to
        self.sizer = wx.BoxSizer( wx.HORIZONTAL )
        # Build the toolbar now
        self.numDieText = wx.TextCtrl( self, TB_IDC_NUMDICE, "1", size= wx.Size(50, 25),
                                      validator=MathOnlyValidator() )
        self.sizer.Add( self.numDieText, 1, wx.EXPAND | wx.ALIGN_LEFT )
        bm = wx.Image(dir_struct["icon"]+"b_d4.gif", wx.BITMAP_TYPE_GIF).ConvertToBitmap()
        butt = wx.BitmapButton( self, TB_IDC_D4, bm, size=(bm.GetWidth(), bm.GetHeight()) )
        self.sizer.Add( butt, 0, wx.ALIGN_CENTER )
        self.Bind(wx.EVT_BUTTON, self.onToolBarClick, id=TB_IDC_D4)
        bm = wx.Image(dir_struct["icon"]+"b_d6.gif", wx.BITMAP_TYPE_GIF).ConvertToBitmap()
        butt = wx.BitmapButton( self, TB_IDC_D6, bm, size=(bm.GetWidth(), bm.GetHeight()) )
        self.sizer.Add( butt, 0, wx.ALIGN_CENTER )
        self.Bind(wx.EVT_BUTTON, self.onToolBarClick, id=TB_IDC_D6)
        bm = wx.Image(dir_struct["icon"]+"b_d8.gif", wx.BITMAP_TYPE_GIF).ConvertToBitmap()
        butt = wx.BitmapButton( self, TB_IDC_D8, bm, size=(bm.GetWidth(), bm.GetHeight()) )
        self.sizer.Add( butt, 0, wx.ALIGN_CENTER )
        self.Bind(wx.EVT_BUTTON, self.onToolBarClick, id=TB_IDC_D8)
        bm = wx.Image(dir_struct["icon"]+"b_d10.gif", wx.BITMAP_TYPE_GIF).ConvertToBitmap()
        butt = wx.BitmapButton( self, TB_IDC_D10, bm, size=(bm.GetWidth(), bm.GetHeight()) )
        self.sizer.Add( butt, 0, wx.ALIGN_CENTER )
        self.Bind(wx.EVT_BUTTON, self.onToolBarClick, id=TB_IDC_D10)
        bm = wx.Image(dir_struct["icon"]+"b_d12.gif", wx.BITMAP_TYPE_GIF).ConvertToBitmap()
        butt = wx.BitmapButton( self, TB_IDC_D12, bm, size=(bm.GetWidth(), bm.GetHeight()) )
        self.sizer.Add( butt, 0, wx.ALIGN_CENTER )
        self.Bind(wx.EVT_BUTTON, self.onToolBarClick, id=TB_IDC_D12)
        bm = wx.Image(dir_struct["icon"]+"b_d20.gif", wx.BITMAP_TYPE_GIF).ConvertToBitmap()
        butt = wx.BitmapButton( self, TB_IDC_D20, bm, size=(bm.GetWidth(), bm.GetHeight()) )
        self.sizer.Add( butt, 0, wx.ALIGN_CENTER )
        self.Bind(wx.EVT_BUTTON, self.onToolBarClick, id=TB_IDC_D20)
        bm = wx.Image(dir_struct["icon"]+"b_d100.gif", wx.BITMAP_TYPE_GIF).ConvertToBitmap()
        butt = wx.BitmapButton( self, TB_IDC_D100, bm, size=(bm.GetWidth(), bm.GetHeight()) )
        self.sizer.Add( butt, 0, wx.ALIGN_CENTER )
        self.Bind(wx.EVT_BUTTON, self.onToolBarClick, id=TB_IDC_D100)
        # Add our other text control to the sizer
        self.dieModText = wx.TextCtrl( self, TB_IDC_MODS, "+0", size= wx.Size(50, 25),
                                      validator=MathOnlyValidator() )
        self.sizer.Add( self.dieModText, 1, wx.EXPAND | wx.ALIGN_RIGHT )
        # Now, attach the sizer to the panel and tell it to do it's magic
        self.SetSizer(self.sizer)
        self.SetAutoLayout(True)
        self.Fit()

    def onToolBarClick( self, evt ):
        # Get our modifiers
        numDie = self.numDieText.GetValue()
        dieMod = self.dieModText.GetValue()
        # Init the die roll text
        if not len(numDie): numDie = 1
        dieRoll = str(numDie)
        # Figure out which die roll was selected
        id = evt.GetId()
	recycle_bin = {TB_IDC_D4: "d4", TB_IDC_D6: "d6", TB_IDC_D8: "d8", TB_IDC_D10: "d10", 
        TB_IDC_D12: "d12", TB_IDC_D20: "d20", TB_IDC_D100: "d100"}
	dieType = recycle_bin[id]; del recycle_bin
        if len(dieMod) and dieMod[0] not in "*/-+": dieMod = "+" + dieMod #Add Modifier
        rollString = "[" + dieRoll + dieType + dieMod + "]" # Build the complete die roll text now
        if self.callBack != None: self.callBack( rollString,1,1 ) # Now, call the post method to send everything off with
