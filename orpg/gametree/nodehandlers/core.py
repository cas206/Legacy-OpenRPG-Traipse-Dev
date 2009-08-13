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
# File: core.py
# Author: Chris Davis
# Maintainer:
# Version:
#   $Id: core.py,v 1.49 2007/12/07 20:39:48 digitalxero Exp $
#
# Description: The file contains code for the core nodehanlers
#

__version__ = "$Id: core.py,v 1.49 2007/12/07 20:39:48 digitalxero Exp $"

from nodehandler_version import NODEHANDLER_VERSION
try:
    from orpg.orpg_windows import *
    import orpg.dirpath
    from orpg.orpg_xml import *
    from orpg.orpgCore import open_rpg
    import webbrowser
    from orpg.mapper import map
    import os
except:
    import wx




#html defaults
TH_BG = "#E9E9E9"
##########################
## base node handler
##########################
class node_handler:
    """ Base nodehandler with virtual functions and standard implmentations """
    def __init__(self,xml_dom,tree_node):
        self.master_dom = xml_dom
        self.mytree_node = tree_node
        self.tree = open_rpg.get_component('tree')
        self.frame = open_rpg.get_component('frame')
        self.chat = open_rpg.get_component('chat')
        self.xml = open_rpg.get_component('xml')
        self.drag = True
        self.myeditor = None # designing
        self.myviewer = None # prett print
        self.mywindow = None # using
        # call version hook
        self.on_version(self.master_dom.getAttribute("version"))
        # set to current version
        self.master_dom.setAttribute("version",NODEHANDLER_VERSION)
        # null events

    def on_version(self,old_version):
        ## added version control code here or implement a new on_version in your derived class.
        ## always call the base class on_version !
        pass

    def on_rclick(self,evt):
        self.tree.do_std_menu(evt,self)

    def on_ldclick(self,evt):
        return 0

    def traverse(self, traverseroot, function, cookie=0, event=None, recursive=True):
        """ walk tree control """
        if traverseroot.IsOk():
            # step in subtree if there are items or ...
            if self.tree.ItemHasChildren(traverseroot) and recursive:
                firstchild, cookie = self.tree.GetFirstChild(traverseroot)
                obj = self.tree.GetPyData(firstchild)
                function(obj, event)
                self.traverse(firstchild, function, cookie, event, recursive)

            # ... loop siblings
            obj = self.tree.GetPyData(traverseroot)
            function(obj, event)

            child = self.tree.GetNextSibling(traverseroot)
            if child.IsOk():
                self.traverse(child, function, cookie, event, recursive)


    def usefulness(self,text):
        if text=="useful":
            self.master_dom.setAttribute('status',"useful")
        elif text=="useless":
            self.master_dom.setAttribute('status',"useless")
        elif text=="indifferent":
            self.master_dom.setAttribute('status',"indifferent")

    def on_design(self,evt):
        try:
            self.myeditor.Show()
            self.myeditor.Raise()
        except:
            del self.myeditor
            if self.create_designframe():
                self.myeditor.Show()
                self.myeditor.Raise()
            else:
                return
        wx.CallAfter(self.myeditor.Layout)


    def create_designframe(self):
        title = self.master_dom.getAttribute('name') + " Editor"
        self.myeditor = wx.Frame(None, -1, title)
        self.myeditor.Freeze()
        if wx.Platform == '__WXMSW__':
            icon = wx.Icon(orpg.dirpath.dir_struct["icon"] + 'grid.ico', wx.BITMAP_TYPE_ICO)
            self.myeditor.SetIcon(icon)
            del icon

        self.myeditor.panel = self.get_design_panel(self.myeditor)
        if self.myeditor.panel == None:
            self.myeditor.Destroy()
            return False
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.myeditor.panel, 1, wx.EXPAND)

        self.myeditor.SetSizer(sizer)
        self.myeditor.SetAutoLayout(True)

        (x, y) = self.myeditor.GetSize()
        if x < 400:
            x = 400
        if y < 400:
            y = 400

        self.myeditor.SetSize((x, y))
        self.myeditor.Layout()
        self.myeditor.Thaw()

        return True

    def on_use(self,evt):
        try:
            self.mywindow.Show()
            self.mywindow.Raise()
        except:
            del self.mywindow
            if self.create_useframe():
                self.mywindow.Show()
                self.mywindow.Raise()
            else:
                return
        wx.CallAfter(self.mywindow.Layout)


    def create_useframe(self):
        caption = self.master_dom.getAttribute('name')
        self.mywindow = wx.Frame(None, -1, caption)
        self.mywindow.Freeze()

        if wx.Platform == '__WXMSW__':
            icon = wx.Icon(orpg.dirpath.dir_struct["icon"] + 'note.ico', wx.BITMAP_TYPE_ICO)
            self.mywindow.SetIcon(icon)
            del icon
        self.mywindow.panel = self.get_use_panel(self.mywindow)
        if self.mywindow.panel == None:
            self.mywindow.Destroy()
            return False
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.mywindow.panel, 2, wx.EXPAND)

        self.mywindow.SetSizer(sizer)
        self.mywindow.SetAutoLayout(True)

        (x, y) = self.mywindow.GetSize()
        if x < 400:
            x = 400
        if y < 400:
            y = 400

        self.mywindow.SetSize((x, y))
        self.mywindow.Layout()
        self.mywindow.Thaw()

        return True


    def on_html_view(self,evt):
        try:
            self.myviewer.Raise()
        except:
            caption = self.master_dom.getAttribute('name')
            self.myviewer = wx.Frame(None, -1, caption)
            if wx.Platform == '__WXMSW__':
                icon = wx.Icon(orpg.dirpath.dir_struct["icon"] + 'grid.ico', wx.BITMAP_TYPE_ICO)
                self.myviewer.SetIcon(icon)
                del icon
            self.myviewer.panel = self.get_html_panel(self.myviewer)
            self.myviewer.Show()

    def map_aware(self):
        return 0

    def can_clone(self):
        return 1;

    def on_del(self,evt):
        print "on del"

    def on_new_data(self,xml_dom):
        pass

    def get_scaled_bitmap(self,x,y):
        return None

    def on_send_to_map(self,evt):
        pass

    def on_send_to_chat(self,evt):
        self.chat.ParsePost(self.tohtml(),True,True)

    def on_drop(self,evt):
        drag_obj = self.tree.drag_obj
        if drag_obj == self or self.tree.is_parent_node(self.mytree_node,drag_obj.mytree_node):
            return
        #if self.is_my_child(self.mytree_node,drag_obj.mytree_node):
        #    return
        xml_dom = self.tree.drag_obj.delete()
        parent = self.master_dom._get_parentNode()
        xml_dom = parent.insertBefore(xml_dom,self.master_dom)
        parent_node = self.tree.GetItemParent(self.mytree_node)
        prev_sib = self.tree.GetPrevSibling(self.mytree_node)
        if not prev_sib.IsOk():
            prev_sib = parent_node
        self.tree.load_xml(xml_dom, parent_node, prev_sib)

    def toxml(self,pretty=0):
        return toxml(self.master_dom,pretty)

    def tohtml(self):
        return self.master_dom.getAttribute("name")

    def delete(self):
        """ removes the tree_node and xml_node, and returns the removed xml_node """

        self.tree.Delete(self.mytree_node)
        parent = self.master_dom._get_parentNode()
        return parent.removeChild(self.master_dom)

    def rename(self,name):
        if len(name):
            self.tree.SetItemText(self.mytree_node,name)
            self.master_dom.setAttribute('name', name)

    def change_icon(self,icon):
        self.master_dom.setAttribute("icon",icon)
        self.tree.SetItemImage(self.mytree_node, self.tree.icons[icon])
        self.tree.SetItemImage(self.mytree_node, self.tree.icons[icon], wx.TreeItemIcon_Selected)
        self.tree.Refresh()

    def on_save(self,evt):
        f = wx.FileDialog(self.tree,"Select a file", orpg.dirpath.dir_struct["user"],"","XML files (*.xml)|*.xml",wx.SAVE)
        if f.ShowModal() == wx.ID_OK:
            type = f.GetFilterIndex()
            if f.GetPath()[:len(f.GetPath())-4] != '.xml': file = open(f.GetPath()+'.xml',"w")
            else: file = open(f.GetPath(),"w")
            file.write(self.toxml(1))
            file.close()
        f.Destroy()

    def get_design_panel(self,parent):
        return None

    def get_use_panel(self,parent):
        return None

    def get_html_panel(self,parent):
        html_str = "<html><body bgcolor=\"#FFFFFF\" >"+self.tohtml()+"</body></html>"
        wnd = wx.html.HtmlWindow(parent,-1)
        html_str = self.chat.ParseDice(html_str)
	wnd.SetPage(html_str)
        return wnd

    def get_size_constraint(self):
        return 0

    def about(self):
        html_str = "<b>"+ self.master_dom.getAttribute('class')
        html_str += " Applet</b><br />by Chris Davis<br />chris@rpgarchive.com"
        return html_str

