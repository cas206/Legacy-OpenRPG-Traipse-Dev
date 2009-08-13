#!/usr/bin/env python
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
# File: player_list.py
# Author: Chris Davis
# Maintainer:
# Version:
#   $Id: player_list.py,v 1.29 2007/03/30 19:12:06 digitalxero Exp $
#
# Description: This is the main entry point of the oprg application
#

__version__ = "$Id: player_list.py,v 1.29 2007/03/30 19:12:06 digitalxero Exp $"

from orpg.orpg_windows import *
import orpg.dirpath

# global definitions
global ROLE_GM; ROLE_GM = "GM"
global ROLE_PLAYER; ROLE_PLAYER = "PLAYER"
global ROLE_LURKER; ROLE_LURKER = "LURKER"

#########################
#player frame window
#########################
PLAYER_BOOT = wx.NewId()
PLAYER_WHISPER = wx.NewId()
PLAYER_IGNORE = wx.NewId()
PLAYER_ROLE_MENU = wx.NewId()
PLAYER_ROLE_LURKER = wx.NewId()
PLAYER_ROLE_PLAYER = wx.NewId()
PLAYER_ROLE_GM = wx.NewId()
PLAYER_MODERATE_MENU = wx.NewId()
PLAYER_MODERATE_ROOM_ON = wx.NewId()
PLAYER_MODERATE_ROOM_OFF = wx.NewId()
PLAYER_MODERATE_GIVE_VOICE = wx.NewId()
PLAYER_MODERATE_TAKE_VOICE = wx.NewId()
PLAYER_SHOW_VERSION = wx.NewId()
WG_LIST = {}

#---------------------------------------------------------
# [START] Digitalxero Multi Whisper Group 1/1/05
#---------------------------------------------------------
PLAYER_WG_MENU = wx.NewId()
PLAYER_WG_CREATE = wx.NewId()
PLAYER_WG_CLEAR_ALL = wx.NewId()
WG_MENU_LIST = {}
#---------------------------------------------------------
# [END] Digitalxero Multi Whisper Group 1/1/05
#---------------------------------------------------------

#---------------------------------------------------------
# [START] Snowdog Password/Room Name altering code 12/02
#---------------------------------------------------------
PLAYER_COMMAND_MENU = wx.NewId()
PLAYER_COMMAND_PASSWORD_ALTER = wx.NewId()
PLAYER_COMMAND_ROOM_RENAME = wx.NewId()
#---------------------------------------------------------
# [END] Snowdog Password/Room Name altering code 12/02
#---------------------------------------------------------

class player_list(wx.ListCtrl):
    def __init__( self, parent):
        ##wx.ListCtrl.__init__( self, parent, -1, wx.DefaultPosition, wx.DefaultSize, wx.LC_REPORT|wx.SUNKEN_BORDER|wx.EXPAND )
        wx.ListCtrl.__init__( self, parent, -1, wx.DefaultPosition, wx.DefaultSize, 
            wx.LC_REPORT|wx.SUNKEN_BORDER|wx.EXPAND|wx.LC_HRULES )
        self.session = open_rpg.get_component("session")
        self.settings = open_rpg.get_component('settings')
        self.chat = open_rpg.get_component('chat')
        self.password_manager = open_rpg.get_component("password_manager")
        # Create in image list -- for whatever reason...guess it will be nice when we can tell which is a bot
        self.whisperCount = 0
        self._imageList = wx.ImageList( 16, 16, False )
        img = wx.Image(orpg.dirpath.dir_struct["icon"]+"player.gif", wx.BITMAP_TYPE_GIF).ConvertToBitmap()
        self._imageList.Add( img )
        img = wx.Image(orpg.dirpath.dir_struct["icon"]+"player-whisper.gif", wx.BITMAP_TYPE_GIF).ConvertToBitmap()
        self._imageList.Add( img )
        self.SetImageList( self._imageList, wx.IMAGE_LIST_SMALL )
        # Create our column headers
        self.InsertColumn( 0, "ID" )
        self.InsertColumn( 1, "Player")
        self.InsertColumn( 2, "Status" )
