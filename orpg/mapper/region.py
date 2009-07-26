# Copyright (C) 2000-2001 The OpenRPG Project
#
#    openrpg-dev@lists.sourceforge.net
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
# File: mapper/region.py
# Author: Mark Tarrabain
# Maintainer:
# Version:
#   $Id: region.py,v 1.10 2006/11/04 21:24:21 digitalxero Exp $
#
__version__ = "$Id: region.py,v 1.10 2006/11/04 21:24:21 digitalxero Exp $"

import sys

# This class manages the edge of a polygon
# it is employed by scan_convert to trace each edge of the polygon as the
# scan converter advances past each Y coordinate
# A bresenham-type of algorithm is used to avoid expensive computation during
# use - no floating point arithmetic is needed.
class Edge:
    def __init__(self,start,end):
        self.startx=start.X
        self.starty=start.Y
        self.endx=end.X
        self.endy=end.Y
        self.dy=self.endy-self.starty
        self.cx=self.startx
        self.bottom=0
        self.dir = 0
        if self.endx>self.startx: self.dx = int((self.endx-self.startx)/self.dy)
        else: self.dx = -int((self.startx-self.endx)/self.dy)
        self.error = 0
        if self.endx >= self.startx: self.inc = (self.endx-self.startx)%self.dy
        else: self.inc = (self.startx-self.endx)%self.dy

    def advance(self):
        self.cx += self.dx
        self.error += self.inc
        if (self.error>=self.dy):
            if (self.endx<self.startx): self.cx -= 1
            else: self.cx += 1
            self.error -= self.dy

# Utilitarian class for describing a coordinate in 2D space
class IPoint:
    def __init__(self):
        X=0
        Y=0

    def __str__(self):
        return "(X:" + str(self.X) + ", Y:" + str(self.Y) + ")"

    def pluseq(self,b):
        self.X += b.X
        self.Y += b.Y

    def minuseq(self,b):
        self.X -= b.X
        self.Y -= b.Y

    def make(self,x,y):
        self.X=x
        self.Y=y
        return self

    def equals(self,b):
        if self.X==b.X and self.Y==b.Y: return 1
        return 0

    def less(self,b):
        if self.Y<b.Y or (self.Y==b.Y and self.X<b.X): return 1
        return 0

    def greater(self,b):
        if self.Y>b.Y or (self.Y==b.Y and self.X>b.X): return 1
        return 0

# generic rectangle class
class IRect:
    def __init__(self): #initializes to an invalid rectangle
        self.left=999999
        self.top=999999
        self.right=-999999
        self.bottom=-999999

    def __str__(self):
        return "[ left:"+str(self.left)+", top:"+str(self.top)+", right:"+str(self.right)+", bottom:"+str(self.bottom)+" ]"

    def ToPoly(self):
        thelist = []
        thelist.append(IPoint().make(self.left,self.top))
        thelist.append(IPoint().make(self.right,self.top))
        thelist.append(IPoint().make(self.right,self.bottom))
        thelist.append(IPoint().make(self.left,self.bottom))
        return thelist

    def Width(self):
        return self.right-self.left+1

    def Height(self):
        return self.bottom-self.top+1

    def GetX(self):
        return self.left

    def GetY(self):
        return self.top

    def GetW(self):
        return self.right-self.left+1

    def GetH(self):
        return self.bottom-self.top+1

    def Size(self):
        return IPoint().make(self.right-self.left+1,self.bottom-self.top+1)

    def TopLeft(self):
        return IPoint().make(self.left,self.top)

    def BottomRight(self):
        return IPoint().make(self.right,self.bottom)

    def Bounds(self):
        return IRect().make(0,0,self.right-self.left,self.bottom-self.top)

    def Resize(self,nL,nT,nR,nB):
        self.left+=nL
        self.top+=nT
        self.right+=nR
        sel.bottom+=nB

    def IsValid(self):
        if (self.left<=self.right and self.top<=self.bottom): return 1
        return 0

    def add(self,pt):
        return IRect().make(self.left+pt.X,self.top+pt.Y,self.right+pt.X,self.bottom+pt.Y)

    def subtract(self,pt):
        return IRect().make(self.left+pt.X,self.top+pt.Y,self.right+pt.X,self.bottom+pt.Y)

    def intersect(self,rect):
        return IRect().make(max(self.left,rect.left),max(self.top,rect.top),min(self.right,rect.right),min(self.bottom,rect.bottom))

    def union(self,rect):
        return IRect().make(min(self.left,rect.left),min(self.top,rect.top),max(self.right,rect.right),max(self.bottom,rect.bottom))

    def equals(self,rect):
        if (self.top==rect.top and self.bottom==rect.bottom and self.left==rect.left and self.right==rect.right): return 1
        return 0

    def make(self,l,t,r,b):
        self.left=l
        self.right=r
        self.top=t
        self.bottom=b
        return self

