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
# File: containers.py
# Author: Chris Davis
# Maintainer:
# Version:
#   $Id: containers.py,v Traipse 'Ornery-Orc' prof.ebral Exp $
#
# Description: The file contains code for the container nodehandlers
#


from core import *
from wx.lib.splitter import MultiSplitterWindow
from orpg.tools.orpg_log import logger
from orpg.orpgCore import component

##########################
##  base container
##########################

class container_handler(node_handler):
    """ should not be used! only a base class!
    <nodehandler name='?'  module='core' class='container_handler'  />
    """
    def __init__(self, xml, tree_node):
        node_handler.__init__(self, xml, tree_node)
        self.load_children()

    def load_children(self):
        for child_xml in self.xml: self.tree.load_xml(child_xml,self.mytree_node)

    def check_map_aware(self, treenode, evt):
        node = self.tree.GetPyData(treenode)
        if hasattr(node,"map_aware") and node.map_aware(): node.on_send_to_map(evt)

    def on_send_to_map(self, evt):
        self.tree.traverse(self.mytree_node, self.check_map_aware, evt) 

    def checkChildToMap(self, treenode, evt):
        node = self.tree.GetPyData(treenode)
        if hasattr(node,"map_aware") and node.map_aware(): self.mapcheck = True

    def checkToMapMenu(self):
        self.mapcheck = False
        self.tree.traverse(self.mytree_node, self.checkChildToMap)
        return self.mapcheck

    def on_drop(self,evt):
        drag_obj = self.tree.drag_obj
        if drag_obj == self or self.tree.is_parent_node(self.mytree_node,drag_obj.mytree_node): return
        opt = wx.MessageBox("Add node as child?","Container Node",wx.YES_NO|wx.CANCEL)
        prev_sib = self.tree.GetPrevSibling(drag_obj.mytree_node)
        if opt == wx.YES:
            drop_xml = self.tree.drag_obj.delete()
            self.xml.insert(0, drop_xml)
            self.tree.load_xml(drop_xml, self.mytree_node, drag_drop=True)
        elif opt == wx.NO: node_handler.on_drop(self,evt)

    def gen_html(self, treenode, evt):
        node = self.tree.GetPyData(treenode)
        self.html_str += "<p>" + node.tohtml()
        
    def tohtml(self):
        self.html_str = "<table border='1' ><tr><td>"
        self.html_str += "<b>"+self.xml.get("name") + "</b>"
        self.html_str += "</td></tr>\n"
        self.html_str += "<tr><td>"
        self.tree.traverse(self.mytree_node, self.gen_html, recurse=False)
        self.html_str += "</td></tr></table>"
        return self.html_str

    def get_size_constraint(self):
        return 2


##########################
## group node handler
##########################
class group_handler(container_handler):
    """ group nodehandler to be used as a placeholder for other nodehandlers.
        This handler will continue parsing child xml data.
        <nodehandler name='?'  module='core' class='group_handler'  />
    """
    def __init__(self, xml, tree_node):
        container_handler.__init__(self, xml, tree_node)

    def load_children(self):
        self.atts = None
        for child_xml in self.xml:
            if child_xml.tag == "group_atts": #having the group attributes as a child is bad!
                self.xml.remove(child_xml)
            elif child_xml: self.tree.load_xml(child_xml, self.mytree_node)
        if not self.xml.get('cols'): self.xml.set('cols', '1')
        if not self.xml.get('border'): self.xml.set('border', '1')

    def get_design_panel(self,parent):
        return group_edit_panel(parent,self)

    def on_use(self,evt):
        return

    def gen_html(self, treenode, evt):
        node = self.tree.GetPyData(treenode)
        if self.i  not in self.tdatas: self.tdatas[self.i] = ''
        self.tdatas[self.i] += "<P>" + node.tohtml()
        self.i += 1
        if self.i >= self.cols: self.i = 0

    def tohtml(self):
        cols = self.xml.get("cols")
        border = self.xml.get("border")
        self.html_str = "<table border='"+border+"' ><tr><td colspan='"+cols+"'>"
        self.html_str += "<font size=4>"+self.xml.get("name") + "</font>"
        self.html_str += "</td></tr>\n<tr>"
        self.cols = int(cols)
        self.i = 0
        self.tdatas = {}
        self.tree.traverse(self.mytree_node, self.gen_html, recurse=False)
        for td in self.tdatas: self.html_str += "<td valign='top' >" + self.tdatas[td] + "</td>\n";
        self.html_str += "</tr></table>"
        return self.html_str

