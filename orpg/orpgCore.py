#!/usr/bin/env python
# Copyright (C) 2000-2006 The OpenRPG Project
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
# File: main.py
# Author: Chris Davis
# Maintainer:
# Version:
#   $Id: orpgCore.py,v 1.8 2006/11/12 00:10:37 digitalxero Exp $
#
# Description: This is the core functionality that is used by both the client and server.
#               As well as everything in here should be global to every file
#

__version__ = "$Id: orpgCore.py,v 1.8 2006/11/12 00:10:37 digitalxero Exp $"

import time
from string import *
import os
import os.path
import thread
import traceback
import sys
import systempath
import re
import string
import urllib
import webbrowser
import random

#########################
## Error Types
#########################
ORPG_CRITICAL       = 1
ORPG_GENERAL        = 2
ORPG_INFO           = 4
ORPG_NOTE           = 8
ORPG_DEBUG          = 16

########################
## openrpg object
########################

class ORPGStorage(object):
    __components = {}

    def add(self, key, com):
        self.__components[key] = com

    def get(self, key):
        if self.__components.has_key(key): return self.__components[key]
        else: return None

    def delete(self, key):
        if self.__components.has_key(key): del self.__components[key]
        else: return

def singleton(cls):
    instances = {}
    def getinstance():
        if cls not in instances:
            instances[cls] = cls()
        return instances[cls]
    return getinstance

ORPGStorage = singleton(ORPGStorage)
component = ORPGStorage()