P_TITLE = 10
P_BODY = 20
class text_edit_panel(wx.Panel):
    def __init__(self, parent, handler):
        wx.Panel.__init__(self, parent, -1)
        self.handler = handler
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.text = {   P_TITLE : wx.TextCtrl(self, P_TITLE, handler.master_dom.getAttribute('name')),
                        P_BODY : html_text_edit(self,P_BODY,handler.text._get_nodeValue(),self.on_text)
                      }
        #P_BODY : wx.TextCtrl(self, P_BODY,handler.text._get_nodeValue(), style=wx.TE_MULTILINE)

        sizer.Add(wx.StaticText(self, -1, "Title:"), 0, wx.EXPAND)
        sizer.Add(self.text[P_TITLE], 0, wx.EXPAND)
        sizer.Add(wx.StaticText(self, -1, "Text Body:"), 0, wx.EXPAND)
        sizer.Add(self.text[P_BODY], 1, wx.EXPAND)
        self.sizer = sizer
        self.outline = wx.StaticBox(self,-1,"Text Block")
        self.Bind(wx.EVT_TEXT, self.on_text, id=P_TITLE)

    def on_text(self,evt):
        id = evt.GetId()
        if id == P_TITLE:
            txt = self.text[id].GetValue()
            #  The following block strips out 8-bit characters
            u_txt = ""
            bad_txt_found = 0
            for c in txt:
                if ord(c) < 128:
                    u_txt += c
                else:
                    bad_txt_found = 1
            if bad_txt_found:
                wx.MessageBox("Some non 7-bit ASCII characters found and stripped","Warning!")
            txt = u_txt
            if txt != "":
                self.handler.master_dom.setAttribute('name',txt)
                self.handler.rename(txt)
        elif id == P_BODY:
            txt = self.text[id].get_text()
            u_txt = ""
            bad_txt_found = 0
            for c in txt:
                if ord(c) < 128:
                    u_txt += c
                else:
                    bad_txt_found = 1

            if bad_txt_found:
                wx.MessageBox("Some non 7-bit ASCII characters found and stripped","Warning!")
            txt = u_txt
            self.handler.text._set_nodeValue(txt)



