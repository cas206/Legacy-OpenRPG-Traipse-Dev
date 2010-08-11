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
# File: srex.py
# Original Author: Michael Edwards (AKA akoman)
# Maintainer:
# Original Version: 1.0
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

# Modified by: Darloth
# Mod Version: 1.1
# Modified Desc:
#       I've altered the vs call to make it report successes against every target number (tn)
#       in a specified (default 3) range, with the original as median.
#       This reduces rerolling if the TN was calculated incorrectly, and is also very useful
#       when people are rolling against multiple TNs, which is the case with most area-effect spells.
#       To aid in picking the specified TN out from the others, it will be in bold.
#       vswide is a version which can be used with no arguments, or can be used to get a very wide range, by
#       directly specifying the upper bound (Which is limited to 30)

from std import std
from orpg.dieroller.base import *

__version__ = "1.1"

class srex(std):
    name = "srex"

    def __init__(self,source=[]):
        std.__init__(self,source)

    def vs(self,actualtarget=4,tnrange=3):        #reports all tns around specified, max distance of range
        return srVs(self,actualtarget,(actualtarget-tnrange),(actualtarget+tnrange))

    def vswide(self,actualtarget=4,maxtarget=12):    #wide simply means it reports TNs from 2 to a specified max.
        return srVs(self,actualtarget,2,maxtarget)

    def open(self):         #unchanged from standard shadowrun open.
        return srOpen(self)

die_rollers.register(srex)

class srVs(std):
    def __init__(self,source=[],actualtarget=4,mintn=2,maxtn=12):
        std.__init__(self, source)
        if actualtarget > 30:
            actualtarget = 30
        if mintn > 30:
            mintn = 30
        if maxtn > 30:
            maxtn = 30
        # In Shadowrun, not target number may be below 2. Any
        # thing lower is scaled up.
        if actualtarget < 2:
            self.target = 2
        else:
            self.target = actualtarget
        #if the target number is higher than max (Mainly for wide rolls) then increase max to tn
        if actualtarget > maxtn:
            maxtn = actualtarget
        #store minimum for later use as well, also in result printing section.
        if mintn < 2:
            self.mintn = 2
        else:
            self.mintn = mintn
        self.maxtn = maxtn #store for later use in printing results. (Yeah, these comments are now disordered)

        # Shadowrun was built to use the d6 but in the interests of experimentation I have
        # made the dieroller generic enough to use any die type
        self.openended(self[0].sides)

    def openended(self,num):
        if num <= 1:
            self
        done = 1

        #reroll dice if they hit the highest number, until they are greater than the max TN (recursive)
        for i in range(len(self.data)):
            if (self.data[i].lastroll() >= num) and (self.data[i] < self.maxtn):
                self.data[i].extraroll()
                done = 0
        if done:
            return self
        else:
            return self.openended(num)

    #count successes, by looping through each die, and checking it against the currently set TN
    def __sum__(self):
        s = 0
        for r in self.data:
            if r >= self.target:
                s += 1
        return s

    #a modified sum, but this one takes a target argument, and is there because otherwise it is difficult to loop through
    #tns counting successes against each one without changing target, which is rather dangerous as the original TN could
    #easily be lost.
    def xsum(self,curtarget):
        s = 0
        for r in self.data:
            if r >= curtarget:
                s += 1
        return s


    def __str__(self):
        if len(self.data) > 0:
            myStr = "[" + str(self.data[0])
            for a in self.data[1:]:
                myStr += ","
                myStr += str(a)
            myStr += "] Results: "
            #cycle through from mintn to maxtn, summing successes for each separate TN
            for targ in range(self.mintn,self.maxtn+1):
                if targ == self.target:
                    myStr += "<b>"
                myStr += "(" + str(self.xsum(targ)) + "&nbsp;vs&nbsp;" + str(targ) + ") "
                if targ == self.target:
                    myStr += "</b>"
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
