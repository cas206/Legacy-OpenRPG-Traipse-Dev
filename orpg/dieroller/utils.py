#!/usr/bin/env python
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
# File: dieroller/utils.py
# Author: OpenRPG Team
# Maintainer:
# Version:
#   $Id: utils.py,v 1.22 2007/05/05 05:30:10 digitalxero Exp $
#
# Description: Classes to help manage the die roller
#

__version__ = "$Id: utils.py,v 1.22 2007/05/05 05:30:10 digitalxero Exp $"

import re

import orpg.dieroller.rollers
from orpg.dieroller.base import die_rollers

class roller_manager(object):
    def __new__(cls):
        it = cls.__dict__.get("__it__")
        if it is not None: return it
        cls.__it__ = it = object.__new__(cls)
        it._init()
        return it

    def _init(self):
        self.setRoller('std')

    def setRoller(self, roller_class):
        try: self.roller_class = die_rollers[roller_class]
        except KeyError: raise Exception("Invalid die roller!")

    def getRoller(self):
        return self.roller_class.name

    def listRollers(self):
        return die_rollers.keys()

    def stdDieToDClass(self,match):
        s = match.group(0)
        num_sides = s.split('d')
        if len(num_sides) > 1: num_sides; num = num_sides[0]; sides = num_sides[1]
        else: return self.non_stdDieToDClass(s) # Use a non standard converter.

        if sides.strip().upper() == 'F': sides = "'f'"
        try:
            if int(num) > 100 or int(sides) > 10000: return None
        except: pass
        ret = ['(', num.strip(), "**die_rollers['", self.getRoller(), "'](",
                sides.strip(), '))']
        return ''.join(ret)

    def non_stdDieToDClass(self, s):
        num_sides = s.split('v')
        if len(num_sides) > 1: 
            num_sides; num = num_sides[0]; sides = num_sides[1]
            if self.getRoller() == 'mythos': sides = '12'; target = num_sides[1]
            elif self.getRoller() == 'wod': sides = '10'; target = num_sides[1]
            ret = ['(', num.strip(), "**die_rollers['", self.getRoller(), "'](",
                    sides.strip(), ')).vs(', target, ')']
            return ''.join(ret)

        num_sides = s.split('k')
        if len(num_sides) > 1: 
            num_sides; num = num_sides[0]; sides = '10'; target = num_sides[1]
            ret = ['(', num.strip(), "**die_rollers['", self.getRoller(), "'](",
                    sides.strip(), ')).takeHighest(', target, ').open(10)']
            return ''.join(ret)

    #  Use this to convert ndm-style (3d6) dice to d_base format
    def convertTheDieString(self,s):
        reg = re.compile("(?:\d+|\([0-9\*/\-\+]+\))\s*[a-zA-Z]+\s*[\dFf]+")
        (result, num_matches) = reg.subn(self.stdDieToDClass, s)
        if num_matches == 0 or result is None:
            try:
                s2 = self.roller_class + "(0)." + s
                test = eval(s2)
                return s2
            except: pass
        return result

    def proccessRoll(self, s):
        return str(eval(self.convertTheDieString(s)))
