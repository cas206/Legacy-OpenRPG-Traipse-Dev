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
#   $Id: utils.py,v Traipse 'Ornery-Orc' prof.ebral Exp  $
#
# Description: Classes to help manage the die roller
#

__version__ = "$Id: utils.py,v Traipse 'Ornery-Orc' prof.ebral Exp  Exp $"

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

    def stdDieToDClass(self, match):
        s = match.group(0); self.eval = str(match.string)
        num_sides = s.split('d')
        if len(num_sides) > 1: 
            num_sides; num = num_sides[0]; sides = num_sides[1]
            if sides.strip().upper() == 'F': sides = "'f'"
            try:
                if int(num) > 100 or int(sides) > 10000: return None
            except: pass
            ret = ['(', num.strip(), "**die_rollers['", self.getRoller(), "'](",
                    sides.strip(), '))']
            s =  ''.join(ret)
            self.eval = s
            return s

        ## Portable Non Standard Die Characters #Prof-Ebral
        else: s = die_rollers._rollers[self.getRoller()]().non_stdDie(s); return s

    #  Use this to convert ndm-style (3d6) dice to d_base format
    def convertTheDieString(self,s):
        self.result = ''
        reg = re.compile("(?:\d+|\([0-9\*/\-\+]+\))\s*[a-zA-Z]+\s*[\dFf]+")
        (result, num_matches) = reg.subn(self.stdDieToDClass, s)
        if num_matches == 0 or result is None:
            reg = re.compile("(?:\d+|\([0-9\*/\-\+]+\))\s*[a-zA-Z]+\s*[a-zA-Z]+") ## Prof Ebral
            (result, num_matches) = reg.subn(self.stdDieToDClass, s) ## Prof Ebral
            """try: ## Kinda pointless when you can create new Regular Expressions
                s2 = self.roller_class + "(0)." + s ## Broken method
                test = eval(s2)
                return s2
            except Exception, e: print e; pass"""
            self.result = result
            try: return self.do_math(s)
            except: pass
        return result

    def do_math(self, s):
        return str(eval(s))

    def proccessRoll(self, s):
        v = self.convertTheDieString(s)
        try: b = str(eval(v))
        except: 
            if v == self.eval: b = s
            else: b = str(v) ##Fail safe for non standard dice.
        return b

