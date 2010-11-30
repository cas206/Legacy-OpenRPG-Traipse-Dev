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
# File: aliaslib.py
# Author: Dj Gilcrease
# Maintainer:
# Version:
#   $Id: aliaslib.py,v Traipse 'Ornery-Orc' prof.ebral Exp $
#
# Description: nodehandler for alias.
#

__version__ = "$Id: aliaslib.py,v Traipse 'Ornery-Orc' prof.ebral Exp $"

from orpg.orpg_wx import *
from orpg.orpgCore import component
from orpg.orpg_windows import createMaskedButton, orpgMultiCheckBoxDlg
from orpg.tools.rgbhex import RGBHex
from orpg.dirpath import dir_struct
from orpg.tools.validate import validate
from orpg.tools.orpg_settings import settings
from xml.etree.ElementTree import tostring, parse
import re

class AliasLib(wx.Frame):
    def __init__(self):
        self.orpgframe = component.get('frame')
        wx.Frame.__init__(self, None, wx.ID_ANY, title="Alias Lib")
        self.orpgframe.Freeze()
        self.Freeze()
        self.SetOwnBackgroundColour('#EFEFEF')
        self.filename = settings.get_setting('aliasfile') + '.alias'
        validate.config_file(self.filename, "default_alias.alias")
        self.buildMenu()
        self.buildButtons()
        self.buildGUI()
        wx.CallAfter(self.InitSetup)
        wx.CallAfter(self.loadFile)
        self.Thaw()
        self.orpgframe.Thaw()
        self.Bind(wx.EVT_CLOSE, self.OnMB_FileExit)

    def InitSetup(self):
        self.chat = component.get('chat')
        self.gametree = component.get('tree')
        self.map = component.get('map')
        self.session = component.get('session')

    def buildMenu(self):
        filemenu = wx.Menu()
        item = wx.MenuItem(filemenu, wx.ID_ANY, "&New\tCtrl+N", "New ALias Lib")
        self.Bind(wx.EVT_MENU, self.OnMB_FileNew, item)
        filemenu.AppendItem(item)
        item = wx.MenuItem(filemenu, wx.ID_ANY, "&Open\tCtrl+O", "Open Alias Lib")
        self.Bind(wx.EVT_MENU, self.OnMB_FileOpen, item)
        filemenu.AppendItem(item)
        item = wx.MenuItem(filemenu, wx.ID_ANY, "&Save\tCtrl+S", "Save Alias Lib")
        self.Bind(wx.EVT_MENU, self.OnMB_FileSave, item)
        filemenu.AppendItem(item)
        item = wx.MenuItem(filemenu, wx.ID_ANY, "&Export to Tree", "Export to Tree")
        self.Bind(wx.EVT_MENU, self.OnMB_FileExportToTree, item)
        filemenu.AppendItem(item)
        item = wx.MenuItem(filemenu, wx.ID_ANY, "&Exit\tCtrl+X", "Exit")
        self.Bind(wx.EVT_MENU, self.OnMB_FileExit, item)
        filemenu.AppendItem(item)
        aliasmenu = wx.Menu()
        item = wx.MenuItem(aliasmenu, wx.ID_ANY, "New", "New")
        self.Bind(wx.EVT_MENU, self.OnMB_AliasNew, item)
        aliasmenu.AppendItem(item)
        item = wx.MenuItem(aliasmenu, wx.ID_ANY, "Add Temporary", "Add Temporary")
        self.Bind(wx.EVT_MENU, self.OnMB_AliasAddTemporary, item)
        aliasmenu.AppendItem(item)
        item = wx.MenuItem(aliasmenu, wx.ID_ANY, "Edit", "Edit")
        self.Bind(wx.EVT_MENU, self.OnMB_AliasEdit, item)
        aliasmenu.AppendItem(item)
        item = wx.MenuItem(aliasmenu, wx.ID_ANY, "Delete", "Delete")
        self.Bind(wx.EVT_MENU, self.OnMB_AliasDelete, item)
        aliasmenu.AppendItem(item)
        filtermenu = wx.Menu()
        item = wx.MenuItem(filtermenu, wx.ID_ANY, "New", "New")
        self.Bind(wx.EVT_MENU, self.OnMB_FilterNew, item)
        filtermenu.AppendItem(item)
        item = wx.MenuItem(filtermenu, wx.ID_ANY, "Edit", "Edit")
        self.Bind(wx.EVT_MENU, self.OnMB_FilterEdit, item)
        filtermenu.AppendItem(item)
        item = wx.MenuItem(filtermenu, wx.ID_ANY, "Delete", "Delete")
        self.Bind(wx.EVT_MENU, self.OnMB_FilterDelete, item)
        filtermenu.AppendItem(item)
        transmitmenu = wx.Menu()
        item = wx.MenuItem(transmitmenu, wx.ID_ANY, "Send\tCtrl+Enter", "Send")
        self.Bind(wx.EVT_MENU, self.OnMB_TransmitSend, item)
        transmitmenu.AppendItem(item)
        item = wx.MenuItem(transmitmenu, wx.ID_ANY, "Emote\tCtrl+E", "Emote")
        self.Bind(wx.EVT_MENU, self.OnMB_TransmitEmote, item)
        transmitmenu.AppendItem(item)
        item = wx.MenuItem(transmitmenu, wx.ID_ANY, "Whisper\tCtrl+W", "Whisper")
        self.Bind(wx.EVT_MENU, self.OnMB_TransmitWhisper, item)
        transmitmenu.AppendItem(item)
        item = wx.MenuItem(transmitmenu, wx.ID_ANY, "Macro\tCtrl+M", "Macro")
        self.Bind(wx.EVT_MENU, self.OnMB_TransmitMacro, item)
        transmitmenu.AppendItem(item)
        menu = wx.MenuBar()
        menu.Append(filemenu, "&File")
        menu.Append(aliasmenu, "&Alias")
        menu.Append(filtermenu, "&Filter")
        menu.Append(transmitmenu, "&Transmit")
        self.SetMenuBar(menu)

    def OnMB_FileNew(self, event):
        oldfilename = self.filename
        dlg = wx.TextEntryDialog(self, "Please Name This Alias Lib", "New Alias Lib")
        if dlg.ShowModal() == wx.ID_OK:
            self.filename = dlg.GetValue() + '.alias'
        dlg.Destroy()
        if oldfilename != self.filename:
            self.OnMB_FileSave(None, oldfilename)
            self.aliasList = []
            self.filterList = []
            self.OnMB_FileSave(None)
        settings.set_setting('aliasfile', self.filename[:-6])

    def OnMB_FileOpen(self, event):
        oldfilename = self.filename
        dlg = wx.FileDialog(self, "Select an Alias Lib to Open", 
                            dir_struct["user"], wildcard="*.alias", 
                            style=wx.HIDE_READONLY|wx.OPEN)
        if dlg.ShowModal() == wx.ID_OK:
            self.filename = dlg.GetFilename()
        dlg.Destroy()
        if oldfilename != self.filename:
            self.OnMB_FileSave(None, oldfilename)
            self.loadFile()
        settings.set_setting('aliasfile', self.filename[:-6])

    def OnMB_FileSave(self, event, file=None):
        idx = self.aliasIdx
        if file == None:
            file = self.filename
        xml = "<aliaslib>\n"
        for n in xrange(self.selectAliasWnd.GetItemCount()):
            self.alias = n
            xml += "\t<alias "
            xml += 'name="' + self.MakeHTMLSafe(self.alias[0]) + '" '
            xml += 'color="' + self.alias[1] + '" '
            xml += "/>\n"
        for n in xrange(1, len(self.filterList)):
            xml += "\t<filter "
            xml += 'name="' + self.filterList[n] + '">' + "\n"
            for rule in self.regExList[n-1]:
                xml += "\t\t<rule "
                xml += 'match="' + self.MakeHTMLSafe(rule[0]) + '" '
                xml += 'sub="' + self.MakeHTMLSafe(rule[1]) + '" '
                xml += "/>\n"
            xml += "\t</filter>\n"
        xml += "</aliaslib>"
        self.alias = idx
        f = open(dir_struct["user"] + file, "w")
        f.write(xml)
        f.close()

    def OnMB_FileExportToTree(self, event):
        xml = '<nodehandler class="voxchat_handler" '
        xml += 'icon="player" '
        xml += 'module="voxchat" '
        xml += 'name="' + self.filename[:-6] + '" '
        xml += 'use.filter="0" '
        xml += 'version="1.0">' + '\n'
        idx = self.aliasIdx
        for n in xrange(self.selectAliasWnd.GetItemCount()):
            self.alias = n
            xml += "\t<voxchat.alias "
            xml += 'name="' + self.MakeHTMLSafe(self.alias[0]) + '" '
            xml += 'color="' + self.alias[1] + '" '
            xml += "/>\n"
        self.alias = idx
        for n in xrange(1, len(self.filterList)):
            xml += "\t<voxchat.filter "
            xml += 'name="' + self.filterList[n] + '">' + "\n"
            for rule in self.regExList[n-1]:
                xml += "\t\t<rule "
                xml += 'match="' + self.MakeHTMLSafe(rule[0]) + '" '
                xml += 'sub="' + self.MakeHTMLSafe(rule[1]) + '" '
                xml += "/>\n"
            xml += "\t</voxchat.filter>\n"
        xml += "</nodehandler>"
        self.gametree.insert_xml(xml)

    def OnMB_FileExit(self, event):
        self.OnMB_FileSave(0)
        self.Hide()
        self.orpgframe.mainmenu.Check(self.orpgframe.mainmenu.FindMenuItem("Windows", "Alias Lib"), False)

    def OnMB_AliasNew(self, event):
        self.NewEditAliasDialog("New")

    def OnMB_AliasAddTemporary(self, event):
        minis = self.map.canvas.layers['miniatures'].miniatures
        for min in minis:
            name = min.label
            if name not in self.aliasList:
                i = self.selectAliasWnd.InsertStringItem(self.selectAliasWnd.GetItemCount(), name)
                self.selectAliasWnd.SetStringItem(i, 1, "Default")
                self.selectAliasWnd.RefreshItem(i)
        self.RefreshAliases()

    def OnMB_AliasEdit(self, event):
        if self.aliasIdx != -1:
            self.NewEditAliasDialog("Edit")

    def NewEditAliasDialog(self, type):
        dlg = wx.Dialog(self, wx.ID_ANY, type + " Alias", style=wx.DEFAULT_DIALOG_STYLE|wx.STAY_ON_TOP)
        txt = wx.TextCtrl(dlg, wx.ID_ANY)
        if type == 'Edit':
            txt.SetValue(self.alias[0])
        self.colorbtn = wx.Button(dlg, wx.ID_ANY, "Default Color")
        dlg.Bind(wx.EVT_BUTTON, self.ChangeAliasColor, self.colorbtn)
        if self.alias[1] != 'Default':
            self.colorbtn.SetLabel("Chat Color")
            self.colorbtn.SetForegroundColour(self.alias[1])
        okbtn = wx.Button(dlg, wx.ID_OK)
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(wx.StaticText(dlg, wx.ID_ANY, "Alias: "), 0, wx.EXPAND)
        sizer.Add(txt, 1, wx.EXPAND)
        sizer.Add(self.colorbtn, 0, wx.EXPAND)
        sizer.Add(okbtn, 0, wx.EXPAND)
        dlg.SetSizer(sizer)
        dlg.SetAutoLayout(True)
        dlg.Fit()
        if dlg.ShowModal() == wx.ID_OK:
            (r, g, b) = self.colorbtn.GetForegroundColour().Get()
            if type == 'Edit':
                self.selectAliasWnd.SetStringItem(self.aliasIdx, 0, txt.GetValue())
                if self.colorbtn.GetLabel() != 'Default Color':
                    self.aliasColor = RGBHex().hexstring(r, g, b)
                self.selectAliasWnd.RefreshItem(self.aliasIdx)
            else:
                i = self.selectAliasWnd.InsertStringItem(self.selectAliasWnd.GetItemCount(), txt.GetValue())
                if self.colorbtn.GetLabel() == 'Default Color':
                    self.selectAliasWnd.SetStringItem(i, 1, "Default")
                else:
                    self.selectAliasWnd.SetStringItem(i, 1, RGBHex().hexstring(r, g, b))
                    self.selectAliasWnd.SetItemTextColour(i, RGBHex().hexstring(r, g, b))
                self.selectAliasWnd.RefreshItem(i)
            self.RefreshAliases()

    def ChangeAliasColor(self, event):
        color = RGBHex().do_hex_color_dlg(self)
        self.colorbtn.SetLabel("Chat Color")
        self.colorbtn.SetForegroundColour(color)

    def OnMB_AliasDelete(self, event):
        if self.aliasIdx != -1:
            self.selectAliasWnd.DeleteItem(self.aliasIdx)
        self.RefreshAliases()

    def OnMB_FilterNew(self, event):
        dlg = wx.TextEntryDialog(self, 'Filter Name: ', 'Please name this filter')
        if dlg.ShowModal() != wx.ID_OK:
            dlg.Destroy()
            return
        filterName = dlg.GetValue()
        i = self.selectFilterWnd.InsertStringItem(self.selectFilterWnd.GetItemCount(), filterName)
        self.filter = i
        self.regExList.append([])
        self.OnMB_FilterEdit(None)

    def OnMB_FilterEdit(self, event):
        wnd = FilterEditWnd(self, self.filter, self.filterRegEx)
        wnd.MakeModal(True)
        wnd.Show()

    def OnMB_FilterDelete(self, event):
        if self.filterIdx != -1:
            self.selectFilterWnd.DeleteItem(self.filterIdx)

    def OnMB_TransmitSend(self, event):
        self.orpgframe.Freeze()
        if self.alias[1] != 'Default':
            defaultcolor = settings.get_setting("mytextcolor")
            settings.set_setting("mytextcolor", self.alias[1])
            self.chat.set_colors()
        line = self.textWnd.GetValue().replace("\n", "<br />")
        if self.checkFilterText.IsChecked() and self.filter != self.chat.defaultFilterName:
            for rule in self.filterRegEx: line = re.sub(rule[0], rule[1], line)
        if len(line) > 1:
            if len(line) > 1 and line[0] != "/": self.chat.ParsePost(line, True, True)
            else: self.chat.chat_cmds.docmd(line)
        if self.alias[1] != 'Default':
            settings.set_setting("mytextcolor", defaultcolor)
            self.chat.set_colors()
        if self.checkClearText.IsChecked():
            self.textWnd.SetValue("")
        self.orpgframe.Thaw()

    def OnMB_TransmitEmote(self, event):
        self.orpgframe.Freeze()
        line = self.textWnd.GetValue().replace("\n", "<br />")
        if self.checkFilterText.IsChecked() and self.filter != self.chat.defaultFilterName:
            for rule in self.filterRegEx: line = re.sub(rule[0], rule[1], line)
        self.chat.emote_message(line)
        if self.checkClearText.IsChecked():
            self.textWnd.SetValue("")
        self.orpgframe.Thaw()

    def OnMB_TransmitWhisper(self, event):
        self.orpgframe.Freeze()
        players = self.session.get_players()
        if self.alias[1] != 'Default':
            defaultcolor = settings.get_setting("mytextcolor")
            settings.set_setting("mytextcolor", self.alias[1])
            self.chat.set_colors()
        opts = []; idlist = []
        myid = self.session.get_id()
        for p in players:
            if p[2] != myid: opts.append("(" + p[2] + ") " + self.chat.html_strip(p[0]))
            if p[2] != myid: idlist.append(p[2])
        dlg = orpgMultiCheckBoxDlg(self, opts, "Select Players:", "Whisper To", [])
        sendto = []
        if dlg.ShowModal() == wx.ID_OK:
            selections = dlg.get_selections()
            for s in selections: sendto.append(idlist[s])
        line = self.textWnd.GetValue().replace("\n", "<br />")
        if self.checkFilterText.IsChecked() and self.filter != self.chat.defaultFilterName:
            for rule in self.filterRegEx: line = re.sub(rule[0], rule[1], line)
        if len(sendto): self.chat.whisper_to_players(line, sendto)
        if self.alias[1] != 'Default':
            settings.set_setting("mytextcolor", defaultcolor)
            self.chat.set_colors()
        if self.checkClearText.IsChecked(): self.textWnd.SetValue("")
        self.orpgframe.Thaw()

    def OnMB_TransmitMacro(self, event):
        self.orpgframe.Freeze()
        if self.alias[1] != 'Default':
            defaultcolor = settings.get_setting("mytextcolor")
            settings.set_setting("mytextcolor", self.alias[1])
            self.chat.set_colors()
        lines = self.textWnd.GetValue().split("\n")
        if self.checkFilterText.IsChecked() and self.filter != self.chat.defaultFilterName:
            line = self.textWnd.GetValue().replace("\n", "<br />")
            for rule in self.filterRegEx:
                line = re.sub(rule[0], rule[1], line)
        for line in lines:
            if len(line) > 1:
                if line[0] != "/": self.chat.ParsePost(line, True, True)
                else: self.chat.chat_cmds.docmd(line)
        if self.alias[1] != 'Default':
            settings.set_setting("mytextcolor", defaultcolor)
            self.chat.set_colors()
        if self.checkClearText.IsChecked(): self.textWnd.SetValue("")
        self.orpgframe.Thaw()

    def buildButtons(self):
        self.topBtnSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.middleBtnSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.bottomBtnSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.addFromMapBtn = createMaskedButton(self, dir_struct["icon"] + 'install.gif', 
                    'Add temporary aliases from map', wx.ID_ANY, "#C0C0C0")
        self.newAliasBtn = createMaskedButton(self, dir_struct["icon"] + 'player.gif', 'Add a new Alias', wx.ID_ANY)
        self.delAliasBtn = createMaskedButton(self, dir_struct["icon"] + 'noplayer.gif', 'Delete selected Alias', wx.ID_ANY)
        self.editAliasBtn = createMaskedButton(self, dir_struct["icon"] + 'note.gif', 'Edit selected Alias', wx.ID_ANY)
        self.Bind(wx.EVT_BUTTON, self.OnMB_AliasNew, self.newAliasBtn)
        self.Bind(wx.EVT_BUTTON, self.OnMB_AliasAddTemporary, self.addFromMapBtn)
        self.Bind(wx.EVT_BUTTON, self.OnMB_AliasEdit, self.editAliasBtn)
        self.Bind(wx.EVT_BUTTON, self.OnMB_AliasDelete, self.delAliasBtn)
        self.newFilterBtn = createMaskedButton(self, dir_struct["icon"] + 'add_filter.gif', 
                    'Add a new Filter', wx.ID_ANY, "#0000FF")
        self.editFilterBtn = createMaskedButton(self, dir_struct["icon"] + 'edit_filter.gif', 
                    'Edit selected Filter', wx.ID_ANY, "#FF0000")
        self.delFilterBtn = createMaskedButton(self, dir_struct["icon"] + 'delete_filter.gif', 
                    'Delete selected Filter', wx.ID_ANY, "#0000FF")
        self.Bind(wx.EVT_BUTTON, self.OnMB_FilterNew, self.newFilterBtn)
        self.Bind(wx.EVT_BUTTON, self.OnMB_FilterEdit, self.editFilterBtn)
        self.Bind(wx.EVT_BUTTON, self.OnMB_FilterDelete, self.delFilterBtn)
        self.textBoldBtn = createMaskedButton(self, dir_struct["icon"] + 'bold.gif', 'Bold', wx.ID_ANY, "#BDBDBD")
        self.textItalicBtn = createMaskedButton(self, dir_struct["icon"] + 'italic.gif', 'Italic', wx.ID_ANY, "#BDBDBD")
        self.textUnderlineBtn = createMaskedButton(self, dir_struct["icon"] + 'underlined.gif', 
                    'Underline', wx.ID_ANY, "#BDBDBD")
        self.textColorBtn = wx.Button(self, wx.ID_ANY, "Color")
        self.textColorBtn.SetForegroundColour(wx.BLACK)
        self.exportBtn = createMaskedButton(self, dir_struct["icon"] + 'grid.gif', 'Export to Tree', wx.ID_ANY)
        self.Bind(wx.EVT_BUTTON, self.FormatText, self.textBoldBtn)
        self.Bind(wx.EVT_BUTTON, self.FormatText, self.textItalicBtn)
        self.Bind(wx.EVT_BUTTON, self.FormatText, self.textUnderlineBtn)
        self.Bind(wx.EVT_BUTTON, self.FormatText, self.textColorBtn)
        self.Bind(wx.EVT_BUTTON, self.OnMB_FileExportToTree, self.exportBtn)
        self.topBtnSizer.Add(self.newAliasBtn, 0, wx.EXPAND)
        self.topBtnSizer.Add(self.addFromMapBtn, 0, wx.EXPAND)
        self.topBtnSizer.Add(self.editAliasBtn, 0, wx.EXPAND)
        self.topBtnSizer.Add(self.delAliasBtn, 0, wx.EXPAND)
        self.topBtnSizer.Add(self.newFilterBtn, 0, wx.EXPAND)
        self.topBtnSizer.Add(self.editFilterBtn, 0, wx.EXPAND)
        self.topBtnSizer.Add(self.delFilterBtn, 0, wx.EXPAND)
        self.topBtnSizer.Add(self.textBoldBtn, 0, wx.EXPAND)
        self.topBtnSizer.Add(self.textItalicBtn, 0, wx.EXPAND)
        self.topBtnSizer.Add(self.textUnderlineBtn, 0, wx.EXPAND)
        self.topBtnSizer.Add(self.textColorBtn, 0, wx.EXPAND)
        self.topBtnSizer.Add(self.exportBtn, 0, wx.EXPAND|wx.ALIGN_RIGHT)
        self.checkFilterText = wx.CheckBox(self, wx.ID_ANY, "Filter Text")
        self.Bind(wx.EVT_CHECKBOX, self.FilterTextChecked, self.checkFilterText)
        self.checkClearText = wx.CheckBox(self, wx.ID_ANY, "Auto Clear Text")
        self.middleBtnSizer.Add(self.checkFilterText, 0, wx.EXPAND)
        self.middleBtnSizer.Add(self.checkClearText, 0, wx.EXPAND)
        self.sayBtn = wx.Button(self, wx.ID_ANY, "Say")
        self.emoteBtn = wx.Button(self, wx.ID_ANY, "Emote")
        self.whisperBtn = wx.Button(self, wx.ID_ANY, "Whisper")
        self.macroBtn = wx.Button(self, wx.ID_ANY, "Macro")
        self.doneBtn = wx.Button(self, wx.ID_ANY, "Done")
        self.Bind(wx.EVT_BUTTON, self.OnMB_TransmitSend, self.sayBtn)
        self.Bind(wx.EVT_BUTTON, self.OnMB_TransmitEmote, self.emoteBtn)
        self.Bind(wx.EVT_BUTTON, self.OnMB_TransmitWhisper, self.whisperBtn)
        self.Bind(wx.EVT_BUTTON, self.OnMB_TransmitMacro, self.macroBtn)
        self.Bind(wx.EVT_BUTTON, self.OnMB_FileExit, self.doneBtn)
        self.bottomBtnSizer.Add(self.sayBtn, 0, wx.EXPAND)
        self.bottomBtnSizer.Add(self.emoteBtn, 0, wx.EXPAND)
        self.bottomBtnSizer.Add(self.whisperBtn, 0, wx.EXPAND)
        self.bottomBtnSizer.Add(self.macroBtn, 0, wx.EXPAND)
        self.bottomBtnSizer.Add(self.doneBtn, 0, wx.EXPAND|wx.ALIGN_RIGHT)

    def buildGUI(self):
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        rightwnd = wx.SplitterWindow(self, wx.ID_ANY, style=wx.SP_LIVE_UPDATE|wx.SP_NO_XP_THEME|wx.SP_3DSASH)
        leftwnd = wx.SplitterWindow(rightwnd, wx.ID_ANY, style=wx.SP_LIVE_UPDATE|wx.SP_NO_XP_THEME|wx.SP_3DSASH)
        self.selectAliasWnd = wx.ListCtrl(leftwnd, wx.ID_ANY, style=wx.LC_SINGLE_SEL|wx.LC_REPORT|wx.LC_HRULES)
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.NewAliasSelection, self.selectAliasWnd)
        self.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.NoAliasSelection, self.selectAliasWnd)
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnMB_AliasEdit, self.selectAliasWnd)
        self.selectFilterWnd = wx.ListCtrl(leftwnd, wx.ID_ANY, style=wx.LC_SINGLE_SEL|wx.LC_REPORT|wx.LC_HRULES)
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.NewFilterSelection, self.selectFilterWnd)
        self.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.NoFilterSelection, self.selectFilterWnd)
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnMB_FilterEdit, self.selectFilterWnd)
        self.textWnd = wx.TextCtrl(rightwnd, wx.ID_ANY, style=wx.TE_MULTILINE|wx.TE_BESTWRAP)
        leftwnd.SplitHorizontally(self.selectAliasWnd, self.selectFilterWnd)
        leftwnd.SetMinimumPaneSize(75)
        rightwnd.SplitVertically(leftwnd, self.textWnd)
        rightwnd.SetMinimumPaneSize(200)
        self.sizer.Add(self.topBtnSizer, 0, wx.EXPAND)
        self.sizer.Add(rightwnd, 1, wx.EXPAND)
        self.sizer.Add(self.middleBtnSizer, 0, wx.EXPAND)
        self.sizer.Add(self.bottomBtnSizer, 0, wx.EXPAND)
        self.SetSizer(self.sizer)
        self.SetAutoLayout(True)
        self.Fit()

    def loadFile(self):
        data = parse(dir_struct["user"] + self.filename)
        xml_dom = data.getroot()
        aliases = xml_dom.findall("alias")
        alist = []
        for alias in aliases:
            if alias.get("color"): color = alias.get("color")
            else: color = 'Default'
            aname = self.MakeSafeHTML(alias.get("name"))
            alist.append([aname, color])
        alist.sort()
        self.aliasList = alist
        filters = xml_dom.findall("filter")
        flist = []
        self.regExList = []
        for f in filters:
            flist.append(f.get("name"))
            rules = f.findall("rule")
            sub = []
            for rule in rules: 
                sub.append([self.MakeSafeHTML(rule.get("match")), 
                                        self.MakeSafeHTML(rule.get("sub"))])
            self.regExList.append(sub)
        self.filterList = flist
        self.alias = 0
        self.filter = 0

    def MakeSafeHTML(self, s):
        if s == None: return ''
        return s.replace("&amp;", "&").replace("&lt;", "<").replace("&quot;", '"').replace("&gt;", ">").replace("&#39;", "'")

    def MakeHTMLSafe(self, s):
        return s.replace("&", "&amp;").replace("<", "&lt;").replace('"', "&quot;").replace(">", "&gt;").replace("'", "&#39;")

    def ImportFromTree(self, xml_dom):
        oldfilename = self.filename
        if xml_dom.get('name') == 'Alias Library':
            dlg = wx.TextEntryDialog(self, "Please Name This Alias Lib", "New Alias Lib")
            if dlg.ShowModal() == wx.ID_OK:
                self.filename = dlg.GetValue() + '.alias'
                dlg.Destroy()
            else:
                dlg.Destroy()
                return
        else: self.filename = xml_dom.get('name') + '.alias'
        settings.set_setting('aliasfile', self.filename[:-6])
        if oldfilename != self.filename: self.OnMB_FileSave(None, oldfilename)
        f = open(dir_struct["user"] + self.filename, "w")
        f.write(tostring(xml_dom).replace('nodehandler', 'aliaslib').replace('voxchat.', ''))
        f.close()
        wx.CallAfter(self.loadFile)

    def NewAliasSelection(self, event):
        self.alias = event.GetIndex()
        wx.CallAfter(self.chat.aliasList.SetStringSelection, self.alias[0])

    def NoAliasSelection(self, event):
        self.aliasIdx = -1
        wx.CallAfter(self.chat.aliasList.SetStringSelection, self.alias[0])

    def GetSelectedAlias(self):
        self.InitSetup()
        if self.aliasIdx != -1:
            return [self.selectAliasWnd.GetItem(self.aliasIdx, 0).GetText(), 
                    self.selectAliasWnd.GetItem(self.aliasIdx, 1).GetText()]
        return [self.chat.defaultAliasName, "Default"]

    def SetSelectedAlias(self, alias):
        found = False
        if isinstance(alias, (int, long)):
            self.aliasIdx = alias
            found = True
        else:
            for n in xrange(self.selectAliasWnd.GetItemCount()):
                if self.selectAliasWnd.GetItem(n, 0).GetText() == alias:
                    self.aliasIdx = n
                    found = True
        if not found:
            self.aliasIdx = -1

    def GetAliasList(self):
        alist = []
        for n in xrange(0, self.selectAliasWnd.GetItemCount()):
            self.alias = n
            alist.append(self.alias[0])
        alist.sort()
        alist.insert(0, self.chat.defaultAliasName)
        return alist

    def SetAliasList(self, alist):
        self.selectAliasWnd.ClearAll()
        self.selectAliasWnd.InsertColumn(0, "Alias")
        self.selectAliasWnd.InsertColumn(1, "Chat Color")
        for item in alist:
            i = self.selectAliasWnd.InsertStringItem(self.selectAliasWnd.GetItemCount(), item[0])
            self.selectAliasWnd.SetStringItem(i, 1, item[1])
            if item[1] != 'Default': self.selectAliasWnd.SetItemTextColour(i, item[1])
            self.selectAliasWnd.RefreshItem(i)
        self.aliasIdx = -1
        self.RefreshAliases()

    def GetAliasColor(self):
        return self.alias[1]

    def RefreshAliases(self):
        self.orpgframe.Freeze()
        self.Freeze()
        self.alias = -1
        l1 = len(self.aliasList)
        l2 = len(self.filterList)
        if self.chat != None:
            tmp = self.chat.aliasList.GetStringSelection()
            self.alias = tmp
            aidx = self.aliasIdx+1
            if len(self.aliasList) <= aidx: aidx = 0
            self.chat.aliasList.Clear()
            for n in xrange(l1): self.chat.aliasList.Insert(self.aliasList[n], n)
            self.chat.aliasList.SetStringSelection(self.aliasList[aidx])
            fidx = self.chat.filterList.GetSelection()
            if len(self.filterList) <= fidx: fidx = 0
            self.chat.filterList.Clear()
            for n in xrange(l2):
                self.chat.filterList.Insert(self.filterList[n], n)
            self.chat.filterList.SetStringSelection(self.filterList[fidx])
            if self.chat.parent.GMChatPanel != None:
                aidx = self.chat.parent.GMChatPanel.aliasList.GetSelection()
                if len(self.aliasList) <- aidx: aidx = 0
                self.chat.parent.GMChatPanel.aliasList.Clear()
                for n in xrange(l1):
                    self.chat.parent.GMChatPanel.aliasList.Insert(self.aliasList[n], n)
                self.chat.parent.GMChatPanel.aliasList.SetStringSelection(self.aliasList[aidx])
                fidx = self.chat.parent.GMChatPanel.filterList.GetSelection()
                self.chat.parent.GMChatPanel.filterList.Clear()
                for n in xrange(l2):
                    self.chat.parent.GMChatPanel.filterList.Insert(self.filterList[n], n)
                self.chat.parent.GMChatPanel.filterList.SetStringSelection(self.filterList[fidx])
            for tab in self.chat.parent.whisper_tabs:
                aidx = tab.aliasList.GetSelection()
                if len(self.aliasList) <= aidx:
                    aidx = 0
                tab.aliasList.Clear()
                for n in xrange(l1):
                    tab.aliasList.Insert(self.aliasList[n], n)
                tab.aliasList.SetStringSelection(self.aliasList[aidx])
                fidx = tab.filterList.GetSelection()
                tab.filterList.Clear()
                for n in xrange(l2):
                    tab.filterList.Insert(self.filterList[n], n)
                tab.filterList.SetStringSelection(self.filterList[fidx])

            for tab in self.chat.parent.group_tabs:
                aidx = tab.aliasList.GetSelection()
                if len(self.aliasList) <= aidx:
                    aidx = 0
                tab.aliasList.Clear()
                for n in xrange(l1):
                    tab.aliasList.Insert(self.aliasList[n], n)
                tab.aliasList.SetStringSelection(self.aliasList[aidx])
                fidx = tab.filterList.GetSelection()
                tab.filterList.Clear()
                for n in xrange(l2):
                    tab.filterList.Insert(self.filterList[n], n)
                tab.filterList.SetStringSelection(self.filterList[fidx])

            for tab in self.chat.parent.null_tabs:
                aidx = tab.aliasList.GetSelection()
                if len(self.aliasList) <= aidx: aidx = 0
                tab.aliasList.Clear()
                for n in xrange(l1):
                    tab.aliasList.Insert(self.aliasList[n], n)
                tab.aliasList.SetStringSelection(self.aliasList[aidx])
                fidx = tab.filterList.GetSelection()
                tab.filterList.Clear()
                for n in xrange(l2):
                    tab.filterList.Insert(self.filterList[n], n)
                tab.filterList.SetStringSelection(self.filterList[fidx])
        self.Thaw()
        wx.CallAfter(self.orpgframe.Thaw)

    def SetAliasColor(self, color):
        if self.aliasIdx != -1:
            self.selectAliasWnd.SetStringItem(self.aliasIdx, 1, color)
            self.selectAliasWnd.SetItemTextColour(self.aliasIdx, color)

    def FilterTextChecked(self, event):
        if self.checkFilterText.IsChecked():
            self.chat.filterList.SetStringSelection(self.filter)
        else: self.chat.filterList.SetStringSelection(self.chat.defaultFilterName)

    def NewFilterSelection(self, event):
        self.filter = event.GetIndex()
        if self.checkFilterText.IsChecked(): wx.CallAfter(self.chat.filterList.SetStringSelection, self.filter)

    def NoFilterSelection(self, event):
        self.filter = -1
        wx.CallAfter(self.chat.filterList.SetStringSelection, self.filter)

    def GetSelectedFilter(self):
        if self.filterIdx != -1: return self.selectFilterWnd.GetItem(self.filterIdx, 0).GetText()
        return self.chat.defaultFilterName

    def SetSelectedFilter(self, idx):
        self.filterIdx = idx

    def GetFilterList(self):
        list = []
        for n in xrange(-1, self.selectFilterWnd.GetItemCount()):
            self.filter = n
            list.append(self.filter)
        return list

    def SetFilterList(self, list):
        self.selectFilterWnd.ClearAll()
        self.selectFilterWnd.InsertColumn(0, "Filter Name")
        for item in list:
            i = self.selectFilterWnd.InsertStringItem(self.selectFilterWnd.GetItemCount(), item)
            self.selectFilterWnd.RefreshItem(i)
        self.selectFilterWnd.SetColumnWidth(0, wx.LIST_AUTOSIZE)
        self.filter = -1
        self.RefreshAliases()

    def GetFilterRegEx(self):
        if self.filterIdx == -1: return []
        return self.regExList[self.filterIdx]

    def SetFilterRegEx(self, list):
        self.regExList[self.filterIdx] = list

    def FormatText(self, event):
        id = event.GetId()
        txt = self.textWnd.GetValue()
        (beg, end) = self.textWnd.GetSelection()
        if beg != end: sel_txt = txt[beg:end]
        else: sel_txt = txt
        if id == self.textBoldBtn.GetId(): sel_txt = "<b>" + sel_txt + "</b>"
        elif id == self.textItalicBtn.GetId(): sel_txt = "<i>" + sel_txt + "</i>"
        elif id == self.textUnderlineBtn.GetId(): sel_txt = "<u>" + sel_txt + "</u>"
        elif id == self.textColorBtn.GetId():
            dlg = wx.ColourDialog(self)
            if not dlg.ShowModal() == wx.ID_OK:
                dlg.Destroy()
                return
            color = dlg.GetColourData().GetColour()
            color = RGBHex().hexstring(color[0], color[1], color[2])
            dlg.Destroy()
            sel_txt = '<font color="' + color + '">' + sel_txt + '</font>'
        if beg != end: txt = txt[:beg] + sel_txt + txt[end:]
        else: txt = sel_txt
        self.textWnd.SetValue(txt)
        self.textWnd.SetInsertionPointEnd()
        self.textWnd.SetFocus()

    #Properties
    alias = property(GetSelectedAlias, SetSelectedAlias)
    aliasList = property(GetAliasList, SetAliasList)
    aliasColor = property(GetAliasColor, SetAliasColor)
    filter = property(GetSelectedFilter, SetSelectedFilter)
    filterList = property(GetFilterList, SetFilterList)
    filterRegEx = property(GetFilterRegEx, SetFilterRegEx)


