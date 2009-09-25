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

import wx.py
from orpg import minidom
import orpg.player_list
import orpg.tools.pluginui as pluginUI
import orpg.tools.aliaslib
import orpg.tools.toolBars
import orpg.tools.orpg_sound
import orpg.tools.rgbhex
import orpg.gametree.gametree
import orpg.chat.chatwnd
import orpg.networking.gsclient
import orpg.networking.mplay_client
import orpg.mapper.map
import orpg.mapper.images

import upmana.updatemana
import upmana.manifest as manifest

from orpg.dirpath import dir_struct
from orpg.dieroller.utils import DiceManager
from orpg.tools.orpg_settings import settings
from orpg.tools.validate import validate
from orpg.tools.passtool import PassTool
from orpg.tools.orpg_log import logger, crash
from orpg.tools.decorators import debugging
from orpg.tools.metamenus import MenuBarEx

#from xml.etree.ElementTree import ElementTree, Element
#from xml.etree.ElementTree import fromstring, tostring
from orpg.orpg_xml import xml #to be replaced by etree


####################################
## Main Frame
####################################


class orpgFrame(wx.Frame):
    @debugging
    def __init__(self, parent, id, title):
        wx.Frame.__init__(self, parent, id, title, wx.Point(100, 100), wx.Size(600,420), style=wx.DEFAULT_FRAME_STYLE)
        self.validate = component.get("validate")
        logger.debug("Enter orpgFrame")
        self.rgb = orpg.tools.rgbhex.RGBHex()
        self._mgr = AUI.AuiManager(self)

        # Determine which icon format to use
        icon = None
        if wx.Platform == '__WXMSW__': icon = wx.Icon(dir_struct["icon"]+'d20.ico', wx.BITMAP_TYPE_ICO)
        else: icon = wx.Icon(dir_struct["icon"]+"d20.xpm", wx.BITMAP_TYPE_XPM)
        self.SetIcon( icon )

        # create session
        call_backs = {"on_receive":self.on_receive,
                "on_mplay_event":self.on_mplay_event,
                "on_group_event":self.on_group_event,
                "on_player_event":self.on_player_event,
                "on_status_event":self.on_status_event,
                "on_password_signal":self.on_password_signal,
                "orpgFrame":self}
        self.settings = component.get('settings') #Arbitrary until settings updated with Core.
        self.session = orpg.networking.mplay_client.mplay_client(self.settings.get_setting("player"), call_backs)
        self.poll_timer = wx.Timer(self, wx.NewId())
        self.Bind(wx.EVT_TIMER, self.session.poll, self.poll_timer)
        self.poll_timer.Start(100)
        self.ping_timer = wx.Timer(self, wx.NewId())
        self.Bind(wx.EVT_TIMER, self.session.update, self.ping_timer)

        # create roller manager
        self.DiceManager = DiceManager(settings.get_setting("dieroller"))
        component.add('DiceManager', self.DiceManager)

        #create password manager --SD 8/03
        self.password_manager = component.get('password_manager')
        component.add("session", self.session)
        component.add('frame', self)

        # build frame windows
        self.build_menu()
        self.build_gui()
        self.build_hotkeys()

        logger.debug("GUI Built")
        component.add("chat",self.chat)
        component.add("map",self.map)
        component.add("alias", self.aliaslib)

        logger.debug("openrpg components all added")
        self.tree.load_tree(settings.get_setting("gametree"))
        logger.debug("Tree Loaded")
        self.players.size_cols()

        #Load the Plugins This has to be after the chat component has been added
        component.add('pluginmenu', self.pluginMenu)
        self.pluginsFrame.Start()
        logger.debug("plugins reloaded and startup plugins launched")
        self.Bind(wx.EVT_CLOSE, self.OnCloseWindow)

        #Load Update Manager
        component.add('updatemana', self.updateMana)
        logger.debug("update manager reloaded")
        self.Bind(wx.EVT_CLOSE, self.OnCloseWindow)

        #Load Update Manager
        component.add('debugconsole', self.debugger)
        logger.debug("debugger window")
        self.Bind(wx.EVT_CLOSE, self.OnCloseWindow)

    @debugging
    def post_show_init(self):
        """Some Actions need to be done after the main fram is drawn"""
        self.players.size_cols()

    @debugging
    def get_activeplugins(self):
        try: tmp = self.pluginsFrame.get_activeplugins()
        except: tmp = {}
        return tmp

    @debugging
    def get_startplugins(self):
        try: tmp = self.pluginsFrame.get_startplugins()
        except: tmp = {}
        return tmp

    @debugging
    def on_password_signal(self,signal,type,id,data):
        try:
            msg = ["DEBUG: password response= ",
                   str(signal),
                   " (T:",
                   str(type),
                   "  #",
                   str(id),
                   ")"]
            logger.debug("".join(msg))
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

    @debugging
    def build_menu(self):
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
        if settings.get_setting('Heartbeat') == '1':
            self.mainmenu.SetMenuState("GameServerServerHeartbeat", True)

        tabtheme = settings.get_setting('TabTheme')  #This change is stable. TaS.
        self.mainmenu.SetMenuState("OpenRPGTabStylesSlantedColorful", tabtheme == 'slanted&colorful')
        self.mainmenu.SetMenuState("OpenRPGTabStylesSlantedBlackandWhite", tabtheme == 'slanted&bw')
        self.mainmenu.SetMenuState("OpenRPGTabStylesSlantedAqua", tabtheme == 'slanted&aqua')
        self.mainmenu.SetMenuState("OpenRPGTabStylesFlatBlackandWhite", tabtheme == 'flat&bw')
        self.mainmenu.SetMenuState("OpenRPGTabStylesFlatAqua", tabtheme == 'flat&aqua')
        self.mainmenu.SetMenuState("OpenRPGTabStylesSlantedCustom", tabtheme == 'customslant')
        self.mainmenu.SetMenuState("OpenRPGTabStylesFlatCustom", tabtheme == 'customflat')

        lvl = int(settings.get_setting('LoggingLevel'))
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

        # Traipse Suite of Additions.
        self.traipseSuite = wx.Menu()
        self.mainmenu.Insert(5, self.traipseSuite, "&Traipse Suite")

        mana = wx.MenuItem(self.traipseSuite, wx.ID_ANY, "Update Manager", "Update Manager")
        self.Bind(wx.EVT_MENU, self.OnMB_UpdateManagerPanel, mana)
        self.traipseSuite.AppendItem(mana)

        self.debugConsole = wx.MenuItem(self.traipseSuite, -1, "Debug Console", "Debug Console")
        self.Bind(wx.EVT_MENU, self.OnMB_DebugConsole, self.debugConsole)
        self.traipseSuite.AppendItem(self.debugConsole)

    def TraipseSuiteWarn(self, menuitem):
        ### Beta ### Allows for the reuse of the 'Attention' menu.
        ### component.get('frame').TraipseSuiteWarn('item') ### Portable
        self.mainmenu.Replace(8, self.traipseSuite, '&Traipse Suite!')
        if menuitem == 'debug':
            if self.debugger.IsShown() == True:
                self.mainmenu.Replace(8, self.traipseSuite, '&Traipse Suite')
            else:
                self.debugConsole.SetBitmap(wx.Bitmap(dir_struct["icon"] + 'spotlight.png'))
                self.traipseSuite.RemoveItem(self.debugConsole)
                self.traipseSuite.AppendItem(self.debugConsole)

    def TraipseSuiteWarnCleanup(self, menuitem):
        ### Beta ### Allows for portable cleanup of the 'Attention' menu.
        ### component.get('frame').TraipseSuiteWarnCleanup('item') ### Portable
        self.mainmenu.Replace(8, self.traipseSuite, '&Traipse Suite')
        if menuitem == 'debug':
            self.traipseSuite.RemoveItem(self.debugConsole)
            self.debugConsole.SetBitmap(wx.Bitmap(dir_struct["icon"] + 'clear.gif'))
            self.traipseSuite.AppendItem(self.debugConsole)
       

    #################################
    ## All Menu Events
    #################################
    #Tab Styles Menus
    @debugging
    def SetTabStyles(self, *args, **kwargs):

        tabtheme = settings.get_setting('TabTheme')  #This change is stable. TaS.
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
            except: logger.general('Invalid Syntax for orpgFrame->SetTabStyles(self, *args, **kwargs)'); return
        if kwargs.has_key('menu'): menu = kwargs['menu']
        else:
            try: menu = args[0]
            except: logger.general('Invalid Syntax for orpgFrame->SetTabStyles(self, *args, **kwargs)'); return

        if kwargs.has_key('graidentTo'): graidentTo = kwargs['graidentTo']
        else: graidentTo = None
        if kwargs.has_key('graidentFrom'): graidentFrom = kwargs['graidentFrom']
        else: graidentFrom = None
        if kwargs.has_key('textColor'): textColor = kwargs['textColor']
        else: textColor = None

        #Run though the current tabbed window list and remove those that have been closed
        tabbedwindows = component.get("tabbedWindows")
        new = []
        for wnd in tabbedwindows:
            try: style = wnd.GetWindowStyleFlag(); new.append(wnd)
            except:  pass
        tabbedwindows = new
        component.add("tabbedWindows", tabbedwindows)

        #Run though the new list and set the proper styles
        tabbg = settings.get_setting('TabBackgroundGradient')
        (red, green, blue) = self.rgb.rgb_tuple(tabbg)

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

    @debugging
    def OnMB_OpenRPGNewMap(self):
        pass #Not Implemented yet!

    @debugging
    def OnMB_OpenRPGTabStylesSlantedColorful(self):
        if self.mainmenu.GetMenuState("OpenRPGTabStylesSlantedColorful"):
            settings.set_setting('TabTheme', 'slanted&colorful')
            self.SetTabStyles("OpenRPGTabStylesSlantedColorful", FNB.FNB_VC8|FNB.FNB_COLORFUL_TABS)
        else: self.mainmenu.SetMenuState("OpenRPGTabStylesSlantedColorful", True)

    @debugging
    def OnMB_OpenRPGTabStylesSlantedBlackandWhite(self):
        if self.mainmenu.GetMenuState("OpenRPGTabStylesSlantedBlackandWhite"):
            settings.set_setting('TabTheme', 'slanted&bw')
            self.SetTabStyles("OpenRPGTabStylesSlantedBlackandWhite", 
                FNB.FNB_VC8, graidentTo=wx.WHITE, graidentFrom=wx.WHITE, textColor=wx.BLACK)
        else: self.mainmenu.SetMenuState("OpenRPGTabStylesSlantedBlackandWhite", True)

    @debugging
    def OnMB_OpenRPGTabStylesSlantedAqua(self):
        if self.mainmenu.GetMenuState("OpenRPGTabStylesSlantedAqua"):
            settings.set_setting('TabTheme', 'slanted&aqua')
            self.SetTabStyles("OpenRPGTabStylesSlantedAqua", FNB.FNB_VC8, 
                graidentTo=wx.Color(0, 128, 255), graidentFrom=wx.WHITE, textColor=wx.BLACK)
        else: self.mainmenu.SetMenuState("OpenRPGTabStylesSlantedAqua", True)

    @debugging
    def OnMB_OpenRPGTabStylesSlantedCustom(self):
        if self.mainmenu.GetMenuState("OpenRPGTabStylesSlantedCustom"):
            settings.set_setting('TabTheme', 'customslant')
            gfrom = settings.get_setting('TabGradientFrom')
            (fred, fgreen, fblue) = self.rgb.rgb_tuple(gfrom)
            gto = settings.get_setting('TabGradientTo')
            (tored, togreen, toblue) = self.rgb.rgb_tuple(gto)
            tabtext = settings.get_setting('TabTextColor')
            (tred, tgreen, tblue) = self.rgb.rgb_tuple(tabtext)
            tabbg = settings.get_setting('TabBackgroundGradient')
            (red, green, blue) = self.rgb.rgb_tuple(tabbg)
            self.SetTabStyles("OpenRPGTabStylesSlantedCustom", FNB.FNB_VC8, 
                graidentTo=wx.Color(tored, togreen, toblue), graidentFrom=wx.Color(fred, fgreen, fblue), 
                textColor=wx.Color(tred, tgreen, tblue))
        else: self.mainmenu.SetMenuState("OpenRPGTabStylesSlantedCustom", True)

    @debugging
    def OnMB_OpenRPGTabStylesFlatBlackandWhite(self):
        if self.mainmenu.GetMenuState("OpenRPGTabStylesFlatBlackandWhite"):
            settings.set_setting('TabTheme', 'flat&bw')
            self.SetTabStyles("OpenRPGTabStylesFlatBlackandWhite", FNB.FNB_FANCY_TABS, 
                graidentTo=wx.WHITE, graidentFrom=wx.WHITE, textColor=wx.BLACK)
        else: self.mainmenu.SetMenuState("OpenRPGTabStylesFlatBlackandWhite", True)

    @debugging
    def OnMB_OpenRPGTabStylesFlatAqua(self):
        if self.mainmenu.GetMenuState("OpenRPGTabStylesFlatAqua"):
            settings.set_setting('TabTheme', 'flat&aqua')
            self.SetTabStyles("OpenRPGTabStylesFlatAqua", FNB.FNB_FANCY_TABS, 
                graidentTo=wx.Color(0, 128, 255), graidentFrom=wx.WHITE, textColor=wx.BLACK)
        else: self.mainmenu.SetMenuState("OpenRPGTabStylesFlatAqua", True)

    @debugging
    def OnMB_OpenRPGTabStylesFlatCustom(self):
        if self.mainmenu.GetMenuState("OpenRPGTabStylesFlatCustom"):
            settings.set_setting('TabTheme', 'customflat')
            gfrom = settings.get_setting('TabGradientFrom')
            (fred, fgreen, fblue) = self.rgb.rgb_tuple(gfrom)
            gto = settings.get_setting('TabGradientTo')
            (tored, togreen, toblue) = self.rgb.rgb_tuple(gto)
            tabtext = settings.get_setting('TabTextColor')
            (tred, tgreen, tblue) = self.rgb.rgb_tuple(tabtext)
            tabbg = settings.get_setting('TabBackgroundGradient')
            (red, green, blue) = self.rgb.rgb_tuple(tabbg)
            self.SetTabStyles("OpenRPGTabStylesFlatCustom", FNB.FNB_FANCY_TABS, 
                graidentTo=wx.Color(tored, togreen, toblue), graidentFrom=wx.Color(fred, fgreen, fblue), 
                textColor=wx.Color(tred, tgreen, tblue))
        else: self.mainmenu.SetMenuState("OpenRPGTabStylesFlatCustom", True)

    #Window Menu
    @debugging
    def OnMB_WindowsMenu(self, event):
        menuid = event.GetId()
        name = self.mainwindows[menuid]
        if name == 'Alias Lib':
            if self.aliaslib.IsShown(): self.aliaslib.Hide()
            else: self.aliaslib.Show()
        else:
            if self._mgr.GetPane(name).IsShown(): self._mgr.GetPane(name).Hide()
            else: self._mgr.GetPane(name).Show()
            self._mgr.Update()

    #OpenRPG Menu
    @debugging
    def OnMB_OpenRPGSettings(self):
        dlg = orpg.tools.orpg_settings.orpgSettingsWnd(self)
        dlg.Centre()
        dlg.ShowModal()

    def OnMB_OpenRPGExit(self):
        self.OnCloseWindow(0)

    #Game Server Menu
    @debugging
    def OnMB_GameServerBrowseServers(self):
        if self._mgr.GetPane("Browse Server Window").IsShown() == True: self._mgr.GetPane("Browse Server Window").Hide()
        else: self._mgr.GetPane("Browse Server Window").Show()
        self._mgr.Update()

    @debugging
    def OnMB_GameServerServerHeartbeat(self):
        if self.mainmenu.GetMenuState("GameServerServerHeartbeat"): settings.set_setting('Heartbeat', '1')
        else: settings.set_setting('Heartbeat', '0')

    @debugging
    def OnMB_GameServerStartServer(self):
        start_dialog = wx.ProgressDialog( "Server Loading", "Server Loading, Please Wait...", 1, self )
        # Spawn the new process and close the stdout handle from it
        start_dialog.Update( 0 )
        # Adjusted following code to work with win32, can't test for Unix
        # as per reported bug 586227
        if wx.Platform == "__WXMSW__":
            arg = '\"' + os.path.normpath(dir_struct["home"] + 'start_server_gui.py') + '\"'
            args = ( sys.executable, arg )
        else:
            arg = dir_struct["home"] + 'start_server_gui.py'
            args = (arg,arg)
        os.spawnv( os.P_NOWAIT, sys.executable, args )
        start_dialog.Update( 1 )
        start_dialog.Show(False)
        start_dialog.Destroy()

    # Tools Menu
    @debugging
    def OnMB_PluginControlPanel(self, evt):
        if self.pluginsFrame.IsShown() == True: self.pluginsFrame.Hide()
        else: self.pluginsFrame.Show()

    @debugging
    def OnMB_UpdateManagerPanel(self, evt):
        if self.updateMana.IsShown() == True: self.updateMana.Hide()
        else: self.updateMana.Show()

    @debugging
    def OnMB_DebugConsole(self, evt):
        self.TraipseSuiteWarnCleanup('debug') ### Beta ###
        if self.debugger.IsShown() == True: self.debugger.Hide()
        else: self.debugger.Show()

    @debugging
    def OnMB_ToolsLoggingLevelDebug(self):
        lvl = logger.log_level
        if self.mainmenu.GetMenuState("ToolsLoggingLevelDebug"): lvl |= ORPG_DEBUG
        else: lvl &= ~ORPG_DEBUG
        logger.log_level = lvl
        settings.set('LoggingLevel', lvl)

    @debugging
    def OnMB_ToolsLoggingLevelNote(self):
        lvl = logger.log_level
        if self.mainmenu.GetMenuState("ToolsLoggingLevelNote"): lvl |= ORPG_DEBUG
        else: lvl &= ~ORPG_DEBUG
        logger.log_level = lvl
        settings.set('LoggingLevel', lvl)

    @debugging
    def OnMB_ToolsLoggingLevelInfo(self):
        lvl = logger.log_level
        if self.mainmenu.GetMenuState("ToolsLoggingLevelInfo"): lvl |= ORPG_INFO
        else: lvl &= ~ORPG_INFO
        logger.log_level = lvl
        settings.set('LoggingLevel', lvl)

    @debugging
    def OnMB_ToolsLoggingLevelGeneral(self):
        lvl = logger.log_level
        if self.mainmenu.GetMenuState("ToolsLoggingLevelGeneral"): lvl |= ORPG_GENERAL
        else: lvl &= ~ORPG_GENERAL
        logger.log_level = lvl
        settings.set('LoggingLevel', lvl)

    @debugging
    def OnMB_ToolsPasswordManager(self):
        if self.mainmenu.GetMenuState("ToolsPasswordManager"): self.password_manager.Enable()
        else: self.password_manager.Disable()

    @debugging
    def OnMB_ToolsStatusBar(self):
        if self._mgr.GetPane("Status Window").IsShown() == True:
            self.mainmenu.SetMenuState("ToolsStatusBar", False)
            self._mgr.GetPane("Status Window").Hide()
        else:
            self.mainmenu.SetMenuState("ToolsStatusBar", True)
            self._mgr.GetPane("Status Window").Show()
        self._mgr.Update()

    @debugging
    def OnMB_ToolsSoundToolbar(self):
        if self._mgr.GetPane("Sound Control Toolbar").IsShown() == True:
            self.mainmenu.SetMenuState("ToolsSoundToolbar", False)
            self._mgr.GetPane("Sound Control Toolbar").Hide()
        else:
            self.mainmenu.SetMenuState("ToolsSoundToolbar", True)
            self._mgr.GetPane("Sound Control Toolbar").Show()
        self._mgr.Update()

    @debugging
    def OnMB_ToolsDiceBar(self):
        if self._mgr.GetPane("Dice Tool Bar").IsShown() == True:
            self.mainmenu.SetMenuState("ToolsDiceBar", False)
            self._mgr.GetPane("Dice Tool Bar").Hide()
        else:
            self.mainmenu.SetMenuState("ToolsDiceBar", True)
            self._mgr.GetPane("Dice Tool Bar").Show()
        self._mgr.Update()

    @debugging
    def OnMB_ToolsMapBar(self):
        if self._mgr.GetPane("Map Tool Bar").IsShown() == True:
            self.mainmenu.SetMenuState("ToolsMapBar", False)
            self._mgr.GetPane("Map Tool Bar").Hide()
        else:
            self.mainmenu.SetMenuState("ToolsMapBar", True)
            self._mgr.GetPane("Map Tool Bar").Show()
        self._mgr.Update()

    #Help Menu #Needs a custom Dialog because it is ugly on Windows
    @debugging
    def OnMB_HelpAbout(self):
        if self.AboutORPG.IsShown() == True: self.AboutORPG.Hide()
        else: self.AboutORPG.Show()

    @debugging
    def OnMB_HelpOnlineUserGuide(self):
        wb = webbrowser.get()
        wb.open("http://www.assembla.com/wiki/show/traipse/User_Manual")

    @debugging
    def OnMB_HelpChangeLog(self):
        wb = webbrowser.get()
        wb.open("http://www.assembla.com/spaces/milestones/index/traipse?spaces_tool_id=Milestones")

    @debugging
    def OnMB_HelpReportaBug(self):
        wb = webbrowser.get()
        wb.open("http://www.assembla.com/spaces/tickets/index/traipse_dev?spaces_tool_id=Tickets")


    #################################
    ##    Build the GUI
    #################################
    @debugging
    def build_gui(self):
        self.Freeze()
        self.validate.config_file("layout.xml","default_layout.xml")

        filename = dir_struct["user"] + "layout.xml"
        temp_file = open(filename)
        txt = temp_file.read()
        xml_dom = xml.parseXml(txt)._get_documentElement()
        temp_file.close()

        """ Would a component work better? 
        etree = ElementTree()
        with open(dir_struct['user'] + 'layout.xml') as f:
            etree.parse(f)

        base = etree.getroot()
        """
        self.windowsmenu = wx.Menu()
        self.mainwindows = {}

        # About Window
        self.AboutORPG = AboutORPG(self)

        #Plugins Window
        self.pluginsFrame = pluginUI.PluginFrame(self)
        component.add("plugins", self.get_activeplugins())
        component.add("startplugs", self.get_startplugins())
        logger.debug("Menu Created")
        h = int(xml_dom.getAttribute("height"))
        w = int(xml_dom.getAttribute("width"))
        posx = int(xml_dom.getAttribute("posx"))
        posy = int(xml_dom.getAttribute("posy"))
        maximized = int(xml_dom.getAttribute("maximized"))
        self.SetDimensions(posx, posy, w, h)
        logger.debug("Dimensions Set")

        # Update Manager
        self.manifest = manifest.ManifestChanges()
        self.updateMana = upmana.updatemana.updaterFrame(self, 
            "OpenRPG Update Manager Beta 0.8", component, self.manifest, True)
        logger.debug("Menu Created")
        h = int(xml_dom.getAttribute("height"))
        w = int(xml_dom.getAttribute("width"))
        posx = int(xml_dom.getAttribute("posx"))
        posy = int(xml_dom.getAttribute("posy"))
        maximized = int(xml_dom.getAttribute("maximized"))
        self.SetDimensions(posx, posy, w, h)
        logger.debug("Dimensions Set")

        # Debug Console
        self.debugger = orpg.tools.orpg_log.DebugConsole(self)
        logger.debug("Menu Created")
        h = int(xml_dom.getAttribute("height"))
        w = int(xml_dom.getAttribute("width"))
        posx = int(xml_dom.getAttribute("posx"))
        posy = int(xml_dom.getAttribute("posy"))
        maximized = int(xml_dom.getAttribute("maximized"))
        self.SetDimensions(posx, posy, w, h)
        logger.debug("Dimensions Set")

        # Sound Manager
        self.sound_player = orpg.tools.orpg_sound.orpgSound(self)
        component.add("sound", self.sound_player)
        wndinfo = AUI.AuiPaneInfo()
        menuid = wx.NewId()
        self.mainwindows[menuid] = "Sound Control Toolbar"
        wndinfo.DestroyOnClose(False)
        wndinfo.Name("Sound Control Toolbar")
        wndinfo.Caption("Sound Control Toolbar")
        wndinfo.Float()
        wndinfo.ToolbarPane()
        wndinfo.Hide()
        self._mgr.AddPane(self.sound_player, wndinfo)
        children = xml_dom._get_childNodes()
        for c in children: self.build_window(c, self)

        # status window
        self.status = status_bar(self)
        wndinfo = AUI.AuiPaneInfo()
        menuid = wx.NewId()
        self.mainwindows[menuid] = "Status Window"
        wndinfo.DestroyOnClose(False)
        wndinfo.Name("Status Window")
        wndinfo.Caption("Status Window")
        wndinfo.Float()
        wndinfo.ToolbarPane()
        wndinfo.Hide()
        self._mgr.AddPane(self.status, wndinfo)
        logger.debug("Status Window Created")

        # Create and show the floating dice toolbar
        self.dieToolBar = orpg.tools.toolBars.DiceToolBar(self, callBack = self.chat.ParsePost)
        wndinfo = AUI.AuiPaneInfo()
        menuid = wx.NewId()
        self.mainwindows[menuid] = "Dice Tool Bar"
        wndinfo.DestroyOnClose(False)
        wndinfo.Name("Dice Tool Bar")
        wndinfo.Caption("Dice Tool Bar")
        wndinfo.Float()
        wndinfo.ToolbarPane()
        wndinfo.Hide()
        self._mgr.AddPane(self.dieToolBar, wndinfo)
        logger.debug("Dice Tool Bar Created")

        #Create the Map tool bar
        self.mapToolBar = orpg.tools.toolBars.MapToolBar(self, callBack = self.map.MapBar)
        wndinfo = AUI.AuiPaneInfo()
        menuid = wx.NewId()
        self.mainwindows[menuid] = "Map Tool Bar"
        wndinfo.DestroyOnClose(False)
        wndinfo.Name("Map Tool Bar")
        wndinfo.Caption("Map Tool Bar")
        wndinfo.Float()
        wndinfo.ToolbarPane()
        wndinfo.Hide()
        self._mgr.AddPane(self.mapToolBar, wndinfo)
        logger.debug("Map Tool Bar Created")

        #Create the Browse Server Window #Turn into frame, as with others.
        self.gs = orpg.networking.gsclient.game_server_panel(self)
        wndinfo = AUI.AuiPaneInfo()
        wndinfo.DestroyOnClose(False)
        wndinfo.Name("Browse Server Window")
        wndinfo.Caption("Game Server")
        wndinfo.Float()
        wndinfo.FloatingPosition((50,50))
        wndinfo.Dockable(False)
        wndinfo.MinSize(wx.Size(640,480))
        wndinfo.Hide()
        self._mgr.AddPane(self.gs, wndinfo)
        logger.debug("Game Server Window Created")

        #Create the Alias Lib Window
        self.aliaslib = orpg.tools.aliaslib.AliasLib()
        self.aliaslib.Hide()
        logger.debug("Alias Window Created")
        menuid = wx.NewId()
        self.windowsmenu.Append(menuid, "Alias Lib", kind=wx.ITEM_CHECK)
        self.windowsmenu.Check(menuid, False)
        self.Bind(wx.EVT_MENU, self.OnMB_WindowsMenu, id=menuid)
        self.mainwindows[menuid] = "Alias Lib"
        self.mainmenu.Insert(3, self.windowsmenu, 'Windows')
        logger.debug("Windows Menu Done")
        self._mgr.Update()
        if wx.VERSION_STRING > "2.8": self.Bind(AUI.EVT_AUI_PANE_CLOSE, self.onPaneClose)
        else: self.Bind(AUI.EVT_AUI_PANECLOSE, self.onPaneClose)
        logger.debug("AUI Bindings Done")

        #Load the layout if one exists
        layout = xml_dom.getElementsByTagName("DockLayout")
        try:
            textnode = xml.safe_get_text_node(layout[0])
            self._mgr.LoadPerspective(textnode._get_nodeValue())
        except: pass
        xml_dom.unlink()
        logger.debug("Perspective Loaded")
        self._mgr.GetPane("Browse Server Window").Hide()
        self._mgr.Update()
        self.Maximize(maximized)
        logger.debug("GUI is all created")
        self.Thaw()

    @debugging
    def do_tab_window(self,xml_dom,parent_wnd):
    #def do_tab_window(self, etreeEl, parent_wnd):
        # if container window loop through childern and do a recursive call
        temp_wnd = orpgTabberWnd(parent_wnd, style=FNB.FNB_ALLOW_FOREIGN_DND)

        children = xml_dom._get_childNodes()
        for c in children:
            wnd = self.build_window(c,temp_wnd)
            name = c.getAttribute("name")
            temp_wnd.AddPage(wnd, name, False)

        """
        for c in etreeEl.getchildren():
            wnd = self.build_window(c, temp_wnd)
            temp_wnd.AddPage(wnd, c.get('name'), False)
        """
        return temp_wnd

    @debugging
    def build_window(self, xml_dom, parent_wnd):
        name = xml_dom._get_nodeName()
        if name == "DockLayout" or name == "dock": return
        dirc = xml_dom.getAttribute("direction") #should NOT use dir, it is a built in function.
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
            if settings.get_setting('ColorTree') == '1':
                self.tree.SetBackgroundColour(settings.get_setting('bgcolor'))
                self.tree.SetForegroundColour(settings.get_setting('textcolor'))
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
            if settings.get_setting('ColorTree') == '1':
                self.players.SetBackgroundColour(settings.get_setting('bgcolor'))
                self.players.SetForegroundColour(settings.get_setting('textcolor'))
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
        if dirc.lower() == 'top': wndinfo.Top()
        elif dirc.lower() == 'bottom': wndinfo.Bottom()
        elif dirc.lower() == 'left': wndinfo.Left()
        elif dirc.lower() == 'right': wndinfo.Right()
        elif dirc.lower() == 'center': wndinfo.Center(); wndinfo.CaptionVisible(False)

        if dockable != 1:
            wndinfo.Dockable(False)
            wndinfo.Floatable(False)
        if pos != '' or pos != '0' or pos != None:
            wndinfo.Position(int(pos))
        wndinfo.Show()
        self._mgr.AddPane(temp_wnd, wndinfo)
        return temp_wnd

    @debugging
    def onPaneClose(self, evt):
        pane = evt.GetPane()
        #Arbitrary If ELIF fix. Items had incorrect ID's set. Finding correct ID will fix it for the iteration.
        #Adding ID also fixed docking. Go figure.
        if pane.name == 'Sound Control Toolbar': self.mainmenu.SetMenuState('ToolsSoundToolbar', False) 
        elif pane.name == 'Status Window': self.mainmenu.SetMenuState('ToolsStatusBar', False) 
        elif pane.name == 'Dice Tool Bar': self.mainmenu.SetMenuState('ToolsDiceBar', False) 
        elif pane.name == 'Map Tool Bar': self.mainmenu.SetMenuState('ToolsMapBar', False) 
        else: 
            for wndid, wname in self.mainwindows.iteritems():
                #print pane.name, wname, wndid
                if pane.name == wname: self.windowsmenu.Check(wndid, False); break
        evt.Skip()
        self._mgr.Update()

    @debugging
    def saveLayout(self):
        filename = dir_struct["user"] + "layout.xml"
        temp_file = open(filename)
        txt = temp_file.read()
        xml_dom = xml.parseXml(txt)._get_documentElement()
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
            textnode = xml.safe_get_text_node(layout[0])
            textnode._set_nodeValue(str(self._mgr.SavePerspective()))
        except:
            elem = minidom.Element('DockLayout')
            elem.setAttribute("DO_NO_EDIT","True")
            textnode = xml.safe_get_text_node(elem)
            textnode._set_nodeValue(str(self._mgr.SavePerspective()))
            xml_dom.appendChild(elem)
        temp_file = open(filename, "w")
        temp_file.write(xml_dom.toxml(1))
        temp_file.close()

    @debugging
    def build_hotkeys(self):
        self.mainmenu.accel.xaccel.extend(self.chat.get_hot_keys())
        self.mainmenu.accel.xaccel.extend(self.map.get_hot_keys())

    @debugging
    def start_timer(self):
        self.poll_timer.Start(100)
        s = component.get('settings')
        if s.get_setting("Heartbeat") == "1":
            self.ping_timer.Start(1000*60)
            logger.debug("starting heartbeat...", True)

    @debugging
    def kill_mplay_session(self):
        self.game_name = ""
        self.session.start_disconnect()

    @debugging
    def quit_game(self, evt):
        dlg = wx.MessageDialog(self,"Exit gaming session?","Game Session",wx.YES_NO)
        if dlg.ShowModal() == wx.ID_YES:
            self.session.exitCondition.notifyAll()
            dlg.Destroy()
            self.kill_mplay_session()

    @debugging
    def on_status_event(self, evt):
        id = evt.get_id()
        status = evt.get_data()
        if id == orpg.networking.mplay_client.STATUS_SET_URL: self.status.set_url(status)

    @debugging
    def on_player_event(self, evt):
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

    @debugging
    def on_group_event(self, evt):
        id = evt.get_id()
        data = evt.get_data()
        if id == orpg.networking.mplay_client.GROUP_NEW: self.gs.add_room(data)
        elif id == orpg.networking.mplay_client.GROUP_DEL:
            self.password_manager.RemoveGroupData(data)
            self.gs.del_room(data)
        elif id == orpg.networking.mplay_client.GROUP_UPDATE: self.gs.update_room(data)

    @debugging
    def on_receive(self, data, player):
        # see if we are ignoring this user
        (ignore_id,ignore_name) = self.session.get_ignore_list()
        for m in ignore_id:
            if m == player[2]: logger.debug("ignoring message from player:" + player[0], True); return

        # ok we are not ignoring this message
        #recvSound = "RecvSound"     #  this will be the default sound.  Whisper will change this below
        if player: display_name = self.chat.chat_display_name(player)
        else: display_name = "Server Administrator"

        if data[:5] == "<tree":
            self.tree.on_receive_data(data,player)
            self.chat.InfoPost(display_name + " has sent you a tree node...")

        elif data[:4] == "<map": self.map.new_data(data)

        elif data[:5] == "<chat":
            msg = orpg.chat.chat_msg.chat_msg(data)
            self.chat.post_incoming_msg(msg,player)
        else:
            """
            all this below code is for comptiablity with older clients and can
            be removed after a bit
            """
            import warnings
            warnings.warn("Getting here is bad, find out how and fix it",
          DeprecationWarning, 2)
            if data[:3] == "/me":
                """
                This fixes the emote coloring to comply with what has been
                asked for by the user population, not to mention, what I
                committed to many moons ago. In doing so, Woody's scheme has
                been tossed out.  I'm sure Woody won't be happy but I'm
                invoking developer priveledge to satisfy user request, not to
                mention, this scheme actually makes more sense.  In Woody's
                scheme, a user could over-ride another users emote color. This
                doesn't make sense, rather, people dictate their OWN colors...
                which is as it should be in the first place and is as it has
                been with normal text.  In short, this makes sense and is
                consistent.
                """
                data = data.replace( "/me", "" )
                """
                Check to see if we find the closing '>' for the font within the
                first 22 values
                """
                index = data[:22].find(  ">" )
                if index == -1:
                    data = "** " + self.chat.colorize( self.chat.infocolor, display_name + data ) + " **"

                else:
                    """
                    This means that we found a valid font string, so we can
                    simply plug the name into the string between the start and
                    stop font delimiter
                    """
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

    @debugging
    def on_mplay_event(self, evt):
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
            settings = component.get('settings')
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

    @debugging
    def OnCloseWindow(self, event):
        dlg = wx.MessageDialog(self, "Quit OpenRPG?", "OpenRPG", wx.YES_NO)
        if dlg.ShowModal() == wx.ID_YES:
            dlg.Destroy()
            self.closed_confirmed()

    @debugging
    def closed_confirmed(self):
        self.activeplugins = component.get('plugins')
        self.aliaslib.OnMB_FileSave(None)

        #following lines added by mDuo13
        #########plugin_disabled()#########
        for plugin_fname in self.activeplugins.keys():
            plugin = self.activeplugins[plugin_fname]
            try: plugin.plugin_disabled()
            except Exception, e:
                    traceback.print_exc()
        #end mDuo13 added code
        self.saveLayout()
        try: settings.save()
        except Exception:
            logger.general("[WARNING] Error saving 'settings' component", True)

        try: self.map.pre_exit_cleanup()
        except Exception:
            logger.general("[WARNING] Map error pre_exit_cleanup()", True)

        try:
            save_tree = string.upper(settings.get_setting("SaveGameTreeOnExit"))
            if  (save_tree != "0") and (save_tree != "False") and (save_tree != "NO"):
                self.tree.save_tree(settings.get_setting("gametree"))
        except Exception:
            logger.general("[WARNING] Error saving gametree", True)

        if self.session.get_status() == orpg.networking.mplay_client.MPLAY_CONNECTED: self.kill_mplay_session()

        try:
            #Kill all the damn timers
            self.sound_player.timer.Stop()
            del self.sound_player.timer
        except Exception:
            logger.general("sound didn't die properly.", True)

        try:
            self.poll_timer.Stop()
            self.ping_timer.Stop()
            self.chat.parent.chat_timer.Stop()
            self.map.canvas.zoom_display_timer.Stop()
            self.map.canvas.image_timer.Stop()
            self.status.timer.Stop()
            del self.ping_timer; del self.poll_timer; del self.chat.parent.chat_timer
            del self.map.canvas.zoom_display_timer; del self.map.canvas.image_timer; del self.status.timer
        except Exception:
            logger.general("some timer didn't die properly.", True)

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
                logger.general("Killing Server process:", True)
                time.sleep(5)
                self.server_stop()
                self.server_pipe.close()
                self.std_out.close()
                self.server_thread.exit()
                dlg.Destroy()
                logger.general("Server killed:", True)
        except Exception:
            pass

