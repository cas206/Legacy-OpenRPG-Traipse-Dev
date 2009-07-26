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
#   $Id: whiteboard.py,v 1.47 2007/03/09 14:11:55 digitalxero Exp $
#
# Description: This file contains some of the basic definitions for the chat
# utilities in the orpg project.
#
__version__ = "$Id: whiteboard.py,v 1.47 2007/03/09 14:11:55 digitalxero Exp $"

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
        self.log = log
        self.log.log("Enter WhiteboardText", ORPG_DEBUG)
        self.scale = 1
        self.r_h = RGBHex()
        self.selected = False
        self.text_string = text_string
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
        self.log.log("Exit WhiteboardText", ORPG_DEBUG)

    def highlight(self, highlight=True):
        self.log.log("Enter WhiteboardText->highlight(self, highlight)", ORPG_DEBUG)
        self.highlighted = highlight
        self.log.log("Exit WhiteboardText->highlight(self, highlight)", ORPG_DEBUG)

    def set_text_props(self, text_string, style, point, weight, color="#000000"):
        self.log.log("Enter WhiteboardText->set_text_props(self, text_string, style, point, weight, color)", ORPG_DEBUG)
        self.text_string = text_string
        self.textcolor = color
        self.style = int(style)
        self.font.SetStyle(self.style)
        self.pointsize = int(point)
        self.font.SetPointSize(self.pointsize)
        self.weight = int(weight)
        self.font.SetWeight(self.weight)
        self.isUpdated = True
        self.log.log("Exit WhiteboardText->set_text_props(self, text_string, style, point, weight, color)", ORPG_DEBUG)

    def hit_test(self, pt, dc):
        self.log.log("Enter WhiteboardText->hit_test(self, pt, dc)", ORPG_DEBUG)
        rect = self.get_rect(dc)
        result = rect.InsideXY(pt.x, pt.y)
        self.log.log("Exit WhiteboardText->hit_test(self, pt, dc)", ORPG_DEBUG)
        return result

    def get_rect(self, dc):
        self.log.log("Enter WhiteboardText->get_rect(self, dc)", ORPG_DEBUG)
        dc.SetFont(self.font)
        (w,x,y,z) = dc.GetFullTextExtent(self.text_string)
        self.log.log("Exit WhiteboardText->get_rect(self, dc)", ORPG_DEBUG)
        return wx.Rect(self.posx,self.posy,w,(x+y+z))

    def draw(self, parent, dc, op=wx.COPY):
        self.log.log("Enter WhiteboardText->draw(self, parent, dc, op)", ORPG_DEBUG)
        self.scale = parent.canvas.layers['grid'].mapscale
        if self.highlighted: textcolor = self.highlight_color
        else: textcolor = self.textcolor
        try: dc.SetTextForeground(textcolor)
        except Exception,e: dc.SetTextForeground('#000000')
        dc.SetUserScale(self.scale, self.scale)

        # Draw text
        (w,x,y,z) = self.get_rect(dc)
        dc.SetFont(self.font)
        dc.DrawText(self.text_string, self.posx, self.posy)
        dc.SetTextForeground(wx.Colour(0,0,0))
        self.log.log("Exit WhiteboardText->draw(self, parent, dc, op)", ORPG_DEBUG)

    def toxml(self, action="update"):
        self.log.log("Enter WhiteboardText->toxml(self, " + action + ")", ORPG_DEBUG)
        if action == "del":
            xml_str = "<text action='del' id='" + str(self.id) + "'/>"
            self.log.log(xml_str, ORPG_DEBUG)
            self.log.log("Exit WhiteboardText->toxml(self, " + action + ")", ORPG_DEBUG)
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
        self.log.log(xml_str, ORPG_DEBUG)
        self.log.log("Exit WhiteboardText->toxml(self, " + action + ")", ORPG_DEBUG)
        if (action == "update" and self.isUpdated) or action == "new":
            self.isUpdated = False
            return xml_str
        else: return ''

    def takedom(self, xml_dom):
        self.log.log("Enter WhiteboardText->takedom(self, xml_dom)", ORPG_DEBUG)
        self.text_string = xml_dom.getAttribute("text_string")
        self.log.log("self.text_string=" + self.text_string, ORPG_DEBUG)
        self.id = xml_dom.getAttribute("id")
        self.log.log("self.id=" + str(self.id), ORPG_DEBUG)
        if xml_dom.hasAttribute("posy"):
            self.posy = int(xml_dom.getAttribute("posy"))
            self.log.log("self.posy=" + str(self.posy), ORPG_DEBUG)
        if xml_dom.hasAttribute("posx"):
            self.posx = int(xml_dom.getAttribute("posx"))
            self.log.log("self.posx=" + str(self.posx), ORPG_DEBUG)
        if xml_dom.hasAttribute("weight"):
            self.weight = int(xml_dom.getAttribute("weight"))
            self.font.SetWeight(self.weight)
            self.log.log("self.weight=" + str(self.weight), ORPG_DEBUG)
        if xml_dom.hasAttribute("style"):
            self.style = int(xml_dom.getAttribute("style"))
            self.font.SetStyle(self.style)
            self.log.log("self.style=" + str(self.style), ORPG_DEBUG)
        if xml_dom.hasAttribute("pointsize"):
            self.pointsize = int(xml_dom.getAttribute("pointsize"))
            self.font.SetPointSize(self.pointsize)
            self.log.log("self.pointsize=" + str(self.pointsize), ORPG_DEBUG)
        if xml_dom.hasAttribute("color") and xml_dom.getAttribute("color") != '':
            self.textcolor = xml_dom.getAttribute("color")
            if self.textcolor == '#0000000': self.textcolor = '#000000'
            self.log.log("self.textcolor=" + self.textcolor, ORPG_DEBUG)
        self.log.log("Exit WhiteboardText->takedom(self, xml_dom)", ORPG_DEBUG)