#---------------------------------------------------------
# [START] Digitalxero Multi Whisper Group 1/1/05
#---------------------------------------------------------
        ##Main Menu
        self.wgMenu = wx.Menu()
        #Add the Base Menu items, so they are always at the bottom
        self.wgMenu.Append(PLAYER_WG_CREATE, "Create")
        self.wgMenu.Append(PLAYER_WG_CLEAR_ALL, "Delete All Groups")
#---------------------------------------------------------
# [END] Digitalxero Multi Whisper Group 1/1/05
#---------------------------------------------------------
        # Create the role menu
        self.roleMenu = wx.Menu()
        self.roleMenu.SetTitle( "Assign Role" )
        self.roleMenu.Append( PLAYER_ROLE_LURKER, "Lurker" )
        self.roleMenu.Append( PLAYER_ROLE_PLAYER, "Player" )
        self.roleMenu.Append( PLAYER_ROLE_GM, "GM" )
        # Create the moderation menu
        self.moderateMenu = wx.Menu()
        self.moderateMenu.SetTitle( "Moderate" )
        self.moderateMenu.Append( PLAYER_MODERATE_ROOM_ON, "Room Moderation ON" )
        self.moderateMenu.Append( PLAYER_MODERATE_ROOM_OFF, "Room Moderation OFF" )
        self.moderateMenu.AppendSeparator()
        self.moderateMenu.Append( PLAYER_MODERATE_GIVE_VOICE, "Give Voice" )
        self.moderateMenu.Append( PLAYER_MODERATE_TAKE_VOICE, "Take Voice" )
#---------------------------------------------------------
# [START] Snowdog Password/Room Name altering code 12/02
#---------------------------------------------------------
        # Create the room control menu
        self.commandMenu = wx.Menu()
        self.commandMenu.SetTitle( "Room Controls" )
        self.commandMenu.Append( PLAYER_COMMAND_PASSWORD_ALTER, "Password" )
        self.commandMenu.Append( PLAYER_COMMAND_ROOM_RENAME, "Room Name" )
        self.commandMenu.AppendSeparator()
#---------------------------------------------------------
# [END] Snowdog Password/Room Name altering code 12/02
#---------------------------------------------------------
        # Create the pop up menu
        self.menu = wx.Menu()
        self.menu.SetTitle( "Player Menu" )
        self.menu.Append( PLAYER_BOOT, "Boot" )
        self.menu.AppendSeparator()
        self.menu.Append( PLAYER_IGNORE, "Toggle &Ignore" )
        self.menu.AppendSeparator()
        self.menu.Append( PLAYER_WHISPER, "Whisper" )
#---------------------------------------------------------
# [START] Digitalxero Multi Whisper Group 1/1/05
#---------------------------------------------------------
        self.menu.AppendMenu(PLAYER_WG_MENU, "Whisper Groups", self.wgMenu)
