#!/usr/bin/env python
# Copyright (C) 2000-2010 The OpenRPG Project
#
#       owner@madmathlabs.com
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
# Maintainer (Traipse): Tyler Starke
# Version:
#   $Id: utils.py,v Traipse 'Ornery-Orc' prof.ebral Exp  $
#
# Description: Classes to help manage the die roller
#

import re

import orpg.dieroller.rollers
from orpg.dieroller.base import die_rollers

"""
Die Roller Changes:
I've made some changes for ease of reading. Below you see the new formula and the old depricated formula. The new formula is easier to understand
and works a little better with math. Try this: [(2+4)+4d(6+8)+(4*4)] with both formulas. Traipse succeeds, Standard (1.7.1) fails.

The new formula deals only with numbers of the Fudge roller. The math has a required process flow, which is unliked currently by me but I am not
going to spend more time on at currently to correct it. It occurs when using paranthesis on the facet. If paranthesis are used no modifier can be added
at the end, but you can added it before the roll.

This is the standard roller formula: (Math D Numbers or Math or Fudge). If that fails the new non_stdDie looks for a regExpression formula inside
the current die roller, set under the name. So all of that bloat to include the english language in the Gilcrease 1.8.0 remains bloat and Traipse's
dice can be liberated to do what they want, where they want, when they want.
"""

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

    def completeMath(self, matches):
        s = matches.group(0)
        try: doMath = str(eval(s))
        except: doMath = s
        return doMath

    def stdDie_Class(self, match):
        s = match.group(0)
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
            return s

    #  Use this to convert ndm-style (3d6) dice to d_base format
    def stdDie(self, s):
        math = '[\(0-9\/\*\-\+\)]+'
        reg = re.compile('[0-9]+d\s*([0-9]+|'+math+'|[fF])')
        #reg = re.compile("(?:\d+|\([0-9\*/\-\+]+\))\s*[a-zA-Z]+\s*[\dFf]+") ## Original
        try:
            (result, num_matches) = reg.subn(self.stdDie_Class, s)
            #print 'main', result, num_matches
            if num_matches == 0 or result is None:
                reg = re.compile(math)
                (result, math_matches) = reg.subn(self.completeMath, s)
                #print 'math1', result, num_matches
                reg = re.compile('[0-9]+d\s*([0-9]+|'+math+'|[fF])')
                (result, num_matches) = reg.subn(self.stdDie_Class, result)
                #print 'math2', result, num_matches
        except Exception, e: 
            print 'Die string conversion failed,', e
            return s
        return str(result)

    def nonStdDie(self, s):
        math = '[\(0-9\/\*\-\+\)]+'
        reg = re.compile(math)
        (result, math_matches) = reg.subn(self.completeMath, s)

        reg = re.compile(die_rollers._rollers[self.getRoller()].regExpression)
        (result, num_matches) = reg.subn(self.roller_class().non_stdDie, s) ## Currently skipping math

        if num_matches == 0 or result is None: return s
        else: return result

    def proccessRoll(self, s):
        ## Re arranged to allow the non standard dice to use the built in roller methods, 
        ## not re-written roller methods.
        b = self.stdDie(s)
        try: b = str(eval(b))
        except:
            b = self.nonStdDie(s)
            try: b = str(eval(b))
            except: pass
        return b


