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
# File: gsclient.py
# Author: Chris Davis
# Maintainer:
# Version:
#   $Id: gsclient.py,v 1.53 2007/10/25 21:49:34 digitalxero Exp $
#
# Description: The file contains code for the game server browser
#

__version__ = "$Id: gsclient.py,v 1.53 2007/10/25 21:49:34 digitalxero Exp $"

import orpg.dirpath
from orpg.orpg_windows import *
from orpg.orpg_xml import *
import meta_server_lib
import orpg.tools.orpg_settings
import orpg.tools.rgbhex
from orpg.orpgCore import open_rpg
import traceback

gs_host = 1
gs_join = 2
# constants

LIST_SERVER = wx.NewId()
LIST_ROOM = wx.NewId()
ADDRESS = wx.NewId()
GS_CONNECT = wx.NewId()
GS_DISCONNECT = wx.NewId()
GS_SERVER_REFRESH = wx.NewId()
GS_JOIN = wx.NewId()
GS_JOINLOBBY = wx.NewId()
GS_CREATE_ROOM = wx.NewId()
GS_PWD = wx.NewId()
GS_CLOSE = wx.NewId()
OR_CLOSE = wx.NewId()

class server_instance:
    def __init__(self, id, name="[Unknown]", users="0", address="127.0.0.1", port="9557"):
        self.id = id
        self.name = name
        self.user = users
        self.addy = address
        self.port = port

def server_instance_compare(x,y):
    """compares server insances for list sort"""
    DEV_SERVER = "OpenRPG DEV"
    xuser = 0
    yuser = 0
    try: xuser = int(x.user)
    except: pass
    try: yuser = int(y.user)
    except: pass
    if x.name.startswith(DEV_SERVER):
        if y.name.startswith(DEV_SERVER):
            if x.name > y.name: return 1
            elif x.name == y.name:
                if xuser < yuser: return 1
                elif xuser > yuser: return -1
                else: return 0
            else: return -1
        else: return -1
    elif y.name.startswith(DEV_SERVER): return 1
    elif xuser < yuser: return 1
    elif xuser == yuser:
        if x.name > y.name: return 1
        elif x.name == y.name: return 0
        else: return -1
    else: return -1

def roomCmp(room1, room2):
    if int(room1) > int(room2):
        return 1
    elif int(room1) < int(room2):
        return -1
    return 0

class game_server_panel(wx.Panel):
    def __init__(self,parent):
        wx.Panel.__init__(self, parent, -1)
        self.parent = parent
        self.log = open_rpg.get_component('log')
        self.log.log("Enter game_server_panel", ORPG_DEBUG)
        self.password_manager = open_rpg.get_component('password_manager') # passtool --SD 8/03
        self.frame = open_rpg.get_component('frame')
        self.session = open_rpg.get_component('session')
        self.settings = open_rpg.get_component('settings')
        self.xml = open_rpg.get_component('xml')
        self.serverNameSet = 0
        self.last_motd = ""
        self.buttons = {}
        self.texts = {}
        self.svrList = []
        self.build_ctrls()
        self.refresh_server_list()
        self.refresh_room_list()
        self.log.log("Exit game_server_panel", ORPG_DEBUG)

