# Copyright (C) 2000-2001 The OpenRPG Project
#
#     openrpg-dev@lists.sourceforge.net
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
# File: chatutils.py
# Author: Chris Davis
# Maintainer:
# Version:
#   $Id: chatwnd.py,v Traipse 'Ornery-Orc' prof.ebral Exp $
#
# Description: This file contains some of the basic definitions for the chat
# utilities in the orpg project.
#
# History
# 2002-01-20 HeroMan
#   + Added 4 dialog items on toolbar in support of Alias Library Functionallity
#   + Shrunk the text view button to an image
# 2005-04-25 Snowdog
#   + Added simple_html_repair() to post() to fix malformed html in the chat window
#   + Added strip_script_tags() to post() to remove crash point. See chat_util.py
# 2005-04-25 Snowdog
#   + Added simple_html_repair() to post() to fix malformed html in the chat window
#

__version__ = "$Id: chatwnd.py,v Traipse 'Ornery-Orc' prof.ebral Exp $"


##
## Module Loading
##
import os, time, re, sys, traceback, webbrowser, commands, chat_msg, chat_util

from orpg.orpg_version import VERSION, DISTRO, DIS_VER, BUILD
from orpg.orpg_windows import *
from orpg.player_list import WG_LIST
from orpg.dirpath import dir_struct
from string import *

import cStringIO # for reading inline imagedata as a stream
from HTMLParser import HTMLParser
from wx.lib.expando import EVT_ETC_LAYOUT_NEEDED 

import orpg.tools.rgbhex
import orpg.tools.inputValidator
from orpg.tools.validate import validate
from orpg.tools.orpg_settings import settings
import orpg.tools.predTextCtrl
from orpg.tools.orpg_log import logger, debug
from orpg.tools.InterParse import Parse
from orpg.orpgCore import component
from xml.etree.ElementTree import tostring

from orpg.networking.mplay_client import MPLAY_CONNECTED  
NEWCHAT = False
try:
    import wx.webview
    NEWCHAT = True
except: pass
NEWCHAT = False

# Global parser for stripping HTML tags:
# The 'tag stripping' is implicit, because this parser echoes every
# type of html data *except* the tags.
class HTMLStripper(HTMLParser):
    
    def __init__(self):
        self.accum = ""
        self.special_tags = ['hr', 'br', 'img']
    
    def handle_data(self, data):  
        self.accum += data
    
    def handle_entityref(self, name): 
        self.accum += "&" + name + ";"
    
    def handle_starttag(self, tag, attrs):
        if tag in self.special_tags:
            self.accum += '<' + tag
            for attrib in attrs: self.accum += ' ' + attrib[0] + '="' + attrib[1] + '"'
            self.accum += '>'
    
    def handle_charref(self, name):
        self.accum += "&#" + name + ";"
htmlstripper = HTMLStripper()


def strip_html(string):
    "Return string tripped of html tags."
    htmlstripper.reset()
    htmlstripper.accum = ""
    htmlstripper.feed(string)
    htmlstripper.close()
    return htmlstripper.accum


def log( settings, c, text ):
    filename = settings.get_setting('GameLogPrefix')
    if filename > '' and filename[0] != commands.ANTI_LOG_CHAR:
        filename = filename + time.strftime( '-%Y-%m-%d.html', time.localtime( time.time() ) )
        timestamp = time.ctime(time.time())
        header = '[%s] : ' % ( timestamp );
        if settings.get_setting('TimeStampGameLog') != '1': header = ''
        try:
            f = open( dir_struct["user"] + filename, 'a' )
            f.write( '<div class="'+c+'">%s%s</div>\n' % ( header, text ) )
            f.close()
        except Exception, e:
            print "could not open " + dir_struct["user"] + filename + ", ignoring..."
            print 'Error given', e
            pass

# This class displayes the chat information in html?
#
# Defines:
#   __init__(self, parent, id)
#   OnLinkClicked(self, linkinfo)
#   CalculateAllFonts(self, defaultsize)
#   SetDefaultFontAndSize(self, fontname)
#
class chat_html_window(wx.html.HtmlWindow):
    """ a wxHTMLwindow that will load links  """

    def __init__(self, parent, id):
        wx.html.HtmlWindow.__init__(self, parent, id, 
                                    style=wx.SUNKEN_BORDER|wx.html.HW_SCROLLBAR_AUTO|wx.NO_FULL_REPAINT_ON_RESIZE)
        self.parent = parent
        self.build_menu()
        self.Bind(wx.EVT_LEFT_UP, self.LeftUp)
        self.Bind(wx.EVT_RIGHT_DOWN, self.onPopup)
        if "gtk2" in wx.PlatformInfo: self.SetStandardFonts()

    def onPopup(self, evt):
        self.PopupMenu(self.menu)

    def LeftUp(self, event):
        event.Skip()
        wx.CallAfter(self.parent.set_chat_text_focus, None)

    def build_menu(self):
        self.menu = wx.Menu()
        item = wx.MenuItem(self.menu, wx.ID_ANY, "Copy", "Copy")
        self.Bind(wx.EVT_MENU, self.OnM_EditCopy, item)
        self.menu.AppendItem(item)

    def OnM_EditCopy(self, evt):
        wx.TheClipboard.UsePrimarySelection(False)
        wx.TheClipboard.Open()
        wx.TheClipboard.SetData(wx.TextDataObject(self.SelectionToText()))
        wx.TheClipboard.Close()

    def scroll_down(self):
        maxrange = self.GetScrollRange(wx.VERTICAL)
        pagesize = self.GetScrollPageSize(wx.VERTICAL)
        self.Scroll(-1, maxrange-pagesize)

    def mouse_wheel(self, event):
        amt = event.GetWheelRotation()
        units = amt/(-(event.GetWheelDelta()))
        self.ScrollLines(units*3)

    
    def Header(self):
        return '<html><body bgcolor="' + self.parent.bgcolor + '" text="' + self.parent.textcolor + '">'

    
    def StripHeader(self):
        return self.GetPageSource().replace(self.Header(), '')

    
    def GetPageSource(self):
        return self.GetParser().GetSource()
    
    def OnLinkClicked(self, linkinfo):
        href = linkinfo.GetHref()
        wb = webbrowser.get()
        wb.open(href)

    def CalculateAllFonts(self, defaultsize):
        return [int(defaultsize * 0.4),
                int(defaultsize * 0.7),
                int(defaultsize),
                int(defaultsize * 1.3),
                int(defaultsize * 1.7),
                int(defaultsize * 2),
                int(defaultsize * 2.5)]

    def SetDefaultFontAndSize(self, fontname, fontsize):
        """Set 'fontname' to the default chat font.
           Returns current font settings in a (fontname, fontsize) tuple."""
        self.SetFonts(fontname, "", self.CalculateAllFonts(int(fontsize)))
        return (self.GetFont().GetFaceName(), self.GetFont().GetPointSize())

# class chat_html_window - end
if NEWCHAT:
    class ChatHtmlWindow(wx.webview.WebView):
        
        def __init__(self, parent, id):
            wx.webview.WebView.__init__(self, parent, id)
            self.parent = parent
            self.__font = wx.Font(10, wx.FONTFAMILY_ROMAN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, faceName='Ariel')
            self.build_menu()
            self.Bind(wx.EVT_LEFT_UP, self.LeftUp)
            self.Bind(wx.EVT_RIGHT_DOWN, self.onPopup)
            self.Bind(wx.webview.EVT_WEBVIEW_BEFORE_LOAD, self.OnLinkClicked)

        def SetPage(self, htmlstring):
            self.SetPageSource(htmlstring)

        def AppendToPage(self, htmlstring):
            self.SetPageSource(self.GetPageSource() + htmlstring)

        def GetFont(self):
            return self.__font

        def CalculateAllFonts(self, defaultsize):
            return

        def SetDefaultFontAndSize(self, fontname, fontsize):
            self.__font = wx.Font(int(fontsize), 
                            wx.FONTFAMILY_ROMAN, wx.FONTSTYLE_NORMAL, 
                            wx.FONTWEIGHT_NORMAL, faceName=fontname)
            try: self.SetPageSource(self.Header() + self.StripHeader())
            except Exception, e: print e
            return (self.GetFont().GetFaceName(), self.GetFont().GetPointSize())

        #Events
        def OnLinkClicked(self, linkinfo):
            href = linkinfo.GetHref()
            wb = webbrowser.get()
            wb.open(href)

        def onPopup(self, evt):
            self.PopupMenu(self.menu)

        def LeftUp(self, event):
            event.Skip()
            wx.CallAfter(self.parent.set_chat_text_focus, None)

        def OnM_EditCopy(self, evt):
            wx.TheClipboard.UsePrimarySelection(False)
            wx.TheClipboard.Open()
            wx.TheClipboard.SetData(wx.TextDataObject(self.SelectionToText()))
            wx.TheClipboard.Close()

        #Cutom Methods
        def Header(self):
            return "<html><head><style>body {font-size: " + str(self.GetFont().GetPointSize()) + "px;font-family: " + self.GetFont().GetFaceName() + ";color: " + self.parent.textcolor + ";background-color: " + self.parent.bgcolor + ";margin: 0;padding: 0 0;height: 100%;}</style></head><body>"

        def StripHeader(self):
            tmp = self.GetPageSource().split('<BODY>')
            if tmp[-1].find('<body>') > -1: tmp = tmp[-1].split('<body>')
            return tmp[-1]

        def build_menu(self):
            self.menu = wx.Menu()
            item = wx.MenuItem(self.menu, wx.ID_ANY, "Copy", "Copy")
            self.Bind(wx.EVT_MENU, self.OnM_EditCopy, item)
            self.menu.AppendItem(item)

        def scroll_down(self):
            maxrange = self.GetScrollRange(wx.VERTICAL)
            pagesize = self.GetScrollPageSize(wx.VERTICAL)
            self.Scroll(-1, maxrange-pagesize)

        def mouse_wheel(self, event):
            amt = event.GetWheelRotation()
            units = amt/(-(event.GetWheelDelta()))
            self.ScrollLines(units*3)
    chat_html_window = ChatHtmlWindow

