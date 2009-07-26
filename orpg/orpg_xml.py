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
# File: orpg_xml.py
# Author: Chris Davis
# Maintainer:
# Version:
#   $Id: orpg_xml.py,v 1.12 2007/07/19 20:33:10 digitalxero Exp $
#
# Description: xml utilies
#

from orpg import minidom
import string

def toxml(root,pretty=0):
    return root.toxml(pretty)

def parseXml(s):
    "parse and return doc"
    try:
        doc = minidom.parseString(s)
        doc.normalize()
        return doc
    except Exception, e:
        print e
        return None

def safe_get_text_node(xml_dom):
    """ returns the child text node or creates one if doesnt exist """
    t_node = xml_dom._get_firstChild()
    if t_node == None:
        t_node = minidom.Text("")
        t_node = xml_dom.appendChild(t_node)
    return t_node

def strip_unicode(txt):
    for i in xrange(len(txt)):
        if txt[i] not in string.printable:
            try: txt = txt.replace(txt[i], '&#' + str(ord(txt[i])) + ';')
            except: txt = txt.replace(txt[i], '{?}')
    return txt

def strip_text(txt):
    #  The following block strips out 8-bit characters
    u_txt = ""
    bad_txt_found = 0
    txt = strip_unicode(txt)
    for c in txt:
        if ord(c) < 128: u_txt += c
        else: bad_txt_found = 1
    if bad_txt_found: print "Some non 7-bit ASCII characters found and stripped"
    return u_txt
