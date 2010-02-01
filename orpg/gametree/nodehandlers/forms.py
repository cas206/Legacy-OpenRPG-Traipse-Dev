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
# File: forms.py
# Author: Chris Davis
# Maintainer:
# Version:
#   $Id: forms.py,v Traipse 'Ornery-Orc' prof.ebral Exp $
#
# Description: The file contains code for the form based nodehanlers
#

__version__ = "$Id: forms.py,v Traipse 'Ornery-Orc' prof.ebral Exp $"

from containers import *
import orpg.minidom as minidom
from orpg.orpg_xml import xml
from wx.lib.scrolledpanel import ScrolledPanel
from orpg.tools.settings import settings
from orpg.tools.InterParse import Parse

def bool2int(b):
    #in wxPython 2.5+, evt.Checked() returns True or False instead of 1.0 or 0.
    #by running the results of that through this function, we convert it.
    #if it was an int already, nothing changes. The difference between 1.0
    #and 1, i.e. between ints and floats, is potentially dangerous when we
    #use str() on it, but it seems to work fine right now.
    if b: return 1
    else: return 0

#################################
## form container
#################################

class form_handler(container_handler):
    """
            <nodehandler name='?'  module='forms' class='form_handler'  >
            <form width='100' height='100' />
            </nodehandler>
    """
    def __init__(self,xml,tree_node):
        container_handler.__init__(self, xml, tree_node)

    def load_children(self):
        self.atts = None
        for child_xml in self.xml:
            if child_xml.tag == "form": self.xml.remove(child_xml)
            elif child_xml: self.tree.load_xml(child_xml, self.mytree_node)
        if not self.xml.get('width'): self.xml.set('width', '400')
        if not self.xml.get('height'): self.xml.set('height', '600')

    def get_design_panel(self,parent):
        return form_edit_panel(parent,self)

    def get_use_panel(self,parent):
        return form_panel(parent,self)

    def on_drop(self,evt):
        # make sure its a contorl node
        container_handler.on_drop(self,evt)

class form_panel(ScrolledPanel):
    def __init__(self, parent, handler):
        ScrolledPanel.__init__(self, parent, wx.ID_ANY, style=wx.NO_BORDER|wx.VSCROLL|wx.HSCROLL)
        self.height = int(handler.xml.get("height"))
        self.width = int(handler.xml.get("width"))
        self.SetSize((0,0))
        self.handler = handler
        self.parent = parent
        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
        handler.tree.traverse(handler.mytree_node, self.create_child_wnd, None, False)
        self.SetSizer(self.main_sizer)
        self.SetAutoLayout(True)
        self.SetupScrolling()
        parent.SetSize(self.GetSize())
        self.Fit()

    def SetSize(self, xy):
        (x, y) = self.GetSize()
        (nx, ny) = xy
        if x < nx:
            x = nx+10
        y += ny+11
        ScrolledPanel.SetSize(self, (x, y))

    def create_child_wnd(self, treenode, evt):
        node = self.handler.tree.GetPyData(treenode)
        panel = node.get_use_panel(self)
        size = node.get_size_constraint()
        if panel:
            self.main_sizer.Add(panel, size, wx.EXPAND)
            self.main_sizer.Add(wx.Size(10,10))

F_HEIGHT = wx.NewId()
F_WIDTH = wx.NewId()
class form_edit_panel(wx.Panel):
    def __init__(self, parent, handler):
        wx.Panel.__init__(self, parent, -1)
        self.handler = handler
        sizer = wx.StaticBoxSizer(wx.StaticBox(self, -1, "Form Properties"), wx.VERTICAL)
        wh_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.text = {   P_TITLE : wx.TextCtrl(self, P_TITLE, handler.xml.get('name')),
                        F_HEIGHT : wx.TextCtrl(self, F_HEIGHT, handler.xml.get('height')),
                        F_WIDTH : wx.TextCtrl(self, F_WIDTH, handler.xml.get('width'))
                      }

        wh_sizer.Add(wx.StaticText(self, -1, "Width:"), 0, wx.ALIGN_CENTER)
        wh_sizer.Add(wx.Size(10,10))
        wh_sizer.Add(self.text[F_WIDTH], 0, wx.EXPAND)
        wh_sizer.Add(wx.Size(10,10))
        wh_sizer.Add(wx.StaticText(self, -1, "Height:"), 0, wx.ALIGN_CENTER)
        wh_sizer.Add(wx.Size(10,10))
        wh_sizer.Add(self.text[F_HEIGHT], 0, wx.EXPAND)

        sizer.Add(wx.StaticText(self, -1, "Title:"), 0, wx.EXPAND)
        sizer.Add(self.text[P_TITLE], 0, wx.EXPAND)
        sizer.Add(wx.Size(10,10))
        sizer.Add(wh_sizer,0,wx.EXPAND)

        self.SetSizer(sizer)
        self.SetAutoLayout(True)
        self.Fit()
        parent.SetSize(self.GetBestSize())

        self.Bind(wx.EVT_TEXT, self.on_text, id=P_TITLE)
        self.Bind(wx.EVT_TEXT, self.on_text, id=F_HEIGHT)
        self.Bind(wx.EVT_TEXT, self.on_text, id=F_WIDTH)

    def on_text(self,evt):
        id = evt.GetId()
        txt = self.text[id].GetValue()
        if not len(txt): return
        if id == P_TITLE:
            self.handler.xml.set('name',txt)
            self.handler.rename(txt)
        elif id == F_HEIGHT or id == F_WIDTH:
            try: int(txt)
            except: return 0
            if id == F_HEIGHT: self.handler.xml.set("height",txt)
            elif id == F_WIDTH: self.handler.xml.set("width",txt)

