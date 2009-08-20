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
#   $Id: containers.py,v 1.43 2007/08/08 19:17:17 digitalxero Exp $
#
# Description: The file contains code for the container nodehandlers
#


from core import *
from wx.lib.splitter import MultiSplitterWindow


##########################
##  base contiainer
##########################

class container_handler(node_handler):
    """ should not be used! only a base class!
    <nodehandler name='?'  module='core' class='container_handler'  />
    """
    def __init__(self,xml_dom,tree_node):
        node_handler.__init__(self,xml_dom,tree_node)
        self.load_children()

    def load_children(self):
        children = self.master_dom._get_childNodes()
        for c in children:
            self.tree.load_xml(c,self.mytree_node)

    def check_map_aware(self, obj, evt):
        if hasattr(obj,"map_aware") and obj.map_aware():
            obj.on_send_to_map(evt)


    def on_send_to_map(self, evt):
        child = self.tree.GetFirstChild(self.mytree_node)
        if child[0].IsOk():
            self.traverse(child[0], self.check_map_aware, 0, evt)


    def checkChildToMap(self, obj, evt):
        if hasattr(obj,"map_aware") and obj.map_aware():
            self.mapcheck = True

    def checkToMapMenu(self):
        self.mapcheck = False
        child = self.tree.GetFirstChild(self.mytree_node)
        if child[0].IsOk():
            self.traverse(child[0], self.checkChildToMap, 0, self.mapcheck)

        return self.mapcheck

    def on_drop(self,evt):
        drag_obj = self.tree.drag_obj
        if drag_obj == self or self.tree.is_parent_node(self.mytree_node,drag_obj.mytree_node):
            return
        opt = wx.MessageBox("Add node as child?","Container Node",wx.YES_NO|wx.CANCEL)
        if opt == wx.YES:
            xml_dom = self.tree.drag_obj.delete()
            xml_dom = self.master_dom.insertBefore(xml_dom,None)
            self.tree.load_xml(xml_dom, self.mytree_node)
            self.tree.Expand(self.mytree_node)
        elif opt == wx.NO:
            node_handler.on_drop(self,evt)

    def gen_html(self, obj, evt):
        self.html_str += "<p>" + obj.tohtml()

    def tohtml(self):
        self.html_str = "<table border=\"1\" ><tr><td>"
        self.html_str += "<b>"+self.master_dom.getAttribute("name") + "</b>"
        self.html_str += "</td></tr>\n"
        self.html_str += "<tr><td>"

        child = self.tree.GetFirstChild(self.mytree_node)
        self.traverse(child[0], self.gen_html, 0, None)

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
    def __init__(self,xml_dom,tree_node):
        container_handler.__init__(self,xml_dom,tree_node)

    def load_children(self):
        self.atts = None
        children = self.master_dom._get_childNodes()
        for c in children:
            if c._get_tagName() == "group_atts":
                self.atts = c
            else:
                self.tree.load_xml(c,self.mytree_node)
        if not self.atts:
            elem = self.xml.minidom.Element('group_atts')
            elem.setAttribute("cols","1")
            elem.setAttribute("border","1")
            self.atts = self.master_dom.appendChild(elem)

    def get_design_panel(self,parent):
        return group_edit_panel(parent,self)

    def on_use(self,evt):
        return

    def gen_html(self, obj, evt):
        if self.i  not in self.tdatas:
            self.tdatas[self.i] = ''
        self.tdatas[self.i] += "<P>" + obj.tohtml()
        self.i += 1
        if self.i >= self.cols:
            self.i = 0

    def tohtml(self):
        cols = self.atts.getAttribute("cols")
        border = self.atts.getAttribute("border")
        self.html_str = "<table border=\""+border+"\" ><tr><td colspan=\""+cols+"\">"
        self.html_str += "<font size=4>"+self.master_dom.getAttribute("name") + "</font>"
        self.html_str += "</td></tr>\n<tr>"

        self.cols = int(cols)
        self.i = 0
        self.tdatas = {}

        child = self.tree.GetFirstChild(self.mytree_node)
        if child[0].IsOk():
            self.traverse(child[0], self.gen_html, 0, None)

        for td in self.tdatas:
            self.html_str += "<td valign=\"top\" >" + self.tdatas[td] + "</td>\n";
        self.html_str += "</tr></table>"
        return self.html_str

GROUP_COLS = wx.NewId()
GROUP_BOR = wx.NewId()

class group_edit_panel(wx.Panel):
    def __init__(self, parent, handler):
        wx.Panel.__init__(self, parent, -1)
        self.handler = handler
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.text = {   P_TITLE : wx.TextCtrl(self, P_TITLE, handler.master_dom.getAttribute('name'))
                      }
        sizer.Add(wx.StaticText(self, -1, "Title:"), 0, wx.EXPAND)
        sizer.Add(self.text[P_TITLE], 0, wx.EXPAND)
        sizer.Add(wx.Size(10,10))

        radio_c = wx.RadioBox(self, GROUP_COLS, "Columns", choices=["1","2","3","4"])
        cols = handler.atts.getAttribute("cols")
        if cols != "":
            radio_c.SetSelection(int(cols)-1)

        radio_b = wx.RadioBox(self, GROUP_BOR, "Border", choices=["no","yes"])
        border = handler.atts.getAttribute("border")
        if border != "":
            radio_b.SetSelection(int(border))

        sizer.Add(radio_c, 0, wx.EXPAND)
        sizer.Add(wx.Size(10,10))
        sizer.Add(radio_b, 0, wx.EXPAND)

        self.sizer = sizer
        self.outline = wx.StaticBox(self,-1,"Group")
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
        if id == GROUP_COLS:
            self.handler.atts.setAttribute("cols",str(index+1))
        elif id == GROUP_BOR:
            self.handler.atts.setAttribute("border",str(index))

    def on_text(self,evt):
        id = evt.GetId()
        if id == P_TITLE:
            txt = self.text[id].GetValue()
            if txt != "":
                self.handler.master_dom.setAttribute('name',txt)
                self.handler.rename(txt)



