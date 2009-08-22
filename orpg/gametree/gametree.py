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
# File: gametree.py
# Author: Chris Davis
# Maintainer:
# Version:
#   $Id: gametree.py,v 1.68 2007/12/07 20:39:48 digitalxero Exp $
#
# Description: The file contains code fore the game tree shell
#

__version__ = "$Id: gametree.py,v 1.68 2007/12/07 20:39:48 digitalxero Exp $"

from orpg.orpg_wx import *
from orpg.orpg_windows import *
from orpg.orpgCore import component
from orpg.dirpath import dir_struct
from nodehandlers import core
import string
import urllib
import time
import os

from orpg.orpg_xml import xml
from orpg.tools.validate import validate
from orpg.tools.orpg_log import logger
from orpg.tools.decorators import debugging
from orpg.gametree.nodehandlers import containers, forms, dnd3e, dnd35, chatmacro
from orpg.gametree.nodehandlers import map_miniature_nodehandler
from orpg.gametree.nodehandlers import minilib, rpg_grid, d20, StarWarsd20, voxchat

from gametree_version import GAMETREE_VERSION

STD_MENU_DELETE = wx.NewId()
STD_MENU_DESIGN = wx.NewId()
STD_MENU_USE = wx.NewId()
STD_MENU_PP = wx.NewId()
STD_MENU_RENAME = wx.NewId()
STD_MENU_SEND = wx.NewId()
STD_MENU_SAVE = wx.NewId()
STD_MENU_ICON = wx.NewId()
STD_MENU_CLONE = wx.NewId()
STD_MENU_ABOUT = wx.NewId()
STD_MENU_HTML = wx.NewId()
STD_MENU_EMAIL = wx.NewId()
STD_MENU_CHAT = wx.NewId()
STD_MENU_WHISPER = wx.NewId()
STD_MENU_WIZARD = wx.NewId()
STD_MENU_NODE_SUBMENU = wx.NewId()
STD_MENU_NODE_USEFUL = wx.NewId()
STD_MENU_NODE_USELESS = wx.NewId()
STD_MENU_NODE_INDIFFERENT = wx.NewId()
STD_MENU_MAP = wx.NewId()
TOP_IFILE = wx.NewId()
TOP_INSERT_URL = wx.NewId()
TOP_NEW_TREE = wx.NewId()
TOP_SAVE_TREE = wx.NewId()
TOP_SAVE_TREE_AS = wx.NewId()
TOP_TREE_PROP = wx.NewId()
TOP_FEATURES = wx.NewId()

