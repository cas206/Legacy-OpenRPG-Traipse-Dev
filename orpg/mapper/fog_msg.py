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
# File: mapper/fog_msg.py
# Author: Mark Tarrabain
# Maintainer:
# Version:
#   $Id: fog_msg.py,v 1.16 2006/11/04 21:24:21 digitalxero Exp $
#
__version__ = "$Id: fog_msg.py,v 1.16 2006/11/04 21:24:21 digitalxero Exp $"

from base_msg import *
from region import *
from orpg.minidom import Element
import string

class fog_msg(map_element_msg_base):

    def __init__(self,reentrant_lock_object = None):
        self.tagname = "fog"
        map_element_msg_base.__init__(self,reentrant_lock_object)
        self.use_fog = 0
        self.fogregion=IRegion()
        self.fogregion.Clear()

    def get_line(self,outline,action,output_act):
        elem = Element( "poly" )
        if ( output_act ): elem.setAttribute( "action", action )
        if ( outline == 'all' ) or ( outline == 'none' ): elem.setAttribute( "outline", outline )
        else:
            elem.setAttribute( "outline", "points" )
            for pair in string.split( outline, ";" ):
                p = string.split( pair, "," )
                point = Element( "point" )
                point.setAttribute( "x", p[ 0 ] )
                point.setAttribute( "y", p[ 1 ] )
                elem.appendChild( point )
        str = elem.toxml()
        elem.unlink()
        return str

    # convenience method to use if only this line is modified
    #   outputs a <map/> element containing only the changes to this line
    def standalone_update_text(self,update_id_string):
        buffer = "<map id='" + update_id_string + "'>"
        buffer += "<fog>"
        buffer += self.get_changed_xml()
        buffer += "</fog></map>"
        return buffer

    def get_all_xml(self,action="new",output_action=1):
        return self.toxml(action,output_action)

    def get_changed_xml(self,action="update",output_action=1):
        return self.toxml(action,output_action)

    def toxml(self,action,output_action):
        #print "fog_msg.toxml called"
        #print "use_fog :",self.use_fog
        #print "output_action :",output_action
        #print "action :",action
        if not (self.use_fog): return ""
        fog_string = ""
        if self.fogregion.isEmpty(): fog_string=self.get_line("all","del",output_action)
        for ri in self.fogregion.GetRectList():
            x1=ri.GetX()
            x2=x1+ri.GetW()-1
            y1=ri.GetY()
            y2=y1+ri.GetH()-1
            fog_string += self.get_line(str(x1)+","+str(y1)+";"+
                                         str(x2)+","+str(y1)+";"+
                                         str(x2)+","+str(y2)+";"+
                                         str(x1)+","+str(y2),action,output_action)
        s = "<fog"
        if fog_string:
            s += ">"
            s += fog_string
            s += "</fog>"
        else: s+="/>"
        return s

    def interpret_dom(self,xml_dom):
        self.use_fog=1
        #print 'fog_msg.interpret_dom called'
        children = xml_dom._get_childNodes()
        #print "children",children
        for l in children:
            action = l.getAttribute("action")
            outline = l.getAttribute("outline")
            #print "action/outline",action, outline
            if (outline=="all"):
                polyline=[]
                self.fogregion.Clear()
            elif (outline=="none"):
                polyline=[]
                self.use_fog=0
                self.fogregion.Clear()
            else:
                polyline=[]
                list = l._get_childNodes()
                for node in list:
                    polyline.append( IPoint().make( int(node.getAttribute("x")), int(node.getAttribute("y")) ) )
                # pointarray = outline.split(";")
                # for m in range(len(pointarray)):
                #     pt=pointarray[m].split(",")
                #     polyline.append(IPoint().make(int(pt[0]),int(pt[1])))
            #print "length of polyline", len(polyline)
            if (len(polyline)>2):
                if action=="del": self.fogregion.FromPolygon(polyline,0)
                else: self.fogregion.FromPolygon(polyline,1)

    def init_from_dom(self,xml_dom):
        self.interpret_dom(xml_dom)