#---------------------------------------------------------
# [END] Digitalxero Multi Whisper Group 1/1/05
#---------------------------------------------------------
        self.menu.AppendSeparator()
        self.menu.AppendMenu( PLAYER_MODERATE_MENU, "Moderate", self.moderateMenu )
        self.menu.AppendMenu( PLAYER_COMMAND_MENU, "Room Control", self.commandMenu )
        self.menu.AppendSeparator()
        self.menu.AppendMenu( PLAYER_ROLE_MENU, "Assign Role", self.roleMenu )
        self.menu.AppendSeparator()
        self.menu.Append( PLAYER_SHOW_VERSION, "Version" )
        # Event processing for our menu
        self.Bind(wx.EVT_MENU, self.on_menu_item, id=PLAYER_BOOT)
        self.Bind(wx.EVT_MENU, self.on_menu_item, id=PLAYER_IGNORE)
        self.Bind(wx.EVT_MENU, self.on_menu_item, id=PLAYER_WHISPER)
        self.Bind(wx.EVT_MENU, self.on_menu_moderate, id=PLAYER_MODERATE_ROOM_ON)
        self.Bind(wx.EVT_MENU, self.on_menu_moderate, id=PLAYER_MODERATE_ROOM_OFF)
        self.Bind(wx.EVT_MENU, self.on_menu_moderate, id=PLAYER_MODERATE_GIVE_VOICE)
        self.Bind(wx.EVT_MENU, self.on_menu_moderate, id=PLAYER_MODERATE_TAKE_VOICE)
        self.Bind(wx.EVT_MENU, self.on_menu_role_change, id=PLAYER_ROLE_LURKER)
        self.Bind(wx.EVT_MENU, self.on_menu_role_change, id=PLAYER_ROLE_PLAYER)
        self.Bind(wx.EVT_MENU, self.on_menu_role_change, id=PLAYER_ROLE_GM)
        self.Bind(wx.EVT_MENU, self.on_menu_item, id=PLAYER_SHOW_VERSION)
#---------------------------------------------------------
# [START] Digitalxero Multi Whisper Group 1/1/05
#---------------------------------------------------------
        self.Bind(wx.EVT_MENU, self.on_menu_whispergroup, id=PLAYER_WG_CREATE)
        self.Bind(wx.EVT_MENU, self.on_menu_whispergroup, id=PLAYER_WG_CLEAR_ALL)
#---------------------------------------------------------
# [END] Digitalxero Multi Whisper Group 1/1/05
#---------------------------------------------------------
#---------------------------------------------------------
# [START] Snowdog Password/Room Name altering code 12/02
#---------------------------------------------------------
        self.Bind(wx.EVT_MENU, self.on_menu_password, id=PLAYER_COMMAND_PASSWORD_ALTER)
        self.Bind(wx.EVT_MENU, self.on_menu_room_rename, id=PLAYER_COMMAND_ROOM_RENAME)
#---------------------------------------------------------
# [END] Snowdog Password/Room Name altering code 12/02
#---------------------------------------------------------
        self.Bind(wx.EVT_LEFT_DCLICK, self.on_d_lclick)
        self.Bind(wx.EVT_RIGHT_DOWN, self.on_menu)
        self.sized = 1
#---------------------------------------------------------
# [START] Snowdog Password/Room Name altering code 12/02
#
#       Revised 8/03 to add support for password manager
#---------------------------------------------------------

    def AutoAdjust(self):
        self.SetColumnWidth(0, -1)
        if self.GetColumnWidth(1) < 75: self.SetColumnWidth(1, 75)
        if self.GetColumnWidth(2) < 75: self.SetColumnWidth(2, 75)
        self.Refresh()

    def on_menu_password( self, evt ):
        id = evt.GetId()
        self.session = open_rpg.get_component("session")
        self.password_manager = open_rpg.get_component("password_manager")
        self.chat = open_rpg.get_component("chat")
        boot_pwd = self.password_manager.GetPassword("admin",int(self.session.group_id))
        if boot_pwd != None:
            alter_pwd_dialog = wx.TextEntryDialog(self,
                "Enter new room password: (blank for no password)","Alter Room Password")
            if alter_pwd_dialog.ShowModal() == wx.ID_OK:
                new_pass = alter_pwd_dialog.GetValue()
                self.chat.InfoPost( "Requesting password change on server..." )
                self.session.set_room_pass(new_pass, boot_pwd)

    def on_menu_room_rename( self, evt ):
        id = evt.GetId()
        self.session = open_rpg.get_component("session")
        self.password_manager = open_rpg.get_component("password_manager")
        self.chat = open_rpg.get_component("chat")
        boot_pwd = self.password_manager.GetPassword("admin",int(self.session.group_id))
        if boot_pwd != None:
            alter_name_dialog = wx.TextEntryDialog(self,"Enter new room name: ","Change Room Name")
            if alter_name_dialog.ShowModal() == wx.ID_OK:
                new_name = alter_name_dialog.GetValue()
                self.chat.InfoPost( "Requesting room name change on server..." )
                loc = new_name.find("&")
                oldloc=0
                while loc > -1:
                    loc = new_name.find("&",oldloc)
                    if loc > -1:
                        b = new_name[:loc]
                        e = new_name[loc+1:]
                        new_name = b + "&amp;" + e
                        oldloc = loc +1
                loc = new_name.find("'")
                oldloc=0
                while loc > -1:
                    loc = new_name.find("'",oldloc)
                    if loc > -1:
                        b = new_name[:loc]
                        e = new_name[loc+1:]
                        new_name = b + "&#39;" + e
                        oldloc = loc +1
                loc = new_name.find('"')
                oldloc=0
                while loc > -1:
                    loc = new_name.find('"',oldloc)
                    if loc > -1:
                        b = new_name[:loc]
                        e = new_name[loc+1:]
                        new_name = b + "&quote" + e
                        oldloc = loc +1
                self.session.set_room_name(new_name, boot_pwd)
