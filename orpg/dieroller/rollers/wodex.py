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
# File: wodex.py
# Original Author: Darloth
# Maintainer:
# Original Version: 1.0
#
# Description: A modified form of the World of Darkness die roller to
#              conform to ShadowRun rules-sets, then modified back to the WoD for
#              the new WoD system. Thanks to the ORPG team
#              for the original die rollers.
#              Much thanks to whoever wrote the original shadowrun roller (akoman I believe)


from std import std
from orpg.dieroller.base import *

__version__ = "$Id: wodex.py,v Traipse 'Ornery-Orc' prof.ebral Exp $"

class wodex(std):
    name = "wodex"

    def __init__(self,source=[]):
        std.__init__(self,source)

    def vs(self,actualtarget=6):
        return oldwodVs(self,actualtarget,(6))

    def wod(self,actualtarget=8):
        return newwodVs(self,actualtarget,(8))

    def exalt(self, actualtarget=7):
        return exaltVs(self, actualtarget)

    def exaltDmg(self, actualtarget=7):
        return exaltDmg(self, actualtarget)

    def vswide(self,actualtarget=6,maxtarget=10):    #wide simply means it reports TNs from 2 to a specified max.
        return oldwodVs(self,actualtarget,2,maxtarget)

die_rollers.register(wodex)

class oldwodVs(std):
    def __init__(self,source=[],actualtarget=6,mintn=2,maxtn=10):
        std.__init__(self, source)
        if actualtarget > 10:
            actualtarget = 10
        if mintn > 10:
            mintn = 10
        if maxtn > 10:
            maxtn = 10
        if actualtarget < 2:
            self.target = 2
        else:
            self.target = actualtarget
        #if the target number is higher than max (Mainly for wide rolls) then increase max to tn
        if actualtarget > maxtn:
            maxtn = actualtarget
        if actualtarget < mintn:
            mintn = actualtarget
        #store minimum for later use as well, also in result printing section.
        if mintn < 2:
            self.mintn = 2
        else:
            self.mintn = mintn
        self.maxtn = maxtn #store for later use in printing results. (Yeah, these comments are now disordered)

        # WoD etc uses d10 but i've left it so it can roll anything openended
        # self.openended(self[0].sides)

    #count successes, by looping through each die, and checking it against the currently set TN
    #1's subtract successes.
    def __sum__(self):
        s = 0
        for r in self.data:
            if r >= self.target:
                s += 1
            elif r == 1:
                s -= 1
        return s

    #a modified sum, but this one takes a target argument, and is there because otherwise it is difficult to loop through
    #tns counting successes against each one without changing target, which is rather dangerous as the original TN could
    #easily be lost. 1s subtract successes from everything.
    def xsum(self,curtarget):
        s = 0
        for r in self.data:
            if r >= curtarget:
                s += 1
            elif r == 1:
                s -= 1
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
                if (targ == self.target):
                    myStr += "<b>"
                myStr += "(" + str(self.xsum(targ)) + "&nbsp;vs&nbsp;" + str(targ) + ") "
                if (targ == self.target):
                    myStr += "</b>"
        else:
            myStr = "[] = (0)"

        return myStr

class newwodVs(std):
    def __init__(self,source=[],actualtarget=8,mintn=8,maxtn=8):
        std.__init__(self, source)
        if actualtarget > 30:
            actualtarget = 30
        if mintn > 10:
            mintn = 10
        if maxtn > 10:
            maxtn = 10
        if actualtarget < 2:
            self.target = 2
        else:
            self.target = actualtarget
        #if the target number is higher than max (Mainly for wide rolls) then increase max to tn
        if actualtarget > maxtn:
            maxtn = actualtarget
        if actualtarget < mintn:
            mintn = actualtarget
        #store minimum for later use as well, also in result printing section.
        if mintn < 2:
            self.mintn = 2
        else:
            self.mintn = mintn
        self.maxtn = maxtn #store for later use in printing results. (Yeah, these comments are now disordered)

        # WoD etc uses d10 but i've left it so it can roll anything openended
        # self.openended(self[0].sides)

    #a modified sum, but this one takes a target argument, and is there because otherwise it is difficult to loop through
    #tns counting successes against each one without changing target, which is rather dangerous as the original TN could
    #easily be lost. 1s subtract successes from original but not re-rolls.
    def xsum(self,curtarget,subones=1):
        s = 0
        done = 1
        for r in self.data:
            if r >= curtarget:
                s += 1
            elif ((r == 1) and (subones == 1)):
                s -= 1
        if r == 10:
            done = 0
            subones = 0
            self.append(di(10))
        if done == 1:
            return s
        else:
            return self.xsum(0)

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


    def __str__(self):
        if len(self.data) > 0:
            myStr = "[" + str(self.data[0])
            for a in self.data[1:]:
                myStr += ","
                myStr += str(a)
            myStr += "] Results: "
            #cycle through from mintn to maxtn, summing successes for each separate TN
            for targ in range(self.mintn,self.maxtn+1):
                if (targ == self.target):
                    myStr += "<b>"
                myStr += "(" + str(self.xsum(targ)) + "&nbsp;vs&nbsp;" + str(targ) + ") "
                if (targ == self.target):
                    myStr += "</b>"
        else:
            myStr = "[] = (0)"

        return myStr

class exaltVs(std):
    def __init__(self, source=[], actualtarget=7):
        std.__init__(self, source)

        if actualtarget > 10:
            actualtarget = 10

        if actualtarget < 2:
            self.target = 2
        else:
            self.target = actualtarget


    def xsum(self, target):
        s = 0

        for r in self.data:
            if r >= target:
                s += 1
            if r == 10:
                s += 1

        return s


    def __str__(self):
        if len(self.data) > 0:
            myStr = str(self.data)
            myStr += " Results: "

            succ = self.xsum(self.target)
            if succ == 0 and 1 in self.data:
                myStr += 'BOTCH!'
            elif succ == 0:
                myStr += str(succ) + " Failure"
            elif succ == 1:
                myStr += str(succ) + " Success"
            else:
                myStr += str(succ) + " Successes"

            return myStr

class exaltDmg(std):
    def __init__(self, source=[], actualtarget=7):
        std.__init__(self, source)
        if actualtarget > 10:
            actualtarget = 10

        if actualtarget < 2:
            self.target = 2
        else:
            self.target = actualtarget

    def xsum(self, target):
        s = 0

        for r in self.data:
            if r >= target:
                s += 1
        return s

    def __str__(self):
        if len(self.data) > 0:
            myStr = str(self.data)
            myStr += " Results: "

            succ = self.xsum(self.target)

            if succ == 0 and 1 in self.data:
                myStr += 'BOTCH!'
            elif succ == 0:
                myStr += str(succ) + " Failure"
            elif succ == 1:
                myStr += str(succ) + " Success"
            else:
                myStr += str(succ) + " Successes"

            return myStr
