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
# File: mapper/base.py
# Author: Chris Davis
# Maintainer:
# Version:
#   $Id: base.py,v 1.18 2007/02/12 02:29:08 digitalxero Exp $
#
# Description:
#
__version__ = "$Id: base.py,v 1.18 2007/02/12 02:29:08 digitalxero Exp $"

from images import ImageHandler
from orpg.tools.rgbhex import *
from orpg.orpg_windows import *
from orpg.orpg_xml import *
from math import *
from threading import Lock
import time

class cmpPoint(wx.Point):
    def __init__(self,*_args,**_kwargs):
        wx.Point.__init__(self,*_args,**_kwargs)

    def __cmp__(self,other):
        try:
            if self.x < other.x: return -1
            elif self.x > other.x: return 1
            elif self.y < other.y: return -1
            elif self.y > other.y: return 1
            else: return 0
        except: return -2

class cmpColour(wx.Colour):
    def __init__(self,*_args,**_kwargs):
        wx.Colour.__init__(self,*_args,**_kwargs)

    def __cmp__(self,other):
        try:
            (r,g,b) = self.Get()
            my_value = b*256*256 + g*256 + r
            (r,g,b) = other.Get()
            other_value = b*256*256 + g*256 + r
            if my_value < other_value: return -1
            elif my_value > other_value: return 1
            else: return 0
        except: return -2

class protectable_attributes:

    def __init__(self):
        self._set("_protected_attr",[])

    def _set(self,name,value):
        self.__dict__[name] = value

    def __setattr__(self,name,value):
        if name in self._protected_attr:
            full_name = "_protect_" + name
            if hasattr(self,full_name):
                (p,c) = getattr(self,full_name)
                if p != value: self._set(full_name,(value,1))
            else: self._set(full_name,(value,1))
        else: self._set(name,value)

    def __getattr__(self,name):
        if name in self._protected_attr:
            (p,c) = self.__dict__["_protect_" + name]
            return p
        else: raise AttributeError

    def _clean_attr(self,name):
        if name in self._protected_attr:
            (p,c) = self.__dict__["_protect_" + name]
            self._set("_protect_" + name,(p,0))

    def _dirty_attr(self,name):
        if name in self._protected_attr:
            (p,c) = self.__dict__["_protect_" + name]
            self._set("_protect_" + name,(p,1))

    def _changed_attr(self):
        changed = {}
        for name in self._protected_attr:
            (p,c) = self.__dict__["_protect_" + name]
            if c: changed[name] = p
        return changed

    def _clean_all_attr(self):
        for name in self._protected_attr:
            (p,c) = self.__dict__["_protect_" + name]
            self._set("_protect_" + name,(p,0))

    def _dirty_all_attr(self):
        for name in self._protected_attr:
            (p,c) = self.__dict__["_protect_" + name]
            self._set("_protect_" + name,(p,1))

##-----------------------------
## base class for layer objects
##-----------------------------

class layer_base:

    def __init__(self):
        self.lock = Lock()

    def layerDraw(self,dc,scale='',topleft='',size=''):
        pass

    def layerToXML(self, action):
        pass

    def layerTakeDOM(self, xml_dom):
        pass

    def hit_test(self,pos):
        pass
