from orpg.dieroller.base import die_base, die_rollers

class std(die_base):
    name = "std"

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

die_rollers.register(std)
