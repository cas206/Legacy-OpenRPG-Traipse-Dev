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
#
#-------------------------------------------------------------------------
#
#  Usage:
#
#   Die  Roller: /dieroller rq
#
#   Skill  Roll: [1d100.skill(50,0,0)]         # ( skill%, modifer, MA% )
#
#   Parry  Roll: [1d100.parry(50,0,0,12)]      # ( skill%, modifer, MA%, Weapon/Shield AP )
#
#   Dodge  Roll: [1d100.parry(50,0,0)]         # ( skill%, modifer, MA% )
#
#   Attack Roll: [1d100.attack(50,0,0,2,9,3,0)]
#       ( skill%, modifer, MA%, min weap dam, max weap dam, dam bonus, truesword )
#
#   Sorcery Roll: [1d100.sorcery(90,   0,   3,   6,   1,   1,    1)]
#                               (sk, mod, pow, cer, int,  acc, mlt)
#
#
#
#   Skill Training Unlimited Roll: [1d100.trainskill(30,75)]       # (starting skill%, desired skill%)
#   Skill Training Cost Limited:   [1d100.trainskillcost(1000, 50) # (payment, starting skill%)
#   Skill Training Time Limited:   [1d100.trainskilltime(150, 50)  # (time, strting skill%)
#
#-------------------------------------------------------------------------
# --
#
# File: rq.py
# Version:
#   $Id: rq.py,v .1 pelwer
#
# Description: Runequest die roller originally based on Heroman's Hero Dieroller
#
#
# v.1 - pelwer - 2/5/2005
#  o Original release
# v.2 - pelwer - 10/30/2006
#  o Ported to openrpg+ by removing dependance on whrandom
#  o Fixed Riposte spelling
#  o Deleted sorcalc - never used
#  o Added Sorcery Fumble table to sorcery spell roller
#

__version__ = "$Id: runequest.py,v Traipse 'Ornery-Orc' prof.ebral Exp $"

from time import time, clock
import random
from math import floor

from std import std
from orpg.dieroller.base import *

# rq stands for "Runequest"

class runequest(std):
    name = "runequest"
    def __init__(self,source=[]):
        std.__init__(self,source)

    def skill(self,sk,mod,ma):
        return rqskill(self,sk,mod,ma)

    def parry(self,sk,mod,ma,AP):
        return rqparry(self,sk,mod,ma,AP)

    def dodge(self,sk,mod,ma):
        return rqdodge(self,sk,mod,ma)

    def attack(self,sk,mod,ma,mindam,maxdam,bondam,trueswd):
        return rqattack(self,sk,mod,ma,mindam,maxdam,bondam,trueswd)

    def sorcery(self,sk,mod,pow,cer,int,acc,mlt):
        return rqsorcery(self,sk,mod,pow,cer,int,acc,mlt)

    def trainskill(self,initial,final):
        return rqtrainskill(self,initial,final)

    def trainskillcost(self,cost,sk):
        return rqtrainskillcost(self,cost,sk)

    def trainskilltime(self,time,sk):
        return rqtrainskilltime(self,time,sk)

die_rollers.register(runequest)

#  RQ Skill Training Cost/Time unlimited
#
# [1d100.trainskill(10,20)]
#          initial skill%, final skill%
#
# sk    = skill %
#
#
class rqtrainskill(std):
    def __init__(self,source=[],initial=11,final=0):
        std.__init__(self,source)
        self.s = initial
        self.f = final

    def __str__(self):
        myStr = "Unrestricted Training"
        if self.s == 0:
            myStr = "Initial training completed for Cost(50) Time(20) Skill(1 + modifier)"
        else:
            cost  = 0
            time  = 0
            myStr = "Training: "
            while self.s < self.f and self.s < 75:
                cost   += self.s * 5
                time   += self.s * 1
                self.s += random.uniform(1,4) + 1
            myStr  = "Training completed:\n"
            myStr += "\tCost(" + str(int(cost)) + ")\n"
            myStr += "\tTime(" + str(int(time)) + ")\n"
            myStr += "\tSkill(" + str(int(self.s)) + ")"
        return myStr