# A span is a single, contiguous horizontal line.  The routine scan_convert
# returns a list of these that describe the polygon
class ISpan:
    def __init__(self,x1,x2,ypos):
        self.left=x1
        self.right=x2
        self.y=ypos

    def __str__(self):
        return "(" + str(self.left) + " to " + str(self.right) + " at " + str(self.y) + ")"

# clipping rectangle class -- this class is a single node in a linked list
# of rectangles that describe a region

class ClipRect:
    def __init__(self):
        self.next=None
        self.prev=None
        self.bounds=IRect().make(0,0,0,0)


# cliprectlist -- the container class that manages a list of cliprects
class ClipRectList:
    def __init__(self):
        self.first=None
        self.last=None
        self.count=0

    def __str__(self):
        x="["
        for y in self.GetList(): x+=" "+str(y.bounds)+" "
        x+="]"
        return x

#remove all rectangles from list
    def Clear(self):
        while(self.first):
            rect=self.first
            self.first=self.first.next
            del rect
        self.last=None
        self.count=0

#add a new clipping rectangle to list
    def AddRect(self,rect):
        rect.prev=None
        rect.next=self.first
        if not (self.first is None): self.first.prev=rect
        self.first=rect
        if self.last is None: self.last=rect
        self.count += 1

#removes the passed clipping rectangle from the list
    def RemoveRect(self,rect):
        if not (rect.prev is None): rect.prev.next=rect.next
        else: self.first=rect.next
        if not (rect.next is None): rect.next.prev=rect.prev
        else: self.last=rect.prev
        self.count -= 1

# find the clipping rectangle at the the beginning of the list, remove it,
# and return it
    def RemoveHead(self):
        if self.count==0: return None
        rect=self.first
        self.first=rect.next
        if (self.first is None): self.last=None
        self.count -= 1
        return rect

# stealrects -- appends the list of clipping rectangles in pclist to the current
# list.  removes the entries from pclist
    def StealRects(self,pclist):
        if pclist.first is None: return
        if self.first is None:
            self.first=pclist.first
            self.last=pclist.last
        else:
            self.last.next=pclist.first
            pclist.first.prev=self.last
            self.last=pclist.last
        self.count += pclist.count
        pclist.first = None
        pclist.last = None
        pclist.count = 0

# utilitarian procedure to return all clipping rectangles as a Python list
    def GetList(self):
        result=[]
        f = self.first
        while f:
            result.append(f)
            f = f.next
        return result

# some utility procedures, defined outside the scope of any class to ensure
# efficiency

def _hSortCmp(rect1,rect2):
    if (rect1.bounds.left<rect2.bounds.left): return -1
    if (rect1.bounds.left>rect2.bounds.left): return 1
    if (rect1.bounds.top<rect2.bounds.top): return -1
    if (rect1.bounds.top>rect2.bounds.top): return 1
    return 0

def _vSortCmp(rect1,rect2):
    if (rect1.bounds.top<rect2.bounds.top): return -1
    if (rect1.bounds.top>rect2.bounds.top): return 1
    if (rect1.bounds.left<rect2.bounds.left): return -1
    if (rect1.bounds.left>rect2.bounds.left): return 1
    return 0