##########################
## node loader
##########################
class node_loader(node_handler):
    """ clones childe node and insert it at top of tree
        <nodehandler name='?'  module='core' class='node_loader'  />
    """
    def __init__(self,xml_dom,tree_node):
        node_handler.__init__(self,xml_dom,tree_node)

    def on_rclick(self,evt):
        pass

    def on_ldclick(self,evt):
        title = self.master_dom.getAttribute('name')
        new_node = self.master_dom._get_firstChild()
        new_node = new_node.cloneNode(True)
        child = self.tree.master_dom._get_firstChild()
        new_node = self.tree.master_dom.insertBefore(new_node,child)
        tree_node = self.tree.load_xml(new_node,self.tree.root,self.tree.root)
        obj = self.tree.GetPyData(tree_node)
        return 1
        #obj.on_design(None)

##########################
## file loader
##########################

class file_loader(node_handler):
    """ loads file and insert into game tree
        <nodehandler name='?'  module='core' class='file_loader'  >
        <file name="file_name.xml" />
        </nodehandler>
    """
    def __init__(self,xml_dom,tree_node):
        node_handler.__init__(self,xml_dom,tree_node)
        self.file_node = self.master_dom._get_firstChild()
        self.frame = open_rpg.get_component('frame')

    def on_ldclick(self,evt):
        file_name = self.file_node.getAttribute("name")
        self.tree.insert_xml(open(orpg.dirpath.dir_struct["nodes"] + file_name,"r").read())
        return 1

    def on_design(self,evt):
        tlist = ['Title','File Name']
        vlist = [self.master_dom.getAttribute("name"),
                  self.file_node.getAttribute("name")]
        dlg = orpgMultiTextEntry(self.tree.GetParent(),tlist,vlist,"File Loader Edit")
        if dlg.ShowModal() == wx.ID_OK:
            vlist = dlg.get_values()
            self.file_node.setAttribute('name', vlist[1])
            self.master_dom.setAttribute('name', vlist[0])
            self.tree.SetItemText(self.mytree_node,vlist[0])
        dlg.Destroy()

##########################
## URL loader
##########################

class url_loader(node_handler):
    """ loads file from url and insert into game tree
        <nodehandler name='?'  module='core' class='url_loader'  >
        <file name="http://file_name.xml" />
        </nodehandler>
    """
    def __init__(self,xml_dom,tree_node):
        node_handler.__init__(self,xml_dom,tree_node)
        self.file_node = self.master_dom._get_firstChild()
        self.frame = open_rpg.get_component('frame')

    def on_ldclick(self,evt):
        file_name = self.file_node.getAttribute("url")
        file = urllib.urlopen(file_name)
        self.tree.insert_xml(file.read())
        return 1

    def on_design(self,evt):
        tlist = ['Title','URL']
        print "design filename",self.master_dom.getAttribute('name')
        vlist = [self.master_dom.getAttribute("name"),
                 self.file_node.getAttribute("url")]
        dlg = orpgMultiTextEntry(self.tree.GetParent(),tlist,vlist,"File Loader Edit")
        if dlg.ShowModal() == wx.ID_OK:
            vlist = dlg.get_values()
            self.file_node.setAttribute('url', vlist[1])
            self.master_dom.setAttribute('name', vlist[0])
            self.tree.SetItemText(self.mytree_node,vlist[0])
        dlg.Destroy()


##########################
## minature map loader
##########################
class min_map(node_handler):
    """ clones childe node and insert it at top of tree
        <nodehandler name='?'  module='core' class='min_map'  />
    """
    def __init__(self,xml_dom,tree_node):
        node_handler.__init__(self,xml_dom,tree_node)
        self.map = open_rpg.get_component('map')
        self.mapdata = self.master_dom._get_firstChild()

    def on_ldclick(self,evt):
        self.map.new_data(toxml(self.mapdata))
        return 1
