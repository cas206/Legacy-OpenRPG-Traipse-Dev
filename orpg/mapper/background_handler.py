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
# File: mapper/background_handler.py
# Author: OpenRPG Team
# Maintainer:
# Version:
#   $Id: background_handler.py,v Traipse 'Ornery-Orc' prof.ebral Exp $
#
# Description: Background layer handler
#
__version__ = "$Id: background_handler.py,v Traipse 'Ornery-Orc' prof.ebral Exp $"

import thread, mimetypes, os
from threading import Lock
from background import *
from base_handler import *
from base import *

from orpg.tools.orpg_settings import settings

class background_handler(base_layer_handler):
    def __init__(self, parent, id, canvas):
        base_layer_handler.__init__(self, parent, id, canvas)
        self.settings = settings

    def build_ctrls(self):
        base_layer_handler.build_ctrls(self)
        self.lock = Lock()
        self.bg_type = wx.Choice(self, wx.ID_ANY, choices = ["Texture", "Image", "Color" ])
        self.bg_type.SetSelection(2)
        self.localBrowse = wx.Button(self, wx.ID_ANY, 'Browse', style=wx.BU_EXACTFIT)
        self.localBrowse.Hide()
        self.url_path = wx.TextCtrl(self, wx.ID_ANY,"http://")
        self.color_button = wx.Button(self, wx.ID_ANY, "Color", style=wx.BU_EXACTFIT)
        self.color_button.SetBackgroundColour(wx.BLACK)
        self.color_button.SetForegroundColour(wx.WHITE)
        self.apply_button = wx.Button(self, wx.ID_ANY, "Apply", style=wx.BU_EXACTFIT)
        self.sizer.Add(self.bg_type, 0, wx.ALIGN_CENTER)
        self.sizer.Add((6, 0))
        self.sizer.Add(self.url_path, 1, wx.ALIGN_CENTER)
        self.sizer.Add((6, 0))
        self.sizer.Add(self.color_button, 0, wx.ALIGN_CENTER)
        self.sizer.Add((6, 0))
        self.sizer.Add(self.localBrowse, 0, wx.ALIGN_CENTER)
        self.sizer.Add((6, 0))
        self.sizer.Add(self.apply_button, 0, wx.ALIGN_CENTER)
        self.Bind(wx.EVT_BUTTON, self.on_bg_color, self.color_button)
        self.Bind(wx.EVT_BUTTON, self.on_apply, self.apply_button)
        self.Bind(wx.EVT_BUTTON, self.on_browse, self.localBrowse)
        self.Bind(wx.EVT_CHOICE, self.on_bg_type, self.bg_type)
        self.update_info()

    def on_browse(self, evt):
        if self.bg_type.GetStringSelection() == 'Texture' or self.bg_type.GetStringSelection() == 'Image':
            dlg = wx.FileDialog(None, "Select a Miniature to load", 
                orpg.dirpath.dir_struct["user"]+'webfiles/', 
                wildcard="Image files (*.bmp, *.gif, *.jpg, *.png)|*.bmp;*.gif;*.jpg;*.png", style=wx.OPEN)
            if not dlg.ShowModal() == wx.ID_OK:
                dlg.Destroy()
                return
            file = open(dlg.GetPath(), "rb")
            imgdata = file.read()
            file.close()
            filename = dlg.GetFilename()
            (imgtype,j) = mimetypes.guess_type(filename)
            postdata = urllib.urlencode({'filename':filename, 'imgdata':imgdata, 'imgtype':imgtype})

            if self.settings.get_setting('LocalorRemote') == 'Remote':
                thread.start_new_thread(self.canvas.layers['bg'].upload, 
                    (postdata, dlg.GetPath(), self.bg_type.GetStringSelection()))
            else:
                try: min_url = component.get("cherrypy") + filename
                except: return
                min_url = dlg.GetDirectory().replace(orpg.dirpath.dir_struct["user"]+'webfiles', 
                    component.get("cherrypy")).replace(os.sep, '/') + '/' + filename

                if self.bg_type.GetStringSelection() == 'Texture': self.canvas.layers['bg'].set_texture(min_url)
                elif self.bg_type.GetStringSelection() == 'Image': self.size = self.canvas.layers['bg'].set_image(min_url,1)
                self.update_info()
                self.canvas.send_map_data()
                self.canvas.Refresh(False)

    def update_info(self):
        bg_type = self.canvas.layers['bg'].get_type()
        session=self.canvas.frame.session
        if (session.my_role() != session.ROLE_GM): self.url_path.Hide()
        else:
            self.url_path.Show()
            self.url_path.Enable(BG_COLOR!=bg_type)
        self.color_button.SetBackgroundColour(self.canvas.layers['bg'].get_color())
        self.url_path.SetValue(self.canvas.layers['bg'].get_img_path())

    def build_menu(self,label = "Background"):
        base_layer_handler.build_menu(self,label)

    def on_bg_color(self,evt):
        data = wx.ColourData()
        data.SetChooseFull(True)
        dlg = wx.ColourDialog(self.canvas, data)
        if dlg.ShowModal() == wx.ID_OK:
            data = dlg.GetColourData()
            data = data.GetColour()
            r = data.Red()
            g = data.Green()
            b = data.Blue()
            fgcolor = wx.Colour(r^255, g^255, b^255)
            bgcolor = wx.Colour(r, g, b)
            self.color_button.SetBackgroundColour(bgcolor)
            self.color_button.SetForegroundColour(fgcolor)
        dlg.Destroy()

    def on_bg_type(self, evt):
        if self.bg_type.GetStringSelection() == 'Texture' or self.bg_type.GetStringSelection() == 'Image':
            self.localBrowse.Show()
            self.url_path.Enable()
        else:
            self.localBrowse.Hide()
            self.url_path.Disable()
        self.Layout()

    def on_apply(self, evt):
        session=self.canvas.frame.session
        if (session.my_role() != session.ROLE_GM) and (session.use_roles()):
            component.get("chat").InfoPost("You must be a GM to use this feature")
            return
        self.canvas.layers['bg'].set_color(self.color_button.GetBackgroundColour())

        if self.bg_type.GetStringSelection() == 'Texture': self.canvas.layers['bg'].set_texture(self.url_path.GetValue())
        elif self.bg_type.GetStringSelection() == 'Image': 
            self.size = self.canvas.layers['bg'].set_image(self.url_path.GetValue(),1)

        self.update_info()
        self.canvas.send_map_data()
        self.canvas.Refresh(False)
