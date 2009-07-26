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
# File: mapper/gird.py
# Author: OpenRPG Team
# Maintainer:
# Version:
#   $Id: grid.py,v 1.29 2007/12/07 20:39:49 digitalxero Exp $
#
# Description:
#
__version__ = "$Id: grid.py,v 1.29 2007/12/07 20:39:49 digitalxero Exp $"

from base import *
from isometric import *
from miniatures import SNAPTO_ALIGN_CENTER
from miniatures import SNAPTO_ALIGN_TL
from math import floor

# Grid mode constants
GRID_RECTANGLE = 0
GRID_HEXAGON = 1
GRID_ISOMETRIC = 2
LINE_NONE = 0
LINE_DOTTED = 1
LINE_SOLID = 2
RATIO_DEFAULT = 2.0

##-----------------------------
## grid layer
##-----------------------------
class grid_layer(layer_base):

    def __init__(self, canvas):
        layer_base.__init__(self)
        self.canvas = canvas
        self.iso_ratio = RATIO_DEFAULT  #2:1 isometric ratio
        self.mapscale = 1.0
        self.unit_size = 100
        self.unit_size_y = 100
        #unit_widest and unit_offset are for the Hex Grid only. 
        #These are mathematics to figure out the exact center of the hex
        self.unit_widest = 100
        self.unit_offset = 100
        #size_ratio is the size ajustment for Hex and ISO to make them more accurate
        self.size_ratio = 1.5
        self.snap = True
        self.color = wx.BLACK# = color.Get()
        #self.color = cmpColour(r,g,b)
        self.r_h = RGBHex()
        self.mode = GRID_RECTANGLE
        self.line = LINE_NONE
        # Keep logic for different modes in different functions
        self.grid_hit_test = self.grid_hit_test_rect
        self.get_top_corner = self.get_top_corner_rect
        self.layerDraw = self.draw_rect
        self.isUpdated = True

    def get_unit_size(self):
        return self.unit_size

    def get_iso_ratio(self):
        return self.iso_ratio

    def get_mode(self):
        return self.mode

    def get_color(self):
        return self.color

    def get_line_type(self):
        return self.line

    def is_snap(self):
        return self.snap

    def get_snapped_to_pos(self, pos, snap_to_align, mini_width, mini_height):
        grid_pos = self.grid_hit_test(pos)
        if grid_pos is not None:
            topLeft = self.get_top_corner(grid_pos)#  get the top corner for this grid cell
            if snap_to_align == SNAPTO_ALIGN_CENTER:
                if self.mode == GRID_HEXAGON:
                    x = topLeft.x + (((self.unit_size/1.75) - mini_width) /2)
                    y = topLeft.y + ((self.unit_size - mini_height) /2)
                elif self.mode == GRID_ISOMETRIC:
                    x = (topLeft.x)-(mini_width/2)
                    y = (topLeft.y)-(mini_height)
                else:# GRID_RECTANGLE
                    x = topLeft.x + ((self.unit_size - mini_width) / 2)
                    y = topLeft.y + ((self.unit_size_y - mini_height) /2)
            else:
                x = topLeft.x
                y = topLeft.y
            return cmpPoint(int(x),int(y))                                           #  Set the pos attribute
        else: return cmpPoint(int(pos.x),int(pos.y))

    def set_rect_mode(self):
        "switch grid to rectangular mode"
        self.mode = GRID_RECTANGLE
        self.grid_hit_test = self.grid_hit_test_rect
        self.get_top_corner = self.get_top_corner_rect
        self.layerDraw = self.draw_rect
        self.unit_size_y = self.unit_size

    def set_hex_mode(self):
        "switch grid to hexagonal mode"
        self.mode = GRID_HEXAGON
        self.grid_hit_test = self.grid_hit_test_hex
        self.get_top_corner = self.get_top_corner_hex
        self.layerDraw = self.draw_hex
        self.unit_size_y = self.unit_size
        self.unit_offset = sqrt(pow((self.unit_size/self.size_ratio ),2)-pow((self.unit_size/2),2))
        self.unit_widest = (self.unit_offset*2)+(self.unit_size/self.size_ratio )

    def set_iso_mode(self):
        "switch grid to hexagonal mode"
        self.mode = GRID_ISOMETRIC
        self.grid_hit_test = self.grid_hit_test_iso
        self.get_top_corner = self.get_top_corner_iso
        self.layerDraw = self.draw_iso
        self.unit_size_y = self.unit_size

    def set_line_none(self):
        "switch to no line mode for grid"
        self.line = LINE_NONE

    def set_line_dotted(self):
        "switch to dotted line mode for grid"
        self.line = LINE_DOTTED

    def set_line_solid(self):
        "switch to solid line mode for grid"
        self.line = LINE_SOLID

    def grid_hit_test_rect(self,pos):
        "return grid pos (w,h) on rect map from pos"
        if self.unit_size and self.snap: return cmpPoint(int(pos.x/self.unit_size), int(pos.y/self.unit_size))
        else: return None

    def grid_hit_test_hex(self,pos):
        "return grid pos (w,h) on hex map from pos"
        if self.unit_size and self.snap:
            # rectangular repeat patern is as follows (unit_size is the height of a hex)
            hex_side = int(self.unit_size/1.75)
            half_height = int(self.unit_size/2)
            height = int(self.unit_size)
            #_____
            #     \       /
            #      \_____/
            #      /     \
            #_____/       \
            col = int(pos.x/(hex_side*1.5))
            row = int(pos.y/height)
            (px, py) = (pos.x-(col*(hex_side*1.5)), pos.y-(row*height))
            # adjust for the odd columns' rows being staggered lower
            if col % 2 == 1:
                if py < half_height:
                    row = row - 1
                    py = py + half_height
                else: py = py - half_height
            # adjust for top right corner
            if (px * height - py * hex_side) > height * hex_side:
                if col % 2 == 0: row = row - 1
                col = col + 1
            # adjust for bottom right corner
            elif (px * height + py * hex_side) > 2 * height * hex_side:
                if col%2==1: row = row + 1
                col = col + 1
            return cmpPoint(col, row)
        else: return None

    def grid_hit_test_iso(self,pos):
        "return grid pos (w,h) on isometric map from pos"
        if self.unit_size and self.snap:
            height = self.unit_size*self.size_ratio/self.iso_ratio
            width = self.unit_size*self.size_ratio
            iso_unit_size = height * width
            # convert to isometric pos which has an origin of cell (0,0)
            # x-ord increasing as you go up and right, y-ord increasing as you go down and right
            # this is the transformation from grid co-ord to iso co-ords
            iso_x = (pos.x*height) - (pos.y*width) + (iso_unit_size/2)
            iso_y = (pos.x*height) + (pos.y*width) - (iso_unit_size/2)
            #
            #  /\
            # /  \
            #/    \
            #\    /
            # \  /
            #  \/
            # so the exact isomorphic (0,0) is the left corner of the first (ie. top left) diamond
            # this is at grid co-ordinate (0, height/2)
            # the top corner of the first diamond is grid co-ord (width/2, 0)
            # and therefore (per transformation above) is at iso co-ord (iso_unit_size, 0)
            # the bottom corner of the first diamond is grid co-ord (width/2, height)
            # and therefore (per transformation above) is at iso co-ord (0, iso_unit_size)

            # the calculation is now as simple as the rectangle case, but using iso co-ords
            return cmpPoint(floor(iso_x/iso_unit_size), floor(iso_y/iso_unit_size))
        else: return None

    def get_top_corner_iso(self, iso_pos):
        "return upper left of a iso grid pos"
        # for whatever reason the iso grid returns the center of the diamond for "top left corner"
        if self.unit_size:
            half_height = self.unit_size*self.size_ratio/(2*self.iso_ratio)
            half_width = self.unit_size*self.size_ratio/2
            # convert back into grid co-ordinates of center of diamond
            grid_x = (iso_pos.y*half_width) + (iso_pos.x*half_width) + half_width
            grid_y = (iso_pos.y*half_height) - (iso_pos.x*half_height) + half_height
            return cmpPoint(int(grid_x), int(grid_y))
        else: return None

    def get_top_corner_rect(self,grid_pos):
        "return upper left of a rect grid pos"
        if self.unit_size: return cmpPoint(grid_pos[0]*self.unit_size,grid_pos[1]*self.unit_size)
        else: return None

    def get_top_corner_hex(self,grid_pos):
        "return upper left of a hex grid pos"
        if self.unit_size:
            # We can get our x value directly, y is trickier
            temp_x = (((self.unit_size/1.75)*1.5)*grid_pos[0])
            temp_y = self.unit_size*grid_pos[1]
            # On odd columns we have to slide down slightly
            if grid_pos[0] % 2:
                temp_y += self.unit_size/2
            return cmpPoint(temp_x,temp_y)
        else: return None

    def set_grid(self, unit_size, snap, color, mode, line, ratio=None):
        self.unit_size = unit_size
        if ratio != None: self.iso_ratio = ratio
        self.snap = snap
        self.set_color(color)
        self.SetMode(mode)
        self.SetLine(line)

    def SetLine(self,line):
        if line == LINE_NONE: self.set_line_none()
        elif line == LINE_DOTTED: self.set_line_dotted()
        elif line == LINE_SOLID: self.set_line_solid()

    def SetMode(self, mode):
        if mode == GRID_RECTANGLE: self.set_rect_mode()
        elif mode == GRID_HEXAGON: self.set_hex_mode()
        elif mode == GRID_ISOMETRIC: self.set_iso_mode()

    def return_grid(self):
        return self.canvas.size

    def set_color(self,color):
        (r,g,b) = color.Get()
        self.color = cmpColour(r,g,b)

    def draw_iso(self,dc,topleft,clientsize):
        if not self.unit_size: return
        if self.line == LINE_NONE: return
        if self.line == LINE_SOLID: dc.SetPen(wx.Pen(self.color,1,wx.SOLID))
        else: dc.SetPen(wx.Pen(self.color,1,wx.DOT))
        sz = self.canvas.size

        # Enable DC optimizations if available on a platform
        dc.BeginDrawing()

        # create IsoGrid helper object
        IG = IsoGrid(self.unit_size*self.size_ratio)
        IG.Ratio(self.iso_ratio)
        rows = int(min(clientsize[1]+topleft[1],sz[1])/IG.height)
        cols = int(min(clientsize[0]+topleft[0],sz[0])/IG.width)
        for y in range(rows+1):
            for x in range(cols+1):
                IG.BoundPlace((x*IG.width),(y*IG.height))
                x1,y1 = IG.Top()
                x2,y2 = IG.Left()
                dc.DrawLine(x1,y1,x2,y2)
                x1,y1 = IG.Left()
                x2,y2 = IG.Bottom()
                dc.DrawLine(x1,y1,x2,y2)
                x1,y1 = IG.Bottom()
                x2,y2 = IG.Right()
                dc.DrawLine(x1,y1,x2,y2)
                x1,y1 = IG.Right()
                x2,y2 = IG.Top()
                dc.DrawLine(x1,y1,x2,y2)
        # Enable DC optimizations if available on a platform
        dc.EndDrawing()
        dc.SetPen(wx.NullPen)
        # Disable pen/brush optimizations to prevent any odd effects elsewhere

    def draw_rect(self,dc,topleft,clientsize):
        if self.unit_size:
            draw = 1
            # Enable pen/brush optimizations if available on a platform
            if self.line == LINE_NONE: draw = 0
            elif self.line == LINE_SOLID: dc.SetPen(wx.Pen(self.color,1,wx.SOLID))
            else: dc.SetPen(wx.Pen(self.color,1,wx.DOT))
            if draw:
                sz = self.canvas.size
                # Enable DC optimizations if available on a platform
                dc.BeginDrawing()
                # Now, draw the map grid
                x = 0
                s = self.unit_size
                x = int(topleft[0]/s)*s
                mx = min(clientsize[0]+topleft[0],sz[0])
                my = min(clientsize[1]+topleft[1],sz[1])
                while x < mx:
                    dc.DrawLine(x,topleft[1],x,my)
                    x += self.unit_size
                y = 0
                y = int (topleft[1]/s)*s
                while y < my:
                    dc.DrawLine(topleft[0],y,mx,y)
                    y += self.unit_size
                # Enable DC optimizations if available on a platform
                dc.EndDrawing()
                dc.SetPen(wx.NullPen)
            # Disable pen/brush optimizations to prevent any odd effects elsewhere

    def draw_hex(self,dc,topleft,clientsize):
        if self.unit_size:
            draw = 1
            # Enable pen/brush optimizations if available on a platform
            if self.line == LINE_NONE: draw = 0
            elif self.line == LINE_SOLID: dc.SetPen(wx.Pen(self.color,1,wx.SOLID))
            else: dc.SetPen(wx.Pen(self.color,1,wx.DOT))
            if draw:
                sz = self.canvas.size
                x = 0
                A = self.unit_size/1.75 #Side Length
                B = self.unit_size #The width between any two sides
                D = self.unit_size/2 #The distance from the top to the middle of the hex
                C = self.unit_size/3.5 #The distance from the point of the hex to the point where the top line starts

                #   _____
                #  /     \
                # /       \
                # \       /
                #  \_____/

                startx=int(topleft[0]/(3*A))*(3*A)
                starty=int(topleft[1]/B)*B
                y = starty
                mx = min(clientsize[0]+topleft[0],sz[0])
                my = min(clientsize[1]+topleft[1],sz[1])
                while y < my:
                    x = startx
                    lineArray = []
                    while x < mx:
                        #The top / Bottom of the Hex
                        lineArray.append((x, y))
                        lineArray.append((x+A, y))
                        #The Right Top Side of the Hex
                        lineArray.append((x+A, y))
                        lineArray.append((x+A+C, y+D))
                        #The Right Bottom Side of the Hex
                        lineArray.append((x+A+C, y+D))
                        lineArray.append((x+A, y+B))
                        #The Top / of the Middle Hex
                        lineArray.append((x+A+C, y+D))
                        lineArray.append((x+A+C+A, y+D))
                        #The Left Bottom Side of the Hex
                        lineArray.append((x+A+C+A, y+D))
                        lineArray.append((x+A+C+A+C, y+B))
                        #The left Top Side of the Hex
                        lineArray.append((x+A+C+A, y+D))
                        lineArray.append((x+A+C+A+C, y))
                        x += A*3
                    y += B
                    dc.DrawLines(lineArray)
                dc.SetPen(wx.NullPen)
            # Disable pen/brush optimizations to prevent any odd effects elsewhere

    def layerToXML(self,action = "update"):
        xml_str = "<grid"
        if self.color != None:
            (red,green,blue) = self.color.Get()
            hexcolor = self.r_h.hexstring(red, green, blue)
            xml_str += " color='" + hexcolor + "'"
        if self.unit_size != None: xml_str += " size='" + str(self.unit_size) + "'"
        if self.iso_ratio != None: xml_str += " ratio='" + str(self.iso_ratio) + "'"
        if self.snap != None:
            if self.snap: xml_str += " snap='1'"
            else: xml_str += " snap='0'"
        if self.mode != None: xml_str+= "  mode='" + str(self.mode) + "'"
        if self.line != None: xml_str+= " line='" + str(self.line) + "'"
        xml_str += "/>"
        if (action == "update" and self.isUpdated) or action == "new":
            self.isUpdated = False
            return xml_str
        else: return ''

    def layerTakeDOM(self, xml_dom):
        if xml_dom.hasAttribute("color"):
            r,g,b = self.r_h.rgb_tuple(xml_dom.getAttribute("color"))
            self.set_color(cmpColour(r,g,b))
        #backwards compatible with non-isometric map formated clients
        ratio = RATIO_DEFAULT
        if xml_dom.hasAttribute("ratio"): ratio = xml_dom.getAttribute("ratio")
        if xml_dom.hasAttribute("mode"):
            self.SetMode(int(xml_dom.getAttribute("mode")))
        if xml_dom.hasAttribute("size"):
            self.unit_size = int(xml_dom.getAttribute("size"))
            self.unit_size_y = self.unit_size
        if xml_dom.hasAttribute("snap"):
            if (xml_dom.getAttribute("snap") == 'True') or (xml_dom.getAttribute("snap") == "1"): self.snap = True
            else: self.snap = False
        if xml_dom.hasAttribute("line"):
            self.SetLine(int(xml_dom.getAttribute("line")))
