#This program is free software; you can redistribute it and/or
#modify it under the terms of the GNU General Public License
#as published by the Free Software Foundation; either version 2
#of the License, or (at your option) any later version.
#
#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.
#
#You should have received a copy of the GNU General Public License
#along with this program; if not, write to the Free Software
#Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
# --
#
# File: gurps.py
# Version:
#   $Id: gurps.py,v 1.3
#
# Description: Modified Hero System die roller based on DJM and Heroman's Hero
# dieroller
#
# GURPS is a trademark of Steve Jackson Games, and its rules and art are
# copyrighted by Steve Jackson Games. All rights are reserved by Steve Jackson
# Games. This game aid is the original creation of Naryt with help from Pyrandon
# and is released for free distribution, and not for resale, under the
# permissions granted in the Steve Jackson Games Online Policy.
# http://www.sjgames.com/general/online_policy.html
#
# Errors should be reported to rpg@ormonds.net
#
# Changelog:
# V 1.3  2007/03/23  Thomas M. Edwards <tmedwards@motoslave.net>
#   Fixed gurpsskill, gurpsdefaultskill, and gurpssupernatural to correctly
#   return a normal failure when the roll is 17 and the effective skill is 27+;
#   previously, they would erroneously return a critical failure.  This fix also
#   corrects the less serious issue whereby rolls of 17 and an effective skill
#   of 17-26 would report "failure by X" instead of merely "failure", which is
#   wrong as the only reason the roll failed was because a 17 was rolled, not
#   because the roll exceeded the effective skill.
# V 1.2 29 October 2006, added defaultskill (Rule of 20 [B344]), supernatural
#   (Rule of 16 [B349]).  The frightcheck roll is now the actual Fright Check
#   (with Rule of 14 [B360]) and a lookup oon the Fright Check Table if needed.
#   The fightcheckfail roll is the old Fright Check Table lookup.
#   Removes the Help roller as it was nothing but trouble, see
#   http://openrpg.wrathof.com/repository/GURPS/GURPS_Roller_1.7.xml for help
#   in using this roller.
# V 1 Original gurps release 2006/05/28 00:00:00, modified crit_hit, crit_headblow, crit_miss, crit_unarm, spellfail, frightcheck and help_me
#       Corrects numerous descriptions
# v.1 original gurps release by Naryt 2005/10/17 16:34:00

from die import *
from time import time, clock
import random

__version__ = "$Id: gurps.py,v 1.5 2007/05/06 16:42:55 digitalxero Exp $"

# gurps

class gurps(std):
    def __init__(self,source=[]):
        std.__init__(self,source)

# these methods return new die objects for specific options

# Original msk roll renamed to be easier to understand/remember
    
    def skill(self,skill,mod):
        return gurpsskill(self,skill,mod)

    
    def defaultskill(self,stat,defaultlevel,mod):
        return gurpsdefaultskill(self,stat,defaultlevel,mod)

    
    def supernatural(self,skill,resistance,mod):
        return gurpssupernatural(self,skill,resistance,mod)

    
    def crit_hit(self):
        return gurpscrit_hit(self)

    
    def crit_headblow(self):
        return gurpscrit_headblow(self)

    
    def crit_miss(self):
        return gurpscrit_miss(self)

    
    def crit_unarm(self):
        return gurpscrit_unarm(self)

    
    def spellfail(self):
        return gurpsspellfail(self)

    
    def frightcheck(self,level,mod):
        return gurpsfrightcheck(self,level,mod)

    
    def frightcheckfail(self,mod):
        return gurpsfrightcheckfail(self,mod)

class gurpsskill(std):
    
    def __init__(self,source=[],skill=0,mod=0):
        std.__init__(self,source)
        self.skill = skill
        self.mod = mod

    
    def is_success(self):
        return (((self.sum()) <= self.skill+self.mod) and (self.sum() < 17))

    
    def __str__(self):
        myStr = "[" + str(self.data[0])
        for a in self.data[1:]:
            myStr += ","
            myStr += str(a)
        myStr +="]"
        myStr += " = <b>" + str(self.sum()) + "</b>"
        myStr += " vs <b>(" + str(self.skill+self.mod) + ")</b>"

        Diff = abs((self.skill+self.mod) - self.sum())

        if self.is_success():
            if self.sum() == 3 or self.sum() == 4:
                myStr += " or less <font color='#ff0000'><b>Critical Success!</b></font> [B556]"
            elif self.sum() == 5 and (self.skill+self.mod > 14):
                myStr += " or less <font color='#ff0000'><b>Critical Success!</b> by " + str(Diff) +" </font> [B556]"
            elif self.sum() == 6 and (self.skill+self.mod > 15):
                myStr += " or less <font color='#ff0000'><b>Critical Success!</b> by " + str(Diff) +" </font> [B556]"
            else:
                myStr += " or less <font color='#ff0000'><b>Success!</b> by " + str(Diff) +" </font>"
        else:
            if self.sum() == 18:
                myStr += " or less <font color='#ff0000'><b>Critical Failure!</b></font> [B556]"
#            elif self.sum() == 17 and (self.skill+self.mod < 16):
#                myStr += " or less <font color='#ff0000'><b>Critical Failure!</b></font> [B556]"
            elif self.sum() == 17:
                if (self.skill+self.mod) < 16:
                    myStr += " or less <font color='#ff0000'><b>Critical Failure!</b></font> [B556]"
                else:
                    myStr += " or less <font color='#ff0000'><b>Failure!</b></font> [B556]"
            elif  Diff > 9:
                myStr += " or less <font color='#ff0000'><b>Critical Failure!</b> by " + str(Diff) +" </font> [B556]"
            else:
                myStr += " or less <font color='#ff0000'><b>Failure!</b> by " + str(Diff) +" </font>"

        return myStr

