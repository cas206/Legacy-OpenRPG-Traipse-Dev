## a die roller as used by Warhammer Fantasy Roleplay Dice Roller
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
# File: wfrpg.py
# Author: Prof. Ebral, TaS (Traipse)
# Maintainer:
# Version:
#   $Id: wfrpg.py,v Traipse 'Ornery-Orc' prof.ebral Exp $
#
# Description: Warhammer Fantasy Roleplay Dice Roller die roller
# Comissioned by Puu-san
#

__version__ = "$Id: wfrpg.py,v Traipse 'Ornery-Orc' prof.ebral Exp $"

from std import std
import random
from orpg.dieroller.base import *

class wfrpg(std):
    name = "wfrpg"

    def __init__(self, source=[]):
        std.__init__(self, source)

    def non_stdDie(self, s):
        self.war_die = {'rec': self.reckless, 
                        'con': self.conservative, 
                        'chr': self.characteristic, 
                        'cha': self.challenge, 
                        'for': self.fortune, 
                        'mis': self.misfortune, 
                        'exp': self.expertise}
        for key in self.war_die.keys():
            dice = s.lower().split(key)
            if len(dice) > 1: 
                return self.war_die[key](int(dice[0]))

    def roll(self, dice, facets):
        for x in range(0,dice):
            self.rolls.append(int(random.uniform(1, facets+1)))

    def reckless(self, dice):
        self.rolls = []
        reck = {1: 'Bane', 2: 'Double Boon', 3: 'Boon & Success', 
                4: 'Double Success', 5: 'Success & Exertion', 6: 'Blank', 
                7: 'Bane', 8: 'Double Success', 9: 'Success & Exertion', 
                10: 'Blank'}
        self.roll(dice, 10)
        for roll in self.rolls:
            self.data.append(reck[roll])
        myStr = '[' + str(dice) + ' Reckless] = ('
        for data in self.data:
            myStr += data + ', '
        myStr = myStr[:len(myStr)-2] + ')'
        return myStr

    def conservative(self, dice):
        self.rolls = []
        reck = {1: 'Boon', 2: 'Success', 3: 'Success & Boon', 
                4: 'Success & Delay', 5: 'Blank', 6: 'Boon', 
                7: 'Success', 8: 'Success', 9: 'Success & Delay', 
                10: 'Success'}
        self.roll(dice, 10)
        for roll in self.rolls:
            self.data.append(reck[roll])
        myStr = '[' + str(dice) + ' Conservative] = ('
        for data in self.data:
            myStr += data + ', '
        myStr = myStr[:len(myStr)-2] + ')'
        return myStr

    def challenge(self, dice):
        self.rolls = []
        reck = {1: 'Challenge', 2: 'Double Challenge', 3: 'Bane', 
                4: 'Double Bane', 5: 'Chaos Star', 6: 'Blank', 
                7: 'Challenge', 8: 'Double Challenge'}
        self.roll(dice, 8)
        for roll in self.rolls:
            self.data.append(reck[roll])
        myStr = '[' + str(dice) + ' Challenge] = ('
        for data in self.data:
            myStr += data + ', '
        myStr = myStr[:len(myStr)-2] + ')'
        return myStr

    def characteristic(self, dice):
        self.rolls = []
        reck = {1: 'Boon', 2: 'Success', 3: 'Blank', 
                4: 'Boon', 5: 'Success', 6: 'Success', 
                7: 'Blank', 8: 'Success'}
        self.roll(dice, 8)
        for roll in self.rolls:
            self.data.append(reck[roll])
        myStr = '[' + str(dice) + ' Characterisitics] = ('
        for data in self.data:
            myStr += data + ', '
        myStr = myStr[:len(myStr)-2] + ')'
        return myStr

    def fortune(self, dice):
        self.rolls = []
        reck = {1: 'Success', 2: 'Blank', 3: 'Boon', 
                4: 'Blank', 5: 'Success', 6: 'Blank'}
        self.roll(dice, 6)
        for roll in self.rolls:
            self.data.append(reck[roll])
        myStr = '[' + str(dice) + ' Fortune] = ('
        for data in self.data:
            myStr += data + ', '
        myStr = myStr[:len(myStr)-2] + ')'
        return myStr

    def misfortune(self, dice):
        self.rolls = []
        reck = {1: 'Challenge', 2: 'Blank', 3: 'Bane', 
                4: 'Blank', 5: 'Challenge', 6: 'Blank'}
        self.roll(dice, 6)
        for roll in self.rolls:
            self.data.append(reck[roll])
        myStr = '[' + str(dice) + ' Misfortune] = ('
        for data in self.data:
            myStr += data + ', '
        myStr = myStr[:len(myStr)-2] + ')'
        return myStr

    def expertise(self, dice):
        self.rolls = []
        reck = {1: 'Boon', 2: 'Success', 3: 'Righteous Success', 
                4: 'Comet', 5: 'Blank', 6: 'Boon'}
        self.roll(dice, 6)
        for roll in self.rolls:
            self.data.append(reck[roll])
        myStr = '[' + str(dice) + ' Expertise] = ('
        for data in self.data:
            myStr += data + ', '
        myStr = myStr[:len(myStr)-2] + ')'
        return myStr


die_rollers.register(wfrpg)