#########################
#chat frame window
#########################
# These are kinda global...and static..and should be located somewhere else
# then the middle of a file between two classes.

###################
# Tab Types
###################
MAIN_TAB = wx.NewId()
WHISPER_TAB = wx.NewId()
GROUP_TAB = wx.NewId()
NULL_TAB = wx.NewId()

# This class defines the tabbed 'notebook' that holds multiple chatpanels.
# It's the widget attached to the main application frame.
#
# Inherits:  wxNotebook
#
# Defines:
#   create_private_tab(self, playerid)
#   get_tab_index(self, chatpanel)
#   destroy_private_tab(self, chatpanel)
#   OnPageChanged(self, event)
#   set_default_font(self, font, fontsize)

class chat_notebook(orpgTabberWnd):
    
    def __init__(self, parent, size):
        orpgTabberWnd.__init__(self, parent, True, size=size, 
                style=FNB.FNB_DROPDOWN_TABS_LIST|FNB.FNB_NO_NAV_BUTTONS|FNB.FNB_MOUSE_MIDDLE_CLOSES_TABS)
        self.settings = component.get("settings")
        self.whisper_tabs = []
        self.group_tabs = []
        self.null_tabs = []
        self.il = wx.ImageList(16, 16)
        bmp = wx.Bitmap(dir_struct["icon"]+'player.gif')
        self.il.Add(bmp)
        bmp = wx.Bitmap(dir_struct["icon"]+'clear.gif')
        self.il.Add(bmp)
        self.SetImageList(self.il)
        # Create "main" chatpanel tab, undeletable, connected to 'public' room.
        self.MainChatPanel = chat_panel(self, -1, MAIN_TAB, 'all')
        self.AddPage(self.MainChatPanel, "Main Room")
        self.SetPageImage(0, 1)
        self.chat_timer = wx.Timer(self, wx.NewId())
        self.Bind(wx.EVT_TIMER, self.MainChatPanel.typingTimerFunc)
        self.chat_timer.Start(1000)
        # Hook up event handler for flipping tabs
        self.Bind(FNB.EVT_FLATNOTEBOOK_PAGE_CHANGED, self.onPageChanged)
        self.Bind(FNB.EVT_FLATNOTEBOOK_PAGE_CHANGING, self.onPageChanging)
        self.Bind(FNB.EVT_FLATNOTEBOOK_PAGE_CLOSING, self.onCloseTab)
        # html font/fontsize is global to all the notebook tabs.
        self.font, self.fontsize =  self.MainChatPanel.chatwnd.SetDefaultFontAndSize(self.settings.get_setting('defaultfont'), self.settings.get_setting('defaultfontsize'))
        self.GMChatPanel = None
        if self.settings.get_setting("GMWhisperTab") == '1':
            self.create_gm_tab()
        self.SetSelection(0)

    def get_tab_index(self, chatpanel):
        "Return the index of a chatpanel in the wxNotebook."
        for i in xrange(self.GetPageCount()):
            if (self.GetPage(i) == chatpanel):
                return i

    def create_gm_tab(self):
        if self.GMChatPanel == None:
            self.GMChatPanel = chat_panel(self, -1, MAIN_TAB, 'gm')
            self.AddPage(self.GMChatPanel, "GM", False)
            self.SetPageImage(self.GetPageCount()-1, 1)
            self.GMChatPanel.chatwnd.SetDefaultFontAndSize(self.font, self.fontsize)

    def create_whisper_tab(self, playerid):
        "Add a new chatpanel directly connected to integer 'playerid' via whispering."
        private_tab = chat_panel(self, -1, WHISPER_TAB, playerid)
        playername = strip_html(self.MainChatPanel.session.get_player_by_player_id(playerid)[0])
        self.AddPage(private_tab, playername, False)
        private_tab.chatwnd.SetDefaultFontAndSize(self.font, self.fontsize)
        self.whisper_tabs.append(private_tab)
        self.newMsg(self.GetPageCount()-1)
        self.AliasLib = component.get('alias')
        wx.CallAfter(self.AliasLib.RefreshAliases)
        return private_tab

    def create_group_tab(self, group_name):
        "Add a new chatpanel directly connected to integer 'playerid' via whispering."
        private_tab = chat_panel(self, -1, GROUP_TAB, group_name)
        self.AddPage(private_tab, group_name, False)
        private_tab.chatwnd.SetDefaultFontAndSize(self.font, self.fontsize)
        self.group_tabs.append(private_tab)
        self.newMsg(self.GetPageCount()-1)
        self.AliasLib = component.get('alias')
        wx.CallAfter(self.AliasLib.RefreshAliases)
        return private_tab

    def create_null_tab(self, tab_name):
        "Add a new chatpanel directly connected to integer 'playerid' via whispering."
        private_tab = chat_panel(self, -1, NULL_TAB, tab_name)
        self.AddPage(private_tab, tab_name, False)
        private_tab.chatwnd.SetDefaultFontAndSize(self.font, self.fontsize)
        self.null_tabs.append(private_tab)
        self.newMsg(self.GetPageCount()-1)
        self.AliasLib = component.get('alias')
        wx.CallAfter(self.AliasLib.RefreshAliases)
        return private_tab

    def onCloseTab(self, evt):
        try: tabid = evt.GetSelection()
        except: tabid = self.GetSelection()
        if self.GetPageText(tabid) == 'Main Room':
            #send no close error to chat
            evt.Veto()
            return
        if self.GetPageText(tabid) == 'GM':
            msg = "Are You Sure You Want To Close This Page?"
            dlg = wx.MessageDialog(self, msg, "NotebookCtrl Question",
                                   wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION)
            if wx.Platform != '__WXMAC__':
                dlg.SetFont(wx.Font(8, wx.NORMAL, wx.NORMAL, wx.NORMAL, False))

            if dlg.ShowModal() in [wx.ID_NO]:
                dlg.Destroy()
                evt.Veto()
                return
            dlg.Destroy()
            self.GMChatPanel = None
            self.settings.set_setting("GMWhisperTab", "0")
        panel = self.GetPage(tabid)
        if panel in self.whisper_tabs: self.whisper_tabs.remove(panel)
        elif panel in self.group_tabs: self.group_tabs.remove(panel)
        elif panel in self.null_tabs: self.null_tabs.remove(panel)

    def newMsg(self, tabid):
        if tabid != self.GetSelection(): self.SetPageImage(tabid, 0)

    def onPageChanging(self, event):
        """When private chattabs are selected, set the bitmap back to 'normal'."""
        event.Skip()

    def onPageChanged(self, event):
        """When private chattabs are selected, set the bitmap back to 'normal'."""
        selected_idx = event.GetSelection()
        self.SetPageImage(selected_idx, 1)
        page = self.GetPage(selected_idx)
        event.Skip()

"""
 This class defines and builds the Chat Frame for OpenRPG

 Inherits: wxPanel

 Defines:
   __init__((self, parent, id, openrpg, sendtarget)
   build_ctrls(self)
   on_buffer_size(self,evt)
   set_colors(self)
   set_buffersize(self)
   set_chat_text(self,txt)
   OnChar(self,event)
   on_chat_save(self,evt)
   on_text_color(self,event)
   colorize(self, color, text)
   on_text_format(self,event)
   OnSize(self,event)
   scroll_down(self)
   InfoPost(self,s)
   Post(self,s="",send=False,myself=False)
   ParsePost(self,s,send=False,myself=False)
   ParseDice(self,s)
   ParseNodes(self,s)
   get_sha_checksum(self)
   get_color(self)

"""