##########################
## control handler
##########################
class control_handler(node_handler):
    """ A nodehandler for form controls.
        <nodehandler name='?' module='forms' class='control_handler' />
    """
    def __init__(self, xml, tree_node):
        node_handler.__init__(self, xml, tree_node)

    def get_size_constraint(self):
        return 0

##########################
## textctrl handler
##########################
    #
    # Updated by Snowdog (April 2003)
    #   Now includes Raw Send Mode (like the chat macro uses)
    #   and an option to remove the title from text when sent
    #   to the chat in the normal non-chat macro mode.
    #
class textctrl_handler(node_handler):
    """ <nodehandler class="textctrl_handler" module="form" name="">
           <text multiline='0' send_button='0' raw_mode='0' hide_title='0'>Text In Node</text>
        </nodehandler>
    """
    def __init__(self,xml,tree_node):
        node_handler.__init__(self,xml,tree_node)
        self.text_elem = self.xml.find('text')
        if self.text_elem.get("send_button") == "": self.text_elem.set("send_button","0")
        if self.text_elem.get("raw_mode") == "": self.text_elem.set("raw_mode","0")
        if self.text_elem.get("hide_title") == "": self.text_elem.set("hide_title","0")

    def get_design_panel(self,parent):
        return textctrl_edit_panel(parent,self)

    def get_use_panel(self,parent):
        return text_panel(parent,self)

    def get_size_constraint(self):
        return int(self.text_elem.get("multiline",0))

    def is_multi_line(self):
        return int(self.text_elem.get("multiline",0))

    def is_raw_send(self):
        return int(self.text_elem.get("raw_mode",0))

    def is_hide_title(self):
        return int(self.text_elem.get("hide_title",0))

    def has_send_button(self):
        return int(self.text_elem.get("send_button",0))

    def tohtml(self):
        txt = self.get_value()
        txt = string.replace(txt,'\n',"<br />")
        if not self.is_hide_title(): txt = "<b>"+self.xml.get("name")+":</b> "+txt
        return txt

    def get_value(self):
        return self.text_elem.text

    def set_value(self, new_value):
        self.text_elem.text = str(new_value)

FORM_TEXT_CTRL = wx.NewId()
FORM_SEND_BUTTON = wx.NewId()

class text_panel(wx.Panel):
    def __init__(self, parent, handler):
        wx.Panel.__init__(self, parent, -1)
        self.chat = handler.chat
        self.handler = handler
        if handler.is_multi_line():
            text_style = wx.TE_MULTILINE
            sizer_style = wx.EXPAND
            sizer = wx.BoxSizer(wx.VERTICAL)
        else:
            sizer_style = wx.ALIGN_CENTER
            text_style = 0
            sizer = wx.BoxSizer(wx.HORIZONTAL)

        txt = handler.get_value()
        if txt == None: txt = ''
        self.text = wx.TextCtrl(self, FORM_TEXT_CTRL, txt, style=text_style)
        sizer.Add(wx.StaticText(self, -1, handler.xml.get('name')+": "), 0, sizer_style)
        sizer.Add(wx.Size(5,0))
        sizer.Add(self.text, 1, sizer_style)

        if handler.has_send_button(): sizer.Add(wx.Button(self, FORM_SEND_BUTTON, "Send"), 0, sizer_style)

        self.sizer = sizer
        self.SetSizer(sizer)
        self.SetAutoLayout(True)

        parent.SetSize(self.GetBestSize())
        self.Bind(wx.EVT_TEXT, self.on_text, id=FORM_TEXT_CTRL)
        self.Bind(wx.EVT_BUTTON, self.on_send, id=FORM_SEND_BUTTON)

    def on_text(self, evt):
        txt = self.text.GetValue()
        #txt = strip_text(txt) ##Does not seem to exist.
        self.handler.text_elem.text = txt

    def on_send(self, evt):
        txt = self.text.GetValue()
        txt = Parse.NodeMap(txt, self.handler.xml)
        txt = Parse.NodeParent(txt, self.handler.xml.get('map'))
        if not self.handler.is_raw_send():
            Parse.Post(self.handler.tohtml(), True, True)
            return 1
        actionlist = txt.split("\n")
        for line in actionlist:
            if(line != ""):
                if line[0] != "/": ## it's not a slash command
                    Parse.Post(line, True, True)
                else:
                    action = line
                    self.chat.chat_cmds.docmd(action)
        return 1

F_MULTI = wx.NewId()
F_SEND_BUTTON = wx.NewId()
F_RAW_SEND = wx.NewId()
F_HIDE_TITLE = wx.NewId()
F_TEXT = wx.NewId()
T_BUT_REF = wx.NewId()