class WhiteboardLine:
    def __init__(self, id, line_string, upperleft, lowerright, color="#000000", width=1, log=None):
        self.log = log
        self.log.log("Enter WhiteboardLine", ORPG_DEBUG)
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
        self.log.log("Exit WhiteboardLine", ORPG_DEBUG)

    def highlight(self, highlight=True):
        self.log.log("Enter WhiteboardLine->highlight(self, highlight)", ORPG_DEBUG)
        self.highlighted = highlight
        self.log.log("Enter WhiteboardLine->highlight(self, highlight)", ORPG_DEBUG)

    def set_line_props(self, line_string="", upperleftx=0, upperlefty=0, 
            lowerrightx=0, lowerrighty=0, color="#000000", width=1):
        self.log.log("Enter WhiteboardLine->set_line_props(self, line_string, upperleftx, upperlefty, lowerrightx, lowerrighty, color, width)", ORPG_DEBUG)
        self.line_string = line_string
        self.upperleft.x = upperleftx
        self.upperleft.y = upperlefty
        self.lowerright.x = lowerrightx
        self.lowerright.y = lowerrighty
        self.linecolor = color
        self.linewidth = width
        self.log.log("Exit WhiteboardLine->set_line_props(self, line_string, upperleftx, upperlefty, lowerrightx, lowerrighty, color, width)", ORPG_DEBUG)

    def hit_test(self, pt):
        self.log.log("Enter WhiteboardLine->hit_test(self, pt)", ORPG_DEBUG)
        coords = self.line_string.split(";")
        stcords = coords[0].split(",")
        oldicords = (int(stcords[0]),int(stcords[1]))
        for coordinate_string_counter in range(1, len(coords)):
            stcords = coords[coordinate_string_counter].split(",")
            if stcords[0] == "":
                self.log.log("Exit WhiteboardLine->hit_test(self, pt) return False", ORPG_DEBUG)
                return False
            icords = (int(stcords[0]),int(stcords[1]))
            if orpg.mapper.map_utils.proximity_test(oldicords,icords,pt,12):
                self.log.log("Exit WhiteboardLine->hit_test(self, pt) return True", ORPG_DEBUG)
                return True
            oldicords = icords
        self.log.log("Exit WhiteboardLine->hit_test(self, pt) return False", ORPG_DEBUG)
        return False

    def draw(self, parent, dc, op=wx.COPY):
        self.log.log("Enter WhiteboardLine->draw(self, parent, dc, op=wx.COPY)", ORPG_DEBUG)
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
        self.log.log("Exit WhiteboardLine->draw(self, parent, dc, op=wx.COPY)", ORPG_DEBUG)

    def toxml(self, action="update"):
        self.log.log("Enter WhiteboardLine->toxml(self, " + action + ")", ORPG_DEBUG)
        if action == "del":
            xml_str = "<line action='del' id='" + str(self.id) + "'/>"
            self.log.log(xml_str, ORPG_DEBUG)
            self.log.log("Exit WhiteboardLine->toxml(self, " + action + ")", ORPG_DEBUG)
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
        self.log.log(xml_str, ORPG_DEBUG)
        self.log.log("Exit WhiteboardLine->toxml(self, " + action + ")", ORPG_DEBUG)
        if action == "new": return xml_str
        return ''

    def takedom(self, xml_dom):
        self.log.log("Enter WhiteboardLine->takedom(self, xml_dom)", ORPG_DEBUG)
        self.line_string = xml_dom.getAttribute("line_string")
        self.log.log("self.line_string=" + self.line_string, ORPG_DEBUG)
        self.id = xml_dom.getAttribute("id")
        self.log.log("self.id=" + str(self.id), ORPG_DEBUG)
        if xml_dom.hasAttribute("upperleftx"):
            self.upperleft.x = int(xml_dom.getAttribute("upperleftx"))
            self.log.log("self.upperleft.x=" + str(self.upperleft.x), ORPG_DEBUG)
        if xml_dom.hasAttribute("upperlefty"):
            self.upperleft.y = int(xml_dom.getAttribute("upperlefty"))
            self.log.log("self.upperleft.y=" + str(self.upperleft.y), ORPG_DEBUG)
        if xml_dom.hasAttribute("lowerrightx"):
            self.lowerright.x = int(xml_dom.getAttribute("lowerrightx"))
            self.log.log("self.lowerright.x=" + str(self.lowerright.x), ORPG_DEBUG)
        if xml_dom.hasAttribute("lowerrighty"):
            self.lowerright.y = int(xml_dom.getAttribute("lowerrighty"))
            self.log.log("self.lowerright.y=" + str(self.lowerright.y), ORPG_DEBUG)
        if xml_dom.hasAttribute("color") and xml_dom.getAttribute("color") != '':
            self.linecolor = xml_dom.getAttribute("color")
            if self.linecolor == '#0000000':
                self.linecolor = '#000000'
            self.log.log("self.linecolor=" + self.linecolor, ORPG_DEBUG)
        if xml_dom.hasAttribute("width"):
            self.linewidth = int(xml_dom.getAttribute("width"))
            self.log.log("self.linewidth=" + str(self.linewidth), ORPG_DEBUG)
        self.log.log("Exit WhiteboardLine->takedom(self, xml_dom)", ORPG_DEBUG)

