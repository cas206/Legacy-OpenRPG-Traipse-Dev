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
# File: orpg/mapper/map_handler.py
# Author: OpenRPG Team
# Maintainer:
# Version:
#   $Id: map_handler.py,v 1.14 2007/04/03 00:14:35 digitalxero Exp $
#
# Description: map layer handler
#
__version__ = "$Id: map_handler.py,v 1.14 2007/04/03 00:14:35 digitalxero Exp $"

from base_handler import *

class map_handler(base_layer_handler):
    def __init__(self, parent, id, canvas):
        base_layer_handler.__init__(self, parent, id, canvas)

    def build_ctrls(self):
        base_layer_handler.build_ctrls(self)
        self.width = wx.TextCtrl(self, wx.ID_ANY)
        self.height = wx.TextCtrl(self, wx.ID_ANY)
        self.apply_button = wx.Button(self, wx.ID_OK, "Apply", style=wx.BU_EXACTFIT)
        self.load_default = wx.Button(self, wx.ID_ANY, "Default Map", style=wx.BU_EXACTFIT)
        self.sizer.Add(wx.StaticText(self, -1, "Width: "),0, wx.ALIGN_CENTER)
        self.sizer.Add(self.width, 0, wx.ALIGN_CENTER)
        self.sizer.Add((6, 0))
        self.sizer.Add(wx.StaticText(self, -1, "Height: "),0, wx.ALIGN_CENTER)
        self.sizer.Add(self.height, 0, wx.ALIGN_CENTER)
        self.sizer.Add((6, 0))
        self.sizer.Add(self.apply_button, 0, wx.ALIGN_CENTER)
        self.sizer.Add((6, 0))
        self.sizer.Add(self.load_default, 0, wx.ALIGN_CENTER)
        self.Bind(wx.EVT_BUTTON, self.on_apply, self.apply_button)
        self.Bind(wx.EVT_BUTTON, self.on_load_default, self.load_default)
        self.update_info()

    def update_info(self):
        size = self.canvas.get_size()
        self.width.SetValue(str(size[0]))
        self.height.SetValue(str(size[1]))

    def build_menu(self,label = "Grid"):
        base_layer_handler.build_menu(self,label)

    def on_load_default(self, evt):
        self.map_frame.load_default()

    def on_apply(self, evt):
        session=self.canvas.frame.session
        if (session.my_role() != session.ROLE_GM):
            open_rpg.get_component("chat").InfoPost("You must be a GM to use this feature")
            return
        try: size = (int(self.width.GetValue()),int(self.height.GetValue()))
        except: wx.MessageBox("Invalid Map Size!","Map Properties"); return
        self.canvas.set_size(size)
        self.update_info()
        self.canvas.send_map_data()
        self.canvas.Refresh()