class gurpsdefaultskill(std):
    
    def __init__(self,source=[],stat=0,defaultlevel=0,mod=0):
        std.__init__(self,source)
        self.stat = stat
        self.defaultlevel = defaultlevel
        self.mod = mod

    
    def is_success(self):
        if self.stat < 21:
            intSkillVal = self.stat + self.defaultlevel + self.mod
        else:
            intSkillVal = 20 + self.defaultlevel + self.mod
        return (((self.sum()) <= intSkillVal) and (self.sum() < 17))

    
    def __str__(self):
        myStr = "[" + str(self.data[0])
        for a in self.data[1:]:
            myStr += ","
            myStr += str(a)
        myStr +="]"
        myStr += " = <b>" + str(self.sum()) + "</b>"
        strRule = ""
        if self.stat < 21:
            intSkillVal = self.stat + self.defaultlevel + self.mod
        else:
            intSkillVal = 20 + self.defaultlevel + self.mod
            strRule = "<br />Rule of 20 in effect [B173, B344]"

        myStr += " vs <b>(" + str(intSkillVal) + ")</b>"

        Diff = abs((intSkillVal) - self.sum())

        if self.is_success():
            if self.sum() == 3 or self.sum() == 4:
                myStr += " or less <font color='#ff0000'><b>Critical Success!</b></font> [B556]"
            elif self.sum() == 5 and (intSkillVal > 14):
                myStr += " or less <font color='#ff0000'><b>Critical Success!</b> by " + str(Diff) +"</font> [B556]"
            elif self.sum() == 6 and (intSkillVal > 15):
                myStr += " or less <font color='#ff0000'><b>Critical Success!</b> by " + str(Diff) +"</font> [B556]"
            else:
                myStr += " or less <font color='#ff0000'><b>Success!</b> by " + str(Diff) +"</font>"
        else:
            if self.sum() == 18:
                myStr += " or less <font color='#ff0000'><b>Critical Failure!</b></font> [B556]"
            elif self.sum() == 17:
                if intSkillVal < 16:
                    myStr += " or less <font color='#ff0000'><b>Critical Failure!</b></font> [B556]"
                else:
                    myStr += " or less <font color='#ff0000'><b>Failure!</b></font> [B556]"
            elif  Diff > 9:
                myStr += " or less <font color='#ff0000'><b>Critical Failure!</b> by " + str(Diff) +"</font> [B556]"
            else:
                myStr += " or less <font color='#ff0000'><b>Failure!</b> by " + str(Diff) +"</font>"

        myStr += strRule
        return myStr

class gurpssupernatural(std):
    
    def __init__(self,source=[],skill=0,resistance=0,mod=0):
        std.__init__(self,source)
        self.skill = skill
        self.resistance = resistance
        self.mod = mod

    
    def is_success(self):
        if self.skill+self.mod > 16:
            if self.resistance > 16:
                if self.resistance > self.skill+self.mod:
                    newSkill = self.skill+self.mod
                else:
                    newSkill = self.resistance
            else:
                newSkill = 16
        else:
            newSkill = self.skill+self.mod
        return (((self.sum()) <= newSkill) and (self.sum() < 17))

    
    def __str__(self):
        myStr = "[" + str(self.data[0])
        for a in self.data[1:]:
            myStr += ","
            myStr += str(a)
        myStr +="]"
        myStr += " = <b>" + str(self.sum()) + "</b>"
        strRule = ""
        if self.skill+self.mod > 16:
            if self.resistance > 16:
                if self.resistance > self.skill+self.mod:
                    newSkill = self.skill+self.mod
                    strRule = "<br />Rule of 16:  Subject's Resistance is higher than skill, no change in skill [B349]"
                else:
                    newSkill = self.resistance
                    strRule = "<br />Rule of 16:  Effective skill limited by subject's Resistance [B349]"
            else:
                newSkill = 16
                strRule = "<br />Rule of 16:  Effective skill limited to 16 [B349]"
        else:
            newSkill = self.skill+self.mod
        myStr += " vs <b>(" + str(newSkill) + ")</b>"

        Diff = abs((newSkill) - self.sum())

        if self.is_success():
            if self.sum() == 3 or self.sum() == 4:
                myStr += " or less <font color='#ff0000'><b>Critical Success!</b></font> [B556]"
            elif self.sum() == 5 and (newSkill > 14):
                myStr += " or less <font color='#ff0000'><b>Critical Success!</b> by " + str(Diff) +" </font> [B556]"
            elif self.sum() == 6 and (newSkill > 15):
                myStr += " or less <font color='#ff0000'><b>Critical Success!</b> by " + str(Diff) +" </font> [B556]"
            else:
                myStr += " or less <font color='#ff0000'><b>Success!</b> by " + str(Diff) +" </font>"
        else:
            if self.sum() == 18:
                myStr += " or less <font color='#ff0000'><b>Critical Failure!</b></font> [B556]"
            elif self.sum() == 17:
                if newSkill < 16:
                    myStr += " or less <font color='#ff0000'><b>Critical Failure!</b></font> [B556]"
                else:
                    myStr += " or less <font color='#ff0000'><b>Failure!</b></font> [B556]"
            elif  Diff > 9:
                myStr += " or less <font color='#ff0000'><b>Critical Failure!</b> by " + str(Diff) +" </font> [B556]"
            else:
                myStr += " or less <font color='#ff0000'><b>Failure!</b> by " + str(Diff) +" </font>"

        myStr += strRule
        return myStr

