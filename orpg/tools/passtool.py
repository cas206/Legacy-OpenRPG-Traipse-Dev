# Copyright (C) 2000-2001 The OpenRPG Project
#
#       openrpg-dev@lists.sourceforge.net
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
# File: passtool.py
# Author: Todd "Snowdog" Faris
# Maintainer:
# Version:
#   $Id: passtool.py,v 1.9 2006/11/04 21:24:22 digitalxero Exp $
#
# Description: password helper. remembers passwords so user
#              doesn't have to type passwords over and over

import orpg.orpg_windows
from orpg.orpgCore import component
import traceback
#from orpg.tools.settings import settings

#####################
## Password Assistant
#####################
class PassSet:
    "set of passwords for a given room id on a server"
    def __init__(self):
        #room admin password (aka boot password)
        self.admin = None

        #room password
        self.room = None

class PassTool:
    "Password Management System"
    def __init__(self):
        self.settings = component.get("settings")
        #server admin password
        self.server = None
        self.groups = {}
        if self.settings.get_setting('PWMannager') == 'On': self.enabled = 1
        else: self.enabled = 0


    def DumpPasswords(self):
        "Debugging Routine"
        print("Password Manager Dump\nServer: \""+self.server+"\"")
        for c in self.groups:
            ad = self.groups[c].admin
            rm = self.groups[c].room
            print( " #"+str(c)+"  R:\""+str(rm)+"\"  A:\""+str(ad)+"\"")

    def ClearPassword( self, type="ALL", groupid=0):
        if type == "ALL" and groupid == 0:
            self.server = None
            self.groups={}
        elif type == "ALL":
            self.groups[ int(groupid) ].admin= None
            self.groups[ int(groupid) ].room= None
        elif type == "server": self.server = None
        elif type == "admin":  self.groups[ int(groupid) ].admin = None
        elif type == "room":
            self.groups[ int(groupid) ].room = None
        else: pass

    def QueryUser(self,info_string):
        pwd_dialog = orpg.orpg_windows.wx.TextEntryDialog(None,info_string,"Password Required")
        if pwd_dialog.ShowModal() == orpg.orpg_windows.wx.ID_OK:
            pwd_dialog.Destroy()
            return str(pwd_dialog.GetValue())
        else:
            pwd_dialog.Destroy()
            return None

    def CheckGroupData(self, id ):
        try: #see if group exists
            group=self.groups[ int(id) ]
        except: #group doesn't exist... create it
            self.groups[ int(id) ] = PassSet()

    def RemoveGroupData(self, id ):
        try:
            #if PassSet exists for group remove it.
            del self.groups[int(id)]
        except:
            pass

    def GetSilentPassword( self, type="server", groupid = 0):
        try:
            self.CheckGroupData( groupid )
            if type == "admin":
                if self.groups[int(groupid)].admin != None: return str(self.groups[int(groupid)].admin)
                else: return None
            elif type == "room":
                if self.groups[int(groupid)].room != None: return str(self.groups[int(groupid)].room)
                else: return None
            elif type == "server":
                if self.server != None: return str(self.server)
                else: return None
        except:
            traceback.print_exc()
            #return None

    def GetPassword(self, type="room", groupid=0):
        if self.Is_Enabled():
            self.CheckGroupData( groupid )
            if type == "admin": return self.AdminPass(int(groupid))
            elif type == "room": return self.RoomPass(int(groupid))
            elif type == "server": return self.ServerPass()
            else:
                querystring = "Enter password for \""+str(type)+"\""
                return self.QueryUser( querystring )
        else:
            if type == "admin": return self.QueryUser( "Enter Admin(Boot) Password" )
            elif type == "room": return self.QueryUser("Enter Room Password" )
            elif type == "server": return self.QueryUser( "Enter Server Administrator Password" )
            else:
                querystring = "Enter password for \""+str(type)+"\""
                return self.QueryUser( querystring )


    def Is_Enabled(self):
        return int(self.enabled)

    def Enable(self):
        self.enabled = 1
        self.settings.set_setting('PWMannager', 'On')

    def Disable(self):
        self.enabled = 0
        self.settings.set_setting('PWMannager', 'Off')


    def AdminPass( self, groupid ):
        self.CheckGroupData( groupid )
        if self.groups[ int(groupid) ].admin != None: return str(self.groups[ int(groupid) ].admin)
        else:
            self.groups[ int(groupid) ].admin = self.QueryUser("Please enter the Room Administrator Password:")
            return  str(self.groups[ int(groupid) ].admin)


    def RoomPass( self, groupid):
        self.CheckGroupData( groupid )
        if self.groups[ int(groupid) ].room != None: return str(self.groups[ int(groupid) ].room)
        else:
            self.groups[ int(groupid) ].room =  self.QueryUser("Please enter the Room Password:")
            return str(self.groups[ int(groupid) ].room)


    def ServerPass( self ):
        if self.server != None: return str(self.server)
        else:
            self.server = self.QueryUser("Please enter the Server Administrator password:")
            return str(self.server)

    def FailPassword( self, type="room", groupid=0):
        self.CheckGroupData( groupid )
        if type == "admin":
            self.ClearPassword( type, groupid )
            return self.AdminPass()
        elif type == "room":
            self.ClearPassword( type, groupid  )
            return self.RoomPass()
        elif type == "server":
            self.ClearPassword( type, groupid  )
            return self.ServerPass()

#PassTool = PassTool()
component.add('password_manager', PassTool())
