## A die roller as used by IronClaw RPG
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
# File: ironclaw.py
# Author: Prof. Ebral, TaS (Traipse)
# Maintainer:
# Version:
#   $Id: ironclaw.py,v Traipse 'Ornery-Orc' prof.ebral Exp $
#
# Description: IronClaw Die Roller
# Comissioned by Ponderer
#
"""
Notes: The original concept of the Iron Claw roller is too advanced for Ornery Orc so I am taking notes. The idea is a highly desired idea, a PC Sheet that
can interact with other PC Sheets to expedite die rolls. PC Sheet data will be shared via the map, expected to occur in Pious Paladin, because the map makes
a safe sand box for the game tree data.

The combat system in Iron Claw is not straight forward enough for compared rolls, so the out put orders the rolls from highest to lowest, coloring the highest
and the ones. When PC Sheet data can be shared in a safe format, the comparitive possibility already exists. After the makeDecision function the list of dice is returned also, allow for the two dice lists to be rolled and then compared.

By far the most intricate commission I have had so far. I really wish I could have accomplised all that was requested.
"""

from std import std
from math import fabs
import random
from orpg.dieroller.base import *
from orpg.tools.InterParse import Parse
""" For note
ret = ['(', num.strip(), "**die_rollers['", self.getRoller(), "'](",
        sides.strip(), '))']
s =  ''.join(ret)
"""
class ironclaw(std):
    name = "ironclaw"
    regGroup = '[a-zA-Z0-9. (::)(\-\+)]+'
    regExpression = regGroup+'/'+regGroup+'|'+regGroup
    pcSheets = {}
    healingTable = {
    1: ['1d4', '2d4', '2d6', '2d8'],
    2: ['1d6', '2d6', '2d8', '2d10'],
    3: ['1d8', '2d8', '2d10', '2d12'],
    4: ['1d10', '2d10', '2d12', '3d12'],
    5: ['1d12', '2d12', '3d12', '3d12'],
    6: ['2d12', '3d12', '3d12', '4d12'],
    7: ['2d12', '3d12', '4d12', '4d12'],
    8: ['3d12', '4d12', '4d12', '4d12'],
    9: ['3d12', '4d12', '5d12', '6d12']
                }
    acceptedDice = ['4', '6', '8', '10', '12']
    deathTable = {
    6: '1d4', 7: '1d6', 8: '1d8', 9: '1d10', 
    10: '1d12', 11: '2d12', 12: '3d12', 13: 'Dead'
                }
    unconTable = {
    3: '1d4', 4: '1d6', 5: '1d8', 6: '1d10', 7: '1d12', 
    8: '2d12', 9: '3d12', 10: '4d12', 11: '4d12', 12: '4d12'
                }
    conditions = {'easy': 0, 'medium': 1, 'hard': 2, 'extreme': 3}

    def __init__(self, source=[]):
        std.__init__(self, source)

    def non_stdDie(self, match):
        s = match.group(0)
        vsRoll = s.split('/'); pcSheets = []; PCs = []
        for roll in vsRoll:
            PCs.append(roll.split('.'))
        for pc in PCs:
            if pc[0].lower() == 'toolbox': return self.ToolBox(pc)
            else: pcSheets.append(self.findSheets(pc))
        #
        actor, aDice, adDice = self.makeDecision(PCs[0], pcSheets[0])
        myStr = actor; compareTest = None
        #
        if len(aDice) > 1: 
            myStr += ' ' +self.cleanDice(aDice)[0]+ ' => '
            attackRoll = self.rollDice(aDice)
            myStr += attackRoll[0]
            compareTest = self.compareTest(attackRoll[1], [1,1])
            if compareTest == 'botch': myStr += ' Botch!'
        if (isinstance(adDice, list)) and (compareTest != 'botch'):
            myStr += ' Damage: ' +self.cleanDice(adDice)[0]+ ' => '
            myStr += self.rollDamage(adDice)[0]
        if len(pcSheets) == 2:
            if pcSheets[1][0] == True: reactor, rDice, rdDice = self.makeDecision(PCs[1], pcSheets[1][1])
            else:
                diceList = ['None']
                for die in PCs[1]: 
                    trueDice = self.makeTrueDice(die)
                    for die in trueDice: diceList.append(die)
                diceList = self.buildActionList(diceList)
                rDice = self.diceModifiers(diceList)
                myStr += ' / ' +str(rDice)+ ' => '
                rDice.sort(); rDice.reverse()
                rDiceRolled = self.rollDice(rDice)[0]
                myStr += str(rDice)
        return myStr

    def ToolBox(self, commands):
        ## This is expandable. Aimed for GM use ##
        if commands[1].lower() == 'clearpcs': 
            for key in self.pcSheets.keys(): del self.pcSheets[key]
            return 'Clearing PC Sheets'

    def makeDecision(self, pcAction, pcSheetData):
        pcSheet = pcSheetData[1]
        if self.pcSheets.has_key(pcAction[0]): pcNode = pcSheet['Node']
        else: pcNode = pcSheetData[2]
        actionList = self.buildActionList(pcAction); skillList = self.buildSkillList(pcSheet['Skills'])
        ability = self.buildAbilities(pcSheet['Abilities']); nodeList = self.buildNodeList(pcSheet)
        myStr = '<b>'+self.NameSpaceXI('name', pcSheet['General']).text+ '</b> '
        diceList = []; options = ['parry', 'guard', 'retreat', 'nocover']
        toolbox = ['setpc', 'delpc', 'clearpcs', 'update']
        actions = ['denarii', 'aureals', 'fatigue', 'wounds', 'passout', 
                    'resolve', 'soak', 'rest', 'block', 'dodge', 'magic', 
                    'damage', 'meditate', 'initiative', 'strength']
        #others = ['cast'] ## For future dev
        #magicCareers = ['cleric', 'elementalist', 'thaumaturge', 'necromancer', 'green and purple mage']
        damage = None
        self.updatePC(pcSheet, skillList, ability['speed'], actionList)
        for action in actionList:
            action = action.lower(); actionNodes = action.split('::')
            if action in options: pass ## Pass over these.

            elif action in toolbox:
                if action == 'setpc': myStr += self.setPCSheet(pcSheetData[2], pcSheet, actionList)
                elif action == 'delpc': myStr += self.delPCSheet(pcAction[0])
                elif action == 'update': 
                    myStr += self.updatePC(pcSheet, skillList, ability['speed'], actionList)
                    while len(actionList) > 1: actionList.pop()

            elif action in actions:
                if action in ['denarii', 'aureals']:
                    myStr += self.setCoin(pcSheet['Purse'], action, actionList)
                elif action in ['fatigue', 'wounds']:
                    myStr += self.setWound(pcSheet['Character'], action, ability['body'], actionList)
                elif action == 'soak':
                    myStr += 'Soak: '
                    diceList += self.pcSoak(pcSheet['Defense'])
                elif action == 'strength':
                    myStr += 'Strength: '
                    diceList += self.pcStrength(pcSheet['Abilities'])
                elif action == 'initiative':
                    myStr += 'Initiative: '
                    diceList += self.pcInit(pcSheet['Defense'])
                elif action in ['block', 'dodge']: 
                    dice = self.dodgeBlock(action, ability, actionList, pcSheet['Defense'], pcSheet['Equipment'], skillList)
                    myStr += action.capitalize()+'s'
                    if dice != 'No Dice Found!': diceList += dice
                elif action == 'rest':
                    myStr += self.restPC(pcSheet['Character'], pcSheet['Skills'], ability['body'], action, actionList)
                elif action == 'meditate':
                    myStr += self.restPC(pcSheet['Character'], skillList, ability['body'], action, actionList)
                elif action == 'magic': myStr += self.pcMagic(pcSheet['Character'], actionList)
                elif action == 'damage': string, damage = self.pcDamage(actionList); myStr += string
                elif action == 'passout': myStr += self.passoutTest(pcSheet['Character'], pcSheet['Defense'], skillList, ability['will'])
                elif action == 'resolve':
                    myStr += 'Resolve: '
                    diceList += self.pcResolve(pcSheet['Character'], pcSheet['Defense'], skillList, ability['will'])

            elif nodeList.has_key(action):
                if ability.has_key(action): 
                    myStr += '<u>Ability; '+action.capitalize()+'</u> '
                    abilityDice = self.makeTrueDice( str(ability[action].find('text').text) )
                    for die in abilityDice: 
                        diceList.append(die)
                else:
                    string, dice, damage = self.getNodeValue(action, actionList, ability, nodeList, pcSheet, skillList, pcNode)
                    myStr += string+' '
                    if isinstance(dice, list): diceList += dice

            elif skillList.has_key(action):
                dice = self.getSkillDice(skillList[action])
                if dice != 'No Dice Found!': diceList += dice
                myStr += '<u>Skill; '+action.capitalize()+'</u> '

            elif nodeList.has_key(actionNodes[len(actionNodes)-1]):
                string, dice, damage = self.getNodeValue(action, actionList, ability, nodeList, pcSheet, skillList, pcNode)
                myStr += string+' '
                if isinstance(dice, list): diceList += dice

            else:
                trueDice = self.makeTrueDice(action)
                for die in trueDice: diceList.append(die)
        if len(actionList) > 1: diceList.append(actionList[len(actionList)-1])
        if len(diceList) > 1: diceList = self.diceModifiers(diceList)
        if damage != None: damage = self.diceModifiers(damage)
        return myStr, diceList, damage

    def pcMagic(self,  character, actionList):
        magic = int(actionList[len(actionList)-1])
        magicPoints = self.NameSpaceVI('magic points', character)
        cMagic = self.NameSpaceXI('current', magicPoints); cM = int(cMagic.text)
        mMagic = self.NameSpaceXI('maximum', magicPoints); mM = int(mMagic.text)
        myStr = 'Regains ' if magic >= 0 else 'Loses '
        if len(actionList) == 2:
            if magic < 0:
                if cM + magic < 0: return 'Insufficient Magic!'
            cM += magic
            if cM > mM: cM = mM
            myStr += str(magic)+ ' Magic.'
            cMagic.text = str(cM)
        else:
            diceList = []
            for x in xrange(1, len(actionList)): 
                trueDice = self.makeTrueDice(actionList[x])
                for die in trueDice:diceList.append(die)
            diceList.append(actionList[len(actionList)-1])
            diceList = self.diceModifiers(diceList)
            while len(actionList) > 1: actionList.pop()
            addMagic = self.rollDice(diceList); x = 0
            for m in addMagic[1]: x += int(m)
            cM += x
            if cM > mM: cM = mM
            cMagic.text = str(cM)
            return 'Regains ' +self.cleanDice(diceList)[0]+ ' => ' +addMagic[0]+ ' => [' +str(x)+ '] Magic.'
        return myStr

    def pcDamage(self, actionList):
        if len(actionList) == 2: return 'No Damage Dice', None
        diceList = []
        if 'd' in actionList[len(actionList)-1]: mod = '0'
        else: mod = int(actionList[len(actionList)-1])
        for x in xrange(1, len(actionList)-1):
            trueDice = self.makeTrueDice(actionList[x])
            for die in trueDice: diceList.append(die)
        diceList.append(mod)
        while len(actionList) > 1: actionList.pop()
        return '', diceList

    def pcStrength(self, abilities):
        strength = self.NameSpaceXI('strength dice', abilities)
        trueDice = self.makeTrueDice(str(strength.text))
        return trueDice

    def pcSoak(self, defense):
        soak = self.NameSpaceXI('soak', defense)
        trueDice = self.makeTrueDice(str(soak.text))
        return trueDice

    def pcInit(self, defense):
        init = self.NameSpaceXI('initiative', defense)
        trueDice = self.makeTrueDice(str(init.text))
        return trueDice

    def setCoin(self, purse, action, actionList):
        denarii = self.NameSpaceXI('denarii', purse); d = int(denarii.text)
        aureals = self.NameSpaceXI('aureals', purse); a = int(aureals.text)
        coins = int(actionList[len(actionList)-1])
        myStr = 'Gains ' if coins >= 0 else 'Loses '
        if action == 'denarii':
            d += coins
            while d >= 24:
                a += 1; d -= 24
            myStr += str(coins)+ ' Denarii'
        if d < 0: a -= 1; d += 24
        if action == 'aureals':  a += coins; myStr += str(coins)+ ' Aureals'
        if a < 0: return 'Not enough coins!'
        if d < 0: return 'Not enough coins!'
        aureals.text = str(a); denarii.text = str(d)
        return myStr

    def setWound(self, character, action, body, actionList):
        fatigue = self.NameSpaceXI('fatigue', character); f = int(fatigue.text)
        wounds = self.NameSpaceVI('wounds', character)
        cWounds = self.NameSpaceXI('current', wounds); cW = int(cWounds.text)
        mWounds = self.NameSpaceXI('maximum', wounds); mW = int(mWounds.text)
        total = self.NameSpaceXI('total', character); t = int(total.text)
        mod = int(actionList[len(actionList)-1])
        myStr = 'Suffers ' if mod >= 0 else 'Regains '
        if action == 'fatigue': 
            myStr += str(mod)+ ' Fatigue '; tie = False
            for x in range(0, mod):
                f += 1
                if f > t: 
                    f -= 1; cW += 1
                    if (cW >= mW-6) and not tie:
                        deathTest = self.deathTest(cW+(12-mW), body)
                        if deathTest[0] == 'Dead': tie = True; myStr += deathTest[1]
                        if deathTest[2] in ['failure', 'riposte', 'tie', 'botch']: tie = True; myStr += deathTest[1]
                        else: myStr += deathTest[1]
        if action == 'wounds':
            myStr += str(int(fabs(mod)))+ ' Wounds '; tie = False
            if mod > 0:
                for x in xrange(0, mod):
                    cW += 1
                    if (cW >= mW-6) and not tie:
                        deathTest = self.deathTest(cW+(12-mW), body)
                        if deathTest[0] == 'Dead': tie = True; myStr += deathTest[1]
                        if deathTest[2] in ['failure', 'riposte', 'tie', 'botch']: tie = True; myStr += deathTest[1]
                        else: myStr += deathTest[1]
            else: cW += mod
        if cW < 0: cW = 0
        if f < 0: f = 0
        t = f + cW; fatigue.text = str(f); cWounds.text = str(cW); total.text = str(t)
        if t > mW: myStr += 'You have fallen.'
        return myStr

    def restPC(self, character, skills, body, action, actionList):
        if 'd' in actionList[len(actionList)-1]: mod = 0
        else: mod = int(actionList[len(actionList)-1])

        if action == 'meditate':
            if not skills.has_key('meditate'):
                if not skills.has_key('meditation'):
                    while len(actionList) > 1: actionList.pop()
                    return 'No skill in Meditation.'
            magicPoints = self.NameSpaceVI('magic points', character)
            cMagic = self.NameSpaceXI('current', magicPoints); cM = int(cMagic.text)
            mMagic = self.NameSpaceXI('maximum', magicPoints); mM = int(mMagic.text)
            vsDice = self.getSkillDice(skills['meditate'], [3,8]) if skills.has_key('meditate') else self.getSkillDice(skills['meditation'], [3,8])
            vsDice += vsDice
            skDice = self.getSkillDice(skills['meditate'], [3,4,5,6,7]) if skills.has_key('meditate') else self.getSkillDice(skills['meditation'], [3,4,5,6,7])
            if skDice != 'No Dice Found!': vsDice += skDice
            myStr = 'Meditates, '
            condition = 'easy'
            vsCondition = []
            for x in xrange(1, len(actionList)): 
                trueDice = self.makeTrueDice(actionList[x])
                for die in trueDice: vsCondition.append(die)
            if len(vsCondition) == 0: return 'No Difficulty Set.'
            magicGained = 0; result = 'success' # Begins loop
            while result in ['success', 'overwhelm']:
                vsRoll = self.rollDice(vsDice); conRoll = self.rollDice(vsCondition)
                if result == 'success': myStr += 'Meditate Skill: ' +self.cleanDice(vsDice)[0]+ ' => ' +vsRoll[0]
                if result == 'overwhelm':  myStr += ' Rolling Again: ' +self.cleanDice(vsDice)[0]+ ' => ' +vsRoll[0]
                myStr += ' vs. '+self.cleanDice(vsCondition)[0]+ ' => ' +conRoll[0]
                result = self.compareTest(vsRoll[1], conRoll[1])
                if result == 'riposte': myStr += ' Overwhelming failure'
                else: myStr += ' '+result.capitalize()
                if result == 'success':
                    magicGained += 1
                    break
                if result == 'overwhelm':
                    magicGained += 2
            if magicGained > 0: 
                myStr += ' Regains '+str(magicGained)+' magic.'
                cM += magicGained
            if cM > mM: cM = mM
            cMagic.text = str(cM)
            while len(actionList) > 1: actionList.pop()

        if action == 'rest':
            fatigue = self.NameSpaceXI('fatigue', character); f = int(fatigue.text)
            wounds = self.NameSpaceVI('wounds', character)
            cWounds = self.NameSpaceXI('current', wounds); cW = int(cWounds.text)
            mWounds = self.NameSpaceXI('maximum', wounds); mW = int(mWounds.text)
            total = self.NameSpaceXI('total', character); t = int(total.text)
            myStr = 'Rests ' +str(mod)+ ' hours. '
            f -= mod
            if f < 0: f = 0
            if mod >= 8: 
                myStr += '<b>Roll Magic Dice</b>'
                if cW > 0:
                    vsDice = body.find('text').text
                    vsDice = self.makeTrueDice(vsDice)
                    c = 9 if cW > 9 else cW
                    condition = 'easy' if not self.conditions.has_key(actionList[1]) else actionList[1]
                    vsCondition = self.healingTable[c][self.conditions[condition]]
                    vsCondition = self.makeTrueDice(vsCondition)
                    vsRoll = self.rollDice(vsDice); conRoll = self.rollDice(vsCondition)
                    myStr += ', Roll Wounds; Body: ' +self.cleanDice(vsDice)[0]+ ' => ' +vsRoll[0]
                    myStr += ' vs. Condition ('+condition.capitalize()+'): '+self.cleanDice(vsCondition)[0]+ ' => ' +conRoll[0]
                    result = self.compareTest(vsRoll[1], conRoll[1])
                    if result == 'riposte': myStr += ' Overwhelming failure'
                    else: myStr += ' '+result.capitalize()
                    if result in ['success', 'overwhelm']: cW -= 1
                    if result == 'botch':
                        cW += 1
                        deathTest = self.deathTest(cW, body)
                        if deathTest[0] == 'Dead': return deathTest[1]
                        else: myStr += deathTest[1]
            if cW < 0: cW = 0
            if f < 0: f = 0
            if t > mW: myStr += 'You have fallen.'
            t = f + cW; fatigue.text = str(f); cWounds.text = str(cW); total.text = str(t)
        return myStr

    def dodgeBlock(self, action, ability, actionList, defense, equipment, skillList):
        optionals = ['guard', 'retreat']
        blockDice = self.getSkillDice(skillList[action]) if action in skillList.keys() else []
        speed = self.makeTrueDice( str(ability['speed'].find('text').text) )
        for s in speed: blockDice.append(s)
        defendSkill = self.NameSpaceXI(action, defense)
        defendSkill.text = ', '.join(blockDice)
        if 'nocover' not in actionList:
            cover = self.NameSpaceXI('cover', defense)
            cover = self.makeTrueDice(str(cover.text))
            for c in cover: blockDice.append(c)
        if 'retreat' in actionList: blockDice.append('1d8')
        if action == 'dodge':
            encumber = self.NameSpaceXI('encumbrance', equipment)
            try:
                encumber = float(encumber.text)
                if encumber < -1:
                    encumber = int(encumber)
                    blockDice = self.encumberDice(blockDice, encumber, speed)
            except: pass
        if 'guard' in actionList: blockDice.append('+2')
        return blockDice

    def pcResolve(self, character, defense, skillList, abilityWill):
        total = self.NameSpaceXI('total', character); t = int(total.text)
        resolveDice = self.getSkillDice(skillList['resolve']) if 'resolve' in skillList.keys() else []
        will = self.makeTrueDice( abilityWill.find('text').text )
        for w in will: resolveDice.append(w)
        resolveDice = self.cleanDice(resolveDice)[1]
        defendSkill = self.NameSpaceXI('resolve', defense)
        defendSkill.text = ', '.join(resolveDice)
        return resolveDice


    ### Data Functions ###
    def getSkillDice(self, skill, skip=[0]):
        dice = []; cells = skill.findall('cell')
        for x in xrange(3, 9):
            if (cells[x].text != '') or (cells[x].text != None):
                if x in skip: pass
                else:
                    skillDice = self.makeTrueDice(str(cells[x].text))
                    for s in skillDice: dice.append(s)
        if len(dice) == 0: return 'No Dice Found!'
        else: return dice

    def buildAbilities(self, pcSheet):
        nodes = pcSheet.getiterator('nodehandler')
        ability = {}
        for node in nodes:
            if node.get('name') == 'Body': ability['body'] = node
            if node.get('name') == 'Speed': ability['speed'] = node
            if node.get('name') == 'Mind': ability['mind'] = node
            if node.get('name') == 'Will': ability['will'] = node
        return ability

    def buildActionList(self, actions):
        actionLength = len(actions); actionList = []
        for x in xrange(1, actionLength):
            if x == actionLength-1: 
                getMod = self.getMod(actions[x])
                for action in getMod[0]: actionList.append(str(action))
                actionList.append(str(getMod[1]))
            else:
                for action in self.getMod(actions[x])[0]: actionList.append(str(action))
        return actionList

    def buildSkillList(self, skills):
        grid = skills.find('grid')
        listRows = []
        for row in grid.findall('row'):
            listRows.append(row)
        skillList = {}
        for x in xrange(1, len(listRows)):
            if listRows[x].findall('cell')[0].text != None: 
                skillList[listRows[x].findall('cell')[0].text.lower()] = listRows[x]
        return skillList

    def buildNodeList(self, pcSheet):
        nodeList = {}
        for key in pcSheet.keys():
            nodes = pcSheet[key].getiterator('nodehandler')
            for node in nodes:
                nodeList[node.get('name').lower()] = node
        return nodeList


    ### Test Functions ###
    def deathTest(self, cW, body):
        vsDice = body.find('text').text
        vsDice = self.makeTrueDice(vsDice)
        vsCondition = self.deathCheck(cW)
        if vsCondition != []:
            if vsCondition[0] == 'Dead': myStr = ' You have fallen.'; return [vsCondition[0], myStr, None]
            vsRoll = self.rollDice(vsDice); conRoll = self.rollDice(vsCondition)
            myStr = '<br />Death Check: '+self.cleanDice(vsDice)[0]+ ' => ' +vsRoll[0]
            myStr += ' vs. Death: '+self.cleanDice(vsCondition)[0]+ ' => ' +conRoll[0]
            result = self.compareTest(vsRoll[1], conRoll[1])
            if result == 'riposte': myStr += ' Overwhelming failure'
            else: myStr += ' '+result.capitalize()
            if result in ['botch', 'failure', 'riposte']:  myStr += ' You have fallen.'
            else: myStr += ' You have survived.'
        return [vsCondition[0], myStr, result]

    def passoutTest(self, character, defense, skillList, abilityWill):
        #mod = int(actionList[len(actionList)-1]) or 0
        total = self.NameSpaceXI('total', character); t = int(total.text)
        vsDice = self.getSkillDice(skillList['resolve']) if 'resolve' in skillList.keys() else []
        will = self.makeTrueDice( abilityWill.find('text').text )
        for w in will: vsDice.append(w)
        vsDice = self.cleanDice(vsDice)[1]
        defendSkill = self.NameSpaceXI('resolve', defense)
        defendSkill.text = ', '.join(vsDice)
        vsCondition = self.unconCheck(t)
        myStr = ''
        if vsCondition != []:
            vsRoll = self.rollDice(vsDice); conRoll = self.rollDice(vsCondition)
            myStr += 'Unconciousness Check: '+self.cleanDice(vsDice)[0]+ ' => ' +vsRoll[0]
            myStr += ' vs. '+self.cleanDice(vsCondition)[0]+ ' => ' +conRoll[0]
            result = self.compareTest(vsRoll[1], conRoll[1])
            if result == 'riposte': myStr += ' Overwhelming failure'
            else: myStr += ' '+result.capitalize()
            if result in ['botch', 'failure', 'riposte']:  myStr += ' You have passed out.'
            else: myStr += ' You have survived.'
        else: myStr += 'No Unconciousness Check Required!'
        return myStr

    def unconCheck(self, fatigue):
        dieList = []
        if fatigue > 12: fatigue = 12
        if self.unconTable.has_key(fatigue):
            dieList.append(self.unconTable[fatigue])
        return dieList

    def deathCheck(self, wounds):
        dieList = []
        if wounds > 13: wounds = 13
        if self.deathTable.has_key(wounds):
            dieList.append(self.deathTable[wounds])
        return dieList

    def compareTest(self, dice1, dice2):
        ## Do Botch, Tie, Overwhelming.
        botch = 0
        for x in xrange(0, len(dice1)):
            if dice1[x] == 1: botch += 1
        if botch == len(dice1): return 'botch'
        botch = 0
        for x in xrange(0, len(dice2)):
            if dice2[x] == 1: botch += 1
        if botch == len(dice2): 
            if dice1[0] > dice2[0]:
                if int(dice1[0]) - int(dice2[0]) >= 5: return 'overwhelm'
                else: return 'success' #result2 = 'botch'
        #
        if dice1[0] == dice2[0]: return 'tie'
        #
        if dice1[0] > dice2[0]:
            if int(dice1[0]) - int(dice2[0]) >= 5: return 'overwhelm'
            else: return 'success'
        elif dice2[0] >= dice1[0]: 
            if int(dice2[0]) - int(dice1[0]) >= 5: return 'riposte'
            else: return 'failure'

    def compareDamage(self, dice1, dice2):
        # Works like this. [6, 4, 3] vs [5, 5, 2] == 2 Wounds.
        # [7, 3, 3] vs [6, 3, 3] == 1 Wounds. Ties go to the defender, 1's are not counted.
        ## Added for future dev.
        pass


    ### Node Functions ###
    def NameSpaceXI(self, s, node):
        nodeList = node.getiterator('nodehandler')
        for node in nodeList:
            if node.get('name').lower() == s: return node.find('text')
        return ''

    def NameSpaceVI(self, s, node): ## Sometimes I just need the node. I don't like the name though.
        nodeList = node.getiterator('nodehandler')
        for node in nodeList:
            if node.get('name').lower() == s: return node
        return ''

    def getNodeValue(self, action, actionList, ability, nodeList, pcSheet, skillList, pcNode):
        nodePath = actionList[0]
        weapons = pcSheet['Combat'].getiterator('nodehandler')
        optionals = ['parry', 'guard', 'retreat']
        damage = None
        if nodeList.has_key(action) and nodeList[action] in weapons:
            toHit = []; damage = []
            speed = self.makeTrueDice( str(ability['speed'].find('text').text) )
            for s in speed: toHit.append(s)
            grid = nodeList[action].find('grid')

            if actionList[1] == 'damage':
                for row in grid.findall('row'):
                    cells = row.findall('cell')
                    if cells[0].text == 'Damage':
                        trueDice = self.makeTrueDice(cells[1].text)
                        for die in trueDice: damage.append(die)
                        damage.append(actionList[len(actionList)-1])
                    if cells[0].text == 'Name':
                        weaponName = str(cells[1].text)
                while len(actionList) > 1: actionList.pop()
                return weaponName, action, damage

            string = 'Attacks!'
            for row in grid.findall('row'):
                cells = row.findall('cell')
                if cells[0].text == 'Skill': 
                    weaponSkill = str(cells[1].text).lower()
                    skillDice = self.getSkillDice(skillList[weaponSkill]) if weaponSkill in skillList.keys() else None
                    if isinstance(skillDice, list): toHit += skillDice
                if cells[0].text == 'Damage':
                    trueDice = self.makeTrueDice(cells[1].text)
                    for die in trueDice: damage.append(die)
                    #damage.append(actionList[len(actionList)-1])
            if 'parry' in actionList:
                damage = None
                string = 'Defends'
                if 'retreat' in actionList: toHit.append('1d8')
                if 'guard' in actionList: toHit.append(str(int(actionList[len(actionList)-1])+2))
            return string, toHit, damage
        return Parse.NameSpaceE('!&'+pcNode.get('name')+'::'+nodePath+'&!'), action, damage


    ### pcSheet Functions ###
    def findSheets(self, initiate):
        if self.pcSheets.has_key(initiate[0]): return True, self.pcSheets[initiate[0]]
        pcSheet = Parse.NameSpaceXE('!&'+initiate[0]+'&!')
        if pcSheet == None: return [False, [initiate[0]], None]
        else: return [True, self.buildPCSheet(pcSheet), pcSheet]
        return [False, [initiate[0]], None]

    def buildPCSheet(self, PC):
        pcSheet = {}
        nodes = PC.getiterator('nodehandler')
        for node in nodes:
            if node.get('name') == 'Character': pcSheet['Character'] = node
            if node.get('name') == 'Skills': 
                if node.get('class') == 'rpg_grid_handler': pcSheet['Skills'] = node
            if node.get('name') == 'General': pcSheet['General'] = node
            if node.get('name') == 'Abilities': pcSheet['Abilities'] = node
            if node.get('name') == 'Gifts / Flaws': pcSheet['Gifts / Flaws'] = node
            if node.get('name') == 'Combat': pcSheet['Combat'] = node
            if node.get('name') == 'Defense': pcSheet['Defense'] = node
            if node.get('name') == 'Equipment': pcSheet['Equipment'] = node
            if node.get('name') == 'Purse': pcSheet['Purse'] = node
        #print 'pcSheet', len(pcSheet)
        return pcSheet

    def setPCSheet(self, pcNode, pcSheet, actionList):
        if len(actionList) < 2: return 'Cannot setPC'
        while actionList[0].lower() != 'setpc': actionList.pop()
        self.pcSheets[actionList[1]] = pcSheet
        self.pcSheets[actionList[1]]['Node'] = pcNode
        return 'PC Sheet set to '+ actionList[1]

    def delPCSheet(self, pcSheet):
        del self.pcSheets[pcSheet]
        return 'PC Sheet '+pcSheet+' deleted.'

    def updatePC(self, pcSheet, skillList, abilitySpeed, actionList):
        denarii = self.NameSpaceXI('denarii', pcSheet['Purse']); d = int(denarii.text)
        aureals = self.NameSpaceXI('aureals', pcSheet['Purse']); a = int(aureals.text)
        while d >= 24: a += 1; d -= 24
        aureals.text = str(a); denarii.text = str(d)
        #
        blockDice = self.getSkillDice(skillList['dodge']) if 'dodge' in skillList.keys() else []
        speed = self.makeTrueDice( abilitySpeed.find('text').text )
        for s in speed: blockDice.append(s)
        blockDice = self.cleanDice(blockDice)[1]
        defendSkill = self.NameSpaceXI('dodge', pcSheet['Defense'])
        defendSkill.text = ', '.join(blockDice)
        #
        blockDice = self.getSkillDice(skillList['block']) if 'block' in skillList.keys() else []
        for s in speed: blockDice.append(s)
        blockDice = self.cleanDice(blockDice)[1]
        defendSkill = self.NameSpaceXI('block', pcSheet['Defense'])
        defendSkill.text = ', '.join(blockDice)
        #
        fatigue = self.NameSpaceXI('fatigue', pcSheet['Character']); f = int(fatigue.text)
        wounds = self.NameSpaceVI('wounds', pcSheet['Character'])
        cWounds = self.NameSpaceXI('current', wounds); cW = int(cWounds.text)
        mWounds = self.NameSpaceXI('maximum', wounds); mW = int(mWounds.text)
        total = self.NameSpaceXI('total', pcSheet['Character']); t = int(total.text)
        t = f + cW; fatigue.text = str(f); cWounds.text = str(cW); total.text = str(t)
        return 'Updated.'


    ### Math Functions ###
    def getMod(self, action):
        action = action.split('+')
        mod = '+'+str(action[1]) if len(action) == 2 else '0'
        action = action[0]
        if mod == '0':
            action = action.split('-')
            mod = '-'+str(action[1]) if len(action) == 2 else '0'
            action = action[0]
        action = [action]
        return [action, mod]

    def encumberDice(self, diceList, encumber, speed):
        encumber += 1; speedCap = 12+encumber*2
        for x in xrange(0, len(diceList)):
            diceCheck = diceList[x].split('d')
            try: rolls = int(diceCheck[0])
            except: continue
            try: facets = int(diceCheck[1])
            except: continue
            if facets > speedCap: facets = speedCap
            diceList[x] = str(rolls)+'d'+str(facets)
        return diceList

    def diceModifiers(self, diceList):
        diceList.sort(); diceList.reverse()
        dice = [0, 0, 0, 0, 0]
        getMod = True; mod = 0
        for dieMod in diceList:
            try:  mod += int(dieMod); del diceList[diceList.index(dieMod)]
            except: pass
        if mod <= 0:
            diceList.append(str(mod))
            return diceList
        for die in diceList: 
            d = die.split('d')
            if die == mod: pass
            elif d[1] == '4': dice[0] += int(d[0])
            elif d[1] == '6': dice[1] += int(d[0])
            elif d[1] == '8': dice[2] += int(d[0])
            elif d[1] == '10': dice[3] += int(d[0])
            elif d[1] == '12': dice[4] += int(d[0])
        diceMod = [0, 0, 0, 0, 0, 0]
        for i in xrange(0, len(dice)):
            dMod = (mod-(4-i))*dice[i]
            if dMod < 0: dMod = 0
            if i == 4: diceMod[5] += mod*dice[i]; diceMod[4] += dice[i]
            elif i+mod >= 5: diceMod[5] += dMod; diceMod[4] += dice[i]
            else: diceMod[i+mod] = dice[i]
        while diceMod[5] > 0:
            self.applyMod(diceMod)
        diceMod.pop(); dice = diceMod
        diceList = []
        if dice[0] != 0: diceList.append(str(dice[0])+'d4')
        if dice[1] != 0: diceList.append(str(dice[1])+'d6')
        if dice[2] != 0: diceList.append(str(dice[2])+'d8')
        if dice[3] != 0: diceList.append(str(dice[3])+'d10')
        if dice[4] != 0: diceList.append(str(dice[4])+'d12')
        diceList.append(str(mod))
        return diceList

    def applyMod(self, diceMod):
        for i in xrange(0, 5):
            while diceMod[i] > 0:
                if diceMod[5] == 0: break
                diceMod[5] -= 1
                if i == 4: diceMod[0] += 1; break
                else: diceMod[i+1] += 1; diceMod[i] -= 1


    ### Dice Functions ###
    def makeTrueDice(self, dieSet):
        dice = dieSet.split(',')
        dieSet = []
        for die in dice:
            if 'd' not in die: die = None
            else:
                die = die.replace(' ', '')
                die = die.split('d')
                try: 
                    int(die[1])
                    if die[0] == '': 
                        if die[1] in self.acceptedDice: die = '1d'.join(die)
                    else: die = 'd'.join(die)
                except: die = None
            if die != None: dieSet.append(die)
        return dieSet

    def cleanDice(self, diceList):
        dice = [0, 0, 0, 0, 0]
        if 'd' in diceList[len(diceList)-1]: mod = '0'
        else: mod = diceList[len(diceList)-1]
        for die in diceList: 
            d = die.split('d')
            if die == mod: pass
            elif d[1] == '4': dice[0] += int(d[0])
            elif d[1] == '6': dice[1] += int(d[0])
            elif d[1] == '8': dice[2] += int(d[0])
            elif d[1] == '10': dice[3] += int(d[0])
            elif d[1] == '12': dice[4] += int(d[0])
        diceList = []
        if dice[0] != 0: diceList.append(str(dice[0])+'d4')
        if dice[1] != 0: diceList.append(str(dice[1])+'d6')
        if dice[2] != 0: diceList.append(str(dice[2])+'d8')
        if dice[3] != 0: diceList.append(str(dice[3])+'d10')
        if dice[4] != 0: diceList.append(str(dice[4])+'d12')
        cleanList = '['
        for die in diceList:
            cleanList += die+', '
        cleanList += mod+']'
        return [cleanList, diceList]

    def rollDamage(self, diceList):
        if 'd' in diceList[len(diceList)-1]: mod = 0; diceList.append('0')
        else: mod = int(diceList[len(diceList)-1])
        removeDice = []
        diceRolls = []
        for x in xrange(0, len(diceList)-1):
            dice, facets = diceList[x].split('d')
            rolls = self.roll(int(dice), int(facets))
            for roll in rolls: diceRolls.append(roll)
        diceRolls.sort(); diceRolls.reverse()
        myStr = '['
        if mod < 0:
            for x in xrange(0, int(fabs(mod))): removeDice.append(len(diceRolls)-x-1)
        if len(diceRolls) > 1:
            if 0 in removeDice: myStr += '<font color=blue>'+str(diceRolls[0])+'</font>, '
            else: myStr += '<font color=red>'+str(diceRolls[0])+'</font>, '
            for x in xrange(1, len(diceRolls)-1):
                if x in removeDice: myStr += '<font color=blue>'+str(diceRolls[x])+'</font>, '
                else: myStr += str(diceRolls[x])+', '
            myStr += '<font color=blue>'+str(diceRolls[len(diceRolls)-1])+'</font>, '+str(mod)+'] '
        else: 
            if 0 in removeDice: myStr += '<font color=blue>'+str(diceRolls[0])+'</font>, '+str(mod)+'] '
            else: myStr += '<font color=red>'+str(diceRolls[0])+'</font>, '+str(mod)+'] '
        diceRolls.append(mod)
        return [myStr, diceRolls]

    def rollDice(self, diceList):
        if 'd' in diceList[len(diceList)-1]: mod = 0; diceList.append('0')
        else: mod = int(diceList[len(diceList)-1])
        if mod < 0: rerolls = mod
        else: rerolls = 0
        rollSets = []; myStr = ''; result = [100]
        while rerolls <= 0:
            diceRolls = []
            for x in xrange(0, len(diceList)-1):
                dice, facets = diceList[x].split('d')
                rolls = self.roll(int(dice), int(facets))
                for roll in rolls: diceRolls.append(roll)
            diceRolls.sort(); diceRolls.reverse()
            rollSets.append(diceRolls); rerolls += 1
        for diceRolls in rollSets:
            if result[0] < diceRolls[0]: pass
            else: result = diceRolls
            myStr += '['
            if len(diceRolls) > 1:
                myStr += '<font color=red>'+str(diceRolls[0])+'</font>, '
                for x in xrange(1, len(diceRolls)-1): myStr += str(diceRolls[x])+', '
                myStr += '<font color=blue>'+str(diceRolls[len(diceRolls)-1])+'</font>] '
            else:  myStr += '<font color=red>'+str(diceRolls[0])+'</font>] '
        myStr += 'Result: <font color=red>'+str(result[0])+'</font> '
        return [myStr, result]

    def roll(self, dice, facets):
        rolls = []
        for x in range(0, dice): rolls.append(int(random.uniform(1, facets+1)))
        return rolls

    def stdDie_Class(self, s): ## Not used
        num_sides = s.split('d')
        if len(num_sides) > 1: 
            num = num_sides[0]; sides = num_sides[1]
            if sides.strip().upper() == 'F': sides = "'f'"
            try:
                if int(num) > 100 or int(sides) > 10000: return None
            except: pass
            ret = ['(q', num.strip(), "**die_rollers['std'](", sides.strip(), '))']
            s =  ''.join(ret)
        return s

die_rollers.register(ironclaw)
