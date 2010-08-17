## 7th Sea Dieroller
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

class seventhsea(std):
    name = "7sea"
    regExpression = "[\(0-9\*\-\+\)]+[a-zA-Z]+[0-9]+"

    def __init__(self,source=[]):
        std.__init__(self,source)

    def non_stdDie(self, match):
        s = match.group(0)
        num_sides = s.split('k')
        if len(num_sides) > 1: 
            num_sides; num = num_sides[0]; sides = '10'; target = num_sides[1]
            ret = ['(', num.strip(), "**die_rollers['7sea'](",
                    sides.strip(), ')).takeHighest(', target, ').open(10)']
            s = ''.join(ret); return str(eval(s))

die_rollers.register(seventhsea)