class textctrl_edit_panel(wx.Panel):
    def __init__(self, parent, handler):
        wx.Panel.__init__(self, parent, -1)
        self.handler = handler
        self.parent = parent
        sizer = wx.StaticBoxSizer(wx.StaticBox(self, -1, "Text Properties"), wx.VERTICAL)

        self.title = wx.TextCtrl(self, P_TITLE, handler.xml.get('name'))
        self.multi = wx.CheckBox(self, F_MULTI, " Multi-Line")
        self.multi.SetValue(handler.is_multi_line())
        self.raw_send = wx.CheckBox(self, F_RAW_SEND, " Send as Macro")
        self.raw_send.SetValue(handler.is_raw_send())
        self.hide_title = wx.CheckBox(self, F_HIDE_TITLE, " Hide Title")
        self.hide_title.SetValue(handler.is_hide_title())
        self.send_button = wx.CheckBox(self, F_SEND_BUTTON, " Send Button")
        self.send_button.SetValue(handler.has_send_button())
        button_ref = wx.Button(self, T_BUT_REF, "Reference")

        sizer.Add(wx.StaticText(self, P_TITLE, "Title:"), 0, wx.EXPAND)
        sizer.Add(self.title, 0, wx.EXPAND)
        sizer.Add(wx.Size(10,10))
        sizer.Add(self.multi, 0, wx.EXPAND)
        sizer.Add(self.raw_send, 0, wx.EXPAND)
        sizer.Add(self.hide_title, 0, wx.EXPAND)
        sizer.Add(self.send_button, 0 , wx.EXPAND)
        sizer.Add(button_ref, 0)
        sizer.Add(wx.Size(10,10))
        if handler.is_multi_line():
            sizer_style = wx.EXPAND
            text_style = wx.TE_MULTILINE
            multi = 1
        else:
            sizer_style=wx.EXPAND
            text_style = 0
            multi = 0
        self.text = wx.TextCtrl(self, F_TEXT, handler.get_value(),style=text_style)
        sizer.Add(wx.Size(5,0))
        sizer.Add(self.text, multi, sizer_style)
        self.SetSizer(sizer)
        self.SetAutoLayout(True)

        self.Bind(wx.EVT_TEXT, self.on_text, id=P_TITLE)
        self.Bind(wx.EVT_TEXT, self.on_text, id=F_TEXT)
        self.Bind(wx.EVT_CHECKBOX, self.on_button, id=F_MULTI)
        self.Bind(wx.EVT_CHECKBOX, self.on_raw_button, id=F_RAW_SEND)
        self.Bind(wx.EVT_CHECKBOX, self.on_hide_button, id=F_HIDE_TITLE)
        self.Bind(wx.EVT_CHECKBOX, self.on_send_button, id=F_SEND_BUTTON)
        self.Bind(wx.EVT_BUTTON, self.on_reference, id=T_BUT_REF)
        self.parent.Bind(wx.EVT_CLOSE, self.tree_failsafe)

    ## EZ_Tree Core TaS - Prof.Ebral ##
    def on_reference(self, evt, car=None):
        self.do_tree = wx.Frame(self, -1, 'EZ Tree')
        self.ez_tree = orpg.gametree.gametree
        self.temp_wnd = self.ez_tree.game_tree(self.do_tree, self.ez_tree.EZ_REF)
        self.temp_wnd.Bind(wx.EVT_LEFT_DCLICK, self.on_ldclick)
        component.get('tree_fs').save_tree(settings.get("gametree"))
        self.temp_wnd.load_tree(settings.get("gametree"))
        self.do_tree.Show()

    def tree_failsafe(self, evt):
        self.parent.Destroy()
        component.add('tree', component.get('tree_fs')) ## Backup

    def get_grid_ref(self, obj, complete):
        self.temp_wnd.Freeze()
        self.grid_ref = complete
        self.mini_grid = wx.Frame(self, -1, 'EZ Tree Mini Grid')
        self.temp_grid = obj.get_use_panel(self.mini_grid)
        self.temp_grid.grid.Bind(wx.grid.EVT_GRID_CELL_LEFT_DCLICK, self.on_grid_ldclick)
        self.mini_grid.Show()

    def on_grid_ldclick(self, evt):
        complete = self.grid_ref
        row = str(evt.GetRow()+1)
        col = str(evt.GetCol()+1)
        complete = complete[:len(complete)-2] + '::'+'('+row+','+col+')'+complete[len(complete)-2:]
        self.text.AppendText(complete); self.on_text(evt)
        self.mini_grid.Destroy()

    def on_ldclick(self, evt):
        self.rename_flag = 0
        pt = evt.GetPosition()
        (item, flag) = self.temp_wnd.HitTest(pt)
        if item.IsOk():
            obj = self.temp_wnd.GetPyData(item)
            self.temp_wnd.SelectItem(item)
            start = self.handler.xml.get('map').split('::')
            end = obj.xml.get('map').split('::')
            if obj.xml.get('class') not in ['rpg_grid_handler', 'textctrl_handler']: do = 'None'
            elif end[0] == '' or start[0] != end[0]: do = 'Root'
            elif start == end: do = 'Child'
            elif start != end: do = 'Parent'
            if do == 'Root':
                complete = "!@"
                for e in end: 
                    if e != '': complete += e +'::'
                complete = complete + obj.xml.get('name') + '@!'
            elif do == 'Parent':
                while start[0] == end[0]:
                    del end[0], start[0]
                    if len(start) == 0 or len(end) == 0: break
                complete = "!#"
                for e in end: complete += e +'::'
                complete = complete + obj.xml.get('name') + '#!'
            elif do == 'Child':
                while start[0] == end[0]:
                    del end[0], start[0]
                    if len(start) == 0 or len(end) == 0: break
                complete = "!!"
                for e in end: complete += e +'::'
                complete = complete + obj.xml.get('name') + '!!'
            if do != 'None': 
                if obj.xml.get('class') == 'rpg_grid_handler': 
                    self.get_grid_ref(obj, complete)
                else: self.text.AppendText(complete); self.on_text(evt)
        self.do_tree.Destroy()
        if do == 'None':
            wx.MessageBox('Invalid Reference', 'Error')
    #####                        #####

    def on_text(self,evt):
        id = evt.GetId()
        if id == P_TITLE:
            txt = self.title.GetValue()
            if not len(txt): return
            self.handler.xml.set('name',txt)
            self.handler.rename(txt)
        if id == F_TEXT:
            txt = self.text.GetValue()
            #txt = strip_text(txt) ##Does not seem to exist. 
            self.handler.text_elem.text = txt

    def on_button(self,evt):
        self.handler.text_elem.set("multiline",str(bool2int(evt.Checked())))

    def on_raw_button(self,evt):
        self.handler.text_elem.set("raw_mode",str(bool2int(evt.Checked())))

    def on_hide_button(self,evt):
        self.handler.text_elem.set("hide_title",str(bool2int(evt.Checked())))

    def on_send_button(self,evt):
        self.handler.text_elem.set("send_button",str(bool2int(evt.Checked())))


