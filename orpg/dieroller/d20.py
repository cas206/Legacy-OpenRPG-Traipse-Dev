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
# File: d20.py
# Author: OpenRPG Dev Team
# Maintainer:
# Version:
#   $Id: d20.py,v 1.9 2006/11/04 21:24:19 digitalxero Exp $
#
# Description: d20 die roller
#
from die import *

__version__ = "$Id: d20.py,v 1.9 2006/11/04 21:24:19 digitalxero Exp $"

# d20 stands for "d20 system" not 20 sided die :)

class d20(std):
    
    def __init__(self,source=[]):
        std.__init__(self,source)

# these methods return new die objects for specific options

    
    def attack(self,AC,mod,critical):
        return d20attack(self,AC,mod,critical)

    
    def dc(self,DC,mod):
        return d20dc(self,DC,mod)

class d20dc(std):
    
    def __init__(self,source=[],DC=10,mod=0):
        std.__init__(self,source)
        self.DC = DC
        self.mod = mod
        self.append(static_di(mod))

    
    def is_success(self):
        return ((self.sum() >= self.DC or self.data[0] == 20) and self.data[0] != 1)

    
    def __str__(self):
        myStr = "[" + str(self.data[0])
        for a in self.data[1:]:
            myStr += ","
            myStr += str(a)
        myStr += "] = (" + str(self.sum()) + ")"

        myStr += " vs DC " + str(self.DC)

        if self.is_success():
            myStr += " Success!"
        else:
            myStr += " Failure!"

        return myStr


class d20attack(std):
    
    def __init__(self,source=[],AC=10,mod=0,critical=20):
        std.__init__(self,source)
        self.mod = mod
        self.critical = critical
        self.AC = AC
        self.append(static_di(mod))
        self.critical_check()

    
    def attack(AC=10,mod=0,critical=20):
        self.mod = mod
        self.critical = critical
        self.AC = AC

    
    def critical_check(self):
        self.critical_result = 0
        self.critical_roll = 0
        if self.data[0] >= self.critical and self.is_hit():
            self.critical_roll = die_base(20) + self.mod
            if self.critical_roll.sum() >= self.AC:
                self.critical_result = 1

    
    def is_critical(self):
        return self.critical_result

    
    def is_hit(self):
        return ((self.sum() >= self.AC or self.data[0] == 20) and self.data[0] != 1)

    
    def __str__(self):
        myStr = "[" + str(self.data[0])
        for a in self.data[1:]:
            myStr += ","
            myStr += str(a)
        myStr += "] = (" + str(self.sum()) + ")"

        myStr += " vs AC " + str(self.AC)

        if self.is_critical():
            myStr += " Critical"

        if self.is_hit():
            myStr += " Hit!"
        else:
            myStr += " Miss!"

        return myStr