# this is the class for which this whole source file is designed!
# a Region is maintained as an optimal set of non-intersecting rectangles
# whose union is the 2D area of interest.  At the end of each of the public
# procedures that may alter the region's structure, the set of rectangles is
# passed through an optimization phase, that joins any rectangles that are found
# to be adjacent and can be combined into a single, larger rectangle

class IRegion:
    def __init__(self):
        self.crects=ClipRectList()
        self.firstclip=None

    def __AllocClipRect(self):
        return ClipRect()

    def __FreeClipRect(self,p):
        del p

    def Clear(self):
        self.crects.Clear()

    def isEmpty(self):
        if self.crects.first: return 0
        return 1

    def Copy(self,dest):
        dest.Clear()
        p=self.crects.first
        while p:
            dest.__AddRect(p.bounds)
            p=p.next

    def __AddRect(self,rect):
        cr=self.__AllocClipRect()
        cr.bounds=IRect().make(rect.left,rect.top,rect.right,rect.bottom)
        self.crects.AddRect(cr)
        return cr

# This is the magic procedure that always makes it possible to merge adjacent
# rectangles later.   It is called once for each rectangle to be combined
# with the current region.  Basically, it dices the current region into
# horizontal bands where any rectangle is found to be beside the one being
# examined.  This tends to leave more rectangles than necessary in the region,
# but they can be culled during the optimization phase when they are combined
# with adjacent rectangles.

    def __Examine(self,rect):
        newlist = ClipRectList()
        while not (self.crects.first is None):
            p = self.crects.RemoveHead()
            if (p.bounds.right+1==rect.left or p.bounds.left==rect.right+1):
                if (p.bounds.top<rect.top and p.bounds.bottom>rect.bottom):
                    cnew=[IRect().make(p.bounds.left,p.bounds.top,p.bounds.right,rect.top-1),
                          IRect().make(p.bounds.left,rect.top,p.bounds.right,rect.bottom),
                          IRect().make(p.bounds.left,rect.bottom+1,p.bounds.right,p.bounds.bottom)]
                elif (p.bounds.top<rect.top and p.bounds.bottom>rect.top):
                    cnew=[IRect().make(p.bounds.left,p.bounds.top,p.bounds.right,rect.top-1),
                          IRect().make(p.bounds.left,rect.top,p.bounds.right,p.bounds.bottom)]
                elif (p.bounds.top<rect.bottom and p.bounds.bottom>rect.bottom):
                    cnew=[IRect().make(p.bounds.left,p.bounds.top,p.bounds.right,rect.bottom),
                          IRect().make(p.bounds.left,rect.bottom+1,p.bounds.right,p.bounds.bottom)]
                else:
                    cnew=[IRect().make(p.bounds.left,p.bounds.top,p.bounds.right,p.bounds.bottom)]
                self.__FreeClipRect(p)
                for i in cnew:
                    if (i.IsValid()):
                        newclip=self.__AllocClipRect()
                        newclip.bounds=i
                        newlist.AddRect(newclip)
            else: newlist.AddRect(p)
        self.crects.StealRects(newlist)

    def __IncludeRect(self,rect):
        tmprg=IRegion()
        tmprg.__AddRect(rect)
        p = self.crects.first
        while p:
            tmprg.__ExcludeRect(p.bounds)
            p = p.next
        self.crects.StealRects(tmprg.crects)

    def IncludeRect(self,rect):
        tmprg = IRegion()
        tmprg.Clear()
        tmprg.__AddRect(rect)
        self.__Examine(rect)
        p= self.crects.first
        while p:
            tmprg.__Examine(p.bounds)
            p=p.next
        p=tmprg.crects.first
        while p:
            self.__IncludeRect(p.bounds)
            p=p.next
        self.Optimize()

    def IncludeRegion(self,regn):
        tmprg = IRegion()
        regn.Copy(tmprg)
        p = self.crects.first
        while p:
            tmprg.__Examine(p.bounds)
            p=p.next
        p = tmprg.crects.first
        while p:
            self.__Examine(p.bounds)
            self.__IncludeRect(p.bounds)
            p = p.next
        self.Optimize()

    def __ExcludeRect(self,rect):
        newlist=ClipRectList()
        while not (self.crects.first is None):
            pcclip=self.crects.RemoveHead()
            hide=rect.intersect(pcclip.bounds)
            if not hide.IsValid(): newlist.AddRect(pcclip)
            else:
                #make 4 new rectangles to replace the one taken out
                #
                # AAAAAAAAAAAA
                # AAAAAAAAAAAA
                # BBBB    CCCC
                # BBBB    CCCC
                # DDDDDDDDDDDD
                # DDDDDDDDDDDD
                # the center rectangle is the one to remove, rectangles A,B,C and D
                # get created.  If the rectangle is not in the middle, then the
                # corresponding rectangle that should have been on "that side" of
                # the current rectangle will have IsValid==False, so it will be
                # rejected.
                cnew=[IRect().make(pcclip.bounds.left,hide.top,hide.left-1,hide.bottom),
                      IRect().make(hide.right+1,hide.top,pcclip.bounds.right,hide.bottom),
                      IRect().make(pcclip.bounds.left,hide.bottom+1,pcclip.bounds.right,pcclip.bounds.bottom),
                      IRect().make(pcclip.bounds.left,pcclip.bounds.top,pcclip.bounds.right,hide.top-1) ]
                self.__FreeClipRect(pcclip)
                for i in cnew:
                    if (i.IsValid()):
                        newclip=self.__AllocClipRect()
                        newclip.bounds=i
                        newlist.AddRect(newclip)
        self.crects.last=None
        self.crects.StealRects(newlist)
        self.Optimize()

    def ExcludeRect(self,rect):
        self.__ExcludeRect(rect)
        self.Optimize()

    def ExcludeRegion(self,reg):
        pclist = reg.crects.first
        while pclist:
            self.__ExcludeRect(pclist.bounds)
            pclist = pclist.next
        self.Optimize()

    def __IntersectRect(self,rect):
        newlist=ClipRectList()
        while not self.crects.first is None:
            pcclip=self.crects.RemoveHead()
            hide=rect.intersect(pcclip.bounds)
            if not hide.IsValid(): newlist.AddRect(pcclip)
            else:
                cnew=[IRect().make(pcclip.bounds.left,hide.top,hide.left-1,hide.bottom),
                      IRect().make(hide.right+1,hide.top,pcclip.bounds.right,hide.bottom),
                      IRect().make(pcclip.bounds.left,hide.bottom+1,pcclip.bounds.right,pcclip.bounds.bottom),
                      IRect().make(pcclip.bounds.left,pcclip.bounds.top,pcclip.bounds.right,hide.top-1) ]
                self.__FreeClipRect(pcclip)
                for i in cnew:
                    if (i.IsValid()):
                        newclip=self.__AllocClipRect()
                        newclip.bounds=i
                        newlist.AddRect(newclip)
        self.crects.last = None
        self.crects.StealRects(newlist)

    def IntersectRect(self,rect):
        self.__IntersectRect(rect)
        self.Optimize()

    def IntersectRegion(self,reg):
        clist=ClipRectList()
        pcvclip = reg.crects.first
        while pcvclip:
            pchclip = self.crects.first
            while pchclip:
                crect=pcvclip.bounds.intersect(pchclip.bounds)
                if crect.IsValid():
                    newclip=self.__AllocClipRect()
                    newclip.bounds=crect
                    clist.AddRect(newclip)
                pchclip = pchclip.next
            pcvclip = pcvclip.next
        self.Clear()
        self.crects.StealRects(clist)
        self.Optimize()

    def GetBounds(self):
        bounds=IRect()
        pcclip = self.crects.first
        while pcclip:
            bounds=bounds.union(pcclip.bounds)
            pcclip = pcclip.next
        return bounds

    def Optimize(self):
        clist=self.crects.GetList()
        removed=[]
        keepgoing = 1
        while len(clist)>1 and keepgoing:
            keepgoing=0
            clist.sort(lambda a,b:_vSortCmp(a,b))
            keys=range(len(clist)-1)
            keys.reverse()
            for i in keys:
                if (clist[i].bounds.right==clist[i+1].bounds.left-1 and
                    clist[i].bounds.top==clist[i+1].bounds.top and
                    clist[i].bounds.bottom==clist[i+1].bounds.bottom):
                    clist[i].bounds.right=clist[i+1].bounds.right
                    x=clist[i+1]
                    del clist[i+1]
                    self.crects.RemoveRect(x)
                    self.__FreeClipRect(x)
                    keepgoing=1
            if len(clist)<=1: break
            clist.sort(lambda a,b:_hSortCmp(a,b))
            keys=range(len(clist)-1)
            keys.reverse()
            for i in keys:
                if (clist[i].bounds.bottom==clist[i+1].bounds.top-1 and
                    clist[i].bounds.left==clist[i+1].bounds.left and
                    clist[i].bounds.right==clist[i+1].bounds.right):
                    clist[i].bounds.bottom=clist[i+1].bounds.bottom
                    x=clist[i+1]
                    del clist[i+1]
                    self.crects.RemoveRect(x)
                    self.__FreeClipRect(x)
                    keepgoing=1

    def FromPolygon(self,polypt,mode):
        thelist=self.scan_Convert(polypt)
        for i in thelist:
            r=IRect().make(i.left,i.y,i.right,i.y)
            if mode:
                self.__Examine(r)
                self.__IncludeRect(r)
            else: self.__ExcludeRect(r)
        self.Optimize()

    def GetRectList(self):
        result=[]
        i = self.crects.first
        while i:
            result.append(i.bounds)
            i = i.next
        return result