#######################
## listbox handler
#######################
    #
    # Updated by Snowdog (April 2003)
    #   Now includesan option to remove the title from
    #   text when sent to the chat.
    #
L_DROP = 0
L_LIST = 1
L_RADIO = 2
L_CHECK = 3
L_ROLLER = 4

class listbox_handler(node_handler):
    """
    <nodehandler class="listbox_handler" module="forms" name="">
        <list type="1"  send_button='0' hide_title='0'>
                <option value="" selected="" >Option Text I</option>
                <option value="" selected="" >Option Text II</option>
        </list>
    </nodehandler>
    """
    def __init__(self,xml,tree_node):
        node_handler.__init__(self,xml,tree_node)
        self.list_reload()
        #print xml
        #print self.tree.GetItemParent(tree_node)
        if self.list.get("send_button") == "": self.list.set("send_button","0")
        if self.list.get("hide_title") == "": self.list.set("hide_title","0")
        if self.list.get("raw_mode") == "": self.list.set("raw_mode","0")

    def list_reload(self):
        self.list = self.xml.find('list')
        self.options = self.list.findall('option')
        self.captions = []
        for opt in self.options:
            if opt.get('caption') == None: opt.set('caption', '')
            self.captions.append(opt.get('caption'))

    def get_design_panel(self,parent):
        return listbox_edit_panel(parent,self)

    def get_use_panel(self,parent):
        return listbox_panel(parent,self)

    def get_type(self):
        return int(self.list.get("type"))

    def set_type(self,type):
        self.list.set("type",str(type))

    def is_hide_title(self):
        return int(self.list.get("hide_title", 0))

    def is_raw_send(self):
        return int(self.list.get("raw_mode",0))

    # single selection methods
    def get_selected_node(self):
        for opt in self.options:
            if opt.get("selected") == "1": return opt
        return None

    def get_selected_index(self):
        i = 0
        for opt in self.options:
            if opt.get("selected") == "1": return i
            i += 1
        return 0

    def get_selected_text(self):
        node = self.get_selected_node()
        if node: return node.text
        else: return ""

    # mult selection methods
    def get_selections(self):
        opts = []
        for opt in self.options:
            if opt.get("selected") == "1": opts.append(opt)
        return opts

    def get_selections_text(self):
        opts = []
        for opt in self.options:
            if opt.get("selected") == "1": opts.append(opt.text)
        return opts

    def get_selections_index(self):
        opts = []
        i = 0
        for opt in self.options:
            if opt.get("selected") == "1": opts.append(i)
            i += 1
        return opts

    # setting selection method
    def set_selected_node(self,index,selected=1):
        if self.get_type() != L_CHECK: self.clear_selections()
        self.options[index].set("selected", str(bool2int(selected)))

    def clear_selections(self):
        for opt in self.options: opt.set("selected","0")

    # misc methods
    def get_options(self):
        opts = []
        for opt in self.options: opts.append(opt.text)
        return opts

    def get_captions(self):
        captions = []
        for opt in self.options: captions.append(opt.get("caption"))
        self.captions = captions
        return captions

    def get_option(self, index):
        return self.options[index].text

    def get_caption(self, index):
        captions = self.get_captions()
        return captions[index] or ''

    def add_option(self, caption, value):
        elem = Element('option')
        elem.set("value","0")
        elem.set('caption', caption)
        elem.set("selected","0")
        elem.text = value
        self.list.append(elem)
        self.list_reload()

    def remove_option(self,index):
        self.list.remove(self.options[index])
        self.list_reload()

    def edit_option(self, index, value):
        self.options[index].text = value

    def edit_caption(self, index, value):
        self.options[index].set('caption', value)
        self.captions[index] = value

    def has_send_button(self):
        if self.list.get("send_button") == '0': return False
        else: return True

    def get_size_constraint(self):
        if self.get_type() == L_DROP: return 0
        else: return 1

    def tohtml(self):
        opts = self.get_selections_text()
        text = ""
        if not self.is_hide_title(): text = "<b>"+self.xml.get("name")+":</b> "
        comma = ", "
        text += comma.join(opts)
        return text

    def get_value(self):
        return "\n".join(self.get_selections_text())

    def on_send_to_chat(self, evt):
        txt = self.get_selected_text()
        txt = Parse.NodeMap(txt, self.xml)
        txt = Parse.NodeParent(txt, self.xml.get('map'))
        if not self.is_raw_send():
            Parse.Post(self.tohtml(), True, True)
            return 1
        actionlist = self.get_selections_text()
        for line in actionlist:
            line = Parse.NodeMap(line, self.xml)
            line = Parse.NodeParent(line, self.xml.get('map'))
            if(line != ""):
                if line[0] != "/": ## it's not a slash command
                    Parse.Post(line, True, True)
                else:
                    action = line
                    self.chat.chat_cmds.docmd(action)
        return 1


