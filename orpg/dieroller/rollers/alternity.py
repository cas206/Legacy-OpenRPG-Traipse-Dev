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
# File: Alternity.py
# Version:
#   $Id: Alternity.py,v .1 JEC (cchriss@thecastle.com)
#
# Description: Alternity die roller based on Posterboy's D20 Dieroller
#
# Changelog:
#
# v.1 original release JEC
#
# Traipse Release: 
# The changes made in the Traipe release are intended to create a more direct connection
# between the source and the intrepretor. IF, ELIF statements have been replaced with dictionaries,
# unused objects have been replace with re-usable objects, and the code has been condensed.


import re

from std import std
from time import time, clock
from orpg.dieroller.base import di, die_base, die_rollers

__version__ = "$Id: alternity.py,v 0.1 2003/01/02 12:00:00 cchriss Exp $"

# Alternity stands for "Alternity system" 20 sided die plus mods

class alternity(std):
    name = "alternity" # ADDED by SEG Nov 2009 ***
    
    def __init__(self,source=[]):
        std.__init__(self,source)

    # these methods return new die objects for specific options
    def sk(self,score,mod):
      return sk(self,score,mod)

    def at(self,score,mod,dmgo,dmgg,dmga):
      return at(self,score,mod,dmgo,dmgg,dmga)

die_rollers.register(alternity)

class sk(std):
    def __init__(self,source=[],sc="10/5/2",mod=0):
        std.__init__(self,source)
        m = re.match( r"\d+", str(sc) )
        self.score = int( m.group(0) )
        self.mod = mod

    def getMod(self,mod=0):
        m=0
        mods = { -4: -di(12), -3: -di(8), -2:  -di(6), -1: -di(4), 1: -di(4),
                2: di(6), 3: di(8), 4: di(12), 5: di(20)}
        if mod in mods.keys(): m = mods[mod].value
        elif mod <= -5: m=-di(20).value
        elif mod == 6:  m=di(20).value + di(20).value
        elif mod >= 7:  m=di(20).value + di(20).value + di(20).value
        return m

    def getRolLStr(self):
        myStr = "[" + str(self.data[0])
        self.d20 = self.sum()
        amod = self.getMod(self.mod)
        self.dieRoll = self.d20 + amod
        for a in self.data[1:]:
            myStr += ","
            myStr += str(a)
        myStr += "," + str(amod) + "] = (" + str(self.dieRoll) + ")"
        if ( self.d20 == 1 ): self.success = 'CS'
        if ( self.dieRoll <= self.score / 4 ): self.success = 'A'
        elif ( self.dieRoll <= self.score / 2 ): self.success = 'G'
        elif ( self.dieRoll <= self.score ): self.success = 'O'
        else: self.success = 'F'
        if ( self.d20 == 20 ): self.success = 'CF'
        return myStr

    def __str__(self):
        myStr = self.getRolLStr()
        successes = {'CS': " <b><font color='#00aa00'>CRITICAL SUCCESS</font></b>",
                    'CF': " <b><font color='#ff0000'>CRITICAL FAILURE</font></b>",
                    'A': " <b>AMAZING Success</b>",
                    'G': " <b>Good Success</b>",
                    'O': " <b>Ordinary Success</b>",
                    'F': " <b>failure</b>"}
        myStr += successes[self.success]
        return myStr

class at(sk):
    ## Traipse Usage: The source I received had the damage rolls like this 1d6s, with the damage type a
    ## letter that could be sliced from the roll. However, the roll is parsed before the letter can be
    ## sliced from it, and with the letter attached it created an error.
    ##
    ## The Traipse method puts the damage type and the damage roll into a Tuple, ie (1d6, 's').
    ## When uing this method you must include single or double quoutes around the damage type or the
    ## software will treat it as an object.
    def __init__(self,source=[],sc=10, mod=0, dmgo="(1d6, 's')",dmgg="(1d6, 'w')",dmga="(1d6, 'm')"):
        sk.__init__(self,source,sc,mod)
        self.dmgo = dmgo
        self.dmgg = dmgg
        self.dmga = dmga

    def getdmg(self,dmgroll):
        astr = "===> Damage "
        droll = str(dmgroll[0])
        dtype = dmgroll[1]
        astr += droll
        if dtype=="s": astr += " stun"
        elif dtype=="w": astr += " wound"
        elif dtype=="m":astr += " mortal"
        return astr

    def __str__(self):
        myStr = self.getRolLStr()
        successes = {'CS': " <b><font color='#00aa00'>CRITICAL SUCCESS</font></b>",
                    'CF': " <b><font color='#ff0000'>CRITICAL FAILURE</font></b>",
                    'A': " <b><font color='#00aa00'>AMAZING HIT</font></b> ",
                    'G': " <b>Good HIT</b> ",
                    'O': " <b>Ordinary HIT</b> ",
                    'F': " <b>miss</b>"}
        myStr += successes[self.success]
        if self.success == 'A': myStr += self.getdmg(self.dmga)
        elif self.success == 'G': myStr += self.getdmg(self.dmgg)
        elif self.success == 'O': myStr += self.getdmg(self.dmgo)
        return myStr

