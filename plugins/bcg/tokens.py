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
# File: mapper/tokens.py
# Author: Chris Davis
# Maintainer:
# Version:
#   $Id: tokens.py,v 1.46 2007/12/07 20:39:50 digitalxero Exp $
#
# Description: This file contains some of the basic definitions for the chat
# utilities in the orpg project.
#
__version__ = "$Id: tokens.py,v 1.46 2007/12/07 20:39:50 digitalxero Exp $"

from orpg.mapper.base import *
import thread
import time
import urllib
import os.path

from orpg.tools.orpg_settings import settings

MIN_STICKY_BACK = -0XFFFFFF
MIN_STICKY_FRONT = 0xFFFFFF

##----------------------------------------
##  token object
##----------------------------------------

FACE_NONE = 0
FACE_NORTH = 1
FACE_NORTHEAST = 2
FACE_EAST = 3
FACE_SOUTHEAST = 4
FACE_SOUTH = 5
FACE_SOUTHWEST = 6
FACE_WEST = 7
FACE_NORTHWEST = 8
SNAPTO_ALIGN_CENTER = 0
SNAPTO_ALIGN_TL = 1

def cmp_zorder(first,second):
    f = first.zorder
    s = second.zorder
    if f == None: f = 0
    if s == None: s = 0
    if f == s: value = 0
    elif f < s: value = -1
    else: value = 1
    return value

