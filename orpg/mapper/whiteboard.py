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
# File: mapper/whiteboard.py
# Author: Chris Davis
# Maintainer:
# Version:
#   $Id: whiteboard.py,v Traipse 'Ornery-Orc' prof.ebral Exp $
#
# Description: This file contains some of the basic definitions for the chat
# utilities in the orpg project.
#
__version__ = "$Id: whiteboard.py,v Traipse 'Ornery-Orc' prof.ebral Exp $"

from base import *
from orpg.mapper.map_utils import *

def cmp_zorder(first,second):
    f = first.zorder
    s = second.zorder
    if f == None: f = 0
    if s == None: s = 0
    if f == s: value = 0
    elif f < s: value = -1
    else: value = 1
    return value

class WhiteboardText:
    def __init__(self, id, text_string, pos, style, pointsize, weight, color="#000000", log=None):
        self.scale = 1
        self.r_h = RGBHex()
        self.selected = False
        self.text_string = text_string.replace('"', '&#34;').replace("'", '&#39;')
        self.id = id
        self.weight = int(weight)
        self.pointsize = int(pointsize)
        self.style = int(style)
        self.textcolor = color
        self.posx = pos.x
        self.posy = pos.y
        self.font = wx.Font(self.pointsize, wx.DEFAULT, self.style, self.weight)
        self.highlighted = False
        r,g,b = self.r_h.rgb_tuple(self.textcolor)
        self.highlight_color = self.r_h.hexstring(r^255, g^255, b^255)
        self.isUpdated = False

    def highlight(self, highlight=True):
        self.highlighted = highlight

    def set_text_props(self, text_string, style, point, weight, color="#000000"):
        self.text_string = text_string
        self.textcolor = color
        self.style = int(style)
        self.font.SetStyle(self.style)
        self.pointsize = int(point)
        self.font.SetPointSize(self.pointsize)
        self.weight = int(weight)
        self.font.SetWeight(self.weight)
        self.isUpdated = True

    def hit_test(self, pt, dc):
        rect = self.get_rect(dc)
        result = rect.InsideXY(pt.x, pt.y)
        return result

    def get_rect(self, dc):
        dc.SetFont(self.font)
        (w,x,y,z) = dc.GetFullTextExtent(self.text_string)
        return wx.Rect(self.posx,self.posy,w,(x+y+z))

    def draw(self, parent, dc, op=wx.COPY):
        self.scale = parent.canvas.layers['grid'].mapscale
        if self.highlighted: textcolor = self.highlight_color
        else: textcolor = self.textcolor
        try: dc.SetTextForeground(textcolor)
        except Exception,e: dc.SetTextForeground('#000000')
        dc.SetUserScale(self.scale, self.scale)

        # Draw text
        (w,x,y,z) = self.get_rect(dc)
        dc.SetFont(self.font)
        text_string = self.text_string.replace('&#34;', '"').replace('&#39;', "'")
        dc.DrawText(text_string, self.posx, self.posy)
        dc.SetTextForeground(wx.Colour(0,0,0))

    def toxml(self, action="update"):
        if action == "del":
            xml_str = "<text action='del' id='" + str(self.id) + "'/>"
            return xml_str
        xml_str = "<text"
        xml_str += " action='" + action + "'"
        xml_str += " id='" + str(self.id) + "'"
        if self.pointsize != None: xml_str += " pointsize='" + str(self.pointsize) + "'"
        if self.style != None: xml_str += " style='" + str(self.style) + "'"
        if self.weight != None: xml_str += " weight='" + str(self.weight) + "'"
        if self.posx != None: xml_str+= " posx='" + str(self.posx) + "'"
        if not (self.posy is None): xml_str += " posy='" + str(self.posy) + "'"
        if self.text_string != None: xml_str+= " text_string='" + self.text_string + "'"
        if self.textcolor != None: xml_str += " color='" + self.textcolor + "'"
        xml_str += "/>"
        if (action == "update" and self.isUpdated) or action == "new":
            self.isUpdated = False
            return xml_str
        else: return ''

    def takedom(self, xml_dom):
        self.text_string = xml_dom.get("text_string")
        self.id = xml_dom.get("id")
        if xml_dom.get("posy") != None: self.posy = int(xml_dom.get("posy"))
        if xml_dom.get("posx") != None: self.posx = int(xml_dom.get("posx"))
        if xml_dom.get("weight"):
            self.weight = int(xml_dom.get("weight"))
            self.font.SetWeight(self.weight)
        if xml_dom.get("style") != None:
            self.style = int(xml_dom.get("style"))
            self.font.SetStyle(self.style)
        if xml_dom.get("pointsize") != None:
            self.pointsize = int(xml_dom.get("pointsize"))
            self.font.SetPointSize(self.pointsize)
        if xml_dom.get("color") != None and xml_dom.get("color") != '':
            self.textcolor = xml_dom.get("color")
            if self.textcolor == '#0000000': self.textcolor = '#000000'