class gurpscrit_hit(std):
    
    def __init__(self,source=[],mod=0):
        std.__init__(self,source)

    
    def __str__(self):
        myStr = "[" + str(self.data[0]) #Variable myStr holds text and first we put a [ into it and then adds the first die rolled
        for a in self.data[1:]:             #This is a for loop.  It will do the next two lines of code for every die (except the first die which we handled in the line above) in the roll.
            myStr += ","                  #Adds a comma after each die
            myStr += str(a)           #Adds the value of each die.
        myStr += "] = "                 #Adds ] = to the end of the string (note the += means append to whatever is already stored in the variable
        myStr += str(self.sum())          #Finally we add the actual result of the roll and myStr contains something like [3,2,1] = 6

        if self.sum() > 8 and self.sum() < 12:
            myStr += " <font color='#ff0000'>The blow inflicts normal damage.</font> [B556]"
        elif self.sum() == 12:
            myStr += " <font color='#ff0000'>The blow inflicts normal damage, AND victim drops anything they hold--even if no damage penetrates DR.</font> [B556]"
        elif self.sum() == 8:
            myStr += " <font color='#ff0000'>Damage penetrating DR does double shock (-8 max) AND if it hits the victim's limb, it's crippled for 16-HT seconds (unless wound is enough to cripple permanently!).</font> [B556]"
        elif self.sum() == 13 or self.sum() == 14 or self.sum() == 7:
            myStr += " <font color='#ff0000'>If any damage penetrates DR, treat as major wound. See [B420] for major wounds.</font> [B556]"
        elif self.sum() == 6 or self.sum() == 15:
            myStr += " <font color='#ff0000'>The blow inflicts maximum normal damage.</font> [B556]"
        elif self.sum() == 5 or self.sum() == 16:
            myStr += " <font color='#ff0000'>The blow inflicts double damage.</font> [B556]"
        elif self.sum() == 4 or self.sum() == 17:
            myStr += " <font color='#ff0000'>The victim's DR protects at half value, rounded down, after applying any armor divisors.</font> [B556]"
        elif self.sum() == 3 or self.sum() == 18 :
            myStr += " <font color='#ff0000'>The blow inflicts triple damage.</font> [B556]"

        return myStr

class gurpscrit_headblow(std):
        def __init__(self,source=[],mod=0):
        std.__init__(self,source)

    
    def __str__(self):
        myStr = "[" + str(self.data[0]) #Variable myStr holds text and first we put a [ into it and then adds the first die rolled
        for a in self.data[1:]:             #This is a for loop.  It will do the next two lines of code for every die (except the first die which we handled in the line above) in the roll.
            myStr += ","                  #Adds a comma after each die
            myStr += str(a)           #Adds the value of each die.
        myStr += "] = "                 #Adds ] = to the end of the string (note the += means append to whatever is already stored in the variable
        myStr += str(self.sum())          #Finally we add the actual result of the roll and myStr contains something like [3,2,1] = 6

        if self.sum() > 8 and self.sum() < 12:
            myStr += " <font color='#ff0000'>The blow inflicts normal damage.</font> [B556]"
        elif self.sum() == 12 or self.sum() == 13:
            myStr += " <font color='#ff0000'>Normal damage to the head, BUT if any penetrates DR victim is scarred (-1 to appearance, -2 if burning or corrosive attacks) OR, if <i>crushing</i> then victim deafened [see B422 for duration].</font> [B556]"
        elif self.sum() == 8:
            myStr += " <font color='#ff0000'>Normal damage to head, but victim knocked off balance: must Do Nothing until next turn (but can defend).</font> [B556]"
        elif self.sum() == 14:
            myStr += " <font color='#ff0000'>Normal damage to head, but victim drops their weapon.  If holding two weapons, roll randomly for which one is dropped.</font> [B556]"
        elif self.sum() == 6 or self.sum() == 7:
            myStr += " <font color='#ff0000'>If you aimed for face or skull, you hit an eye [B399];  otherwise, DR only half effective & if even 1 point damage penetrates it's a major wound [B420].  If you hit an eye and that should be impossible, treat as if a <b>4</b> were rolled, see [B556].</font> [B556]"
        elif self.sum() == 15:
            myStr += " <font color='#ff0000'>The blow inflicts maximum normal damage.</font> [B556]"
        elif self.sum() == 16:
            myStr += " <font color='#ff0000'>The blow inflicts double damage.</font> [B556]"
        elif self.sum() == 4 or self.sum() == 5:
            myStr += " <font color='#ff0000'>The victim's DR protects at half value, rounded up, after applying armor divisors AND if even 1 point penetrates it's a major wound [B420].</font> [B556]"
        elif self.sum() == 17:
            myStr += " <font color='#ff0000'>The victim's DR protects at half value, rounded up, after applying any armor divisors.</font> [B556]"
        elif self.sum() == 3:
            myStr += " <font color='#ff0000'>The blow inflicts maximum normal damage AND ignores all DR.</font> [B556]"
        elif self.sum() == 18:
            myStr += " <font color='#ff0000'>The blow inflicts triple damage.</font> [B556]"

        return myStr

