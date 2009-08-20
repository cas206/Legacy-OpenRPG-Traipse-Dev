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
# File: Hero.py
# Version:
#   $Id: Hero.py,v .3 DJM & Heroman
#
# Description: Hero System die roller originally based on Posterboy's D20 Dieroller
#
# Changelog:
# v.3 by Heroman
# Added hl() to show hit location (+side), and hk() for Hit Location killing damage
# (No random stun multiplier)
# v.2 DJM
# Removed useless modifiers from the Normal damage roller
# Changed Combat Value roller and SKill roller so that positive numbers are bonuses,
# negative numbers are penalties
# Changed Killing damage roller to correct stun multiplier bug
# Handled new rounding issues
#
# v.1 original release DJM

from die import *
from time import time, clock
import random

__version__ = "$Id: hero.py,v 1.15 2006/11/04 21:24:19 digitalxero Exp $"

# Hero stands for "Hero system" not 20 sided die :)

class hero(std):
    
    def __init__(self,source=[]):
        std.__init__(self,source)

# these methods return new die objects for specific options

    
    def k(self,mod):
        return herok(self,mod)

    
    def hl(self):
        return herohl(self)

    
    def hk(self):
        return herohk(self)

    
    def n(self):
        return heron(self)

    
    def cv(self,cv,mod):
        return herocv(self,cv,mod)

    
    def sk(self,sk,mod):
        return herosk(self,sk,mod)

class herocv(std):
    
    def __init__(self,source=[],cv=10,mod=0):
        std.__init__(self,source)
        self.cv = cv
        self.mod = mod


    
    def __str__(self):
        myStr = "[" + str(self.data[0])
        for a in self.data[1:]:
            myStr += ","
            myStr += str(a)
        myStr += "] = (" + str(self.sum()) + ")"

        myStr += " with a CV of " + str(self.cv)
        myStr += " and a modifier of " + str(self.mod)
        cvhit = 11 + self.cv - self.sum() + self.mod
        myStr += " hits up to <b>DCV <font color='#ff0000'>" + str(cvhit) + "</font></b>"
        return myStr

class herosk(std):
    
    def __init__(self,source=[],sk=11,mod=0):
        std.__init__(self,source)
        self.sk = sk
        self.mod = mod

    
    def is_success(self):
        return (((self.sum()-self.mod) <= self.sk))

    
    def __str__(self):
        myStr = "[" + str(self.data[0])
        for a in self.data[1:]:
            myStr += ","
            myStr += str(a)
        strAdd="] - "
        swapmod=self.mod
        if self.mod < 0:
            strAdd= "] + "
            swapmod= -self.mod
        myStr += strAdd + str(swapmod)
        modSum = self.sum()-self.mod
        myStr += " = (" + str(modSum) + ")"
        myStr += " vs " + str(self.sk)

        if self.is_success():
            myStr += " or less <font color='#ff0000'>Success!"
        else:
            myStr += " or less <font color='#ff0000'>Failure!"

        Diff = self.sk - modSum
        myStr += " by " + str(Diff) +" </font>"

        return myStr

class herok(std):
    
    def __init__(self,source=[],mod=0):
        std.__init__(self,source)
        self.mod = mod

    
    def __str__(self):
        myStr = "[" + str(self.data[0])
        for a in self.data[1:]:
            myStr += ","
            myStr += str(a)
        myStr += "] = (<font color='#ff0000'><b>" + str(int(round(self.sum()))) + "</b></font>)"
        stunx = random.randint(1,6)-1
        if stunx <= 1:
            stunx = 1
        myStr += " <b>Body</b> and a stunx of (" + str(stunx)
        stunx = stunx + self.mod
        myStr += " + " + str(self.mod)
        stunsum = round(self.sum()) * stunx
        myStr += ") for a total of (<font color='#ff0000'><b>" + str(int(stunsum)) + "</b></font>) <b>Stun</b>"
        return myStr