#---------------------------------------------------------
# [START] Snowdog: Updated Game Server Window 12/02
#---------------------------------------------------------
    def build_ctrls(self):
        self.log.log("Enter game_server_panel->build_ctrls(self)", ORPG_DEBUG)

        ## Section Sizers (with frame edges and text captions)
        self.box_sizers = {}
        self.box_sizers["server"] = wx.StaticBox(self, -1, "Server")
        self.box_sizers["window"] = wx.StaticBox(self, -1, "Exit" )
        self.box_sizers["room"] = wx.StaticBox(self, -1, "Rooms")
        self.box_sizers["c_room"] = wx.StaticBox(self, -1, "Create Room")

        ## Layout Sizers
        self.sizers = {}
        self.sizers["main"] = wx.GridBagSizer(hgap=1, vgap=1)
        self.sizers["server"] = wx.StaticBoxSizer(self.box_sizers["server"], wx.VERTICAL)
        self.sizers["rooms"] = wx.StaticBoxSizer(self.box_sizers["room"], wx.VERTICAL)
        self.sizers["close"] = wx.StaticBoxSizer(self.box_sizers["window"], wx.HORIZONTAL)
        self.sizers["c_room"] = wx.StaticBoxSizer(self.box_sizers["c_room"], wx.VERTICAL)

        #Build Server Sizer
        adder = wx.StaticText(self, -1, "Address:")
        self.texts["address"] = wx.TextCtrl(self, ADDRESS)
        servers = wx.StaticText(self, -1, "Servers:")
        self.server_list = wx.ListCtrl(self, LIST_SERVER, style=wx.LC_REPORT | wx.SUNKEN_BORDER )
        self.server_list.InsertColumn(0, "Players", wx.LIST_FORMAT_LEFT, 0)
        self.server_list.InsertColumn(1, "Name", wx.LIST_FORMAT_LEFT, 0)
        self.buttons[GS_CONNECT] = wx.Button(self, GS_CONNECT, "Connect")
        self.buttons[GS_SERVER_REFRESH] = wx.Button(self, GS_SERVER_REFRESH, "Refresh")
        self.buttons[GS_DISCONNECT] = wx.Button(self, GS_DISCONNECT, "Disconnect")
        self.sizers["svrbtns"] = wx.BoxSizer(wx.HORIZONTAL)
        self.sizers["svrbtns"].Add(self.buttons[GS_CONNECT], 0, wx.EXPAND)
        self.sizers["svrbtns"].Add(self.buttons[GS_SERVER_REFRESH], 0, wx.EXPAND)
        self.sizers["svrbtns"].Add(self.buttons[GS_DISCONNECT], 0, wx.EXPAND)
        self.sizers["server"].Add(adder, 0, wx.EXPAND)
        self.sizers["server"].Add(self.texts["address"], 0, wx.EXPAND)
        self.sizers["server"].Add(servers, 0, wx.EXPAND)
        self.sizers["server"].Add(self.server_list, 1, wx.EXPAND)
        self.sizers["server"].Add(self.sizers["svrbtns"], 0, wx.EXPAND)

        #Build Rooms Sizer
        self.room_list = wx.ListCtrl(self, LIST_ROOM, style=wx.LC_REPORT | wx.SUNKEN_BORDER)
        self.room_list.InsertColumn(0,"Game", wx.LIST_FORMAT_LEFT,-1)
        self.room_list.InsertColumn(1,"Players", wx.LIST_FORMAT_LEFT,-1)
        self.room_list.InsertColumn(2,"PW", wx.LIST_FORMAT_LEFT,-1)
        self.buttons[GS_JOIN] = wx.Button(self, GS_JOIN, "Join Room")
        self.buttons[GS_JOINLOBBY] = wx.Button(self, GS_JOINLOBBY, "Lobby")
        self.sizers["roombtns"] = wx.BoxSizer(wx.HORIZONTAL)
        self.sizers["roombtns"].Add(self.buttons[GS_JOIN], 0, wx.EXPAND)
        self.sizers["roombtns"].Add(self.buttons[GS_JOINLOBBY], 0, wx.EXPAND)
        self.sizers["rooms"].Add(self.room_list, 1, wx.EXPAND)
        self.sizers["rooms"].Add(self.sizers["roombtns"], 0, wx.EXPAND)

        #Build Close Sizer
        self.buttons[OR_CLOSE] = wx.Button(self, OR_CLOSE,"Exit OpenRPG")
        self.buttons[GS_CLOSE] = wx.Button(self, GS_CLOSE,"Close Window")
        self.sizers["close"].Add(self.buttons[OR_CLOSE], 1, wx.ALIGN_CENTER_VERTICAL)
        self.sizers["close"].Add(self.buttons[GS_CLOSE], 1, wx.ALIGN_CENTER_VERTICAL)

        #Build Create Room Sizer
        rname = wx.StaticText(self,-1, "Room Name:")
        self.texts["room_name"] = wx.TextCtrl(self, -1)
        rpass = wx.StaticText(self,-1, "Password:")
        self.buttons[GS_PWD] = wx.CheckBox(self, GS_PWD, "")
        self.texts["room_pwd"] = wx.TextCtrl(self, -1)
        self.texts["room_pwd"].Enable(0)
        pwsizer = wx.BoxSizer(wx.HORIZONTAL)
        pwsizer.Add(self.buttons[GS_PWD],0,0)
        pwsizer.Add(self.texts["room_pwd"], 1, wx.EXPAND)
        apass = wx.StaticText(self,-1, "Admin Password:")
        self.texts["room_boot_pwd"] = wx.TextCtrl(self, -1)
        minver = wx.StaticText(self,-1, "Minimum Version:")
        self.texts["room_min_version"] = wx.TextCtrl(self, -1)
        self.sizers["c_room_layout"] = wx.FlexGridSizer(rows=8, cols=2, hgap=1, vgap=1)
        self.sizers["c_room_layout"].Add(rname, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL|wx.ALL)
        self.sizers["c_room_layout"].Add(self.texts["room_name"], 0, wx.EXPAND)
        self.sizers["c_room_layout"].Add(rpass, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL|wx.ALL)
        self.sizers["c_room_layout"].Add(pwsizer, 0, wx.EXPAND)
        self.sizers["c_room_layout"].Add(apass, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL|wx.ALL)
        self.sizers["c_room_layout"].Add(self.texts["room_boot_pwd"], 0, wx.EXPAND)
        self.sizers["c_room_layout"].Add(minver, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL|wx.ALL)
        self.sizers["c_room_layout"].Add(self.texts["room_min_version"], 0, wx.EXPAND)
        self.sizers["c_room_layout"].AddGrowableCol(1)
        self.buttons[GS_CREATE_ROOM] = wx.Button(self, GS_CREATE_ROOM, "Create Room")
        self.sizers["c_room"].Add(self.sizers["c_room_layout"], 1, wx.EXPAND)
        self.sizers["c_room"].Add(self.buttons[GS_CREATE_ROOM], 0, wx.EXPAND)

        #Build Main Sizer
        self.sizers["main"].Add(self.sizers["server"], (0,0), span=(2,1), flag=wx.EXPAND)
        self.sizers["main"].Add(self.sizers["rooms"], (0,1), flag=wx.EXPAND)
        self.sizers["main"].Add(self.sizers["close"], (2,0), flag=wx.EXPAND)
        self.sizers["main"].Add(self.sizers["c_room"], (1,1), span=(2,1), flag=wx.EXPAND)
        self.sizers["main"].AddGrowableCol(0)
        self.sizers["main"].AddGrowableCol(1)
        self.sizers["main"].AddGrowableRow(0)
        self.SetSizer(self.sizers["main"])
        self.SetAutoLayout(True)
        self.Fit()

        ## Event Handlers
        self.Bind(wx.EVT_BUTTON, self.on_button, id=GS_CONNECT)
        self.Bind(wx.EVT_BUTTON, self.on_button, id=GS_DISCONNECT)
        self.Bind(wx.EVT_BUTTON, self.on_button, id=GS_CREATE_ROOM)
        self.Bind(wx.EVT_BUTTON, self.on_button, id=GS_JOIN)
        self.Bind(wx.EVT_BUTTON, self.on_button, id=GS_JOINLOBBY)
        self.Bind(wx.EVT_BUTTON, self.on_button, id=GS_SERVER_REFRESH)
        self.Bind(wx.EVT_BUTTON, self.on_button, id=GS_CLOSE)
        self.Bind(wx.EVT_BUTTON, self.on_button, id=OR_CLOSE)
        self.Bind(wx.EVT_CHECKBOX, self.on_button, id=GS_PWD)

        # Added double click handlers 5/05 -- Snowdog
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.on_server_dbclick, id=LIST_SERVER)
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.on_room_dbclick, id=LIST_ROOM)
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.on_select, id=LIST_ROOM)
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.on_select, id=LIST_SERVER)
        self.texts['address'].Bind(wx.EVT_SET_FOCUS, self.on_text)
        self.set_connected(self.session.is_connected())
        self.cur_room_index = -1
        self.cur_server_index = -1
        self.rmList = {}
        self.log.log("Exit game_server_panel->build_ctrls(self)", ORPG_DEBUG)

