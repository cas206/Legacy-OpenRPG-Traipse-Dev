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

from die import *
from wod import *
from d20 import *
from hero import *
from shadowrun import *
from sr4 import *
from hackmaster import *
from wodex import *
from srex import *
from gurps import *
from runequest import *
from savage import *
from trinity import *
import re

rollers = ['std','wod','d20','hero','shadowrun', 'sr4','hackmaster','srex','wodex', 'gurps', 'runequest', 'sw', 'trinity']

class roller_manager:
    
    def __init__(self,roller_class="d20"):
        try: self.setRoller(roller_class)
        except: self.roller_class = "std"

    
    def setRoller(self,roller_class):
        try:
            rollers.index(roller_class)
            self.roller_class = roller_class
        except: raise Exception, "Invalid die roller!"

    
    def getRoller(self):
        return self.roller_class

    
    def listRollers(self):
        return rollers

    
    def stdDieToDClass(self,match):
        s = match.group(0)
        (num,sides) = s.split('d')

        if sides.strip().upper() == 'F': sides = "'f'"
        try:
            if int(num) > 100 or int(sides) > 10000:
                return None
        except: pass
        return "(" + num.strip() + "**" + self.roller_class + "(" + sides.strip() + "))"

    #  Use this to convert ndm-style (3d6) dice to d_base format
    
    def convertTheDieString(self,s):
        reg = re.compile("\d+\s*[a-zA-Z]+\s*[\dFf]+")
        (result, num_matches) = reg.subn(self.stdDieToDClass, s)
        if num_matches == 0 or result is None:
            try:
                s2 = self.roller_class + "(0)." + s
                test = eval(s2)
                return s2
            except: pass
        return result

    
    def proccessRoll(self,s):
        return str(eval(self.convertTheDieString(s)))

DiceManager = roller_manager
