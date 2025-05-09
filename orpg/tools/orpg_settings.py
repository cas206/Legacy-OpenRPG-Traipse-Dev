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
# File: orpg_settings.py
# Author: Dj Gilcrease
# Maintainer:
# Version:
#   $Id: orpg_settings.py,v 1.51 2007/07/15 14:25:12 digitalxero Exp $
#
# Description: classes for orpg settings
#

from orpg.orpg_windows import *
from orpg.orpgCore import component
from orpg.dirpath import dir_struct
from rgbhex import *

from orpg.tools.orpg_log import logger
from orpg.tools.validate import validate
from xml.etree.ElementTree import ElementTree, Element, parse
from xml.etree.ElementTree import fromstring, tostring
from orpg.tools.settings import settings

class orpgSettingsWnd(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self,parent,-1,"OpenRPG Preferences", 
                            wx.DefaultPosition,size = wx.Size(-1,-1), 
                            style=wx.RESIZE_BORDER | wx.SYSTEM_MENU | wx.CAPTION)
        self.Freeze()
        self.settings = component.get("settings")
        self.chat = component.get("chat")
        self.changes = []
        self.SetMinSize((545,500))
        self.tabber = orpgTabberWnd(self, style=FNB.FNB_NO_X_BUTTON)
        self.build_gui()
        self.tabber.SetSelection(0)
        winsizer = wx.BoxSizer(wx.VERTICAL)
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(wx.Button(self, wx.ID_OK, "OK"), 1, wx.EXPAND)
        sizer.Add(wx.Size(10,10))
        sizer.Add(wx.Button(self, wx.ID_CANCEL, "Cancel"), 1, wx.EXPAND)
        winsizer.Add(self.tabber, 1, wx.EXPAND)
        winsizer.Add(sizer, 0, wx.EXPAND | wx.ALIGN_BOTTOM)
        self.winsizer = winsizer
        self.SetSizer(self.winsizer)
        self.SetAutoLayout(True)
        self.Fit()
        self.Bind(wx.EVT_BUTTON, self.onOk, id=wx.ID_OK)
        self.Thaw()

    def on_size(self,evt):
        (w,h) = self.GetClientSizeTuple()
        self.winsizer.SetDimension(0,0,w,h-25)

    def build_gui(self):
        validate.config_file("settings.xml","default_settings.xml")
        filename = dir_struct["user"] + "settings.xml"
        temp_file = parse(filename)
        children = self.settings.xml_dom.getchildren()
        for c in children: self.build_window(c, self.tabber)

    def build_window(self, xml_dom, parent_wnd):
        name = xml_dom.tag
        #container = 0
        if name=="tab": temp_wnd = self.do_tab_window(xml_dom,parent_wnd)
        return temp_wnd

    def do_tab_window(self, xml_dom, parent_wnd):
        type = xml_dom.get("type")
        name = xml_dom.get("name")

        if type == "grid":
            temp_wnd = self.do_grid_tab(xml_dom, parent_wnd)
            parent_wnd.AddPage(temp_wnd, name, False)
        elif type == "tab":
            temp_wnd = orpgTabberWnd(parent_wnd, style=FNB.FNB_NO_X_BUTTON)
            children = xml_dom.getchildren()
            for c in children:
                if c.tag == "tab": self.do_tab_window(c, temp_wnd)
            temp_wnd.SetSelection(0)
            parent_wnd.AddPage(temp_wnd, name, False)
        elif type == "text":
            temp_wnd = wx.TextCtrl(parent_wnd,-1)
            parent_wnd.AddPage(temp_wnd, name, False)
        else: temp_wnd = None
        return temp_wnd

    def do_grid_tab(self, xml_dom, parent_wnd):
        settings = []
        children = xml_dom.getchildren()
        for c in children:
            name = c.tag
            value = c.get("value")
            help = c.get("help")
            options = c.get("options")
            settings.append([name, value, options, help])
        temp_wnd = settings_grid(parent_wnd, settings, self.changes)
        return temp_wnd

    def onOk(self, evt):
        #This will write the settings back to the XML
        self.session = component.get("session")
        tabbedwindows = component.get("tabbedWindows")
        new = []
        for wnd in tabbedwindows:
            try:
                style = wnd.GetWindowStyleFlag()
                new.append(wnd)
            except: pass
        tabbedwindows = new
        component.add("tabbedWindows", tabbedwindows)
        rgbconvert = RGBHex()

        for i in xrange(0,len(self.changes)):
            self.settings.set_setting(self.changes[i][0], self.changes[i][1])

            ## Settings are now reactive and organized ##
            ok = {'IdleStatusAlias': self.chat.chat_cmds.on_status,
                'dieroller': self.dieroller_ok,
                'defaultfontsize': self.font_ok,
                'defaultfont': self.font_ok,
                'bgcolor': self.text_ok,
                'textcolor': self.text_ok,
                'ColorTree': self.colortree_ok,
                'player': self.session.set_name,
                'TabBackgroundGradient': self.tab_gradient_ok}

            if self.changes[i][0] in ok.keys(): ok[self.changes[i][0]](self.changes[i][1])

            elif self.changes[i][0] == 'GMWhisperTab' and self.changes[i][1] == '1': self.chat.parent.create_gm_tab()

            elif (self.changes[i][0][:3] == 'Tab' and self.changes[i][1][:6] == 'custom') or\
                (self.changes[i][0][:3] == 'Tab' and self.settings.get_setting('TabTheme')[:6] == 'custom'):
                gfrom = self.settings.get_setting('TabGradientFrom')
                (fred, fgreen, fblue) = rgbconvert.rgb_tuple(gfrom)
                gto = self.settings.get_setting('TabGradientTo')
                (tored, togreen, toblue) = rgbconvert.rgb_tuple(gto)
                tabtext = self.settings.get_setting('TabTextColor')
                (tred, tgreen, tblue) = rgbconvert.rgb_tuple(tabtext)
                for wnd in tabbedwindows:
                    style = wnd.GetWindowStyleFlag()
                    mirror = ~(FNB.FNB_VC71 | FNB.FNB_VC8 | FNB.FNB_FANCY_TABS | FNB.FNB_COLORFUL_TABS)
                    style &= mirror
                    if self.settings.get_setting('TabTheme') == 'customslant': style |= FNB.FNB_VC8
                    else: style |= FNB.FNB_FANCY_TABS
                    wnd.SetWindowStyleFlag(style)
                    wnd.SetGradientColourTo(wx.Color(tored, togreen, toblue))
                    wnd.SetGradientColourFrom(wx.Color(fred, fgreen, fblue))
                    wnd.SetNonActiveTabTextColour(wx.Color(tred, tgreen, tblue))
                    wnd.Refresh()

            self.toggleToolBars(self.chat, self.changes[i])
            try: self.toggleToolBars(self.chat.parent.GMChatPanel, self.changes[i])
            except: pass
            for panel in self.chat.parent.whisper_tabs: self.toggleToolBars(panel, self.changes[i])
            for panel in self.chat.parent.group_tabs: self.toggleToolBars(panel, self.changes[i])
            for panel in self.chat.parent.null_tabs: self.toggleToolBars(panel, self.changes[i])

        self.settings.save()
        self.Destroy()

    def tab_gradient_ok(self, changes):
        for wnd in tabbedwindows:
            (red, green, blue) = rgbconvert.rgb_tuple(changes)
            wnd.SetTabAreaColour(wx.Color(red, green, blue))
            wnd.Refresh()

    def dieroller_ok(self, changes):
        rm = component.get('DiceManager')
        cur_die = rm.getRoller()
        try:
            rm.setRoller(changes)
            self.chat.SystemPost('You have changed your die roller to the <b>"' + rm.getRoller() + '"</b> roller.')
        except Exception, e:
            rm.setRoller('std')
            rm.setRoller(cur_die)
            self.settings.change('dieroller', cur_die)
            self.chat.SystemPost('<b>"' + changes + '"</b> is an invalid roller.')
            self.chat.InfoPost('Available die rollers: ' +str(rm.listRollers()) )
            self.chat.InfoPost('You are using the <b>"' +cur_die+ '"</b> die roller.')

    def colortree_ok(self, changes):
        top_frame = component.get('frame')
        if changes == '1':
            top_frame.tree.SetBackgroundColour(self.settings.get_setting('bgcolor'))
            top_frame.tree.SetForegroundColour(self.settings.get_setting('textcolor'))
            top_frame.tree.Refresh()
            top_frame.players.SetBackgroundColour(self.settings.get_setting('bgcolor'))
            top_frame.players.SetForegroundColour(self.settings.get_setting('textcolor'))
            top_frame.players.Refresh()
        else:
            top_frame.tree.SetBackgroundColour('white')
            top_frame.tree.SetForegroundColour('black')
            top_frame.tree.Refresh()
            top_frame.players.SetBackgroundColour('white')
            top_frame.players.SetForegroundColour('black')
            top_frame.players.Refresh()

    def font_ok(self, changes):
        self.chat.chatwnd.SetDefaultFontAndSize(self.settings.get_setting('defaultfont'), 
                                                self.settings.get_setting('defaultfontsize'))
        self.chat.InfoPost("Font is now " + 
                            self.settings.get_setting('defaultfont') + " point size " + 
                            self.settings.get_setting('defaultfontsize'))
        self.chat.chatwnd.scroll_down()

    def text_ok(self, changes):
        self.chat.chatwnd.SetPage(self.chat.ResetPage())
        self.chat.chatwnd.scroll_down()
        top_frame = component.get('frame')
        if self.settings.get_setting('ColorTree') == '1':
            top_frame.tree.SetBackgroundColour(self.settings.get_setting('bgcolor'))
            top_frame.tree.SetForegroundColour(self.settings.get_setting('textcolor'))
            top_frame.tree.Refresh()
            top_frame.players.SetBackgroundColour(self.settings.get_setting('bgcolor'))
            top_frame.players.SetForegroundColour(self.settings.get_setting('textcolor'))
            top_frame.players.Refresh()
        else:
            top_frame.tree.SetBackgroundColour('white')
            top_frame.tree.SetForegroundColour('black')
            top_frame.tree.Refresh()
            top_frame.players.SetBackgroundColour('white')
            top_frame.players.SetForegroundColour('black')
            top_frame.players.Refresh()

    def toggleToolBars(self, panel, changes):
        if changes[0] == 'AliasTool_On': panel.toggle_alias(changes[1])
        elif changes[0] == 'DiceButtons_On': panel.toggle_dice(changes[1])
        elif changes[0] == 'FormattingButtons_On': panel.toggle_formating(changes[1])