#---------------------------------------------------------
# [END] Snowdog: Updated Game Server Window 12/02
#---------------------------------------------------------

    #-----------------------------------------------------
    # on_server_dbclick()
    # support for double click selection of server.
    # 5/16/05 -- Snowdog
    #-----------------------------------------------------
    def on_server_dbclick(self, evt=None):
        self.log.log("Enter game_server_panel->on_server_dbclick(self, evt)", ORPG_DEBUG)

        #make sure address is updated just in case list select wasn't done
        try:
            self.on_select(evt)
        except:
            pass
        address = self.texts["address"].GetValue()
        if self.session.is_connected():
            if self.session.host_server == address :
                #currently connected to address. Do nothing.
                return
            else:
                #address differs, disconnect.
                self.frame.kill_mplay_session()
        self.do_connect(address)
        self.log.log("Exit game_server_panel->on_server_dbclick(self, evt)", ORPG_DEBUG)


    #-----------------------------------------------------
    # on_room_dbclick()
    # support for double click selection of server.
    # 5/16/05 -- Snowdog
    #-----------------------------------------------------

    def on_room_dbclick(self, evt=None):
        self.log.log("Enter game_server_panel->on_room_dbclick(self, evt)", ORPG_DEBUG)

        #make sure address is updated just in case list select wasn't done
        try:
            self.on_select(evt)
        except:
            pass
        group_id = str(self.room_list.GetItemData(self.cur_room_index))

        if self.NoGroups:
            self.NoGroups = False
            self.session.group_id = group_id
            self.on_server_dbclick()
            return

        if self.cur_room_index >= 0:
            if self.cur_room_index != 0:
                self.set_lobbybutton(1);
            else:
                self.set_lobbybutton(0);
            group = self.session.get_group_info(group_id)
            pwd = ""
            if (group[2] == "True") or (group[2] == "1"):
                pwd = self.password_manager.GetPassword("room", group_id)
            else:
                pwd = ""
            self.session.send_join_group(group_id, pwd)
        self.log.log("Exit game_server_panel->on_room_dbclick(self, evt)", ORPG_DEBUG)


    def on_select(self,evt):
        self.log.log("Enter game_server_panel->on_select(self,evt)", ORPG_DEBUG)
        id = evt.GetId()
        if id == LIST_ROOM:
            self.cur_room_index = evt.m_itemIndex
        elif id==LIST_SERVER:
            self.cur_server_index = evt.m_itemIndex
            self.name = self.svrList[self.cur_server_index].name
            address = self.svrList[self.cur_server_index].addy
            port = self.svrList[self.cur_server_index].port
            self.texts["address"].SetValue(address+":"+str(port))
            self.refresh_room_list()
        self.log.log("Exit game_server_panel->on_select(self,evt)", ORPG_DEBUG)

    def on_text(self,evt):
        self.log.log("Enter game_server_panel->on_text(self,evt)", ORPG_DEBUG)
        id = evt.GetId()
        if (id == ADDRESS) and (self.cur_server_index >= 0):
            #print "ADDRESS id = ", id, "index = ", self.cur_server_index
            self.cur_server_index = -1
        evt.Skip()
        self.log.log("Exit game_server_panel->on_text(self,evt)", ORPG_DEBUG)

    def add_room(self,data):
        self.log.log("Enter game_server_panel->add_room(self,data)", ORPG_DEBUG)
        i = self.room_list.GetItemCount()
        if (data[2]=="1") or (data[2]=="True"): pwd="yes"
        else: pwd="no"
        self.room_list.InsertStringItem(i,data[1])
        self.room_list.SetStringItem(i,1,data[3])
        self.room_list.SetStringItem(i,2,pwd)
        self.room_list.SetItemData(i,int(data[0]))
        self.refresh_room_list()
        self.log.log("Exit game_server_panel->add_room(self,data)", ORPG_DEBUG)

    def del_room(self, data):
        self.log.log("Enter game_server_panel->del_room(self, data)", ORPG_DEBUG)
        i = self.room_list.FindItemData(-1, int(data[0]))
        self.room_list.DeleteItem(i)
        self.refresh_room_list()
        self.log.log("Exit game_server_panel->del_room(self, data)", ORPG_DEBUG)