class chat_panel(wx.Panel):

    """
    This is the initialization subroutine
    
    !self : instance of self
    !parent : parent that defines the chatframe
    !id :
    !openrpg :
    !sendtarget:  who gets outbound messages: either 'all' or a playerid
    """

    
    def __init__(self, parent, id, tab_type, sendtarget):
        wx.Panel.__init__(self, parent, id)
        logger._set_log_to_console(False)
        self.session = component.get('session')
        self.settings = component.get('settings')
        self.activeplugins = component.get('plugins')
        self.parent = parent
        # who receives outbound messages, either "all" or "playerid" string
        self.sendtarget = sendtarget
        self.type = tab_type
        self.r_h = orpg.tools.rgbhex.RGBHex()
        self.h = 0
        self.set_colors()
        self.version = VERSION
        self.histidx = -1
        self.temptext = ""
        self.history = []
        self.storedata = []
        #self.lasthistevt = None
        self.parsed=0
        #chat commands
        self.lockscroll = False      # set the default to scrolling on.
        self.chat_cmds = commands.chat_commands(self)
        self.html_strip = strip_html
        self.f_keys = {wx.WXK_F1: 'event.GetKeyCode() == wx.WXK_F1', wx.WXK_F2: 'event.GetKeyCode() == wx.WXK_F2', 
                    wx.WXK_F3: 'event.GetKeyCode() == wx.WXK_F3', wx.WXK_F4: 'event.GetKeyCode() == wx.WXK_F4', 
                    wx.WXK_F5: 'event.GetKeyCode() == wx.WXK_F5', wx.WXK_F6: 'event.GetKeyCode() == wx.WXK_F6', 
                    wx.WXK_F7: 'event.GetKeyCode() == wx.WXK_F7', wx.WXK_F8: 'event.GetKeyCode() == wx.WXK_F8', 
                    wx.WXK_F9: 'event.GetKeyCode() == wx.WXK_F9', wx.WXK_F10: 'event.GetKeyCode() == wx.WXK_F10', 
                    wx.WXK_F11: 'event.GetKeyCode() == wx.WXK_F11', wx.WXK_F12: 'event.GetKeyCode() == wx.WXK_F12'}
        #Alias Lib stuff
        self.defaultAliasName = 'Use Real Name'
        self.defaultFilterName = 'No Filter'
        self.advancedFilter = False
        self.lastSend = 0         #  this is used to help implement the player typing indicator
        self.lastPress = 0        #  this is used to help implement the player typing indicator
        self.Bind(wx.EVT_SIZE, self.OnSize)
        self.Bind(EVT_ETC_LAYOUT_NEEDED, self.OnSize) 
        self.build_ctrls()
        StartupFont = self.settings.get_setting("defaultfont")
        StartupFontSize = self.settings.get_setting("defaultfontsize")
        if(StartupFont != "") and (StartupFontSize != ""):
            try: self.set_default_font(StartupFont, int(StartupFontSize))
            except: pass
        self.font = self.chatwnd.GetFont().GetFaceName()
        self.fontsize = self.chatwnd.GetFont().GetPointSize()
        self.scroll_down()

    def set_default_font(self, fontname=None, fontsize=None):
        """Set all chatpanels to new default fontname/fontsize. 
        Returns current font settings in a (fontname, fontsize) tuple."""
        if (fontname is not None): newfont = fontname
        else: newfont = self.font
        if (fontsize is not None): newfontsize = int(fontsize)
        else: newfontsize = int(self.fontsize)
        self.chatwnd.SetDefaultFontAndSize(newfont, newfontsize)
        self.InfoPost("Font is now " + newfont + " point size " + `newfontsize`)
        self.font = newfont
        self.fontsize = newfontsize
        return (self.font, self.fontsize)

    def build_menu(self):
        top_frame = component.get('frame')
        menu = wx.Menu()
        item = wx.MenuItem(menu, wx.ID_ANY, "&Background color", "Background color")
        top_frame.Bind(wx.EVT_MENU, self.OnMB_BackgroundColor, item)
        menu.AppendItem(item)
        item = wx.MenuItem(menu, wx.ID_ANY, "&Text color", "Text color")
        top_frame.Bind(wx.EVT_MENU, self.OnMB_TextColor, item)
        menu.AppendItem(item)
        menu.AppendSeparator()
        item = wx.MenuItem(menu, wx.ID_ANY, "&Chat Focus\tCtrl-H", "Chat Focus")
        self.setChatFocusMenu = item
        top_frame.Bind(wx.EVT_MENU, self.set_chat_text_focus, item)
        menu.AppendItem(item)
        menu.AppendSeparator()
        item = wx.MenuItem(menu, wx.ID_ANY, "Toggle &Scroll Lock", "Toggle Scroll Lock")
        top_frame.Bind(wx.EVT_MENU, self.lock_scroll, item)
        menu.AppendItem(item)
        item = wx.MenuItem(menu, wx.ID_ANY, "Save Chat &Log", "Save Chat Log")
        top_frame.Bind(wx.EVT_MENU, self.on_chat_save, item)
        menu.AppendItem(item)
        item = wx.MenuItem(menu, wx.ID_ANY, "Text &View", "Text View")
        top_frame.Bind(wx.EVT_MENU, self.pop_textpop, item)
        menu.AppendItem(item)
        item = wx.MenuItem(menu, wx.ID_ANY, "Forward Tab\tCtrl+Tab", "Swap Tabs")
        top_frame.Bind(wx.EVT_MENU, self.forward_tabs, item)
        menu.AppendItem(item)
        item = wx.MenuItem(menu, wx.ID_ANY, "Forward Tab\tCtrl+Shift+Tab", "Swap Tabs")
        top_frame.Bind(wx.EVT_MENU, self.back_tabs, item)
        menu.AppendItem(item)
        menu.AppendSeparator()
        settingmenu = wx.Menu()
        wndmenu = wx.Menu()
        tabmenu = wx.Menu()
        toolmenu = wx.Menu()
        item = wx.MenuItem(wndmenu, wx.ID_ANY, "Show Images", "Show Images", wx.ITEM_CHECK)
        top_frame.Bind(wx.EVT_MENU, self.OnMB_ShowImages, item)

        wndmenu.AppendItem(item)
        if self.settings.get_setting("Show_Images_In_Chat") == '1': item.Check(True)
        item = wx.MenuItem(wndmenu, wx.ID_ANY, "Strip HTML", "Strip HTML", wx.ITEM_CHECK)
        top_frame.Bind(wx.EVT_MENU, self.OnMB_StripHTML, item)
        wndmenu.AppendItem(item)
        if self.settings.get_setting("striphtml") == '1': item.Check(True)
        item = wx.MenuItem(wndmenu, wx.ID_ANY, "Chat Time Index", "Chat Time Index", wx.ITEM_CHECK)
        top_frame.Bind(wx.EVT_MENU, self.OnMB_ChatTimeIndex, item)
        wndmenu.AppendItem(item)
        if self.settings.get_setting("Chat_Time_Indexing") == '1': item.Check(True)
        item = wx.MenuItem(wndmenu, wx.ID_ANY, "Chat Auto Complete", "Chat Auto Complete", wx.ITEM_CHECK)
        top_frame.Bind(wx.EVT_MENU, self.OnMB_ChatAutoComplete, item)
        wndmenu.AppendItem(item)
        if self.settings.get_setting("SuppressChatAutoComplete") == '0': item.Check(True)
        item = wx.MenuItem(wndmenu, wx.ID_ANY, "Show ID in Chat", "Show ID in Chat", wx.ITEM_CHECK)
        top_frame.Bind(wx.EVT_MENU, self.OnMB_ShowIDinChat, item)
        wndmenu.AppendItem(item)
        if self.settings.get_setting("ShowIDInChat") == '1': item.Check(True)
        item = wx.MenuItem(wndmenu, wx.ID_ANY, "Log Time Index", "Log Time Index", wx.ITEM_CHECK)
        top_frame.Bind(wx.EVT_MENU, self.OnMB_LogTimeIndex, item)
        wndmenu.AppendItem(item)
        if self.settings.get_setting("TimeStampGameLog") == '1': item.Check(True)
        settingmenu.AppendMenu(wx.ID_ANY, 'Chat Window', wndmenu )
        item = wx.MenuItem(tabmenu, wx.ID_ANY, "Tabbed Whispers", "Tabbed Whispers", wx.ITEM_CHECK)
        top_frame.Bind(wx.EVT_MENU, self.OnMB_TabbedWhispers, item)
        tabmenu.AppendItem(item)
        if self.settings.get_setting("tabbedwhispers") == '1': item.Check(True)
        item = wx.MenuItem(tabmenu, wx.ID_ANY, "GM Tab", "GM Tab", wx.ITEM_CHECK)
        top_frame.Bind(wx.EVT_MENU, self.OnMB_GMTab, item)
        tabmenu.AppendItem(item)
        if self.settings.get_setting("GMWhisperTab") == '1':item.Check(True)
        item = wx.MenuItem(tabmenu, wx.ID_ANY, "Group Whisper Tabs", "Group Whisper Tabs", wx.ITEM_CHECK)
        top_frame.Bind(wx.EVT_MENU, self.OnMB_GroupWhisperTabs, item)
        tabmenu.AppendItem(item)
        if self.settings.get_setting("GroupWhisperTab") == '1': item.Check(True)
        settingmenu.AppendMenu(wx.ID_ANY, 'Chat Tabs', tabmenu)
        item = wx.MenuItem(toolmenu, wx.ID_ANY, "Dice Bar", "Dice Bar", wx.ITEM_CHECK)
        top_frame.Bind(wx.EVT_MENU, self.OnMB_DiceBar, item)
        toolmenu.AppendItem(item)
        if self.settings.get_setting("DiceButtons_On") == '1': item.Check(True)
        item = wx.MenuItem(toolmenu, wx.ID_ANY, "Format Buttons", "Format Buttons", wx.ITEM_CHECK)
        top_frame.Bind(wx.EVT_MENU, self.OnMB_FormatButtons, item)
        toolmenu.AppendItem(item)
        if self.settings.get_setting("FormattingButtons_On") == '1': item.Check(True)
        item = wx.MenuItem(toolmenu, wx.ID_ANY, "Alias Tool", "Alias Tool", wx.ITEM_CHECK)
        top_frame.Bind(wx.EVT_MENU, self.OnMB_AliasTool, item)
        toolmenu.AppendItem(item)
        if self.settings.get_setting("AliasTool_On") == '1': item.Check(True)
        settingmenu.AppendMenu(wx.ID_ANY, 'Chat Tool Bars', toolmenu)
        menu.AppendMenu(wx.ID_ANY, 'Chat Settings', settingmenu)
        top_frame.mainmenu.Insert(2, menu, '&Chat')

    ## Settings Menu Events
    def OnMB_ShowImages(self, event):
        if event.IsChecked(): self.settings.set_setting("Show_Images_In_Chat", '1')
        else: self.settings.set_setting("Show_Images_In_Chat", '0')

    def OnMB_StripHTML(self, event):
        if event.IsChecked(): self.settings.set_setting("striphtml", '1')
        else: self.settings.set_setting("striphtml", '0')

    def OnMB_ChatTimeIndex(self, event):
        if event.IsChecked(): self.settings.set_setting("Chat_Time_Indexing", '1')
        else: self.settings.set_setting("Chat_Time_Indexing", '0')

    def OnMB_ChatAutoComplete(self, event):
        if event.IsChecked(): self.settings.set_setting("SuppressChatAutoComplete", '0')
        else: self.settings.set_setting("SuppressChatAutoComplete", '1')

    def OnMB_ShowIDinChat(self, event):
        if event.IsChecked(): self.settings.set_setting("ShowIDInChat", '1')
        else: self.settings.set_setting("ShowIDInChat", '0')

    def OnMB_LogTimeIndex(self, event):
        if event.IsChecked(): self.settings.set_setting("TimeStampGameLog", '1')
        else: self.settings.set_setting("TimeStampGameLog", '0')

    def OnMB_TabbedWhispers(self, event):
        if event.IsChecked(): self.settings.set_setting("tabbedwhispers", '1')
        else: self.settings.set_setting("tabbedwhispers", '0')

    def OnMB_GMTab(self, event):
        if event.IsChecked():
            self.settings.set_setting("GMWhisperTab", '1')
            self.parent.create_gm_tab()
        else: self.settings.set_setting("GMWhisperTab", '0')

    def OnMB_GroupWhisperTabs(self, event):
        if event.IsChecked(): self.settings.set_setting("GroupWhisperTab", '1')
        else: self.settings.set_setting("GroupWhisperTab", '0')

    def OnMB_DiceBar(self, event):
        act = '0'
        if event.IsChecked():
            self.settings.set_setting("DiceButtons_On", '1')
            act = '1'
        else: self.settings.set_setting("DiceButtons_On", '0')
        self.toggle_dice(act)
        try: self.parent.GMChatPanel.toggle_dice(act)
        except: pass
        for panel in self.parent.whisper_tabs: panel.toggle_dice(act)
        for panel in self.parent.group_tabs: panel.toggle_dice(act)
        for panel in self.parent.null_tabs: panel.toggle_dice(act)

    def OnMB_FormatButtons(self, event):
        act = '0'
        if event.IsChecked():
            self.settings.set_setting("FormattingButtons_On", '1')
            act = '1'
        else:
            self.settings.set_setting("FormattingButtons_On", '0')
        self.toggle_formating(act)
        try: self.parent.GMChatPanel.toggle_formating(act)
        except: pass
        for panel in self.parent.whisper_tabs: panel.toggle_formating(act)
        for panel in self.parent.group_tabs: panel.toggle_formating(act)
        for panel in self.parent.null_tabs: panel.toggle_formating(act)

    def OnMB_AliasTool(self, event):
        act = '0'
        if event.IsChecked():
            self.settings.set_setting("AliasTool_On", '1')
            act = '1'
        else: self.settings.set_setting("AliasTool_On", '0')
        self.toggle_alias(act)
        try: self.parent.GMChatPanel.toggle_alias(act)
        except: pass
        for panel in self.parent.whisper_tabs: panel.toggle_alias(act)
        for panel in self.parent.group_tabs: panel.toggle_alias(act)
        for panel in self.parent.null_tabs:panel.toggle_alias(act)

    def OnMB_BackgroundColor(self, event):
        top_frame = component.get('frame')
        hexcolor = self.get_color()
        if hexcolor != None:
            self.bgcolor = hexcolor
            self.settings.set_setting('bgcolor', hexcolor)
            self.chatwnd.SetPage(self.ResetPage())
            if self.settings.get_setting('ColorTree') == '1':
                top_frame.tree.SetBackgroundColour(self.settings.get_setting('bgcolor'))
                top_frame.tree.Refresh()
                top_frame.players.SetBackgroundColour(self.settings.get_setting('bgcolor'))
                top_frame.players.Refresh()
            else:
                top_frame.tree.SetBackgroundColour('white')
                top_frame.tree.SetForegroundColour('black')
                top_frame.tree.Refresh()
                top_frame.players.SetBackgroundColour('white')
                top_frame.players.SetForegroundColour('black')
                top_frame.players.Refresh()
            self.chatwnd.scroll_down()

    
    def OnMB_TextColor(self, event):
        top_frame = component.get('frame')
        hexcolor = self.get_color()
        if hexcolor != None:
            self.textcolor = hexcolor
            self.settings.set_setting('textcolor', hexcolor)
            self.chatwnd.SetPage(self.ResetPage())
            if self.settings.get_setting('ColorTree') == '1':
                top_frame.tree.SetForegroundColour(self.settings.get_setting('textcolor'))
                top_frame.tree.Refresh()
                top_frame.players.SetForegroundColour(self.settings.get_setting('textcolor'))
                top_frame.players.Refresh()
            else:
                top_frame.tree.SetBackgroundColour('white')
                top_frame.tree.SetForegroundColour('black')
                top_frame.tree.Refresh()
                top_frame.players.SetBackgroundColour('white')
                top_frame.players.SetForegroundColour('black')
                top_frame.players.Refresh()
            self.chatwnd.scroll_down()

    
    def get_hot_keys(self):
        # dummy menus for hotkeys
        self.build_menu()
        entries = []
        entries.append((wx.ACCEL_CTRL, ord('H'), self.setChatFocusMenu.GetId()))
        return entries

    
    def forward_tabs(self, evt):
        self.parent.AdvanceSelection()

    def back_tabs(self, evt):
        self.parent.AdvanceSelection(False)

    def build_ctrls(self):
        self.chatwnd = chat_html_window(self,-1)
        self.set_colors()
        wx.CallAfter(self.chatwnd.SetPage, self.chatwnd.Header())
        welcome = "<b>Welcome to <a href='http://www.knowledgearcana.com//content/view/199/128/'>"
        welcome += DISTRO +'</a> '+ DIS_VER +' {'+BUILD+'},'
        welcome += ' built on OpenRPG '+ VERSION +'</b>'
        if (self.sendtarget == "all"):
            wx.CallAfter(self.Post, self.colorize(self.syscolor, welcome))
        self.chattxt = orpg.tools.predTextCtrl.predTextCtrl(self, -1, "", 
                        style=wx.TE_PROCESS_ENTER |wx.TE_PROCESS_TAB|wx.TE_LINEWRAP, 
                        keyHook = self.myKeyHook, validator=None )
        self.build_bar()
        self.basesizer = wx.BoxSizer(wx.VERTICAL)
        self.basesizer.Add( self.chatwnd, 1, wx.EXPAND )
        self.basesizer.Add( self.toolbar_sizer, 0, wx.EXPAND )
        self.basesizer.Add( self.chattxt, 0, wx.EXPAND )
        self.SetSizer(self.basesizer)
        self.SetAutoLayout(True)
        self.Fit()
        #events
        self.Bind(wx.EVT_BUTTON, self.on_text_format, self.boldButton)
        self.Bind(wx.EVT_BUTTON, self.on_text_format, self.italicButton)
        self.Bind(wx.EVT_BUTTON, self.on_text_format, self.underlineButton)
        self.Bind(wx.EVT_BUTTON, self.on_text_color, self.color_button)
        self.Bind(wx.EVT_BUTTON, self.on_chat_save, self.saveButton)
        self.Bind(wx.EVT_BUTTON, self.onDieRoll, self.d4Button)
        self.Bind(wx.EVT_BUTTON, self.onDieRoll, self.d6Button)
        self.Bind(wx.EVT_BUTTON, self.onDieRoll, self.d8Button)
        self.Bind(wx.EVT_BUTTON, self.onDieRoll, self.d10Button)
        self.Bind(wx.EVT_BUTTON, self.onDieRoll, self.d12Button)
        self.Bind(wx.EVT_BUTTON, self.onDieRoll, self.d20Button)
        self.Bind(wx.EVT_BUTTON, self.onDieRoll, self.d100Button)
        self.dieIDs = {}
        self.dieIDs[self.d4Button.GetId()] = 'd4'
        self.dieIDs[self.d6Button.GetId()] = 'd6'
        self.dieIDs[self.d8Button.GetId()] = 'd8'
        self.dieIDs[self.d10Button.GetId()] = 'd10'
        self.dieIDs[self.d12Button.GetId()] = 'd12'
        self.dieIDs[self.d20Button.GetId()] = 'd20'
        self.dieIDs[self.d100Button.GetId()] = 'd100'
        self.Bind(wx.EVT_BUTTON, self.pop_textpop, self.textpop_lock)
        self.Bind(wx.EVT_BUTTON, self.lock_scroll, self.scroll_lock)
        self.chattxt.Bind(wx.EVT_MOUSEWHEEL, self.chatwnd.mouse_wheel)
        self.chattxt.Bind(wx.EVT_CHAR, self.chattxt.OnChar)
        self.chattxt.Bind(wx.EVT_KEY_DOWN, self.on_chat_key_down)
        self.chattxt.Bind(wx.EVT_TEXT_COPY, self.chatwnd.OnM_EditCopy)

    def build_bar(self):
        self.toolbar_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.scroll_lock = None
        self.numDieText = None
        self.dieModText = None
        if self.settings.get_setting('Toolbar_On') == "1":
            self.build_alias()
            self.build_dice()
            self.build_scroll()
            self.build_text()
            self.toolbar_sizer.Add(self.textpop_lock, 0, wx.EXPAND)
            self.toolbar_sizer.Add(self.scroll_lock, 0, wx.EXPAND)
            self.build_formating()
            self.build_colorbutton()

    def build_scroll(self):
        self.scroll_lock = wx.Button( self, wx.ID_ANY, "Scroll ON",size= wx.Size(80,25))

    def build_alias(self):
        self.aliasSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.aliasList = wx.Choice(self, wx.ID_ANY, size=(100, 25), choices=[self.defaultAliasName])
        self.aliasButton = createMaskedButton( self, dir_struct["icon"] + 'player.gif', 
                                            'Refresh list of aliases from Game Tree', 
                                            wx.ID_ANY, '#bdbdbd' )
        self.aliasList.SetSelection(0)
        self.filterList = wx.Choice(self, wx.ID_ANY, size=(100, 25), choices=[self.defaultFilterName])
        self.filterButton = createMaskedButton( self, dir_struct["icon"] + 'add_filter.gif', 
                                             'Refresh list of filters from Game Tree', 
                                             wx.ID_ANY, '#bdbdbd' )
        self.filterList.SetSelection(0)

        self.aliasSizer.Add( self.aliasButton, 0, wx.EXPAND )
        self.aliasSizer.Add( self.aliasList,0,wx.EXPAND)
        self.aliasSizer.Add( self.filterButton, 0, wx.EXPAND )
        self.aliasSizer.Add( self.filterList,0,wx.EXPAND)

        self.toolbar_sizer.Add(self.aliasSizer, 0, wx.EXPAND)

        if self.settings.get_setting('AliasTool_On') == '0': self.toggle_alias('0')
        else: self.toggle_alias('1')
    
    def toggle_alias(self, act):
        if act == '0': self.toolbar_sizer.Show(self.aliasSizer, False)
        else: self.toolbar_sizer.Show(self.aliasSizer, True)
        self.toolbar_sizer.Layout()
    
    def build_text(self):
        self.textpop_lock = createMaskedButton(self, dir_struct["icon"]+'note.gif', 'Open Text View Of Chat Session', wx.ID_ANY, '#bdbdbd')

    
    def build_dice(self):
        self.diceSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.numDieText = wx.TextCtrl( self, wx.ID_ANY, "1", 
                                    size= wx.Size(25, 25), validator=orpg.tools.inputValidator.MathOnlyValidator() )
        self.dieModText = wx.TextCtrl( self, wx.ID_ANY, "", 
                                    size= wx.Size(50, 25), validator=orpg.tools.inputValidator.MathOnlyValidator() )
        self.d4Button = createMaskedButton(self, dir_struct["icon"]+'b_d4.gif', 'Roll d4', wx.ID_ANY)
        self.d6Button = createMaskedButton(self, dir_struct["icon"]+'b_d6.gif', 'Roll d6', wx.ID_ANY)
        self.d8Button = createMaskedButton(self, dir_struct["icon"]+'b_d8.gif', 'Roll d8', wx.ID_ANY)
        self.d10Button = createMaskedButton(self, dir_struct["icon"]+'b_d10.gif', 'Roll d10', wx.ID_ANY)
        self.d12Button = createMaskedButton(self, dir_struct["icon"]+'b_d12.gif', 'Roll d12', wx.ID_ANY)
        self.d20Button = createMaskedButton(self, dir_struct["icon"]+'b_d20.gif', 'Roll d20', wx.ID_ANY)
        self.d100Button = createMaskedButton(self, dir_struct["icon"]+'b_d100.gif', 'Roll d100', wx.ID_ANY)

        self.diceSizer.Add( self.numDieText, 0, wx.ALIGN_CENTER | wx.EXPAND)
        self.diceSizer.Add( self.d4Button, 0 ,wx.EXPAND)
        self.diceSizer.Add( self.d6Button, 0 ,wx.EXPAND)
        self.diceSizer.Add( self.d8Button, 0 ,wx.EXPAND)
        self.diceSizer.Add( self.d10Button, 0 ,wx.EXPAND)
        self.diceSizer.Add( self.d12Button, 0 ,wx.EXPAND)
        self.diceSizer.Add( self.d20Button, 0 ,wx.EXPAND)
        self.diceSizer.Add( self.d100Button, 0 ,wx.EXPAND)
        self.diceSizer.Add( self.dieModText, 0, wx.ALIGN_CENTER, 5 )

        self.toolbar_sizer.Add( self.diceSizer, 0, wx.EXPAND)
        if self.settings.get_setting('DiceButtons_On') == '0': self.toggle_dice('0')
        else: self.toggle_dice('1')

    
    def toggle_dice(self, act):
        if act == '0': self.toolbar_sizer.Show(self.diceSizer, False)
        else: self.toolbar_sizer.Show(self.diceSizer, True)
        self.toolbar_sizer.Layout()

    
    def build_formating(self):
        self.formatSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.boldButton = createMaskedButton( self, dir_struct["icon"]+'bold.gif', 
                                                            'Make the selected text Bold', wx.ID_ANY, '#bdbdbd')
        self.italicButton = createMaskedButton( self, dir_struct["icon"]+'italic.gif', 
                                                            'Italicize the selected text', wx.ID_ANY, '#bdbdbd' )
        self.underlineButton = createMaskedButton( self, dir_struct["icon"]+'underlined.gif', 
                                                            'Underline the selected text', wx.ID_ANY, '#bdbdbd' )

        self.formatSizer.Add( self.boldButton, 0, wx.EXPAND )
        self.formatSizer.Add( self.italicButton, 0, wx.EXPAND )
        self.formatSizer.Add( self.underlineButton, 0, wx.EXPAND )
        self.toolbar_sizer.Add( self.formatSizer, 0, wx.EXPAND )
        if self.settings.get_setting('FormattingButtons_On') == '0': self.toggle_formating('0')
        else: self.toggle_formating('1')

    
    def toggle_formating(self, act):
        if act == '0': self.toolbar_sizer.Show(self.formatSizer, False)
        else: self.toolbar_sizer.Show(self.formatSizer, True)
        self.toolbar_sizer.Layout()

    def build_colorbutton(self):
        self.color_button = createMaskedButton(self, dir_struct["icon"]+'textcolor.gif', 
                                                    'Text Color', wx.ID_ANY, '#bdbdbd', 
                                                    wx.BITMAP_TYPE_GIF)

        self.saveButton = createMaskedButton(self, dir_struct["icon"]+'save.bmp', 
                                                    'Save the chatbuffer', wx.ID_ANY, 
                                                    '#c0c0c0', wx.BITMAP_TYPE_BMP )
        self.color_button.SetBackgroundColour(self.settings.get_setting('mytextcolor'))
        self.toolbar_sizer.Add(self.color_button, 0, wx.EXPAND)
        self.toolbar_sizer.Add(self.saveButton, 0, wx.EXPAND)

    
    def OnMotion(self, evt):
        contain = self.chatwnd.GetInternalRepresentation()
        if contain:
            sx = sy = 0
            x = y = 0
            (sx,sy) = self.chatwnd.GetViewStart()
            (sx1,sy1) = self.chatwnd.GetScrollPixelsPerUnit()
            sx = sx*sx1
            sy = sy*sy1
            (x,y) = evt.GetPosition()
            lnk = contain.GetLink(sx+x,sy+y)
            if lnk:
                try:
                    link = lnk.GetHref()
                    self.session.set_status_url(link)
                except: pass
        else: logger.general("Error, self.chatwnd.GetInternalRepresentation() return None")
        evt.Skip()

    def myKeyHook(self, event):
        if self.session.get_status() == MPLAY_CONNECTED:   #  only do if we're connected
            thisPress = time.time()                #  thisPress is local temp variable
            if (thisPress - self.lastSend) > 4:    #  Check to see if it's been 5 seconds since our last notice
                                                   #    If we're not already typing, then self.lastSend will be 0
                self.sendTyping(1)                 #  send a not typing event here (1 for True)
            self.lastPress = thisPress             #  either way, record the time of this keystroke for use in
                                                   #  self.typingTimerFunc()
        if self.settings.get_setting('SuppressChatAutoComplete') == '1':
            logger.debug("Exit chat_panel->myKeyHook(self, event) return 1")
            return 1
        else:
            logger.debug("Exit chat_panel->myKeyHook(self, event) return 0")
            return 0

    def typingTimerFunc(self, event):
        #following added by mDuo13
        ##############refresh_counter()##############
        for plugin_fname in self.activeplugins.keys():
            plugin = self.activeplugins[plugin_fname]
            try: plugin.refresh_counter()
            except Exception, e:
                if str(e) != "'module' object has no attribute 'refresh_counter'":
                    logger.general(traceback.format_exc())
                    logger.general("EXCEPTION: " + str(e))
        #end mDuo13 added code
        if self.lastSend:                          #  This will be zero when not typing, so equiv to if is_typing
            thisTime = time.time()                 #  thisTime is a local temp variable
            if (thisTime - self.lastPress) > 4:    #  Check to see if it's been 5 seconds since our last keystroke
                                                   #  If we're not already typing, then self.lastSend will be 0

                self.sendTyping(0)                 #  send a typing event here (0 for False)

    def sendTyping(self, typing):
        if typing:
            self.lastSend = time.time()  #  remember our send time for use in myKeyHook()
            #I think this is cleaner
            status_text = self.settings.get_setting('TypingStatusAlias')
            if status_text == "" or status_text == None: status_text = "Typing"
            self.session.set_text_status(status_text)
        else:
            self.lastSend = 0                            #  set lastSend to zero to indicate we're not typing
            #I think this is cleaner
            status_text = self.settings.get_setting('IdleStatusAlias')
            if status_text == "" or status_text == None: status_text = "Idle"
            self.session.set_text_status(status_text)

    def set_colors(self):
        # chat window backround color
        self.bgcolor = self.settings.get_setting('bgcolor')
        # chat window normal text color
        self.textcolor = self.settings.get_setting('textcolor')
        # color of text player types
        self.mytextcolor = self.settings.get_setting('mytextcolor')
        # color of system warnings
        self.syscolor = self.settings.get_setting('syscolor')
        # color of system info messages
        self.infocolor = self.settings.get_setting('infocolor')
        # color of emotes
        self.emotecolor = self.settings.get_setting('emotecolor')
        # color of whispers
        self.whispercolor = self.settings.get_setting('whispercolor')
    
    def set_chat_text(self, txt):
        self.chattxt.SetValue(txt)
        self.chattxt.SetFocus()
        self.chattxt.SetInsertionPointEnd()

    
    def get_chat_text(self):
        return self.chattxt.GetValue()

    # This subroutine sets the focus to the chat window
    
    def set_chat_text_focus(self, event):
        wx.CallAfter(self.chattxt.SetFocus)

    def submit_chat_text(self, s):
        self.histidx = -1
        self.temptext = ""
        self.history = [s] + self.history 

        # play sound
        sound_file = self.settings.get_setting("SendSound")
        if sound_file != '': component.get('sound').play(sound_file)
        if s[0] != "/": ## it's not a slash command
            s = self.ParsePost( s, True, True )
        else: self.chat_cmds.docmd(s) # emote is in chatutils.py

    def on_chat_key_down(self, event):
        s = self.chattxt.GetValue()
        if event.GetKeyCode() == wx.WXK_RETURN and not event.ShiftDown():
            logger.debug("event.GetKeyCode() == wx.WXK_RETURN")
            self.set_colors()
            if self.session.get_status() == MPLAY_CONNECTED:
                self.sendTyping(0)
            if len(s):
                self.chattxt.SetValue('')
                s = s.replace('\n', '<br />')
                self.submit_chat_text(s)
            return
        event.Skip()
    
    def OnChar(self, event):
        s = self.chattxt.GetValue()

        macroText = ""
        s_key = False
        if self.f_keys.has_key(event.GetKeyCode()): s_key = self.f_keys[event.GetKeyCode()]

        if s_key: macroText = settings.get(s_key[29:])

        # Append to the existing typed text as needed and make sure the status doesn't change back.
        if len(macroText):
            self.sendTyping(0)
            self.submit_chat_text(macroText)

        ## UP KEY
        elif event.GetKeyCode() == wx.WXK_UP:
            logger.debug("event.GetKeyCode() == wx.WXK_UP")
            if self.histidx < len(self.history)-1:
                if self.histidx is -1: self.temptext = self.chattxt.GetValue()
                self.histidx += 1
                self.chattxt.SetValue(self.history[self.histidx])
                self.chattxt.SetInsertionPointEnd()
            else:
                self.histidx = len(self.history) -1

        ## DOWN KEY
        elif event.GetKeyCode() == wx.WXK_DOWN:
            logger.debug("event.GetKeyCode() == wx.WXK_DOWN")
            #histidx of -1 indicates currently viewing text that's not in self.history
            if self.histidx > -1:
                self.histidx -= 1
                if self.histidx is -1: #remember, it just decreased
                    self.chattxt.SetValue(self.temptext)
                else: self.chattxt.SetValue(self.history[self.histidx])
                self.chattxt.SetInsertionPointEnd()
            else: self.histidx = -1 

        ## TAB KEY
        elif  event.GetKeyCode() == wx.WXK_TAB:
            logger.debug("event.GetKeyCode() == wx.WXK_TAB")
            if s !="":
                found = 0
                nicks = []
                testnick = ""
                inlength = len(s)
                for getnames in self.session.players.keys():
                    striphtmltag = re.compile ('<[^>]+>*')
                    testnick = striphtmltag.sub ("", self.session.players[getnames][0])
                    if string.lower(s) == string.lower(testnick[:inlength]):
                        found = found + 1
                        nicks[len(nicks):]=[testnick]
                if found == 0: ## no nick match
                    self.Post(self.colorize(self.syscolor," ** No match found"))
                elif found > 1: ## matched more than 1, tell user what matched
                    nickstring = ""
                    nicklist = []
                    for foundnicks in nicks:
                        nickstring = nickstring + foundnicks + ", "
                        nicklist.append(foundnicks)
                    nickstring = nickstring[:-2]
                    self.Post(self.colorize(self.syscolor, " ** Multiple matches found: " + nickstring))
                    # set text to the prefix match between first two matches
                    settext = re.match(''.join(map(lambda x: '(%s?)' % x, string.lower(nicklist[0]))), string.lower(nicklist[1])).group()
                    # run through the rest of the nicks
                    for i in nicklist:
                        settext = re.match(''.join(map(lambda x: '(%s?)' % x, string.lower(i))), string.lower(settext)).group()
                    if settext:
                        self.chattxt.SetValue(settext)
                        self.chattxt.SetInsertionPointEnd()
                else: ## put the matched name in the chattxt box
                    settext = nicks[0] + ": "
                    self.chattxt.SetValue(settext)
                    self.chattxt.SetInsertionPointEnd()
            else: ## not online, and no text in chattxt box
                self.Post(self.colorize(self.syscolor, " ** That's the Tab key, Dave"))

        ## PAGE UP
        elif event.GetKeyCode() in (wx.WXK_PRIOR, wx.WXK_PAGEUP):
            logger.debug("event.GetKeyCode() in (wx.WXK_PRIOR, wx.WXK_PAGEUP)")
            self.chatwnd.ScrollPages(-1)
            if not self.lockscroll: self.lock_scroll(0)

        ## PAGE DOWN
        elif event.GetKeyCode() in (wx.WXK_NEXT, wx.WXK_PAGEDOWN):
            logger.debug("event.GetKeyCode() in (wx.WXK_NEXT, wx.WXK_PAGEDOWN)")
            if not self.lockscroll: self.lock_scroll(0)
            if ((self.chatwnd.GetScrollRange(1)-self.chatwnd.GetScrollPos(1)-self.chatwnd.GetScrollThumb(1) < 30) and self.lockscroll):
                self.lock_scroll(0)
            self.chatwnd.ScrollPages(1)

        ## END
        elif event.GetKeyCode() == wx.WXK_END:
            logger.debug("event.GetKeyCode() == wx.WXK_END")
            if self.lockscroll:
                self.lock_scroll(0)
                self.Post()
            event.Skip()

        elif event.GetKeyCode() == wx.WXK_RETURN and event.ShiftDown():
            st = self.chattxt.GetValue().split('\x0b')
            st += '\n'
            i = self.chattxt.GetInsertionPoint()
            self.chattxt.SetValue(''.join(st))
            self.chattxt.SetInsertionPoint(i+1)
            return

        ## NOTHING
        else: event.Skip()
        logger.debug("Exit chat_panel->OnChar(self, event)")
    
    def onDieRoll(self, evt):
        """Roll the dice based on the button pressed and the die modifiers entered, if any."""
        # Get any die modifiers if they have been entered
        numDie = self.numDieText.GetValue()
        dieMod = self.dieModText.GetValue()
        dieText = numDie
        # Now, apply and roll die mods based on the button that was pressed
        id = evt.GetId()
        if self.dieIDs.has_key(id): dieText += self.dieIDs[id]
        if len(dieMod) and dieMod[0] not in "*/-+": dieMod = "+" + dieMod
        dieText += dieMod
        dieText = "[" + dieText + "]"
        self.ParsePost(dieText, 1, 1)
        self.chattxt.SetFocus()

    def on_chat_save(self, evt):
        f = wx.FileDialog(self,"Save Chat Buffer",".","","HTM* (*.htm*)|*.htm*|HTML (*.html)|*.html|HTM (*.htm)|*.htm",wx.SAVE)
        if f.ShowModal() == wx.ID_OK:
            file = open(f.GetPath(), "w")
            file.write(self.ResetPage() + "</body></html>")
            file.close()
        f.Destroy()
        os.chdir(dir_struct["home"])

    def ResetPage(self):
        self.set_colors()
        buffertext = self.chatwnd.Header() + "\n"
        buffertext += chat_util.strip_body_tags(self.chatwnd.StripHeader()).replace("<br>", 
                                                                            "<br />").replace('</html>', 
                                                                            '').replace("<br />", 
                                                                            "<br />\n").replace("\n\n", '')
        return buffertext

    def on_text_color(self, event):
        hexcolor = self.r_h.do_hex_color_dlg(self)
        if hexcolor != None:
            (beg,end) = self.chattxt.GetSelection()
            if beg != end:
                txt = self.chattxt.GetValue()
                txt = txt[:beg]+self.colorize(hexcolor,txt[beg:end]) +txt[end:]
                self.chattxt.SetValue(txt)
                self.chattxt.SetInsertionPointEnd()
                self.chattxt.SetFocus()
            else:
                self.color_button.SetBackgroundColour(hexcolor)
                self.mytextcolor = hexcolor
                self.settings.set_setting('mytextcolor',hexcolor)
                self.set_colors()
                self.Post()

    def colorize(self, color, text):
        """Puts font tags of 'color' around 'text' value, and returns the string"""
        return "<font color='" + color + "'>" + text + "</font>"

    def on_text_format(self, event):
        id = event.GetId()
        txt = self.chattxt.GetValue()
        (beg,end) = self.chattxt.GetSelection()
        if beg != end: sel_txt = txt[beg:end]
        else: sel_txt = txt
        if id == self.boldButton.GetId(): sel_txt = "<b>" + sel_txt + "</b>"
        elif id == self.italicButton.GetId(): sel_txt = "<i>" + sel_txt + "</i>"
        elif id == self.underlineButton.GetId(): sel_txt = "<u>" + sel_txt + "</u>"
        if beg != end: txt = txt[:beg] + sel_txt + txt[end:]
        else: txt = sel_txt
        self.chattxt.SetValue(txt)
        self.chattxt.SetInsertionPointEnd()
        self.chattxt.SetFocus()

    def lock_scroll(self, event):
        if self.lockscroll:
            self.lockscroll = False
            self.scroll_lock.SetLabel("Scroll ON")
            if len(self.storedata) != 0:
                for line in self.storedata: self.chatwnd.AppendToPage(line)
            self.storedata = []
            self.scroll_down()
        else:
            self.lockscroll = True
            self.scroll_lock.SetLabel("Scroll OFF")

    def pop_textpop(self, event):
        """searchable popup text view of chatbuffer"""
        h_buffertext = self.ResetPage()
        h_dlg = orpgScrolledMessageFrameEditor(self, h_buffertext, "Text View of Chat Window", None, (500,300))
        h_dlg.Show(True)

    def OnSize(self, event=None):
        event.Skip()
        wx.CallAfter(self.scroll_down)

    def scroll_down(self):
        self.Freeze()
        self.chatwnd.scroll_down()
        self.Thaw()

    ###### message helpers ######
    
    def PurgeChat(self):
        self.set_colors()
        self.chatwnd.SetPage(self.chatwnd.Header())

    def system_message(self, text):
        self.send_chat_message(text,chat_msg.SYSTEM_MESSAGE)
        self.SystemPost(text)

    def info_message(self, text):
        self.send_chat_message(text,chat_msg.INFO_MESSAGE)
        self.InfoPost(text)

    def get_gms(self):
        the_gms = []
        for playerid in self.session.players:
            if len(self.session.players[playerid])>7:
                if self.session.players[playerid][7]=="GM" and self.session.group_id != '0': the_gms += [playerid]
        return the_gms

    def GetName(self):
        self.AliasLib = component.get('alias')
        player = self.session.get_my_info()
        if self.AliasLib != None:
            self.AliasLib.alias = self.aliasList.GetStringSelection();
            if self.AliasLib.alias[0] != self.defaultAliasName:
                logger.debug("Exit chat_panel->GetName(self)")
                return [self.chat_display_name([self.AliasLib.alias[0], player[1], player[2]]), self.AliasLib.alias[1]]
        return [self.chat_display_name(player), "Default"]

    def GetFilteredText(self, text):
        advregex = re.compile('\"(.*?)\"', re.I)
        self.AliasLib = component.get('alias')
        if self.AliasLib != None:
            self.AliasLib.filter = self.filterList.GetSelection()-1;
            for rule in self.AliasLib.filterRegEx:
                if not self.advancedFilter: text = re.sub(rule[0], rule[1], text)
                else:
                    for m in advregex.finditer(text):
                        match = m.group(0)
                        newmatch = re.sub(rule[0], rule[1], match)
                        text = text.replace(match, newmatch)
        return text

    def emote_message(self, text):
        text = Parse.Normalize(text)
        text = self.colorize(self.emotecolor, text)
        if self.type == MAIN_TAB and self.sendtarget == 'all': self.send_chat_message(text,chat_msg.EMOTE_MESSAGE)
        elif self.type == MAIN_TAB and self.sendtarget == "gm":
            msg_type = chat_msg.WHISPER_EMOTE_MESSAGE
            the_gms = self.get_gms()
            for each_gm in the_gms: self.send_chat_message(text,chat_msg.WHISPER_EMOTE_MESSAGE, str(each_gm))
        elif self.type == GROUP_TAB and WG_LIST.has_key(self.sendtarget):
            for pid in WG_LIST[self.sendtarget]:
                self.send_chat_message(text,chat_msg.WHISPER_EMOTE_MESSAGE, str(pid))
        elif self.type == WHISPER_TAB: self.send_chat_message(text,chat_msg.WHISPER_EMOTE_MESSAGE, str(self.sendtarget))
        elif self.type == NULL_TAB: pass
        name = self.GetName()[0]
        text = "** " + name + " " + text + " **"
        self.EmotePost(text)

    def whisper_to_players(self, text, player_ids):
        tabbed_whispers_p = self.settings.get_setting("tabbedwhispers")
        text = Parse.Normalize(text)
        player_names = ""
        for m in player_ids:
            id = m.strip()
            if self.session.is_valid_id(id):
                returned_name = self.session.get_player_by_player_id(id)[0]
                player_names += returned_name
                player_names += ", "
            else:
                player_names += " Unknown!"
                player_names += ", "
        comma = ","
        comma.join(player_ids)
        if (self.sendtarget == "all"):
            self.InfoPost("<i>whispering to "+ player_names + " " + text + "</i> ")
        text = self.colorize(self.mytextcolor, text)
        for id in player_ids:
            id = id.strip()
            if self.session.is_valid_id(id): self.send_chat_message(text,chat_msg.WHISPER_MESSAGE,id)
            else: self.InfoPost(id + " Unknown!")

    
    def send_chat_message(self, text, type=chat_msg.CHAT_MESSAGE, player_id="all"):
        #########send_msg()#############
        send = 1
        for plugin_fname in self.activeplugins.keys():
            plugin = self.activeplugins[plugin_fname]
            try: text, send = plugin.send_msg(text, send)
            except Exception, e:
                if str(e) != "'module' object has no attribute 'send_msg'":
                    logger.general(traceback.format_exc())
                    logger.general("EXCEPTION: " + str(e))
        msg = chat_msg.chat_msg()
        msg.set_text(text)
        msg.set_type(type)
        turnedoff = False
        if self.settings.get_setting("ShowIDInChat") == "1":
            turnedoff = True
            self.settings.set_setting("ShowIDInChat", "0")
        playername = self.GetName()[0]

        if turnedoff: self.settings.set_setting("ShowIDInChat", "1")
        msg.set_alias(playername)
        if send: self.session.send(msg.toxml(),player_id)
        del msg

    def post_incoming_msg(self, msg, player):
        type = msg.get_type()
        text = msg.get_text()
        alias = msg.get_alias()
        # who sent us the message?
        if alias: display_name = self.chat_display_name([alias, player[1], player[2]])
        elif player: display_name = self.chat_display_name(player)
        else: display_name = "Server Administrator"

        ######### START plugin_incoming_msg() ###########
        for plugin_fname in self.activeplugins.keys():
            plugin = self.activeplugins[plugin_fname]
            try: text, type, name = plugin.plugin_incoming_msg(text, type, display_name, player)
            except Exception, e:
                if str(e) != "'module' object has no attribute 'receive_msg'":
                    logger.general(traceback.format_exc())
                    logger.general("EXCEPTION: " + str(e))
        strip_img = self.settings.get_setting("Show_Images_In_Chat")
        if (strip_img == "0"): display_name = chat_util.strip_img_tags(display_name)
        recvSound = "RecvSound"
        # act on the type of messsage
        if (type == chat_msg.CHAT_MESSAGE):
            text = "<b>" + display_name + "</b>: " + text
            self.Post(text)
            self.parent.newMsg(0)
        elif type == chat_msg.WHISPER_MESSAGE or type == chat_msg.WHISPER_EMOTE_MESSAGE:
            tabbed_whispers_p = self.settings.get_setting("tabbedwhispers")
            displaypanel = self
            whisperingstring = " (whispering): "
            panelexists = 0
            GMWhisperTab = self.settings.get_setting("GMWhisperTab")
            GroupWhisperTab = self.settings.get_setting("GroupWhisperTab")
            name = '<i><b>' + display_name + '</b>: '
            text += '</i>'
            panelexists = 0
            created = 0
            try:
                if GMWhisperTab == '1':
                    the_gms = self.get_gms()
                    #Check if whisper if from a GM
                    if player[2] in the_gms:
                        msg = name + ' (GM Whisper:) ' + text
                        if type == chat_msg.WHISPER_MESSAGE: self.parent.GMChatPanel.Post(msg)
                        else: self.parent.GMChatPanel.EmotePost("**" + msg + "**")
                        idx = self.parent.get_tab_index(self.parent.GMChatPanel)
                        self.parent.newMsg(idx)
                        panelexists = 1
                #See if message if from someone in our groups or for a whisper tab we already have
                if not panelexists and GroupWhisperTab == "1":
                    for panel in self.parent.group_tabs:
                        if WG_LIST.has_key(panel.sendtarget) and WG_LIST[panel.sendtarget].has_key(int(player[2])):
                            msg = name + text
                            if type == chat_msg.WHISPER_MESSAGE: panel.Post(msg)
                            else: panel.EmotePost("**" + msg + "**")
                            idx = self.parent.get_tab_index(panel)
                            self.parent.newMsg(idx)
                            panelexists = 1
                            break
                if not panelexists and tabbed_whispers_p == "1":
                    for panel in self.parent.whisper_tabs:
                        #check for whisper tabs as well, to save the number of loops
                        if panel.sendtarget == player[2]:
                            msg = name + whisperingstring + text
                            if type == chat_msg.WHISPER_MESSAGE: panel.Post(msg)
                            else: panel.EmotePost("**" + msg + "**")
                            idx = self.parent.get_tab_index(panel)
                            self.parent.newMsg(idx)
                            panelexists = 1
                            break
                #We did not fint the tab
                if not panelexists:
                    #If we get here the tab was not found
                    if GroupWhisperTab == "1":
                        for group in WG_LIST.keys():
                            #Check if this group has the player in it
                            if WG_LIST[group].has_key(int(player[2])):
                                #Yup, post message. Player may be in more then 1 group so continue as well
                                panel = self.parent.create_group_tab(group)
                                msg = name + text
                                if type == chat_msg.WHISPER_MESSAGE: wx.CallAfter(panel.Post, msg)
                                else: wx.CallAfter(panel.EmotePost, "**" + msg + "**")
                                created = 1
                    #Check to see if we should create a whisper tab
                    if not created and tabbed_whispers_p == "1":
                        panel = self.parent.create_whisper_tab(player[2])
                        msg = name + whisperingstring + text
                        if type == chat_msg.WHISPER_MESSAGE: wx.CallAfter(panel.Post, msg)
                        else: wx.CallAfter(panel.EmotePost, "**" + msg + "**")
                        created = 1
                    #Final check
                    if not created:
                        #No tabs to create, just send the message to the main chat tab
                        msg = name + whisperingstring + text
                        if type == chat_msg.WHISPER_MESSAGE: self.parent.MainChatPanel.Post(msg)
                        else: self.parent.MainChatPanel.EmotePost("**" + msg + "**")
                        self.parent.newMsg(0)
            except Exception, e:
                logger.general(traceback.format_exc())
                logger.general("EXCEPTION: 'Error in posting whisper message': " + str(e))
        elif (type == chat_msg.EMOTE_MESSAGE):
            text = "** " + display_name + " " + text + " **"
            self.EmotePost(text)
            self.parent.newMsg(0)
        elif (type == chat_msg.INFO_MESSAGE):
            text = "<b>" + display_name + "</b>: " + text
            self.InfoPost(text)
            self.parent.newMsg(0)
        elif (type == chat_msg.SYSTEM_MESSAGE):
            text = "<b>" + display_name + "</b>: " + text
            self.SystemPost(text)
            self.parent.newMsg(0)
        # playe sound
        sound_file = self.settings.get_setting(recvSound)
        if sound_file != '':
            component.get('sound').play(sound_file)

    #### Posting helpers #####

    def InfoPost(self, s):
        self.Post(self.colorize(self.infocolor, s), c='info')

    def SystemPost(self, s):
        self.Post(self.colorize(self.syscolor, s), c='system')

    def EmotePost(self, s):
        self.Post(self.colorize(self.emotecolor, s), c='emote')

    #### Standard Post method #####
    
    def Post(self, s="", send=False, myself=False, c='post'):
        strip_p = self.settings.get_setting("striphtml")
        strip_img = self.settings.get_setting("Show_Images_In_Chat")#moved back 7-11-05. --mDuo13
        if (strip_p == "1"): s = strip_html(s)
        if (strip_img == "0"): s = chat_util.strip_img_tags(s)
        s = chat_util.simple_html_repair(s)
        s = chat_util.strip_script_tags(s)
        s = chat_util.strip_li_tags(s)
        s = chat_util.strip_body_tags(s) #7-27-05 mDuo13
        s = chat_util.strip_misalignment_tags(s) #7-27-05 mDuo13
        aliasInfo = self.GetName()
        display_name = aliasInfo[0]
        if aliasInfo[1] != 'Default':
            defaultcolor = self.settings.get_setting("mytextcolor")
            self.settings.set_setting("mytextcolor", aliasInfo[1])
            self.set_colors()
        newline = ''
        #following added by mDuo13
        #########post_msg() - other##########
        if not myself and not send:
            for plugin_fname in self.activeplugins.keys():
                plugin = self.activeplugins[plugin_fname]
                try: s = plugin.post_msg(s, myself)
                except Exception, e:
                    if str(e) != "'module' object has no attribute 'post_msg'":
                        logger.general(traceback.format_exc())
                        logger.general("EXCEPTION: " + str(e))
        #end mDuo13 added code
        if myself:
            name = "<b>" + display_name + "</b>: "
            s = self.colorize(self.mytextcolor, s)
        else: name = ""
        if aliasInfo[1] != 'Default':
            self.settings.set_setting("mytextcolor", defaultcolor)
            self.set_colors()
        lineHasText = 1
        try: lineHasText = strip_html(s).replace("&nbsp;","").replace(" ","").strip()!=""
        except:
            lineHasText = 1
        if lineHasText:
            #following added by mDuo13
            if myself:
                s2 = s
                ########post_msg() - self #######
                for plugin_fname in self.activeplugins.keys():
                    plugin = self.activeplugins[plugin_fname]
                    try:
                        s2 = plugin.post_msg(s2, myself)
                    except Exception, e:
                        if str(e) != "'module' object has no attribute 'post_msg'":
                            logger.general(traceback.format_exc())
                            logger.general("EXCEPTION: " + str(e))
                if s2 != "":
                    #Italici the messages from tabbed whispers
                    if self.type == WHISPER_TAB or self.type == GROUP_TAB or self.sendtarget == 'gm':
                        s2 = s2 + '</i>'
                        name = '<i>' + name
                        if self.type == WHISPER_TAB: name += " (whispering): "
                        elif self.type == GROUP_TAB: name += self.settings.get_setting("gwtext") + ' '
                        elif self.sendtarget == 'gm': name += " (whispering to GM) "
                    newline = "<div class='"+c+"'> " + self.TimeIndexString() + name + s2 + "</div>"
                    log( self.settings, c, name+s2 )
            else:
                newline = "<div class='"+c+"'> " + self.TimeIndexString() + name + s + "</div>"
                log( self.settings, c, name+s )
        else: send = False
        newline = chat_util.strip_unicode(newline)
        if self.lockscroll == 0:
            self.chatwnd.AppendToPage(newline)
            self.scroll_down()
        else: self.storedata.append(newline)
        if send:
            if self.type == MAIN_TAB and self.sendtarget == 'all': self.send_chat_message(s)
            elif self.type == MAIN_TAB and self.sendtarget == "gm":
                the_gms = self.get_gms()
                self.whisper_to_players(s, the_gms)
            elif self.type == GROUP_TAB and WG_LIST.has_key(self.sendtarget):
                members = []
                for pid in WG_LIST[self.sendtarget]: members.append(str(WG_LIST[self.sendtarget][pid]))
                self.whisper_to_players(self.settings.get_setting("gwtext") + s, members)
            elif self.type == WHISPER_TAB: self.whisper_to_players(s, [self.sendtarget])
            elif self.type == NULL_TAB: pass
            else: self.InfoPost("Failed to send message, unknown send type for this tab")
        self.parsed=0

    def TimeIndexString(self):
        try:
            mtime = ""
            if self.settings.get_setting('Chat_Time_Indexing') == "0": pass
            elif self.settings.get_setting('Chat_Time_Indexing') == "1":
                mtime = time.strftime("[%I:%M:%S] ", time.localtime())
            return mtime
        except Exception, e:
            logger.general(traceback.format_exc())
            logger.general("EXCEPTION: " + str(e))
            return "[ERROR]"

    def ParsePost(self, s, send=False, myself=False):
        s = Parse.Normalize(s)
        self.set_colors()
        self.Post(s,send,myself)

    # This subroutine builds a chat display name.
    #
    def chat_display_name(self, player):
        if self.settings.get_setting("ShowIDInChat") == "0":
            display_name = player[0]
        else:
            display_name = "("+player[2]+") " + player[0]
        return display_name

    # This subroutine will get a hex color and return it, or return nothing
    #
    def get_color(self):
        data = wx.ColourData()
        data.SetChooseFull(True)
        dlg = wx.ColourDialog(self, data)
        if dlg.ShowModal() == wx.ID_OK:
            data = dlg.GetColourData()
            (red,green,blue) = data.GetColour().Get()
            hexcolor = self.r_h.hexstring(red, green, blue)
            dlg.Destroy()
            return hexcolor
        else:
            dlg.Destroy()
            return None

    # def get_color - end
    def replace_quotes(self, s):
        in_tag = 0
        i = 0
        rs = s[:]
        for c in s:
            if c == "<": in_tag += 1
            elif c == ">":
                if in_tag: in_tag -= 1
            elif c == '"':
                if in_tag: rs = rs[:i] + "'" + rs[i+1:]
            i += 1
        return rs