class herohl(std):
    
    def __init__(self,source=[],mod=0):
        std.__init__(self,source)
        self.mod = mod

    
    def __str__(self):
        myStr = "[" + str(self.data[0])
        side = random.randint(1,6)
        sidestr = "Left "
        if side >=4:
            sidestr = "Right "
        for a in self.data[1:]:
            myStr += ","
            myStr += str(a)
        myStr += "] = (<font color='#ff0000'><b>" + str(int(round(self.sum()))) + "</b></font>) "
        location = int(round(self.sum()))
        if location <= 5:
            myStr += "Location: <B>Head</B>, StunX:<B>x5</B>, NStun:<B>x2</B>, Bodyx:<B>x2</B>"
        elif location == 6:
            myStr += "Location: <B>" + sidestr + "Hand</B>, StunX:<B>x1</B>, NStun:<B>x1/2</B>, Bodyx:<B>x1/2</B>"
        elif location == 7:
            myStr += "Location: <B>" + sidestr + "Arm</B>, StunX:<B>x2</B>, NStun:<B>x1/2</B>, Bodyx:<B>x1/2</B>"
        elif location == 8:
            myStr += "Location: <B>" + sidestr + "Arm</B>, StunX:<B>x2</B>, NStun:<B>x1/2</B>, Bodyx:<B>x1/2</B>"
        elif location == 9:
            myStr += "Location: <B>" + sidestr + "Shoulder</B>, StunX:<B>x3</B>, NStun:<B>x1</B>, Bodyx:<B>x1</B>"
        elif location == 10:
            myStr += "Location: <B>Chest</B>, StunX:<B>x3</B>, NStun:<B>x1</B>, Bodyx:<B>x1</B>"
        elif location == 11:
            myStr += "Location: <B>Chest</B>, StunX:<B>x3</B>, NStun:<B>x1</B>, Bodyx:<B>x1</B>"
        elif location == 12:
            myStr += "Location: <B>Stomach</B>, StunX:<B>x4</B>, NStun:<B>x1 1/2</B>, Bodyx:<B>x1</B>"
        elif location == 13:
            myStr += "Location: <B>Vitals</B>, StunX:<B>x4</B>, NStun:<B>x1 1/2</B>, Bodyx:<B>x2</B>"
        elif location == 14:
            myStr += "Location: <B>" + sidestr + "Thigh</B>, StunX:<B>x2</B>, NStun:<B>x1</B>, Bodyx:<B>x1</B>"
        elif location == 15:
            myStr += "Location: <B>" + sidestr + "Leg</B>, StunX:<B>x2</B>, NStun:<B>x1/2</B>, Bodyx:<B>x1/2</B>"
        elif location == 16:
            myStr += "Location: <B>" + sidestr + "Leg</B>, StunX:<B>x2</B>, NStun:<B>x1/2</B>, Bodyx:<B>x1/2</B>"
        elif location >= 17:
            myStr += "Location: <B>" + sidestr + "Foot</B>, StunX:<B>x1</B>, NStun:<B>x1/2</B>, Bodyx:<B>x1/2</B>"
        return myStr

class herohk(std):
    
    def __init__(self,source=[],mod=0):
        std.__init__(self,source)
        self.mod = mod

    
    def __str__(self):
        myStr = "[" + str(self.data[0])
        for a in self.data[1:]:
            myStr += ","
            myStr += str(a)
        myStr += "] = (<font color='#ff0000'><b>" + str(int(round(self.sum()))) + "</b></font>)"
        stunx = 1
        myStr += " <b>Body</b> "
        stunx = stunx + self.mod
        stunsum = round(self.sum()) * stunx
        myStr += " for a total of (<font color='#ff0000'><b>" + str(int(stunsum)) + "</b></font>) <b>Stun</b>"
        return myStr

class heron(std):
    
    def __init__(self,source=[],mod=0):
        std.__init__(self,source)
        self.bodtot=0

    
    def __str__(self):
        myStr = "[" + str(self.data[0])
        if self.data[0] == 6:
            self.bodtot=self.bodtot+2
        else:
            self.bodtot=self.bodtot+1
        if self.data[0] <= 1:
            self.bodtot=self.bodtot-1
        for a in self.data[1:]:
            myStr += ","
            myStr += str(a)
            if a == 6:
                self.bodtot=self.bodtot+2
            else:
                self.bodtot=self.bodtot+1
            if a <= 1:
                self.bodtot=self.bodtot-1
        myStr += "] = (<font color='#ff0000'><b>" + str(self.bodtot) + "</b></font>)"
        myStr += " <b>Body</b> and "
        myStr += "(<font color='#ff0000'><b>" + str(int(round(self.sum()))) + "</b></font>) <b>Stun</b>"
        return myStr
