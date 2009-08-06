#!/usr/bin/env python
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
# File: main.py
# Author: Chris Davis
# Maintainer:
# Version:
#   $Id: main.py,v 1.153 2008/01/24 03:52:03 digitalxero Exp $
#
# Description: This is the main entry point of the oprg application
#

__version__ = "$Id: main.py,v 1.154 2009/07/19 03:52:03 madmathlabs Exp $"

from orpg.orpg_wx import *
from orpg.orpgCore import *
from orpg_version import *
from orpg.orpg_windows import *
import orpg.dirpath
import orpg.orpg_xml
import orpg.player_list
import orpg.tools.pluginui as pluginUI
import orpg.tools.orpg_settings
import orpg.tools.orpg_log
import orpg.tools.aliaslib
from orpg.tools.metamenus import MenuBarEx
import orpg.tools.toolBars
import orpg.tools.passtool
import orpg.tools.orpg_sound
import orpg.tools.validate
import orpg.tools.rgbhex
import orpg.gametree.gametree
import orpg.chat.chatwnd
import orpg.dieroller.utils
import orpg.networking.mplay_client
import orpg.networking.gsclient
import orpg.mapper.map
import orpg.mapper.images
import upmana.updatemana
import upmana.manifest as manifest
import wx.py

####################################
## Main Frame
####################################


