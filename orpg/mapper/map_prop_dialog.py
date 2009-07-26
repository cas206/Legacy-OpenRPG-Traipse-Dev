# Copyright (C) 2000-2001 The OpenRPG Project
#
#    openrpg-dev@lists.sourceforge.net
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
# File: mapper/map_prop_dialog.py
# Author: OpenRPG
# Maintainer:
# Version:
#   $Id: map_prop_dialog.py,v 1.16 2006/11/04 21:24:21 digitalxero Exp $
#
# Description:
#
__version__ = "$Id: map_prop_dialog.py,v 1.16 2006/11/04 21:24:21 digitalxero Exp $"

from orpg.orpg_windows import *
from background import *
from grid import *
from miniatures import *
from whiteboard import *

##-----------------------------
## map prop dialog
##-----------------------------

CTRL_WIDTH = wx.NewId()
CTRL_HEIGHT = wx.NewId()
CTRL_BG_COLOR = wx.NewId()
CTRL_BG_COLOR_VALUE = wx.NewId()
CTRL_TEXTURE = wx.NewId()
CTRL_TEXTURE_PATH = wx.NewId()
CTRL_IMAGE = wx.NewId()
CTRL_IMAGE_PATH  = wx.NewId()
CTRL_GRID = wx.NewId()
CTRL_GRID_SNAP = wx.NewId()
CTRL_GRID_COLOR = wx.NewId()
CTRL_GRID_MODE_RECT = wx.NewId()
CTRL_GRID_MODE_HEX = wx.NewId()
CTRL_GRID_LINE_NONE = wx.NewId()
CTRL_GRID_LINE_DOTTED = wx.NewId()
CTRL_GRID_LINE_SOLID = wx.NewId()

