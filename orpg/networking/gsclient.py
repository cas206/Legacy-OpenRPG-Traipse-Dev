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
#   $Id: gsclient.py,v Traipse 'Ornery-Orc' prof.ebral Exp $
#
# Description: The file contains code for the game server browser
#

from __future__ import with_statement
__version__ = "$Id: gsclient.py,v Traipse 'Ornery-Orc' prof.ebral Exp $"

import meta_server_lib
import orpg.tools.rgbhex
import traceback

from orpg.dirpath import dir_struct
from orpg.orpg_windows import *
from orpg.tools.validate import validate
from orpg.orpgCore import component
from orpg.tools.orpg_settings import settings
from orpg.tools.orpg_log import debug

from xml.etree.ElementTree import ElementTree, Element
from xml.etree.ElementTree import fromstring, tostring

gs_host = 1
gs_join = 2
# constants

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
    xname = x.name
    xuser = int(x.user)
    yname = y.name
    yuser = int(y.user)

    who_name = cmp(yname, xname)
    who_user = cmp(yuser, xuser)

    if x.name.startswith(DEV_SERVER):
        if y.name.startswith(DEV_SERVER):
            if not who_name: return who_user
            else: return who_name
        else: return -1

    elif y.name.startswith(DEV_SERVER): return 1
    elif not who_user: return who_name
    else: return who_user

def roomCmp(room1, room2):
    if int(room1) > int(room2): return 1
    elif int(room1) < int(room2): return -1
    return 0

