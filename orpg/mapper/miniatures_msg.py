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
# File: mapper/miniatures_msg.py
# Author: Chris Davis
# Maintainer:
# Version:
#   $Id: miniatures_msg.py,v 1.8 2006/11/04 21:24:21 digitalxero Exp $
#
# Description: This file contains some of the basic definitions for the chat
# utilities in the orpg project.
#
__version__ = "$Id: miniatures_msg.py,v 1.8 2006/11/04 21:24:21 digitalxero Exp $"

from base_msg import *

class mini_msg(map_element_msg_base):

    def __init__(self,reentrant_lock_object = None):
        self.tagname = "miniature"   # set this to be for minis.  Tagname gets used in some base class functions.
        map_element_msg_base.__init__(self,reentrant_lock_object)   # call base class

    # convenience method to use if only this mini is modified
    #   outputs a <map/> element containing only the changes to this mini
    def standalone_update_text(self,update_id_string):
        buffer = "<map id='" + update_id_string + "'>"
        buffer += "<miniatures>"
        buffer += self.get_changed_xml()
        buffer += "</miniatures></map>"
        return buffer

    # convenience method to use if only this mini is modified
    #   outputs a <map/> element that deletes this mini
    def standalone_delete_text(self,update_id_string):
        buffer = None
        if self._props.has_key("id"):
            buffer = "<map id='" + update_id_string + "'>"
            buffer += "<miniatures>"
            buffer += "<miniature action='del' id='" + self._props("id") + "'/>"
            buffer += "</miniatures></map>"
        return buffer

    # convenience method to use if only this mini is modified
    #   outputs a <map/> element to add this mini
    def standalone_add_text(self,update_id_string):
        buffer = "<map id='" + update_id_string + "'>"
        buffer += "<miniatures>"
        buffer += self.get_all_xml()
        buffer += "</miniatures></map>"
        return buffer

    def get_all_xml(self,action="new",output_action=1):
        return map_element_msg_base.get_all_xml(self,action,output_action)

    def get_changed_xml(self,action="update",output_action=1):
        return map_element_msg_base.get_changed_xml(self,action,output_action)

class minis_msg(map_element_msg_base):

    def __init__(self,reentrant_lock_object = None):
        self.tagname = "miniatures"
        map_element_msg_base.__init__(self,reentrant_lock_object)

    def init_from_dom(self,xml_dom):
        self.p_lock.acquire()
        if xml_dom.tagName == self.tagname:
            if xml_dom.getAttributeKeys():
                for k in xml_dom.getAttributeKeys():
                    self.init_prop(k,xml_dom.getAttribute(k))

            for c in xml_dom._get_childNodes():
                mini = mini_msg(self.p_lock)
                try: mini.init_from_dom(c)
                except Exception, e: print e; continue
                id = mini.get_prop("id")
                action = mini.get_prop("action")

                if action == "new": self.children[id] = mini
                elif action == "del":
                    if self.children.has_key(id):
                        self.children[id] = None
                        del self.children[id]

                elif action == "update":
                    if self.children.has_key(id):
                        self.children[id].init_props(mini.get_all_props())
        else:
            self.p_lock.release()
            raise Exception, "Error attempting to initialize a " + self.tagname + " from a non-<" + self.tagname + "/> element"
        self.p_lock.release()

    def set_from_dom(self,xml_dom):
        self.p_lock.acquire()
        if xml_dom.tagName == self.tagname:
            if xml_dom.getAttributeKeys():
                for k in xml_dom.getAttributeKeys():
                    self.set_prop(k,xml_dom.getAttribute(k))

            for c in xml_dom._get_childNodes():
                mini = mini_msg(self.p_lock)

                try: mini.set_from_dom(c)
                except Exception, e: print e; continue
                id = mini.get_prop("id")
                action = mini.get_prop("action")
                if action == "new": self.children[id] = mini
                elif action == "del":
                    if self.children.has_key(id):
                        self.children[id] = None
                        del self.children[id]
                elif action == "update":
                    if self.children.has_key(id):
                        self.children[id].set_props(mini.get_all_props())
        else:
            self.p_lock.release()
            raise Exception, "Error attempting to set a " + self.tagname + " from a non-<" + self.tagname + "/> element"
        self.p_lock.release()
