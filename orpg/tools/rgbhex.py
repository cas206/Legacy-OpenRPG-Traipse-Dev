# Copyright (C) 2000-2001 The OpenRPG Project
#
#       openrpg-dev@lists.sourceforge.net
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
# File: rgbhex.py
# Author: Chris Davis
# Maintainer:
# Version:
#   $Id: rgbhex.py,v Traipse 'Ornery-Orc' prof.ebral Exp $
#
# Description: rgb to hex utility

from orpg.orpg_wx import *


#####################
## RPGHex Tool
#####################

class RGBHex:
    "Tools for Converting from hex to rgb and versa vicea"

    def rgb_tuple(self,hexnum):
        red = self.c2rgb(hexnum[1:3])
        green = self.c2rgb(hexnum[3:5])
        blue = self.c2rgb(hexnum[5:7])
        #print "Converted %s to %s, %s, %s" % (hexnum, red, green, blue)
        return (red, green, blue)

    def hexstring(self, red, green, blue):
        hexcolor = "#" + self.c2hex(red)
        hexcolor = hexcolor + self.c2hex(green)
        hexcolor = hexcolor + self.c2hex(blue)
        return hexcolor

    def c2rgb(self,num):
        "Converts from hex to rgb"
        first = num[0]
        second = num[1]
        s = 0
        if first == 'a': s = 10 * 16
        elif first == 'b': s = 11 * 16
        elif first == 'c': s = 12 * 16
        elif first == 'd': s = 13 * 16
        elif first == 'e': s = 14 * 16
        elif first == 'f': s = 15 * 16
        else: s = s+ int(first) * 16
        if second == 'a': s = s + 10
        elif second == 'b': s = s + 11
        elif second == 'c': s = s + 12
        elif second == 'd': s = s + 13
        elif second == 'e': s = s + 14
        elif second == 'f': s = s + 15
        else: s = s + int(second)
        return s

    def c2hex(self,num):
        "Converts from RGB to Hex"
        first = num/16
        second = num%16
        s = ""
        if first == 10: s = s+"a"
        elif first == 11: s = s+"b"
        elif first == 12: s = s+"c"
        elif first == 13: s = s+"d"
        elif first == 14: s = s+"e"
        elif first == 15: s = s+"f"
        else: s = s+ str(first)
        if second == 10: s = s+"a"
        elif second == 11: s = s+"b"
        elif second == 12: s = s+"c"
        elif second == 13: s = s+"d"
        elif second == 14: s = s+"e"
        elif second == 15: s = s+"f"
        else: s = s+ str(second)
        return s

    def do_hex_color_dlg(self, parent):
        data = wx.ColourData()
        data.SetChooseFull(True)
        dlg = wx.ColourDialog(parent, data)
        if dlg.ShowModal() == wx.ID_OK:
            data = dlg.GetColourData()
            (red,green,blue) = data.GetColour().Get()
            hexcolor = self.hexstring(red, green, blue)
            dlg.Destroy()
            return hexcolor
        else:
            dlg.Destroy()
            return None