#---------------------------------------------------------
# [END] Snowdog Password/Room Name altering code 12/02
#---------------------------------------------------------

#---------------------------------------------------------
# [START] Digitalxero Multi Whisper Group 1/1/05
#---------------------------------------------------------
    def clean_sub_menus(self):
        for mid in WG_MENU_LIST:
            try:
                self.wgMenu.Remove(WG_MENU_LIST[mid]["menuid"])
                WG_MENU_LIST[mid]["menu"].Destroy()
            except: self.wgMenu.UpdateUI()
        if self.wgMenu.GetMenuItemCount() == 2: WG_MENU_LIST.clear()
        return

    def on_menu_whispergroup( self, evt ):
        self.session = open_rpg.get_component("session")
        self.settings = open_rpg.get_component('settings')
        self.chat = open_rpg.get_component('chat')
        "Add/Remove players from Whisper Groups"
        id = evt.GetId()
        item = self.GetItem( self.selected_item )
        #See if it is the main menu
        if id == PLAYER_WG_CREATE:
            create_new_group_dialog = wx.TextEntryDialog(self,"Enter Group Name","Create New Whisper Group")
            if create_new_group_dialog.ShowModal() == wx.ID_OK:
                group_name = create_new_group_dialog.GetValue()
                WG_LIST[group_name] = {}
            return
        elif id == PLAYER_WG_CLEAR_ALL: WG_LIST.clear(); return
        #Check Sub Menus
        for mid in WG_MENU_LIST:
            if id == WG_MENU_LIST[mid]["add"]: WG_LIST[mid][int(item.GetText())] = int(item.GetText()); return
            elif id == WG_MENU_LIST[mid]["remove"]: del WG_LIST[mid][int(item.GetText())]; return
            elif id == WG_MENU_LIST[mid]["clear"]: WG_LIST[mid].clear(); return
            elif id == WG_MENU_LIST[mid]["whisper"]: self.chat.set_chat_text("/gw " + mid + "="); return
        return