class game_tree(wx.TreeCtrl):
    @debugging
    def __init__(self, parent, id):
        wx.TreeCtrl.__init__(self,parent,id,  wx.DefaultPosition, 
                wx.DefaultSize,style=wx.TR_EDIT_LABELS | wx.TR_HAS_BUTTONS)
        #self.xml = component.get('xml') #
        self.settings = component.get('settings')
        self.session = component.get('session')
        self.chat = component.get('chat')
        self.mainframe = component.get('frame')
        self.build_img_list()
        self.build_std_menu()
        self.nodehandlers = {}
        self.nodes = {}
        self.init_nodehandlers()
        self.Bind(wx.EVT_LEFT_DCLICK, self.on_ldclick)
        self.Bind(wx.EVT_RIGHT_DOWN, self.on_rclick)
        self.Bind(wx.EVT_TREE_BEGIN_DRAG, self.on_drag, id=id)
        self.Bind(wx.EVT_LEFT_UP, self.on_left_up)
        self.Bind(wx.EVT_LEFT_DOWN, self.on_left_down)
        self.Bind(wx.EVT_TREE_END_LABEL_EDIT, self.on_label_change, id=self.GetId())
        self.Bind(wx.EVT_TREE_BEGIN_LABEL_EDIT, self.on_label_begin, id=self.GetId())
        self.Bind(wx.EVT_CHAR, self.on_char)
        self.Bind(wx.EVT_KEY_UP, self.on_key_up)
        self.id = 1
        self.dragging = False
        self.last_save_dir = dir_struct["user"]

        #Create tree from default if it does not exist
        validate.config_file("tree.xml","default_tree.xml")
        component.add("tree", self)
        #build tree
        self.root = self.AddRoot("Game Tree",self.icons['gear'])
        self.was_labeling = 0
        self.rename_flag = 0
        self.image_cache = {}
        logger.debug("Exit game_tree")

    @debugging
    def add_nodehandler(self, nodehandler, nodeclass):
        if not self.nodehandlers.has_key(nodehandler): self.nodehandlers[nodehandler] = nodeclass
        else: logger.debug("Nodehandler for " + nodehandler + " already exists!")

    @debugging
    def remove_nodehandler(self, nodehandler):
        if self.nodehandlers.has_key(nodehandler):
            del self.nodehandlers[nodehandler]
        else: logger.debug("No nodehandler for " + nodehandler + " exists!")

    @debugging
    def init_nodehandlers(self):
        self.add_nodehandler('group_handler', containers.group_handler)
        self.add_nodehandler('tabber_handler', containers.tabber_handler)
        self.add_nodehandler('splitter_handler', containers.splitter_handler)
        self.add_nodehandler('form_handler', forms.form_handler)
        self.add_nodehandler('textctrl_handler', forms.textctrl_handler)
        self.add_nodehandler('listbox_handler', forms.listbox_handler)
        self.add_nodehandler('link_handler', forms.link_handler)
        self.add_nodehandler('webimg_handler', forms.webimg_handler)
        self.add_nodehandler('dnd3echar_handler', dnd3e.dnd3echar_handler)
        self.add_nodehandler('dnd35char_handler', dnd35.dnd35char_handler)
        self.add_nodehandler('macro_handler', chatmacro.macro_handler)
        self.add_nodehandler('map_miniature_handler', map_miniature_nodehandler.map_miniature_handler)
        self.add_nodehandler('minilib_handler', minilib.minilib_handler)
        self.add_nodehandler('mini_handler', minilib.mini_handler)
        self.add_nodehandler('rpg_grid_handler', rpg_grid.rpg_grid_handler)
        self.add_nodehandler('d20char_handler', d20.d20char_handler)
        self.add_nodehandler('SWd20char_handler', StarWarsd20.SWd20char_handler)
        self.add_nodehandler('voxchat_handler', voxchat.voxchat_handler)
        self.add_nodehandler('file_loader', core.file_loader)
        self.add_nodehandler('node_loader', core.node_loader)
        self.add_nodehandler('url_loader', core.url_loader)
        self.add_nodehandler('min_map', core.min_map)

    #   event = wxKeyEvent
    #   set to be called by wxWindows by EVT_CHAR macro in __init__
    @debugging
    def on_key_up(self, evt):
        key_code = evt.GetKeyCode()
        if self.dragging and (key_code == wx.WXK_SHIFT):
            curSelection = self.GetSelection()
            cur = wx.StockCursor(wx.CURSOR_ARROW)
            self.SetCursor(cur)
            self.dragging = False
            obj = self.GetPyData(curSelection)
            self.SelectItem(curSelection)
            if(isinstance(obj,core.node_handler)):
                obj.on_drop(evt)
                self.drag_obj = None
        evt.Skip()

    @debugging
    def on_char(self, evt):
        key_code = evt.GetKeyCode()
        curSelection = self.GetSelection()                            #  Get the current selection
        if evt.ShiftDown() and ((key_code == wx.WXK_UP) or (key_code == wx.WXK_DOWN)) and not self.dragging:
            curSelection = self.GetSelection()
            obj = self.GetPyData(curSelection)
            self.SelectItem(curSelection)
            if(isinstance(obj,core.node_handler)):
                self.dragging = True
                cur = wx.StockCursor(wx.CURSOR_HAND)
                self.SetCursor(cur)
                self.drag_obj = obj
        elif key_code == wx.WXK_LEFT: self.Collapse(curSelection)
        elif key_code == wx.WXK_DELETE:                          #  Handle the delete key
            if curSelection:
                nextSelect = self.GetItemParent(curSelection)
                self.on_del(evt)
                try:
                    if self.GetItemText(nextSelect) != "": self.SelectItem(nextSelect)
                except: pass
        elif key_code == wx.WXK_F2:
            self.rename_flag = 1
            self.EditLabel(curSelection)
        evt.Skip()
   
    @debugging
    def locate_valid_tree(self, error, msg, dir, filename): ## --Snowdog 3/05
        """prompts the user to locate a new tree file or create a new one"""
        response = wx.MessageDialog(self, msg, error, wx.YES|wx.NO|wx.ICON_ERROR)
        if response == wx.YES:
            file = None
            filetypes = "Gametree (*.xml)|*.xml|All files (*.*)|*.*"
            dlg = wx.FileDialog(self, "Locate Gametree file", dir, filename, filetypes,wx.OPEN | wx.CHANGE_DIR)
            if dlg.ShowModal() == wx.ID_OK: file = dlg.GetPath()
            dlg.Destroy()
            if not file: self.load_tree(error=1)
            else: self.load_tree(file)
            return
        else:
            validate.config_file("tree.xml","default_tree.xml")
            self.load_tree(error=1)
            return

    @debugging
    def load_tree(self, filename=dir_struct["user"]+'tree.xml', error=0):
        self.settings.set_setting("gametree", filename)
        tmp = None
        xml_dom = None
        xml_doc = None
        try:
            logger.info("Reading Gametree file: " + filename + "...", True)
            tmp = open(filename,"r")
            xml_doc = xml.parseXml(tmp.read())
            tmp.close()
            if xml_doc == None: pass
            else: xml_dom = xml_doc._get_documentElement()
            logger.info("done.", True)

        except IOError:
            emsg = "Gametree Missing!\n"+filename+" cannot be found.\n\n"\
                   "Would you like to locate it?\n"\
                   "(Selecting 'No' will cause a new default gametree to be generated)"
            fn = filename[ ((filename.rfind(os.sep))+len(os.sep)):]
            self.locate_valid_tree("Gametree Error", emsg, dir_struct["user"], fn)
            logger.general(emsg)
            return

        if not xml_dom:
            os.rename(filename,filename+".corrupt")
            fn = filename[ ((filename.rfind(os.sep))+len(os.sep)):]
            emsg = "Your gametree is being regenerated.\n\n"\
                   "To salvage a recent version of your gametree\n"\
                   "exit OpenRPG and copy the lastgood.xml file in\n"\
                   "your myfiles directory to "+fn+ "\n"\
                   "in your myfiles directory.\n\n"\
                   "lastgood.xml WILL BE OVERWRITTEN NEXT TIME YOU RUN OPENRPG.\n\n"\
                   "Would you like to select a different gametree file to use?\n"\
                   "(Selecting 'No' will cause a new default gametree to be generated)"
            self.locate_valid_tree("Corrupt Gametree!", emsg, dir_struct["user"], fn)
            logger.general(emsg)
            return

        if xml_dom._get_tagName() != "gametree":
            fn = filename[ ((filename.rfind(os.sep))+len(os.sep)):]
            emsg = fn+" does not appear to be a valid gametree file.\n\n"\
                   "Would you like to select a different gametree file to use?\n"\
                   "(Selecting 'No' will cause a new default gametree to be generated)"
            self.locate_valid_tree("Invalid Gametree!", emsg, dir_struct["user"], fn)
            logger.debug(emsg)
            return

        # get gametree version - we could write conversion code here!
        self.master_dom = xml_dom
        logger.debug("Master Dom Set")

        try:
            version = self.master_dom.getAttribute("version")
            # see if we should load the gametree
            loadfeatures = int(self.settings.get_setting("LoadGameTreeFeatures"))
            if loadfeatures:
                xml_dom = xml.parseXml(open(dir_struct["template"]+"feature.xml","r").read())
                xml_dom = xml_dom._get_documentElement()
                xml_dom = self.master_dom.appendChild(xml_dom)
                self.settings.set_setting("LoadGameTreeFeatures","0")

            ## load tree
            logger.debug("Features loaded (if required)")
            self.CollapseAndReset(self.root)
            children = self.master_dom._get_childNodes()
            logger.info("Parsing Gametree Nodes ", True)
            for c in children:
                print '.',
                self.load_xml(c,self.root)
            logger.info("done", True)
            self.Expand(self.root)
            self.SetPyData(self.root,self.master_dom)
            if error != 1:
                infile = open(filename, "rb")
                outfile = open(dir_struct["user"]+"lastgood.xml", "wb")
                outfile.write(infile.read())
            else: logger.info("Not overwriting lastgood.xml file.", True)

        except Exception, e:
            logger.general(traceback.format_exc())
            wx.MessageBox("Corrupt Tree!\nYour game tree is being regenerated. To\nsalvage a recent version of your gametree\nexit OpenRPG and copy the lastgood.xml\nfile in your myfiles directory\nto "+filename+ "\nin your myfiles directory.\nlastgood.xml WILL BE OVERWRITTEN NEXT TIME YOU RUN OPENRPG.")
            os.rename(filename,filename+".corrupt")
            validate.config_file("tree.xml","default_tree.xml")
            self.load_tree(error=1)

    @debugging
    def build_std_menu(self, obj=None):
        # build useful menu
        useful_menu = wx.Menu()
        useful_menu.Append(STD_MENU_NODE_USEFUL,"Use&ful")
        useful_menu.Append(STD_MENU_NODE_USELESS,"Use&less")
        useful_menu.Append(STD_MENU_NODE_INDIFFERENT,"&Indifferent")

        # build standard menu
        self.std_menu = wx.Menu()
        self.std_menu.SetTitle("game tree")
        self.std_menu.Append(STD_MENU_USE,"&Use")
        self.std_menu.Append(STD_MENU_DESIGN,"&Design")
        self.std_menu.Append(STD_MENU_PP,"&Pretty Print")
        self.std_menu.AppendSeparator()
        self.std_menu.Append(STD_MENU_SEND,"Send To Player")
        self.std_menu.Append(STD_MENU_MAP,"Send To Map")
        self.std_menu.Append(STD_MENU_CHAT,"Send To Chat")
        self.std_menu.Append(STD_MENU_WHISPER,"Whisper To Player")
        self.std_menu.AppendSeparator()
        self.std_menu.Append(STD_MENU_ICON,"Change &Icon")
        self.std_menu.Append(STD_MENU_DELETE,"D&elete")
        self.std_menu.Append(STD_MENU_CLONE,"&Clone")
        self.std_menu.AppendMenu(STD_MENU_NODE_SUBMENU,"Node &Usefulness",useful_menu)
        self.std_menu.AppendSeparator()
        self.std_menu.Append(STD_MENU_SAVE,"&Save Node")
        self.std_menu.Append(STD_MENU_HTML,"E&xport as HTML")
        self.std_menu.AppendSeparator()
        self.std_menu.Append(STD_MENU_ABOUT,"&About")
        self.Bind(wx.EVT_MENU, self.on_send_to, id=STD_MENU_SEND)
        self.Bind(wx.EVT_MENU, self.indifferent, id=STD_MENU_NODE_INDIFFERENT)
        self.Bind(wx.EVT_MENU, self.useful, id=STD_MENU_NODE_USEFUL)
        self.Bind(wx.EVT_MENU, self.useless, id=STD_MENU_NODE_USELESS)
        self.Bind(wx.EVT_MENU, self.on_del, id=STD_MENU_DELETE)
        self.Bind(wx.EVT_MENU, self.on_send_to_map, id=STD_MENU_MAP)
        self.Bind(wx.EVT_MENU, self.on_node_design, id=STD_MENU_DESIGN)
        self.Bind(wx.EVT_MENU, self.on_node_use, id=STD_MENU_USE)
        self.Bind(wx.EVT_MENU, self.on_node_pp, id=STD_MENU_PP)
        self.Bind(wx.EVT_MENU, self.on_save, id=STD_MENU_SAVE)
        self.Bind(wx.EVT_MENU, self.on_icon, id=STD_MENU_ICON)
        self.Bind(wx.EVT_MENU, self.on_clone, id=STD_MENU_CLONE)
        self.Bind(wx.EVT_MENU, self.on_about, id=STD_MENU_ABOUT)
        self.Bind(wx.EVT_MENU, self.on_send_to_chat, id=STD_MENU_CHAT)
        self.Bind(wx.EVT_MENU, self.on_whisper_to, id=STD_MENU_WHISPER)
        self.Bind(wx.EVT_MENU, self.on_export_html, id=STD_MENU_HTML)
        self.top_menu = wx.Menu()
        self.top_menu.SetTitle("game tree")
        self.top_menu.Append(TOP_IFILE,"&Insert File")
        self.top_menu.Append(TOP_INSERT_URL,"Insert &URL")
        self.top_menu.Append(TOP_FEATURES, "Insert &Features Node")
        self.top_menu.Append(TOP_NEW_TREE, "&Load New Tree")
        self.top_menu.Append(TOP_SAVE_TREE,"&Save Tree")
        self.top_menu.Append(TOP_SAVE_TREE_AS,"Save Tree &As...")
        self.top_menu.Append(TOP_TREE_PROP,"&Tree Properties")
        self.Bind(wx.EVT_MENU, self.on_insert_file, id=TOP_IFILE)
        self.Bind(wx.EVT_MENU, self.on_insert_url, id=TOP_INSERT_URL)
        self.Bind(wx.EVT_MENU, self.on_save_tree_as, id=TOP_SAVE_TREE_AS)
        self.Bind(wx.EVT_MENU, self.on_save_tree, id=TOP_SAVE_TREE)
        self.Bind(wx.EVT_MENU, self.on_load_new_tree, id=TOP_NEW_TREE)
        self.Bind(wx.EVT_MENU, self.on_tree_prop, id=TOP_TREE_PROP)
        self.Bind(wx.EVT_MENU, self.on_insert_features, id=TOP_FEATURES)

    @debugging
    def do_std_menu(self, evt, obj):
        try: self.std_menu.Enable(STD_MENU_MAP, obj.checkToMapMenu())
        except: self.std_menu.Enable(STD_MENU_MAP, obj.map_aware())
        self.std_menu.Enable(STD_MENU_CLONE, obj.can_clone())
        self.PopupMenu(self.std_menu)

    @debugging
    def strip_html(self, player):
        ret_string = ""
        x = 0
        in_tag = 0
        for x in xrange(len(player[0])) :
            if player[0][x] == "<" or player[0][x] == ">" or in_tag == 1 :
                if player[0][x] == "<" : in_tag = 1
                elif player[0][x] == ">" : in_tag = 0
                else: pass
            else: ret_string = ret_string + player[0][x]
        logger.debug(ret_string)
        return ret_string

    @debugging
    def on_receive_data(self, data, player):
        beg = string.find(data,"<tree>")
        end = string.rfind(data,"</tree>")
        data = data[6:end]
        self.insert_xml(data)

    @debugging
    def on_send_to_chat(self, evt):
        item = self.GetSelection()
        obj = self.GetPyData(item)
        obj.on_send_to_chat(evt)

    @debugging
    def on_whisper_to(self, evt):
        players = self.session.get_players()
        opts = []
        myid = self.session.get_id()
        me = None
        for p in players:
            if p[2] != myid: opts.append("("+p[2]+") " + self.strip_html(p))
            else: me = p
        if len(opts): players.remove(me)
        if len(opts):
            dlg = orpgMultiCheckBoxDlg( self.GetParent(),opts,"Select Players:","Whisper To",[] )
            if dlg.ShowModal() == wx.ID_OK:
                item = self.GetSelection()
                obj = self.GetPyData(item)
                selections = dlg.get_selections()
                if len(selections) == len(opts): self.chat.ParsePost(obj.tohtml(),True,True)
                else:
                    player_ids = []
                    for s in selections:
                        player_ids.append(players[s][2])
                    self.chat.whisper_to_players(obj.tohtml(),player_ids)

    @debugging
    def on_export_html(self, evt):
        f = wx.FileDialog(self,"Select a file", self.last_save_dir,"","HTML (*.html)|*.html",wx.SAVE)
        if f.ShowModal() == wx.ID_OK:
            item = self.GetSelection()
            obj = self.GetPyData(item)
            type = f.GetFilterIndex()
            file = open(f.GetPath(),"w")
            data = "<html><head><title>"+obj.master_dom.getAttribute("name")+"</title></head>"
            data += "<body bgcolor=\"#FFFFFF\" >"+obj.tohtml()+"</body></html>"
            for tag in ("</tr>","</td>","</th>","</table>","</html>","</body>"):
                data = data.replace(tag,tag+"\n")
            file.write(data)
            file.close()
            self.last_save_dir, throwaway = os.path.split( f.GetPath() )
        f.Destroy()
        os.chdir(dir_struct["home"])

    @debugging
    def indifferent(self, evt):
        item = self.GetSelection()
        obj = self.GetPyData(item)
        obj.usefulness("indifferent")

    @debugging
    def useful(self, evt):
        item = self.GetSelection()
        obj = self.GetPyData(item)
        obj.usefulness("useful")

    @debugging
    def useless(self, evt):
        item = self.GetSelection()
        obj = self.GetPyData(item)
        obj.usefulness("useless")

    @debugging
    def on_email(self,evt):
        pass

    @debugging
    def on_send_to(self, evt):
        players = self.session.get_players()
        opts = []
        myid = self.session.get_id()
        me = None
        for p in players:
            if p[2] != myid: opts.append("("+p[2]+") " + self.strip_html(p))
            else: me = p
        if len(opts):
            players.remove(me)
            dlg = orpgMultiCheckBoxDlg( None, opts, "Select Players:", "Send To", [] )
            if dlg.ShowModal() == wx.ID_OK:
                item = self.GetSelection()
                obj = self.GetPyData(item)
                xmldata = "<tree>" + xml.toxml(obj) + "</tree>"
                selections = dlg.get_selections()
                if len(selections) == len(opts): self.session.send(xmldata)
                else:
                    for s in selections: self.session.send(xmldata,players[s][2])
            dlg.Destroy()

    @debugging
    def on_icon(self, evt):
        icons = self.icons.keys()
        icons.sort()
        dlg = wx.SingleChoiceDialog(self,"Choose Icon?","Change Icon",icons)
        if dlg.ShowModal() == wx.ID_OK:
            key = dlg.GetStringSelection()
            item = self.GetSelection()
            obj = self.GetPyData(item)
            obj.change_icon(key)
        dlg.Destroy()

    @debugging
    def on_wizard(self, evt):
        item = self.GetSelection()
        obj = self.GetPyData(item)
        name = "New " + obj.master_dom.getAttribute("name")
        icon = obj.master_dom.getAttribute("icon")
        xml_data = "<nodehandler name=\""+name+"\" icon=\"" + icon + "\" module=\"core\" class=\"node_loader\" >"
        xml_data += xml.toxml(obj)
        xml_data += "</nodehandler>"
        self.insert_xml(xml_data)
        logger.debug(xml_data)

    @debugging
    def on_clone(self, evt):
        item = self.GetSelection()
        obj = self.GetPyData(item)
        if obj.can_clone():
            parent_node = self.GetItemParent(item)
            prev_sib = self.GetPrevSibling(item)
            if not prev_sib.IsOk(): prev_sib = parent_node
            xml_dom = xml.parseXml(xml.toxml(obj))
            xml_dom = xml_dom._get_firstChild()
            parent = obj.master_dom._get_parentNode()
            xml_dom = parent.insertBefore(xml_dom, obj.master_dom)
            self.load_xml(xml_dom, parent_node, prev_sib)

    @debugging
    def on_save(self, evt):
        """save node to a xml file"""
        item = self.GetSelection()
        obj = self.GetPyData(item)
        obj.on_save(evt)
        os.chdir(dir_struct["home"])

    @debugging
    def on_save_tree_as(self, evt):
        f = wx.FileDialog(self,"Select a file", self.last_save_dir,"","*.xml",wx.SAVE)
        if f.ShowModal() == wx.ID_OK:
            self.save_tree(f.GetPath())
            self.last_save_dir, throwaway = os.path.split( f.GetPath() )
        f.Destroy()
        os.chdir(dir_struct["home"])

    @debugging
    def on_save_tree(self, evt=None):
        filename = self.settings.get_setting("gametree")
        self.save_tree(filename)

    @debugging
    def save_tree(self, filename=dir_struct["user"]+'tree.xml'):
        self.master_dom.setAttribute("version",GAMETREE_VERSION)
        self.settings.set_setting("gametree",filename)
        file = open(filename,"w")
        file.write(xml.toxml(self.master_dom,1))
        file.close()

    @debugging
    def on_load_new_tree(self, evt):
        f = wx.FileDialog(self,"Select a file", self.last_save_dir,"","*.xml",wx.OPEN)
        if f.ShowModal() == wx.ID_OK:
            self.load_tree(f.GetPath())
            self.last_save_dir, throwaway = os.path.split( f.GetPath() )
        f.Destroy()
        os.chdir(dir_struct["home"])

    @debugging
    def on_insert_file(self, evt):
        """loads xml file into the tree"""
        if self.last_save_dir == ".":
            self.last_save_dir = dir_struct["user"]
        f = wx.FileDialog(self,"Select a file", self.last_save_dir,"","*.xml",wx.OPEN)
        if f.ShowModal() == wx.ID_OK:
            self.insert_xml(open(f.GetPath(),"r").read())
            self.last_save_dir, throwaway = os.path.split( f.GetPath() )
        f.Destroy()
        os.chdir(dir_struct["home"])

    @debugging
    def on_insert_url(self, evt):
        """loads xml url into the tree"""
        dlg = wx.TextEntryDialog(self,"URL?","Insert URL", "http://")
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetValue()
            file = urllib.urlopen(path)
            self.insert_xml(file.read())
        dlg.Destroy()

    @debugging
    def on_insert_features(self, evt):
        self.insert_xml(open(dir_struct["template"]+"feature.xml","r").read())

    @debugging
    def on_tree_prop(self, evt):
        dlg = gametree_prop_dlg(self, self.settings)
        if dlg.ShowModal() == wx.ID_OK: pass
        dlg.Destroy()

    @debugging
    def on_node_design(self, evt):
        item = self.GetSelection()
        obj = self.GetPyData(item)
        obj.on_design(evt)

    @debugging
    def on_node_use(self, evt):
        item = self.GetSelection()
        obj = self.GetPyData(item)
        obj.on_use(evt)

    @debugging
    def on_node_pp(self, evt):
        item = self.GetSelection()
        obj = self.GetPyData(item)
        obj.on_html_view(evt)

    @debugging
    def on_del(self, evt):
        status_value = "none"
        try:
            item = self.GetSelection()
            if item:
                obj = self.GetPyData(item)
                parent_obj = obj
                try:
                    status_value = parent_obj.master_dom.getAttribute('status')
                    name = parent_obj.master_dom.getAttribute('name')
                except: status_value = "none"
                parent_obj = parent_obj.master_dom._get_parentNode()
                while status_value!="useful" and status_value!="useless":
                    try:
                        status_value = parent_obj.getAttribute('status')
                        name = parent_obj.getAttribute('name')
                        if status_value == "useless": break
                        elif status_value == "useful": break
                    except: status_value = "none"
                    try: parent_obj = parent_obj._get_parentNode()
                    except: break
                if status_value == "useful":
                    dlg = wx.MessageDialog(self, `name` + "  And everything beneath it are considered useful.  \n\nAre you sure you want to delete this item?",'Important Item',wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION)
                    if dlg.ShowModal() == wx.ID_YES: obj.delete()
                else: obj.delete()
        except:
            if self.GetSelection() == self.GetRootItem():
                msg = wx.MessageDialog(None,"You can't delete the root item.","Delete Error",wx.OK)
            else: msg = wx.MessageDialog(None,"Unknown error deleting node.","Delete Error",wx.OK)
            msg.ShowModal()
            msg.Destroy()

    @debugging
    def on_about(self, evt):
        item = self.GetSelection()
        obj = self.GetPyData(item)
        about = MyAboutBox(self,obj.about())
        about.ShowModal()
        about.Destroy()

    @debugging
    def on_send_to_map(self, evt):
        item = self.GetSelection()
        obj = self.GetPyData(item)
        if hasattr(obj,"on_send_to_map"): obj.on_send_to_map(evt)

    @debugging
    def insert_xml(self, txt):
        #Updated to allow safe merging of gametree files
        #without leaving an unusable and undeletable node.
        #                               -- Snowdog 8/03
        xml_dom = xml.parseXml(txt)
        if xml_dom == None:
            wx.MessageBox("Import Failed: Invalid or missing node data")
            logger.debug("Import Failed: Invalid or missing node data")
            logger.debug("Exit game_tree->insert_xml(self, txt)")
            return
        xml_temp = xml_dom._get_documentElement()

        if not xml_temp:
            wx.MessageBox("Error Importing Node or Tree")
            logger.debug("Error Importing Node or Tree")
            logger.debug("Exit game_tree->insert_xml(self, txt)")
            return

        if xml_temp._get_tagName() == "gametree":
            children = xml_temp._get_childNodes()
            for c in children: self.load_xml(c, self.root)
            logger.debug("Exit game_tree->insert_xml(self, txt)")
            return

        if not xml_dom:
            wx.MessageBox("XML Error")
            logger.debug("XML Error")
            logger.debug("Exit game_tree->insert_xml(self, txt)")
            return

        xml_dom = xml_dom._get_firstChild()
        child = self.master_dom._get_firstChild()
        xml_dom = self.master_dom.insertBefore(xml_dom,child)
        self.load_xml(xml_dom,self.root,self.root)

    @debugging
    def build_img_list(self):
        """make image list"""
        helper = img_helper()
        self.icons = { }
        self._imageList= wx.ImageList(16,16,False)
        man = open(dir_struct["icon"]+"icons.xml","r")
        xml_dom = xml.parseXml(man.read())
        man.close()
        xml_dom = xml_dom._get_documentElement()
        node_list = xml_dom._get_childNodes()
        for n in node_list:
            key = n.getAttribute("name")
            path = dir_struct["icon"] + n.getAttribute("file")
            img = helper.load_file(path)
            self.icons[key] = self._imageList.Add(img)
        self.SetImageList(self._imageList)

    @debugging
    def load_xml(self, xml_dom, parent_node, prev_node=None):
        #add the first tree node
        i = 0
        text = xml_dom.getAttribute("name")
        icon = xml_dom.getAttribute("icon")
        if self.icons.has_key(icon): i = self.icons[icon]
        name = xml_dom._get_nodeName()
        logger.debug("Text, icon and name set\n" + text + "\n" + icon + "\n" + name)
        if prev_node:
            if prev_node == parent_node: new_tree_node = self.PrependItem(parent_node, text, i, i)
            else: new_tree_node = self.InsertItem(parent_node,prev_node, text, i, i)
        else: new_tree_node = self.AppendItem(parent_node, text, i, i)

        logger.debug("Node Added to tree")
        #create a nodehandler or continue loading xml into tree
        if name == "nodehandler":
            #wx.BeginBusyCursor()
            logger.debug("We have a Nodehandler")
            try:
                py_class = xml_dom.getAttribute("class")
                logger.debug("nodehandler class: " + py_class)
                if not self.nodehandlers.has_key(py_class):
                    raise Exception, "Unknown Nodehandler for " + py_class
                self.nodes[self.id] = self.nodehandlers[py_class](xml_dom, new_tree_node)
                self.SetPyData(new_tree_node, self.nodes[self.id])
                logger.debug("Node Data set")
                bmp = self.nodes[self.id].get_scaled_bitmap(16,16)
                if bmp: self.cached_load_of_image(bmp,new_tree_node,)
                logger.debug("Node Icon loaded")
                self.id = self.id + 1
            except Exception, er:
                logger.general(traceback.format_exc())
 		        #logger.debug("Error Info: " + xml_dom.getAttribute("class") + "\n" + str(er), True)?indent?
                self.Delete(new_tree_node)
                parent = xml_dom._get_parentNode()
                parent.removeChild(xml_dom)
        return new_tree_node

    @debugging
    def cached_load_of_image(self, bmp_in, new_tree_node):
        image_list = self.GetImageList()
        img = wx.ImageFromBitmap(bmp_in)
        img_data = img.GetData()
        image_index = None
        for key in self.image_cache.keys():
            if self.image_cache[key] == str(img_data):
                image_index = key
                break

        if image_index is None:
            image_index = image_list.Add(bmp_in)
            self.image_cache[image_index] = img_data
        self.SetItemImage(new_tree_node,image_index)
        self.SetItemImage(new_tree_node,image_index, wx.TreeItemIcon_Selected)
        return image_index

    @debugging
    def on_rclick(self, evt):
        pt = evt.GetPosition()
        (item, flag) = self.HitTest(pt)
        if item.IsOk():
            obj = self.GetPyData(item)
            self.SelectItem(item)
            if(isinstance(obj,core.node_handler)): obj.on_rclick(evt)
            else: self.PopupMenu(self.top_menu)
        else: self.PopupMenu(self.top_menu,pt)

    @debugging
    def on_ldclick(self, evt):
        self.rename_flag = 0
        pt = evt.GetPosition()
        (item, flag) = self.HitTest(pt)
        if item.IsOk():
            obj = self.GetPyData(item)
            self.SelectItem(item)
            if(isinstance(obj,core.node_handler)):
                if not obj.on_ldclick(evt):
                    action = self.settings.get_setting("treedclick")
                    if action == "use": obj.on_use(evt)
                    elif action == "design": obj.on_design(evt)
                    elif action == "print": obj.on_html_view(evt)
                    elif action == "chat": self.on_send_to_chat(evt)

    @debugging
    def on_left_down(self, evt):
        pt = evt.GetPosition()
        (item, flag) = self.HitTest(pt)
        if item.IsOk() and self.was_labeling:
            self.SelectItem(item)
            self.rename_flag = 0
            self.was_labeling = 0
        elif (flag & wx.TREE_HITTEST_ONITEMLABEL) == wx.TREE_HITTEST_ONITEMLABEL and self.IsSelected(item):
            #  this next if tests to ensure that the mouse up occurred over a label, and not the icon
            self.rename_flag = 1
        else: self.SelectItem(item)
        evt.Skip()

    @debugging
    def on_left_up(self, evt):
        if self.dragging:
            cur = wx.StockCursor(wx.CURSOR_ARROW)
            self.SetCursor(cur)
            self.dragging = False
            pt = evt.GetPosition()
            (item, flag) = self.HitTest(pt)
            if item.IsOk():
                obj = self.GetPyData(item)
                self.SelectItem(item)
                if(isinstance(obj,core.node_handler)):
                    obj.on_drop(evt)
                    self.drag_obj = None

    @debugging
    def on_label_change(self, evt):
        item = evt.GetItem()
        txt = evt.GetLabel()
        self.was_labeling = 0
        self.rename_flag = 0
        if txt != "":
            obj = self.GetPyData(item)
            obj.master_dom.setAttribute('name',txt)
        else: evt.Veto()

    @debugging
    def on_label_begin(self, evt):
        if not self.rename_flag: evt.Veto()
        else:
            self.was_labeling = 1
            item = evt.GetItem()
            if item == self.GetRootItem():
                evt.Veto()

    @debugging
    def on_drag(self, evt):
        self.rename_flag = 0
        item = self.GetSelection()
        obj = self.GetPyData(item)
        self.SelectItem(item)
        if(isinstance(obj,core.node_handler) and obj.drag):
            self.dragging = True
            cur = wx.StockCursor(wx.CURSOR_HAND)
            self.SetCursor(cur)
            self.drag_obj = obj

    @debugging
    def is_parent_node(self, node, compare_node):
        parent_node = self.GetItemParent(node)
        if compare_node == parent_node:
            logger.debug("parent node")
            return 1
        elif parent_node == self.root:
            logger.debug("not parent")
            return 0
        else: return self.is_parent_node(parent_node, compare_node)

