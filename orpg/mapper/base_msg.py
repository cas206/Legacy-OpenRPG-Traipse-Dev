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
# File: mapper/base_msg.py
# Author: Chris Davis
# Maintainer:
# Version:
#   $Id: base_msg.py,v Traipse 'Ornery-Orc' prof.ebral Exp $
#
# Description:
#
__version__ = "$Id: base_msg.py,v Traipse 'Ornery-Orc' prof.ebral Exp $"

from threading import RLock
from orpg.networking.mplay_client import *
from xml.etree.ElementTree import ElementTree, Element

class map_element_msg_base:
#  This is a base class

    def __init__(self,reentrant_lock_object = None):

        if not hasattr(self,"tagname"):
            raise Exception, "This is a virtual class that cannot be directly instantiated.  Set self.tagname in derived class."
        self._props = {}
        #  This is a dictionary that holds (value,changed) 2-tuples, indexed by attribute
        #  Avoid manipulating these values directly.  Instead, use the provided accessor methods.
        #  If there is not one that suits your needs, please add one to this class and
        #  use it instead.

        self.children = {}
        # This next clause will set self.p_lock to a passed-in RLock object, if present.
        #    Otherwise, it will create it's very own for this instance.
        #    Using a passed in object is useful to protect an entire <map/> element from
        #    being changed by another thread when any part of it is being change by another
        #    thread.  Just pass the map_msg's p_lock object in to it's descendents.
        if reentrant_lock_object: self.p_lock = reentrant_lock_object
        else: self.p_lock = RLock()

    def clear(self):
        self.p_lock.acquire()

        for child in self.children.keys():
            self.children[child].clear()
            self.children[child] = None
            del self.children[child]

        for p in self._props.keys(): self._props[p] = None

        self.p_lock.release()

    #########################################
    #  Accessor functions begin

    #  Access single property

    def init_prop(self,prop,value):  # set's the changed flag to False and assigns
        self.p_lock.acquire()
        self._props[prop] = (value, 0)
        self.p_lock.release()

    def set_prop(self,prop,value):  # set's the changed flag to True and assigns
        self.p_lock.acquire()
        self._props[prop] = (value, 1)
        self.p_lock.release()

    def get_prop(self,prop):  # returns None if prop not found
        self.p_lock.acquire()
        if prop in self._props.keys():
            (p,c) = self._props[prop]
            self.p_lock.release()
            return p
        else: self.p_lock.release(); return None

    def is_prop_changed(self,prop):  # returns None if prop not found
        self.p_lock_acquire()
        if prop in self._props.keys():
            (p,c) = self._props[prop]
            self.p_lock.release()
            return c
        else: self.p_lock.release(); return None

    def get_child(self,key):         # returns None if key not found in children list
        self.p_lock_acquire()
        if self.children.has_key(key):
            self.p_lock.release()
            return self.children[key]
        else:
            self.p_lock.release()
            return None

    #  Access multiple properties
    def init_props(self,props):               # same as init_prop(), but takes dictionary of props
        self.p_lock.acquire()
        for k in props.keys(): self._props[k] = (props[k],0)
        self.p_lock.release()

    def set_props(self,props):                # same as set_prop(), but takes dictionary of props
        self.p_lock.acquire()
        for k in props.keys(): self._props[k] = (props[k],1)
        self.p_lock.release()

    def get_all_props(self):                  # returns dictionary of all properties, regardless of change
        self.p_lock.acquire()
        result = {}
        for k in self._props.keys():
            (p,c) = self._props[k]
            result[k] = p
        self.p_lock.release()
        return result

    def get_changed_props(self):              # returns dictionary of all properties that have been changed
        self.p_lock.acquire()
        result = {}
        for k in self._props.keys():
            (p,c) = self._props[k]
            if c: result[k] = p
        self.p_lock.release()
        return result

    def get_children(self):                 # returns dictionary of children
        return self.children

    #  Accessor functions end
    #########################################

    #########################################
    #  XML emitters begin
    def get_all_xml(self,action="new",output_action = 0):    # outputs a tag with all attributes it contains
        self.p_lock.acquire()
        xml_str = "<" + self.tagname
        if action and output_action: xml_str += " action='" + action + "'"
        for k in self._props.keys():
            (p,c) = self._props[k]
            if k != "action" or not action: xml_str += " " + k + "='" + p + "'"
        if self.children:
            xml_str += ">"
            for child in self.children.keys(): xml_str += self.children[child].get_all_xml(action)
            xml_str += "</" + self.tagname + ">"
        else: xml_str += "/>"
        self.p_lock.release()
        return xml_str

    def get_changed_xml(self,action="update",output_action = 0):    # outputs a tag with all changed attributes
        self.p_lock.acquire()
        xml_str = "<" + self.tagname
        if action and output_action:
            xml_str += " action='" + action + "'"

        # if present, always send the id, even if it didn't change
        if self._props.has_key("id"):
            (p,c) = self._props["id"]
            xml_str += " id='" + p + "'"
        for k in self._props.keys():
            (p,c) = self._props[k]
            if (k != "id" or k != "action") and c == 1: xml_str += " " + k + "='" + p + "'"
        if self.children:
            xml_str += ">"
            for child in self.children.keys(): xml_str += self.children[child].get_changed_xml(action)
            xml_str += "</" + self.tagname + ">"
        else: xml_str += "/>"
        self.p_lock.release()
        return xml_str

    # convenience method to use if only this tag is modified
    #   outputs a <map/> element containing only the changes to this tag
    def standalone_update_text(self,update_id_string):
        buffer = "<map id='" + update_id_string + "'>"
        buffer += self.get_changed_xml("update")
        buffer += "<map/>"
        return buffer

    # XML emitters end
    #########################################

    #########################################
    #  XML importers begin

    def _from_dom(self,xml_dom,prop_func):
        self.p_lock.acquire()
        if iselement(xml_dom): ## Uses new Element Tree style
            if xml_dom.tag == self.tagname:
                if xml_dom.attrib:
                    for k in xml_dom.attrib: prop_func(k,xml_dom.get(k))
        elif not iselement(xml_dom): ## Uses old DOM style (deprecated!!)
            if xml_dom.tagName == self.tagname:
                if xml_dom.getAttributeKeys():
                    for k in xml_dom.getAttributeKeys(): prop_func(k,xml_dom.getAttribute(k))
        else:
            self.p_lock.release()
            raise Exception, "Error attempting to modify a " + self.tagname + " from a non-<" + self.tagname + "/> element"
        self.p_lock.release()

    def init_from_dom(self,xml_dom):
    #  xml_dom must be pointing to an empty tag.  Override in a derived class for <map/> and other similar tags.
        self._from_dom(xml_dom,self.init_prop)

    def set_from_dom(self,xml_dom):
    #  xml_dom must be pointing to an empty tag.  Override in a derived class for <map/> and other similar tags
        self._from_dom(xml_dom,self.set_prop)

    def init_from_xml(self,xml):
        xml_dom = parseXml(xml)
        node_list = xml_dom.getElementsByTagName(self.tagname)
        if len(node_list) < 1: print "Warning: no <" + self.tagname + "/> elements found in DOM."
        else:
            while len(node_list): self.init_from_dom(node_list.pop())
        if xml_dom: xml_dom.unlink()

    def set_from_xml(self,xml):
        xml_dom = parseXml(xml)
        node_list = xml_dom.getElementsByTagName(self.tagname)
        if len(node_list) < 1: print "Warning: no <" + self.tagname + "/> elements found in DOM."
        else:
            while len(node_list): self.set_from_dom(node_list.pop())
        if xml_dom: xml_dom.unlink()

    # XML importers end
    #########################################