class orpgFrame(wx.Frame):
    def __init__(self, parent, id, title):
        wx.Frame.__init__(self, parent, id, title, wx.Point(100, 100), wx.Size(600,420), style=wx.DEFAULT_FRAME_STYLE)
        self.log = open_rpg.get_component("log")
        self.xml = open_rpg.get_component("xml")
        self.dir_struct = open_rpg.get_component("dir_struct")
        self.validate = open_rpg.get_component("validate")
        self.settings = open_rpg.get_component("settings")
        self.log.log("Enter orpgFrame", ORPG_DEBUG)
        self.rgbcovert = orpg.tools.rgbhex.RGBHex()
        self._mgr = AUI.AuiManager(self)

        # Determine which icon format to use
        icon = None
        if wx.Platform == '__WXMSW__': icon = wx.Icon(orpg.dirpath.dir_struct["icon"]+'d20.ico', wx.BITMAP_TYPE_ICO)
        else: icon = wx.Icon(orpg.dirpath.dir_struct["icon"]+"d20.xpm", wx.BITMAP_TYPE_XPM)
        #if icon != None: self.SetIcon( icon ) worth 'less' now since it sets the icon either or.
        self.SetIcon( icon )

        # create session
        call_backs = {"on_receive":self.on_receive,
                "on_mplay_event":self.on_mplay_event,
                "on_group_event":self.on_group_event,
                "on_player_event":self.on_player_event,
                "on_status_event":self.on_status_event,
                "on_password_signal":self.on_password_signal,
                "orpgFrame":self}
        self.session = orpg.networking.mplay_client.mplay_client(self.settings.get_setting("player"), call_backs)
        self.poll_timer = wx.Timer(self, wx.NewId())
        self.Bind(wx.EVT_TIMER, self.session.poll, self.poll_timer)
        self.poll_timer.Start(100)
        self.ping_timer = wx.Timer(self, wx.NewId())
        self.Bind(wx.EVT_TIMER, self.session.update, self.ping_timer)

        # create roller manager
        self.DiceManager = orpg.dieroller.utils.roller_manager(self.settings.get_setting("dieroller"))

        #create password manager --SD 8/03
        self.password_manager = orpg.tools.passtool.PassTool()
        open_rpg.add_component("session", self.session)
        open_rpg.add_component('frame', self)
        open_rpg.add_component('DiceManager', self.DiceManager)
        open_rpg.add_component('password_manager', self.password_manager)

        # build frame windows
        self.build_menu()
        self.build_gui()
        self.build_hotkeys()
        self.log.log("GUI Built", ORPG_DEBUG)
        open_rpg.add_component("chat",self.chat)
        open_rpg.add_component("map",self.map)
        open_rpg.add_component("alias", self.aliaslib)
        self.log.log("openrpg components all added", ORPG_DEBUG)
        self.tree.load_tree(self.settings.get_setting("gametree"))
        self.log.log("Tree Loaded", ORPG_DEBUG)
        self.players.size_cols()
        self.log.log("player window cols sized", ORPG_DEBUG)

        #Load the Plugins This has to be after the chat component has been added
        open_rpg.add_component('pluginmenu', self.pluginMenu)
        self.pluginsFrame.Start()
        self.log.log("plugins reloaded and startup plugins launched", ORPG_DEBUG)
        self.Bind(wx.EVT_CLOSE, self.OnCloseWindow)
        self.log.log("Exit orpgFrame", ORPG_DEBUG)

        #Load Update Manager
        open_rpg.add_component('updatemana', self.updateMana)
        self.log.log("update manager reloaded", ORPG_DEBUG)
        self.Bind(wx.EVT_CLOSE, self.OnCloseWindow)
        self.log.log("Exit orpgFrame", ORPG_DEBUG)

    def post_show_init(self):
        """Some Actions need to be done after the main fram is drawn"""
        self.log.log("Enter orpgFrame->post_show_init(self)", ORPG_DEBUG)
        self.players.size_cols()
        self.log.log("Exit orpgFrame->post_show_init(self)", ORPG_DEBUG)

    def get_activeplugins(self):
        self.log.log("Enter orpgFrame->get_activeplugins(self)", ORPG_DEBUG)
        try: tmp = self.pluginsFrame.get_activeplugins()
        except: tmp = {}
        self.log.log("Exit orpgFrame->get_activeplugins(self)", ORPG_DEBUG)
        return tmp

    def get_startplugins(self):
        self.log.log("Enter orpgFrame->get_startplugins(self)", ORPG_DEBUG)
        try: tmp = self.pluginsFrame.get_startplugins()
        except: tmp = {}
        self.log.log("Exit orpgFrame->get_startplugins(self)", ORPG_DEBUG)
        return tmp

    def on_password_signal(self,signal,type,id,data):
        self.log.log("Enter orpgFrame->on_password_signal(self,signal,type,id,data)", ORPG_DEBUG)
        try:
            self.log.log("DEBUG: password response= "+str(signal)+" (T:"+str(type)+"  #"+str(id)+")", ORPG_DEBUG)
            id = int(id)
            type = str(type)
            data = str(data)
            signal = str(signal)
            if signal == "fail":
                if type == "server": self.password_manager.ClearPassword("server", 0)
                elif type == "admin": self.password_manager.ClearPassword("admin", int(id))
                elif type == "room": self.password_manager.ClearPassword("room", int(id))
                else: pass
        except: traceback.print_exc()
        self.log.log("Exit orpgFrame->on_password_signal(self,signal,type,id,data)", ORPG_DEBUG)

    def build_menu(self):
        self.log.log("Enter orpgFrame->build_menu()", ORPG_DEBUG)
        menu = \
                [[
                    ['&OpenRPG'],
                    ['  &Settings\tCtrl-S'],
                    ['  -'],
                    ['  Tab Styles'],
                    ['    Slanted'],
                    ['      Colorful', "check"],
                    ['      Black and White', "check"],
                    ['      Aqua', "check"],
                    ['      Custom', "check"],
                    ['    Flat'],
                    ['      Black and White', "check"],
                    ['      Aqua', "check"],
                    ['      Custom', "check"],
                    ['  NewMap'],
                    ['  -'],
                    ['  &Exit']
                ],
                [
                    ['&Game Server'],
                    ['  &Browse Servers\tCtrl-B'],
                    ['  -'],
                    ['  Server Heartbeat', "check"],
                    ['  -'],
                    ['  &Start Server']
                ],
                [
                    ['&Tools'],
                    ['  Logging Level'],
                    ['    Debug', "check"],
                    ['    Note', "check"],
                    ['    Info', "check"],
                    ['    General', "check"],
                    ['  -'],
                    ['  Password Manager', "check"],
                    ['  -'],
                    ['  Sound Toolbar', "check"],
                    ['  Dice Bar\tCtrl-D', "check"],
                    ['  Map Bar', "check"],
                    ['  Status Bar\tCtrl-T', "check"],
                ],
                [
                    ['&Help'],
                    ['  &About'],
                    ['  Online User Guide'],
                    ['  Change Log'],
                    ['  Report a Bug']
                ]]

        self.mainmenu = MenuBarEx(self, menu)
        if self.settings.get_setting('Heartbeat') == '1':
            self.mainmenu.SetMenuState("GameServerServerHeartbeat", True)

        tabtheme = self.settings.get_setting('TabTheme')  #This change is stable. TaS.
        self.mainmenu.SetMenuState("OpenRPGTabStylesSlantedColorful", tabtheme == 'slanted&colorful')
        self.mainmenu.SetMenuState("OpenRPGTabStylesSlantedBlackandWhite", tabtheme == 'slanted&bw')
        self.mainmenu.SetMenuState("OpenRPGTabStylesSlantedAqua", tabtheme == 'slanted&aqua')
        self.mainmenu.SetMenuState("OpenRPGTabStylesFlatBlackandWhite", tabtheme == 'flat&bw')
        self.mainmenu.SetMenuState("OpenRPGTabStylesFlatAqua", tabtheme == 'flat&aqua')
        self.mainmenu.SetMenuState("OpenRPGTabStylesSlantedCustom", tabtheme == 'customslant')
        self.mainmenu.SetMenuState("OpenRPGTabStylesFlatCustom", tabtheme == 'customflat')

        lvl = int(self.settings.get_setting('LoggingLevel'))
        if lvl & ORPG_DEBUG: self.mainmenu.SetMenuState("ToolsLoggingLevelDebug", True)
        if lvl & ORPG_DEBUG: self.mainmenu.SetMenuState("ToolsLoggingLevelNote", True)
        if lvl & ORPG_INFO: self.mainmenu.SetMenuState("ToolsLoggingLevelInfo", True)
        if lvl & ORPG_GENERAL: self.mainmenu.SetMenuState("ToolsLoggingLevelGeneral", True)

        self.pluginMenu = wx.Menu()
        item = wx.MenuItem(self.pluginMenu, wx.ID_ANY, "Control Panel", "Control Panel")
        self.Bind(wx.EVT_MENU, self.OnMB_PluginControlPanel, item)

        self.pluginMenu.AppendItem(item)
        self.pluginMenu.AppendSeparator()
        self.mainmenu.Insert(2, self.pluginMenu, "&Plugins")
        self.log.log("Exit orpgFrame->build_menu()", ORPG_DEBUG)

        self.updateMana = wx.Menu()
        mana = wx.MenuItem(self.updateMana, wx.ID_ANY, "Update Manager", "Update Manager")
        self.Bind(wx.EVT_MENU, self.OnMB_UpdateManagerPanel, mana)

        self.updateMana.AppendItem(mana)
        self.mainmenu.Insert(5, self.updateMana, "&Update Manager")
        self.log.log("Exit orpgFrame->build_menu()", ORPG_DEBUG)
       

    #################################
    ## All Menu Events
    #################################
    #Tab Styles Menus
    def SetTabStyles(self, *args, **kwargs):
        self.log.log("Enter orpgFrame->SetTabStyles(self, *args, **kwargs)", ORPG_DEBUG)

        tabtheme = self.settings.get_setting('TabTheme')  #This change is stable. TaS.
        self.mainmenu.SetMenuState("OpenRPGTabStylesSlantedColorful", tabtheme == 'slanted&colorful')
        self.mainmenu.SetMenuState("OpenRPGTabStylesSlantedBlackandWhite", tabtheme == 'slanted&bw')
        self.mainmenu.SetMenuState("OpenRPGTabStylesSlantedAqua", tabtheme == 'slanted&aqua')
        self.mainmenu.SetMenuState("OpenRPGTabStylesFlatBlackandWhite", tabtheme == 'flat&bw')
        self.mainmenu.SetMenuState("OpenRPGTabStylesFlatAqua", tabtheme == 'flat&aqua')
        self.mainmenu.SetMenuState("OpenRPGTabStylesSlantedCustom", tabtheme == 'customslant')
        self.mainmenu.SetMenuState("OpenRPGTabStylesFlatCustom", tabtheme == 'customflat')

        if kwargs.has_key('style'): newstyle = kwargs['style']
        else:
            try: newstyle = args[1]
            except: self.log.log('Invalid Syntax for orpgFrame->SetTabStyles(self, *args, **kwargs)', ORPG_GENERAL); return
        if kwargs.has_key('menu'): menu = kwargs['menu']
        else:
            try: menu = args[0]
            except: self.log.log('Invalid Syntax for orpgFrame->SetTabStyles(self, *args, **kwargs)', ORPG_GENERAL); return

        if kwargs.has_key('graidentTo'): graidentTo = kwargs['graidentTo']
        else: graidentTo = None
        if kwargs.has_key('graidentFrom'): graidentFrom = kwargs['graidentFrom']
        else: graidentFrom = None
        if kwargs.has_key('textColor'): textColor = kwargs['textColor']
        else: textColor = None

        #Run though the current tabbed window list and remove those that have been closed
        tabbedwindows = open_rpg.get_component("tabbedWindows")
        rgbc = orpg.tools.rgbhex.RGBHex()
        new = []
        for wnd in tabbedwindows:
            try: style = wnd.GetWindowStyleFlag(); new.append(wnd)
            except:  pass
        tabbedwindows = new
        open_rpg.add_component("tabbedWindows", tabbedwindows)

        #Run though the new list and set the proper styles
        tabbg = self.settings.get_setting('TabBackgroundGradient')
        rgbc = orpg.tools.rgbhex.RGBHex()
        (red, green, blue) = rgbc.rgb_tuple(tabbg)

        for wnd in tabbedwindows:
            style = wnd.GetWindowStyleFlag()
            # remove old tabs style
            mirror = ~(FNB.FNB_VC71 | FNB.FNB_VC8 | FNB.FNB_FANCY_TABS | FNB.FNB_COLORFUL_TABS)
            style &= mirror
            style |= newstyle
            wnd.SetWindowStyleFlag(style)
            wnd.SetTabAreaColour(wx.Color(red, green, blue))
            if graidentTo != None: wnd.SetGradientColourTo(graidentTo)
            if graidentFrom != None: wnd.SetGradientColourFrom(graidentFrom)
            if textColor != None: wnd.SetNonActiveTabTextColour(textColor)
            wnd.Refresh()

    def OnMB_OpenRPGNewMap(self):
        self.log.log("Enter orpgFrame->OnMB_OpenRPGNewMap(self)", ORPG_DEBUG)
        self.log.log("Exit orpgFrame->OnMB_OpenRPGNewMap(self)", ORPG_DEBUG)

    def OnMB_OpenRPGTabStylesSlantedColorful(self):
        self.log.log("Enter orpgFrame->OnMB_OpenRPGTabStylesSlantedColorful(self)", ORPG_DEBUG)
        if self.mainmenu.GetMenuState("OpenRPGTabStylesSlantedColorful"):
            self.settings.set_setting('TabTheme', 'slanted&colorful')
            self.SetTabStyles("OpenRPGTabStylesSlantedColorful", FNB.FNB_VC8|FNB.FNB_COLORFUL_TABS)
        else: self.mainmenu.SetMenuState("OpenRPGTabStylesSlantedColorful", True)
        self.log.log("Exit orpgFrame->OnMB_OpenRPGTabStylesSlantedColorful(self)", ORPG_DEBUG)

    def OnMB_OpenRPGTabStylesSlantedBlackandWhite(self):
        self.log.log("Enter orpgFrame->OnMB_OpenRPGTabStylesSlantedBlackandWhite(self)", ORPG_DEBUG)
        if self.mainmenu.GetMenuState("OpenRPGTabStylesSlantedBlackandWhite"):
            self.settings.set_setting('TabTheme', 'slanted&bw')
            self.SetTabStyles("OpenRPGTabStylesSlantedBlackandWhite", FNB.FNB_VC8, graidentTo=wx.WHITE, graidentFrom=wx.WHITE, textColor=wx.BLACK)
        else: self.mainmenu.SetMenuState("OpenRPGTabStylesSlantedBlackandWhite", True)
        self.log.log("Exit orpgFrame->OnMB_OpenRPGTabStylesSlantedBlackandWhite(self)", ORPG_DEBUG)

    def OnMB_OpenRPGTabStylesSlantedAqua(self):
        self.log.log("Enter orpgFrame->OnMB_OpenRPGTabStylesSlantedAqua(self)", ORPG_DEBUG)
        if self.mainmenu.GetMenuState("OpenRPGTabStylesSlantedAqua"):
            self.settings.set_setting('TabTheme', 'slanted&aqua')
            self.SetTabStyles("OpenRPGTabStylesSlantedAqua", FNB.FNB_VC8, graidentTo=wx.Color(0, 128, 255), graidentFrom=wx.WHITE, textColor=wx.BLACK)
        else: self.mainmenu.SetMenuState("OpenRPGTabStylesSlantedAqua", True)
        self.log.log("Exit orpgFrame->OnMB_OpenRPGTabStylesSlantedBlackandWhite(self)", ORPG_DEBUG)

    def OnMB_OpenRPGTabStylesSlantedCustom(self):
        self.log.log("Enter orpgFrame->OnMB_OpenRPGTabStylesSlantedCustom(self)", ORPG_DEBUG)
        if self.mainmenu.GetMenuState("OpenRPGTabStylesSlantedCustom"):
            self.settings.set_setting('TabTheme', 'customslant')
            rgbc = orpg.tools.rgbhex.RGBHex()
            gfrom = self.settings.get_setting('TabGradientFrom')
            (fred, fgreen, fblue) = rgbc.rgb_tuple(gfrom)
            gto = self.settings.get_setting('TabGradientTo')
            (tored, togreen, toblue) = rgbc.rgb_tuple(gto)
            tabtext = self.settings.get_setting('TabTextColor')
            (tred, tgreen, tblue) = rgbc.rgb_tuple(tabtext)
            tabbg = self.settings.get_setting('TabBackgroundGradient')
            (red, green, blue) = rgbc.rgb_tuple(tabbg)
            self.SetTabStyles("OpenRPGTabStylesSlantedCustom", FNB.FNB_VC8, 
                graidentTo=wx.Color(tored, togreen, toblue), graidentFrom=wx.Color(fred, fgreen, fblue), 
                textColor=wx.Color(tred, tgreen, tblue))
        else: self.mainmenu.SetMenuState("OpenRPGTabStylesSlantedCustom", True)
        self.log.log("Exit orpgFrame->OnMB_OpenRPGTabStylesSlantedCustom(self)", ORPG_DEBUG)

    def OnMB_OpenRPGTabStylesFlatBlackandWhite(self):
        self.log.log("Enter orpgFrame->OnMB_OpenRPGTabStylesFlatBlackandWhite(self)", ORPG_DEBUG)
        if self.mainmenu.GetMenuState("OpenRPGTabStylesFlatBlackandWhite"):
            self.settings.set_setting('TabTheme', 'flat&bw')
            self.SetTabStyles("OpenRPGTabStylesFlatBlackandWhite", FNB.FNB_FANCY_TABS, 
                graidentTo=wx.WHITE, graidentFrom=wx.WHITE, textColor=wx.BLACK)
        else: self.mainmenu.SetMenuState("OpenRPGTabStylesFlatBlackandWhite", True)
        self.log.log("Exit orpgFrame->OnMB_OpenRPGTabStylesFlatBlackandWhite(self)", ORPG_DEBUG)

    def OnMB_OpenRPGTabStylesFlatAqua(self):
        self.log.log("Enter orpgFrame->OnMB_OpenRPGTabStylesFlatAqua(self)", ORPG_DEBUG)
        if self.mainmenu.GetMenuState("OpenRPGTabStylesFlatAqua"):
            self.settings.set_setting('TabTheme', 'flat&aqua')
            self.SetTabStyles("OpenRPGTabStylesFlatAqua", FNB.FNB_FANCY_TABS, 
                graidentTo=wx.Color(0, 128, 255), graidentFrom=wx.WHITE, textColor=wx.BLACK)
        else: self.mainmenu.SetMenuState("OpenRPGTabStylesFlatAqua", True)
        self.log.log("Exit orpgFrame->OnMB_OpenRPGTabStylesFlatAqua(self)", ORPG_DEBUG)

    def OnMB_OpenRPGTabStylesFlatCustom(self):
        self.log.log("Enter orpgFrame->OnMB_OpenRPGTabStylesFlatCustom(self)", ORPG_DEBUG)
        if self.mainmenu.GetMenuState("OpenRPGTabStylesFlatCustom"):
            self.settings.set_setting('TabTheme', 'customflat')
            rgbc = orpg.tools.rgbhex.RGBHex()
            gfrom = self.settings.get_setting('TabGradientFrom')
            (fred, fgreen, fblue) = rgbc.rgb_tuple(gfrom)
            gto = self.settings.get_setting('TabGradientTo')
            (tored, togreen, toblue) = rgbc.rgb_tuple(gto)
            tabtext = self.settings.get_setting('TabTextColor')
            (tred, tgreen, tblue) = rgbc.rgb_tuple(tabtext)
            tabbg = self.settings.get_setting('TabBackgroundGradient')
            (red, green, blue) = rgbc.rgb_tuple(tabbg)
            self.SetTabStyles("OpenRPGTabStylesFlatCustom", FNB.FNB_FANCY_TABS, 
                graidentTo=wx.Color(tored, togreen, toblue), graidentFrom=wx.Color(fred, fgreen, fblue), 
                textColor=wx.Color(tred, tgreen, tblue))
        else: self.mainmenu.SetMenuState("OpenRPGTabStylesFlatCustom", True)
        self.log.log("Exit orpgFrame->OnMB_OpenRPGTabStylesFlatCustom(self)", ORPG_DEBUG)

    #Window Menu
    def OnMB_WindowsMenu(self, event):
        self.log.log("Enter orpgFrame->OnMB_WindowsMenu(self, event)", ORPG_DEBUG)
        menuid = event.GetId()
        name = self.mainwindows[menuid]
        if name == 'Alias Lib':
            if self.aliaslib.IsShown() == True: self.aliaslib.Hide()
            else: self.aliaslib.Show()
        else:
            if self._mgr.GetPane(name).IsShown() == True: self._mgr.GetPane(name).Hide()
            else: self._mgr.GetPane(name).Show()
            self._mgr.Update()
        self.log.log("Exit orpgFrame->OnMB_WindowsMenu(self, event)", ORPG_DEBUG)

    #OpenRPG Menu
    def OnMB_OpenRPGSettings(self):
        self.log.log("Enter orpgFrame->OnMB_OpenRPGSettings()", ORPG_DEBUG)
        dlg = orpg.tools.orpg_settings.orpgSettingsWnd(self)
        dlg.Centre()
        dlg.ShowModal()
        self.log.log("Exit orpgFrame->OnMB_OpenRPGSettings()", ORPG_DEBUG)

    def OnMB_OpenRPGExit(self):
        self.OnCloseWindow(0)

    #Game Server Menu
    def OnMB_GameServerBrowseServers(self):
        self.log.log("Enter orpgFrame->OnMB_GameServerBrowseServers(self)", ORPG_DEBUG)
        if self._mgr.GetPane("Browse Server Window").IsShown() == True: self._mgr.GetPane("Browse Server Window").Hide()
        else: self._mgr.GetPane("Browse Server Window").Show()
        self._mgr.Update()
        self.log.log("Exit orpgFrame->OnMB_GameServerBrowseServers(self)", ORPG_DEBUG)

    def OnMB_GameServerServerHeartbeat(self):
        self.log.log("Enter orpgFrame->OnMB_GameServerServerHeartbeat(self)", ORPG_DEBUG)
        if self.mainmenu.GetMenuState("GameServerServerHeartbeat"): self.settings.set_setting('Heartbeat', '1')
        else: self.settings.set_setting('Heartbeat', '0')
        self.log.log("Exit orpgFrame->OnMB_GameServerServerHeartbeat(self)", ORPG_DEBUG)

    def OnMB_GameServerStartServer(self):
        self.log.log("Enter orpgFrame->OnMB_GameServerStartServer(self)", ORPG_DEBUG)
        start_dialog = wx.ProgressDialog( "Server Loading", "Server Loading, Please Wait...", 1, self )
        # Spawn the new process and close the stdout handle from it
        start_dialog.Update( 0 )
        # Adjusted following code to work with win32, can't test for Unix
        # as per reported bug 586227
        if wx.Platform == "__WXMSW__":
            arg = '\"' + os.path.normpath(orpg.dirpath.dir_struct["home"] + 'start_server_gui.py') + '\"'
            args = ( sys.executable, arg )
        else:
            arg = orpg.dirpath.dir_struct["home"] + 'start_server_gui.py'
            args = (arg,arg)
        os.spawnv( os.P_NOWAIT, sys.executable, args )
        start_dialog.Update( 1 )
        start_dialog.Show(False)
        start_dialog.Destroy()
        self.log.log("Exit orpgFrame->OnMB_GameServerStartServer(self)", ORPG_DEBUG)

    # Tools Menu
    def OnMB_PluginControlPanel(self, evt):
        self.log.log("Enter orpgFrame->OnMB_ToolsPlugins(self)", ORPG_DEBUG)
        if self.pluginsFrame.IsShown() == True: self.pluginsFrame.Hide()
        else: self.pluginsFrame.Show()
        self.log.log("Exit orpgFrame->OnMB_ToolsPlugins(self)", ORPG_DEBUG)

    def OnMB_UpdateManagerPanel(self, evt):
        self.log.log("Enter orpgFrame->OnMB_ToolsPlugins(self)", ORPG_DEBUG)
        if self.updateMana.IsShown() == True: self.updateMana.Hide()
        else: self.updateMana.Show()
        self.log.log("Exit orpgFrame->OnMB_ToolsPlugins(self)", ORPG_DEBUG)

    def OnMB_ToolsLoggingLevelDebug(self):
        self.log.log("Enter orpgFrame->OnMB_ToolsLoggingLevelDebug(self)", ORPG_DEBUG)
        lvl = self.log.getLogLevel()
        if self.mainmenu.GetMenuState("ToolsLoggingLevelDebug"): lvl |= ORPG_DEBUG
        else: lvl &= ~ORPG_DEBUG
        self.log.setLogLevel(lvl)
        self.settings.set_setting('LoggingLevel', lvl)
        self.log.log("Exit orpgFrame->OnMB_ToolsLoggingLevelDebug(self)", ORPG_DEBUG)

    def OnMB_ToolsLoggingLevelNote(self):
        self.log.log("Enter orpgFrame->OnMB_ToolsLoggingLevelNote(self)", ORPG_DEBUG)
        lvl = self.log.getLogLevel()
        if self.mainmenu.GetMenuState("ToolsLoggingLevelNote"): lvl |= ORPG_DEBUG
        else: lvl &= ~ORPG_DEBUG
        self.log.setLogLevel(lvl)
        self.settings.set_setting('LoggingLevel', lvl)
        self.log.log("Exit orpgFrame->OnMB_ToolsLoggingLevelNote(self)", ORPG_DEBUG)

    def OnMB_ToolsLoggingLevelInfo(self):
        self.log.log("Enter orpgFrame->OnMB_ToolsLoggingLevelInfo(self)", ORPG_DEBUG)
        lvl = self.log.getLogLevel()
        if self.mainmenu.GetMenuState("ToolsLoggingLevelInfo"): lvl |= ORPG_INFO
        else: lvl &= ~ORPG_INFO
        self.log.setLogLevel(lvl)
        self.settings.set_setting('LoggingLevel', lvl)
        self.log.log("Exit orpgFrame->OnMB_ToolsLoggingLevelInfo(self)", ORPG_DEBUG)

    def OnMB_ToolsLoggingLevelGeneral(self):
        self.log.log("Enter orpgFrame->OnMB_ToolsLoggingLevelGeneral(self)", ORPG_DEBUG)
        lvl = self.log.getLogLevel()
        if self.mainmenu.GetMenuState("ToolsLoggingLevelGeneral"): lvl |= ORPG_GENERAL
        else: lvl &= ~ORPG_GENERAL
        self.log.setLogLevel(lvl)
        self.settings.set_setting('LoggingLevel', lvl)
        self.log.log("Exit orpgFrame->OnMB_ToolsLoggingLevelGeneral(self)", ORPG_DEBUG)

    def OnMB_ToolsPasswordManager(self):
        self.log.log("Enter orpgFrame->OnMB_ToolsPasswordManager(self)", ORPG_DEBUG)
        if self.mainmenu.GetMenuState("ToolsPasswordManager"): self.password_manager.Enable()
        else: self.password_manager.Disable()
        self.log.log("Exit orpgFrame->OnMB_ToolsPasswordManager(self)", ORPG_DEBUG)

    def OnMB_ToolsStatusBar(self):
        self.log.log("Enter orpgFrame->OnMB_ToolsStatusBar(self)", ORPG_DEBUG)
        if self._mgr.GetPane("Status Window").IsShown() == True:
            self.mainmenu.SetMenuState("ToolsStatusBar", False)
            self._mgr.GetPane("Status Window").Hide()
        else:
            self.mainmenu.SetMenuState("ToolsStatusBar", True)
            self._mgr.GetPane("Status Window").Show()
        self._mgr.Update()
        self.log.log("Exit orpgFrame->OnMB_ToolsStatusBar(self)", ORPG_DEBUG)

    def OnMB_ToolsSoundToolbar(self):
        self.log.log("Enter orpgFrame->OnMB_ToolsSoundToolbar(self)", ORPG_DEBUG)
        if self._mgr.GetPane("Sound Control Toolbar").IsShown() == True:
            self.mainmenu.SetMenuState("ToolsSoundToolbar", False)
            self._mgr.GetPane("Sound Control Toolbar").Hide()
        else:
            self.mainmenu.SetMenuState("ToolsSoundToolbar", True)
            self._mgr.GetPane("Sound Control Toolbar").Show()
        self._mgr.Update()
        self.log.log("Exit orpgFrame->OnMB_ToolsSoundToolbar(self)", ORPG_DEBUG)

    def OnMB_ToolsDiceBar(self):
        self.log.log("Enter orpgFrame->OnMB_ToolsDiceBar(self)", ORPG_DEBUG)
        if self._mgr.GetPane("Dice Tool Bar").IsShown() == True:
            self.mainmenu.SetMenuState("ToolsDiceBar", False)
            self._mgr.GetPane("Dice Tool Bar").Hide()
        else:
            self.mainmenu.SetMenuState("ToolsDiceBar", True)
            self._mgr.GetPane("Dice Tool Bar").Show()
        self._mgr.Update()
        self.log.log("Exit orpgFrame->OnMB_ToolsDiceBar(self)", ORPG_DEBUG)

    def OnMB_ToolsMapBar(self):
        self.log.log("Enter orpgFrame->OnMB_ToolsMapBar(self)", ORPG_DEBUG)
        if self._mgr.GetPane("Map Tool Bar").IsShown() == True:
            self.mainmenu.SetMenuState("ToolsMapBar", False)
            self._mgr.GetPane("Map Tool Bar").Hide()
        else:
            self.mainmenu.SetMenuState("ToolsMapBar", True)
            self._mgr.GetPane("Map Tool Bar").Show()
        self._mgr.Update()
        self.log.log("Exit orpgFrame->OnMB_ToolsMapBar(self)", ORPG_DEBUG)

    #Help Menu #Needs a custom Dialog because it is ugly on Windows
    def OnMB_HelpAbout(self):

        description = """OpenRPG is a Virtual Game Table that allows users to connect via a network and play table
top games with friends.  'Traipse' is an OpenRPG distro that is easy to setup and provides superb 
functionality.  OpenRPG is originally designed by Chris Davis."""

        license = """OpenRPG is free software; you can redistribute it and/or modify it 
under the terms of the GNU General Public License as published by the Free Software Foundation; 
either version 2 of the License, or (at your option) any later version.

OpenRPG and Traipse 'OpenRPG' is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; 
without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  
See the GNU General Public License for more details. You should have received a copy of 
the GNU General Public License along with Traipse 'OpenRPG'; if not, write to 
the Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

'Traipse' and the 'Traipse' Logo are trademarks of Mad Mathematics Laboratories."""

        info = wx.AboutDialogInfo()
        info.SetIcon(wx.Icon(orpg.dirpath.dir_struct["icon"]+'splash.gif', wx.BITMAP_TYPE_GIF))
        info.SetName('Traipse')
        info.SetVersion('OpenRPG ' + VERSION)
        info.SetDescription(description)
        info.SetCopyright('(C) Copyright 2009 Mad Math Labs')
        info.SetWebSite('http://www.openrpg.com')
        info.SetLicence(license)
        orpg_devs = ['Thomas Baleno', 'Andrew Bennett', 'Lex Berezhny', 'Ted Berg',
		'Bernhard Bergbauer', 'Chris Blocher', 'David Byron', 'Ben Collins-Sussman', 'Robin Cook', 'Greg Copeland',
		'Chris Davis', 'Michael Edwards', 'Andrew Ettinger', 'Todd Faris', 'Dj Gilcrease',
        'Christopher Hickman', 'Paul Hosking', 'Brian Manning', 'Scott Mackay', 'Jesse McConnell', 
		'Brian Osman', 'Rome Reginelli', 'Christopher Rouse', 'Dave Sanders', 'Tyler Starke', 'Mark Tarrabain']
        for dev in orpg_devs:
            info.AddDeveloper(dev)
        wx.AboutBox(info)

    def OnMB_HelpOnlineUserGuide(self):
        wb = webbrowser.get()
        wb.open("https://www.assembla.com/wiki/show/traipse/User_Manual")

    def OnMB_HelpChangeLog(self):
        wb = webbrowser.get()
        wb.open("http://www.assembla.com/spaces/milestones/index/traipse_dev?spaces_tool_id=Milestones")

    def OnMB_HelpReportaBug(self):
        wb = webbrowser.get()
        wb.open("http://www.assembla.com/spaces/tickets/index/traipse_dev?spaces_tool_id=Tickets")


    #################################
    ##    Build the GUI
    #################################
    def build_gui(self):
        self.log.log("Enter orpgFrame->build_gui()", ORPG_DEBUG)
        self.Freeze()
        self.validate.config_file("layout.xml","default_layout.xml")
        filename = orpg.dirpath.dir_struct["user"] + "layout.xml"
        temp_file = open(filename)
        txt = temp_file.read()
        xml_dom = self.xml.parseXml(txt)._get_documentElement()
        temp_file.close()

        #Plugins Window
        self.pluginsFrame = pluginUI.PluginFrame(self)
        open_rpg.add_component("plugins", self.get_activeplugins())
        open_rpg.add_component("startplugs", self.get_startplugins())
        self.windowsmenu = wx.Menu()
        self.mainwindows = {}
        self.log.log("Menu Created", ORPG_DEBUG)
        h = int(xml_dom.getAttribute("height"))
        w = int(xml_dom.getAttribute("width"))
        posx = int(xml_dom.getAttribute("posx"))
        posy = int(xml_dom.getAttribute("posy"))
        maximized = int(xml_dom.getAttribute("maximized"))
        self.SetDimensions(posx, posy, w, h)
        self.log.log("Dimensions Set", ORPG_DEBUG)

        #Update Manager
        self.manifest = manifest.ManifestChanges()
        self.updateMana = upmana.updatemana.updaterFrame(self, "OpenRPG Update Manager Beta 0.6.7", open_rpg, self.manifest, True)
        self.log.log("Menu Created", ORPG_DEBUG)
        h = int(xml_dom.getAttribute("height"))
        w = int(xml_dom.getAttribute("width"))
        posx = int(xml_dom.getAttribute("posx"))
        posy = int(xml_dom.getAttribute("posy"))
        maximized = int(xml_dom.getAttribute("maximized"))
        self.SetDimensions(posx, posy, w, h)
        self.log.log("Dimensions Set", ORPG_DEBUG)

        # Sound Manager
        self.sound_player = orpg.tools.orpg_sound.orpgSound(self)
        open_rpg.add_component("sound", self.sound_player)
        wndinfo = AUI.AuiPaneInfo()
        wndinfo.DestroyOnClose(False)
        wndinfo.Name("Sound Control Toolbar")
        wndinfo.Caption("Sound Control Toolbar")
        wndinfo.Float()
        wndinfo.ToolbarPane()
        wndinfo.Hide()
        self._mgr.AddPane(self.sound_player, wndinfo)
        children = xml_dom._get_childNodes()
        for c in children:
            self.build_window(c, self)

        # status window
        self.status = status_bar(self)
        wndinfo = AUI.AuiPaneInfo()
        wndinfo.DestroyOnClose(False)
        wndinfo.Name("Status Window")
        wndinfo.Caption("Status Window")
        wndinfo.Float()
        wndinfo.ToolbarPane()
        wndinfo.Hide()
        self._mgr.AddPane(self.status, wndinfo)
        self.log.log("Status Window Created", ORPG_DEBUG)

        # Create and show the floating dice toolbar
        self.dieToolBar = orpg.tools.toolBars.DiceToolBar(self, callBack = self.chat.ParsePost)
        wndinfo = AUI.AuiPaneInfo()
        wndinfo.DestroyOnClose(False)
        wndinfo.Name("Dice Tool Bar")
        wndinfo.Caption("Dice Tool Bar")
        wndinfo.Float()
        wndinfo.ToolbarPane()
        wndinfo.Hide()
        self._mgr.AddPane(self.dieToolBar, wndinfo)
        self.log.log("Dice Tool Bar Created", ORPG_DEBUG)

        #Create the Map tool bar
        self.mapToolBar = orpg.tools.toolBars.MapToolBar(self, callBack = self.map.MapBar)
        wndinfo = AUI.AuiPaneInfo()
        wndinfo.DestroyOnClose(False)
        wndinfo.Name("Map Tool Bar")
        wndinfo.Caption("Map Tool Bar")
        wndinfo.Float()
        wndinfo.ToolbarPane()
        wndinfo.Hide()
        self._mgr.AddPane(self.mapToolBar, wndinfo)
        self.log.log("Map Tool Bar Created", ORPG_DEBUG)

        #Create the Browse Server Window
        self.gs = orpg.networking.gsclient.game_server_panel(self)
        wndinfo = AUI.AuiPaneInfo()
        wndinfo.DestroyOnClose(False)
        wndinfo.Name("Browse Server Window")
        wndinfo.Caption("Game Server")
        wndinfo.Float()
        wndinfo.Dockable(False)
        wndinfo.MinSize(wx.Size(640,480))
        wndinfo.Hide()
        self._mgr.AddPane(self.gs, wndinfo)
        self.log.log("Game Server Window Created", ORPG_DEBUG)

        #Create the Alias Lib Window
        self.aliaslib = orpg.tools.aliaslib.AliasLib()
        self.aliaslib.Hide()
        self.log.log("Alias Window Created", ORPG_DEBUG)
        menuid = wx.NewId()
        self.windowsmenu.Append(menuid, "Alias Lib", kind=wx.ITEM_CHECK)
        self.windowsmenu.Check(menuid, False)
        self.Bind(wx.EVT_MENU, self.OnMB_WindowsMenu, id=menuid)
        self.mainwindows[menuid] = "Alias Lib"
        self.mainmenu.Insert(3, self.windowsmenu, 'Windows')
        self.log.log("Windows Menu Done", ORPG_DEBUG)
        self._mgr.Update()
        if wx.VERSION_STRING > "2.8":
            self.Bind(AUI.EVT_AUI_PANE_CLOSE, self.onPaneClose)
        else:
            self.Bind(AUI.EVT_AUI_PANECLOSE, self.onPaneClose)
        self.log.log("AUI Bindings Done", ORPG_DEBUG)

        #Load the layout if one exists
        layout = xml_dom.getElementsByTagName("DockLayout")
        try:
            textnode = self.xml.safe_get_text_node(layout[0])
            self._mgr.LoadPerspective(textnode._get_nodeValue())
        except: pass
        xml_dom.unlink()
        self.log.log("Perspective Loaded", ORPG_DEBUG)
        self._mgr.GetPane("Browse Server Window").Hide()
        self._mgr.Update()
        self.Maximize(maximized)
        self.log.log("GUI is all created", ORPG_DEBUG)
        self.Thaw()
        self.log.log("Exit orpgFrame->build_gui()", ORPG_DEBUG)

    def do_tab_window(self,xml_dom,parent_wnd):
        self.log.log("Enter orpgFrame->do_tab_window(self,xml_dom,parent_wnd)", ORPG_DEBUG)

        # if container window loop through childern and do a recursive call
        temp_wnd = orpgTabberWnd(parent_wnd, style=FNB.FNB_ALLOW_FOREIGN_DND)
        children = xml_dom._get_childNodes()
        for c in children:
            wnd = self.build_window(c,temp_wnd)
            name = c.getAttribute("name")
            temp_wnd.AddPage(wnd, name, False)
        self.log.log("Exit orpgFrame->do_tab_window(self,xml_dom,parent_wnd)", ORPG_DEBUG)
        return temp_wnd

    def build_window(self, xml_dom, parent_wnd):
        name = xml_dom._get_nodeName()
        self.log.log("Enter orpgFrame->build_window(" + name + ")", ORPG_DEBUG)
        if name == "DockLayout" or name == "dock": return
        dir = xml_dom.getAttribute("direction")
        pos = xml_dom.getAttribute("pos")
        height = xml_dom.getAttribute("height")
        width = xml_dom.getAttribute("width")
        cap = xml_dom.getAttribute("caption")
        dockable = xml_dom.getAttribute("dockable")
        layer = xml_dom.getAttribute("layer")

        try: layer = int(layer); dockable = int(dockable)
        except: layer = 0; dockable = 1

        if name == "tab": temp_wnd = self.do_tab_window(xml_dom, parent_wnd)
        elif name == "map":
            temp_wnd = orpg.mapper.map.map_wnd(parent_wnd, -1)
            self.map = temp_wnd
        elif name == "tree":
            temp_wnd = orpg.gametree.gametree.game_tree(parent_wnd, -1)
            self.tree = temp_wnd
            if self.settings.get_setting('ColorTree') == '1':
                self.tree.SetBackgroundColour(self.settings.get_setting('bgcolor'))
                self.tree.SetForegroundColour(self.settings.get_setting('textcolor'))
            else:
                self.tree.SetBackgroundColour('white')
                self.tree.SetForegroundColour('black')

        elif name == "chat":
            temp_wnd = orpg.chat.chatwnd.chat_notebook(parent_wnd, wx.DefaultSize)
            self.chattabs = temp_wnd
            self.chat = temp_wnd.MainChatPanel

        elif name == "player":
            temp_wnd = orpg.player_list.player_list(parent_wnd)
            self.players = temp_wnd
            if self.settings.get_setting('ColorTree') == '1':
                self.players.SetBackgroundColour(self.settings.get_setting('bgcolor'))
                self.players.SetForegroundColour(self.settings.get_setting('textcolor'))
            else:
                self.players.SetBackgroundColour('white')
                self.players.SetForegroundColour('black')

        if parent_wnd != self: return temp_wnd
        menuid = wx.NewId()
        self.windowsmenu.Append(menuid, cap, kind=wx.ITEM_CHECK)
        self.windowsmenu.Check(menuid, True)
        self.Bind(wx.EVT_MENU, self.OnMB_WindowsMenu, id=menuid)
        self.mainwindows[menuid] = cap
        wndinfo = AUI.AuiPaneInfo()
        wndinfo.DestroyOnClose(False)
        wndinfo.Name(cap)
        wndinfo.FloatingSize(wx.Size(int(width), int(height)))
        wndinfo.BestSize(wx.Size(int(width), int(height)))
        wndinfo.Layer(int(layer))
        wndinfo.Caption(cap)

        # Lambda here should work! (future dev)
        if dir.lower() == 'top': wndinfo.Top()
        elif dir.lower() == 'bottom': wndinfo.Bottom()
        elif dir.lower() == 'left': wndinfo.Left()
        elif dir.lower() == 'right': wndinfo.Right()
        elif dir.lower() == 'center': wndinfo.Center(); wndinfo.CaptionVisible(False)

        if dockable != 1:
            wndinfo.Dockable(False)
            wndinfo.Floatable(False)
        if pos != '' or pos != '0' or pos != None:
            wndinfo.Position(int(pos))
        wndinfo.Show()
        self._mgr.AddPane(temp_wnd, wndinfo)
        self.log.log("Exit orpgFrame->build_window(" + name + ")", ORPG_DEBUG)
        return temp_wnd

    def onPaneClose(self, evt):
        self.log.log("Enter orpgFrame->onPaneClose()", ORPG_DEBUG)
        pane = evt.GetPane()
        for wndid, wname in self.mainwindows.iteritems():
            if pane.name == wname: self.windowsmenu.Check(wndid, False); break
        evt.Skip()
        self._mgr.Update()
        self.log.log("Exit orpgFrame->onPaneClose()", ORPG_DEBUG)

    def saveLayout(self):
        self.log.log("Enter orpgFrame->saveLayout()", ORPG_DEBUG)
        filename = orpg.dirpath.dir_struct["user"] + "layout.xml"
        temp_file = open(filename)
        txt = temp_file.read()
        xml_dom = self.xml.parseXml(txt)._get_documentElement()
        temp_file.close()
        (x_size,y_size) = self.GetClientSize()
        (x_pos,y_pos) = self.GetPositionTuple()
        if self.IsMaximized(): max = 1
        else: max = 0
        xml_dom.setAttribute("height", str(y_size))
        xml_dom.setAttribute("width", str(x_size))
        xml_dom.setAttribute("posx", str(x_pos))
        xml_dom.setAttribute("posy", str(y_pos))
        xml_dom.setAttribute("maximized", str(max))
        layout = xml_dom.getElementsByTagName("DockLayout")
        try:
            textnode = self.xml.safe_get_text_node(layout[0])
            textnode._set_nodeValue(str(self._mgr.SavePerspective()))
        except:
            elem = self.xml.minidom.Element('DockLayout')
            elem.setAttribute("DO_NO_EDIT","True")
            textnode = self.xml.safe_get_text_node(elem)
            textnode._set_nodeValue(str(self._mgr.SavePerspective()))
            xml_dom.appendChild(elem)
        temp_file = open(filename, "w")
        temp_file.write(xml_dom.toxml(1))
        temp_file.close()
        self.log.log("Exit saveLayout()", ORPG_DEBUG)

    def build_hotkeys(self):
        self.log.log("Enter orpgFrame->build_hotkeys(self)", ORPG_DEBUG)
        self.mainmenu.accel.xaccel.extend(self.chat.get_hot_keys())
        self.mainmenu.accel.xaccel.extend(self.map.get_hot_keys())
        self.log.log("Exit orpgFrame->build_hotkeys(self)", ORPG_DEBUG)

    def start_timer(self):
        self.log.log("Enter orpgFrame->start_timer(self)", ORPG_DEBUG)
        self.poll_timer.Start(100)
        s = open_rpg.get_component('settings')
        if s.get_setting("Heartbeat") == "1":
            self.ping_timer.Start(1000*60)
            self.log.log("starting heartbeat...", ORPG_DEBUG, True)
        self.log.log("Exit orpgFrame->start_timer(self)", ORPG_DEBUG)

    def kill_mplay_session(self):
        self.log.log("Enter orpgFrame->kill_mplay_session(self)", ORPG_DEBUG)
        self.game_name = ""
        self.session.start_disconnect()
        self.log.log("Exit orpgFrame->kill_mplay_session(self)", ORPG_DEBUG)

    def quit_game(self, evt):
        self.log.log("Enter orpgFrame->quit_game(self, evt)", ORPG_DEBUG)
        dlg = wx.MessageDialog(self,"Exit gaming session?","Game Session",wx.YES_NO)
        if dlg.ShowModal() == wx.ID_YES:
            self.session.exitCondition.notifyAll()
            dlg.Destroy()
            self.kill_mplay_session()
        self.log.log("Exit orpgFrame->quit_game(self, evt)", ORPG_DEBUG)

    def on_status_event(self, evt):
        self.log.log("Enter orpgFrame->on_status_event(self, evt)", ORPG_DEBUG)
        id = evt.get_id()
        status = evt.get_data()
        if id == orpg.networking.mplay_client.STATUS_SET_URL: self.status.set_url(status)
        self.log.log("Exit orpgFrame->on_status_event(self, evt)", ORPG_DEBUG)

    def on_player_event(self, evt):
        self.log.log("Enter orpgFrame->on_player_event(self, evt)", ORPG_DEBUG)
        id = evt.get_id()
        player = evt.get_data()
        display_name = self.chat.chat_display_name(player)
        time_str = time.strftime("%H:%M", time.localtime())
        if id == orpg.networking.mplay_client.PLAYER_NEW:
            self.players.add_player(player)
            self.chat.InfoPost(display_name + " (enter): " + time_str)
        elif id == orpg.networking.mplay_client.PLAYER_DEL:
            self.players.del_player(player)
            self.chat.InfoPost(display_name + " (exit): " + time_str)
        elif id == orpg.networking.mplay_client.PLAYER_UPDATE:
            self.players.update_player(player)
        self.players.Refresh()
        self.log.log("Exit orpgFrame->on_player_event(self, evt)", ORPG_DEBUG)

    def on_group_event(self, evt):
        self.log.log("Enter orpgFrame->on_group_event(self, evt)", ORPG_DEBUG)
        id = evt.get_id()
        data = evt.get_data()

        if id == orpg.networking.mplay_client.GROUP_NEW: self.gs.add_room(data)
        elif id == orpg.networking.mplay_client.GROUP_DEL:
            self.password_manager.RemoveGroupData(data)
            self.gs.del_room(data)
        elif id == orpg.networking.mplay_client.GROUP_UPDATE: self.gs.update_room(data)
        self.log.log("Exit orpgFrame->on_group_event(self, evt)", ORPG_DEBUG)

    def on_receive(self, data, player):
        self.log.log("Enter orpgFrame->on_receive(self, data, player)", ORPG_DEBUG)

        # see if we are ignoring this user
        (ignore_id,ignore_name) = self.session.get_ignore_list()
        for m in ignore_id:
            if m == player[2]: self.log.log("ignoring message from player:" + player[0], ORPG_INFO, True); return

        # ok we are not ignoring this message
        #recvSound = "RecvSound"                #  this will be the default sound.  Whisper will change this below
        if player: display_name = self.chat.chat_display_name(player)
        else: display_name = "Server Administrator"

        if data[:5] == "<tree":
            self.tree.on_receive_data(data,player)
            self.chat.InfoPost(display_name + " has sent you a tree node...")
            #self.tree.OnNewData(data)

        elif data[:4] == "<map": self.map.new_data(data)

        elif data[:5] == "<chat":
            msg = orpg.chat.chat_msg.chat_msg(data)
            self.chat.post_incoming_msg(msg,player)
        else:
        ##############################################################################################
        #  all this below code is for comptiablity with older clients and can be removed after a bit #
        ##############################################################################################
            if data[:3] == "/me":
                # This fixes the emote coloring to comply with what has been asked for by the user
                # population, not to mention, what I committed to many moons ago.
                #  In doing so, Woody's scheme has been tossed out.  I'm sure Woody won't be
                # happy but I'm invoking developer priveledge to satisfy user request, not to mention,
                # this scheme actually makes more sense.  In Woody's scheme, a user could over-ride another
                # users emote color.  This doesn't make sense, rather, people dictate their OWN colors...which is as
                # it should be in the first place and is as it has been with normal text.  In short, this makes
                # sense and is consistent.
                data = data.replace( "/me", "" )

                # Check to see if we find the closing ">" for the font within the first 22 values
                index = data[:22].find(  ">" )
                if index == -1:
                    data = "** " + self.chat.colorize( self.chat.infocolor, display_name + data ) + " **"

                else:
                    # This means that we found a valid font string, so we can simply plug the name into
                    # the string between the start and stop font delimiter
                    print "pre data = " + data
                    data = data[:22] + "** " + display_name + " " + data[22:] + " **"
                    print "post data = " + data

            elif data[:2] == "/w":
                data = data.replace("/w","")
                data = "<b>" + display_name + "</b> (whispering): " + data

            else:
                # Normal text
                if player: data = "<b>" + display_name + "</b>: " + data
                else: data = "<b><i><u>" + display_name + "</u>-></i></b> " + data
            self.chat.Post(data)
        self.log.log("Exit orpgFrame->on_receive(self, data, player)", ORPG_DEBUG)

    def on_mplay_event(self, evt):
        self.log.log("Enter orpgFrame->on_mplay_event(self, evt)", ORPG_DEBUG)

        id = evt.get_id()
        if id == orpg.networking.mplay_client.MPLAY_CONNECTED:
            self.chat.InfoPost("Game connected!")
            self.gs.set_connected(1)
            self.password_manager.ClearPassword("ALL")

        elif id == orpg.networking.mplay_client.MPLAY_DISCONNECTED:
            self.poll_timer.Stop()
            self.ping_timer.Stop()
            self.chat.SystemPost("Game disconnected!")
            self.players.reset()
            self.gs.set_connected(0)
            self.status.set_connect_status("Not Connected")

        ####Begin changes for Custom Exit Message by mDuo13######
        elif id == orpg.networking.mplay_client.MPLAY_DISCONNECTING:
            settings = open_rpg.get_component('settings')
            custom_msg = settings.get_setting("dcmsg")
            custom_msg=custom_msg[:80]
            if custom_msg[:3]=="/me": self.chat.send_chat_message(custom_msg[3:], 3)
            else: self.chat.system_message(custom_msg)
        #####End Changes for Custom Exit Message by mDuo13

        elif id== orpg.networking.mplay_client.MPLAY_GROUP_CHANGE:
            group = evt.get_data()
            self.chat.InfoPost("Moving to room '"+group[1]+"'..")
            if self.gs : self.gs.set_cur_room_text(group[1])
            self.players.reset()
        elif id== orpg.networking.mplay_client.MPLAY_GROUP_CHANGE_F:
            self.chat.SystemPost("Room access denied!")
        self.log.log("Exit orpgFrame->on_mplay_event(self, evt)", ORPG_DEBUG)

    def OnCloseWindow(self, event):
        self.log.log("Enter orpgFrame->OnCloseWindow(self, event)", ORPG_DEBUG)
        dlg = wx.MessageDialog(self, "Quit OpenRPG?", "OpenRPG", wx.YES_NO)
        if dlg.ShowModal() == wx.ID_YES:
            dlg.Destroy()
            self.closed_confirmed()
        self.log.log("Exit orpgFrame->OnCloseWindow(self, event)", ORPG_DEBUG)

    def closed_confirmed(self):
        self.log.log("Enter orpgFrame->closed_confirmed(self)", ORPG_DEBUG)
        self.activeplugins = open_rpg.get_component('plugins')
        self.aliaslib.OnMB_FileSave(None)

        #following lines added by mDuo13
        #########plugin_disabled()#########
        for plugin_fname in self.activeplugins.keys():
            plugin = self.activeplugins[plugin_fname]
            try: plugin.plugin_disabled()
            except Exception, e:
                if str(e) != "'module' object has no attribute 'plugin_disabled'":
                    #print e
                    traceback.print_exc()
        #end mDuo13 added code
        self.saveLayout()
        try: self.settings.save()
        except: self.log.log("[WARNING] Error saving 'settings' component", ORPG_GENERAL, True)

        try: self.map.pre_exit_cleanup()
        except: self.log.log("[WARNING] Map error pre_exit_cleanup()", ORPG_GENERAL, True)

        try:
            save_tree = string.upper(self.settings.get_setting("SaveGameTreeOnExit"))
            if  (save_tree != "0") and (save_tree != "False") and (save_tree != "NO"):
                self.tree.save_tree(self.settings.get_setting("gametree"))
        except: self.log.log("[WARNING] Error saving gametree", ORPG_GENERAL, True)

        if self.session.get_status() == orpg.networking.mplay_client.MPLAY_CONNECTED: self.kill_mplay_session()

        try:
            #Kill all the damn timers
            self.sound_player.timer.Stop()
            del self.sound_player.timer
        except: self.log.log("sound didn't die properly.",ORPG_GENERAL, True)

        try:
            self.poll_timer.Stop()
            self.ping_timer.Stop()
            self.chat.parent.chat_timer.Stop()
            self.map.canvas.zoom_display_timer.Stop()
            self.map.canvas.image_timer.Stop()
            self.status.timer.Stop()
            del self.ping_timer; del self.poll_timer; del self.chat.parent.chat_timer
            del self.map.canvas.zoom_display_timer; del self.map.canvas.image_timer; del self.status.timer
        except: self.log.log("some timer didn't die properly.",ORPG_GENERAL, True)
        self._mgr.UnInit()
        mainapp = wx.GetApp()
        mainapp.ExitMainLoop()
        self.Destroy()

        try:
            if self.server_pipe != None:
                dlg = wx.ProgressDialog("Exit","Stoping server",2,self)
                dlg.Update(2)
                dlg.Show(True)
                self.server_pipe.write("\nkill\n")
                self.log.log("Killing Server process:", ORPG_GENERAL, True)
                time.sleep(5)
                self.server_stop()
                self.server_pipe.close()
                self.std_out.close()
                self.server_thread.exit()
                dlg.Destroy()
                self.log.log("Server killed:", ORPG_GENERAL, True)
        except: pass
        self.log.log("Exit orpgFrame->closed_confirmed(self)", ORPG_DEBUG)