########################################
## About Dialog class
########################################
class AboutORPG(wx.Frame):
    def __init__(self, parent):
        super(AboutORPG, self).__init__(parent, -1, "About 'Traipse' OpenRPG")
        icon = None
        icon = wx.Icon(dir_struct["icon"]+'d20.ico', wx.BITMAP_TYPE_ICO)
        self.SetIcon( icon )
        sizer = wx.GridBagSizer(hgap=1, vgap=1)
        height = 425; width = 350
        self.About = wx.TextCtrl(self, -1, size=wx.DefaultSize, style=wx.TE_MULTILINE | wx.TE_READONLY)
        img = wx.Image(dir_struct['icon']+'splash.gif', wx.BITMAP_TYPE_ANY).ConvertToBitmap()
        image = wx.StaticBitmap(self, -1, img, size=wx.DefaultSize)
        sizer.Add(image, (0,0), flag=wx.ALIGN_CENTER_HORIZONTAL|wx.ALL|wx.ADJUST_MINSIZE)
        sizer.Add(self.About, (1,0), flag=wx.EXPAND)
        self.SetSizer(sizer)
        self.SetAutoLayout(True)
        self.SetSize((width, height))
        sizer.AddGrowableCol(0)
        sizer.AddGrowableCol(1)
        sizer.AddGrowableRow(1)
        self.Bind(wx.EVT_CLOSE, self.Min) 
        self.Min(None)

        description = "OpenRPG is a Virtual Game Table that allows users to connect via a network and play table "
        description += "top games with friends.  'Traipse' is an OpenRPG distro that is easy to setup and provides superb "
        description += "functionality.  OpenRPG is originally designed by Chris Davis."

        license = "OpenRPG is free software; you can redistribute it and/or modify it "
        license += "under the terms of the GNU General Public License as published by the Free Software Foundation; "
        license += "either version 2 of the License, or (at your option) any later version.\n\n"
        license += "OpenRPG and Traipse 'OpenRPG' is distributed in the hope that it will be useful, but WITHOUT ANY "
        license += "WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. "
        license += "See the GNU General Public License for more details. You should have received a copy of "
        license += "the GNU General Public License along with Traipse 'OpenRPG'; if not, write to "
        license += "the Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA \n\n"
        license += "'Traipse' and the 'Traipse' Logo are trademarks of Mad Mathematics Laboratories."

        self.About.AppendText(description+'\n\n')
        self.About.AppendText(license+'\n\n')
        self.About.AppendText('OpenRPG Developers:\n')
        orpg_devs = ['Thomas Baleno', 'Andrew Bennett', 'Lex Berezhny', 'Ted Berg',
		'Bernhard Bergbauer', 'Chris Blocher', 'David Byron', 'Ben Collins-Sussman', 'Robin Cook', 'Greg Copeland',
		'Chris Davis', 'Michael Edwards', 'Andrew Ettinger', 'Todd Faris', 'Dj Gilcrease',
        'Christopher Hickman', 'Paul Hosking', 'Brian Manning', 'Scott Mackay', 'Jesse McConnell', 
		'Brian Osman', 'Rome Reginelli', 'Christopher Rouse', 'Dave Sanders', 'Tyler Starke', 'Mark Tarrabain']
        for dev in orpg_devs:
            self.About.AppendText(dev+'\n')

    def Min(self, evt):
        self.Hide()

