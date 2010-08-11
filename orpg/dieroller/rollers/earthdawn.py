## A die roller as used by Earthdawn RPG
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
# File: earthdawn.py
# Author: Prof. Ebral, TaS (Traipse)
# Maintainer:
# Version:
#   $Id: earthdawn.py,v Traipse 'Ornery-Orc' prof.ebral Exp $
#
# Description: Earthdawn Die Roller
# Comissioned by Jacob H.
#


from std import std
import random
from orpg.dieroller.base import *

class earthdawn(std):
    name = "earthdawn"
    regExpression = "[a-zA-Z]+([0-9]+/[0-9]+|[0-9]+)"

    def __init__(self, source=[]):
        std.__init__(self, source)
        self.successLevels = self.buildLevels()

    def non_stdDie(self, match):
        s = match.group(0)
        if s[:4] == 'step' or s[:1] == 's':
            dice = s.lower().split('step')
            rollType = 'Step'
            if len(dice) == 1: dice = s.lower().split('s')
            try: step, vs = dice[1].split('/')
            except: step, vs = dice[1], 0
            stepRoll = self.stepAlgorithm(step)
        elif s[:5] == 'karma' or s[:1] == 'k':
            dice = s.lower().split('karma')
            rollType = 'Karma'
            if len(dice) == 1: dice = s.lower().split('k')
            step, vs = dice[1], 0
            stepRoll = self.stepAlgorithm(step)
        elif s[:4] == 'test' or s[:1] == 't':
            dice = s.lower().split('test')
            rollType = 'Test'
            if len(dice) == 1: dice = s.lower().split('t')
            try: step, vs = dice[1].split('/')
            except: return
            return self.successTest(step, vs)
        return self.finalize(step, stepRoll, vs, rollType)

    def rollDice(self, dice, facets):
        rolls = []
        for x in range(0, dice):
            roll = self.roll(facets)
            while roll >= facets:
                rolls.append(roll)
                roll = self.roll(facets)
            rolls.append(roll)
        return rolls

    def roll(self, facets):
        return int(random.uniform(1, facets+1))

    def stepAlgorithm(self, stepRoll):
        if stepRoll == 0: return 0
        oneTothree = {'1': -3, '2': -2, '3': -1}
        if oneTothree.has_key(stepRoll): 
            dieList = self.rollDice(1, 6)
            dieList[0] += oneTothree[stepRoll]
            return dieList
        stepRoll = int(stepRoll)-3; self.dieList = []
        for step in xrange(0, stepRoll): self.stepIncrease()
        d6s = 0; d8s = 0; d10s = 0; d12s = 0
        dieList = []
        for die in self.dieList:
            if die == 6: d6s += 1 
            if die == 8: d8s += 1
            if die == 10: d10s += 1
            if die == 12: d12s += 1
        if d6s!= 0: d6s = self.rollDice(d6s, 6); dieList += d6s
        if d8s!= 0: d8s = self.rollDice(d8s, 8); dieList += d8s
        if d10s!= 0: d10s = self.rollDice(d10s, 10); dieList += d10s
        if d12s!= 0: d12s = self.rollDice(d12s, 12); dieList += d12s
        return dieList

    def stepIncrease(self):
        lowDie = 12
        if len(self.dieList) == 0: self.dieList.append(6); return
        for splitDie in self.dieList:
            if splitDie < lowDie: lowDie = splitDie
        if lowDie == 12: self.dieList[self.dieList.index(lowDie)] = 6; self.dieList.append(6); return
        else: self.dieList[self.dieList.index(lowDie)] += 2; return

    def successLevel(self, level, vs):
        index = 0
        successLevels = self.successLevels[int(vs)]
        for success in successLevels:
            if level > success: index = successLevels.index(success)+1
            elif level == success: index = successLevels.index(success)
        if index == 0: return 'Pathetic'
        if index == 1: return 'Poor'
        if index == 2: return 'Average'
        if index == 3: return 'Good'
        if index == 4: return 'Excellent'
        if index >= 5: return 'Extraordinary'

    def successTest(self, stepTotal, vs):
        myStr = '<b>Success Test: </b> ' +stepTotal+ ' vs. ' +vs
        successLevel = self.successLevel(int(stepTotal), int(vs))
        myStr += '= ' +successLevel
        return myStr

    def finalize(self, step, stepRoll, vs, rollType):
        myStr = '<b>' +rollType+' Roll: </b>' +step
        if vs != 0: myStr += ' vs. ' +vs
        myStr += ' => ' +str(stepRoll)+ ' (Total: '
        stepTotal = 0
        for step in stepRoll: stepTotal += step
        myStr += str(stepTotal)
        if vs != 0:
            myStr += ' vs. ' +str(vs)
            successLevel = self.successLevel(stepTotal, vs)
            myStr += ') ' +successLevel
        else: myStr += ')'
        return myStr

    def buildLevels(self):
        successLevels = {
        2: [0, 1, 4, 6, 8, 9], 3: [0, 2, 5, 7, 9, 10], 4: [0, 3, 6, 9, 11, 12], 
        5: [1, 4, 7, 10, 13, 14], 6: [1, 5, 8, 12, 16, 17], 7: [2, 6, 10, 14, 18, 19], 
        8: [3, 7, 12, 15, 19, 20], 9: [4, 8, 14, 17, 21, 22], 10: [5, 9, 15, 19, 22, 23], 
        11: [5, 10, 16, 20, 24, 25], 12: [6, 11, 17, 22, 26, 27], 13: [6, 12, 19, 24, 28, 29], 
        14: [7, 13, 20, 25, 30, 31], 15: [8, 14, 22, 26, 30, 31], 16: [9, 15, 23, 27, 32, 33], 
        17: [10, 16, 24, 29, 33, 34], 18: [11, 17, 25, 30, 35, 36], 19: [11, 18, 27, 32, 36, 37], 
        20: [12, 19, 28, 33, 38, 39], 21: [13, 20, 29, 35, 40, 41], 22: [14, 21, 30, 36, 41, 42], 
        23: [15, 22, 32, 37, 42, 43], 24: [15, 23, 33, 38, 43, 44], 25: [16, 24, 34, 40, 45, 46], 
        26: [17, 25, 35, 41, 46, 47], 27: [18, 26, 36, 42, 48, 49], 28: [18, 27, 38, 44, 49, 50], 
        29: [20, 28, 39, 45, 50, 51], 30: [20, 29, 40, 46, 52, 53], 31: [21, 30, 41, 47, 53, 54], 
        32: [22, 31, 42, 48, 54, 55], 33: [23, 32, 44, 50, 56, 57], 34: [23, 33, 45, 51, 57, 58], 
        35: [24, 34, 46, 52, 59, 60], 36: [25, 35, 47, 53, 59, 60], 37: [26, 36, 48, 55, 61, 62], 
        38: [27, 37, 50, 56, 62, 63], 39: [28, 38, 51, 57, 63, 64], 40: [29, 39, 52, 58, 65, 66], 
        41: [28, 40, 52, 60, 70, 71], 42: [29, 41, 53, 61, 71, 72], 43: [30, 42, 54, 63, 72, 73], 
        44: [31, 43, 55, 64, 74, 75], 45: [31, 44, 57, 66, 76, 77]
                        }
        return successLevels

die_rollers.register(earthdawn)