#  RQ Skill Training Cost Limited
#
# [1d100.trainskillcost(50,0)]
#          cost, skill%
#
# cost  = cash for training
# sk    = skill %
#
#
class rqtrainskillcost(std):
    def __init__(self,source=[],cost=11,sk=0):
        std.__init__(self,source)
        self.cost = cost
        self.sk   = sk

    def __str__(self):
        myStr = ""
        if self.sk == 0 and self.cost >= 50:
            myStr = "Initial training completed for Cost(50), Time(50), Skill(1 + modifier)"
        else:
            cost  = 0
            time  = 0
            icost = self.sk * 5
            myStr = "Training: "
            while (cost + icost) < self.cost:
                if self.sk >= 75:
                    break
                cost += icost
                time += self.sk * 1
                self.sk += random.uniform(1,4) + 1
                icost = self.sk * 5
            myStr  = "Training completed: "
            myStr += "Cost(" + str(int(cost)) + ") "
            myStr += "Time(" + str(int(time)) + ") "
            myStr += "Skill(" + str(int(self.sk)) + ")"
        return myStr


#  RQ Skill Training Time Limited
#
# [1d100.trainskilltime(50,0)]
#          time, skill%
#
# time  = time for training
# sk    = skill %
#
#
class rqtrainskilltime(std):
    def __init__(self,source=[],time=11,sk=0):
        std.__init__(self,source)
        self.time = time
        self.sk   = sk

    def __str__(self):
        myStr = ""
        if self.sk == 0 and self.time >= 20:
            myStr = "Initial training completed for Cost(50), Time(50), Skill(1 + modifier)"
        else:
            cost  = 0
            time  = 0
            itime = self.sk * 1
            myStr = "Trainingsss: "
            while (time + itime) < self.time:
                if self.sk >= 75:
                    break
                cost += self.sk * 5
                time += itime
                self.sk += random.uniform(1,4) + 1
                itime = self.sk * 5
            myStr  = "Training completed: "
            myStr += "Cost(" + str(int(cost)) + ") "
            myStr += "Time(" + str(int(time)) + ") "
            myStr += "Skill(" + str(int(self.sk)) + ")"
        return myStr

#  RQ Skill Roll
#
# [1d100.skill(50,0,0)]
#          skill%, modifer, ma%
#
# sk    = skill %
# mod   = modifier %
# ma    = martial arts %
# skill = sk + mod
#
# success   roll <= skill
#
# failure   roll > skill
#
# crit
#     push( @{$::Cre{Weapons}{$weap_cnt}}, POSIX::floor( skill/20 ) );
#
# special
#     push( @{$::Cre{Weapons}{$weap_cnt}}, POSIX::floor( $skill/5 ) );
#
# fumble: if ( $skill > 100 ) { $fum = 0; } else { $fum = 100 - $skill; }
#             $fum = 100 - POSIX::floor( $fum/20 );
#             if ( $fum == 100 ) { $fum = '00'; };
#
class rqskill(std):
    def __init__(self,source=[],sk=11,mod=0,ma=0):
        std.__init__(self,source)
        self.sk  = sk
        self.mod = mod
        self.ma  = ma

    def is_success(self):
        return (((self.sum() <= (self.sk + self.mod)) or (self.sum() <= 5)) and (self.sum() <= 95))

    def is_ma(self):
        return (self.sum() <= self.ma)

    def is_special(self):
        return (self.sum() <= int(floor((self.sk + self.mod)/5)))

    def is_critical(self):
        return (self.sum() <= int(floor((self.sk + self.mod) / 20)))

    def is_fumble(self):
        if ( self.sk >= 100 ):
            fum = 0
        else:
            fum = (100 - self.sk )
        final_fum = ( 100 - int( floor( fum/20  ) ) )
        return (  self.sum() >= final_fum )

    def __str__(self):
        strAdd="+"
        swapmod= self.mod
        if self.mod < 0:
            strAdd= "-"
            swapmod= -self.mod
        modSum = self.sum()
        # build output string
        myStr = " (" + str(modSum) + ")"
        myStr += " vs [" + str(self.sk) + strAdd + str(swapmod) + "]"
        if self.is_fumble():
            myStr += " <b><font color=red>Fumble!</font></b>"
        elif self.is_critical():
            myStr += " <b><font color=green>Critical!</font></b>"
        elif self.is_special():
            myStr += " <i><font color=green>Special!</font></i>"
        elif self.is_success() and self.is_ma():
            myStr += " <i><font color=green>Special!</font></i>"
        elif self.is_success():
            myStr += " <font color=blue>Success!</font>"
        else:
            myStr += " <font color=red>Failure!</font>"
        Diff = self.sk - modSum
        myStr += " </font>"
        return myStr