#---------------------------------------------------------
# [START] Snowdog Password/Room Name altering code 12/02
#---------------------------------------------------------

    def update_room(self,data):
        self.log.log("Enter game_server_panel->update_room(self,data)", ORPG_DEBUG)

        #-------------------------------------------------------
        # Udated 12/02 by Snowdog
        # allows refresh of all room data not just player counts
        #-------------------------------------------------------
        i = self.room_list.FindItemData(-1,int(data[0]))
        if data[2]=="1" : pwd="yes"
        else: pwd="no"
        self.room_list.SetStringItem(i,0,data[1])
        self.room_list.SetStringItem(i,1,data[3])
        self.room_list.SetStringItem(i,2,pwd)
        self.refresh_room_list()
        self.log.log("Exit game_server_panel->update_room(self,data)", ORPG_DEBUG)

#---------------------------------------------------------
# [END] Snowdog Password/Room Name altering code 12/02
#---------------------------------------------------------

    def set_cur_room_text(self,name):
        pass
        #self.texts["cur_room"].SetLabel(name)
        #self.sizers["room"].Layout()

    def set_lobbybutton(self,allow):
        self.log.log("Enter game_server_panel->set_lobbybutton(self,allow)", ORPG_DEBUG)
        self.buttons[GS_JOINLOBBY].Enable(allow)
        self.log.log("Exit game_server_panel->set_lobbybutton(self,allow)", ORPG_DEBUG)

    def set_connected(self,connected):
        self.log.log("Enter game_server_panel->set_connected(self,connected)", ORPG_DEBUG)
        self.buttons[GS_CONNECT].Enable(not connected)
        self.buttons[GS_DISCONNECT].Enable(connected)
        self.buttons[GS_JOIN].Enable(connected)
        self.buttons[GS_CREATE_ROOM].Enable(connected)
        if not connected:
            self.buttons[GS_JOINLOBBY].Enable(connected)
            self.room_list.DeleteAllItems()
            self.set_cur_room_text("Not Connected!")
            self.cur_room_index = -1
            self.frame.status.set_connect_status("Not Connected")
        else:
            #data = self.session.get_my_group()
            self.frame.status.set_connect_status(self.name)
            self.set_cur_room_text("Lobby")
        self.log.log("Exit game_server_panel->set_connected(self,connected)", ORPG_DEBUG)

    def on_button(self,evt):
        self.log.log("Enter game_server_panel->son_button(self,evt)", ORPG_DEBUG)
        id = evt.GetId()
        if id == GS_CONNECT:
            address = self.texts["address"].GetValue()
            ### check to see if this is a manual entry vs. list entry.
            try:
                dummy = self.name
            except:
                self.name = `address`
            self.do_connect(address)
        elif id == GS_DISCONNECT:
            self.frame.kill_mplay_session()
        elif id == GS_CREATE_ROOM:
            self.do_create_group()
        elif id == GS_JOIN:
            self.do_join_group()
        elif id == GS_JOINLOBBY:
            self.do_join_lobby()
        elif id == GS_SERVER_REFRESH:
            self.refresh_server_list()
        elif id == GS_PWD:
            self.texts["room_pwd"].Enable(evt.Checked())
        elif id == OR_CLOSE:
            dlg = wx.MessageDialog(self,"Quit OpenRPG?","OpenRPG",wx.YES_NO)
            if dlg.ShowModal() == wx.ID_YES:
                dlg.Destroy()
                self.frame.kill_mplay_session()
                self.frame.closed_confirmed()
        elif id == GS_CLOSE:
            self.parent.OnMB_GameServerBrowseServers()
        self.log.log("Exit game_server_panel->son_button(self,evt)", ORPG_DEBUG)

    def refresh_room_list(self):
        self.log.log("Enter game_server_panel->refresh_room_list(self)", ORPG_DEBUG)
        self.room_list.DeleteAllItems()
        address = self.texts["address"].GetValue()
        try:
            cadder = self.session.host_server
        except:
            cadder = ''
        if self.rmList.has_key(address) and len(self.rmList[address]) > 0 and cadder != address:
            groups = self.rmList[address]
            self.NoGroups = True
        else:
            self.NoGroups = False
            groups = self.session.get_groups()
        for g in groups:
            i = self.room_list.GetItemCount()
            if (g[2]=="True") or (g[2]=="1") : pwd="yes"
            else: pwd="no"
            self.room_list.InsertStringItem(i, g[1])
            self.room_list.SetStringItem(i, 1, g[3])
            self.room_list.SetStringItem(i, 2, pwd)
            self.room_list.SetItemData(i, int(g[0]))
        if self.room_list.GetItemCount() > 0:
            self.colorize_group_list(groups)
            self.room_list.SortItems(roomCmp)
            wx.CallAfter(self.autosizeRooms)
        self.log.log("Exit game_server_panel->refresh_room_list(self)", ORPG_DEBUG)

    def autosizeRooms(self):
        self.log.log("Enter game_server_panel->autosizeRooms(self)", ORPG_DEBUG)
        self.room_list.SetColumnWidth(0, wx.LIST_AUTOSIZE)
        #self.room_list.SetColumnWidth(1, wx.LIST_AUTOSIZE)
        #self.room_list.SetColumnWidth(2, wx.LIST_AUTOSIZE)
        if self.room_list.GetColumnWidth(0) < 70: self.room_list.SetColumnWidth(0, 70)
        if self.room_list.GetColumnWidth(1) < 70: self.room_list.SetColumnWidth(1, 70)
        if self.room_list.GetColumnWidth(2) < 50: self.room_list.SetColumnWidth(2, 50)
        self.log.log("Exit game_server_panel->autosizeRooms(self)", ORPG_DEBUG)

    def refresh_server_list(self):
        self.log.log("Enter game_server_panel->refresh_server_list(self)", ORPG_DEBUG)

        try:
            self.svrList = []
            self.server_list.DeleteAllItems()
            xml_dom = meta_server_lib.get_server_list(["2"]);
            node_list = xml_dom.getElementsByTagName('server')
            hex = orpg.tools.rgbhex.RGBHex()
            color1 = self.settings.get_setting("RoomColor_Active")
            color2 = self.settings.get_setting("RoomColor_Locked")
            color3 = self.settings.get_setting("RoomColor_Empty")
            color4 = self.settings.get_setting("RoomColor_Lobby")

            if len(node_list):
                length = len(node_list)
                part = 0
                partLength = 1.0/length
                for n in node_list:
                    if n.hasAttribute('id') and n.hasAttribute('name') and n.hasAttribute('num_users') and n.hasAttribute('address') and n.hasAttribute('port'):
                        self.svrList.append( server_instance(n.getAttribute('id'),n.getAttribute('name'), n.getAttribute('num_users'), n.getAttribute('address'),n.getAttribute('port')))
                        address = n.getAttribute('address') + ':' + n.getAttribute('port')
                        self.rmList[address] = []
                        rooms = n.getElementsByTagName('room')

                        for room in rooms:
                            pwd = room.getAttribute("pwd")
                            id = room.getAttribute("id")
                            name = room.getAttribute("name")
                            nump = room.getAttribute("num_users")
                            self.rmList[address].append((id, name, pwd, nump))
                self.svrList.sort(server_instance_compare)

                for n in self.svrList:
                    i = self.server_list.GetItemCount()
                    name = n.name
                    players = n.user
                    self.server_list.InsertStringItem(i,players)
                    self.server_list.SetStringItem(i,1,name)
                    r,g,b = hex.rgb_tuple(color1)
                    svrcolor = wx.Colour(red=r,green=g,blue=b)

                    if players == "0":
                        r,g,b = hex.rgb_tuple(color3)
                        svrcolor = wx.Colour(red=r,green=g,blue=b)

                    if n.name.startswith("OpenRPG DEV"):
                        r,g,b = hex.rgb_tuple(color2)
                        svrcolor = wx.Colour(red=r,green=g,blue=b)

                    item = self.server_list.GetItem(i)
                    item.SetTextColour(svrcolor)
                    self.server_list.SetItem(item)
                    part += partLength
                self.servers = node_list

            # No server is currently selected!!!  Versus the broken and random 0!
            self.cur_server_index = -1
            self.server_list.SetColumnWidth(0, wx.LIST_AUTOSIZE)
            if self.server_list.GetColumnWidth(0) < 70: self.server_list.SetColumnWidth(0, 70)
            self.server_list.SetColumnWidth(1, wx.LIST_AUTOSIZE)

            if self.serverNameSet == 0:
                # Pointless to constantly set the address field to random
                # server.  This way, at least, if someone has their own local
                # server it can now easily be connected with.  Nor do we want
                # to reset this every time as it would wipe any previously
                # entered data or even the previously selected server data!
                # Localhost should probably be used but some systems are ultra/lame
                # broken about localhost use.
                self.texts["address"].SetValue("127.0.0.1:6774")
                self.serverNameSet = 1
            else:
                pass

            #  Allow xml_dom to be collected
            try:
                xml_dom.unlink()
            except:
                pass
        except Exception, e:
            print "Server List not available."
            traceback.print_exc()
        self.log.log("Exit game_server_panel->refresh_server_list(self)", ORPG_DEBUG)

    def failed_connection(self):
        self.log.log("Enter game_server_panel->failed_connection(self)", ORPG_DEBUG)
        if(self.cur_server_index >= 0):
            id = self.servers[self.cur_server_index].getAttribute('id')
            meta = self.servers[self.cur_server_index].getAttribute('meta')
            address = self.servers[self.cur_server_index].getAttribute('address')
            port = self.servers[self.cur_server_index].getAttribute('port')
            #  post_failed_connection will return a non-zero if the server
            #  was removed.  If it was, refresh the display
            if(meta_server_lib.post_failed_connection(id,meta=meta,address=address,port=port)):
                self.refresh_server_list()
        self.log.log("Exit game_server_panel->failed_connection(self)", ORPG_DEBUG)

    def do_connect(self, address):
        self.log.log("Enter game_server_panel->do_connect(self, address)", ORPG_DEBUG)
        chat = open_rpg.get_component('chat')
        chat.InfoPost("Locating server at " + address + "...")
        if self.session.connect(address):
            self.frame.start_timer()
        else:
            chat.SystemPost("Failed to connect to game server...")
            self.failed_connection()
        self.log.log("Exit game_server_panel->do_connect(self, address)", ORPG_DEBUG)

    def do_join_lobby(self):
        self.log.log("Enter game_server_panel->do_join_lobby(self)", ORPG_DEBUG)
        self.cur_room_index = 0
        self.session.send_join_group("0","")
        self.set_lobbybutton(0);
        self.log.log("Exit game_server_panel->do_join_lobby(self)", ORPG_DEBUG)

    def do_join_group(self):
        self.log.log("Enter game_server_panel->do_join_group(self)", ORPG_DEBUG)
        if self.cur_room_index >= 0:
            if self.cur_room_index != 0:
                self.set_lobbybutton(1);
            else:
                self.set_lobbybutton(0);
            group_id = str(self.room_list.GetItemData(self.cur_room_index))
            group = self.session.get_group_info(group_id)
            pwd = ""
            if (group[2] == "True") or (group[2] == "1"):
                pwd = self.password_manager.GetPassword("room", group_id)
                #dlg = wx.TextEntryDialog(self,"Password?","Join Private Room")
                #if dlg.ShowModal() == wx.ID_OK:
                #    pwd = dlg.GetValue()
                #dlg.Destroy()
            else:
                pwd = ""
            if pwd != None: #pwd==None means the user clicked "Cancel"
                self.session.send_join_group(group_id,pwd)
        self.log.log("Exit game_server_panel->do_join_group(self)", ORPG_DEBUG)

    def do_create_group(self):
        self.log.log("Enter game_server_panel->do_create_group(self)", ORPG_DEBUG)
        name = self.texts["room_name"].GetValue()
        boot_pwd = self.texts["room_boot_pwd"].GetValue()
        minversion = self.texts["room_min_version"].GetValue()
        #
        # Check for & in name.  We want to allow this becaus of its common use in D&D.
        #
        loc = name.find("&")
        oldloc=0
        while loc > -1:
            loc = name.find("&",oldloc)
            if loc > -1:
                b = name[:loc]
                e = name[loc+1:]
                name = b + "&amp;" + e
                oldloc = loc+1
        loc = name.find('"')
        oldloc=0
        while loc > -1:
            loc = name.find('"',oldloc)
            if loc > -1:
                b = name[:loc]
                e = name[loc+1:]
                name = b + "&quote;" + e
                oldloc = loc+1
        loc = name.find("'")
        oldloc=0
        while loc > -1:
            loc = name.find("'",oldloc)
            if loc > -1:
                b = name[:loc]
                e = name[loc+1:]
                name = b + "&#39;" + e
                oldloc = loc+1
        if self.buttons[GS_PWD].GetValue():
            pwd = self.texts["room_pwd"].GetValue()
        else:
            pwd = ""
        if name == "":
            wx.MessageBox("Invalid Name","Error");
        else:
            msg = "%s is creating room \'%s.\'" % (self.session.name, name)
            self.session.send( msg )
            self.session.send_create_group(name,pwd,boot_pwd,minversion)
            self.set_lobbybutton(1); #enable the Lobby quickbutton
        self.log.log("Exit game_server_panel->do_create_group(self)", ORPG_DEBUG)