#---------------------------------------------------------
# [END] Digitalxero Multi Whisper Group 1/1/05
#---------------------------------------------------------

    def on_menu_moderate( self, evt ):
        "Change the moderated status of a room or player."
        id = evt.GetId()
        self.chat = open_rpg.get_component( "chat" )
        self.session = open_rpg.get_component("session")
        playerID = self.GetItemData( self.selected_item )
        moderationString = None
        moderateRoomBase = "/moderate %s"
        moderatePlayerBase = "/moderate %d=%s"
        infoRoomBase = "Attempting to %s moderation in the current room..."
        infoPlayerBase = "Attempting to %s voice to %s (%d)..."

        if id == PLAYER_MODERATE_ROOM_ON:
            moderationString = (moderateRoomBase % "on")
            infoString = (infoRoomBase % "ENABLE")
        if id == PLAYER_MODERATE_ROOM_OFF:
            moderationString = (moderateRoomBase % "off")
            infoString = (infoRoomBase % "DISABLE")
        elif id == PLAYER_MODERATE_GIVE_VOICE:
            moderationString = (moderatePlayerBase % (playerID, "on"))
            infoString = (infoPlayerBase % ("GIVE", self.session.get_player_by_player_id( str(playerID) )[0], playerID))
        elif id == PLAYER_MODERATE_TAKE_VOICE:
            moderationString = (moderatePlayerBase % (playerID, "off"))
            infoString = (infoPlayerBase % ("TAKE", self.session.get_player_by_player_id( str(playerID) )[0], playerID))

        # Now, send it to the server
        if moderationString:
            self.chat.chat_cmds.docmd( moderationString )
            # Now, provide local feedback as to what we requested
            self.chat.InfoPost( infoString )

    def on_menu_role_change( self, evt ):
        self.session = open_rpg.get_component("session")
        "Change the role of the selected id."
        id = evt.GetId()
        self.chat = open_rpg.get_component( "chat" )
        playerID = self.GetItemData( self.selected_item )
        roleString = None
        roleBase = "/role %d=%s"
        infoBase = "Attempting to assign the role of %s to (%d) %s..."

        # Do type specific processing
	recycle_bin = {PLAYER_ROLE_LURKER: ROLE_LURKER, PLAYER_ROLE_PLAYER: ROLE_PLAYER, PLAYER_ROLE_GM: ROLE_GM}
	if recycle_bin.has_key(id):
	    roleName = recycle_bin[id]
	    roleString = (roleBase % ( playerID, roleName ))
	    recycle_bin = {}

        # Now, send it to the server
        if roleString:
            self.chat.chat_cmds.docmd( roleString )
            # Now, provide local feedback as to what we requested
            displayName = self.session.get_player_by_player_id( str(playerID) )[0]
            infoString = (infoBase % ( roleName, playerID, displayName ))
            self.chat.InfoPost( infoString )

    def on_d_lclick(self,evt):
        pos = wx.Point(evt.GetX(),evt.GetY())
        (item, flag) = self.HitTest(pos)
        id = self.GetItemText(item)
        self.chat = open_rpg.get_component("chat")
        self.chat.set_chat_text("/w " + id + "=")

    def on_menu_item(self,evt):
        id = evt.GetId()
        self.session = open_rpg.get_component("session")
        self.password_manager = open_rpg.get_component("password_manager")

        if id == PLAYER_BOOT:
            id = str(self.GetItemData(self.selected_item))
            boot_pwd = self.password_manager.GetPassword("admin",int(self.session.group_id))
            if boot_pwd != None: self.session.boot_player(id,boot_pwd)
        elif id == PLAYER_WHISPER:
            id = self.GetItemText(self.selected_item)
            self.chat = open_rpg.get_component("chat")
            self.chat.set_chat_text("/w " + id + "=")
        elif id == PLAYER_IGNORE:
            id = str(self.GetItemData(self.selected_item))
            self.chat = open_rpg.get_component("chat")
            (result,id,name) = self.session.toggle_ignore(id)
            if result == 0: self.chat.Post(self.chat.colorize(self.chat.syscolor, 
                "Player " + name + " with ID:" + id +" no longer ignored"))
            else: self.chat.Post(self.chat.colorize(self.chat.syscolor, 
                "Player " + name + " with ID:" + id +" now being ignored"))
        elif id == PLAYER_SHOW_VERSION:
            id = str(self.GetItemData(self.selected_item))
            version_string = self.session.players[id][6]
            if version_string: wx.MessageBox("Running client version " + version_string,"Version")
            else: wx.MessageBox("No client version available for this player","Version")

    def on_menu(self, evt):
        pos = wx.Point(evt.GetX(),evt.GetY())
        (item, flag) = self.HitTest(pos)
        if item > -1:
            self.selected_item = item
            #  This if-else block makes the menu item to boot players active or inactive, as appropriate
            # This block is enabled for 1.7.8. Ver. 1.7.9 will boast Admin features.
            #if open_rpg.get_component("session").group_id == "0":
            #    self.menu.Enable(PLAYER_BOOT,0)
            #    self.menu.SetLabel(PLAYER_BOOT,"Can't boot from Lobby")
            #else:
            self.menu.Enable(PLAYER_BOOT,1)
            self.menu.SetLabel(PLAYER_BOOT,"Boot")