class BmpToken:
    def __init__(self, id,path, bmp, pos=cmpPoint(0,0), 
                heading=FACE_NONE, rotate=0, label="", 
                locked=False, hide=False, snap_to_align=SNAPTO_ALIGN_CENTER, 
                zorder=0, width=0, height=0, log=None, local=False, localPath='', localTime=-1):
        self.heading = heading
        self.rotate = rotate
        self.label = label
        self.path = path
        self.bmp = bmp
        self.pos = pos
        self.selected = False
        self.locked = locked
        self.snap_to_align = snap_to_align
        self.hide = hide
        self.id = id
        self.zorder = zorder
        self.left = 0
        self.local = local
        self.localPath = localPath
        self.localTime = localTime
        if not width: self.width = 0
        else: self.width = width
        if not height: self.height = 0
        else: self.height = height
        self.right = bmp.GetWidth()
        self.top = 0
        self.bottom = bmp.GetHeight()
        self.isUpdated = False
        self.gray = False
        self.drawn = {}

    def __del__(self):
        del self.bmp
        self.bmp = None

    def set_bmp(self, bmp):
        self.bmp = bmp

    def set_min_props(self, heading=FACE_NONE, rotate=0, label="", locked=False, hide=False, width=0, height=0):
        self.heading = heading
        self.rotate = rotate
        self.label = label
        if locked: self.locked = True
        else: self.locked = False
        if hide: self.hide = True
        else: self.hide = False
        self.width = int(width)
        self.height = int(height)
        self.isUpdated = True

    def hit_test(self, pt):
        rect = self.get_rect()
        result = None
        result = rect.InsideXY(pt.x, pt.y)
        return result

    def get_rect(self):
        ret = wx.Rect(self.pos.x, self.pos.y, self.bmp.GetWidth(), self.bmp.GetHeight())
        return ret

    def draw(self, dc, mini_layer, op=wx.COPY):
        if isinstance(self.bmp, tuple):
            self.bmp = wx.ImageFromMime(self.bmp[1], self.bmp[2]).ConvertToBitmap()
        if self.bmp != None and self.bmp.Ok():
            # check if hidden and GM: we outline the mini in grey (little bit smaller than the actual size)
            # and write the label in the center of the mini
            if self.hide and mini_layer.canvas.frame.session.my_role() == mini_layer.canvas.frame.session.ROLE_GM:
                # set the width and height of the image
                if self.width and self.height:
                    tmp_image = self.bmp.ConvertToImage()
                    tmp_image.Rescale(int(self.width), int(self.height))
                    tmp_image.ConvertAlphaToMask()
                    self.bmp = tmp_image.ConvertToBitmap()
                    mask = wx.Mask(self.bmp, wx.Colour(tmp_image.GetMaskRed(), 
                        tmp_image.GetMaskGreen(), tmp_image.GetMaskBlue()))
                    self.bmp.SetMask(mask)
                    del tmp_image
                    del mask
                self.left = 0
                self.right = self.bmp.GetWidth()
                self.top = 0
                self.bottom = self.bmp.GetHeight()
                # grey outline
                graypen = wx.Pen("gray", 1, wx.DOT)
                dc.SetPen(graypen)
                dc.SetBrush(wx.TRANSPARENT_BRUSH)
                #if width or height < 20 then offset = 1
                if self.bmp.GetWidth() <= 20: xoffset = 1
                else: xoffset = 5
                if self.bmp.GetHeight() <= 20: yoffset = 1
                else: yoffset = 5
                dc.DrawRectangle(self.pos.x + xoffset, 
                    self.pos.y + yoffset, self.bmp.GetWidth() - (xoffset * 2), 
                    self.bmp.GetHeight() - (yoffset * 2))
                dc.SetBrush(wx.NullBrush)
                dc.SetPen(wx.NullPen)
                ## draw label in the center of the mini
                label = mini_layer.get_mini_label(self)
                if len(label):
                    dc.SetTextForeground(wx.RED)
                    (textWidth,textHeight) = dc.GetTextExtent(label)
                    x = self.pos.x +((self.bmp.GetWidth() - textWidth) /2) - 1
                    y = self.pos.y + (self.bmp.GetHeight() / 2)
                    dc.SetPen(wx.GREY_PEN)
                    dc.SetBrush(wx.LIGHT_GREY_BRUSH)
                    dc.DrawRectangle(x, y, textWidth+2, textHeight+2)
                    if (textWidth+2 > self.right):
                        self.right += int((textWidth+2-self.right)/2)+1
                        self.left -= int((textWidth+2-self.right)/2)+1
                    self.bottom = y+textHeight+2-self.pos.y
                    dc.SetPen(wx.NullPen)
                    dc.SetBrush(wx.NullBrush)
                    dc.DrawText(label, x+1, y+1)

                #selected outline
                if self.selected:
                    dc.SetPen(wx.RED_PEN)
                    dc.SetBrush(wx.TRANSPARENT_BRUSH)
                    dc.DrawRectangle(self.pos.x, self.pos.y, self.bmp.GetWidth(), self.bmp.GetHeight())
                    dc.SetBrush(wx.NullBrush)
                    dc.SetPen(wx.NullPen)
                return True
            elif self.hide: return True

            else:
                # set the width and height of the image
                bmp = self.bmp
                if self.width and self.height:
                    tmp_image = self.bmp.ConvertToImage()
                    tmp_image.Rescale(int(self.width), int(self.height))
                    tmp_image.ConvertAlphaToMask()
                    self.bmp = tmp_image.ConvertToBitmap()
                    mask = wx.Mask(self.bmp, wx.Colour(tmp_image.GetMaskRed(), 
                        tmp_image.GetMaskGreen(), tmp_image.GetMaskBlue()))
                    self.bmp.SetMask(mask)
                    if self.gray:
                        tmp_image = tmp_image.ConvertToGreyscale()
                        bmp = tmp_image.ConvertToBitmap()
                    else: bmp = self.bmp

                if self.rotate != 0:
                    x = bmp.GetWidth(); print x
                    y = bmp.GetHeight(); print y
                    img = bmp.ConvertToImage()
                    img = img.Rotate(self.rotate, (3, 80), True)
                    img.ConvertAlphaToMask()

                    bmp = img.ConvertToBitmap()
                    mask = wx.Mask(bmp, wx.Colour(img.GetMaskRed(), 
                        img.GetMaskGreen(), img.GetMaskBlue()))
                    bmp.SetMask(mask)

                dc.DrawBitmap(bmp, self.pos.x, self.pos.y, True)
                component.get('drawn')[bmp] = True
                self.left = 0
                self.right = self.bmp.GetWidth()
                self.top = 0
                self.bottom = self.bmp.GetHeight()

                # Draw the heading if needed
                if self.heading:
                    x_adjust = 0
                    y_adjust = 4
                    x_half = self.bmp.GetWidth()/2
                    y_half = self.bmp.GetHeight()/2
                    x_quarter = self.bmp.GetWidth()/4
                    y_quarter = self.bmp.GetHeight()/4
                    x_3quarter = x_quarter*3
                    y_3quarter = y_quarter*3
                    x_full = self.bmp.GetWidth()
                    y_full = self.bmp.GetHeight()
                    x_center = self.pos.x + x_half
                    y_center = self.pos.y + y_half
                    # Remember, the pen/brush must be a different color than the
                    # facing marker!!!!  We'll use black/cyan for starters.
                    # Also notice that we will draw the heading on top of the
                    # larger facing marker.
                    dc.SetPen(wx.BLACK_PEN)
                    dc.SetBrush(wx.CYAN_BRUSH)
                    triangle = []

                    # Figure out which direction to draw the marker!!
                    if self.heading == FACE_NORTH:
                        triangle.append(cmpPoint(x_center - x_quarter, y_center - y_half ))
                        triangle.append(cmpPoint(x_center, y_center - y_3quarter ))
                        triangle.append(cmpPoint(x_center + x_quarter, y_center - y_half ))
                    elif self.heading ==  FACE_SOUTH:
                        triangle.append(cmpPoint(x_center - x_quarter, y_center + y_half ))
                        triangle.append(cmpPoint(x_center, y_center + y_3quarter ))
                        triangle.append(cmpPoint(x_center + x_quarter, y_center + y_half ))
                    elif self.heading == FACE_NORTHEAST:
                        triangle.append(cmpPoint(x_center + x_quarter, y_center - y_half ))
                        triangle.append(cmpPoint(x_center + x_3quarter, y_center - y_3quarter ))
                        triangle.append(cmpPoint(x_center + x_half, y_center - y_quarter ))
                    elif self.heading == FACE_EAST:
                        triangle.append(cmpPoint(x_center + x_half, y_center - y_quarter ))
                        triangle.append(cmpPoint(x_center + x_3quarter, y_center ))
                        triangle.append(cmpPoint(x_center + x_half, y_center + y_quarter ))
                    elif self.heading == FACE_SOUTHEAST:
                        triangle.append(cmpPoint(x_center + x_half, y_center + y_quarter ))
                        triangle.append(cmpPoint(x_center + x_3quarter, y_center + y_3quarter ))
                        triangle.append(cmpPoint(x_center + x_quarter, y_center + y_half ))
                    elif self.heading == FACE_SOUTHWEST:
                        triangle.append(cmpPoint(x_center - x_quarter, y_center + y_half ))
                        triangle.append(cmpPoint(x_center - x_3quarter, y_center + y_3quarter ))
                        triangle.append(cmpPoint(x_center - x_half, y_center + y_quarter ))
                    elif self.heading == FACE_WEST:
                        triangle.append(cmpPoint(x_center - x_half, y_center + y_quarter ))
                        triangle.append(cmpPoint(x_center - x_3quarter, y_center ))
                        triangle.append(cmpPoint(x_center - x_half, y_center - y_quarter ))
                    elif self.heading == FACE_NORTHWEST:
                        triangle.append(cmpPoint(x_center - x_half, y_center - y_quarter ))
                        triangle.append(cmpPoint(x_center - x_3quarter, y_center - y_3quarter ))
                        triangle.append(cmpPoint(x_center - x_quarter, y_center - y_half ))
                    dc.DrawPolygon(triangle)
                    dc.SetBrush(wx.NullBrush)
                    dc.SetPen(wx.NullPen)
                #selected outline
                if self.selected:
                    dc.SetPen(wx.RED_PEN)
                    dc.SetBrush(wx.TRANSPARENT_BRUSH)
                    dc.DrawRectangle(self.pos.x, self.pos.y, self.bmp.GetWidth(), self.bmp.GetHeight())
                    dc.SetBrush(wx.NullBrush)
                    dc.SetPen(wx.NullPen)
                # draw label
                label = mini_layer.get_mini_label(self)
                if len(label):
                    dc.SetTextForeground(wx.RED)
                    (textWidth,textHeight) = dc.GetTextExtent(label)
                    x = self.pos.x +((self.bmp.GetWidth() - textWidth) /2) - 1
                    y = self.pos.y + self.bmp.GetHeight() + 6
                    dc.SetPen(wx.WHITE_PEN)
                    dc.SetBrush(wx.WHITE_BRUSH)
                    dc.DrawRectangle(x,y,textWidth+2,textHeight+2)
                    if (textWidth+2 > self.right):
                        self.right += int((textWidth+2-self.right)/2)+1
                        self.left -= int((textWidth+2-self.right)/2)+1
                    self.bottom = y+textHeight+2-self.pos.y
                    dc.SetPen(wx.NullPen)
                    dc.SetBrush(wx.NullBrush)
                    dc.DrawText(label,x+1,y+1)
                self.top-=5
                self.bottom+=5
                self.left-=5
                self.right+=5
                return True
        else: return False

    def toxml(self, action="update"):
        if action == "del":
            xml_str = "<token action='del' id='" + self.id + "'/>"
            return xml_str
        xml_str = "<token"
        xml_str += " action='" + action + "'"
        xml_str += " label='" + self.label + "'"
        xml_str+= " id='" + self.id + "'"
        if self.pos != None:
            xml_str += " posx='" + str(self.pos.x) + "'"
            xml_str += " posy='" + str(self.pos.y) + "'"
        if self.heading != None: xml_str += " heading='" + str(self.heading) + "'"
        if self.rotate != None: xml_str += " rotate='" + str(self.rotate) + "'"
        if self.path != None: xml_str += " path='" + urllib.quote(self.path).replace('%3A', ':') + "'"
        if self.locked: xml_str += "  locked='1'"
        else: xml_str += "  locked='0'"
        if self.hide: xml_str += " hide='1'"
        else: xml_str += " hide='0'"
        if self.snap_to_align != None: xml_str += " align='" + str(self.snap_to_align) + "'"
        if self.id != None: xml_str += " zorder='" + str(self.zorder) + "'"
        if self.width != None: xml_str += " width='" + str(self.width) + "'"
        if self.height != None: xml_str += " height='" + str(self.height) + "'"
        if self.local:
            xml_str += ' local="' + str(self.local) + '"'
            xml_str += ' localPath="' + str(urllib.quote(self.localPath).replace('%3A', ':')) + '"'
            xml_str += ' localTime="' + str(self.localTime) + '"'
        xml_str += " />"
        if (action == "update" and self.isUpdated) or action == "new":
            self.isUpdated = False
            return xml_str
        else: return ''

    def takedom(self, xml_dom):
        self.id = xml_dom.getAttribute("id")
        if xml_dom.hasAttribute("posx"):
            self.pos.x = int(xml_dom.getAttribute("posx"))
        if xml_dom.hasAttribute("posy"):
            self.pos.y = int(xml_dom.getAttribute("posy"))
        if xml_dom.hasAttribute("heading"):
            self.heading = int(xml_dom.getAttribute("heading"))
        if xml_dom.hasAttribute("rotate"):
            self.rotate = int(xml_dom.getAttribute("rotate"))
        if xml_dom.hasAttribute("path"):
            self.path = urllib.unquote(xml_dom.getAttribute("path"))
            self.set_bmp(ImageHandler.load(self.path, 'token', self.id))
        if xml_dom.hasAttribute("locked"):
            if xml_dom.getAttribute("locked") == '1' or xml_dom.getAttribute("locked") == 'True': self.locked = True
            else: self.locked = False
        if xml_dom.hasAttribute("hide"):
            if xml_dom.getAttribute("hide") == '1' or xml_dom.getAttribute("hide") == 'True': self.hide = True
            else: self.hide = False
        if xml_dom.hasAttribute("label"):
            self.label = xml_dom.getAttribute("label")
        if xml_dom.hasAttribute("zorder"):
            self.zorder = int(xml_dom.getAttribute("zorder"))
        if xml_dom.hasAttribute("align"):
            if xml_dom.getAttribute("align") == '1' or xml_dom.getAttribute("align") == 'True': self.snap_to_align = 1
            else: self.snap_to_align = 0
        if xml_dom.hasAttribute("width"):
            self.width = int(xml_dom.getAttribute("width"))
        if xml_dom.hasAttribute("height"):
            self.height = int(xml_dom.getAttribute("height"))

