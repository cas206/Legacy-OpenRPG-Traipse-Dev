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
# File: map_miniature_nodehandler.py
# Author: Andrew Bennett
# Maintainer:
# Version:
#   $Id: map_miniature_nodehandler.py,v Traipse 'Ornery-Orc' prof.ebral Exp $
#
# Description: nodehandler for miniature images
#

#from nodehandlers.core import *
from core import *
from orpg.gametree import *
from orpg.mapper.miniatures_msg import mini_msg
from orpg.mapper.images import ImageHandler
import urllib

class map_miniature_handler(node_handler):

    """ A node handler for miniatures
        <nodehandler name='Elf-1' module='map_miniature_nodehandler' class='map_miniature_handler' >
                <miniature id='' label='Elf-1' posx='' posy='' path='' ...  />
        </nodehandler >
    """

    def __init__(self,xml,tree_node):
        node_handler.__init__(self,xml,tree_node)
        self.mapper = component.get("map")
        self.session = component.get("session")
        self.miniature_xml = self.xml.find("miniature")
        
    def get_scaled_bitmap(self,x,y):
        my_mini_msg = mini_msg()
        my_mini_msg.init_from_dom(self.miniature_xml)
        bmp = None
        path = my_mini_msg.get_prop("path")

        if path:
            path = urllib.unquote(path)
            if ImageHandler.Cache.has_key(path): bmp = ImageHandler.Cache[path]
            else: bmp = ImageHandler.directLoad(path)# Old Code TaS.

            if bmp:
                img = wx.ImageFromMime(ImageHandler.Cache[path][1], ImageHandler.Cache[path][2])
                #img = wx.ImageFromBitmap(bmp)
                scaled_img = img.Scale(x,y)
                scaled_bmp = scaled_img.ConvertToBitmap()
                scratch = scaled_img.ConvertToBitmap()
                memDC = wx.MemoryDC()
                memDC.BeginDrawing()
                memDC.SelectObject(scaled_bmp)
                memDC.SetBrush(wx.WHITE_BRUSH)
                memDC.SetPen(wx.WHITE_PEN)
                memDC.DrawRectangle(0,0,x,y)
                memDC.SetPen(wx.NullPen)
                memDC.SetBrush(wx.NullBrush)
                memDC.DrawBitmap(scratch,0,0,1)
                memDC.SelectObject(wx.NullBitmap)
                memDC.EndDrawing()
                del memDC
                return scaled_bmp

    def map_aware(self):
        return 1

    def get_miniature_XML(self):
        my_mini_msg = mini_msg()
        my_mini_msg.init_from_dom(self.miniature_xml)
        my_mini_msg.init_prop("id",self.session.get_next_id())
        label = self.xml.get("name")
        my_mini_msg.init_prop("label",label)
        new_xml = my_mini_msg.get_all_xml()
        return new_xml

    def get_to_map_XML(self):
        new_xml = self.get_miniature_XML()
        new_xml = str("<map action='update'><miniatures>" + new_xml + "</miniatures></map>")
        return new_xml

    def on_send_to_map(self,evt):
        if isinstance(evt, wx.MouseEvent) and evt.LeftUp():# as opposed to a menu event
            dc = wx.ClientDC(self.mapper.canvas)
            self.mapper.canvas.PrepareDC(dc)
            grid = self.mapper.canvas.layers['grid']
            dc.SetUserScale(grid.mapscale, grid.mapscale)
            pos = evt.GetLogicalPosition(dc)
            try:
                align = int(self.xml.get("align"))
                width = int(self.xml.get("width"))
                height = int(self.xml.get("height"))
                pos = grid.get_snapped_to_pos(pos, align, width, height)
            except: pass
            self.miniature_xml.set("posx", str(pos.x))
            self.miniature_xml.set("posy", str(pos.y))
        new_xml = self.get_to_map_XML()
        if (self.session.my_role() != self.session.ROLE_GM) and (self.session.my_role() != self.session.ROLE_PLAYER):
            component.get("chat").InfoPost("You must be either a player or GM to use the miniature Layer")
            return
        if new_xml:
            self.mapper.new_data(new_xml)
            self.session.send(new_xml)
        else: print "problem converting old mini xml to new mini xml"

    def about(self):
        return "Miniature node by Andrew Bennett"

    def tohtml(self):
        html_str = "<table><tr><td>"
        html_str += "<center><img src='" + self.xml.get("path") + "'>"
        html_str += "</center></td></tr>\n"
        html_str += "<tr><td><center>" + self.xml.get("name") + "</center></td></tr></table>"
        return html_str
