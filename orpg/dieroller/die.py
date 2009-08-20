#!/usr/bin/env python
# Copyright (C) 2000-2001 The OpenRPG Project
#
#        openrpg-dev@lists.sourceforge.net
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
# File: die.py
# Author: Andrew Bennett
# Maintainer:
# Version:
#   $Id: die.py,v 1.13 2007/03/13 17:53:42 digitalxero Exp $
#
# Description: This class is used to make working with dice easier
#

__version__ = "$Id: die.py,v 1.13 2007/03/13 17:53:42 digitalxero Exp $"


import random
import UserList
import copy
#import string

class die_base(UserList.UserList):

    
    def __init__(self,source = []):
        if isinstance(source, (int, float, basestring)):
            s = []
            s.append(di(source))
        else:
            s = source
        UserList.UserList.__init__(self,s)


    
    def sum(self):
        s = 0
        for a in self.data:
            s += int(a)
        return s

    
    def __lshift__(self,other):
        if type(other) == type(3) or type(other) == type(3.0):
            o = other
        elif hasattr(other,"sum"):
            o = other.sum()
        else:
            return None

        result = []
        for die in self:
            if die < o:
                result.append(die)
        return self.__class__(result)

    
    def __rshift__(self,other):

        if type(other) == type(3) or type(other) == type(3.0):
            o = other
        elif hasattr(other,"sum"):
            o = other.sum()
        else:
            return None

        result = []
        for die in self:
            if die > o:
                result.append(die)
        return self.__class__(result)

    
    def __rlshift__(self,other):
        return self.__rshift__(other)

    
    def __rrshift__(self,other):
        return self.__lshift__(other)


    
    def __str__(self):
        if len(self.data) > 0:
            myStr = "[" + str(self.data[0])
            for a in self.data[1:]:
                myStr += ","
                myStr += str(a)
            myStr += "] = (" + str(self.sum()) + ")"
        else:
            myStr = "[] = (0)"
        return myStr

    
    def __lt__(self,other):
        if type(other) == type(3) or type(other) == type(3.0):
            return (self.sum() < other)
        elif hasattr(other,"sum"):
            return  (self.sum() < other.sum())
        else:
            return UserList.UserList.__lt__(self,other)

    
    def __le__(self,other):
        if type(other) == type(3) or type(other) == type(3.0):
            return (self.sum() <= other)
        elif hasattr(other,"sum"):
            return  (self.sum() <= other.sum())
        else:
            return UserList.UserList.__le__(self,other)

    
    def __eq__(self,other):
        if type(other) == type(3) or type(other) == type(3.0):
            return (self.sum() == other)
        elif hasattr(other,"sum"):
            return  (self.sum() == other.sum())
        else:
            return UserList.UserList.__eq__(self,other)

    
    def __ne__(self,other):
        if type(other) == type(3) or type(other) == type(3.0):
            return (self.sum() != other)
        elif hasattr(other,"sum"):
            return  (self.sum() != other.sum())
        else:
            return UserList.UserList.__ne__(self,other)

    
    def __gt__(self,other):
        if type(other) == type(3) or type(other) == type(3.0):
            return (self.sum() > other)
        elif hasattr(other,"sum"):
            return  (self.sum() > other.sum())
        else:
            return UserList.UserList.__gt__(self,other)

    
    def __ge__(self,other):
        if type(other) == type(3) or type(other) == type(3.0):
            return (self.sum() >= other)
        elif hasattr(other,"sum"):
            return  (self.sum() >= other.sum())
        else:
            return UserList.UserList.__ge__(self,other)

    
    def __cmp__(self,other):
        #  this function included for backwards compatibility
        #  As of 2.1, lists implement the "rich comparison"
        #  methods overloaded above.
        if type(other) == type(3) or type(other) == type(3.0):
            return cmp(self.sum(), other)
        elif hasattr(other,"sum"):
            return  cmp(self.sum(), other.sum())
        else:
            return UserList.UserList.__cmp__(self,other)


    
    def __rcmp__(self,other):
        return self.__cmp__(other)

    
    def __add__(self,other):
        mycopy = copy.deepcopy(self)
        if type(other) == type(3) or type(other) == type(3.0):
            #if other < 0:
            #    return self.__sub__(-other)
            #other = [di(other,other)]
            other = [static_di(other)]
            #return self.sum() + other

        elif type(other) == type("test"):
            return self
        mycopy.extend(other)
        #result = UserList.UserList.__add__(mycopy,other)
        return mycopy

    
    def __iadd__(self,other):
        return self.__add__(other)

    
    def __radd__(self,other):
        mycopy = copy.deepcopy(self)
        if type(other) == type(3) or type(other) == type(3.0):
            new_die = di(0)
            new_die.set_value(other)
            other = new_die
        mycopy.insert(0,other)
        return mycopy

    
    def __int__(self):
        return self.sum()

    
    def __sub__(self,other):
        mycopy = copy.deepcopy(self)
        if type(other) == type(3) or type(other) == type(3.0):
            neg_die = static_di(-other)
            #neg_die.set_value(-other)
            other = [neg_die]
            #return self.sum() - other
        else:
            other = -other
        mycopy.extend(other)
        return mycopy

    
    def __rsub__(self,other):
        mycopy = -copy.deepcopy(self)
        #print type(other)
        if type(other) == type(3) or type(other) == type(3.0):
            new_die = di(0)
            new_die.set_value(other)
            other = new_die
        mycopy.insert(0,other)
        return mycopy

    
    def __isub__(self,other):
        return self.__sub__(other)

    
    def __mul__(self,other):
        if type(other) == type(3) or type(other) == type(3.0):
            return self.sum() * other
        elif hasattr(other,"sum"):
            return other.sum() * self.sum()
        else:
            return UserList.UserList.__mul__(self,other)

    
    def __rmul__(self,other):
        return self.__mul__(other)

    
    def __div__(self,other):
        if type(other) == type(3) or type(other) == type(3.0):
            return float(self.sum()) / other
        elif hasattr(other,"sum"):
            return  float(self.sum()) / other.sum()
        else:
            return UserList.UserList.__div__(self,other)

    
    def __rdiv__(self,other):
        if type(other) == type(3) or type(other) == type(3.0):
            return other / float(self.sum())
        elif hasattr(other,"sum"):
            return  other.sum() / float(self.sum())
        else:
            return UserList.UserList.__rdiv__(self,other)

    
    def __mod__(self,other):
        if type(other) == type(3) or type(other) == type(3.0):
            return self.sum()%other
        elif hasattr(other,"sum"):
            return  self.sum() % other.sum()
        else:
            return UserList.UserList.__mod__(self,other)

    
    def __rmod__(self,other):
        if type(other) == type(3) or type(other) == type(3.0):
            return other % self.sum()
        elif hasattr(other,"sum"):
            return  other.sum() % self.sum()
        else:
            return UserList.UserList.__rmod__(self,other)

    
    def __neg__(self):
        for i in range(len(self.data)):
            self.data[i] = -self.data[i]
        return self

    
    def __pos__(self):
        for i in range(len(self.data)):
            self.data[i] = +self.data[i]
        return self

    
    def __abs__(self):
        for i in range(len(self.data)):
            self.data[i] = abs(self.data[i])
        return self
        #return abs(self.sum())

    
    def __pow__(self,other):
        if type(other) == type(3) or type(other) == type(3.0):
            return self.sum() ** other
        elif hasattr(other,"sum"):
            return  self.sum() ** other.sum()
        else:
            return UserList.UserList.__pow__(self,other)


    
    def __rpow__(self,other):
        #  We're overloading exponentiation of ints to create "other" number of dice

        if other >= 1:
            result = self.__class__(self[0].sides)
            for t in range(other-1):
                result+=self.__class__(self[0].sides)
        else:
            result = None

        return result