GROUP_COLS = wx.NewId()
GROUP_BOR = wx.NewId()

class group_edit_panel(wx.Panel):
    def __init__(self, parent, handler):
        wx.Panel.__init__(self, parent, -1)
        self.handler = handler
        self.outline = wx.StaticBoxSizer(wx.StaticBox(self, -1, "Group"), wx.VERTICAL)

        sizer = wx.BoxSizer(wx.VERTICAL)
        self.text = {P_TITLE : wx.TextCtrl(self, P_TITLE, handler.xml.get('name')) }
        sizer.Add(wx.StaticText(self, -1, "Title:"), 0, wx.EXPAND)
        sizer.Add(self.text[P_TITLE], 0, wx.EXPAND)
        sizer.Add(wx.Size(10,10))

        radio_c = wx.RadioBox(self, GROUP_COLS, "Columns", choices=["1","2","3","4"])
        cols = handler.xml.get("cols")
        if cols != "": radio_c.SetSelection(int(cols)-1)

        radio_b = wx.RadioBox(self, GROUP_BOR, "Border", choices=["no","yes"])
        border = handler.xml.get("border")
        if border != "": radio_b.SetSelection(int(border))

        sizer.Add(radio_c, 0, wx.EXPAND)
        sizer.Add(wx.Size(10,10))
        sizer.Add(radio_b, 0, wx.EXPAND)

        self.outline.Add(sizer, 0)
        self.sizer = self.outline
        self.SetSizer(self.sizer)
        self.SetAutoLayout(True)
        self.Fit()
        parent.SetSize(self.GetBestSize())
        self.Bind(wx.EVT_TEXT, self.on_text, id=P_TITLE)
        self.Bind(wx.EVT_RADIOBOX, self.on_radio_box, id=GROUP_BOR)
        self.Bind(wx.EVT_RADIOBOX, self.on_radio_box, id=GROUP_COLS)

    def on_radio_box(self,evt):
        id = evt.GetId()
        index = evt.GetInt()
        if id == GROUP_COLS: self.handler.xml.set("cols",str(index+1))
        elif id == GROUP_BOR: self.handler.xml.set("border",str(index))

    def on_text(self,evt):
        id = evt.GetId()
        if id == P_TITLE:
            txt = self.text[id].GetValue()
            if txt != "":
                self.handler.xml.set('name',txt)
                self.handler.rename(txt)



##########################
## tabber node handler
##########################
class tabber_handler(container_handler):
    """ <nodehandler name='?'  module='containers' class='tabber_handler'  />"""

    def __init__(self, xml, tree_node):
        container_handler.__init__(self, xml, tree_node)

    def get_design_panel(self, parent):
        return tabbed_panel(parent, self, 1)

    def get_use_panel(self, parent):
        return tabbed_panel(parent, self, 0)


class tabbed_panel(orpgTabberWnd):
    def __init__(self, parent, handler, mode):
        orpgTabberWnd.__init__(self, parent, style=FNB.FNB_NO_X_BUTTON)
        self.handler = handler
        self.parent = parent
        if mode == 1: self.AddPage(tabbed_edit_panel(parent, handler), 'Tabber', False)
        handler.tree.traverse(handler.mytree_node, self.pick_panel, mode, False)
        parent.SetSize(self.GetBestSize())

    def pick_panel(self, treenode, mode):
        node = self.handler.tree.GetPyData(treenode)

        if mode == 1: panel = node.get_design_panel(self)
        else: panel = node.get_use_panel(self)
        name = node.xml.get("name")
        if name == None: ## Fixes broken 3e Inventory child
            if node.xml.tag == 'inventory':
                node.xml.set('name', 'Inventory')
                name = "Inventory"
                logger.info('A corrective action was take to a 3e PC Sheet', True)
                component.get('frame').TraipseSuiteWarn('item')
        if panel: self.AddPage(panel, name, False)

class tabbed_edit_panel(wx.Panel):
    def __init__(self, parent, handler):
        wx.Panel.__init__(self, parent, -1, style=FNB.FNB_NO_X_BUTTON)
        self.handler = handler
        self.parent = parent
        main_sizer = wx.StaticBoxSizer(wx.StaticBox(self, -1, "Tabber"), wx.VERTICAL)
        self.title = wx.TextCtrl(self, 1, handler.xml.get('name'))
        main_sizer.Add(wx.StaticText(self, -1, "Title:"), 0, wx.EXPAND)
        main_sizer.Add(self.title, 0, wx.EXPAND)
        self.SetSizer(main_sizer)
        self.SetAutoLayout(True)
        self.Fit()
        parent.SetSize(self.GetBestSize())
        self.Bind(wx.EVT_TEXT, self.on_text, id=1)

    def on_text(self,evt):
        txt = self.title.GetValue()
        if txt != "":
            self.handler.xml.set('name',txt)
            self.handler.rename(txt)


