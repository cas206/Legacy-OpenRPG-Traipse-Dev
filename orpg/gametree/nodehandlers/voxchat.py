# Copyright (C) 2000-2001 The OpenRPG Project
#
#   openrpg-dev@lists.sourceforge.net
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
# File: voxchat.py
# Author: Ted Berg
# Maintainer:
# Version:
#   $Id: voxchat.py,v Traipse 'Ornery-Orc' prof.ebral Exp $
#
# Description: nodehandler for alias.
#

__version__ = "$Id: voxchat.py,v Traipse 'Ornery-Orc' prof.ebral Exp $"

import re, os, string, core

from orpg.orpg_windows import *
import core
import orpg.tools.scriptkit
import orpg.tools.predTextCtrl
import orpg.tools.rgbhex
import orpg.tools.inputValidator

from orpg.dirpath import dir_struct
import orpg.minidom
import orpg.networking.mplay_client
from orpg.orpgCore import component

#
# Good things to add:
# 1.u'use filter' per alias  [ this should be done ]
# 2. make aliases remember which filter they're using  [ lisbox in gtk appaears to ignore SetSelection( <= 0 )
#


class voxchat_handler(core.node_handler):
    def __init__(self, xml_dom, tree_node):
        core.node_handler.__init__( self, xml_dom, tree_node)
        self.node = xml_dom
        #self.xml = component.get('xml')

    def get_design_panel( self, parent ):
        aliasLib = component.get('alias')
        aliasLib.ImportFromTree(self.node)
        return None

    def get_use_panel( self, parent ):
        aliasLib = component.get('alias')
        aliasLib.ImportFromTree(self.node)
        return None