########################################
## Application class
########################################
class orpgSplashScreen(wx.SplashScreen):
    @debugging
    def __init__(self, parent, bitmapfile, duration, callback):
        wx.SplashScreen.__init__(self, wx.Bitmap(bitmapfile), 
            wx.SPLASH_CENTRE_ON_SCREEN | wx.SPLASH_TIMEOUT, duration, None, -1)
        self.callback = callback
        self.closing = False
        self.Bind(wx.EVT_CLOSE, self.callback)

class orpgApp(wx.App):
    @debugging
    def OnInit(self):

        component.add('log', logger)
        component.add('xml', xml)
        component.add('settings', settings)
        component.add('validate', validate)
        component.add("tabbedWindows", [])

        logger._set_log_level = int(settings.get_setting('LoggingLevel'))
        logger._set_log_to_console(False)

        self.manifest = manifest.ManifestChanges()

        self.called = False
        wx.InitAllImageHandlers()
        self.splash = orpgSplashScreen(None, dir_struct["icon"] + 'splash13.jpg', 3000, self.AfterSplash)
        self.Bind(wx.EVT_KEY_DOWN, self.OnKeyPress)
        self._crust = None
        wx.Yield()
        return True

    @debugging
    def OnKeyPress(self, evt):
        #Event handler
        if evt.AltDown() and evt.CmdDown() and evt.KeyCode == ord('I'): self.ShowShell()
        else: evt.Skip()

    @debugging
    def ShowShell(self):
        #Show the PyCrust window.
        if not self._crust:
            self._crust = wx.py.crust.CrustFrame(self.GetTopWindow())
            self._crust.shell.interp.locals['app'] = self
        win = wx.FindWindowAtPointer()
        self._crust.shell.interp.locals['win'] = win
        self._crust.Show()

    @debugging
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

    @debugging
    def OnExit_CleanUp(self):
        logger.debug("Preforming cleanup\n")
        try: del os.environ["OPENRPG_BASE"]
        except: pass
        try: os.remove(os.environ["OPENRPG_BASE"] + os.sep + 'orpg' + os.sep + 'dirpath' + os.sep + 'approot.py')
        except: pass
        try: os.remove(os.environ["OPENRPG_BASE"] + os.sep + 'orpg' + os.sep + 'dirpath' + os.sep + 'approot.pyc')
        except: pass

    @debugging
    def OnExit(self):
        self.OnExit_CleanUp()
        #Exit
        logger.debug("Main Application Exit\n\n")