class WhiteboardLine:
    def __init__(self, id, line_string, upperleft, lowerright, color="#000000", width=1, log=None):
        self.scale = 1
        self.r_h = RGBHex()
        if color == '': color = "#000000"
        self.linecolor = color
        self.linewidth = width
        self.lowerright = lowerright
        self.upperleft = upperleft
        self.selected = False
        self.line_string = line_string
        self.id = id
        self.highlighted = False
        r,g,b = self.r_h.rgb_tuple(self.linecolor)
        self.highlight_color = self.r_h.hexstring(r^255, g^255, b^255)

    def highlight(self, highlight=True):
        self.highlighted = highlight

    def set_line_props(self, line_string="", 
                        upperleftx=0, upperlefty=0, 
                        lowerrightx=0, lowerrighty=0, 
                        color="#000000", width=1):
        self.line_string = line_string
        self.upperleft.x = upperleftx
        self.upperleft.y = upperlefty
        self.lowerright.x = lowerrightx
        self.lowerright.y = lowerrighty
        self.linecolor = color
        self.linewidth = width

    def hit_test(self, pt):
        coords = self.line_string.split(";")
        stcords = coords[0].split(",")
        oldicords = (int(stcords[0]),int(stcords[1]))
        for coordinate_string_counter in range(1, len(coords)):
            stcords = coords[coordinate_string_counter].split(",")
            if stcords[0] == "": return False
            icords = (int(stcords[0]),int(stcords[1]))
            if orpg.mapper.map_utils.proximity_test(oldicords,icords,pt,12): return True
            oldicords = icords
        return False

    def draw(self, parent, dc, op=wx.COPY):
        self.scale = parent.canvas.layers['grid'].mapscale
        if self.highlighted: linecolor = self.highlight_color
        else: linecolor = self.linecolor
        pen = wx.BLACK_PEN
        try: pen.SetColour(linecolor)
        except Exception,e: pen.SetColour('#000000')
        pen.SetWidth( self.linewidth )
        dc.SetPen( pen )
        dc.SetBrush(wx.BLACK_BRUSH)
        # draw lines
        dc.SetUserScale(self.scale,self.scale)
        pointArray = self.line_string.split(";")
        x2 = y2 = -999
        for m in range(len(pointArray)-1):
            x = pointArray[m]
            points = x.split(",")
            x1 = int(points[0])
            y1 = int(points[1])
            if x2 != -999: dc.DrawLine(x2,y2,x1,y1)
            x2 = x1
            y2 = y1
        pen.SetColour(wx.Colour(0,0,0))
        dc.SetPen(pen)
        dc.SetPen(wx.NullPen)
        dc.SetBrush(wx.NullBrush)
        #selected outline

    def toxml(self, action="update"):
        if action == "del":
            xml_str = "<line action='del' id='" + str(self.id) + "'/>"
            return xml_str
        #  if there are any changes, make sure id is one of them
        xml_str = "<line"
        xml_str += " action='" + action + "'"
        xml_str += " id='" + str(self.id) + "'"
        xml_str+= " line_string='" + self.line_string + "'"
        if self.upperleft != None:
            xml_str += " upperleftx='" + str(self.upperleft.x) + "'"
            xml_str += " upperlefty='" + str(self.upperleft.y) + "'"
        if self.lowerright != None:
            xml_str+= " lowerrightx='" + str(self.lowerright.x) + "'"
            xml_str+= " lowerrighty='" + str(self.lowerright.y) + "'"
        if self.linecolor != None:
            xml_str += " color='" + str(self.linecolor) + "'"
        if self.linewidth != None:
            xml_str += " width='" + str(self.linewidth) + "'"
        xml_str += "/>"
        if action == "new": return xml_str
        return ''

    def takedom(self, xml_dom):
        self.line_string = xml_dom.get("line_string")
        self.id = xml_dom.get("id")
        if xml_dom.get("upperleftx") != None: self.upperleft.x = int(xml_dom.get("upperleftx"))
        if xml_dom.get("upperlefty") != None: self.upperleft.y = int(xml_dom.get("upperlefty"))
        if xml_dom.get("lowerrightx") != None: self.lowerright.x = int(xml_dom.get("lowerrightx"))
        if xml_dom.get("lowerrighty") != None: self.lowerright.y = int(xml_dom.get("lowerrighty"))
        if xml_dom.get("color") != None and xml_dom.get("color") != '':
            self.linecolor = xml_dom.get("color")
            if self.linecolor == '#0000000': self.linecolor = '#000000'
        if xml_dom.get("width") != None: self.linewidth = int(xml_dom.get("width"))