class settings_grid(wx.grid.Grid):
    """grid for gen info"""
    def __init__(self, parent, settings, changed = []):
        wx.grid.Grid.__init__(self, parent, -1, style=wx.SUNKEN_BORDER | wx.WANTS_CHARS)
        self.setting_data = changed
        self.Bind(wx.EVT_SIZE, self.on_size)
        self.Bind(wx.grid.EVT_GRID_CELL_CHANGE, self.on_cell_change)
        self.Bind(wx.grid.EVT_GRID_CELL_LEFT_CLICK, self.on_left_click)
        self.CreateGrid(len(settings),3)
        self.SetRowLabelSize(0)
        self.SetColLabelValue(0,"Setting")
        self.SetColLabelValue(1,"Value")
        self.SetColLabelValue(2,"Available Options")
        self.settings = settings
        for i in range(len(settings)):
            self.SetCellValue(i,0,settings[i][0])
            self.SetCellValue(i,1,settings[i][1])
            if settings[i][1] and settings[i][1][0] == '#': self.SetCellBackgroundColour(i,1,settings[i][1])
            self.SetCellValue(i,2,settings[i][2])

    def on_left_click(self,evt):
        row = evt.GetRow()
        col = evt.GetCol()
        if col == 2: return
        elif col == 0:
            name = self.GetCellValue(row,0)
            str = self.settings[row][3]
            msg = wx.MessageBox(str,name)
            return
        elif col == 1:
            setting = self.GetCellValue(row,0)
            value = self.GetCellValue(row,1)
            if value and value[0] == '#':
                hexcolor = orpg.tools.rgbhex.RGBHex().do_hex_color_dlg(self)
                if hexcolor:
                    self.SetCellValue(row,2, hexcolor)
                    self.SetCellBackgroundColour(row,1,hexcolor)
                    self.Refresh()
                    setting = self.GetCellValue(row,0)
                    self.setting_data.append([setting, hexcolor])
            else: evt.Skip()

    def on_cell_change(self,evt):
        row = evt.GetRow()
        col = evt.GetCol()
        if col != 1: return
        setting = self.GetCellValue(row,0)
        value = self.GetCellValue(row,1)
        self.setting_data.append([setting, value])

    def get_h(self):
        (w,h) = self.GetClientSizeTuple()
        rows = self.GetNumberRows()
        minh = 0
        for i in range (0,rows): minh += self.GetRowSize(i)
        minh += 120
        return minh

    def on_size(self,evt):
        (w,h) = self.GetClientSizeTuple()
        cols = self.GetNumberCols()
        col_w = w/(cols)
        for i in range(0,cols): self.SetColSize(i,col_w)
        self.Refresh()

