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
# File: mapper/fog_handler.py
# Author: Mark Tarrabain
#
# Description: Handler for fog layer
#

from fog import *
from base_handler import *
from region import *

#CTRL_REVEAL = wx.NewId()
#CTRL_HIDE = wx.NewId()
#CTRL_REMOVE = wx.NewId()
#CTRL_SHOWALL = wx.NewId()
#CTRL_HIDEALL = wx.NewId()
#CTRL_COLOR = wx.NewId()
#CTRL_PEN = wx.NewId()

class fog_handler(base_layer_handler):
    def __init__(self, parent, id, canvas):
        self.showmode = 1
        self.drawing = False
        self.pencolor=wx.WHITE
        base_layer_handler.__init__(self, parent, id, canvas)

    def build_ctrls(self):
        foglayer = self.canvas.layers['fog']
        base_layer_handler.build_ctrls(self)
        self.f_type_radio = {}
        self.fogshow = wx.RadioButton(self, wx.ID_ANY, "Show", style=wx.RB_GROUP)
        self.foghide = wx.RadioButton(self, wx.ID_ANY, "Hide")
        self.sizer.Add(self.foghide, 0, wx.ALIGN_CENTER)
        self.sizer.Add(self.fogshow, 0, wx.ALIGN_CENTER)
        self.sizer.Add(wx.Size(20,25),1)

    def build_menu(self,label = "fog"):
        base_layer_handler.build_menu(self,label)
        self.main_menu.AppendSeparator()
        item = wx.MenuItem(self.main_menu, wx.ID_ANY, "&Hide All", "Hide All")
        self.canvas.Bind(wx.EVT_MENU, self.on_hideall, item)
        self.main_menu.AppendItem(item)
        item = wx.MenuItem(self.main_menu, wx.ID_ANY, "&Fog Mask", "Fog Mask")
        self.canvas.Bind(wx.EVT_MENU, self.on_color, item)
        self.main_menu.AppendItem(item)
        item = wx.MenuItem(self.main_menu, wx.ID_ANY, "&Remove Fog Layer", "Remove Fog Layer")
        self.canvas.Bind(wx.EVT_MENU, self.on_remove, item)
        self.main_menu.AppendItem(item)
        item = wx.MenuItem(self.main_menu, wx.ID_ANY, "&Pen Color", "Pen Color")
        self.canvas.Bind(wx.EVT_MENU, self.on_pen_color, item)
        self.main_menu.AppendItem(item)

    def on_remove(self,evt):
        session=self.canvas.frame.session
        if (session.my_role() != session.ROLE_GM):
            open_rpg.get_component("chat").InfoPost("You must be a GM to use this feature")
            return
        self.canvas.layers['fog'].remove_fog()
        self.canvas.Refresh(False)

    def on_showall(self,evt):
        session=self.canvas.frame.session
        if (session.my_role() != session.ROLE_GM):
            open_rpg.get_component("chat").InfoPost("You must be a GM to use this feature")
            return
        foglayer = self.canvas.layers['fog']
        foglayer.showall()
        self.canvas.Refresh(False)

    def on_pen_color(self,evt):
        data = wx.ColourData()
        data.SetChooseFull(True)
        data.SetColour(self.pencolor)
        dlg = wx.ColourDialog(self.canvas, data)
        if dlg.ShowModal() == wx.ID_OK:
            data = dlg.GetColourData()
            color = data.GetColour()
            self.pencolor=color
        dlg.Destroy()

    def on_hideall(self,evt):
        session=self.canvas.frame.session
        if (session.my_role() != session.ROLE_GM):
            open_rpg.get_component("chat").InfoPost("You must be a GM to use this feature")
            return
        foglayer=self.canvas.layers['fog']
        foglayer.clear()
        self.canvas.Refresh(False)

    def on_color(self,evt):
        session=self.canvas.frame.session
        if (session.my_role() != session.ROLE_GM):
            open_rpg.get_component("chat").InfoPost("You must be a GM to use this feature")
            return
        data = wx.ColourData()
        data.SetChooseFull(True)
        data.SetColour(self.canvas.layers['fog'].color)
        dlg = wx.ColourDialog(self.canvas, data)
        if dlg.ShowModal() == wx.ID_OK:
            data = dlg.GetColourData()
            color = data.GetColour()
            if "__WXGTK__" not in wx.PlatformInfo: color = wx.Color(color.Red(), color.Green(), color.Blue(), 128)
            self.canvas.layers['fog'].color = color
        dlg.Destroy()
        self.canvas.layers['fog'].fill_fog()
        self.canvas.Refresh(False)

    def update_info(self):
        foglayer = self.canvas.layers['fog']
        pass

    def on_motion(self, evt):
        scale = self.canvas.layers['grid'].mapscale
        dc = wx.ClientDC(self.canvas)
        dc.SetUserScale(scale, scale)
        self.canvas.PrepareDC(dc)
        pos = evt.GetLogicalPosition(dc)
        pos.x /= COURSE
        pos.y /= COURSE
        pos.x /= scale
        pos.y /= scale

        if evt.m_leftDown:
            if not self.drawing:
                self.line = []
                self.line.append(IPoint().make(pos.x, pos.y))
            elif pos.x != self.last.x or pos.y != self.last.y:
                pen= wx.Pen(self.pencolor)
                pen.SetWidth(COURSE/2+1)
                dc.SetPen(pen)
                multi = scale*COURSE
                dc.DrawLine(self.last.x*multi, self.last.y*multi, pos.x*multi, pos.y*multi)
                dc.SetPen(wx.NullPen)
                self.line.append(IPoint().make(pos.x, pos.y))
            self.last = pos
            self.drawing = True
        del dc

    def on_left_up(self,evt):
        if self.drawing == True:
            session=self.canvas.frame.session
            if (session.my_role() != session.ROLE_GM):
                open_rpg.get_component("chat").InfoPost("You must be a GM to use this feature")
            else:
                # This code sets the mode to either new or del 
                # depending on the action to function with the updated createregen code.
                if (self.fogshow.GetValue() == 1):
                    showmode = 'new'
                else:
                    showmode = 'del'
                scale = self.canvas.layers['grid'].mapscale
                dc = wx.ClientDC(self.canvas)
                self.canvas.PrepareDC(dc)
                dc.SetUserScale(scale,scale)
                pen= wx.Pen(self.pencolor)
                pen.SetWidth(COURSE/2+1)
                dc.SetPen(pen)
                dc.DrawLine(self.last.x*scale*COURSE,self.last.y*scale*COURSE,
                    self.line[0].X*scale*COURSE,self.line[0].Y*scale*COURSE)
                dc.SetPen(wx.NullPen)
                wx.BeginBusyCursor()
                # This prevents the divide by zero error by not even 
                # sending the line to be proccessed if it contains less then 3 points
                if (len(self.line)>1): self.canvas.layers['fog'].createregn(self.line, showmode)
                else: pass
                wx.EndBusyCursor()
                del dc
            self.canvas.Refresh(False)
            self.drawing = False