#---------------------------------------------------------
# [START] Snowdog: Updated Game Server Window 12/02
#---------------------------------------------------------

    def on_size(self,evt):
        # set column widths for room list


        # set column widths for server list
        pass



#---------------------------------------------------------
# [END] Snowdog: Updated Game Server Window 12/02
#---------------------------------------------------------


    def colorize_group_list(self, groups):
        self.log.log("Enter game_server_panel->colorize_group_list(self, groups)", ORPG_DEBUG)

        try:
            hex = orpg.tools.rgbhex.RGBHex()
#            activ = self.settings.get_setting("RoomColor_Active")
#            lockt = self.settings.get_setting("RoomColor_Locked")
#            empty = self.settings.get_setting("RoomColor_Empty")
#            lobby = self.settings.get_setting("RoomColor_Lobby")
#renamed colors - TaS sirebral

            for gr in groups:
                item_list_location = self.room_list.FindItemData(-1,int(gr[0]))
                if item_list_location != -1:
                    item = self.room_list.GetItem(item_list_location)
                    if gr[0] == "0":
#                        active_state = lobby
			r,g,b = hex.rgb_tuple(self.settings.get_setting("RoomColor_Lobby"))
                    elif gr[3] <> "0":
#                        active_state = activ
                        if gr[2] == "True" or gr[2] == "1":
#                           active_state = lockt
			   r,g,b = hex.rgb_tuple(self.settings.get_setting("RoomColor_Locked"))
			else:
#			   active_state = activ
			   r,g,b = hex.rgb_tuple(self.settings.get_setting("RoomColor_Active"))
                    else:
#                        active_state = empty
			r,g,b = hex.rgb_tuple(self.settings.get_setting("RoomColor_Empty"))
                        
#                    r,g,b = hex.rgb_tuple(active_state)
		    color = wx.Colour(red=r,green=g,blue=b)
                    item.SetTextColour(color)
                    self.room_list.SetItem(item)
        except:
            traceback.print_exc()
        self.log.log("Exit game_server_panel->colorize_group_list(self, groups)", ORPG_DEBUG)