class FilterEditWnd(wx.Frame):
    def __init__(self, parent, filterName, filterList):
        wx.Frame.__init__(self, parent, wx.ID_ANY, "Edit Filter: " + filterName)
        self.filterList = filterList
        self.parent = parent
        self.Freeze()
        self.buildGUI()
        self.fillList()
        self.Layout()
        self.grid.Select(0)
        self.Thaw()
        self.Bind(wx.EVT_CLOSE, self.OnExit)

    def buildGUI(self):
        bsizer = wx.BoxSizer(wx.VERTICAL)
        self.panel = wx.Panel(self, wx.ID_ANY)
        bsizer.Add(self.panel, 1, wx.EXPAND)
        self.SetSizer(bsizer)
        self.SetAutoLayout(True)
        self.grid = wx.ListCtrl(self.panel, wx.ID_ANY, style=wx.LC_SINGLE_SEL|wx.LC_REPORT|wx.LC_HRULES)
        self.grid.InsertColumn(0, "Replace")
        self.grid.InsertColumn(1, "With")
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.selectRule, self.grid)
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.RuleEdit, self.grid)
        self.addBtn = wx.Button(self.panel, wx.ID_ANY, 'Add')
        self.editBtn = wx.Button(self.panel, wx.ID_ANY, 'Edit')
        self.deleteBtn = wx.Button(self.panel, wx.ID_ANY, 'Delete')
        self.okBtn = wx.Button(self.panel, wx.ID_OK, 'Done')
        self.Bind(wx.EVT_BUTTON, self.RuleAdd, self.addBtn)
        self.Bind(wx.EVT_BUTTON, self.RuleEdit, self.editBtn)
        self.Bind(wx.EVT_BUTTON, self.RuleDelete, self.deleteBtn)
        self.Bind(wx.EVT_BUTTON, self.OnDone, self.okBtn)
        btsizer = wx.BoxSizer(wx.VERTICAL)
        btsizer.Add(self.addBtn, 0, wx.EXPAND)
        btsizer.Add(self.editBtn, 0, wx.EXPAND)
        btsizer.Add(self.deleteBtn, 0, wx.EXPAND)
        btsizer.Add(self.okBtn, 0, wx.EXPAND)
        sizer = wx.GridBagSizer(5,5)
        sizer.Add(self.grid, (0,0), flag=wx.EXPAND)
        sizer.Add(btsizer, (0,1), flag=wx.EXPAND)
        sizer.AddGrowableCol(0)
        sizer.AddGrowableRow(0)
        sizer.SetEmptyCellSize((0,0))
        self.panel.SetSizer(sizer)
        self.panel.SetAutoLayout(True)

    def fillList(self):
        for rule in self.filterList:
            i = self.grid.InsertStringItem(self.grid.GetItemCount(), rule[0])
            self.grid.SetStringItem(i, 1, rule[1])
        self.grid.SetColumnWidth(0, wx.LIST_AUTOSIZE)
        self.grid.SetColumnWidth(1, wx.LIST_AUTOSIZE)

    def selectRule(self, event):
        self.currentIdx = event.GetIndex()
        self.Freeze()
        for i in xrange(0, self.grid.GetItemCount()):
            self.grid.SetItemBackgroundColour(i, (255,255,255))
        self.grid.SetItemBackgroundColour(self.currentIdx, (0,255,0))
        self.grid.SetItemState(self.currentIdx, 0, wx.LIST_STATE_SELECTED)
        self.grid.EnsureVisible(self.currentIdx)
        self.Thaw()

    def RuleEdit(self, event):
        dlg = wx.Dialog(self, wx.ID_ANY, 'Edit Filter Rule')
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(wx.StaticText(dlg, wx.ID_ANY, 'Replace: '), 0, wx.EXPAND)
        rpltxt = wx.TextCtrl(dlg, wx.ID_ANY)
        sizer.Add(rpltxt, 0, wx.EXPAND)
        sizer.Add(wx.StaticText(dlg, wx.ID_ANY, 'With: '), 0, wx.EXPAND)
        withtxt = wx.TextCtrl(dlg, wx.ID_ANY)
        sizer.Add(withtxt, 0, wx.EXPAND)
        sizer.Add(wx.Button(dlg, wx.ID_OK, 'Ok'), 0, wx.EXPAND)
        sizer.Add(wx.Button(dlg, wx.ID_CANCEL, 'Cancel'), 0, wx.EXPAND)
        dlg.SetSizer(sizer)
        dlg.SetAutoLayout(True)
        dlg.Fit()
        rpltxt.SetValue(self.grid.GetItem(self.currentIdx, 0).GetText())
        withtxt.SetValue(self.grid.GetItem(self.currentIdx, 1).GetText())
        if dlg.ShowModal() != wx.ID_OK:
            dlg.Destroy()
            return
        self.grid.SetStringItem(self.currentIdx, 0, rpltxt.GetValue())
        self.grid.SetStringItem(self.currentIdx, 1, withtxt.GetValue())
        self.grid.RefreshItem(self.currentIdx)
        self.grid.SetColumnWidth(0, wx.LIST_AUTOSIZE)
        self.grid.SetColumnWidth(1, wx.LIST_AUTOSIZE)
        dlg.Destroy()

    def RuleAdd(self, event):
        i = self.grid.InsertStringItem(self.grid.GetItemCount(), '')
        self.grid.SetStringItem(i, 1, '')
        self.grid.Select(i)
        self.RuleEdit(None)

    def RuleDelete(self, event):
        self.grid.DeleteItem(self.currentIdx)
        self.grid.Select(0)

    def OnExit(self, event):
        self.MakeModal(False)
        list = []
        for i in xrange(0, self.grid.GetItemCount()):
            list.append([self.grid.GetItem(i, 0).GetText(), self.grid.GetItem(i, 1).GetText()])
        self.parent.filterRegEx = list
        event.Skip()

    def OnDone(self, event):
        self.Close()
