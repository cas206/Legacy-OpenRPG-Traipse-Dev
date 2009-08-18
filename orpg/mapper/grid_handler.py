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
# File: orpg/mapper/grid_handler.py
# Author: OpenRPG Team
# Maintainer:
# Version:
#   $Id: grid_handler.py,v 1.20 2007/04/03 00:14:35 digitalxero Exp $
#
# Description: grid layer handler
#
__version__ = "$Id: grid_handler.py,v 1.20 2007/04/03 00:14:35 digitalxero Exp $"

from grid import *
from base_handler import *

class grid_handler(base_layer_handler):
    def __init__(self, parent, id, canvas):
        base_layer_handler.__init__(self, parent, id, canvas)

    def build_ctrls(self):
        base_layer_handler.build_ctrls(self)
        self.line_type = wx.Choice(self, wx.ID_ANY, choices = ["No Lines", "Dotted Lines", "Solid Lines" ])
        self.grid_mode = wx.Choice(self, wx.ID_ANY, choices = ["Rectangular", "Hexagonal","Isometric"])
        self.grid_snap = wx.CheckBox(self, wx.ID_ANY, " Snap")
        self.grid_size = wx.TextCtrl(self, wx.ID_ANY, size=(32,-1) )
        self.grid_ratio = wx.TextCtrl(self, wx.ID_ANY, size=(32,-1) )
        self.color_button = wx.Button(self, wx.ID_ANY, "Color", style=wx.BU_EXACTFIT)
        self.apply_button = wx.Button(self, wx.ID_OK, "Apply", style=wx.BU_EXACTFIT)
        self.color_button.SetBackgroundColour(wx.BLACK)
        self.color_button.SetForegroundColour(wx.WHITE)
        self.sizer.Add(wx.StaticText(self, -1, "Size: "), 0, wx.ALIGN_CENTER)
        self.sizer.Add(self.grid_size, 0, wx.ALIGN_CENTER)
        self.sizer.Add((6,0))
        self.sizer.Add(wx.StaticText(self, -1, "Ratio: "), 0, wx.ALIGN_CENTER)
        self.sizer.Add(self.grid_ratio, 0, wx.ALIGN_CENTER)
        self.sizer.Add((6,0))
        self.sizer.Add(self.line_type, 0, wx.ALIGN_CENTER)
        self.sizer.Add((6,0))
        self.sizer.Add(self.grid_mode, 0, wx.ALIGN_CENTER)
        self.sizer.Add((6,0))
        self.sizer.Add(self.grid_snap, 0, wx.ALIGN_CENTER)
        self.sizer.Add((6,0))
        self.sizer.Add(self.color_button, 0, wx.ALIGN_CENTER)
        self.sizer.Add((6,0))
        self.sizer.Add(self.apply_button, 0, wx.ALIGN_CENTER)
        self.Bind(wx.EVT_BUTTON, self.on_bg_color, self.color_button)
        self.Bind(wx.EVT_BUTTON, self.on_apply, self.apply_button)
        self.update_info()

    def update_info(self):
        layer = self.canvas.layers['grid']
        self.grid_size.SetValue(str(layer.get_unit_size()))
        self.grid_ratio.SetValue(str(layer.get_iso_ratio()))
        self.grid_mode.SetSelection(layer.get_mode())
        self.line_type.SetSelection(layer.get_line_type())
        self.color_button.SetBackgroundColour(layer.get_color())
        self.grid_snap.SetValue(layer.is_snap())
        layer.isUpdated = True

    def build_menu(self,label = "Grid"):
        base_layer_handler.build_menu(self,label)

    def on_bg_color(self,evt):
        data = wx.ColourData()
        data.SetChooseFull(True)
        dlg = wx.ColourDialog(self.canvas, data)
        if dlg.ShowModal() == wx.ID_OK:
            data = dlg.GetColourData()
            color = data.GetColour()
            self.color_button.SetBackgroundColour(color)
        dlg.Destroy()

    def on_apply(self, evt):
        session=self.canvas.frame.session
        if (session.my_role() != session.ROLE_GM):
            component.get("chat").InfoPost("You must be a GM to use this feature")
            return

        self.canvas.layers['grid'].set_grid(int(self.grid_size.GetValue()),self.grid_snap.GetValue(),
            self.color_button.GetBackgroundColour(),self.grid_mode.GetSelection(),
            self.line_type.GetSelection(),float(self.grid_ratio.GetValue()))
        self.update_info()
        self.canvas.send_map_data()
        self.canvas.Refresh()
