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
# File: shadowrun.py
# Author: Michael Edwards (AKA akoman)
# Maintainer:
# Version: 1.0
#
# Description: A modified form of the World of Darkness die roller to
#              conform to ShadowRun rules-sets. Thanks to the ORPG team
#              for the original die rollers.
#              Thanks to tdb30_ for letting me think out loud with him.
#         I take my hint from the HERO dieroller: It creates for wildly variant options
#         Further, .vs and .open do not work together in any logical way. One method of
#         chaining them results in a [Bad Dice Format] and the other results in a standard
#         output from calling .open()

#         vs is a classic 'comparison' method function, with one difference. It uses a
#           c&p'ed .open(int) from die.py but makes sure that once the target has been exceeded
#           then it stops rerolling. The overhead from additional boolean checking is probably
#           greater than the gains from not over-rolling. The behaviour is in-line with
#           Shadowrun Third Edition which recommends not rolling once you've exceeded the target
#         open is an override of .open(int) in die.py. The reason is pretty simple. In die.py open
#           refers to 'open-ended rolling' whereas in Shadowrun it refers to an 'Open Test' where
#           the objective is to find the highest die total out of rolled dice. This is then generally
#           used as the target in a 'Success Test' (for which .vs functions)
from die import *

__version__ = "1.0"

class shadowrun(std):
    
    def __init__(self,source=[],target=2):
        std.__init__(self,source)

    
    def vs(self,target):
        return srVs(self, target)

    
    def open(self):
        return srOpen(self)

class srVs(std):
    
    def __init__(self,source=[], target=2):
        std.__init__(self, source)
        # In Shadowrun, not target number may be below 2. All defaults are set to two and any
        # thing lower is scaled up.
        if target < 2:
            self.target = 2
        else:
            self.target = target
        # Shadowrun was built to use the d6 but in the interests of experimentation I have
        # made the dieroller generic enough to use any die type
        self.openended(self[0].sides)

    
    def openended(self,num):
        if num <= 1:
            self
        done = 1
        for i in range(len(self.data)):
            if (self.data[i].lastroll() >= num) and (self.data[i] < self.target):
                self.data[i].extraroll()
                done = 0
        if done:
            return self
        else:
            return self.openended(num)

    
    def __sum__(self):
        s = 0
        for r in self.data:
            if r >= self.target:
                s += 1
        return s

    
    def __str__(self):
        if len(self.data) > 0:
            myStr = "[" + str(self.data[0])
            for a in self.data[1:]:
                myStr += ","
                myStr += str(a)
            myStr += "] vs " + str(self.target) + " for a result of (" + str(self.sum()) + ")"
        else:
            myStr = "[] = (0)"

        return myStr

class srOpen(std):
    
    def __init__(self,source=[]):
        std.__init__(self,source)
        self.openended(self[0].sides)

    
    def openended(self,num):
        if num <= 1:
            self
        done = 1
        for i in range(len(self.data)):
            if self.data[i].lastroll() == num:
                self.data[i].extraroll()
                done = 0
        if done:
            return self
        else:
            return self.openended(num)

    
    def __sum__(self):
        s = 0
        for r in self.data:
            if r > s:
                s = r
        return s

    
    def __str__(self):
        if len(self.data) > 0:
            myStr = "[" + str(self.data[0])
            for a in self.data[1:]:
                myStr += ","
                myStr += str(a)
            self.takeHighest(1)
            myStr += "] for a result of (" + str(self.__sum__().__int__()) + ")"
        else:
            myStr = "[] = (0)"

        return myStr