class game_server_panel(wx.Panel):
    def __init__(self,parent):
        wx.Panel.__init__(self, parent, -1)
        self.parent = parent
        self.password_manager = component.get('password_manager')
        self.frame = component.get('frame')
        self.session = component.get('session')
        self.serverNameSet = 0
        self.last_motd = ""
        self.buttons = {}
        self.texts = {}
        self.svrList = []
        self.build_ctrls()
        self.bookmarks()
        self.refresh_server_list()
        self.refresh_room_list()
        self.build_bookmark_menu() 

    def build_ctrls(self):
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
        self.texts["address"] = wx.TextCtrl(self, wx.ID_ANY)
        servers = wx.StaticText(self, -1, "Servers:")
        self.server_list = wx.ListCtrl(self, wx.ID_ANY, style=wx.LC_REPORT | wx.SUNKEN_BORDER )
        self.server_list.InsertColumn(0, '', wx.LIST_FORMAT_LEFT, 0)
        self.server_list.InsertColumn(1, "Players", wx.LIST_FORMAT_LEFT, 0)
        self.server_list.InsertColumn(2, "Name", wx.LIST_FORMAT_LEFT, 0)
        self.buttons['gs_connect'] = wx.Button(self, wx.ID_ANY, "Connect")
        self.buttons['gs_refresh'] = wx.Button(self, wx.ID_ANY, "Refresh")
        self.buttons['gs_disconnect'] = wx.Button(self, wx.ID_ANY, "Disconnect")
        self.sizers["svrbtns"] = wx.BoxSizer(wx.HORIZONTAL)
        self.sizers["svrbtns"].Add(self.buttons['gs_connect'], 0, wx.EXPAND)
        self.sizers["svrbtns"].Add(self.buttons['gs_refresh'], 0, wx.EXPAND)
        self.sizers["svrbtns"].Add(self.buttons['gs_disconnect'], 0, wx.EXPAND)
        self.sizers["server"].Add(adder, 0, wx.EXPAND)
        self.sizers["server"].Add(self.texts["address"], 0, wx.EXPAND)
        self.sizers["server"].Add(servers, 0, wx.EXPAND)
        self.sizers["server"].Add(self.server_list, 1, wx.EXPAND)
        self.sizers["server"].Add(self.sizers["svrbtns"], 0, wx.EXPAND)

        #Build Rooms Sizer
        self.room_list = wx.ListCtrl(self, wx.ID_ANY, style=wx.LC_REPORT | wx.SUNKEN_BORDER)
        self.room_list.InsertColumn(0,"Game", wx.LIST_FORMAT_LEFT,-1)
        self.room_list.InsertColumn(1,"Players", wx.LIST_FORMAT_LEFT,-1)
        self.room_list.InsertColumn(2,"PW", wx.LIST_FORMAT_LEFT,-1)
        self.buttons['gs_join_room'] = wx.Button(self, wx.ID_ANY, "Join Room")
        self.buttons['gs_join_lobby'] = wx.Button(self, wx.ID_ANY, "Lobby")
        self.sizers["roombtns"] = wx.BoxSizer(wx.HORIZONTAL)
        self.sizers["roombtns"].Add(self.buttons['gs_join_room'], 0, wx.EXPAND)
        self.sizers["roombtns"].Add(self.buttons['gs_join_lobby'], 0, wx.EXPAND)
        self.sizers["rooms"].Add(self.room_list, 1, wx.EXPAND)
        self.sizers["rooms"].Add(self.sizers["roombtns"], 0, wx.EXPAND)

        #Build Close Sizer
        self.buttons['close_orpg'] = wx.Button(self, wx.ID_ANY,"Exit OpenRPG")
        self.buttons['gs_close'] = wx.Button(self, wx.ID_ANY,"Close Window")
        self.sizers["close"].Add(self.buttons['close_orpg'], 1, wx.ALIGN_CENTER_VERTICAL)
        self.sizers["close"].Add(self.buttons['gs_close'], 1, wx.ALIGN_CENTER_VERTICAL)

        #Build Create Room Sizer
        rname = wx.StaticText(self,-1, "Room Name:")
        self.texts["room_name"] = wx.TextCtrl(self, -1)
        rpass = wx.StaticText(self,-1, "Password:")
        self.buttons['gs_pwd'] = wx.CheckBox(self, wx.ID_ANY, "")
        self.texts["room_pwd"] = wx.TextCtrl(self, -1)
        self.texts["room_pwd"].Enable(0)
        pwsizer = wx.BoxSizer(wx.HORIZONTAL)
        pwsizer.Add(self.buttons['gs_pwd'],0,0)
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
        self.buttons['gs_create_room'] = wx.Button(self, wx.ID_ANY, "Create Room")
        self.sizers["c_room"].Add(self.sizers["c_room_layout"], 1, wx.EXPAND)
        self.sizers["c_room"].Add(self.buttons['gs_create_room'], 0, wx.EXPAND)

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
        self.Bind(wx.EVT_BUTTON, self.gs_connect, self.buttons['gs_connect'])
        self.Bind(wx.EVT_BUTTON, self.gs_disconnect, self.buttons['gs_disconnect'])
        self.Bind(wx.EVT_BUTTON, self.gs_create_room, self.buttons['gs_create_room'])
        self.Bind(wx.EVT_BUTTON, self.gs_join, self.buttons['gs_join_room'])
        self.Bind(wx.EVT_BUTTON, self.gs_join_lobby, self.buttons['gs_join_lobby'])
        self.Bind(wx.EVT_BUTTON, self.gs_server_refresh, self.buttons['gs_refresh'])
        self.Bind(wx.EVT_BUTTON, self.gs_close, self.buttons['gs_close'])
        self.Bind(wx.EVT_BUTTON, self.close_orpg, self.buttons['close_orpg'])
        self.Bind(wx.EVT_CHECKBOX, self.gs_pwd, self.buttons['gs_pwd'])

        # Added double click handlers 5/05 -- Snowdog
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.on_server_dbclick, self.server_list)
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.on_room_dbclick, self.room_list)
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.on_room_select, self.room_list)
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.on_server_select, self.server_list)
        self.texts['address'].Bind(wx.EVT_SET_FOCUS, self.on_text)
        self.set_connected(self.session.is_connected())
        self.cur_room_index = -1
        self.cur_server_index = -1
        self.rmList = {}
        
        # Create Book Mark Image List
        self.server_list.Bind(wx.EVT_LEFT_DOWN, self.on_hit)
        self._imageList = wx.ImageList( 16, 16, False )
        img = wx.Image(dir_struct["icon"]+"add.png", wx.BITMAP_TYPE_PNG).ConvertToBitmap()
        self._imageList.Add( img )
        img = wx.Image(dir_struct["icon"]+"star.png", wx.BITMAP_TYPE_PNG).ConvertToBitmap()
        self._imageList.Add( img )
        self.server_list.SetImageList( self._imageList, wx.IMAGE_LIST_SMALL )
        
    def bookmarks(self):
        validate.config_file('server_bookmarks.xml',
                             'default_server_bookmarks.xml')
        self.bookmarks = ElementTree()
        self.bookmarks.parse(dir_struct['user'] + 'server_bookmarks.xml')

    def build_bookmark_menu(self):
        gsm = self.frame.mainmenu.GetMenu(
            self.frame.mainmenu.FindMenu('Game Server'))
        self.bookmarks_menu = wx.Menu()
        x = 0
        for server in self.bookmarks.findall('server'):
            for svr in self.svrList:
                address = svr.addy
                if server.get('address') == address: self.server_list.SetItemImage(x, 1)
                x += 1
            item = wx.MenuItem(self.bookmarks_menu, wx.ID_ANY,
                               server.get('name'), server.get('name'))
            open_rpg.get_component('frame').Bind(wx.EVT_MENU,
                                                 self.on_bookmarks_menu, item)
            self.bookmarks_menu.AppendItem(item)
        gsm.AppendSubMenu(self.bookmarks_menu, "Bookmarks")

    def on_bookmarks_menu(self, evt):
        id = evt.GetId()
        menu = self.bookmarks_menu.FindItemById(id)
        for server in self.bookmarks.findall('server'):
            if server.get('name') == menu.GetLabel():
                address = server.get('address')
                self.cur_server_index = 999
                self.name = server.get('name')
                self.texts["address"].SetValue(address)
                if self.session.is_connected():
                    if self.session.host_server == address : return
                    else: self.frame.kill_mplay_session()
                self.do_connect(address)
                break
        
    def bookmark(self, item, flag):
        name = self.svrList[item].name
        address = self.svrList[item].addy
        port = self.svrList[item].port
        self.server_list.SetItemImage(item, 1)
        for server in self.bookmarks.findall('server'):
            if server.get('name') == name:
                self.bookmarks_menu.Remove(
                    self.bookmarks_menu.FindItem(server.get('name')))
                self.bookmarks.getroot().remove(server)
                self.server_list.SetItemImage(item, 0)
                break
        else:
            server = Element('server')
            server.set('name', name)
            server.set('address', address + ':' + port)
            self.bookmarks.getroot().append(server)
            item = wx.MenuItem(self.bookmarks_menu, wx.ID_ANY, name, name)
            open_rpg.get_component('frame').Bind(wx.EVT_MENU,
                                                 self.on_bookmarks_menu, item)
            self.bookmarks_menu.AppendItem(item)
        self.save_bookmarks()

    def save_bookmarks(self):
        with open(dir_struct['user'] + 'server_bookmarks.xml', 'w') as f:
            self.bookmarks.write(f)

    def on_server_dbclick(self, evt=None):
        #make sure address is updated just in case list select wasn't done
        try: self.on_select(evt)
        except: pass
        address = self.texts["address"].GetValue()
        if self.session.is_connected():
            if self.session.host_server == address : return 
            else: self.frame.kill_mplay_session()
        self.do_connect(address)

    def on_room_dbclick(self, evt=None):
        #make sure address is updated just in case list select wasn't done
        try: self.on_select(evt)
        except: pass
        group_id = str(self.room_list.GetItemData(self.cur_room_index))
        if self.NoGroups:
            self.NoGroups = False
            self.session.group_id = group_id
            self.on_server_dbclick()
            return
        if self.cur_room_index >= 0:
            if self.cur_room_index != 0: self.set_lobbybutton(1);
            else: self.set_lobbybutton(0);
            group = self.session.get_group_info(group_id)
            pwd = ""
            if (group[2] == "True") or (group[2] == "1"):
                pwd = self.password_manager.GetPassword("room", group_id)
            else: pwd = ""
            self.session.send_join_group(group_id, pwd)

    def on_room_select(self,evt):
        self.cur_room_index = evt.m_itemIndex

    def on_hit(self, evt):
        pos = wx.Point( evt.GetX(), evt.GetY() )
        (item, flag) = self.server_list.HitTest( pos )
        ## Item == list[server], flag == (32 = 0 colum, 128 = else) ##
        if flag == 32: self.bookmark(item, flag)
        evt.Skip()
        
    def on_server_select(self,evt):
        self.cur_server_index = evt.m_itemIndex
        self.name = self.svrList[self.cur_server_index].name
        address = self.svrList[self.cur_server_index].addy
        port = self.svrList[self.cur_server_index].port
        self.texts["address"].SetValue(address + ":" + str(port))
        self.refresh_room_list()

    def on_text(self, evt):
        id = evt.GetId()
        if (id == self.texts["address"].GetValue()) and (self.cur_server_index >= 0):
            self.cur_server_index = -1
        evt.Skip()

    def add_room(self, data):
        i = self.room_list.GetItemCount()
        if (data[2]=="1") or (data[2]=="True"): pwd="yes"
        else: pwd="no"
        self.room_list.InsertStringItem(i,data[1])
        self.room_list.SetStringItem(i,1,data[3])
        self.room_list.SetStringItem(i,2,pwd)
        self.room_list.SetItemData(i,int(data[0]))
        self.refresh_room_list()

    def del_room(self, data):
        i = self.room_list.FindItemData(-1, int(data[0]))
        self.room_list.DeleteItem(i)
        self.refresh_room_list()

    def update_room(self, data):
        i = self.room_list.FindItemData(-1,int(data[0]))
        if data[2]=="1" : pwd="yes"
        else: pwd="no"
        self.room_list.SetStringItem(i,0,data[1])
        self.room_list.SetStringItem(i,1,data[3])
        self.room_list.SetStringItem(i,2,pwd)
        self.refresh_room_list()

    def set_cur_room_text(self, name):
        pass
        #self.texts["cur_room"].SetLabel(name)
        #self.sizers["room"].Layout()

    def set_lobbybutton(self, allow):
        self.buttons['gs_join_lobby'].Enable(allow)

    def set_connected(self, connected):
        self.buttons['gs_connect'].Enable(not connected)
        self.buttons['gs_disconnect'].Enable(connected)
        self.buttons['gs_join_room'].Enable(connected)
        self.buttons['gs_create_room'].Enable(connected)
        if not connected:
            self.buttons['gs_join_lobby'].Enable(connected)
            self.room_list.DeleteAllItems()
            self.set_cur_room_text("Not Connected!")
            self.cur_room_index = -1
            self.frame.status.set_connect_status("Not Connected")
        else:
            self.frame.status.set_connect_status(self.name)
            self.set_cur_room_text("Lobby")

    def gs_connect(self, evt):
        address = self.texts['address'].GetValue()
        try: dummy = self.name
        except: self.name = `address`
        self.do_connect(address)
        
    def gs_disconnect(self, evt):
        self.frame.kill_mplay_session()
        
    def gs_create_room(self, evt):
        self.do_create_group()
    
    def gs_join(self, evt):
        self.do_join_group()
        
    def gs_join_lobby(self, evt):
        self.do_join_lobby()
        
    def gs_server_refresh(self, evt):
        self.refresh_server_list()
        
    def gs_pwd(self, evt):
        self.texts['room_pwd'].Enable(evt.Checked())
        
    def close_orpg(self, evt):
        dlg = wx.MessageDialog(self, 'Quit OpenRPG?', "OpenRPG", wx.YES_NO)
        if dlg.ShowModal() == wx.ID_YES:
            dlg.Destroy()
            self.frame.kill_mplay_session()
            self.frame.closed_confirmed()
    
    def gs_close(self, evt):
        self.parent.OnMB_GameServerBrowseServers()
        
    def refresh_room_list(self):
        self.room_list.DeleteAllItems()
        address = self.texts["address"].GetValue()
        try: cadder = self.session.host_server
        except: cadder = ''
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

    def autosizeRooms(self):
        self.room_list.SetColumnWidth(0, wx.LIST_AUTOSIZE)
        if self.room_list.GetColumnWidth(0) < 70: self.room_list.SetColumnWidth(0, 70)
        if self.room_list.GetColumnWidth(1) < 70: self.room_list.SetColumnWidth(1, 70)
        if self.room_list.GetColumnWidth(2) < 50: self.room_list.SetColumnWidth(2, 50)

    def refresh_server_list(self):
        try:
            self.svrList = []
            self.server_list.DeleteAllItems()
            etreeEl = meta_server_lib.get_server_list(["2"]);
            node_list = etreeEl.findall('server')
            hex = orpg.tools.rgbhex.RGBHex()
            color1 = settings.get("RoomColor_Active")
            color2 = settings.get("RoomColor_Locked")
            color3 = settings.get("RoomColor_Empty")
            color4 = settings.get("RoomColor_Lobby")

            if len(node_list):
                length = len(node_list)
                part = 0
                partLength = 1.0/length
                for n in node_list:
                    self.svrList.append(server_instance(n.get('id'), n.get('name'), 
                                        n.get('num_users'), n.get('address'), 
                                        n.get('port')))
                    address = n.get('address') + ':' + n.get('port')
                    self.rmList[address] = []
                    rooms = n.findall('room')

                    for room in rooms:
                        self.rmList[address].append((room.get("id"), room.get("name"), 
                                                    room.get("pwd"), room.get("num_users")))
                self.svrList.sort(server_instance_compare)

                for n in self.svrList:
                    i = self.server_list.GetItemCount()
                    name = n.name
                    players = n.user
                    self.server_list.InsertImageStringItem(i, '', 0)
                    for server in self.bookmarks.findall('server'):
                        if server.get('name') == name: self.server_list.SetItemImage(i, 1)
                    self.server_list.SetStringItem(i,1,players)
                    self.server_list.SetStringItem(i,2,name)
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
            self.server_list.SetColumnWidth(1, wx.LIST_AUTOSIZE)
            if self.server_list.GetColumnWidth(1) < 70: self.server_list.SetColumnWidth(1, 70)
            self.server_list.SetColumnWidth(2, wx.LIST_AUTOSIZE)

            if self.serverNameSet == 0:
                self.texts["address"].SetValue("127.0.0.1:6774")
                self.serverNameSet = 1
            else: pass
        except Exception, e:
            print "Server List not available."
            traceback.print_exc()
            
    def failed_connection(self):
        if(self.cur_server_index >= 0):
            server_index = self.servers[self.cur_server_index]
            if(meta_server_lib.post_failed_connection(server_index.get('id'), 
                meta=server_index.get('meta'), address=server_index.get('address'),
                port=server_index.get('port'))):
                self.refresh_server_list()

    def do_connect(self, address):
        chat = component.get('chat')
        chat.InfoPost("Locating server at " + address + "...")
        if self.session.connect(address): self.frame.start_timer()
        else:
            chat.SystemPost("Failed to connect to game server...")
            self.failed_connection()

    def do_join_lobby(self):
        self.cur_room_index = 0
        self.session.send_join_group("0", "")
        self.set_lobbybutton(0);

    def do_join_group(self):
        if self.cur_room_index >= 0:
            if self.cur_room_index != 0: self.set_lobbybutton(1);
            else: self.set_lobbybutton(0);
            group_id = str(self.room_list.GetItemData(self.cur_room_index))
            group = self.session.get_group_info(group_id)
            pwd = ""
            if (group[2] == "True") or (group[2] == "1"):
                pwd = self.password_manager.GetPassword("room", group_id)
                #dlg = wx.TextEntryDialog(self,"Password?","Join Private Room")
                #if dlg.ShowModal() == wx.ID_OK:
                #    pwd = dlg.GetValue()
                #dlg.Destroy()
            else: pwd = ""
            if pwd != None: #pwd == None means the user clicked "Cancel"
                self.session.send_join_group(group_id, pwd)

    def do_create_group(self):
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
        if self.buttons['gs_pwd'].GetValue(): pwd = self.texts["room_pwd"].GetValue()
        else: pwd = ""
        if name == "": wx.MessageBox("Invalid Name","Error");
        else:
            msg = "%s is creating room \'%s.\'" % (self.session.name, name)
            self.session.send(msg)
            self.session.send_create_group(name, pwd, boot_pwd, minversion)
            self.set_lobbybutton(1); 

    def on_size(self, evt):
        pass

    def colorize_group_list(self, groups):
        try:
            hex = orpg.tools.rgbhex.RGBHex()
            for gr in groups:
                item_list_location = self.room_list.FindItemData(-1,int(gr[0]))
                if item_list_location != -1:
                    item = self.room_list.GetItem(item_list_location)
                    if gr[0] == "0": r,g,b = hex.rgb_tuple(settings.get("RoomColor_Lobby"))
                    elif gr[3] <> "0":
                        if gr[2] == "True" or gr[2] == "1":
			   r,g,b = hex.rgb_tuple(settings.get("RoomColor_Locked"))
			else: r,g,b = hex.rgb_tuple(settings.get("RoomColor_Active"))
                    else: r,g,b = hex.rgb_tuple(settings.get("RoomColor_Empty"))
		    color = wx.Colour(red=r,green=g,blue=b)
                    item.SetTextColour(color)
                    self.room_list.SetItem(item)
        except: traceback.print_exc()