#
# RQ Parry Roll
#
# same as skill but with fumble dice and armor points
#
# [1d100.parry(50,0,0,12)]
#             skill%, modifer, ma%, Weapon AP
#

class rqparry(std):
    def __init__(self,source=[],sk=11,mod=0,ma=0,AP=0):
        std.__init__(self,source)
        self.sk = sk
        self.mod = mod
        self.ma  = ma
        self.AP = AP

    def is_success(self):
        return (((self.sum() <= (self.sk + self.mod)) or (self.sum() <= 5)) and (self.sum() <= 95))

    def is_special(self):
        return (self.sum() <= int(floor((self.sk + self.mod) / 5)))

    def is_ma(self):
        return (self.sum() <= self.ma)

    def is_riposte(self):
        return (self.sum() <= (self.ma / 5))

    def is_critical(self):
        return ( (  self.sum() <= int( floor( ( self.sk + self.mod  )/20 ) ) ) )

    def is_fumble(self):
        if ( self.sk >= 100 ):
            fum = 0
        else:
            fum = (100 - self.sk )
        final_fum = ( 100 - int( floor( fum/20  ) ) )
        return (  self.sum() >= final_fum )

    def __str__(self):
        # get fumble roll result in case needed
        fum_roll = random.randint(1,100)

        # get special AP
        spec_AP = int( floor ( self.AP * 1.5 ) )

        # figure out +/- for modifer
        strAdd="+"
        swapmod= self.mod
        if self.mod < 0:
            strAdd= "-"
            swapmod= -self.mod
        modSum = self.sum()

        # build output string
        myStr = " (" + str(modSum) + ")"
        myStr += " vs [" + str(self.sk) + strAdd + str(swapmod) + "]"
        if self.is_fumble():
            myStr += " <b><font color=red>Fumble!</font>  See Fumble Chart [" + str(fum_roll) + "]</b>"
        elif self.is_critical() and self.is_riposte():
            myStr += " <b><font color=green>Critical!</font> All damage blocked!</b>"
            myStr += " Riposte next SR"
        elif self.is_critical():
            myStr += " <b><font color=green>Critical!</font> All damage blocked!</b>"
        elif self.is_special and self.is_riposte():
            myStr += " <i><font color=green>Special!</font> Weapon/Shield AP [" + str(spec_AP) + "]</i>"
            myStr += " Riposte next SR"
        elif self.is_special():
            myStr += " <i><font color=green>Special!</font> Weapon/Shield AP [" + str(spec_AP) + "]</i>"
        elif self.is_success() and self.is_ma():
            myStr += " <i><font color=green>Special!</font> Weapon/Shield AP [" + str(spec_AP) + "]</i>"
        elif self.is_success():
            myStr += " <font color=blue>Success!</font> Weapon/Shield AP [" + str(self.AP) + "]"
        else:
            myStr += " <font color=red>Failure!</font>"
        Diff = self.sk - modSum
        myStr += " </font>"
        return myStr

# RQ Dodge Roll
#
# same as skill but with fumble dice and armor points
#
# [1d100.parry(50,0,0)]
#             skill%, modifer, ma%
#