class gurpscrit_miss(std):
    
    def __init__(self,source=[],mod=0):
        std.__init__(self,source)

    
    def __str__(self):
        myStr = "[" + str(self.data[0]) #Variable myStr holds text and first we put a [ into it and then adds the first die rolled
        for a in self.data[1:]:             #This is a for loop.  It will do the next two lines of code for every die (except the first die which we handled in the line above) in the roll.
            myStr += ","                  #Adds a comma after each die
            myStr += str(a)           #Adds the value of each die.
        myStr += "] = "                 #Adds ] = to the end of the string (note the += means append to whatever is already stored in the variable
        myStr += str(self.sum())          #Finally we add the actual result of the roll and myStr contains something like [3,2,1] = 6

        if self.sum() > 8 and self.sum() < 12:
            myStr += " <font color='#ff0000'>You drop your weapon (& a <i>cheap</i> weapon breaks).</font> [B556]"
        elif self.sum() == 12 or self.sum() == 8:
            myStr += " <font color='#ff0000'>Your weapon turns in your hand;  must Ready it before it can be used again.</font> [B556]"
        elif self.sum() == 13 or self.sum() == 7:
            myStr += " <font color='#ff0000'>You lose your balance & can do nothing else (not even free actions) until next turn;  all defenses -2 until next turn.</font> [B556]"
        elif self.sum() == 14:
            yrdStr = str(int(random.uniform(1,7)))
            myStr += " <font color='#ff0000'>A <i>swung</i> weapon flies from hand " + yrdStr + " yards (50% chance straight forward/backward) anyone on the target of the flying weapon makes a DX roll or takes half-damage; a <i>thrust</i> or <i>ranged</i> weapon is dropped (& a <i>cheap</i> weapon breaks).</font> [B556]"
        elif self.sum() == 6:
            myStr += " <font color='#ff0000'>You hit yourself in arm or leg (50/50 chance), doing half damage;  if impaling, piercing, or ranged attack, then roll again (if you hit yourself again then use that result).</font> [B556]"
        elif self.sum() == 15:
            myStr += " <font color='#ff0000'>You strain your shoulder!  Weapon arm crippled for 30 min;  do not drop weapon, but that arm is useless.</font> [B557]"
        elif self.sum() == 16:
            myStr += " <font color='#ff0000'>If <i>melee attack,</i>  you fall down!  If <i>ranged attack,</i> you lose your balance & can do nothing until next turn & all defenses -2 until next turn.</font> [B557]"
        elif self.sum() == 5:
            myStr += " <font color='#ff0000'>You hit yourself in the arm or leg (50/50 chance), doing normal damage;  if impaling, piercing, or ranged attack, then roll again (if you hit yourself again then use that result).</font> [B556]"
        elif self.sum() == 4 or self.sum() == 3 or self.sum() == 17 or self.sum() == 18:
            broke = int(random.uniform(3,19))
            if broke >=5 and broke <=16:
                brokestr = "it is dropped."
            else:
                brokestr = "the weapon also breaks!"
            myStr += " <font color='#ff0000'>A normal weapon breaks [B485];  if solid crushing weapon OR fine, very fine, or magical weapon " + brokestr + "</font> [B556] Note, second for roll non-normal weapons already fingured into this result."

        return myStr

class gurpscrit_unarm(std):
    
    def __init__(self,source=[],mod=0):
        std.__init__(self,source)

    
    def __str__(self):
        myStr = "[" + str(self.data[0]) #Variable myStr holds text and first we put a [ into it and then adds the first die rolled
        for a in self.data[1:]:             #This is a for loop.  It will do the next two lines of code for every die (except the first die which we handled in the line above) in the roll.
            myStr += ","                  #Adds a comma after each die
            myStr += str(a)           #Adds the value of each die.
        myStr += "] = "                 #Adds ] = to the end of the string (note the += means append to whatever is already stored in the variable
        myStr += str(self.sum())          #Finally we add the actual result of the roll and myStr contains something like [3,2,1] = 6

        if self.sum() > 8 and self.sum() < 12:
            myStr += " <font color='#ff0000'>You lose your balance;  you can do nothing else (not even free actions) until next turn, and all defenses -2 until next turn.</font> [B557]"
        elif self.sum() == 12:
            myStr += " <font color='#ff0000'>You trip; make a DX roll to avoid falling at -4 if kicking or twice the normal penatly for a technique that normally requires a DX to avoid injury on even a normal failure (e.g., Jump Kick).</font> [B557]"
        elif self.sum() == 8:
            myStr += " <font color='#ff0000'>You fall down!</font> [B557]"
        elif self.sum() == 13:
            myStr += " <font color='#ff0000'>You drop your guard:  all defenses -2 for the next turn & any Evaluate bonus or Feint penalties against you are doubled.  This is obvious to those around you.</font> [B557]"
        elif self.sum() == 7 or self.sum() == 14:
            myStr += " <font color='#ff0000'>You stumble:  <i>If attacking,</i> you advance one yard past opponent with them behind you (you are facing away); <i>if parrying</i> you fall down!</font> [B557]"
        elif self.sum() == 15:
            mslStr = str(int(random.uniform(1,4)))
            myStr += " <font color='#ff0000'>You tear a muscle; " + mslStr + " HT damage to the limb used to attack (to one limb if two used to attack), & -3 to use it (-1 w/high pain thresh); also all atacks & defenses -1 until next turn.  If neck was injured -3 (-1 w/high pain thresh) applies to ALL actions.</font> [B557]"
        elif self.sum() == 6:
            myStr += " <font color='#ff0000'>You hit a solid object (wall, floor, etc.) & take crushing damage equalt to 1/2 of (your thrusting damage - your DR) (<i>EXCEPTION:</i> If attacking with natural weapons, such as claws or teeth, they <i>break</i> -1 damage on future attacks until you heal (for recovery, B422).</font> [B557]"
        elif self.sum() == 5 or self.sum() == 16:
            myStr += " <font color='#ff0000'>You hit a solid object (wall, floor, etc.) & take crushing damage = your thrusting damage - your DR (<i>EXCEPTION:</i> if opponent using impaling weapon, you fall on it & take damage based on your ST).  If attacking an opponent who is using an impaling weapon, you fall on <i>his weapon</i>.  You suffer the weapon's normal damage based on <i>your</i> <b>ST</b>.</font> [B557]"
        elif self.sum() == 4:
            myStr += " <font color='#ff0000'>If attacking or parrying with a limb, you strain the limb:  1 HP damage & it's crippled for 30 min. If biting, butting, etc., have moderate neck pain (B428) for next 20-HT min minimum of 1 minute.</font> [B557]"
        elif self.sum() == 17:
            myStr += " <font color='#ff0000'>If attacking or parrying with a limb, you strain the limb:  1 HP damage & it's crippled for 30 min. If IQ 3-5 animal, it loses its nerve & flees on next turn or surrenders if cornered.</font> [B557]"
        elif self.sum() == 3 or self.sum() == 18 :
            myStr += " <font color='#ff0000'>You knock yourself out!  Roll vs. HT every 30 min. to recover.</font> [B557]"

        return myStr