F_LIST = wx.NewId()
F_SEND = wx.NewId()


class listbox_panel(wx.Panel):
    def __init__(self, parent, handler):
        wx.Panel.__init__(self, parent, -1)
        self.handler = handler
        self.chat = handler.chat
        opts = []
        values = handler.get_options()
        captions = handler.get_captions()
        for value in values:
            if captions[values.index(value)] != '': opts.append(captions[values.index(value)])
            else: opts.append(value)
        cur_opt = handler.get_selected_text()
        type = handler.get_type()
        label = handler.xml.get('name')

        if type == L_DROP:
            self.list = wx.ComboBox(self, F_LIST, cur_opt, choices=opts, style=wx.CB_READONLY)
            if self.list.GetSize()[0] > 200:
                self.list.Destroy()
                self.list = wx.ComboBox(self, F_LIST, cur_opt, size=(200, -1), choices=opts, style=wx.CB_READONLY)
        elif type == L_LIST: self.list = wx.ListBox(self,F_LIST,choices=opts)
        elif type == L_RADIO: self.list = wx.RadioBox(self,F_LIST,label,choices=opts,majorDimension=3)
        elif type == L_CHECK:
            self.list = wx.CheckListBox(self,F_LIST,choices=opts)
            self.set_checks()

        for i in handler.get_selections_text():
            if type == L_DROP: self.list.SetValue( i )
            else: self.list.SetStringSelection( i )
        if type == L_DROP: sizer = wx.BoxSizer(wx.HORIZONTAL)
        else: sizer = wx.BoxSizer(wx.VERTICAL)

        if type != L_RADIO:
            sizer.Add(wx.StaticText(self, -1, label+": "), 0, wx.EXPAND)
            sizer.Add(wx.Size(5,0))
        sizer.Add(self.list, 1, wx.EXPAND)
        if handler.has_send_button():
            sizer.Add(wx.Button(self, F_SEND, "Send"), 0, wx.EXPAND)
            self.Bind(wx.EVT_BUTTON, self.handler.on_send_to_chat, id=F_SEND)
        self.sizer = sizer
        self.SetSizer(sizer)
        self.SetAutoLayout(True)
        self.Fit()
        parent.SetSize(self.GetBestSize())

        if type == L_DROP: self.Bind(wx.EVT_COMBOBOX, self.on_change, id=F_LIST)
        elif type == L_LIST: self.Bind(wx.EVT_LISTBOX, self.on_change, id=F_LIST)
        elif type == L_RADIO: self.Bind(wx.EVT_RADIOBOX, self.on_change, id=F_LIST)
        elif type == L_CHECK:self.Bind(wx.EVT_CHECKLISTBOX, self.on_check, id=F_LIST)
        self.type = type

    def on_change(self,evt):
        self.handler.set_selected_node(self.list.GetSelection())

    def on_check(self,evt):
        for i in xrange(self.list.GetCount()): self.handler.set_selected_node(i, bool2int(self.list.IsChecked(i)))

    def set_checks(self):
        for i in self.handler.get_selections_index(): self.list.Check(i)


BUT_ADD = wx.NewId()
BUT_REM = wx.NewId()
BUT_REF = wx.NewId()
BUT_EDIT = wx.NewId()
F_TYPE = wx.NewId()
F_NO_TITLE = wx.NewId()
LIST_CTRL = wx.NewId()