class rqdodge(std):
    def __init__(self,source=[],sk=11,mod=0,ma=0,AP=0):
        std.__init__(self,source)
        self.sk = sk
        self.mod = mod
        self.ma  = ma
        self.AP = AP

    def is_success(self):
        return (((self.sum() <= (self.sk + self.mod)) or (self.sum() <= 5)) and (self.sum() <= 95))

    def is_special(self):
        return (self.sum() <= int(floor((self.sk + self.mod) / 5)))

    def is_ma(self):
        return (self.sum() <= self.ma)

    def is_riposte(self):
        return (self.sum() <= (self.ma / 5))

    def is_critical(self):
        return ( (  self.sum() <= int( floor( ( self.sk + self.mod  )/20 ) ) ) )

    def is_fumble(self):
        if ( self.sk >= 100 ):
            fum = 0
        else:
            fum = (100 - self.sk )
        final_fum = ( 100 - int( floor( fum/20  ) ) )
        return (  self.sum() >= final_fum )

    def __str__(self):
        # get fumble roll result in case needed
        fum_roll = random.randint(1,100)

        # get special AP
        spec_AP = int( floor ( self.AP * 1.5 ) )

        # figure out +/- for modifer
        strAdd="+"
        swapmod= self.mod
        if self.mod < 0:
            strAdd= "-"
            swapmod= -self.mod
        modSum = self.sum()

        # build output string
        myStr = " (" + str(modSum) + ")"
        myStr += " vs [" + str(self.sk) + strAdd + str(swapmod) + "]"
        if self.is_fumble():
            myStr += " <b><font color=red>Fumble!</font>  See Fumble Chart [" + str(fum_roll) + "]</b>"
        elif self.is_critical() and self.is_riposte():
            myStr += " <b><font color=green>Critical!</font> All damage dodged!</b>"
            myStr += " Riposte on next SR"
        elif self.is_critical():
            myStr += " <b><font color=green>Critical!</font> All damage dodged!</b>"
        elif self.is_special and self.is_riposte():
            myStr += " <i><font color=green>Special!</font> Damage dodged</b>"
            myStr += " Riposte on next SR"
        elif self.is_special():
            myStr += " <i><font color=green>Special!</font> Damage dodged</b>"
        elif self.is_success() and self.is_ma():
            myStr += " <i><font color=green>Special!</font> Damage dodged</b>"
        elif self.is_success():
            myStr += " <font color=blue>Success!</font> Damage dodged</b>"
        else:
            myStr += " <font color=red>Failure!</font>"
        Diff = self.sk - modSum
        myStr += " </font>"
        return myStr