class gurpsspellfail(std):
    
    def __init__(self,source=[],mod=0):
        std.__init__(self,source)

    
    def __str__(self):
        myStr = "[" + str(self.data[0])
        for a in self.data[1:]:
            myStr += ","
            myStr += str(a)
        myStr +="]"
        myStr += " = <b>" + str(self.sum()) + "</b>"

        if self.sum() == 10 or self.sum() == 11:
            myStr += " <font color='#ff0000'>Spell produces nothing but a loud noise, bright flash, awful odor, etc.</font> [B236]"
        elif self.sum() == 9:
            myStr += " <font color='#ff0000'>Spell fails entirely.  Caster is stunned (IQ roll to recover).</font> [B236]"
        elif self.sum() == 12:
            myStr += " <font color='#ff0000'>Spell produces a weak and useless shadow of the intended effect.</font> [B236]"
        elif self.sum() == 8:
            myStr += " <font color='#ff0000'>Spell fails entirely.  Caster takes 1 point of damage.</font> [B236]"
        elif self.sum() == 13:
            myStr += " <font color='#ff0000'>Spell produces the reverse of the intended effect.</font> [B236]"
        elif self.sum() == 7:
            myStr += " <font color='#ff0000'>Spell affects someone or something other than the intended subject.</font> [B236]"
        elif self.sum() == 14:
            myStr += " <font color='#ff0000'>Spell seems to work, but it is only a useless illusion.</font> [B236]"
        elif self.sum() == 5 or self.sum() == 6:
            myStr += " <font color='#ff0000'>Spell is cast on one of the caster's companions (if harmful) or a random nearby foe (if beneficial).</font> [B236]"
        elif self.sum() == 15 or self.sum() == 16:
            myStr += " <font color='#ff0000'>Spell has the reverse of the intended, on the wrong target.  Roll randomly.</font> [B236]"
        elif self.sum() == 4:
            myStr += " <font color='#ff0000'>Spell is cast on caster (if harmful) or on a random nearby foe (if beneficial).</font> [B236]"
        elif self.sum() == 17:
            myStr += " <font color='#ff0000'>Spell fails entirely.  Caster temporarily forgets the spell.  Make a weekly IQ roll (after a week passes) until the spell is remembered.</font> [B236]"
        elif self.sum() == 3:
            myStr += " <font color='#ff0000'>Spell fails entirely.  Caster takes 1d of injury.</font> [B236]"
        elif self.sum() == 18:
            myStr += " <font color='#ff0000'>Spell fails entirely.  A demon or other malign entity appears and attacks the caster.  (GM may waive this if the caster and spell were both lily-white, pure good in intent.)</font> [B236]"

        return myStr