#Portable implementation to scan-convert a polygon
#from algoritm described in Section 3.6.3 of Foley, et al
#returns a (possibly redundant) list of spans that comprise the polygon
#this routine does not manipulate the current region in any way, but
#is enclosed in this class to isolate its name from the global namespace
#invoke via IRegion().scan_Convert(polypt)

    def scan_Convert(self,polypt):
        result=[]
        ET = {}  # edge table
        i = 0
        size = len(polypt)
        polylines=[] # list of lines in polygon
        y = -1
        for i in xrange(size):
            n = (i+1) % size
            if polypt[i].Y < polypt[n].Y:
                e = Edge(polypt[i],polypt[n])
                e.dir = 1 #moving top to bottom
                polylines.append(e)
            elif polypt[i].Y > polypt[n].Y:
                e = Edge(polypt[n],polypt[i])
                e.dir = -1 #moving bottom to top
                polylines.append(e)
            elif polypt[i].X != polypt[n].X:  # any horizontal lines just get added directly
                sx = min(polypt[i].X,polypt[n].X)
                ex = max(polypt[i].X,polypt[n].X)
                result.append(ISpan(sx,ex,polypt[i].Y))
        size = len(polylines)
        for i in xrange(size):
            if i == 0 and polylines[i].dir == -1: n = size-1
            elif (polylines[i].dir == -1): n = i-1
            else: n = (i+1) % size
            if (polylines[i].dir != polylines[n].dir): polylines[i].bottom = 1
            if i == 0 or polylines[i].starty < y: y = polylines[i].starty
            if not ET.has_key(polylines[i].starty): ET[polylines[i].starty] = []
            ET[polylines[i].starty].append(polylines[i]) #add to edge table, indexed by smaller y coordinate
        AET = [] #active edge table
        while len(AET) > 0 or len(ET) > 0:
            if ET.has_key(y): #if current y value has entries in edge tabe
                AET.extend(ET[y]) # add them to active edge table
                del ET[y] #and delete the entries in the edge table
            i = len(AET)-1
            vals = []
            while i >= 0:
                if (AET[i].endy == y): #if at the end of this edge's run
                    if (AET[i].bottom): #check and see if we need one more point
                        vals.append(AET[i].cx) #we do, add it
                    del AET[i] # y=end of edge, so remove it
                i -= 1
            i = 0
            while i < len(AET): # for every edge in AET
                vals.append(AET[i].cx) # add x intercept
                AET[i].advance() #and advance the edge one down
                i += 1
            vals.sort()
            i = 0
            while i < len(vals)-1:  #split vals[] array into pairs and output them
                result.append(ISpan(vals[i],vals[i+1],y))
                i += 2
            y += 1
        return result
