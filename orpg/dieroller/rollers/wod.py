## a vs die roller as used by WOD games
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
# File: wod.py
# Author: OpenRPG Dev Team
# Maintainer:
# Version:
#   $Id: wod.py,v Traipse 'Ornery-Orc' prof.ebral Exp $
#
# Description: WOD die roller
#
# Targetthr is the Threshhold target
# for compatibility with Mage die rolls.
# Threshhold addition by robert t childers

__version__ = "$Id: wod.py,v Traipse 'Ornery-Orc' prof.ebral Exp $"

from std import std
from orpg.dieroller.base import *

class wod(std):
    name = "wod"
    regExpression = "[\(0-9\*\-\+\)]+[a-zA-Z]+[0-9]+"

    def __init__(self,source=[],target=0,targetthr=0):
        std.__init__(self,source)
        self.target = target
        self.targetthr = targetthr

    def vs(self,target):
        self.target = target
        return self

    def thr(self,targetthr):
        self.targetthr = targetthr
        return self

    def sum(self):
        rolls = []
        s = 0
        s1 = self.targetthr
        botch = 0
        for a in self.data:
            rolls.extend(a.gethistory())
        for r in rolls:
            if r >= self.target or r == 10:
                s += 1
                if s1 >0:
                    s1 -= 1
                    s -= 1
                else: botch = 1
            elif r == 1: s -= 1
            if botch == 1 and s < 0: s = 0
        return s

    def __str__(self):
        if len(self.data) > 0:
            myStr = "[" + str(self.data[0])
            for a in self.data[1:]:
                myStr += ","
                myStr += str(a)
            if self.sum() < 0: myStr += "] vs " +str(self.target)+" result of a botch"
            elif self.sum() == 0: myStr += "] vs " +str(self.target)+" result of a failure"
            else: myStr += "] vs " +str(self.target)+" result of (" + str(self.sum()) + ")"
        return myStr

    def non_stdDie(self, match):
        s = match.group(0)
        num_sides = s.split('v')
        if len(num_sides) > 1: 
            num_sides; num = num_sides[0]; sides = num_sides[1]
            sides = '10'; target = num_sides[1]
            ret = ['(', num.strip(), "**die_rollers['wod'](",
                    sides.strip(), ')).vs(', target, ')']
            s = ''.join(ret); return s

die_rollers.register(wod)