class gurpsfrightcheck(std):
    
    def __init__(self,source=[],skill=0,mod=0):
        std.__init__(self,source)
        self.skill = skill
        self.mod = mod

    
    def is_success(self):
        return (((self.sum()) <= self.skill+self.mod) and (self.sum() < 14))

    
    def __str__(self):
        myStr = "[" + str(self.data[0])
        for a in self.data[1:]:
            myStr += ","
            myStr += str(a)
        myStr +="]"
        myStr += " = <b>" + str(self.sum()) + "</b>"

        if self.skill+self.mod < 14:
            myStr += " vs <b>(" + str(self.skill+self.mod) + ")</b>"
            Diff = abs((self.skill+self.mod) - self.sum())
        else:
            myStr += " vs <b>(13)</b>"
            Diff = abs(13 - self.sum())

        if self.is_success():
            if self.sum() == 3 or self.sum() == 4:
                myStr += " or less <font color='#ff0000'><b>Critical Success!</b></font> [B556]"
            else:
                myStr += " or less <font color='#ff0000'><b>Success!</b> by " + str(Diff) +" </font>"
        else:
                myStr += " or less <font color='#ff0000'><b>Failure!</b> by " + str(Diff) +" </font>"

        if self.skill + self.mod > 13:
            myStr += " Rule of 14 in effect [B360]"

        if not(self.is_success()):
            intD1 = int(random.uniform(1,7))
            intD2 = int(random.uniform(1,7))
            intD3 = int(random.uniform(1,7))
            intFright = intD1 + intD2 + intD3 + Diff
            myStr += "<br />Rolling on Fright Check Table<br />[" + str(intD1) + "," + str(intD2) + "," + str(intD3) + "] ==> " + str(intFright - Diff) + " +  " + str(Diff) + " = " + str(intFright) + "<br />"
            if intFright < 6:
                myStr += "<font color='#ff0000'>Stunned for one second, then recover automatically.</font> [B360]"
            elif intFright < 8:
                myStr += "<font color='#ff0000'>Stunned for one second.  Every second after that, roll vs. unmodified Will to snap out of it.</font> [B360]"
            elif intFright < 10:
                myStr += "<font color='#ff0000'>Stunned for one second.  Every second after that, roll vs. Will, plus whatever bonuses or penalties you had on your original roll, to snap out of it.</font> [B360]"
            elif intFright == 10:
                strStun = str(int(random.uniform(1,7)))
                myStr += "<font color='#ff0000'>Stunned for " + strStun + " seconds.  Every second after that, roll vs. Will, plus whatever bonuses or penalties you had on your original roll, to snap out of it.</font> [B360]"
            elif intFright == 11:
                strStun = str(int(random.uniform(2,13)))
                myStr += "<font color='#ff0000'>Stunned for " + strStun + " seconds.  Every second after that, roll vs. Will, plus whatever bonuses or penalties you had on your original roll, to snap out of it.</font> [B361]"
            elif intFright == 12:
                myStr += "<font color='#ff0000'>Lose your lunch.  Treat this as retching for (25-HT) seconds, and then roll vs. HT each second to recover [B428].</font> [B361]"
            elif intFright == 13:
                myStr += "<font color='#ff0000'>Acquire a new mental quirk.</font> [B361]"
            elif intFright < 16:
                strFP = str(int(random.uniform(1,7)))
                strSeconds = str(int(random.uniform(1,7)))
                myStr += "<font color='#ff0000'>Lose " + strFP + " FP, and stunned for " + strSeconds + " seconds.  Every second after that, roll vs. Will, plus whatever bonuses or penalties you had on your original roll, to snap out of it.</font> [B361]"
            elif intFright == 16:
                strSeconds = str(int(random.uniform(1,7)))
                myStr += "<font color='#ff0000'>Stunned for " + strSeconds + " seconds.  Every second after that, roll vs. Will, plus whatever bonuses or penalties you had on your original roll, to snap out of it.  Acquire a new mental quirk.</font> [B361]"
            elif intFright == 17:
                strMinutes = str(int(random.uniform(1,7)))
                myStr += "<font color='#ff0000'>Faint for " + strMinutes + " minutes.  Every minute after that roll vs. HT to recover.</font> [B361]"
            elif intFright == 18:
                strMinutes = str(int(random.uniform(1,7)))
                myStr += "<font color='#ff0000'>Faint for " + strMinutes + " minutes and roll vs. HT immediately.  On a failed roll, take 1 HP of injury as you collapse.  Every minute after that roll vs. HT to recover.</font> [B361]"
            elif intFright == 19:
                strMinutes = str(int(random.uniform(2,13)))
                myStr += "<font color='#ff0000'>Severe faint, lasting for " + strMinutes + " minutes.  Every minute after that roll vs. HT to recover.  Take 1 HP of injury.</font> [B361]"
            elif intFright == 20:
                strMinutes = str(int(random.uniform(4,25)))
                strFP = str(int(random.uniform(1,7)))
                myStr += "<font color='#ff0000'>Faint bordering on shock, lastering for " + strMinutes + " minutes.  Also, lose " + strFP + " FP.</font> [B361]"
            elif intFright == 21:
                strMinutes = str(int(random.uniform(1,7)))
                myStr += "<font color='#ff0000'>Panic.  You run around screaming, sit down and cry, or do something else equally pointless for " + strMinutes + " minutes.  Every minute after that, roll vs. unmodified Will to snap out of it.</font> [B361]"
            elif intFright == 22:
                myStr += "<font color='#ff0000'>Acquire a new -10-point Delusion (B130).</font> [B361]"
            elif intFright == 23:
                myStr += "<font color='#ff0000'>Acquire a new -10-point Phobia (B148) or other -10-point mental disadvantage.</font> [B361]"
            elif intFright == 24:
                myStr += "<font color='#ff0000'>Major physical effect, set by the GM: hair turns white, age five years overnight, go partially deaf, etc.  (Acquire -15 points worth of physical disadvantages.  Each year of aging = -3 points.)</font> [B361]"
            elif intFright == 25 :
                myStr += "<font color='#ff0000'>If you already have a Phobia or other mental disadvantage that is logically related to the frightening incident, your self-control number becomes one step worse.  If not, or if your self-control number is already 6, add a new -10-point Phobia or other -10-point mental disadvantage.</font> [B361]"
            elif intFright == 26:
                strMinutes = str(int(random.uniform(1,7)))
                myStr += "<font color='#ff0000'>Faint for " + strMinutes + " minutes and roll vs. HT immediately.  On a failed roll, take 1 HP of injury as you collapse.  Every minute after that roll vs. HT to recover.  Also acquire a new -10-point Delusion (B130).</font> [B361]"
            elif intFright == 27:
                strMinutes = str(int(random.uniform(1,7)))
                myStr += "<font color='#ff0000'>Faint for " + strMinutes + " minutes and roll vs. HT immediately.  On a failed roll, take 1 HP of injury as you collapse.  Every minute after that roll vs. HT to recover.  Also acquire a new -10-point Phobia (B148) or other -10-point mental disadvantage.</font> [B361]"
            elif intFright == 28:
                myStr += "<font color='#ff0000'>Light coma.  You fall unconscious, rolling vs. HT every 30 minutes to recover.  For 6 hours after you come to, all skill rolls and attribute checks are at -2.</font> [B361]"
            elif intFright == 29:
                strHours = str(int(random.uniform(1,7)))
                myStr += "<font color='#ff0000'>Coma.  You fall unconcious for " + strHours + " hours.  At the end of the " + strHours + " hours, roll vs. HT to recover.  Continue to roll every " + strHours + " hours until you recover.</font> [B361]"
            elif intFright == 30:
                strDays = str(int(random.uniform(1,7)))
                myStr += "<font color='#ff0000'>Catatonia.  Stare into space for " + strDays + " days.  Then roll vs. HT.  On a failed roll, remain catatonic for another " + strDays + " days, and so on.  If you have no medical care, lose 1 HP the first day, 2 HP the second day and so on.  If you survive and awaken, all skill rolls and attribute checks are at -2 for as many days as the catatonia lasted.</font> [B361]"
            elif intFright == 31:
                strMinutes = str(int(random.uniform(1,7)))
                strFP = str(int(random.uniform(1,7)))
                strInjury = str(int(random.uniform(1,7)))
                myStr += "<font color='#ff0000'>Seizure.  You lose control of your body and fall to the ground in a fit lasting " + strMinutes + " minutes and costing " + strFP + " FP.  Also, roll vs. HT.  On a failure, take " + strInjury + " HP of injury.  On a critical failure, you also lose 1 HT <i>permanently</i>.</font> [B361]"
            elif intFright == 32:
                strInjury = str(int(random.uniform(2,13)))
                myStr += "<font color='#ff0000'>Stricken.  You fall to the ground, taking " + strInjury + " HP of injury in the form of a mild heart attack or stroke.</font> [B361]"
            elif intFright == 33:
                myStr += "<font color='#ff0000'>Total panic.  You are out of control; you might do anything (GM rolls 3d: the higher the roll, the more useless your reaction).  For instance, you might jump off a cliff to avoid the monster.  If you survive your first reaction, roll vs. Will to come out of the panic.  If you fail, the GM rolls again for another panic reaction, and so on!</font> [B361]"
            elif intFright == 34:
                myStr += "<font color='#ff0000'>Acquire a new -15-point Delusion (B130).</font> [B361]"
            elif intFright == 35:
                myStr += "<font color='#ff0000'>Acquire a new -15-point Phobia (B148) or other -15-point mental disadvantage.</font> [B361]"
            elif intFright == 36:
                myStr += "<font color='#ff0000'>Severe physical effect, set by the GM.  (Acquire -20 points worth of physical disadvantages, aging = -3 per year).</font> [B361]"
            elif intFright == 37:
                myStr += "<font color='#ff0000'>Severe physical effect, set by the GM.  (Acquire -30 points worth of physical disadvantages, aging = -3 per year).</font> [B361]"
            elif intFright == 39:
                strHours = str(int(random.uniform(1,7)))
                myStr += "<font color='#ff0000'>Coma.  You fall unconcious for " + strHours + " hours.  At the end of the " + strHours + " hours, roll vs. HT to recover.  Continue to roll every " + strHours + " hours until you recover.  Also acquire a new -15-point Delusion (B130).</font> [B361]"
            elif intFright == 39:
                strHours = str(int(random.uniform(1,7)))
                myStr += "<font color='#ff0000'>Coma.  You fall unconcious for " + strHours + " hours.  At the end of the " + strHours + " hours, roll vs. HT to recover.  Continue to roll every " + strHours + " hours until you recover.  Also acquire a new -15-point Phobia (B148) or other -15-point mental disadvantage.</font> [B361]"
            else:
                strHours = str(int(random.uniform(1,7)))
                myStr += "<font color='#ff0000'>Coma.  You fall unconcious for " + strHours + " hours.  At the end of the " + strHours + " hours, roll vs. HT to recover.  Continue to roll every " + strHours + " hours until you recover.  Also acquire a new -15-point Phobia (B148) or other -15-point mental disadvantage.  Also lose 1 point of IQ <i>permanently</i>.  This automatically reduces all IQ-based skill, including magic spells, by 1.</font> [B361]"
        return myStr