class general_map_prop_dialog(wx.Dialog):
    def __init__(self,parent,size,bg_layer,grid_layer):
        wx.Dialog.__init__(self,parent,-1,"General Map Properties",wx.DefaultPosition,wx.Size(425,405))
        self.size = size
        self.bg_layer = bg_layer
        self.grid_layer = grid_layer
        #build controls
        self.ctrls = {  CTRL_WIDTH : wx.TextCtrl(self, CTRL_WIDTH, str(size[0])),
                        CTRL_HEIGHT : wx.TextCtrl(self, CTRL_HEIGHT, str(size[1])),
                        CTRL_BG_COLOR : wx.RadioButton(self, CTRL_BG_COLOR, "Color", style=wx.RB_GROUP),
                        CTRL_BG_COLOR_VALUE : wx.Button(self, CTRL_BG_COLOR_VALUE, "Color"),
                        CTRL_TEXTURE : wx.RadioButton(self, CTRL_TEXTURE, "Texture"),
                        CTRL_TEXTURE_PATH: wx.TextCtrl(self, CTRL_TEXTURE_PATH,"http://"),
                        CTRL_IMAGE : wx.RadioButton(self, CTRL_IMAGE, "Image"),
                        CTRL_IMAGE_PATH :wx.TextCtrl(self, CTRL_IMAGE_PATH,"http://"),
                        CTRL_GRID : wx.TextCtrl(self, CTRL_GRID),
                        CTRL_GRID_SNAP : wx.CheckBox(self, CTRL_GRID_SNAP, " Snap to grid"),
                        CTRL_GRID_COLOR : wx.Button(self, CTRL_GRID_COLOR, "Grid Color"),
                        CTRL_GRID_MODE_RECT : wx.RadioButton(self, CTRL_GRID_MODE_RECT, "Rectangular", style=wx.RB_GROUP),
                        CTRL_GRID_MODE_HEX : wx.RadioButton(self, CTRL_GRID_MODE_HEX, "Hexagonal"),
                        CTRL_GRID_LINE_NONE : wx.RadioButton(self, CTRL_GRID_LINE_NONE, "No Lines", style=wx.RB_GROUP),
                        CTRL_GRID_LINE_DOTTED : wx.RadioButton(self, CTRL_GRID_LINE_DOTTED, "Dotted Lines"),
                        CTRL_GRID_LINE_SOLID : wx.RadioButton(self, CTRL_GRID_LINE_SOLID, "Solid Lines")
                     }
        # set values of bg controls
        self.ctrls[CTRL_BG_COLOR].SetValue(False)
        self.ctrls[CTRL_TEXTURE].SetValue(False)
        self.ctrls[CTRL_IMAGE].SetValue(False)

        # Begin ted's changes for map bg persistency.
        if bg_layer.bg_color != None: self.ctrls[CTRL_BG_COLOR_VALUE].SetBackgroundColour(bg_layer.bg_color)
        if bg_layer.img_path != None:
            self.ctrls[CTRL_TEXTURE_PATH].SetValue(bg_layer.img_path)
            self.ctrls[CTRL_IMAGE_PATH].SetValue(bg_layer.img_path)
        # End ted's changes

        if bg_layer.type == BG_COLOR: self.ctrls[CTRL_BG_COLOR].SetValue(True)
        elif bg_layer.type == BG_TEXTURE: self.ctrls[CTRL_TEXTURE].SetValue(True)
        elif bg_layer.type == BG_IMAGE:
            self.ctrls[CTRL_WIDTH].Enable(False)
            self.ctrls[CTRL_HEIGHT].Enable(False)
            self.ctrls[CTRL_IMAGE].SetValue(True)
            # self.ctrls[CTRL_IMAGE_PATH].SetValue(bg_layer.img_path)

        # set grid layer control values
        self.ctrls[CTRL_GRID].SetValue(str(grid_layer.unit_size))
        self.ctrls[CTRL_GRID_SNAP].SetValue(grid_layer.snap)
        self.ctrls[CTRL_GRID_COLOR].SetBackgroundColour(grid_layer.color)
        self.ctrls[CTRL_GRID_MODE_RECT].SetValue(grid_layer.mode == GRID_RECTANGLE)
        self.ctrls[CTRL_GRID_MODE_HEX].SetValue(grid_layer.mode == GRID_HEXAGON)
        self.ctrls[CTRL_GRID_LINE_NONE].SetValue(grid_layer.line == LINE_NONE)
        self.ctrls[CTRL_GRID_LINE_DOTTED].SetValue(grid_layer.line == LINE_DOTTED)
        self.ctrls[CTRL_GRID_LINE_SOLID].SetValue(grid_layer.line == LINE_SOLID)

        #create sizers
        sizers = {}
        sizers['main'] = wx.BoxSizer(wx.VERTICAL)

        #size
        sizers['size'] = wx.StaticBoxSizer(wx.StaticBox(self,-1,"Size"), wx.HORIZONTAL)
        sizers['size'].Add(wx.StaticText(self, -1, "Width: "), 0, wx.ALIGN_CENTER)
        sizers['size'].Add(self.ctrls[CTRL_WIDTH], 0, wx.ALIGN_CENTER)
        sizers['size'].Add(wx.Size(20,25))
        sizers['size'].Add(wx.StaticText(self, -1, "Height: "), 0, wx.ALIGN_CENTER)
        sizers['size'].Add(self.ctrls[CTRL_HEIGHT], 0, wx.ALIGN_CENTER)

        #bg
        sizers['bg'] = wx.StaticBoxSizer(wx.StaticBox(self,-1,"Background"), wx.HORIZONTAL)
        sizers['bg_layout'] = wx.FlexGridSizer(3, 2,10,10)
        sizers['bg_layout'].AddMany([(self.ctrls[CTRL_BG_COLOR],0,wx.EXPAND),
                              (self.ctrls[CTRL_BG_COLOR_VALUE],1,wx.EXPAND),
                              (self.ctrls[CTRL_TEXTURE],0,wx.EXPAND),
                              (self.ctrls[CTRL_TEXTURE_PATH],1,wx.EXPAND),
                              (self.ctrls[CTRL_IMAGE],0,wx.EXPAND),
                              (self.ctrls[CTRL_IMAGE_PATH],1,wx.EXPAND)
                            ])
        sizers['bg_layout'].AddGrowableCol(1)
        sizers['bg'].Add(sizers['bg_layout'], 0, wx.EXPAND)

        #grid
        sizers['grid'] = wx.StaticBoxSizer(wx.StaticBox(self,-1,"Grid"), wx.HORIZONTAL)
        sizers['grid_layout'] = wx.FlexGridSizer(2, 3,10,10)
        sizers['grid_layout'].AddMany([(wx.StaticText(self, -1, "Pixels per Square: "),2,wx.ALIGN_CENTER),
                              (self.ctrls[CTRL_GRID],1,wx.EXPAND),
                              (self.ctrls[CTRL_GRID_COLOR],1,wx.EXPAND),
                              (self.ctrls[CTRL_GRID_SNAP],2,wx.EXPAND),
                              (self.ctrls[CTRL_GRID_MODE_RECT],1,wx.EXPAND),
                              (self.ctrls[CTRL_GRID_MODE_HEX],1,wx.EXPAND),
                              (self.ctrls[CTRL_GRID_LINE_NONE],1,wx.EXPAND),
                              (self.ctrls[CTRL_GRID_LINE_DOTTED],1,wx.EXPAND),
                              (self.ctrls[CTRL_GRID_LINE_SOLID],1,wx.EXPAND)
                            ])
        sizers['grid'].Add(sizers['grid_layout'], 0, wx.EXPAND)

        # buttons
        sizers['but'] = wx.BoxSizer(wx.HORIZONTAL)
        sizers['but'].Add(wx.Button(self, wx.ID_OK, "Apply"), 1, wx.EXPAND)
        sizers['but'].Add(wx.Size(10,10))
        sizers['but'].Add(wx.Button(self, wx.ID_CANCEL, "Cancel"), 1, wx.EXPAND)
        self.sizers = sizers

        #main sizer
        self.sizers['main'].Add(sizers['size'],1, wx.EXPAND)
        self.sizers['main'].Add(sizers['bg'], 1, wx.EXPAND)
        self.sizers['main'].Add(sizers['grid'], 1, wx.EXPAND)
        self.sizers['main'].Add(sizers['but'], 0, wx.EXPAND)
        self.SetSizer(self.sizers['main'])
        self.SetAutoLayout(True)
        self.Fit()

        #event handlers
        self.Bind(wx.EVT_BUTTON, self.on_ok, id=wx.ID_OK)
        self.Bind(wx.EVT_RADIOBUTTON, self.on_click, id=CTRL_BG_COLOR)
        self.Bind(wx.EVT_RADIOBUTTON, self.on_click, id=CTRL_TEXTURE)
        self.Bind(wx.EVT_RADIOBUTTON, self.on_click, id=CTRL_IMAGE)
        self.Bind(wx.EVT_BUTTON, self.on_click, id=CTRL_BG_COLOR_VALUE)
        self.Bind(wx.EVT_BUTTON, self.on_click, id=CTRL_GRID_COLOR)
        self.Bind(wx.EVT_RADIOBUTTON, self.on_click, id=CTRL_GRID_MODE_RECT)
        self.Bind(wx.EVT_RADIOBUTTON, self.on_click, id=CTRL_GRID_MODE_HEX)
        self.Bind(wx.EVT_RADIOBUTTON, self.on_click, id=CTRL_GRID_LINE_NONE)
        self.Bind(wx.EVT_RADIOBUTTON, self.on_click, id=CTRL_GRID_LINE_DOTTED)
        self.Bind(wx.EVT_RADIOBUTTON, self.on_click, id=CTRL_GRID_LINE_SOLID)

    def on_click(self,evt):
        id = evt.GetId()
        if id == CTRL_BG_COLOR or id == CTRL_TEXTURE:
            self.ctrls[CTRL_WIDTH].Enable(True)
            self.ctrls[CTRL_HEIGHT].Enable(True)
        elif id == CTRL_IMAGE:
            self.ctrls[CTRL_WIDTH].Enable(False)
            self.ctrls[CTRL_HEIGHT].Enable(False)
        elif id == CTRL_BG_COLOR_VALUE:
            data = wx.ColourData()
            data.SetChooseFull(True)
            dlg = wx.ColourDialog(self, data)
            if dlg.ShowModal() == wx.ID_OK:
                data = dlg.GetColourData()
                self.ctrls[CTRL_BG_COLOR_VALUE].SetBackgroundColour(data.GetColour())
            dlg.Destroy()
        elif id == CTRL_GRID_COLOR:
            data = wx.ColourData()
            data.SetChooseFull(True)
            dlg = wx.ColourDialog(self, data)
            if dlg.ShowModal() == wx.ID_OK:
                data = dlg.GetColourData()
                self.ctrls[CTRL_GRID_COLOR].SetBackgroundColour(data.GetColour())
            dlg.Destroy()
    def on_ok(self,evt):
        try: self.size = (int(self.ctrls[CTRL_WIDTH].GetValue()),int(self.ctrls[CTRL_HEIGHT].GetValue()))
        except: pass
        if self.ctrls[CTRL_BG_COLOR].GetValue() == True:
            self.bg_layer.set_color(self.ctrls[CTRL_BG_COLOR_VALUE].GetBackgroundColour())
        elif self.ctrls[CTRL_TEXTURE].GetValue() == True:
            self.bg_layer.set_texture(self.ctrls[CTRL_TEXTURE_PATH].GetValue())
        elif self.ctrls[CTRL_IMAGE].GetValue() == True:
            self.size = self.bg_layer.set_image(self.ctrls[CTRL_IMAGE_PATH].GetValue(),self.grid_layer.mapscale)
        else: self.bg_layer.clear()
        if self.ctrls[CTRL_GRID_MODE_RECT].GetValue() == True: grid_mode = GRID_RECTANGLE
        else: grid_mode = GRID_HEXAGON
        if self.ctrls[CTRL_GRID_LINE_NONE].GetValue() == True: grid_line = LINE_NONE
        elif self.ctrls[CTRL_GRID_LINE_DOTTED].GetValue() == True: grid_line = LINE_DOTTED
        else: grid_line = LINE_SOLID
        self.grid_layer.set_grid(int(self.ctrls[CTRL_GRID].GetValue()),
                                 self.ctrls[CTRL_GRID_SNAP].GetValue(),
                                 self.ctrls[CTRL_GRID_COLOR].GetBackgroundColour(),
                                 grid_mode,
                                 grid_line)
        self.EndModal(wx.ID_OK)
