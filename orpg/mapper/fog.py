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
# File: mapper/fog.py
# Author: OpenRPG Team
#
# Description: Maintenance of data structures required for FoW
#

import sys
from base import *
from random import Random
from region import *
from orpg.minidom import Element
import traceback
COURSE = 10

class FogArea:
    def __init__(self, outline, log):
        self.log = log
        self.outline = outline

    def set_fog_props(self, str):
        self.outline = str

    def points_to_elements(self, points=None):
        result = []
        if points == None:
            return result

        for pairs in string.split( points, ';' ):
            pair = string.split( pairs, ',' )
            p = Element( "point" )
            p.setAttribute( "x", pair[0] )
            p.setAttribute( "y", pair[1] )
            result.append( p )
        return result

    def toxml(self, action="update"):
        xml_str = ""
        localOutline = self.outline
        if localOutline != None and localOutline != "all" and localOutline != "none":
            localOutline = "points"
        elem = Element( "poly" )
        if action == "del":
            elem.setAttribute( "action", action )
            elem.setAttribute( "outline", localOutline )
            if localOutline == 'points':
                list = self.points_to_elements( self.outline )
                for p in list: elem.appendChild( p )
            str = elem.toxml()
            elem.unlink()
            return str
        elem.setAttribute( "action", action )
        if  localOutline != None:
            elem.setAttribute( "outline", localOutline )
            if localOutline == 'points':
                list = self.points_to_elements( self.outline )
                for p in list: elem.appendChild( p )
        xml_str = elem.toxml()
        elem.unlink()
        return xml_str