#
# RQ Attack Roll
#
# same as skill but with fumble dice and armor points
#
# [1d100.attack(50,0,0,2,9,3,1)]
#             skill%, modifer, ma%, min weap dam, max weap dam, dam bonus, truesword_enabled
#
class rqattack(std):
    def __init__(self,source=[],sk=11,mod=0,ma=0,mindam=0,maxdam=0,bondam=0,trueswd=0):
        std.__init__(self,source)
        self.sk = sk
        self.mod = mod
        self.ma  = ma
        self.mindam = mindam
        self.maxdam = maxdam
        self.bondam = bondam
        self.trueswd = trueswd

    def is_success(self):
        return (((self.sum() <= (self.sk + self.mod)) or (self.sum() <= 5)) and (self.sum() <= 95))

    def is_ma(self):
        return (self.sum() <= self.ma)

    def is_special(self):
        return (self.sum() <= int(floor((self.sk + self.mod) / 5)))

    def is_critical(self):
        return ((self.sum() <= int(floor((self.sk + self.mod) / 20))))

    def is_supercritical(self):
        return (self.sum() == 1)

    def is_fumble(self):
        if ( self.sk >= 100 ):
            fum = 0
        else:
            fum = (100 - self.sk )
        final_fum = ( 100 - int( floor( fum/20  ) ) )
        return (  self.sum() >= final_fum )

    def __str__(self):

        # get fumble roll result in case needed
        fum_roll = random.randint(1,100)

        # get hit location roll result in case needed
        location = random.randint(1,20)
        myStr = " to the ["+ str(location) + "] "
        if location < 5:
            myStr += "<B>Right Leg</B>"
        elif location < 9:
            myStr += "<B>Left Leg</B>"
        elif location < 12:
            myStr += "<B>Abdomen</B>"
        elif location < 13:
            myStr += "<B>Chest</B>"
        elif location < 16:
            myStr += "<B>Right Arm</B>"
        elif location < 19:
            myStr += "<B>Left Arm</B>"
        else:
            myStr += "<B>Head</B>"
        hit_loc = myStr

        # get normal damage in case needed
        norm_damage = random.randint(self.mindam*(self.trueswd+1),self.maxdam*(self.trueswd+1)) + self.bondam
        norm_damage_string  = "{" + str( self.mindam*(self.trueswd+1) ) + "-"
        norm_damage_string += str(self.maxdam*(self.trueswd+1)) + "+" + str(self.bondam)
        norm_damage_string += "}[" + str(norm_damage) + "] "

        # get special/critical damage in case needed
        crit_damage = random.randint( self.mindam*(self.trueswd+2), self.maxdam*(self.trueswd+2) ) + self.bondam
        crit_damage_string = "{" + str( self.mindam*(self.trueswd+2) ) + "-" + str(self.maxdam*(self.trueswd+2)) + "+" + str(self.bondam) + "}[" + str(crit_damage) + "] "

        # get supercritical damage in case needed
        super_damage = norm_damage + self.maxdam
        super_damage_string  = "{" + str( self.mindam*(self.trueswd+1) ) + "-"
        super_damage_string += str(self.maxdam*(self.trueswd+1)) + "+" + str(self.maxdam)
        super_damage_string += "+" + str(self.bondam) + "}[" + str(super_damage) + "] "

        # figure out +/- for modifer
        strAdd="+"
        swapmod= self.mod
        if self.mod < 0:
            strAdd= "-"
            swapmod= -self.mod
        modSum = self.sum()

        # build output string
        myStr = " (" + str(modSum) + ")"
        myStr += " vs [" + str(self.sk) + strAdd + str(swapmod) + "]"
        if self.is_fumble():
            myStr += " <b><font color=red>Fumble!</font>  See Fumble Chart [" + str(fum_roll) + "]</b>"
        elif (self.is_supercritical() and self.is_success()):
            myStr += " <b><font color=green>Super Critical!</font></b> Damage: " + str(super_damage_string) + "<u>No Armor Stops</u>" + str(hit_loc)
        elif (self.is_critical() and self.is_success()):
            myStr += " <b><font color=green>Critical!</font></b> Damage: " + str(crit_damage_string) + "<u>No Armor Stops</u>" + str(hit_loc)
        elif ( self.is_special() and self.is_success() ):
            myStr += " <i><font color=green>Special!</font></i> Damage: " + str(crit_damage_string) + str(hit_loc)
        elif (self.is_success() and self.is_ma()):
            myStr += " <i><font color=green>Special!</font></i> Damage: " + str(crit_damage_string) + str(hit_loc)
        elif self.is_success():
            myStr += " <font color=blue>Success!</font> Damage: " + str(norm_damage_string) + str(hit_loc)
        else:
            myStr += " <font color=red>Failure!</font>"
        return myStr