##-----------------------------
## whiteboard layer
##-----------------------------
class whiteboard_layer(layer_base):

    def __init__(self, canvas):
        self.canvas = canvas
        self.log = self.canvas.log
        self.log.log("Enter whiteboard_layer", ORPG_DEBUG)
        layer_base.__init__(self)
        self.r_h = RGBHex()
        self.id = -1
        self.lines = []
        self.texts = []
        self.serial_number = 0
        self.color = "#000000"
        self.width = 1
        self.removedLines = []
        self.log.log("Exit whiteboard_layer", ORPG_DEBUG)

    def next_serial(self):
        self.log.log("Enter whiteboard_layer->next_serial(self)", ORPG_DEBUG)
        self.serial_number += 1
        self.log.log("Exit whiteboard_layer->next_serial(self)", ORPG_DEBUG)
        return self.serial_number

    def get_next_highest_z(self):
        self.log.log("Enter whiteboard_layer->get_next_highest_z(self)", ORPG_DEBUG)
        z = len(self.lines)+1
        self.log.log("Exit whiteboard_layer->get_next_highest_z(self)", ORPG_DEBUG)
        return z

    def cleanly_collapse_zorder(self):
        self.log.log("Enter/Exit whiteboard_layer->cleanly_collapse_zorder(self)", ORPG_DEBUG)

    def collapse_zorder(self):
        self.log.log("Enter/Exit whiteboard_layer->collapse_zorder(self)", ORPG_DEBUG)

    def rollback_serial(self):
        self.log.log("Enter whiteboard_layer->rollback_serial(self)", ORPG_DEBUG)
        self.serial_number -= 1
        self.log.log("Exit whiteboard_layer->rollback_serial(self)", ORPG_DEBUG)

    def add_line(self, line_string="", upperleft=cmpPoint(0,0), lowerright=cmpPoint(0,0), color="#000000", width=1):
        self.log.log("Enter whiteboard_layer->add_line(self, line_string, upperleft, lowerright, color, width)", ORPG_DEBUG)
        id = 'line-' + str(self.next_serial())
        line = WhiteboardLine(id, line_string, upperleft, lowerright, color=self.color, width=self.width, log=self.log)
        self.lines.append(line)
        xml_str = "<map><whiteboard>"
        xml_str += line.toxml("new")
        xml_str += "</whiteboard></map>"
        self.canvas.frame.session.send(xml_str)
        self.canvas.Refresh(True)
        self.log.log("Exit whiteboard_layer->add_line(self, line_string, upperleft, lowerright, color, width)", ORPG_DEBUG)
        return line

    def get_line_by_id(self, id):
        self.log.log("Enter whiteboard_layer->get_line_by_id(self, id)", ORPG_DEBUG)
        for line in self.lines:
            if str(line.id) == str(id):
                self.log.log("Exit whiteboard_layer->get_line_by_id(self, id) return LineID: " + str(id), ORPG_DEBUG)
                return line
        self.log.log("Exit whiteboard_layer->get_line_by_id(self, id) return None", ORPG_DEBUG)
        return None

    def get_text_by_id(self, id):
        self.log.log("Enter whiteboard_layer->get_text_by_id(self, id)", ORPG_DEBUG)
        for text in self.texts:
            if str(text.id) == str(id):
                self.log.log("Exit whiteboard_layer->get_text_by_id(self, id) return textID: " + str(id), ORPG_DEBUG)
                return text
        self.log.log("Enter whiteboard_layer->get_text_by_id(self, id) return None", ORPG_DEBUG)
        return None

    def del_line(self, line):
        self.log.log("Enter whiteboard_layer->del_line(self, line)", ORPG_DEBUG)
        xml_str = "<map><whiteboard>"
        xml_str += line.toxml("del")
        xml_str += "</whiteboard></map>"
        self.canvas.frame.session.send(xml_str)
        if line:
            self.lines.remove(line)
            self.removedLines.append(line)
        self.canvas.Refresh(True)
        self.log.log("Exit whiteboard_layer->del_line(self, line)", ORPG_DEBUG)

    def undo_line(self):
        if len(self.removedLines)>0:
            line = self.removedLines[len(self.removedLines)-1]
            self.removedLines.remove(line)
            self.add_line(line.line_string, line.upperleft, line.lowerright, line.linecolor, line.linewidth)
            self.canvas.Refresh(True)

    def del_all_lines(self):
        self.log.log("Enter whiteboard_layer->del_all_lines(self)", ORPG_DEBUG)
        for i in xrange(len(self.lines)):
            self.del_line(self.lines[0])
        print self.lines
        self.log.log("Exit whiteboard_layer->del_all_lines(self)", ORPG_DEBUG)

    def del_text(self, text):
        self.log.log("Enter whiteboard_layer->del_text(self, text)", ORPG_DEBUG)
        xml_str = "<map><whiteboard>"
        xml_str += text.toxml("del")
        xml_str += "</whiteboard></map>"
        self.canvas.frame.session.send(xml_str)
        if text:
            self.texts.remove(text)
        self.canvas.Refresh(True)
        self.log.log("Exit whiteboard_layer->del_text(self, text)", ORPG_DEBUG)

    def layerDraw(self, dc):
        self.log.log("Enter whiteboard_layer->layerDraw(self, dc)", ORPG_DEBUG)
        for m in self.lines: m.draw(self, dc)
        for m in self.texts: m.draw(self,dc)
        self.log.log("Exit whiteboard_layer->layerDraw(self, dc)", ORPG_DEBUG)

    def hit_test_text(self, pos, dc):
        self.log.log("Enter whiteboard_layer->hit_test_text(self, pos, dc)", ORPG_DEBUG)
        list_of_texts_matching = []
        if self.canvas.layers['fog'].use_fog == 1:
            if self.canvas.frame.session.role != "GM":
                self.log.log("Exit whiteboard_layer->hit_test_text(self, pos, dc)", ORPG_DEBUG)
                return list_of_texts_matching
        for m in self.texts:
            if m.hit_test(pos,dc): list_of_texts_matching.append(m)
        self.log.log("Exit whiteboard_layer->hit_test_text(self, pos, dc)", ORPG_DEBUG)
        return list_of_texts_matching

    def hit_test_lines(self, pos, dc):
        self.log.log("Enter whiteboard_layer->hit_test_lines(self, pos, dc)", ORPG_DEBUG)
        list_of_lines_matching = []
        if self.canvas.layers['fog'].use_fog == 1:
            if self.canvas.frame.session.role != "GM":
                self.log.log("Exit whiteboard_layer->hit_test_lines(self, pos, dc)", ORPG_DEBUG)
                return list_of_lines_matching
        for m in self.lines:
            if m.hit_test(pos): list_of_lines_matching.append(m)
        self.log.log("Exit whiteboard_layer->hit_test_lines(self, pos, dc)", ORPG_DEBUG)
        return list_of_lines_matching

    def find_line(self, pt):
        self.log.log("Enter whiteboard_layer->find_line(self, pt)", ORPG_DEBUG)
        scale = self.canvas.layers['grid'].mapscale
        dc = wx.ClientDC( self.canvas )
        self.canvas.PrepareDC( dc )
        dc.SetUserScale(scale,scale)
        line_list = self.hit_test_lines(pt,dc)
        if line_list:
            self.log.log("Exit whiteboard_layer->find_line(self, pt)", ORPG_DEBUG)
            return line_list[0]
        else:
            self.log.log("Exit whiteboard_layer->find_line(self, pt) return None", ORPG_DEBUG)
            return None

    def setcolor(self, color):
        self.log.log("Enter whiteboard_layer->setcolor(self, color)", ORPG_DEBUG)
        r,g,b = color.Get()
        self.color = self.r_h.hexstring(r,g,b)
        self.log.log("Exit whiteboard_layer->setcolor(self, color)", ORPG_DEBUG)

    def sethexcolor(self, hexcolor):
        self.log.log("Enter whiteboard_layer->sethexcolor(self, hexcolor)", ORPG_DEBUG)
        self.color = hexcolor
        self.log.log("Exit whiteboard_layer->sethexcolor(self, hexcolor)", ORPG_DEBUG)

    def setwidth(self, width):
        self.log.log("Enter whiteboard_layer->setwidth(self, width)", ORPG_DEBUG)
        self.width = int(width)
        self.log.log("Exit whiteboard_layer->setwidth(self, width)", ORPG_DEBUG)

    def set_font(self, font):
        self.log.log("Enter whiteboard_layer->set_font(self, font)", ORPG_DEBUG)
        self.font = font
        self.log.log("Exit whiteboard_layer->set_font(self, font)", ORPG_DEBUG)

    def add_text(self, text_string, pos, style, pointsize, weight, color="#000000"):
        self.log.log("Enter whiteboard_layer->add_text(self, text_string, pos, style, pointsize, weight, color)", ORPG_DEBUG)
        id = 'text-' + str(self.next_serial())
        text = WhiteboardText(id,text_string, pos, style, pointsize, weight, color, self.log)
        self.texts.append(text)
        xml_str = "<map><whiteboard>"
        xml_str += text.toxml("new")
        xml_str += "</whiteboard></map>"
        self.canvas.frame.session.send(xml_str)
        self.canvas.Refresh(True)
        self.log.log("Exit whiteboard_layer->add_text(self, text_string, pos, style, pointsize, weight, color)", ORPG_DEBUG)

    def draw_working_line(self, dc, line_string):
        self.log.log("Enter whiteboard_layer->draw_working_line(self, dc, line_string)", ORPG_DEBUG)
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
            if x2 != -999:
                dc.DrawLine(x2,y2,x1,y1)
            x2 = x1
            y2 = y1
        dc.SetPen(wx.NullPen)
        dc.SetBrush(wx.NullBrush)
        self.log.log("Exit whiteboard_layer->draw_working_line(self, dc, line_string)", ORPG_DEBUG)

    def layerToXML(self, action="update"):
        """ format  """
        self.log.log("Enter whiteboard_layer->layerToXML(self, " + action + ")", ORPG_DEBUG)
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
            self.log.log(s, ORPG_DEBUG)
            self.log.log("Exit whiteboard_layer->layerToXML(self, " + action + ")", ORPG_DEBUG)
            return s
        else:
            self.log.log("Exit whiteboard_layer->layerToXML(self, " + action + ")", ORPG_DEBUG)
            return ""

    def layerTakeDOM(self, xml_dom):
        self.log.log("Enter whiteboard_layer->layerTakeDOM(self, xml_dom)", ORPG_DEBUG)
        serial_number = xml_dom.getAttribute('serial')
        if serial_number != "": self.serial_number = int(serial_number)
        children = xml_dom._get_childNodes()
        for l in children:
            nodename = l._get_nodeName()
            action = l.getAttribute("action")
            id = l.getAttribute('id')
            if action == "del":
                if nodename == 'line':
                    line = self.get_line_by_id(id)
                    if line != None: self.lines.remove(line)
                    else: self.log.log("Whiteboard error: Deletion of unknown line object attempted.", ORPG_GENERAL)
                elif nodename == 'text':
                    text = self.get_text_by_id(id)
                    if text != None: self.texts.remove(text)
                    else: self.log.log("Whiteboard error: Deletion of unknown text object attempted.", ORPG_GENERAL)
                else: self.log.log("Whiteboard error: Deletion of unknown whiteboard object attempted.", ORPG_GENERAL)
            elif action == "new":
                if nodename == "line":
                    try:
                        line_string = l.getAttribute('line_string')
                        upperleftx = l.getAttribute('upperleftx')
                        upperlefty = l.getAttribute('upperlefty')
                        lowerrightx = l.getAttribute('lowerrightx')
                        lowerrighty = l.getAttribute('lowerrighty')
                        upperleft = wx.Point(int(upperleftx),int(upperlefty))
                        lowerright = wx.Point(int(lowerrightx),int(lowerrighty))
                        color = l.getAttribute('color')
                        if color == '#0000000': color = '#000000'
                        id = l.getAttribute('id')
                        width = int(l.getAttribute('width'))
                    except:
                        line_string = upperleftx = upperlefty = lowerrightx = lowerrighty = color = 0
                        self.log.log(traceback.format_exc(), ORPG_GENERAL)
                        self.log.log("invalid line", ORPG_GENERAL)
                        continue
                    line = WhiteboardLine(id, line_string, upperleft, lowerright, color, width, self.log)
                    self.lines.append(line)
                elif nodename == "text":
                    try:
                        text_string = l.getAttribute('text_string')
                        style = l.getAttribute('style')
                        pointsize = l.getAttribute('pointsize')
                        weight = l.getAttribute('weight')
                        color = l.getAttribute('color')
                        if color == '#0000000': color = '#000000'
                        id = l.getAttribute('id')
                        posx = l.getAttribute('posx')
                        posy = l.getAttribute('posy')
                        pos = wx.Point(0,0)
                        pos.x = int(posx)
                        pos.y = int(posy)
                    except:
                        self.log.log(traceback.format_exc(), ORPG_GENERAL)
                        self.log.log("invalid line", ORPG_GENERAL)
                        continue
                    text = WhiteboardText(id, text_string, pos, style, pointsize, weight, color, self.log)
                    self.texts.append(text)
            else:
                if nodename == "line":
                    line = self.get_line_by_id(id)
                    if line: line.takedom(l)
                    else: self.log.log("Whiteboard error: Update of unknown line attempted.", ORPG_GENERAL)
                if nodename == "text":
                    text = self.get_text_by_id(id)
                    if text: text.takedom(l)
                    else: self.log.log("Whiteboard error: Update of unknown text attempted.", ORPG_GENERAL)
        self.log.log("Enter whiteboard_layer->layerTakeDOM(self, xml_dom)", ORPG_DEBUG)
        #self.canvas.send_map_data()

    def add_temp_line(self, line_string):
        line = WhiteboardLine(0, line_string, wx.Point(0,0), wx.Point(0,0), 
            color=self.color, width=self.width, log=self.log)
        self.lines.append(line)
        return line

    def del_temp_line(self, line):
        if line: self.lines.remove(line)
