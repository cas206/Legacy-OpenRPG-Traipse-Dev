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
# File: background.py
# Author: Chris Davis
# Maintainer:
# Version:
#   $Id: background.py,v 1.29 2007/03/09 14:11:55 digitalxero Exp $
#
# Description: This file contains some of the basic definitions for the chat
# utilities in the orpg project.
#
__version__ = "$Id: background.py,v 1.29 2007/03/09 14:11:55 digitalxero Exp $"

from base import *
import thread
import urllib
import os.path
import time
import mimetypes

from orpg.orpgCore import component
from orpg.tools.orpg_log import logger
from orpg.tools.decorators import debugging
from orpg.tools.orpg_settings import settings

##-----------------------------
## background layer
##-----------------------------

BG_NONE = 0
BG_TEXTURE = 1
BG_IMAGE = 2
BG_COLOR = 3

class layer_back_ground(layer_base):
    @debugging
    def __init__(self, canvas):
        self.canvas = canvas
        self.log = component.get('log')
        layer_base.__init__(self)
        self.canvas = canvas
        self.r_h = RGBHex()
        self.clear()

    @debugging
    def error_loading_image(self, image):
        msg = "Unable to load image:" + `image`
        dlg = wx.MessageDialog(self.canvas,msg,'File not Found',wx.ICON_EXCLAMATION)
        dlg.ShowModal()
        dlg.Destroy()

    @debugging
    def clear(self):
        self.type = BG_NONE
        self.bg_bmp = None
        self.bg_color = None
        self.img_path = None
        self.local = False
        self.localPath = ''
        self.localTime = -1
        self.isUpdated = True

    @debugging
    def get_type(self):
        return self.type

    @debugging
    def get_img_path(self):
        if self.img_path: return self.img_path
        else: return ""

    @debugging
    def get_color(self):
        hexcolor = "#FFFFFF"
        if self.bg_color:
            (red,green,blue) = self.bg_color.Get()
            hexcolor = self.r_h.hexstring(red, green, blue)
        return hexcolor

    @debugging
    def set_texture(self, path):
        self.isUpdated = True
        self.type = BG_TEXTURE
        if self.img_path != path:
            try:
                self.bg_bmp = ImageHandler.load(path, "texture", 0)
                if self.bg_bmp == None:
                    logger.general("Invalid image type!")
                    raise Exception, "Invalid image type!"
            except: self.error_loading_image(path)
        self.img_path = path

    @debugging
    def set_image(self, path, scale):
        self.isUpdated = True
        self.type = BG_IMAGE
        if self.img_path != path:
            self.bg_bmp = ImageHandler.load(path, "background", 0)
            try:
                if self.bg_bmp == None:
                    logger.general("Invalid image type!")
                    raise Exception, "Invalid image type!"
            except: self.error_loading_image(path)
        self.img_path = path
        return (self.bg_bmp.GetWidth(),self.bg_bmp.GetHeight())

    @debugging
    def set_color(self, color):
        self.isUpdated = True
        self.type = BG_COLOR
        (r,g,b) = color.Get()
        self.bg_color = cmpColour(r,g,b)
        self.canvas.SetBackgroundColour(self.bg_color)

    @debugging
    def layerDraw(self, dc, scale, topleft, size):
        if self.bg_bmp == None or not self.bg_bmp.Ok() or ((self.type != BG_TEXTURE) and (self.type != BG_IMAGE)):
            return False
        dc2 = wx.MemoryDC()
        dc2.SelectObject(self.bg_bmp)
        topLeft = [int(topleft[0]/scale), int(topleft[1]/scale)]
        topRight = [int((topleft[0]+size[0]+1)/scale)+1, int((topleft[1]+size[1]+1)/scale)+1]
        if (topRight[0] > self.canvas.size[0]): topRight[0] = self.canvas.size[0]
        if (topRight[1] > self.canvas.size[1]): topRight[1] = self.canvas.size[1]
        bmpW = self.bg_bmp.GetWidth()
        bmpH = self.bg_bmp.GetHeight()
        if self.type == BG_TEXTURE:
            x = (topLeft[0]/bmpW)*bmpW
            y1 = int(topLeft[1]/bmpH)*bmpH
            if x < topLeft[0]:
                posx = topLeft[0]
                cl = topLeft[0]-x
            else:
                cl = 0
                posx = x
            while x < topRight[0]:
                if x+bmpW > topRight[0]: cr = x+bmpW-topRight[0]
                else: cr = 0
                y = int(topLeft[1]/bmpH)*bmpH
                if y < topLeft[1]:
                    posy = topLeft[1]
                    ct = topLeft[1]-y
                else:
                    ct = 0
                    posy = y
                while y < topRight[1]:
                    if y+bmpH > topRight[1]: cb = y+bmpH-topRight[1]
                    else: cb = 0
                    newW = bmpW-cr-cl
                    newH = bmpH-cb-ct
                    if newW < 0: newW = 0
                    if newH < 0:  newH = 0
                    dc.DrawBitmap(self.bg_bmp, posx, posy)
                    dc.Blit(posx, posy, newW, newH, dc2, cl, ct)
                    ct = 0
                    y = y+bmpH
                    posy = y
                cl = 0
                x = x+bmpW
                posx = x
        elif self.type == BG_IMAGE:
            x = 0
            y = 0
            if x < topLeft[0]:
                posx = topLeft[0]
                cl = topLeft[0]-x
            else:
                cl = 0
                posx = x
            if y < topLeft[1]:
                posy = topLeft[1]
                ct = topLeft[1]-y
            else:
                ct = 0
                posy = y
            if x+bmpW > topRight[0]: cr = x+bmpW-topRight[0]
            else: cr = 0
            if y+bmpH > topRight[1]: cb = y+bmpH-topRight[1]
            else: cb = 0
            newW = bmpW-cr-cl
            newH = bmpH-cb-ct
            if newW < 0: newW = 0
            if newH < 0: newH = 0
            dc.DrawBitmap(self.bg_bmp, posx, posy)
            dc.Blit(posx, posy, newW, newH, dc2, cl, ct)
        dc2.SelectObject(wx.NullBitmap)
        del dc2
        return True

    @debugging
    def layerToXML(self, action="update"):
        xml_str = "<bg"
        if self.bg_color != None:
            (red,green,blue) = self.bg_color.Get()
            hexcolor = self.r_h.hexstring(red, green, blue)
            xml_str += ' color="' + hexcolor + '"'
        if self.img_path != None: xml_str += ' path="' + urllib.quote(self.img_path).replace('%3A', ':') + '"'
        if self.type != None: xml_str += ' type="' + str(self.type) + '"'
        if self.local and self.img_path != None:
            xml_str += ' local="True"'
            xml_str += ' localPath="' + urllib.quote(self.localPath).replace('%3A', ':') + '"'
            xml_str += ' localTime="' + str(self.localTime) + '"'
        xml_str += "/>"
        logger.debug(xml_str)
        if (action == "update" and self.isUpdated) or action == "new":
            self.isUpdated = False
            return xml_str
        else: return ''

    @debugging
    def layerTakeDOM(self, xml_dom):
        type = BG_COLOR
        color = xml_dom.getAttribute("color")
        logger.debug("color=" + color)
        path = urllib.unquote(xml_dom.getAttribute("path"))
        logger.debug("path=" + path)
        # Begin ted's map changes
        if xml_dom.hasAttribute("color"):
            r,g,b = self.r_h.rgb_tuple(xml_dom.getAttribute("color"))
            self.set_color(cmpColour(r,g,b))
        # End ted's map changes
        if xml_dom.hasAttribute("type"):
            type = int(xml_dom.getAttribute("type"))
            logger.debug("type=" + str(type))
        if type == BG_TEXTURE:
            if path != "": self.set_texture(path)
        elif type == BG_IMAGE:
            if path != "": self.set_image(path, 1)
        elif type == BG_NONE: self.clear()
        if xml_dom.hasAttribute('local') and xml_dom.getAttribute('local') == 'True' and os.path.exists(urllib.unquote(xml_dom.getAttribute('localPath'))):
            self.localPath = urllib.unquote(xml_dom.getAttribute('localPath'))
            self.local = True
            self.localTime = int(xml_dom.getAttribute('localTime'))
            if self.localTime-time.time() <= 144000:
                file = open(self.localPath, "rb")
                imgdata = file.read()
                file.close()
                filename = os.path.split(self.localPath)
                (imgtype,j) = mimetypes.guess_type(filename[1])
                postdata = urllib.urlencode({'filename':filename[1], 'imgdata':imgdata, 'imgtype':imgtype})
                thread.start_new_thread(self.upload, (postdata, self.localPath, type))

    @debugging
    def upload(self, postdata, filename, type):
        self.lock.acquire()
        if type == 'Image' or type == 'Texture':
            url = component.get('settings').get_setting('ImageServerBaseURL')
            file = urllib.urlopen(url, postdata)
            recvdata = file.read()
            file.close()
            try:
                xml_dom = minidom.parseString(recvdata)._get_documentElement()
                if xml_dom.nodeName == 'path':
                    path = xml_dom.getAttribute('url')
                    path = urllib.unquote(path)
                    if type == 'Image': self.set_image(path, 1)
                    else: self.set_texture(path)
                    self.localPath = filename
                    self.local = True
                    self.localTime = time.time()
                else:
                    print xml_dom.getAttribute('msg')
            except Exception, e:
                print e
                print recvdata
        self.lock.release()