class fog_layer(layer_base):
    def __init__(self, canvas):
        self.canvas = canvas
        self.log = component.get('log')
        layer_base.__init__(self)
        self.color = wx.Color(128,128,128)
        if "__WXGTK__" not in wx.PlatformInfo: self.color = wx.Color(128,128,128, 128)
        self.fogregion = wx.Region()
        self.fogregion.Clear()
        self.fog_bmp = None
        self.width = 0
        self.height = 0
        self.use_fog = False
        self.last_role = ""

    def clear(self):
        self.fogregion.Clear()
        self.use_fog = True
        self.del_area("all")
        self.recompute_fog()

    def remove_fog(self):
        self.fogregion.Clear()
        self.use_fog = False
        self.del_area("all")
        self.add_area("none")
        self.fog_bmp = None

    def resize(self, size):
        try:
            if self.width == size[0] and self.height == size[1]:
                return
            self.recompute_fog()
        except: pass

    def recompute_fog(self):
        if not self.use_fog:
            return
        size = self.canvas.size
        self.width = size[0]/COURSE+1
        self.height = size[1]/COURSE+1
        self.fog_bmp = wx.EmptyBitmap(self.width+2,self.height+2)
        self.fill_fog()

    def fill_fog(self):
        if not self.use_fog:
            return
        if "__WXGTK__" in wx.PlatformInfo:
            mdc = wx.MemoryDC()
            mdc.SelectObject(self.fog_bmp)
            mdc.SetPen(wx.TRANSPARENT_PEN)
            if (self.canvas.frame.session.role == "GM"): color = self.color
            else: color = wx.BLACK
            self.last_role = self.canvas.frame.session.role
            mdc.SetBrush(wx.Brush(color,wx.SOLID))
            mdc.DestroyClippingRegion()
            mdc.DrawRectangle(0, 0, self.width+2, self.height+2)
            mdc.SetBrush(wx.Brush(wx.WHITE, wx.SOLID))
            if self.fogregion.GetBox().GetWidth()>0:
                mdc.SetClippingRegionAsRegion(self.fogregion)
                mdc.DrawRectangle(0, 0, self.width+2, self.height+2)
            mdc.SelectObject(wx.NullBitmap)
            del mdc

    def layerDraw(self, dc, topleft, size):
        if self.fog_bmp == None or not self.fog_bmp.Ok() or not self.use_fog:
            return
        if self.last_role != self.canvas.frame.session.role: self.fill_fog()
        if "__WXGTK__" not in wx.PlatformInfo:
            gc = wx.GraphicsContext.Create(dc)
            gc.SetBrush(wx.Brush(wx.BLACK))
            if (self.canvas.frame.session.role == "GM"):
                gc.SetBrush(wx.Brush(self.color))
            rgn = wx.Region(0, 0, self.canvas.size[0]+2, self.canvas.size[1]+2)
            if not self.fogregion.IsEmpty(): rgn.SubtractRegion(self.fogregion)
            gc.ClipRegion(rgn)
            gc.DrawRectangle(0, 0, self.canvas.size[0]+2, self.canvas.size[1]+2)
        else:
            sc = dc.GetUserScale()
            bmp = wx.EmptyBitmap(size[0],size[1])
            mdc = wx.MemoryDC()
            mdc.BeginDrawing()
            mdc.SelectObject(bmp)
            mdc.SetPen(wx.TRANSPARENT_PEN)
            mdc.SetBrush(wx.Brush(wx.WHITE, wx.SOLID))
            mdc.DrawRectangle(0,0,size[0],size[1])
            srct = [int(topleft[0]/(sc[0]*COURSE)), int(topleft[1]/(sc[1]*COURSE))]
            srcsz = [int((int(size[0]/COURSE+1)*COURSE)/(sc[0]*COURSE))+2, 
                int((int(size[1]/COURSE+1)*COURSE)/(sc[1]*COURSE))+2]
            if (srct[0]+srcsz[0] > self.width): srcsz[0] = self.width-srct[0]
            if (srct[1]+srcsz[1] > self.height): srcsz[1] = self.height-srct[1]
            img = wx.ImageFromBitmap(self.fog_bmp).GetSubImage(wx.Rect(srct[0], srct[1], srcsz[0], srcsz[1]))
            img.Rescale(srcsz[0]*COURSE*sc[0], srcsz[1]*COURSE*sc[1])
            fog = wx.BitmapFromImage(img)
            mdc.SetDeviceOrigin(-topleft[0], -topleft[1])
            mdc.DrawBitmap(fog, srct[0]*COURSE*sc[0], srct[1]*COURSE*sc[1])
            mdc.SetDeviceOrigin(0,0)
            mdc.SetUserScale(1,1)
            mdc.EndDrawing()
            dc.SetUserScale(1,1)
            dc.Blit(topleft[0], topleft[1], size[0], size[1], mdc,0,0,wx.AND)
            dc.SetUserScale(sc[0],sc[1])
            mdc.SelectObject(wx.NullBitmap)
            del mdc

    def createregn2(self, polyline, mode, show):
        regn = self.scanConvert(polyline)
        area = ""
        for i in polyline:
            if (area != ""):
                area += ";"
            area += str(i.X) + "," + str(i.Y)
        if mode == 'new':
            if self.fogregion.IsEmpty():
                self.fogregion = regn
            else: self.fogregion.UnionRegion(regn)
            self.add_area(area, show)
        else:
            if not self.fogregion.IsEmpty():
                self.fogregion.SubtractRegion(regn)
            else:
                self.fogregion = wx.Region(0, 0, self.canvas.size[0]+2, self.canvas.size[1]+2)
                self.fogregion.SubtractRegion(regn)
            self.del_area(area, show)

    def createregn(self, polyline, mode, show="Yes"):
        if not self.use_fog and mode == 'del':
            self.clear()
            self.canvas.Refresh(False)
        if self.use_fog:
            self.createregn2(polyline, mode, show)
            self.fill_fog()

    def scanConvert(self, polypt):
        regn = wx.Region()
        regn.Clear()
        list = IRegion().scan_Convert(polypt)
        for i in list:
            if regn.IsEmpty():
                if "__WXGTK__" not in wx.PlatformInfo: regn = wx.Region(i.left*COURSE, i.y*COURSE, 
                                                                        i.right*COURSE+1-i.left*COURSE, 1*COURSE)
                else: regn = wx.Region(i.left, i.y, i.right+1-i.left, 1)
            else:
                if "__WXGTK__" not in wx.PlatformInfo: regn.Union(i.left*COURSE, i.y*COURSE, 
                                                                i.right*COURSE+1-i.left*COURSE, 1*COURSE)
                else: regn.Union(i.left, i.y, i.right+1-i.left, 1)
        return regn

    def add_area(self, area="", show="Yes"):
        poly = FogArea(area, self.log)
        xml_str = "<map><fog>"
        xml_str += poly.toxml("new")
        xml_str += "</fog></map>"
        if show == "Yes": self.canvas.frame.session.send(xml_str)

    def del_area(self, area="", show="Yes"):
        poly = FogArea(area, self.log)
        xml_str = "<map><fog>"
        xml_str += poly.toxml("del")
        xml_str += "</fog></map>"
        if show == "Yes": self.canvas.frame.session.send(xml_str)

    def layerToXML(self, action="update"):
        if not self.use_fog:
            return ""
        fog_string = ""
        ri = wx.RegionIterator(self.fogregion)
        if not (ri.HaveRects()): fog_string = FogArea("all", self.log).toxml("del")
        while ri.HaveRects():
            if "__WXGTK__" not in wx.PlatformInfo:
                x1 = ri.GetX()/COURSE
                x2 = x1+(ri.GetW()/COURSE)-1
                y1 = ri.GetY()/COURSE
                y2 = y1+(ri.GetH()/COURSE)-1
            else:
                x1 = ri.GetX()
                x2 = x1+ri.GetW()-1
                y1 = ri.GetY()
                y2 = y1+ri.GetH()-1
            poly = FogArea(str(x1) + "," + str(y1) + ";" +
                          str(x2) + "," + str(y1) + ";" +
                          str(x2) + "," + str(y2) + ";" +
                          str(x1) + "," + str(y2), self.log)
            fog_string += poly.toxml(action)
            ri.Next()
        if fog_string:
            s = "<fog"
            s += ">"
            s += fog_string
            s += "</fog>"
            return s
        else:
            return ""

    def layerTakeDOM(self, xml_dom):
        try:
            if not self.use_fog:
                self.use_fog = True
                self.recompute_fog()
            if xml_dom.hasAttribute('serial'): self.serial_number = int(xml_dom.getAttribute('serial'))
            children = xml_dom._get_childNodes()
            for l in children:
                action = l.getAttribute("action")
                outline = l.getAttribute("outline")
                if (outline == "all"):
                    polyline = [IPoint().make(0,0), IPoint().make(self.width-1, 0),
                              IPoint().make(self.width-1, self.height-1),
                              IPoint().make(0, self.height-1)]
                elif (outline == "none"):
                    polyline = []
                    self.use_fog = 0
                    self.fog_bmp = None
                else:
                    polyline = []
                    lastx = None
                    lasty = None
                    list = l._get_childNodes()
                    for point in list:
                        x = point.getAttribute( "x" )
                        y = point.getAttribute( "y" )
                        if (x != lastx or y != lasty):
                            polyline.append(IPoint().make(int(x), int(y)))
                        lastx = x
                        lasty = y
                if (len(polyline) > 1): self.createregn2(polyline, action, "No")
            self.fill_fog()
        except: pass