CTRL_TREE_FILE = wx.NewId()
CTRL_YES = wx.NewId()
CTRL_NO = wx.NewId()
CTRL_USE = wx.NewId()
CTRL_DESIGN = wx.NewId()
CTRL_CHAT = wx.NewId()
CTRL_PRINT = wx.NewId()

class gametree_prop_dlg(wx.Dialog):
    @debugging
    def __init__(self, parent, settings):
        wx.Dialog.__init__(self, parent, wx.ID_ANY, "Game Tree Properties")
        self.settings  = settings

        #sizers
        sizers = {}
        sizers['but'] = wx.BoxSizer(wx.HORIZONTAL)
        sizers['main'] = wx.BoxSizer(wx.VERTICAL)

        #box sizers
        box_sizers = {}
        box_sizers["save"] = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, "Save On Exit"), wx.HORIZONTAL)
        box_sizers["file"] = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, "Tree File"), wx.HORIZONTAL)
        box_sizers["dclick"] = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, "Double Click Action"), wx.HORIZONTAL)
        self.ctrls = {  CTRL_TREE_FILE : FileBrowseButtonWithHistory(self, wx.ID_ANY,  labelText="" ) ,
                        CTRL_YES : wx.RadioButton(self, CTRL_YES, "Yes", style=wx.RB_GROUP),
                        CTRL_NO : wx.RadioButton(self, CTRL_NO, "No"),
                        CTRL_USE : wx.RadioButton(self, CTRL_USE, "Use", style=wx.RB_GROUP),
                        CTRL_DESIGN : wx.RadioButton(self, CTRL_DESIGN, "Desgin"),
                        CTRL_CHAT : wx.RadioButton(self, CTRL_CHAT, "Chat"),
                        CTRL_PRINT : wx.RadioButton(self, CTRL_PRINT, "Pretty Print")
                        }
        self.ctrls[CTRL_TREE_FILE].SetValue(settings.get_setting("gametree"))
        opt = settings.get_setting("SaveGameTreeOnExit")
        self.ctrls[CTRL_YES].SetValue(opt=="1")
        self.ctrls[CTRL_NO].SetValue(opt=="0")
        opt = settings.get_setting("treedclick")
        self.ctrls[CTRL_DESIGN].SetValue(opt=="design")
        self.ctrls[CTRL_USE].SetValue(opt=="use")
        self.ctrls[CTRL_CHAT].SetValue(opt=="chat")
        self.ctrls[CTRL_PRINT].SetValue(opt=="print")
        box_sizers['save'].Add(self.ctrls[CTRL_YES],0, wx.EXPAND)
        box_sizers['save'].Add(wx.Size(10,10))
        box_sizers['save'].Add(self.ctrls[CTRL_NO],0, wx.EXPAND)
        box_sizers['file'].Add(self.ctrls[CTRL_TREE_FILE], 0, wx.EXPAND)
        box_sizers['dclick'].Add(self.ctrls[CTRL_USE],0, wx.EXPAND)
        box_sizers['dclick'].Add(wx.Size(10,10))
        box_sizers['dclick'].Add(self.ctrls[CTRL_DESIGN],0, wx.EXPAND)
        box_sizers['dclick'].Add(wx.Size(10,10))
        box_sizers['dclick'].Add(self.ctrls[CTRL_CHAT],0, wx.EXPAND)
        box_sizers['dclick'].Add(wx.Size(10,10))
        box_sizers['dclick'].Add(self.ctrls[CTRL_PRINT],0, wx.EXPAND)

        # buttons
        sizers['but'].Add(wx.Button(self, wx.ID_OK, "Apply"), 1, wx.EXPAND)
        sizers['but'].Add(wx.Size(10,10))
        sizers['but'].Add(wx.Button(self, wx.ID_CANCEL, "Cancel"), 1, wx.EXPAND)
        sizers['main'].Add(box_sizers['save'], 1, wx.EXPAND)
        sizers['main'].Add(box_sizers['file'], 1, wx.EXPAND)
        sizers['main'].Add(box_sizers['dclick'], 1, wx.EXPAND)
        sizers['main'].Add(sizers['but'], 0, wx.EXPAND|wx.ALIGN_BOTTOM )

        #sizers['main'].SetDimension(10,10,csize[0]-20,csize[1]-20)
        self.SetSizer(sizers['main'])
        self.SetAutoLayout(True)
        self.Fit()
        self.Bind(wx.EVT_BUTTON, self.on_ok, id=wx.ID_OK)

    @debugging
    def on_ok(self,evt):
        self.settings.set_setting("gametree",self.ctrls[CTRL_TREE_FILE].GetValue())
        self.settings.set_setting("SaveGameTreeOnExit",str(self.ctrls[CTRL_YES].GetValue()))
        if self.ctrls[CTRL_USE].GetValue(): self.settings.set_setting("treedclick","use")
        elif self.ctrls[CTRL_DESIGN].GetValue(): self.settings.set_setting("treedclick","design")
        elif self.ctrls[CTRL_PRINT].GetValue(): self.settings.set_setting("treedclick","print")
        elif self.ctrls[CTRL_CHAT].GetValue(): self.settings.set_setting("treedclick","chat")
        self.EndModal(wx.ID_OK)
