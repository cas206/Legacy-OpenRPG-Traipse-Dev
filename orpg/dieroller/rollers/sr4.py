## a vs die roller as used by WOD games
#!/usr/bin/env python
# Copyright (C) 2000-2001 The OpenRPG Project
#
#   openrpg-dev@lists.sourceforge.net
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
# File: sr4.py
# Author: Veggiesama, ripped straight from Michael Edwards (AKA akoman)
# Maintainer:
# Version: 1.1
#
# 1.1: Now with glitch and critical glitch detection!
# 1.1: Cleaned up some of the output to make it simpler.
#
# Description: Modified from the original Shadowrun dieroller by akoman,
#              but altered to follow the new Shadowrun 4th Ed dice system.
#
#              SR4 VS
#              Typing [Xd6.vs(Y)] will roll X dice, checking each die
#              roll against the MIN_TARGET_NUMBER (default: 5). If it
#              meets or beats it, it counts as a hit. If the total hits
#              meet or beat the Y value (threshold), there's a success.
#
#              SR4 EDGE VS
#              Identical to the above function, except it looks like
#              [Xd6.edge(Y)] and follows the "Rule of Six". That rule
#              states any roll of 6 is counted as a hit and rerolled
#              with a potential to score more hits. The "Edge" bonus
#              dice must be included into X.
#
#              SR4 INIT
#              Typing [Xd6.init(Y)] will roll X dice, checking each
#              die for a hit. All hits are added to Y (the init attrib
#              of the player), to give an Init Score for the combat.
#
#              SR4 EDGE INIT
#              Typing [Xd6.initedge(Y)] or [Xd6.edgeinit(Y)] will do
#              as above, except adding the possibility of Edge dice.
#
#              Note about non-traditional uses:
#              - D6's are not required. This script will work with any
#                die possible, and the "Rule of Six" will only trigger
#                on the highest die roll possible. Not throughly tested.
#              - If you want to alter the minimum target number (ex.
#                score a hit on a 4, 5, or 6), scroll down and change
#                the global value MIN_TARGET_NUMBER to your liking.

__version__ = "1.1"

from std import std
from orpg.dieroller.base import *

MIN_TARGET_NUMBER = 5
GLITCH_NUMBER = 1

class sr4(std):
    name = "sr4"

    def __init__(self,source=[]):
        std.__init__(self,source)
        self.threshold = None
        self.init_attrib = None

    def vs(self,threshold=0):
        return sr4vs(self, threshold)

    def edge(self,threshold=0):
        return sr4vs(self, threshold, 1)

    def init(self,init_attrib=0):
        return sr4init(self, init_attrib)

    def initedge(self,init_attrib=0):
        return sr4init(self, init_attrib, 1)
    def edgeinit(self,init_attrib=0):
        return sr4init(self, init_attrib, 1)

    def countEdge(self,num):
        if num <= 1:
            self
        done = 1
        for i in range(len(self.data)):
            if (self.data[i].lastroll() >= num):
                # counts every rerolled 6 as a hit
                self.hits += 1
                self.data[i].extraroll()
                self.total += 1
                done = 0
            elif (self.data[i].lastroll() <= GLITCH_NUMBER):
                self.ones += 1
            self.total += 1
        if done:
            return self
        else:
            return self.countEdge(num)

    def countHits(self,num):
        for i in range(len(self.data)):
            if (self.data[i].lastroll() >= MIN_TARGET_NUMBER):
                # (Rule of Six taken into account in countEdge(), not here)
                self.hits += 1
            elif (self.data[i].lastroll() <= GLITCH_NUMBER):
                self.ones += 1
            self.total += 1

    def __str__(self):
        if len(self.data) > 0:
            self.hits = 0
            self.ones = 0
            self.total = 0
            for i in range(len(self.data)):
                if (self.data[i].lastroll() >= MIN_TARGET_NUMBER):
                    self.hits += 1
                elif (self.data[i].lastroll() <= GLITCH_NUMBER):
                    self.ones += 1
                self.total += 1
            firstpass = 0
            myStr = "["
            for a in self.data[0:]:
                if firstpass != 0:
                    myStr += ","
                firstpass = 1
                if a >= MIN_TARGET_NUMBER:
                    myStr += "<B>" + str(a) + "</B>"
                elif a <= GLITCH_NUMBER:
                    myStr += "<i>" + str(a) + "</i>"
                else:
                    myStr += str(a)
            myStr += "] " + CheckIfGlitch(self.ones, self.hits, self.total)
            myStr += "Hits: (" + str(self.hits) + ")"
        else:
            myStr = "[] = (0)"
        return myStr

die_rollers.register(sr4)

class sr4init(sr4):
    def __init__(self,source=[],init_attrib=1,edge=0):
        std.__init__(self,source)
        if init_attrib < 2:
            self.init_attrib = 2
        else:
            self.init_attrib = init_attrib
        self.dicesides = self[0].sides
        self.hits = 0
        self.ones = 0
        self.total = 0
        if edge:
            self.countEdge(self.dicesides)
        self.countHits(self.dicesides)

    def __str__(self):
        if len(self.data) > 0:
            firstpass = 0
            myStr = "["
            for a in self.data[0:]:
                if firstpass != 0:
                    myStr += ","
                firstpass = 1
                if a >= MIN_TARGET_NUMBER:
                    myStr += "<B>" + str(a) + "</B>"
                elif a <= GLITCH_NUMBER:
                    myStr += "<i>" + str(a) + "</i>"
                else:
                    myStr += str(a)
            myStr += "] " + CheckIfGlitch(self.ones, self.hits, self.total)
            init_score = str(self.init_attrib + self.hits)
            myStr += "InitScore: " + str(self.init_attrib) + "+"
            myStr += str(self.hits) + " = (" + init_score + ")"
        else:
            myStr = "[] = (0)"
        return myStr

class sr4vs(sr4):
    def __init__(self,source=[], threshold=1, edge=0):
        std.__init__(self, source)
        if threshold < 0:
            self.threshold = 0
        else:
            self.threshold = threshold
        self.dicesides = self[0].sides
        self.hits = 0
        self.ones = 0
        self.total = 0
        if edge:
            self.countEdge(self.dicesides)
        self.countHits(self.dicesides)

    def __str__(self):
        if len(self.data) > 0:
            firstpass = 0
            myStr = "["
            for a in self.data[0:]:
                if firstpass != 0:
                    myStr += ","
                firstpass = 1
                if a >= MIN_TARGET_NUMBER:
                    myStr += "<B>" + str(a) + "</B>"
                elif a <= GLITCH_NUMBER:
                    myStr += "<i>" + str(a) + "</i>"
                else:
                    myStr += str(a)
            #myStr += "] Threshold=" + str(self.threshold)
            myStr += "] vs " + str(self.threshold) + " "
            myStr += CheckIfGlitch(self.ones, self.hits, self.total)
            if self.hits >= self.threshold:
                myStr += "*SUCCESS* "
            else:
                myStr += "*FAILURE* "
            myStr += "Hits: (" + str(self.hits) + ")"
        else:
            myStr = "[] = (0)"
        return myStr

def CheckIfGlitch(ones, hits, total_dice):
    if (ones * 2) >= total_dice:
        if hits >= 1:
            return "*GLITCH* "
        else:
            return "*CRITICAL GLITCH* "
    else:
        return ""