##########################
## tabber node handler
##########################
class tabber_handler(container_handler):
    """ <nodehandler name='?'  module='containers' class='tabber_handler'  />"""

    def __init__(self,xml_dom,tree_node):
        container_handler.__init__(self,xml_dom,tree_node)

    def get_design_panel(self,parent):
        return tabbed_panel(parent,self,1)

    def get_use_panel(self,parent):
        return tabbed_panel(parent,self,2)


class tabbed_panel(orpgTabberWnd):
    def __init__(self, parent, handler, mode):
        orpgTabberWnd.__init__(self, parent, style=FNB.FNB_NO_X_BUTTON)
        self.handler = handler
        self.parent = parent
        tree = self.handler.tree
        child = tree.GetFirstChild(handler.mytree_node)
        if child[0].IsOk():
            handler.traverse(child[0], self.pick_panel, 0, mode, False)

        parent.SetSize(self.GetBestSize())

    def pick_panel(self, obj, mode):
        if mode == 1:
            panel = obj.get_design_panel(self)
        else:
            panel = obj.get_use_panel(self)

        name = obj.master_dom.getAttribute("name")

        if panel:
            self.AddPage(panel, name, False)

#################################
## Splitter container
#################################

class splitter_handler(container_handler):
    """ <nodehandler name='?'  module='containers' class='splitter_handler'  />"""

    def __init__(self,xml_dom,tree_node):
        container_handler.__init__(self,xml_dom,tree_node)

    def load_children(self):
        self.atts = None
        children = self.master_dom._get_childNodes()
        for c in children:
            if c._get_tagName() == "splitter_atts":
                self.atts = c
            else:
                self.tree.load_xml(c,self.mytree_node)
        if not self.atts:
            elem = self.xml.minidom.Element('splitter_atts')
            elem.setAttribute("horizontal","0")
            self.atts = self.master_dom.appendChild(elem)

    def get_design_panel(self,parent):
        return self.build_splitter_wnd(parent, 1)

    def get_use_panel(self,parent):
        return self.build_splitter_wnd(parent, 2)

    def on_drop(self,evt):
        drag_obj = self.tree.drag_obj
        container_handler.on_drop(self,evt)

    def build_splitter_wnd(self, parent, mode):
        self.split = self.atts.getAttribute("horizontal")

        self.pane = splitter_panel(parent, self)

        self.splitter = MultiSplitterWindow(self.pane, -1, style=wx.SP_LIVE_UPDATE|wx.SP_3DSASH|wx.SP_NO_XP_THEME)

        if self.split == '1':
            self.splitter.SetOrientation(wx.VERTICAL)
        else:
            self.splitter.SetOrientation(wx.HORIZONTAL)

        self.bestSizex = -1
        self.bestSizey = -1

        cookie = 0
        (child, cookie) = self.tree.GetFirstChild(self.mytree_node)
        if child.IsOk():
            self.traverse(child, self.doSplit, 0, mode, False)

        self.pane.sizer.Add(self.splitter, 1, wx.EXPAND)


        if mode != 1:
            self.pane.hozCheck.Hide()

        self.pane.SetSize((self.bestSizex, self.bestSizey))
        self.pane.Layout()
        parent.SetSize(self.pane.GetSize())
        return self.pane

    def doSplit(self, obj, mode):
        if mode == 1:
            tmp = obj.get_design_panel(self.splitter)
        else:
            tmp = obj.get_use_panel(self.splitter)

        if self.split == '1':
            sash = tmp.GetBestSize()[1]+1
            self.bestSizey += sash+11
            if self.bestSizex < tmp.GetBestSize()[0]:
                self.bestSizex = tmp.GetBestSize()[0]+10
        else:
            sash = tmp.GetBestSize()[0]+1
            self.bestSizex += sash
            if self.bestSizey < tmp.GetBestSize()[1]:
                self.bestSizey = tmp.GetBestSize()[1]+31

        self.splitter.AppendWindow(tmp, sash)

    def get_size_constraint(self):
        return 1

class splitter_panel(wx.Panel):
    def __init__(self, parent, handler):
        wx.Panel.__init__(self, parent, -1)
        self.handler = handler
        sizer = wx.BoxSizer(wx.VERTICAL)

        self.hozCheck = wx.CheckBox(self, -1, "Horizontal Split")
        hoz = self.handler.atts.getAttribute("horizontal")

        if hoz == '1':
            self.hozCheck.SetValue(True)
            #self.splitsize = wx.BoxSizer(wx.HORIZONTAL)
        else:
            self.hozCheck.SetValue(False)
            #self.splitsize = wx.BoxSizer(wx.VERTICAL)

        sizer.Add(self.hozCheck, 0, wx.EXPAND)
        sizer.Add(wx.Size(10,0))
        #sizer.Add(self.splitsize,  1, wx.EXPAND)

        self.sizer = sizer
        self.SetSizer(self.sizer)
        self.SetAutoLayout(True)

        self.Bind(wx.EVT_CHECKBOX, self.on_check_box, id=self.hozCheck.GetId())

    def on_check_box(self,evt):
        state = self.hozCheck.GetValue()
        if state:
            self.handler.atts.setAttribute("horizontal", "1")
        else:
            self.handler.atts.setAttribute("horizontal", "0")