##-----------------------------
## whiteboard layer
##-----------------------------
class whiteboard_layer(layer_base):

    def __init__(self, canvas):
        self.canvas = canvas
        layer_base.__init__(self)
        self.r_h = RGBHex()
        self.id = -1
        self.lines = []
        self.texts = []
        self.serial_number = 0
        self.color = "#000000"
        self.width = 1
        self.removedLines = []

    def next_serial(self):
        self.serial_number += 1
        return self.serial_number

    def get_next_highest_z(self):
        z = len(self.lines)+1
        return z

    def cleanly_collapse_zorder(self):
        pass

    def collapse_zorder(self):
        pass

    def rollback_serial(self):
        self.serial_number -= 1

    def add_line(self, line_string="", upperleft=cmpPoint(0,0), lowerright=cmpPoint(0,0), color="#000000", width=1):
        id = 'line-' + self.canvas.session.get_next_id()
        line = WhiteboardLine(id, line_string, upperleft, lowerright, color=self.color, width=self.width)
        self.lines.append(line)
        xml_str = "<map><whiteboard>"
        xml_str += line.toxml("new")
        xml_str += "</whiteboard></map>"
        self.canvas.frame.session.send(xml_str)
        self.canvas.Refresh(True)
        return line

    def get_line_by_id(self, id):
        for line in self.lines:
            if str(line.id) == str(id): return line
        return None

    def get_text_by_id(self, id):
        for text in self.texts:
            if str(text.id) == str(id): return text
        return None

    def del_line(self, line):
        xml_str = "<map><whiteboard>"
        xml_str += line.toxml("del")
        xml_str += "</whiteboard></map>"
        self.canvas.frame.session.send(xml_str)
        if line:
            self.lines.remove(line)
            self.removedLines.append(line)
        self.canvas.Refresh(True)

    def undo_line(self):
        if len(self.removedLines)>0:
            line = self.removedLines[len(self.removedLines)-1]
            self.removedLines.remove(line)
            self.add_line(line.line_string, line.upperleft, line.lowerright, line.linecolor, line.linewidth)
            self.canvas.Refresh(True)

    def del_all_lines(self):
        for i in xrange(len(self.lines)): self.del_line(self.lines[0])

    def del_text(self, text):
        xml_str = "<map><whiteboard>"
        xml_str += text.toxml("del")
        xml_str += "</whiteboard></map>"
        self.canvas.frame.session.send(xml_str)
        if text: self.texts.remove(text)
        self.canvas.Refresh(True)

    def layerDraw(self, dc):
        for m in self.lines: m.draw(self, dc)
        for m in self.texts: m.draw(self,dc)

    def hit_test_text(self, pos, dc):
        list_of_texts_matching = []
        if self.canvas.layers['fog'].use_fog == 1:
            if self.canvas.frame.session.role != "GM": return list_of_texts_matching
        for m in self.texts:
            if m.hit_test(pos,dc): list_of_texts_matching.append(m)
        return list_of_texts_matching

    def hit_test_lines(self, pos, dc):
        list_of_lines_matching = []
        if self.canvas.layers['fog'].use_fog == 1:
            if self.canvas.frame.session.role != "GM": return list_of_lines_matching
        for m in self.lines:
            if m.hit_test(pos): list_of_lines_matching.append(m)
        return list_of_lines_matching

    def find_line(self, pt):
        scale = self.canvas.layers['grid'].mapscale
        dc = wx.ClientDC( self.canvas )
        self.canvas.PrepareDC( dc )
        dc.SetUserScale(scale,scale)
        line_list = self.hit_test_lines(pt,dc)
        if line_list: return line_list[0]
        else: return None

    def setcolor(self, color):
        r,g,b = color.Get()
        self.color = self.r_h.hexstring(r,g,b)

    def sethexcolor(self, hexcolor):
        self.color = hexcolor

    def setwidth(self, width):
        self.width = int(width)

    def set_font(self, font):
        self.font = font

    def add_text(self, text_string, pos, style, pointsize, weight, color="#000000"):
        id = 'text-' + self.canvas.session.get_next_id()
        text = WhiteboardText(id, text_string, pos, style, pointsize, weight, color)
        self.texts.append(text)
        xml_str = "<map><whiteboard>"
        xml_str += text.toxml("new")
        xml_str += "</whiteboard></map>"
        self.canvas.frame.session.send(xml_str)
        self.canvas.Refresh(True)

    def draw_working_line(self, dc, line_string):
        scale = self.canvas.layers['grid'].mapscale
        dc.SetPen(wx.BLACK_PEN)
        dc.SetBrush(wx.BLACK_BRUSH)
        pen = wx.BLACK_PEN
        pen.SetColour(self.color)
        pen.SetWidth(self.width)
        dc.SetPen(pen)
        dc.SetUserScale(scale,scale)
        pointArray = line_string.split(";")
        x2 = y2 = -999
        for m in range(len(pointArray)-1):
            x = pointArray[m]
            points = x.split(",")
            x1 = int(points[0])
            y1 = int(points[1])
            if x2 != -999: dc.DrawLine(x2,y2,x1,y1)
            x2 = x1
            y2 = y1
        dc.SetPen(wx.NullPen)
        dc.SetBrush(wx.NullBrush)

    def layerToXML(self, action="update"):
        """ format  """
        white_string = ""
        if self.lines: 
            for l in self.lines: white_string += l.toxml(action)
        if self.texts: 
            for l in self.texts: white_string += l.toxml(action)
        if len(white_string):
            s = "<whiteboard"
            s += " serial='" + str(self.serial_number) + "'"
            s += ">"
            s += white_string
            s += "</whiteboard>"
            return s
        else: return ""

    def layerTakeDOM(self, xml_dom):
        serial_number = xml_dom.get('serial')
        if serial_number != None: self.serial_number = int(serial_number)
        children = xml_dom.getchildren()
        for l in children:
            nodename = l.tag
            action = l.get("action")
            id = l.get('id')
            try:
                if self.serial_number < int(id.split('-')[2]): self.serial_number = int(id.split('-')[2])
            except: pass
            if action == "del":
                if nodename == 'line':
                    line = self.get_line_by_id(id)
                    if line != None: self.lines.remove(line)
                elif nodename == 'text':
                    text = self.get_text_by_id(id)
                    if text != None: self.texts.remove(text)
            elif action == "new":
                if nodename == "line":
                    try:
                        line_string = l.get('line_string')
                        upperleftx = l.get('upperleftx')
                        upperlefty = l.get('upperlefty')
                        lowerrightx = l.get('lowerrightx')
                        lowerrighty = l.get('lowerrighty')
                        upperleft = wx.Point(int(upperleftx),int(upperlefty))
                        lowerright = wx.Point(int(lowerrightx),int(lowerrighty))
                        color = l.get('color')
                        if color == '#0000000': color = '#000000'
                        id = l.get('id')
                        width = int(l.get('width'))
                    except:
                        line_string = upperleftx = upperlefty = lowerrightx = lowerrighty = color = 0
                        continue
                    line = WhiteboardLine(id, line_string, upperleft, lowerright, color, width)
                    self.lines.append(line)
                elif nodename == "text":
                    try:
                        text_string = l.get('text_string')
                        style = l.get('style')
                        pointsize = l.get('pointsize')
                        weight = l.get('weight')
                        color = l.get('color')
                        if color == '#0000000': color = '#000000'
                        id = l.get('id')
                        posx = l.get('posx')
                        posy = l.get('posy')
                        pos = wx.Point(0,0)
                        pos.x = int(posx)
                        pos.y = int(posy)
                    except: continue
                    text = WhiteboardText(id, text_string, pos, style, pointsize, weight, color)
                    self.texts.append(text)
            else:
                if nodename == "line":
                    line = self.get_line_by_id(id)
                    if line: line.takedom(l)
                if nodename == "text":
                    text = self.get_text_by_id(id)
                    if text: text.takedom(l)

    def add_temp_line(self, line_string):
        line = WhiteboardLine(0, line_string, wx.Point(0,0), wx.Point(0,0), 
            color=self.color, width=self.width)
        self.lines.append(line)
        return line

    def del_temp_line(self, line):
        if line: self.lines.remove(line)