### di class to handle actual dice

class di:
    
    def __init__(self,sides,min=1):
        self.sides = sides
        self.history = None
        self.value = None
        self.target = None
        self.roll(min)

    
    def __str__(self):
        if len(self.history) > 1:
            return str(self.history)
        else:
            return str(self.value)

    
    def __neg__(self):
        self.value = -self.value
        for i in range(len(self.history)):
            self.history[i] = -self.history[i]
        return self

    
    def __pos__(self):
        self.value = +self.value
        for i in range(len(self.history)):
            self.history[i] = +self.history[i]
        return self

    
    def __abs__(self):
        self.value = abs(self.value)
        for i in range(len(self.history)):
            self.history[i] = abs(self.history[i])
        return self

    
    def __repr__(self):
        if len(self.history) > 1:
            return str(self.history)
        else:
            return str(self.value)

    
    def __int__(self):
        return self.value


    
    def __lt__(self,other):
        if type(other) == type(3) or type(other) == type(3.0):
            return self.value < other
        elif hasattr(other,"value"):
            return self.value < other.value
        else:
            return self < other

    
    def __le__(self,other):
        if type(other) == type(3) or type(other) == type(3.0):
            return self.value <= other
        elif hasattr(other,"value"):
            return self.value <= other.value
        else:
            return self <= other

    
    def __eq__(self,other):
        if type(other) == type(3) or type(other) == type(3.0):
            return self.value == other
        elif hasattr(other,"value"):
            return self.value == other.value
        else:
            return self == other

    
    def __ne__(self,other):
        if type(other) == type(3) or type(other) == type(3.0):
            return self.value != other
        elif hasattr(other,"value"):
            return self.value != other.value
        else:
            return self != other

    
    def __gt__(self,other):
        if type(other) == type(3) or type(other) == type(3.0):
            return self.value > other
        elif hasattr(other,"value"):
            return self.value > other.value
        else:
            return self > other

    
    def __ge__(self,other):
        if type(other) == type(3) or type(other) == type(3.0):
            return self.value >= other
        elif hasattr(other,"value"):
            return self.value >= other.value
        else:
            return self >= other

    
    def __cmp__(self,other):
        #  this function included for backwards compatibility
        #  As of 2.1, lists implement the "rich comparison"
        #  methods overloaded above.
        if type(other) == type(3) or type(other) == type(3.0):
            return cmp(self.value, other)
        elif hasattr(other,"value"):
            return cmp(self.value, other.value)
        else:
            return cmp(self,other)

    
    def roll(self,min=1):
        if isinstance(self.sides, basestring) and self.sides.lower() == 'f':
            self.value = random.randint(-1, 1)
        else:
            #self.value = random.randint(min, self.sides)
            self.value = int(random.uniform(min, self.sides+1))
        self.history = []
        self.history.append(self.value)

    
    def extraroll(self):
        if isinstance(self.sides, basestring) and self.sides.lower() == 'f':
            result = random.randint(-1, 1)
        else:
            #result = random.randint(1, self.sides)
            result = int(random.uniform(1,self.sides+1))

        self.value += result
        self.history.append(result)

    
    def lastroll(self):
        return self.history[len(self.history)-1]

    
    def set_value(self,value):
        self.value = value
        self.history = []
        self.history.append(self.value)

    
    def modify(self,mod):
        self.value += mod
        self.history.append(mod)

    
    def gethistory(self):
        return self.history[:]