class listbox_edit_panel(wx.Panel):
    def __init__(self, parent, handler):
        wx.Panel.__init__(self, parent, -1)
        self.handler = handler
        self.parent = parent
        sizer = wx.StaticBoxSizer(wx.StaticBox(self, -1, "List Box Properties"), wx.VERTICAL)

        self.text = wx.TextCtrl(self, P_TITLE, handler.xml.get('name'))
        self.listbox = wx.ListCtrl(self, LIST_CTRL, style=wx.LC_REPORT)
        self.listbox.InsertColumn(0, 'Caption')
        self.listbox.InsertColumn(1, 'Value')
        self.listbox.SetColumnWidth(0, 75)
        self.listbox.SetColumnWidth(1, 300)
        self.reload_options()

        opts = ['Drop Down', 'List Box', 'Radio Box', 'Check List']
        self.type_radios = wx.RadioBox(self,F_TYPE,"List Type",choices=opts)
        self.type_radios.SetSelection(handler.get_type())

        self.send_button = wx.CheckBox(self, F_SEND_BUTTON, " Send Button")
        self.send_button.SetValue(handler.has_send_button())

        self.raw_send = wx.CheckBox(self, F_RAW_SEND, " Send as Macro")
        self.raw_send.SetValue(handler.is_raw_send())

        self.hide_title = wx.CheckBox(self, F_NO_TITLE, " Hide Title")
        self.hide_title.SetValue(handler.is_hide_title())

        but_sizer = wx.BoxSizer(wx.HORIZONTAL)
        but_sizer.Add(wx.Button(self, BUT_ADD, "Add"), 1, wx.EXPAND)
        but_sizer.Add(wx.Size(10,10))
        but_sizer.Add(wx.Button(self, BUT_EDIT, "Edit"), 1, wx.EXPAND)
        but_sizer.Add(wx.Size(10,10))
        but_sizer.Add(wx.Button(self, BUT_REM, "Remove"), 1, wx.EXPAND)

        sizer.Add(wx.StaticText(self, -1, "Title:"), 0, wx.EXPAND)
        sizer.Add(self.text, 0, wx.EXPAND)
        sizer.Add(wx.Size(10,10))
        sizer.Add(self.type_radios, 0, wx.EXPAND)
        sizer.Add(wx.Size(10,10))
        sizer.Add(self.send_button, 0 , wx.EXPAND)
        sizer.Add(self.hide_title, 0, wx.EXPAND)
        sizer.Add(self.raw_send, 0, wx.EXPAND)
        sizer.Add(wx.Size(10,10))
        sizer.Add(wx.StaticText(self, -1, "Options:"), 0, wx.EXPAND)
        sizer.Add(self.listbox,1,wx.EXPAND);
        sizer.Add(but_sizer,0,wx.EXPAND)

        self.SetSizer(sizer)
        self.SetAutoLayout(True)
        self.Fit()
        parent.SetSize(self.GetBestSize())

        self.Bind(wx.EVT_TEXT, self.on_text, id=P_TITLE)
        self.Bind(wx.EVT_BUTTON, self.on_edit, id=BUT_EDIT)
        self.Bind(wx.EVT_BUTTON, self.on_remove, id=BUT_REM)
        self.Bind(wx.EVT_BUTTON, self.on_add, id=BUT_ADD)
        self.Bind(wx.EVT_RADIOBOX, self.on_type, id=F_TYPE)
        self.Bind(wx.EVT_CHECKBOX, self.on_hide_button, id=F_NO_TITLE)
        self.Bind(wx.EVT_CHECKBOX, self.on_send_button, id=F_SEND_BUTTON)
        self.Bind(wx.EVT_CHECKBOX, self.on_raw_button, id=F_RAW_SEND)

    def on_type(self,evt):
        self.handler.set_type(evt.GetInt())

    def on_add(self,evt):
        self.dlg = wx.Frame(self, -1, 'Text', size=(300,150))
        edit_panel = wx.Panel(self.dlg, -1)
        sizer = wx.GridBagSizer(1, 1)
        edit_panel.SetSizer(sizer)
        caption_text = wx.StaticText(edit_panel, -1, 'Caption')
        self.caption_entry = wx.TextCtrl(edit_panel, -1, '')
        value_text = wx.StaticText(edit_panel, -1, 'Value') 
        self.value_entry = wx.TextCtrl(edit_panel, -1, '')
        button_ok = wx.Button(edit_panel, wx.ID_OK)
        button_cancel = wx.Button(edit_panel, wx.ID_CANCEL)
        button_ref = wx.Button(edit_panel, BUT_REF, "Reference")
        sizer.Add(caption_text, (0,0))
        sizer.Add(self.caption_entry, (0,1), span=(1,4), flag=wx.EXPAND)
        sizer.Add(value_text, (1,0))
        sizer.Add(self.value_entry, (1,1), span=(1,4), flag=wx.EXPAND)
        sizer.Add(button_ok, (3,0))
        sizer.Add(button_cancel, (3,1))
        sizer.Add(button_ref, (3,2), flag=wx.EXPAND)
        sizer.AddGrowableCol(3)
        sizer.AddGrowableRow(2)
        self.dlg.SetSize((275, 125))
        self.dlg.SetMinSize((275, 125))
        self.dlg.Layout()
        self.Bind(wx.EVT_BUTTON, self.on_reference, id=BUT_REF)
        self.Bind(wx.EVT_BUTTON, self.on_add_option, id=wx.ID_OK)
        self.Bind(wx.EVT_BUTTON, self.on_edit_cancel, id=wx.ID_CANCEL)
        self.dlg.Show()

    def on_add_option(self, evt):
        self.handler.add_option(self.caption_entry.GetValue(), self.value_entry.GetValue())
        self.reload_options()
        self.dlg.Destroy()
        component.add('tree', component.get('tree_fs')) ## Backup
        return

    ## EZ_Tree Core TaS - Prof.Ebral ##
    def on_reference(self, evt, car=None):
        self.do_tree = wx.Frame(self, -1, 'EZ Tree')
        self.ez_tree = orpg.gametree.gametree
        self.temp_wnd = self.ez_tree.game_tree(self.do_tree, self.ez_tree.EZ_REF)
        self.temp_wnd.Bind(wx.EVT_LEFT_DCLICK, self.on_ldclick)
        component.get('tree_fs').save_tree(settings.get("gametree"))
        self.temp_wnd.load_tree(settings.get("gametree"))
        self.do_tree.Show()

    def get_grid_ref(self, obj, complete):
        self.temp_wnd.Freeze()
        self.grid_ref = complete
        self.mini_grid = wx.Frame(self, -1, 'EZ Tree Grid')
        self.temp_grid = obj.get_use_panel(self.mini_grid)
        self.temp_grid.grid.Bind(wx.grid.EVT_GRID_CELL_LEFT_DCLICK, self.on_grid_ldclick)
        self.mini_grid.Show()

    def on_grid_ldclick(self, evt):
        complete = self.grid_ref
        row = str(evt.GetRow()+1)
        col = str(evt.GetCol()+1)
        complete = complete[:len(complete)-2] + '::'+'('+row+','+col+')'+complete[len(complete)-2:]
        self.value_entry.AppendText(complete)
        self.mini_grid.Destroy()

    def on_ldclick(self, evt):
        self.rename_flag = 0
        pt = evt.GetPosition()
        (item, flag) = self.temp_wnd.HitTest(pt)
        if item.IsOk():
            obj = self.temp_wnd.GetPyData(item)
            self.temp_wnd.SelectItem(item)
            start = self.handler.xml.get('map').split('::')
            end = obj.xml.get('map').split('::')
            if obj.xml.get('class') not in ['rpg_grid_handler', 'textctrl_handler']: do = 'None'
            elif end[0] == '' or start[0] != end[0]: do = 'Root'
            elif start == end: do = 'Child'
            elif start != end: do = 'Parent'
            if do == 'Root':
                complete = "!@"
                for e in end: 
                    if e != '': complete += e +'::'
                complete = complete + obj.xml.get('name') + '@!'
            elif do == 'Parent':
                while start[0] == end[0]:
                    del end[0], start[0]
                    if len(start) == 0 or len(end) == 0: break
                complete = "!#"
                for e in end: complete += e +'::'
                complete = complete + obj.xml.get('name') + '#!'
            elif do == 'Child':
                while start[0] == end[0]:
                    del end[0], start[0]
                    if len(start) == 0 or len(end) == 0: break
                complete = "!!"
                for e in end: complete += e +'::'
                complete = complete + obj.xml.get('name') + '!!'
            if do != 'None': 
                if obj.xml.get('class') == 'rpg_grid_handler': 
                    self.get_grid_ref(obj, complete)
                else: self.value_entry.AppendText(complete); self.reload_options()
        self.do_tree.Destroy()
        if do == 'None':
            wx.MessageBox('Invalid Reference', 'Error')
    #####                        #####

    def on_edit_ok(self, evt):
        self.handler.edit_caption(self.index, self.caption_entry.GetValue())
        self.handler.edit_option(self.index, self.value_entry.GetValue())
        self.reload_options()
        self.dlg.Destroy()
        component.add('tree', component.get('tree_fs')) ## Backup
        return

    def on_edit_cancel(self, evt):
        self.dlg.Destroy()
        component.add('tree', component.get('tree_fs')) ## Backup
        return

    def on_remove(self,evt):
        index = self.listbox.GetFocusedItem()
        if index >= 0:
            self.handler.remove_option(index)
            self.reload_options()

    def on_edit(self,evt):
        self.index = self.listbox.GetFocusedItem()
        if self.index >= 0:
            self.dlg = wx.Frame(self, -1, 'Text', size=(300,150))
            edit_panel = wx.Panel(self.dlg, -1)
            sizer = wx.GridBagSizer(1, 2)
            edit_panel.SetSizer(sizer)
            caption_text = wx.StaticText(edit_panel, -1, 'Caption')
            self.caption_entry = wx.TextCtrl(edit_panel, -1, self.handler.get_caption(self.index))
            value_text = wx.StaticText(edit_panel, -1, 'Value') 
            self.value_entry = wx.TextCtrl(edit_panel, -1, self.handler.get_option(self.index))
            button_ok = wx.Button(edit_panel, wx.ID_OK)
            button_cancel = wx.Button(edit_panel, wx.ID_CANCEL)
            button_ref = wx.Button(edit_panel, BUT_REF, "Reference")
            sizer.Add(caption_text, (0,0))
            sizer.Add(self.caption_entry, (0,1), span=(1,4), flag=wx.EXPAND)
            sizer.Add(value_text, (1,0))
            sizer.Add(self.value_entry, (1,1), span=(1,4), flag=wx.EXPAND)
            sizer.Add(button_ok, (3,0))
            sizer.Add(button_cancel, (3,1))
            sizer.Add(button_ref, (3,2), flag=wx.EXPAND)
            sizer.AddGrowableCol(3)
            sizer.AddGrowableRow(2)
            self.dlg.SetSize((275, 125))
            self.dlg.SetMinSize((275, 125))
            self.dlg.Layout()
            self.Bind(wx.EVT_BUTTON, self.on_reference, id=BUT_REF)
            self.Bind(wx.EVT_BUTTON, self.on_edit_ok, id=wx.ID_OK)
            self.Bind(wx.EVT_BUTTON, self.on_edit_cancel, id=wx.ID_CANCEL)
            self.dlg.Show()

    def reload_options(self):
        self.listbox.DeleteAllItems()
        values = self.handler.get_options()
        captions = self.handler.get_captions()
        for index in range(len(values)):
            self.listbox.Append((captions[index], values[index]))

    def on_text(self,evt):
        id = evt.GetId()
        txt = self.text.GetValue()
        if not len(txt): return
        if id == P_TITLE:
            self.handler.xml.set('name',txt)
            self.handler.rename(txt)

    def on_send_button(self,evt):
        self.handler.list.set("send_button", str( bool2int(evt.Checked()) ))

    def on_hide_button(self,evt):
        self.handler.list.set("hide_title", str( bool2int(evt.Checked()) ))

    def on_raw_button(self,evt):
        self.handler.list.set("raw_mode",str(bool2int(evt.Checked())))


