#!/usr/bin/env python
# Copyright Not Yet, see how much I trust you
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
# File: hackmaster.py
# Author: Ric Soard
# Maintainer:
# Version:
#   $Id: hackmaster.py,v Traipse 'Ornery-Orc' prof.ebral Exp
#
# Description: special die roller for HackMaster(C)(TM) RPG
#               has penetration damage - .damage(bonus,honor)
#               has attack - .attack(bonus, honor)
#               has severity .severity(honor)
#               has help - .help()
#
#

__version__ = "$Id: hackmaster.py,v Traipse 'Ornery-Orc' prof.ebral Exp $"

import random
from std import std
from orpg.dieroller.base import *

#hackmaster Class basically passes into functional classes
class hackmaster(std):
    name = "hackmaster"

    def __init__(self,source=[]):
        std.__init__(self,source)

    def damage(self, mod, hon):
        return HMdamage(self, mod, hon)

    def attack(self, mod, hon):
        return HMattack(self, mod, hon)

    def help(self):
        return HMhelp(self)

    def severity(self, honor):
        return HMSeverity(self, honor)

die_rollers.register(hackmaster)

# HM Damage roller - rolles penetration as per the PHB - re-rolles on max die - 1, adds honor to the penetration rolls
# and this appears to be invisible to the user ( if a 4 on a d4 is rolled a 3 will appear and be followed by another
# die. if High honor then a 4 will appear followed by a another die.
class HMdamage(std):
    def __init__(self,source=[], mod = 0, hon = 0):
        std.__init__(self,source)
        self.mod = mod
        self.hon = hon
        self.check_pen()
        #here we roll the mod die
        self.append(static_di(self.mod))
        #here we roll the honor die
        self.append(static_di(self.hon))

    def damage(mod = 0, hon = 0):
        self.mod = mod
        self.hon = hon

# This function is called by default to display the die string to the chat window.
# Our die string attempts to explain the results
    def __str__(self):
        myStr = "Damage "
        myStr += "[Damage Roll, Modifiers, Honor]: " + " [" + str(self.data[0])
        for a in self.data[1:]:
            myStr += ","
            myStr += str(a)
        myStr += "] = (" + str(self.sum()) + ")"

        return myStr

# This function checks to see if we need to reroll for penetration
    def check_pen(self):
        for i in range(len(self.data)):
            if self.data[i].lastroll() >= self.data[i].sides:
                self.pen_roll(i)

#this function rolls the penetration die, and checks to see if it needs to be re-rolled again.
    def pen_roll(self,num):
        result = int(random.uniform(1,self.data[num].sides+1))
        self.data[num].value += (result - 1 + self.hon)
        self.data[num].history.append(result - 1 + self.hon)
        if result >= self.data[num].sides:
            self.pen_roll(num)

# this function rolls for the HM Attack. the function checks for a 20 and displays critical, and a 1
# and displays fumble
class HMattack(std):
    def __init__(self, source=[], mod = 0, base_severity = 0, hon = 0, size = 0):
        std.__init__(self,source)
        self.size = size
        self.mod = mod
        self.base_severity = base_severity
        self.hon = hon
        self.fumble = 0
        self.crit = 0
        self.check_crit()
        #this is a static die that adds the modifier
        self.append(static_di(self.mod))
        #this is a static die that adds honor, we want high rolls so it's +1
        self.append(static_di(self.hon))

    def check_crit(self):
        if self.data[0] == self.data[0].sides:
            self.crit = 1
        if self.data[0] == 1:
            self.fumble = 1


    #this function is the out put to the chat window, it basicaly just displays the roll unless
    #it's a natural 20, or a natural 1
    def __str__(self):
        if self.crit > 0:
            myStr = "Critical Hit!!: "
        elif self.fumble > 0:
            myStr = "FUMBLE!!"
        else:
            myStr = "To Hit:"
        myStr += "[To Hit Roll, Modifiers, Honor]" + " [" + str(self.data[0])
        for a in self.data[1:]:
            myStr += ","
            myStr += str(a)
        myStr += "] = (" + str(self.sum()) + ")"
        return myStr

class HMhelp(std):
    def __init__(self,source=[]):
        std.__init__(self,source)
        self.source = source

    def __str__(self):
        myStr = " <br /> .attack(Bonus, Honor): <br />"
        myStr += " The attack roll rolles the dice and adds your bonus <br />"
        myStr += " and honor modifier and returns you final roll. <br />"
        myStr += " On a natural 20 the dieroller displays Critical Hit!! <br />"
        myStr += " On a natural 1 the dieroller displays FUMBLE!! <br />"
        myStr += " Example A 1st level fighter with +1 to hit and a +2 sword and High Honor <br />"
        myStr += " would roll [1d20.attack(3,1)] <br />"
        myStr += " .damage(Bonus, Honor): <br />"
        myStr += " The damage roll rolls the dice and rerolls on a max roll for <br />"
        myStr += " penetration damage, the penetration die is -1 and is rerolled on a max roll <br />"
        myStr += " The roller returns the damage dice, monidifiers, and honor <br />"
        myStr += " Example A magic-user uses a quaterstaff +1 with high honor, he would roll <br />"
        myStr += " [1d6.damage(1,1)] <br />"
        myStr += " .severity(honor): <br />"
        myStr += " the severity is for critical hit resolution - the character rolls <br />"
        myStr += " a d8 and adds honor bonus. the die is rerolled on natural 8 and natural 1 with a -1 modifier <br />"
        myStr += " on an 8 the reroll is added on a 1 the reroll is subtracted <br />"
        myStr += " Example [1d8.severity(1)] <br />"
        myStr += " .help() : <br />"
        myStr += " displays this message <br />"
        return myStr

# the severity roll is for critical resolution. The die is rerolled and added
#on a natural 8 and rerolled and subtracted on a 1
class HMSeverity(std):
    def __init__(self, source =[], honor=0):
        std.__init__(self,source)
        self.source = source
        self.hon = honor
        self.data = []
        self.append(di(8))
        self.CheckReroll()
        self.append(static_di(self.hon))

    def __str__(self):
        myStr = "[Severity Dice, Honor]" + " [" + str(self.data[0])
        for a in self.data[1:]:
            myStr += ","
            myStr += str(a)
        myStr += "] = (" + str(self.sum()) + ")"
        return myStr

    def CheckReroll(self):
        if self.data[0] == self.data[0].sides:
            self.crit_chain(0,1)
        if self.data[0] == 1:
            self.crit_chain(0,-1)

    #this function needes moved for severity
    def crit_chain(self,num,neg):
        result = int(random.uniform(1,self.data[num].sides+1))
        self.data[num].value += (((result - 1) * neg) + self.hon)
        self.data[num].history.append(((result - 1) * neg) + self.hon)
        if result >= self.data[num].sides: self.crit_chain(num,1)
        if result == 1: self.crit_chain(num,-1)

