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
# Traipse EZ_Tree Reference System (TaS - Prof.Ebral):
#
# The new EZ_Tree Reference System being implemented takes full advantage of 
# Python's OOP Language. The entire tree code is being reused, but a new ID is 
# being created which 'shuts off' some of the features of the tree and adds new ones.
# This new feature will allow users to quickly add a Reference button to new node
# handlers. The button will show a faximile of the tree and users can then create a
# node reference with ease!
#

from __future__ import with_statement

__version__ = "$Id: gametree.py,v 1.68 2007/12/07 20:39:48 digitalxero Exp $"

from orpg.orpg_wx import *
from orpg.orpg_windows import *
from orpg.orpgCore import component
from orpg.dirpath import dir_struct
from nodehandlers import core
import string, urllib, time, os
from shutil import copytree, copystat, copy, copyfile

#from orpg.orpg_xml import xml
from orpg.tools.validate import validate
from orpg.tools.orpg_log import logger, debug
from orpg.tools.orpg_settings import settings
from orpg.gametree.nodehandlers import containers, forms, dnd3e, dnd35, chatmacro
from orpg.gametree.nodehandlers import map_miniature_nodehandler
from orpg.gametree.nodehandlers import minilib, rpg_grid, d20, StarWarsd20, voxchat

from gametree_version import GAMETREE_VERSION

from xml.etree.ElementTree import ElementTree, Element, parse
from xml.etree.ElementTree import fromstring, tostring, XML, iselement
from xml.parsers.expat import ExpatError

def exists(path):
    try:
        os.stat(path)
        return True
    except: return False

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
EZ_REF = wx.NewId()

