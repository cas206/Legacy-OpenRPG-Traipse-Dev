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
# File: mapper/map_msg.py
# Author: OpenRPG
# Maintainer:
# Version:
#   $Id: map_msg.py,v Traipse 'Ornery-Orc' prof.ebral Exp $
#
# Description:
#
__version__ = "$Id: map_msg.py,v Traipse 'Ornery-Orc' prof.ebral Exp $"

from base_msg import *
from background_msg import *
from grid_msg import *
from miniatures_msg import *
from whiteboard_msg import *
from fog_msg import *

"""
<map name=? id=? >
    <bg type=? file=? color=? />
    <grid size=? snap=? />
    <miniatures serial=? >
        <miniature  path=?  posx=?  posy=?  heading=? face=? owner=? label=? locked=? width=? height=? />
    </miniatures>
</map>

"""

class map_msg(map_element_msg_base):

    def __init__(self,reentrant_lock_object = None):
        self.tagname = "map"
        map_element_msg_base.__init__(self,reentrant_lock_object)

    def init_from_dom(self,xml_dom):
        self.p_lock.acquire()
        if xml_dom.tagName == self.tagname:
            # If this is a map message, look for the "action=new"
            # Notice we only do this when the root is a map tag
            if self.tagname == "map" and xml_dom.hasAttribute("action") and xml_dom.getAttribute("action") == "new":
                self.clear()
            # Process all of the properties in each tag
            if xml_dom.getAttributeKeys():
                for k in xml_dom.getAttributeKeys():
                    self.init_prop(k,xml_dom.getAttribute(k))
            for c in xml_dom._get_childNodes():
                name = c._get_nodeName()
                if not self.children.has_key(name):
                    if name == "miniatures": self.children[name] = minis_msg(self.p_lock)
                    elif name == "grid": self.children[name] = grid_msg(self.p_lock)
                    elif name == "bg": self.children[name] = bg_msg(self.p_lock)
                    elif name == "whiteboard": self.children[name] = whiteboard_msg(self.p_lock)
                    elif name == "fog": self.children[name] = fog_msg(self.p_lock)
                    else:
                        print "Unrecognized tag " + name + " found in map_msg.init_from_dom - skipping"
                        continue
                try: self.children[name].init_from_dom(c)
                except Exception, e:
                    print "map_msg.init_from_dom() exception: "+str(e)
                    continue
        else:
            self.p_lock.release()
            raise Exception, "Error attempting to initialize a " + self.tagname + " from a non-<" + self.tagname + "/> element"
        self.p_lock.release()

    def set_from_dom(self,xml_dom):
        self.p_lock.acquire()
        if xml_dom.tagName == self.tagname:
            # If this is a map message, look for the "action=new"
            # Notice we only do this when the root is a map tag
            if self.tagname == "map" and xml_dom.hasAttribute("action") and xml_dom.getAttribute("action") == "new":
                self.clear()
            # Process all of the properties in each tag
            if xml_dom.getAttributeKeys():
                for k in xml_dom.getAttributeKeys(): self.set_prop(k,xml_dom.getAttribute(k))
            for c in xml_dom._get_childNodes():
                name = c._get_nodeName()
                if not self.children.has_key(name):
                    if name == "miniatures": self.children[name] = minis_msg(self.p_lock)
                    elif name == "grid": self.children[name] = grid_msg(self.p_lock)
                    elif name == "bg": self.children[name] = bg_msg(self.p_lock)
                    elif name == "whiteboard": self.children[name] = whiteboard_msg(self.p_lock)
                    elif name == "fog": self.children[name] = fog_msg(self.p_lock)
                    else:
                        print "Unrecognized tag " + name + " found in map_msg.init_from_dom - skipping"
                        continue
                try: self.children[name].set_from_dom(c)
                except Exception, e:
                    print "map_msg.set_from_dom() exception: "+str(e)
                    continue
        else:
            self.p_lock.release()
            raise Exception, "Error attempting to set a " + self.tagname + " from a non-<" + self.tagname + "/> element in map"
        self.p_lock.release()

    def get_all_xml(self, action="new", output_action=1):
        return map_element_msg_base.get_all_xml(self, action, output_action)

    def get_changed_xml(self, action="update", output_action=1):
        return map_element_msg_base.get_changed_xml(self, action, output_action)