class gurpsfrightcheckfail(std):
    
    def __init__(self,source=[],mod=0):
        std.__init__(self,source)
        self.mod = mod

    
    def __str__(self):
        myStr = "[" + str(self.data[0])
        for a in self.data[1:]:
            myStr += ","
            myStr += str(a)
        myStr +="] + " + str(self.mod)
        intFright = self.sum() + self.mod
        myStr += " = <b>" + str(intFright) + "</b> "

        if intFright < 6:
            myStr += "<font color='#ff0000'>Stunned for one second, then recover automatically.</font> [B360]"
        elif intFright < 8:
            myStr += "<font color='#ff0000'>Stunned for one second.  Every second after that, roll vs. unmodified Will to snap out of it.</font> [B360]"
        elif intFright < 10:
            myStr += "<font color='#ff0000'>Stunned for one second.  Every second after that, roll vs. Will, plus whatever bonuses or penalties you had on your original roll, to snap out of it.</font> [B360]"
        elif intFright == 10:
            strStun = str(int(random.uniform(1,7)))
            myStr += "<font color='#ff0000'>Stunned for " + strStun + " seconds.  Every second after that, roll vs. Will, plus whatever bonuses or penalties you had on your original roll, to snap out of it.</font> [B360]"
        elif intFright == 11:
            strStun = str(int(random.uniform(2,13)))
            myStr += "<font color='#ff0000'>Stunned for " + strStun + " seconds.  Every second after that, roll vs. Will, plus whatever bonuses or penalties you had on your original roll, to snap out of it.</font> [B361]"
        elif intFright == 12:
            myStr += "<font color='#ff0000'>Lose your lunch.  Treat this as retching for (25-HT) seconds, and then roll vs. HT each second to recover [B428].</font> [B361]"
        elif intFright == 13:
            myStr += "<font color='#ff0000'>Acquire a new mental quirk.</font> [B361]"
        elif intFright < 16:
            strFP = str(int(random.uniform(1,7)))
            strSeconds = str(int(random.uniform(1,7)))
            myStr += "<font color='#ff0000'>Lose " + strFP + " FP, and stunned for " + strSeconds + " seconds.  Every second after that, roll vs. Will, plus whatever bonuses or penalties you had on your original roll, to snap out of it.</font> [B361]"
        elif intFright == 16:
            strSeconds = str(int(random.uniform(1,7)))
            myStr += "<font color='#ff0000'>Stunned for " + strSeconds + " seconds.  Every second after that, roll vs. Will, plus whatever bonuses or penalties you had on your original roll, to snap out of it.  Acquire a new mental quirk.</font> [B361]"
        elif intFright == 17:
            strMinutes = str(int(random.uniform(1,7)))
            myStr += "<font color='#ff0000'>Faint for " + strMinutes + " minutes.  Every minute after that roll vs. HT to recover.</font> [B361]"
        elif intFright == 18:
            strMinutes = str(int(random.uniform(1,7)))
            myStr += "<font color='#ff0000'>Faint for " + strMinutes + " minutes and roll vs. HT immediately.  On a failed roll, take 1 HP of injury as you collapse.  Every minute after that roll vs. HT to recover.</font> [B361]"
        elif intFright == 19:
            strMinutes = str(int(random.uniform(2,13)))
            myStr += "<font color='#ff0000'>Severe faint, lasting for " + strMinutes + " minutes.  Every minute after that roll vs. HT to recover.  Take 1 HP of injury.</font> [B361]"
        elif intFright == 20:
            strMinutes = str(int(random.uniform(4,25)))
            strFP = str(int(random.uniform(1,7)))
            myStr += "<font color='#ff0000'>Faint bordering on shock, lastering for " + strMinutes + " minutes.  Also, lose " + strFP + " FP.</font> [B361]"
        elif intFright == 21:
            strMinutes = str(int(random.uniform(1,7)))
            myStr += "<font color='#ff0000'>Panic.  You run around screaming, sit down and cry, or do something else equally pointless for " + strMinutes + " minutes.  Every minute after that, roll vs. unmodified Will to snap out of it.</font> [B361]"
        elif intFright == 22:
            myStr += "<font color='#ff0000'>Acquire a new -10-point Delusion (B130).</font> [B361]"
        elif intFright == 23:
            myStr += "<font color='#ff0000'>Acquire a new -10-point Phobia (B148) or other -10-point mental disadvantage.</font> [B361]"
        elif intFright == 24:
            myStr += "<font color='#ff0000'>Major physical effect, set by the GM: hair turns white, age five years overnight, go partially deaf, etc.  (Acquire -15 points worth of physical disadvantages.  Each year of aging = -3 points.)</font> [B361]"
        elif intFright == 25 :
            myStr += "<font color='#ff0000'>If you already have a Phobia or other mental disadvantage that is logically related to the frightening incident, your self-control number becomes one step worse.  If not, or if your self-control number is already 6, add a new -10-point Phobia or other -10-point mental disadvantage.</font> [B361]"
        elif intFright == 26:
            strMinutes = str(int(random.uniform(1,7)))
            myStr += "<font color='#ff0000'>Faint for " + strMinutes + " minutes and roll vs. HT immediately.  On a failed roll, take 1 HP of injury as you collapse.  Every minute after that roll vs. HT to recover.  Also acquire a new -10-point Delusion (B130).</font> [B361]"
        elif intFright == 27:
            strMinutes = str(int(random.uniform(1,7)))
            myStr += "<font color='#ff0000'>Faint for " + strMinutes + " minutes and roll vs. HT immediately.  On a failed roll, take 1 HP of injury as you collapse.  Every minute after that roll vs. HT to recover.  Also acquire a new -10-point Phobia (B148) or other -10-point mental disadvantage.</font> [B361]"
        elif intFright == 28:
            myStr += "<font color='#ff0000'>Light coma.  You fall unconscious, rolling vs. HT every 30 minutes to recover.  For 6 hours after you come to, all skill rolls and attribute checks are at -2.</font> [B361]"
        elif intFright == 29:
            strHours = str(int(random.uniform(1,7)))
            myStr += "<font color='#ff0000'>Coma.  You fall unconcious for " + strHours + " hours.  At the end of the " + strHours + " hours, roll vs. HT to recover.  Continue to roll every " + strHours + " hours until you recover.</font> [B361]"
        elif intFright == 30:
            strDays = str(int(random.uniform(1,7)))
            myStr += "<font color='#ff0000'>Catatonia.  Stare into space for " + strDays + " days.  Then roll vs. HT.  On a failed roll, remain catatonic for another " + strDays + " days, and so on.  If you have no medical care, lose 1 HP the first day, 2 HP the second day and so on.  If you survive and awaken, all skill rolls and attribute checks are at -2 for as many days as the catatonia lasted.</font> [B361]"
        elif intFright == 31:
            strMinutes = str(int(random.uniform(1,7)))
            strFP = str(int(random.uniform(1,7)))
            strInjury = str(int(random.uniform(1,7)))
            myStr += "<font color='#ff0000'>Seizure.  You lose control of your body and fall to the ground in a fit lasting " + strMinutes + " minutes and costing " + strFP + " FP.  Also, roll vs. HT.  On a failure, take " + strInjury + " HP of injury.  On a critical failure, you also lose 1 HT <i>permanently</i>.</font> [B361]"
        elif intFright == 32:
            strInjury = str(int(random.uniform(2,13)))
            myStr += "<font color='#ff0000'>Stricken.  You fall to the ground, taking " + strInjury + " HP of injury in the form of a mild heart attack or stroke.</font> [B361]"
        elif intFright == 33:
            myStr += "<font color='#ff0000'>Total panic.  You are out of control; you might do anything (GM rolls 3d: the higher the roll, the more useless your reaction).  For instance, you might jump off a cliff to avoid the monster.  If you survive your first reaction, roll vs. Will to come out of the panic.  If you fail, the GM rolls again for another panic reaction, and so on!</font> [B361]"
        elif intFright == 34:
            myStr += "<font color='#ff0000'>Acquire a new -15-point Delusion (B130).</font> [B361]"
        elif intFright == 35:
            myStr += "<font color='#ff0000'>Acquire a new -15-point Phobia (B148) or other -15-point mental disadvantage.</font> [B361]"
        elif intFright == 36:
            myStr += "<font color='#ff0000'>Severe physical effect, set by the GM.  (Acquire -20 points worth of physical disadvantages, aging = -3 per year).</font> [B361]"
        elif intFright == 37:
            myStr += "<font color='#ff0000'>Severe physical effect, set by the GM.  (Acquire -30 points worth of physical disadvantages, aging = -3 per year).</font> [B361]"
        elif intFright == 39:
            strHours = str(int(random.uniform(1,7)))
            myStr += "<font color='#ff0000'>Coma.  You fall unconcious for " + strHours + " hours.  At the end of the " + strHours + " hours, roll vs. HT to recover.  Continue to roll every " + strHours + " hours until you recover.  Also acquire a new -15-point Delusion (B130).</font> [B361]"
        elif intFright == 39:
            strHours = str(int(random.uniform(1,7)))
            myStr += "<font color='#ff0000'>Coma.  You fall unconcious for " + strHours + " hours.  At the end of the " + strHours + " hours, roll vs. HT to recover.  Continue to roll every " + strHours + " hours until you recover.  Also acquire a new -15-point Phobia (B148) or other -15-point mental disadvantage.</font> [B361]"
        else:
            strHours = str(int(random.uniform(1,7)))
            myStr += "<font color='#ff0000'>Coma.  You fall unconcious for " + strHours + " hours.  At the end of the " + strHours + " hours, roll vs. HT to recover.  Continue to roll every " + strHours + " hours until you recover.  Also acquire a new -15-point Phobia (B148) or other -15-point mental disadvantage.  Also lose 1 point of IQ <i>permanently</i>.  This automatically reduces all IQ-based skill, including magic spells, by 1.</font> [B361]"

        return myStr