class game_tree(wx.TreeCtrl):
    
    def __init__(self, parent, id):
        wx.TreeCtrl.__init__(self,parent,id, wx.DefaultPosition, 
                wx.DefaultSize,style=wx.TR_EDIT_LABELS | wx.TR_HAS_BUTTONS)
        self.chat = component.get('chat')
        self.session = component.get('session')
        self.mainframe = component.get('frame')
        self.ez_ref = True if id == EZ_REF else False
        self.build_img_list()
        if not self.ez_ref: self.build_std_menu()
        self.nodehandlers = {}
        self.nodes = {}
        self.init_nodehandlers()
        if not self.ez_ref:
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
        self.tree_map = {}

        #Create tree from default if it does not exist
        validate.config_file("tree.xml","default_tree.xml")

        ## The EZ_Tree Reference creates a duplicate component called tree_back. This is because the
        ## tree wont parse fully without adding the component, and when a dupplicate component is created
        ## the older one is deleted. If there are an C++ errors the tree_back can be used as a failsafe

        if not self.ez_ref: component.add("tree", self); component.add('tree_fs', self) ## Fail Safe
        component.add('tree', self)

        #build tree
        self.root = self.AddRoot("Game Tree", self.icons['gear'])
        self.was_labeling = 0
        self.rename_flag = 0
        self.image_cache = {}
        logger.debug("Exit game_tree")
    
    def add_nodehandler(self, nodehandler, nodeclass):
        if not self.nodehandlers.has_key(nodehandler): self.nodehandlers[nodehandler] = nodeclass
        else: logger.debug("Nodehandler for " + nodehandler + " already exists!")
    
    def remove_nodehandler(self, nodehandler):
        if self.nodehandlers.has_key(nodehandler): del self.nodehandlers[nodehandler]
        else: logger.debug("No nodehandler for " + nodehandler + " exists!")

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
    
    def on_char(self, evt):
        key_code = evt.GetKeyCode()
        curSelection = self.GetSelection()  #  Get the current selection
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
   
    def locate_valid_tree(self, error, msg, filename): ## --Snowdog 3/05
        """prompts the user to locate a new tree file or create a new one"""
        response = wx.MessageBox(msg, error, wx.YES|wx.NO|wx.ICON_ERROR)
        if response == wx.YES:
            file = None
            dlg = wx.FileDialog(self, "Locate Gametree file", dir_struct["user"],
                                filename[ ((filename.rfind(os.sep))+len(os.sep)):],
                                "Gametree (*.xml)|*.xml|All files (*.*)|*.*",
                                wx.OPEN | wx.CHANGE_DIR)
            if dlg.ShowModal() == wx.ID_OK: file = dlg.GetPath()
            dlg.Destroy()
            if not file: self.load_tree(error=1)
            else: self.load_tree(file)
            return
        else:
            copyfile(dir_struct['template']+'default_tree.xml', filename)
            validate.config_file("tree.xml","default_tree.xml")
            self.load_tree(error=1)
            return
    
    def load_tree(self, filename=dir_struct["user"]+'tree.xml', error=0):
        settings.change("gametree", filename)
        if not os.path.exists(filename):
            emsg = "Gametree Missing!\n"+filename+" cannot be found.\n\n"\
                 "Would you like to locate it?\n"\
                 "(Selecting 'No' will cause a new default gametree to be generated)"
            self.locate_valid_tree("Gametree Error", emsg, filename)
            return
        try:
            self.xml_root = False
            tree = parse(filename)
            self.xml_root = tree.getroot()
        except: self.xml_root = False
        if not self.xml_root:
            count = 1
            while exists(filename[:len(filename)-4]+'-'+str(count)+'.xml'): count += 1
            corrupt_tree = filename[:len(filename)-4]+'-'+str(count)+'.xml'
            copyfile(filename, corrupt_tree)
            emsg = "Your gametree is being regenerated.\n\n"\
                 "To salvage a recent version of your gametree\n"\
                 "exit OpenRPG and copy the one of the tree-# files in\n"\
                 "your myfiles directory to "+filename+ "\n"\
                 "in your myfiles directory.\n\n"\
                 "lastgood.xml WILL BE OVERWRITTEN NEXT TIME YOU RUN OPENRPG.\n\n"\
                 "Would you like to select a different gametree file to use?\n"\
                 "(Selecting 'No' will cause a new default gametree to be generated)"
            self.locate_valid_tree("Corrupt Gametree!", emsg, filename)
            return
        if self.xml_root.tag != "gametree":
            emsg = filename+" does not appear to be a valid gametree file.\n\n"\
                 "Would you like to select a different gametree file to use?\n"\
                 "(Selecting 'No' will cause a new default gametree to be generated)"
            self.locate_valid_tree("Invalid Gametree!", emsg, filename)
            return
        try:
            # version = self.xml_root.get("version")
            # see if we should load the gametree
            loadfeatures = int(settings.get_setting("LoadGameTreeFeatures"))
            if loadfeatures:
                features_tree = parse(orpg.dirpath.dir_struct["template"]+"feature.xml")
                self.xml_root.append(features_tree.getroot())
                settings.change("LoadGameTreeFeatures","0")

            ## load tree
            logger.debug("Features loaded (if required)")
            self.CollapseAndReset(self.root)
            logger.note("Parsing Gametree Nodes ", True)
            for xml_child in self.xml_root:
                logger.note('.', True)
                self.load_xml(xml_child,self.root)
            logger.note("done", True)

            self.Expand(self.root)
            self.SetPyData(self.root,self.xml_root)
            if error != 1:
                with open(filename, "rb") as infile:
                    with open(dir_struct["user"]+"lastgood.xml", "wb") as outfile:
                        outfile.write(infile.read())
            else: logger.info("Not overwriting lastgood.xml file.", True)

        except Exception, e:
            logger.exception(traceback.format_exc())

            count = 1
            while exists(filename[:len(filename)-4]+'-'+str(count)+'.xml'): count += 1
            corrupt_tree = filename[:len(filename)-4]+'-'+str(count)+'.xml'
            copyfile(filename, corrupt_tree)
            wx.MessageBox("Your gametree is being regenerated.\n\n"\
                 "To salvage a recent version of your gametree\n"\
                 "exit OpenRPG and copy the one of the tree-# files in\n"\
                 "your myfiles directory to "+filename+ "\n"\
                 "in your myfiles directory.\n\n"\
                 "lastgood.xml WILL BE OVERWRITTEN NEXT TIME YOU RUN OPENRPG.\n\n")

            count = 1
            while exists(filename[:len(filename)-4]+'-'+str(count)+'.xml'): count += 1
            corrupt_tree = filename[:len(filename)-4]+'-'+str(count)+'.xml'
            copyfile(filename, corrupt_tree)
            validate.config_file("tree.xml","default_tree.xml")
            self.load_tree(error=1)
    
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
        self.top_menu.Append(TOP_IFILE,"&Insert Node File")
        self.top_menu.Append(TOP_INSERT_URL,"Insert Node &URL")
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

    def do_std_menu(self, evt, obj):
        try: self.std_menu.Enable(STD_MENU_MAP, obj.checkToMapMenu())
        except: self.std_menu.Enable(STD_MENU_MAP, obj.map_aware())
        self.std_menu.Enable(STD_MENU_CLONE, obj.can_clone())
        self.PopupMenu(self.std_menu)

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

    def on_receive_data(self, data):
        self.insert_xml(data)
    
    def on_send_to_chat(self, evt):
        item = self.GetSelection()
        obj = self.GetPyData(item)
        obj.on_send_to_chat(evt)
    
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
                    for s in selections: player_ids.append(players[s][2])
                    self.chat.whisper_to_players(obj.tohtml(),player_ids)

    def on_export_html(self, evt):
        f = wx.FileDialog(self,"Select a file", self.last_save_dir,"","HTML (*.html)|*.html",wx.SAVE)
        if f.ShowModal() == wx.ID_OK:
            item = self.GetSelection()
            obj = self.GetPyData(item)
            type = f.GetFilterIndex()
            with open(f.GetPath(),"w") as f:
                data = "<html><head><title>"+obj.xml.get("name")+"</title></head>"
                data += "<body bgcolor='#FFFFFF' >"+obj.tohtml()+"</body></html>"
                for tag in ("</tr>","</td>","</th>","</table>","</html>","</body>"): data = data.replace(tag,tag+"\n")
                f.write(data)
            self.last_save_dir, throwaway = os.path.split( f.GetPath() )
        f.Destroy()
        os.chdir(dir_struct["home"])

    def indifferent(self, evt):
        item = self.GetSelection()
        obj = self.GetPyData(item)
        obj.usefulness("indifferent")

    def useful(self, evt):
        item = self.GetSelection()
        obj = self.GetPyData(item)
        obj.usefulness("useful")

    def useless(self, evt):
        item = self.GetSelection()
        obj = self.GetPyData(item)
        obj.usefulness("useless")

    def on_email(self,evt):
        pass

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
                xmldata = "<tree>" + tostring(obj.xml) + "</tree>"
                selections = dlg.get_selections()
                if len(selections) == len(opts): self.session.send(xmldata)
                else:
                    for s in selections: self.session.send(xmldata,players[s][2])
            dlg.Destroy()

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

    def on_wizard(self, evt):
        item = self.GetSelection()
        obj = self.GetPyData(item)
        name = "New " + obj.xml_root.get("name")
        icon = obj.xml_root.get("icon")
        xml_data = "<nodehandler name='"+name+"' icon='" + icon + "' module='core' class='node_loader' >"
        xml_data += xml.toxml(obj)
        xml_data += "</nodehandler>"
        self.insert_xml(xml_data)
        logger.debug(xml_data)

    def on_clone(self, evt):
        item = self.GetSelection()
        obj = self.GetPyData(item)
        if obj.can_clone():
            parent_node = self.GetItemParent(item)
            prev_sib = self.GetPrevSibling(item)
            if not prev_sib.IsOk(): prev_sib = parent_node
            clone_xml = XML(tostring(obj.xml))
            if parent_node == self.root: parent_xml = self.GetPyData(parent_node)
            else: parent_xml = self.GetPyData(parent_node).xml
            for i in range(len(parent_xml)):
                if parent_xml[i] is obj.xml:
                    name = self.clone_renaming(parent_xml, parent_xml[i].get('name'))
                    clone_xml.set('name', name)
                    parent_xml.insert(i, clone_xml)
                    break
            self.load_xml(clone_xml, parent_node, prev_sib)

    def clone_renaming(self, node, name):
        node_list = node.getchildren()
        parent = node
        append = name.split('_')
        try: append_d = int(append[len(append)-1]); del append[len(append)-1]
        except: append_d = False
        if append_d: 
            append_d += 1; name = ''
            for a in append: name += a+'_'
            name = name+str(append_d)
        if not append_d:
            append_d = 1; name = ''
            for a in append: name += a+'_'
            name = name+str(append_d)
        for n in node_list:
            if n.get('name') == name: name = self.clone_renaming(parent, name)
        return name

    def on_save(self, evt):
        """save node to a xml file"""
        item = self.GetSelection()
        obj = self.GetPyData(item)
        obj.on_save(evt)
        os.chdir(dir_struct["home"])

    def on_save_tree_as(self, evt):
        f = wx.FileDialog(self,"Select a file", self.last_save_dir,"","*.xml",wx.SAVE)
        if f.ShowModal() == wx.ID_OK:
            self.save_tree(f.GetPath())
            self.last_save_dir, throwaway = os.path.split( f.GetPath() )
        f.Destroy()
        os.chdir(dir_struct["home"])

    def on_save_tree(self, evt=None):
        filename = settings.get_setting("gametree")
        self.save_tree(filename)

    def save_tree(self, filename=dir_struct["user"]+'tree.xml'):
        self.xml_root.set("version", GAMETREE_VERSION)
        settings.change("gametree", filename)
        ElementTree(self.xml_root).write(filename)

    def on_load_new_tree(self, evt):
        f = wx.FileDialog(self,"Select a file", self.last_save_dir,"","*.xml",wx.OPEN)
        if f.ShowModal() == wx.ID_OK:
            self.load_tree(f.GetPath())
            self.last_save_dir, throwaway = os.path.split( f.GetPath() )
        f.Destroy()
        os.chdir(dir_struct["home"])

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

    def on_insert_url(self, evt):
        """loads xml url into the tree"""
        dlg = wx.TextEntryDialog(self,"URL?","Insert URL", "http://")
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetValue()
            file = urllib.urlopen(path)
            self.insert_xml(file.read())
        dlg.Destroy()

    def on_insert_features(self, evt):
        self.insert_xml(open(dir_struct["template"]+"feature.xml","r").read())

    def on_tree_prop(self, evt):
        dlg = gametree_prop_dlg(self, settings)
        if dlg.ShowModal() == wx.ID_OK: pass
        dlg.Destroy()

    def on_node_design(self, evt):
        item = self.GetSelection()
        obj = self.GetPyData(item)
        obj.on_design(evt)

    def on_node_use(self, evt):
        item = self.GetSelection()
        obj = self.GetPyData(item)
        obj.on_use(evt)

    def on_node_pp(self, evt):
        item = self.GetSelection()
        obj = self.GetPyData(item)
        obj.on_html_view(evt)

    def on_del(self, evt):
        status_value = "none"
        try:
            item = self.GetSelection()
            if item:
                handler = self.GetPyData(item)
                status_value = handler.xml.get('status')
                name = handler.xml.get('name')
                parent_item = self.GetItemParent(item)
                while parent_item.IsOk() and status_value!="useful" and status_value!="useless":
                    try:
                        parent_handler = self.GetPyData(parent_item)
                        status_value = parent_handler.get('status')
                        name = parent_handler.get('name')
                        if status_value == "useless": break
                        elif status_value == "useful": break
                    except: status_value = "none"
                    parent_item = self.GetItemParent(parent_item)
                if status_value == "useful":
                    dlg = wx.MessageDialog(self, `name` + "  And everything beneath it are considered useful.  \n\nAre you sure you want to delete this item?",'Important Item',wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION)
                    if dlg.ShowModal() == wx.ID_YES: handler.delete()
                else: handler.delete()
        except:
            if self.GetSelection() == self.GetRootItem(): msg = wx.MessageDialog(None,"You can't delete the root item.","Delete Error",wx.OK)
            else: msg = wx.MessageDialog(None,"Unknown error deleting node.","Delete Error",wx.OK)
            msg.ShowModal()
            msg.Destroy()

    def on_about(self, evt):
        item = self.GetSelection()
        obj = self.GetPyData(item)
        text = str(obj.about())
        #about = MyAboutBox(self, obj.about())
        wx.MessageBox(text, 'About')#.ShowModal()
        #about.ShowModal()
        #about.Destroy()
    
    def on_send_to_map(self, evt):
        item = self.GetSelection()
        obj = self.GetPyData(item)
        if hasattr(obj,"on_send_to_map"): obj.on_send_to_map(evt)
    
    def insert_xml(self, txt):
        #Updated to allow safe merging of gametree files
        #without leaving an unusable and undeletable node.
        #                               -- Snowdog 8/03
        if not txt:
            wx.MessageBox("Import Failed: Invalid or missing node data")
            logger.general("Import Failed: Invalid or missing node data")
            return
        try: new_xml = XML(txt)
        except ExpatError:
            wx.MessageBox("Error Importing Node or Tree")
            logger.general("Error Importing Node or Tree")
            return
        if new_xml.tag == "gametree":
            for xml_child in new_xml: self.load_xml(xml_child, self.root)
            return
        if new_xml.tag == "tree":
            self.xml_root.append(new_xml.find('nodehandler'))
            for xml_child in new_xml: self.load_xml(xml_child, self.root)
            return
        self.xml_root.append(new_xml)
        self.load_xml(new_xml, self.root, self.root)
    
    def build_img_list(self):
        """make image list"""
        helper = img_helper()
        self.icons = { }
        self._imageList= wx.ImageList(16,16,False)
        icons_xml = parse(orpg.dirpath.dir_struct["icon"]+"icons.xml")
        for icon in icons_xml.getroot():
            key = icon.get("name")
            path = orpg.dirpath.dir_struct["icon"] + icon.get("file")
            img = helper.load_file(path)
            self.icons[key] = self._imageList.Add(img)
        self.SetImageList(self._imageList)

    def get_tree_map(self, parent):
        ## Could be a little cleaner ##
        family_tree = []
        test = parent
        while test != self.root:
            parent = self.GetItemText(test)
            test = self.GetItemParent(test)
            family_tree.append(parent)
        return family_tree
    
    def load_xml(self, xml_element, parent_node, prev_node=None, drag_drop=False):
        if parent_node == self.root:
            name = xml_element.get('name').replace(u'\xa0', ' ') #Required for XSLT sheets
            xml_element.set('name', name)
            self.tree_map[str(xml_element.get('name'))] = {}
            self.tree_map[str(xml_element.get('name'))]['node'] = xml_element
            xml_element.set('map', '')
        if parent_node != self.root:
            ## Loading XML seems to lag on Grids and Images need a cache for load speed ##
            family_tree = self.get_tree_map(parent_node)
            family_tree.reverse()
            map_str = '' #'!@'
            for member in family_tree: map_str += member +'::'
            map_str = map_str[:len(map_str)-2] #+'@!'
            xml_element.set('map', map_str)

        #add the first tree node
        i = 0
        name = xml_element.get("name")
        icon = xml_element.get("icon")
        if self.icons.has_key(icon): i = self.icons[icon]

        if prev_node:
            if prev_node == parent_node: new_tree_node = self.PrependItem(parent_node, name, i, i)
            else: new_tree_node = self.InsertItem(parent_node, prev_node, name, i, i)
        elif drag_drop:
            new_tree_node = self.InsertItemBefore(parent_node, 0, name, i)
        else: new_tree_node = self.AppendItem(parent_node, name, i, i)

        logger.debug("Node Added to tree")
        #create a nodehandler or continue loading xml into tree
        if xml_element.tag == "nodehandler":
            try:
                py_class = xml_element.get("class")
                logger.debug("nodehandler class: " + py_class)
                if not self.nodehandlers.has_key(py_class): raise Exception("Unknown Nodehandler for " + py_class)
                self.nodes[self.id] = self.nodehandlers[py_class](xml_element, new_tree_node)
                self.SetPyData(new_tree_node, self.nodes[self.id])
                logger.debug("Node Data set")
                bmp = self.nodes[self.id].get_scaled_bitmap(16,16)
                if bmp: self.cached_load_of_image(bmp,new_tree_node,)
                logger.debug("Node Icon loaded")
                self.id = self.id + 1
            except Exception, er:
                logger.exception(traceback.format_exc())
                # was deleted -- should we delete non-nodehandler nodes then?
                #self.Delete(new_tree_node)
                #parent = xml_dom._get_parentNode()
                #parent.removeChild(xml_dom)
        return new_tree_node
    
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

    def on_rclick(self, evt):
        pt = evt.GetPosition()
        (item, flag) = self.HitTest(pt)
        if item.IsOk():
            obj = self.GetPyData(item)
            self.SelectItem(item)
            if(isinstance(obj,core.node_handler)): obj.on_rclick(evt)
            else: self.PopupMenu(self.top_menu)
        else: self.PopupMenu(self.top_menu,pt)
    
    def on_ldclick(self, evt):
        self.rename_flag = 0
        pt = evt.GetPosition()
        (item, flag) = self.HitTest(pt)
        if item.IsOk():
            obj = self.GetPyData(item)
            self.SelectItem(item)
            if(isinstance(obj,core.node_handler)):
                if not obj.on_ldclick(evt):
                    action = settings.get_setting("treedclick")
                    if action == "use": obj.on_use(evt)
                    elif action == "design": obj.on_design(evt)
                    elif action == "print": obj.on_html_view(evt)
                    elif action == "chat": self.on_send_to_chat(evt)
    
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

    def traverse(self, root, function, data=None, recurse=True):
        child, cookie = self.GetFirstChild(root)
        while child.IsOk():
            function(child, data)
            if recurse: self.traverse(child, function, data)
            child, cookie = self.GetNextChild(root, cookie)
    
    def on_label_change(self, evt):
        item = evt.GetItem()
        txt = evt.GetLabel()
        self.was_labeling = 0
        self.rename_flag = 0
        if txt != "":
            obj = self.GetPyData(item)
            #obj.xml.set('name', txt)
            obj.rename(txt)
        else: evt.Veto()
    
    def on_label_begin(self, evt):
        if not self.rename_flag: evt.Veto()
        else:
            self.was_labeling = 1
            item = evt.GetItem()
            if item == self.GetRootItem(): evt.Veto()
    
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
    
    def __init__(self, parent, settings):
        wx.Dialog.__init__(self, parent, wx.ID_ANY, "Game Tree Properties")

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

    
    def on_ok(self,evt):
        settings.change("gametree",self.ctrls[CTRL_TREE_FILE].GetValue())
        settings.change("SaveGameTreeOnExit",str(self.ctrls[CTRL_YES].GetValue()))
        if self.ctrls[CTRL_USE].GetValue(): settings.change("treedclick","use")
        elif self.ctrls[CTRL_DESIGN].GetValue(): settings.change("treedclick","design")
        elif self.ctrls[CTRL_PRINT].GetValue(): settings.change("treedclick","print")
        elif self.ctrls[CTRL_CHAT].GetValue(): settings.change("treedclick","chat")
        self.EndModal(wx.ID_OK)