#---------------------------------------------------------
# [START] Digitalxero Multi Whisper Group 1/1/05
#---------------------------------------------------------
            self.menu.Enable(PLAYER_WG_MENU, True)
            item = self.GetItem( self.selected_item )
            if len(WG_MENU_LIST) > len(WG_LIST): self.clean_sub_menus()
            if len(WG_LIST) == 0: self.wgMenu.Enable(PLAYER_WG_CLEAR_ALL, False)
            else: self.wgMenu.Enable(PLAYER_WG_CLEAR_ALL, True)
            for gid in WG_LIST:
                if not WG_MENU_LIST.has_key(gid):
                    WG_MENU_LIST[gid] = {}
                    WG_MENU_LIST[gid]["menuid"] = wx.NewId()
                    WG_MENU_LIST[gid]["whisper"] = wx.NewId()
                    WG_MENU_LIST[gid]["add"] = wx.NewId()
                    WG_MENU_LIST[gid]["remove"] = wx.NewId()
                    WG_MENU_LIST[gid]["clear"] = wx.NewId()
                    WG_MENU_LIST[gid]["menu"] = wx.Menu()
                    WG_MENU_LIST[gid]["menu"].SetTitle(gid)
                    WG_MENU_LIST[gid]["menu"].Append(WG_MENU_LIST[gid]["whisper"], "Whisper")
                    WG_MENU_LIST[gid]["menu"].Append(WG_MENU_LIST[gid]["add"], "Add")
                    WG_MENU_LIST[gid]["menu"].Append(WG_MENU_LIST[gid]["remove"], "Remove")
                    WG_MENU_LIST[gid]["menu"].Append(WG_MENU_LIST[gid]["clear"], "Clear")
                    self.wgMenu.PrependMenu(WG_MENU_LIST[gid]["menuid"], gid, WG_MENU_LIST[gid]["menu"])
                if WG_LIST[gid].has_key(int(item.GetText())):
                    WG_MENU_LIST[gid]["menu"].Enable(WG_MENU_LIST[gid]["remove"], True)
                    WG_MENU_LIST[gid]["menu"].Enable(WG_MENU_LIST[gid]["add"], False)
                else:
                    WG_MENU_LIST[gid]["menu"].Enable(WG_MENU_LIST[gid]["remove"], False)
                    WG_MENU_LIST[gid]["menu"].Enable(WG_MENU_LIST[gid]["add"], True)
                if len(WG_LIST[gid]) == 0:
                    WG_MENU_LIST[gid]["menu"].Enable(WG_MENU_LIST[gid]["whisper"], False)
                    WG_MENU_LIST[gid]["menu"].Enable(WG_MENU_LIST[gid]["clear"], False)
                else:
                    WG_MENU_LIST[gid]["menu"].Enable(WG_MENU_LIST[gid]["whisper"], True)
                    WG_MENU_LIST[gid]["menu"].Enable(WG_MENU_LIST[gid]["clear"], True)

                #Event Stuff
                self.Bind(wx.EVT_MENU, self.on_menu_whispergroup, id=WG_MENU_LIST[gid]["whisper"] )
                self.Bind(wx.EVT_MENU, self.on_menu_whispergroup, id=WG_MENU_LIST[gid]["add"] )
                self.Bind(wx.EVT_MENU, self.on_menu_whispergroup, id=WG_MENU_LIST[gid]["remove"] )
                self.Bind(wx.EVT_MENU, self.on_menu_whispergroup, id=WG_MENU_LIST[gid]["clear"] )