#################################
## Splitter container
#################################

class splitter_handler(container_handler):
    """ <nodehandler name='?'  module='containers' class='splitter_handler'  />"""

    def __init__(self,xml,tree_node):
        container_handler.__init__(self,xml,tree_node)

    def load_children(self):
        self.atts = None
        for child_xml in self.xml:
            if child_xml.tag == "splitter_atts": print 'splitter_atts exist!'; self.xml.remove(child_xml) #Same here!
            elif child_xml: self.tree.load_xml(child_xml,self.mytree_node)
        if not self.xml.get('horizontal'): self.xml.set('horizontal', '0')

    def get_design_panel(self,parent):
        return self.build_splitter_wnd(parent, 1)

    def get_use_panel(self,parent):
        return self.build_splitter_wnd(parent, 0)

    def on_drop(self,evt):
        drag_obj = self.tree.drag_obj
        container_handler.on_drop(self,evt)

    def build_splitter_wnd(self, parent, mode):
        self.parent = parent
        self.split = self.xml.get("horizontal")
        self.pane = splitter_panel(parent, self, mode)
        self.frame = self.pane.frame
        self.splitter = MultiSplitterWindow(self.pane, -1, 
                        style=wx.SP_LIVE_UPDATE|wx.SP_3DSASH|wx.SP_NO_XP_THEME)
        self.splitter.parent = self
        if self.split == '1': self.splitter.SetOrientation(wx.VERTICAL)
        else: self.splitter.SetOrientation(wx.HORIZONTAL)
        self.tree.traverse(self.mytree_node, self.doSplit, mode, False) 
        self.pane.sizer.Add(self.splitter, -1, wx.EXPAND)
        self.pane.SetAutoLayout(True)
        self.pane.Fit()
        parent.SetSize(self.pane.GetSize())
        return self.pane

    def doSplit(self, treenode, mode):
        node = self.tree.GetPyData(treenode)
        if mode == 1: tmp = node.get_design_panel(self.splitter)
        else: tmp = node.get_use_panel(self.splitter)
        if self.split == '1': sash = self.frame.GetSize()[1]/len(self.xml.findall('nodehandler'))
        else: sash = self.frame.GetSize()[0]/len(self.xml.findall('nodehandler'))
        self.splitter.AppendWindow(tmp, sash)

    def get_size_constraint(self):
        return 1

class splitter_panel(wx.Panel):
    def __init__(self, parent, handler, mode):
        wx.Panel.__init__(self, parent, -1)
        self.parent = parent
        self.handler = handler
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        if mode == 0: self.title = wx.StaticText(self, 1, handler.xml.get('name'))
        elif mode == 1: self.title = wx.TextCtrl(self, 1, handler.xml.get('name'))
        self.frame = self.GetParent()
        while self.frame.GetName() != 'frame':
            self.frame = self.frame.GetParent()

        if mode == 1:
            self.hozCheck = wx.CheckBox(self, -1, "Horizontal Split")
            hoz = self.handler.xml.get("horizontal")
            if hoz == '1': self.hozCheck.SetValue(True)
            else: self.hozCheck.SetValue(False)

        if mode == 1: self.sizer.Add(wx.StaticText(self, -1, "Title:"), 0, wx.EXPAND)
        self.sizer.Add(self.title, 0)
        if mode == 1: self.sizer.Add(self.hozCheck, 0, wx.EXPAND)
        self.sizer.Add(wx.Size(10,0))

        self.SetSizer(self.sizer)
        self.SetAutoLayout(True)
        self.Bind(wx.EVT_TEXT, self.on_text, id=1)
        if mode == 1: self.Bind(wx.EVT_CHECKBOX, self.on_check_box, id=self.hozCheck.GetId())

    def on_check_box(self,evt):
        state = self.hozCheck.GetValue()
        if state: self.handler.xml.set("horizontal", "1")
        else: self.handler.xml.set("horizontal", "0")

    def on_text(self,evt):
        txt = self.title.GetValue()
        if txt != "":
            self.handler.xml.set('name',txt)
            self.handler.rename(txt)