###############################
## link image handlers
###############################

class link_handler(node_handler):
    """ A nodehandler for URLs. Will open URL in a wxHTMLFrame
        <nodehandler name='?' module='forms' class='link_handler' >
                <link  href='http//??.??'  />
        </nodehandler >
    """
    def __init__(self,xml,tree_node):
        node_handler.__init__(self,xml,tree_node)
        self.link = self.xml[0]

    def on_use(self,evt):
        href = self.link.get("href")
        wb = webbrowser.get()
        wb.open(href)

    def get_design_panel(self,parent):
        return link_edit_panel(parent,self)

    def get_use_panel(self,parent):
        return link_panel(parent,self)

    def tohtml(self):
        href = self.link.get("href")
        title = self.xml.get("name")
        return "<a href='"+href+"' >"+title+"</a>"

class link_panel(wx.StaticText):
    def __init__(self,parent,handler):
        self.handler = handler
        label = handler.xml.get('name')
        wx.StaticText.__init__(self,parent,-1,label)
        self.SetForegroundColour(wx.BLUE)
        self.Bind(wx.EVT_LEFT_DOWN, self.handler.on_use)

P_URL = wx.NewId()

class link_edit_panel(wx.Panel):
    def __init__(self, parent, handler):
        wx.Panel.__init__(self, parent, -1)
        self.handler = handler
        sizer = wx.StaticBoxSizer(wx.StaticBox(self, -1, "Link Properties"), wx.VERTICAL)

        self.text = {}
        self.text[P_TITLE] = wx.TextCtrl(self, P_TITLE, handler.xml.get('name'))
        self.text[P_URL] = wx.TextCtrl(self, P_URL, handler.link.get('href'))

        sizer.Add(wx.StaticText(self, -1, "Title:"), 0, wx.EXPAND)
        sizer.Add(self.text[P_TITLE], 0, wx.EXPAND)
        sizer.Add(wx.Size(10,10))
        sizer.Add(wx.StaticText(self, -1, "URL:"), 0, wx.EXPAND)
        sizer.Add(self.text[P_URL], 0, wx.EXPAND)
        self.SetSizer(sizer)
        self.Bind(wx.EVT_TEXT, self.on_text, id=P_TITLE)
        self.Bind(wx.EVT_TEXT, self.on_text, id=P_URL)

    def on_text(self,evt):
        id = evt.GetId()
        txt = self.text[id].GetValue()
        if not len(txt): return
        if id == P_TITLE:
            self.handler.xml.set('name',txt)
            self.handler.rename(txt)
        elif id == P_URL: self.handler.link.set('href',txt)

##########################
## webimg node handler
##########################
class webimg_handler(node_handler):
    """ A nodehandler for URLs. Will open URL in a wxHTMLFrame
        <nodehandler name='?' module='forms' class='webimg_handler' >
                <link  href='http//??.??'  />
        </nodehandler >
    """
    def __init__(self,xml,tree_node):
        node_handler.__init__(self,xml,tree_node)
        self.link = self.xml[0]

    def get_design_panel(self,parent):
        return link_edit_panel(parent,self)

    def get_use_panel(self,parent):
        img = img_helper().load_url(self.link.get("href"))
        if not img is None: return wx.StaticBitmap(parent,-1,img,size= wx.Size(img.GetWidth(),img.GetHeight()))
        return wx.EmptyBitmap(1, 1)

    def tohtml(self):
        href = self.link.get("href")
        title = self.xml.get("name")
        return "<img src='"+href+"' alt="+title+" >"