########################################
## Application class
########################################
class orpgSplashScreen(wx.SplashScreen):
    def __init__(self, parent, bitmapfile, duration, callback):
        wx.SplashScreen.__init__(self, wx.Bitmap(bitmapfile), 
            wx.SPLASH_CENTRE_ON_SCREEN | wx.SPLASH_TIMEOUT, duration, None, -1)
        self.callback = callback
        self.closing = False
        self.Bind(wx.EVT_CLOSE, self.callback)

class orpgApp(wx.App):
    def OnInit(self):
        self.log = orpg.tools.orpg_log.orpgLog(orpg.dirpath.dir_struct["user"] + "runlogs/")
        self.log.setLogToConsol(False)
        self.log.log("Main Application Start", ORPG_DEBUG)
        self.manifest = manifest.ManifestChanges()
        #Add the initial global components of the openrpg class
        #Every class should be passed openrpg
        open_rpg.add_component("log", self.log)
        open_rpg.add_component("xml", orpg.orpg_xml)
        open_rpg.add_component("dir_struct", orpg.dirpath.dir_struct)
        open_rpg.add_component("tabbedWindows", [])
        self.validate = orpg.tools.validate.Validate()
        open_rpg.add_component("validate", self.validate)
        self.settings = orpg.tools.orpg_settings.orpgSettings()
        open_rpg.add_component("settings", self.settings)
        self.log.setLogLevel(int(self.settings.get_setting('LoggingLevel')))
        self.called = False
        wx.InitAllImageHandlers()
        self.splash = orpgSplashScreen(None, orpg.dirpath.dir_struct["icon"] + 'splash13.jpg', 3000, self.AfterSplash)
        self.Bind(wx.EVT_KEY_DOWN, self.OnKeyPress)
        self._crust = None
        wx.Yield()
        return True

    def OnKeyPress(self, evt):
        #Event handler
        if evt.AltDown() and evt.CmdDown() and evt.KeyCode == ord('I'): self.ShowShell()
        else: evt.Skip()

    def ShowShell(self):
        #Show the PyCrust window.
        if not self._crust:
            self._crust = wx.py.crust.CrustFrame(self.GetTopWindow())
            self._crust.shell.interp.locals['app'] = self
        win = wx.FindWindowAtPointer()
        self._crust.shell.interp.locals['win'] = win
        self._crust.Show()

    def AfterSplash(self,evt):
        if not self.called:
            self.splash.Hide()
            self.called = True
            self.frame = orpgFrame(None, wx.ID_ANY, MENU_TITLE)
            self.frame.Raise()
            self.frame.Refresh()
            self.frame.Show(True)
            self.SetTopWindow(self.frame)
            #self.frame.show_dlgs()
            self.frame.post_show_init()
            wx.CallAfter(self.splash.Close)
            return True

    def OnExit_CleanUp(self):
        self.log.log("Preforming cleanup\n", ORPG_DEBUG)
        try: del os.environ["OPENRPG_BASE"]
        except: pass
        try: os.remove(os.environ["OPENRPG_BASE"] + os.sep + 'orpg' + os.sep + 'dirpath' + os.sep + 'approot.py')
        except: pass
        try: os.remove(os.environ["OPENRPG_BASE"] + os.sep + 'orpg' + os.sep + 'dirpath' + os.sep + 'approot.pyc')
        except: pass

    def OnExit(self):
        self.OnExit_CleanUp()
        #Exit
        self.log.log("Main Application Exit\n\n", ORPG_DEBUG)