#---------------------------------------------------------
# [END] Digitalxero Multi Whisper Group 1/1/05
#---------------------------------------------------------
            self.PopupMenu(self.menu,pos)

    def add_player(self,player):
        i = self.InsertImageStringItem(0,player[2],0)
        self.SetStringItem(i,1,self.strip_html(player))
        self.SetItemData(i,int(player[2]))
        self.SetStringItem(i, 2,player[3])
        self.colorize_player_list()
        self.Refresh()
        # play sound
        setobj = open_rpg.get_component('settings')
        sound_file = setobj.get_setting("AddSound")
        if sound_file != '':
            sound_player = open_rpg.get_component('sound')
            sound_player.play(sound_file)
        self.AutoAdjust()

    def del_player(self,player):
        i = self.FindItemData(-1,int(player[2]))
        self.DeleteItem(i)

#---------------------------------------------------------
# [START] Digitalxero Multi Whisper Group 1/1/05
#---------------------------------------------------------
        for gid in WG_LIST:
            if WG_LIST[gid].has_key(int(player[2])): del WG_LIST[gid][int(player[2])]
#---------------------------------------------------------
# [END] Digitalxero Multi Whisper Group 1/1/05
#---------------------------------------------------------

        # play sound
        setobj = open_rpg.get_component('settings')
        sound_file = setobj.get_setting("DelSound")
        if sound_file != '':
            sound_player = open_rpg.get_component('sound')
            sound_player.play(sound_file)
        ic = self.GetItemCount()
        self.whisperCount = 0
        index = 0
        while index < ic:
            item = self.GetItem( index )
            if item.GetImage(): self.whisperCount += 1
            index += 1
        self.colorize_player_list()
        self.Refresh()

    #  This method updates the player info
    #
    #  self:  reference to this PlayerList
    #  player:  reference to a player structure(list)
    #
    #  Returns:  None
    #
    def update_player(self,player):
        i = self.FindItemData(-1,int(player[2]))  #  finds the right list box index
        self.SetStringItem(i,1,self.strip_html(player))
        self.SetStringItem(i,2,player[3])
        item = self.GetItem(i)
        self.colorize_player_list()
        self.AutoAdjust()

    def colorize_player_list(self):
        session = open_rpg.get_component("session")
        settings = open_rpg.get_component('settings')
        mode = settings.get_setting("ColorizeRoles")
        if mode.lower() == "0": return
        players = session.players
        for m in players.keys():
            item_list_location = self.FindItemData(-1,int(m))
            if item_list_location == -1: continue
            player_info = session.get_player_by_player_id(m)
            item = self.GetItem(item_list_location)
            role = player_info[7]
            color = wx.GREEN
            if self.session.group_id != "0": item.SetTextColour(settings.get_setting(role + "RoleColor"))
            self.SetItem(item)

    def reset(self):
        self.whisperCount = 0
#---------------------------------------------------------
# [START] Digitalxero Multi Whisper Group 1/1/05
#---------------------------------------------------------
        WG_LIST.clear()
#---------------------------------------------------------
# [END] Digitalxero Multi Whisper Group 1/1/05
#---------------------------------------------------------
        self.DeleteAllItems()

    def strip_html(self,player):
        ret_string = ""; x = 0; in_tag = 0
        for x in range(len(player[0])) :
            if player[0][x] == "<" or player[0][x] == ">" or in_tag == 1 :
                if player[0][x] == "<": in_tag = 1
                elif player[0][x] == ">": in_tag = 0
                else: pass
            else: ret_string = ret_string + player[0][x]
        return ret_string

    def size_cols(self):
        ##moved skip here to see if it breaks
        ## w,h = self.GetClientSizeTuple()
        ## w /= 8
        ## self.SetColumnWidth( 0, w*2 )
        ## self.SetColumnWidth( 1, w*2 )
        ## self.SetColumnWidth( 2, w*3 )
        pass