#
#
#   Sorcery Roll: [1d100.sorcery(90,   10,  5,   4,   3,   2,    1)]
#                               (sk, mod, pow, cer, int,  acc, mlt)
#
# Ceremony: (+1d6% per strike rank spent on ceremony)
# Intensity: (-3% per point of Intensity)
# Duration: (-4% per point of Duration)
# Range: (-5% per point of Range)
# Multispell: (-10% per each spell over 1)
# Acceleration: (-5% per point of Acceleration)
# Hold: (-2% per point in spell Held)
#
class rqsorcery(std):
    def __init__(self,source=[],sk=11,mod=0,pow=0,cer=0,int=0,acc=0,mlt=0):
        std.__init__(self,source)
        self.sk  = sk   # sorcery skill
        self.mod = mod  # additional modifier ( from duration, range, etc )
        self.pow = pow  # boost pow and additional pow ( from duration, range, etc )
        self.cer = cer  # ceremony d6
        self.int = int  # intensity ( -3% )
        self.acc = acc  # accelerate ( -5% )
        self.mlt = mlt  # multispell ( -10% )

    def is_success(self):
        return (((self.sum() <= (self.sk + self.mod)) or (self.sum() <= 5)) and (self.sum() <= 95))

    def is_special(self):
        return ( (  self.sum() <= int( floor( ( self.sk + self.mod  )/5  ) ) ) )

    def is_critical(self):
        return ( (  self.sum() <= int( floor( ( self.sk + self.mod  )/20 ) ) ) )

    def is_fumble(self):
        if ( self.sk >= 100 ):
            fum = 0
        else:
            fum = (100 - self.sk )
        final_fum = ( 100 - int( floor( fum/20  ) ) )
        return (  self.sum() >= final_fum )

    def __str__(self):

        # get fumble roll result in case needed
        fum_roll = random.randint(2,12)
        if fum_roll == 12 :
            fum_string = "<br /><font color=purple>Caster temporarily forgets spell. Make an INTx5 roll each day to remember.</font>"
        if fum_roll == 11 :
            fum_string = "<br /><font color=purple>Caster temporarily forgets spell. Make an INTx5 roll each hour to remember.  </font>"
        if fum_roll == 10 :
            fum_string = "<br /><font color=purple>Spell produces reverse of the intended effect.  </font>"
        if fum_roll == 9 :
            fum_string = "<br /><font color=purple>Caster is Stunned. Roll INTx3 to recover at SR 10 each round.  </font>"
        if fum_roll == 8 :
            fum_string = "<br /><font color=purple>Caster takes 2D6 Damage to THP  </font>"
        if fum_roll == 7 :
            fum_string = "<br /><font color=purple>Spell produces reverse of the intended effect at 2x Intensity.  </font>"
        if fum_roll == 6 :
            fum_string = "<br /><font color=purple>Spell is cast on companions (if harmful) or on random nearby foes (if beneficial)  </font>"
        if fum_roll == 5 :
            fum_string = "<br /><font color=purple>Caster takes 1d6 Damage to Head  </font>"
        if fum_roll == 4 :
            fum_string = "<br /><font color=purple>Spell is cast on caster (if harmful) or on random nearby foe (if beneficial)  </font>"
        if fum_roll == 3 :
            fum_string = "<br /><font color=purple>Caster takes 1d6 Damage to THP  </font>"
        if fum_roll == 2 :
            fum_string = "<br /><font color=purple>Caster takes 1 point of Damage to Head  </font>"

            # roll ceremony
        ceremony_roll = random.randint( self.cer, (self.cer*6) )

        # subtract manipulations
        extra_mod = self.mod
        self.mod += ceremony_roll - self.int*3 - self.acc*5 - self.mlt*10

        # add up power cost
        extra_pow = self.pow
        self.pow += self.int + self.mlt + self.acc
        special_pow = int( floor( ( self.pow )/2  ) )

        # figure out +/- for modifer
        strAdd="+"
        swapmod= self.mod
        if self.mod < 0:
            strAdd= "-"
            swapmod= -self.mod
        modSum = self.sum()

        # build output string
        myStr = " (" + str(modSum) + ")"
        myStr += " vs [" + str(self.sk) + strAdd + str(swapmod) + "]"

        if self.is_fumble():
            myStr += " <b><font color=red>Fumble!</font>  POW Cost: [" + str(self.pow) + "],</b> " + fum_string
        elif self.is_critical():
            myStr += " <b><font color=green>Critical!</font></b> POW Cost: [1] "
        elif self.is_special():
            myStr += " <i><font color=green>Special!</font></i> POW Cost: [" + str(special_pow) + "] "
        elif self.is_success():
            myStr += " <font color=blue>Success!</font> POW Cost: [" + str(self.pow) + "] "
        else:
            myStr += " <font color=red>Failure!</font> POW Cost: [1]"

        # print spell details
        myStr += "<br /> --- Other Modifiers:["    + str( extra_mod     ) + "], "
        myStr += "Extra POW:[" + str( extra_pow     ) + "], "
        myStr += "Ceremony:[+"          + str( ceremony_roll ) + "%], "
        myStr += "Intensity(-3):["      + str( self.int      ) + "], "
        myStr += "Accelerate(-5):["     + str( self.acc      ) + "], "
        myStr += "Multispell(-10):["    + str( self.mlt      ) + "] ---"
        return myStr