##-----------------------------
## token layer
##-----------------------------
class token_layer(layer_base):
    def __init__(self, canvas):
        self.canvas = canvas
        layer_base.__init__(self)
        self.id = -1 #added.
        self.tokens = []
        self.serial_number = 0

        self.drawn = {}
        component.add('drawn', self.drawn)
        # Set the font of the labels to be the same as the chat window
        # only smaller.
        font_size = int(settings.get_setting('defaultfontsize'))
        if (font_size >= 10): font_size -= 2
        self.label_font = wx.Font(font_size, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL,
                                  False, settings.get_setting('defaultfont'))

    def next_serial(self):
        self.serial_number += 1
        return self.serial_number

    def get_next_highest_z(self):
        z = len(self.tokens)+1
        return z

    def cleanly_collapse_zorder(self):
        #  lock the zorder stuff
        sorted_tokens = self.tokens[:]
        sorted_tokens.sort(cmp_zorder)
        i = 0
        for mini in sorted_tokens:
            mini.zorder = i
            i = i + 1
        #  unlock the zorder stuff

    def collapse_zorder(self):
        #  lock the zorder stuff
        sorted_tokens = self.tokens[:]
        sorted_tokens.sort(cmp_zorder)
        i = 0
        for mini in sorted_tokens:
            if (mini.zorder != MIN_STICKY_BACK) and (mini.zorder != MIN_STICKY_FRONT): mini.zorder = i
            else: pass
            i = i + 1
        #  unlock the zorder stuff

    def rollback_serial(self):
        self.serial_number -= 1

    def add_token(self, id, path, pos=cmpPoint(0,0), label="", heading=FACE_NONE, 
            rotate=0, width=0, height=0, local=False, localPath='', localTime=-1):
        bmp = ImageHandler.load(path, 'token', id)
        if bmp:
            mini = BmpToken(id, path, bmp, pos, heading, rotate, label, 
                zorder=self. get_next_highest_z(), width=width, 
                height=height, local=local, localPath=localPath, localTime=localTime)
            self.tokens.append(mini)
            self.drawn[mini.bmp] = False
            xml_str = "<map><tokens>"
            xml_str += mini.toxml("new")
            xml_str += "</tokens></map>"
            component.get('session').send(xml_str)

    def get_token_by_id(self, id):
        for mini in self.tokens:
            if str(mini.id) == str(id):
                return mini
        return None

    def del_token(self, min):
        xml_str = "<map><tokens>"
        xml_str += min.toxml("del")
        xml_str += "</tokens></map>"
        self.canvas.frame.session.send(xml_str)
        self.tokens.remove(min)
        del min
        self.collapse_zorder()

    def del_all_tokens(self):
        while len(self.tokens):
            min = self.tokens.pop()
            del min
        self.collapse_zorder()

    def layerDraw(self, dc, topleft, size):
        dc.SetFont(self.label_font)
        sorted_tokens = self.tokens[:]
        sorted_tokens.sort(cmp_zorder)
        for m in sorted_tokens:
            if (m.pos.x>topleft[0]-m.right and
                m.pos.y>topleft[1]-m.bottom and
                m.pos.x<topleft[0]+size[0]-m.left and
                m.pos.y<topleft[1]+size[1]-m.top):
                """
                if self.drawn.has_key(m.bmp):
                    if self.drawn[m.bmp] == True:
                        dc2 = wx.MemoryDC()
                        img = m.bmp.ConvertToImage()
                        bmp = img.ConvertToBitmap()

                        dc2.SelectObject(bmp)
                        dc.Blit(m.pos.x, m.pos.y, img.GetHeight(), img.GetWidth(), dc2, 0, 0, wx.COPY, True, 0, 0)
                        del dc2
                
                else:
                """
                m.draw(dc, self)

    def find_token(self, pt, only_unlocked=False):
        min_list = []
        for m in self.tokens:
            if m.hit_test(pt):
                if m.hide and self.canvas.frame.session.my_role() != self.canvas.frame.session.ROLE_GM: continue
                if only_unlocked and not m.locked: min_list.append(m)
                elif not only_unlocked and m.locked: min_list.append(m)
                else: continue
        if len(min_list) > 0:
            return min_list
        else: return None

    def layerToXML(self, action="update"):
        """ format  """
        minis_string = ""
        if self.tokens:
            for m in self.tokens: minis_string += m.toxml(action)
        if minis_string != '':
            s = "<tokens"
            s += " serial='" + str(self.serial_number) + "'"
            s += ">"
            s += minis_string
            s += "</tokens>"
            return s
        else: return ""

    def layerTakeDOM(self, xml_dom):
        if xml_dom.hasAttribute('serial'):
            self.serial_number = int(xml_dom.getAttribute('serial'))
        children = xml_dom._get_childNodes()
        for c in children:
            action = c.getAttribute("action")
            id = c.getAttribute('id')
            if action == "del": 
                mini = self.get_token_by_id(id)
                if mini:
                    self.tokens.remove(mini)
                    del mini
            elif action == "new":
                pos = cmpPoint(int(c.getAttribute('posx')),int(c.getAttribute('posy')))
                path = urllib.unquote(c.getAttribute('path'))
                label = c.getAttribute('label')
                height = width = heading = rotate = snap_to_align = zorder = 0
                locked = hide = False
                if c.hasAttribute('height'): height = int(c.getAttribute('height'))
                if c.hasAttribute('width'): width = int(c.getAttribute('width'))
                if c.getAttribute('locked') == 'True' or c.getAttribute('locked') == '1': locked = True
                if c.getAttribute('hide') == 'True' or c.getAttribute('hide') == '1': hide = True
                if c.getAttribute('heading'): heading = int(c.getAttribute('heading'))
                if c.hasAttribute('rotate'): rotate = int(c.getAttribute('rotate'))
                if c.hasAttribute('align'): snap_to_align = int(c.getAttribute('align'))
                if c.getAttribute('zorder'): zorder = int(c.getAttribute('zorder'))
                min = BmpToken(id, path, ImageHandler.load(path, 'token', id), pos, heading, 
                    rotate, label, locked, hide, snap_to_align, zorder, width, height)
                self.tokens.append(min)
                if c.hasAttribute('local') and c.getAttribute('local') == 'True' and os.path.exists(urllib.unquote(c.getAttribute('localPath'))):
                    localPath = urllib.unquote(c.getAttribute('localPath'))
                    local = True
                    localTime = float(c.getAttribute('localTime'))
                    if localTime-time.time() <= 144000:
                        file = open(localPath, "rb")
                        imgdata = file.read()
                        file.close()
                        filename = os.path.split(localPath)
                        (imgtype,j) = mimetypes.guess_type(filename[1])
                        postdata = urllib.urlencode({'filename':filename[1], 'imgdata':imgdata, 'imgtype':imgtype})
                        thread.start_new_thread(self.upload, (postdata, localPath, True))
                #  collapse the zorder.  If the client behaved well, then nothing should change.
                #    Otherwise, this will ensure that there's some kind of z-order
                self.collapse_zorder()
            else:
                mini = self.get_token_by_id(id)
                if mini: mini.takedom(c)

    def upload(self, postdata, filename, modify=False, pos=cmpPoint(0,0)):
        self.lock.acquire()
        url = settings.get_setting('ImageServerBaseURL')
        file = urllib.urlopen(url, postdata)
        recvdata = file.read()
        file.close()
        try:
            xml_dom = minidom.parseString(recvdata)._get_documentElement()
            if xml_dom.nodeName == 'path':
                path = xml_dom.getAttribute('url')
                path = urllib.unquote(path)
                if not modify:
                    start = path.rfind("/") + 1
                    if self.canvas.parent.layer_handlers[2].auto_label: min_label = path[start:len(path)-4]
                    else: min_label = ""
                    id = 'mini-' + self.canvas.frame.session.get_next_id()
                    self.add_token(id, path, pos=pos, label=min_label, local=True, 
                        localPath=filename, localTime=time.time())
                else:
                    self.tokens[len(self.tokens)-1].local = True
                    self.tokens[len(self.tokens)-1].localPath = filename
                    self.tokens[len(self.tokens)-1].localTime = time.time()
                    self.tokens[len(self.tokens)-1].path = path
            else:
                print xml_dom.getAttribute('msg')
        except Exception, e:
            print e
            print recvdata
        urllib.urlcleanup()
        self.lock.release()
####################################################################
        ## helper function

    def get_mini_label(self, mini):
        # override this to change the label displayed under each mini (and the label on hidden minis)
        return mini.label