class static_di(di):
    
    def __init__(self,value):
        di.__init__(self,value,value)
        self.set_value(value)


class std(die_base):
    
    def __init__(self,source=[]):
        die_base.__init__(self,source)

    #  Examples of adding member functions through inheritance.

    
    def ascending(self):
        result = self[:]
        result.sort()
        return result

    
    def descending(self):
        result = self[:]
        result.sort()
        result.reverse()
        return result

    
    def takeHighest(self,num_dice):
        return self.descending()[:num_dice]

    
    def takeLowest(self,num_dice):
        return self.ascending()[:num_dice]

    
    def extra(self,num):
        for i in range(len(self.data)):
            if self.data[i].lastroll() >= num:
                self.data[i].extraroll()
        return self

    
    def open(self,num):
        if num <= 1:
            self
        done = 1
        for i in range(len(self.data)):
            if self.data[i].lastroll() >= num:
                self.data[i].extraroll()
                done = 0
        if done:
            return self
        else:
            return self.open(num)

    
    def minroll(self,min):
        for i in range(len(self.data)):
            if self.data[i].lastroll() < min:
                self.data[i].roll(min)
        return self

    
    def each(self,mod):
        mod = int(mod)
        for i in range(len(self.data)):
            self.data[i].modify(mod)
        return self


    
    def vs(self, target):
        for dn in self.data:
            dn.target = target
        return self


    ## If we are testing against a saving throw, we check for
    ## greater than or equal to against the target value and
    ## we only return the number of successful saves.  A negative
    ## value will never be generated.
    
    def sum(self):
        retValue = 0
        for dn in self.data:
            setValue = reduce( lambda x, y : int(x)+int(y), dn.history )
            if dn.target:
                if setValue >= dn.target:
                    retValue += 1

            else:
                retValue += setValue

        return retValue
