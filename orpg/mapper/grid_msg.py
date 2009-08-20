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
# File: mapper/gird_msg.py
# Author: OpenRPG Team
# Maintainer:
# Version:
#   $Id: grid_msg.py,v 1.8 2006/11/04 21:24:21 digitalxero Exp $
#
# Description:
#
__version__ = "$Id: grid_msg.py,v 1.8 2006/11/04 21:24:21 digitalxero Exp $"

from base_msg import map_element_msg_base
#from base_msg import * ## ?? import all? Deprecated!?

class grid_msg(map_element_msg_base):

    def __init__(self,reentrant_lock_object = None):
        self.tagname = "grid"
        map_element_msg_base.__init__(self,reentrant_lock_object)
