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
#   $Id: forms.py,v 1.53 2007/04/21 23:00:51 digitalxero Exp $
#
# Description: The file contains code for the form based nodehanlers
#

__version__ = "$Id: forms.py,v 1.53 2007/04/21 23:00:51 digitalxero Exp $"

from containers import *
import wx.lib.scrolledpanel

def bool2int(b):
    #in wxPython 2.5+, evt.Checked() returns True or False instead of 1.0 or 0.
    #by running the results of that through this function, we convert it.
    #if it was an int already, nothing changes. The difference between 1.0
    #and 1, i.e. between ints and floats, is potentially dangerous when we
    #use str() on it, but it seems to work fine right now.
    if b:
        return 1
    else:
        return 0

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
        container_handler.__init__(self,xml,tree_node)

    def load_children(self):
        self.atts = None
        for child_xml in self.xml:
            if child_xml.tag == "form":
                self.atts = child_xml
            else:
                self.tree.load_xml(child_xml,self.mytree_node)
        if not self.atts:
            self.atts = ET.Element('form')
            self.atts.set("width","400")
            self.atts.set("height","600")
            self.xml.append(self.atts)

    def get_design_panel(self,parent):
        return form_edit_panel(parent,self)

    def get_use_panel(self,parent):
        return form_panel(parent,self)

    def on_drop(self,evt):
        # make sure its a contorl node
        container_handler.on_drop(self,evt)


class form_panel(wx.lib.scrolledpanel.ScrolledPanel):
    def __init__(self, parent, handler):
        wx.lib.scrolledpanel.ScrolledPanel.__init__(self, parent, wx.ID_ANY, style=wx.NO_BORDER|wx.VSCROLL|wx.HSCROLL)
        self.height = int(handler.atts.get("height"))
        self.width = int(handler.atts.get("width"))


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
        wx.lib.scrolledpanel.ScrolledPanel.SetSize(self, (x, y))


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
                        F_HEIGHT : wx.TextCtrl(self, F_HEIGHT, handler.atts.get('height')),
                        F_WIDTH : wx.TextCtrl(self, F_WIDTH, handler.atts.get('width'))
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
            try:
                int(txt)
            except:
                return 0
            if id == F_HEIGHT:
                self.handler.atts.set("height",txt)
            elif id == F_WIDTH:
                self.handler.atts.set("width",txt)





##########################
## control handler
##########################
class control_handler(node_handler):
    """ A nodehandler for form controls.
        <nodehandler name='?' module='forms' class='control_handler' />
    """
    def __init__(self,xml,tree_node):
        node_handler.__init__(self,xml,tree_node)

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
        if self.text_elem.get("send_button") == "":
            self.text_elem.set("send_button","0")
        if self.text_elem.get("raw_mode") == "":
            self.text_elem.set("raw_mode","0")
        if self.text_elem.get("hide_title") == "":
            self.text_elem.set("hide_title","0")

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
        if not self.is_hide_title():
            txt = "<b>"+self.xml.get("name")+":</b> "+txt
        return txt

    def get_value(self):
        return getText(self.text_elem)

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
##        if self.handler.tree.ContainsReference(txt):
##            txt = self.handler.tree.ReplaceReferences(txt, False)
##            text_style |= wx.TE_READONLY
        
        self.text = wx.TextCtrl(self, FORM_TEXT_CTRL, txt, style=text_style)
        sizer.Add(wx.StaticText(self, -1, handler.xml.get('name')+": "), 0, sizer_style)
        sizer.Add(wx.Size(5,0))
        sizer.Add(self.text, 1, sizer_style)

        if handler.has_send_button():
            sizer.Add(wx.Button(self, FORM_SEND_BUTTON, "Send"), 0, sizer_style)

        self.sizer = sizer
        self.SetSizer(sizer)
        self.SetAutoLayout(True)

        parent.SetSize(self.GetBestSize())
        self.Bind(wx.EVT_TEXT, self.on_text, id=FORM_TEXT_CTRL)
        self.Bind(wx.EVT_BUTTON, self.on_send, id=FORM_SEND_BUTTON)

    def on_text(self,evt):
        txt = self.text.GetValue()
        txt = strip_text(txt)
        self.handler.text_elem.text = txt

    def on_send(self,evt):
        txt = self.text.GetValue()
        if not self.handler.is_raw_send():
            #self.chat.ParsePost(self.tohtml(),True,True)
            self.chat.ParsePost(self.handler.tohtml(),True,True)
            return 1
        actionlist = txt.split("\n")
        for line in actionlist:
            if(line != ""):
                if line[0] != "/": ## it's not a slash command
                    self.chat.ParsePost(line,True,True)
                else:
                    action = line
                    self.chat.chat_cmds.docmd(action)
        return 1

F_MULTI = wx.NewId()
F_SEND_BUTTON = wx.NewId()
F_RAW_SEND = wx.NewId()
F_HIDE_TITLE = wx.NewId()
F_TEXT = wx.NewId()

class textctrl_edit_panel(wx.Panel):
    def __init__(self, parent, handler):
        wx.Panel.__init__(self, parent, -1)
        self.handler = handler
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

        sizer.Add(wx.StaticText(self, P_TITLE, "Title:"), 0, wx.EXPAND)
        sizer.Add(self.title, 0, wx.EXPAND)
        sizer.Add(wx.Size(10,10))
        sizer.Add(self.multi, 0, wx.EXPAND)
        sizer.Add(self.raw_send, 0, wx.EXPAND)
        sizer.Add(self.hide_title, 0, wx.EXPAND)
        sizer.Add(self.send_button, 0 , wx.EXPAND)
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

    def on_text(self,evt):
        id = evt.GetId()
        if id == P_TITLE:
            txt = self.title.GetValue()
            if not len(txt): return
            self.handler.xml.set('name',txt)
            self.handler.rename(txt)
        if id == F_TEXT:
            txt = self.text.GetValue()
            txt = strip_text(txt)
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
        self.list = self.xml.find('list')
        self.options = self.list.findall('option')
        if self.list.get("send_button") == "":
            self.list.set("send_button","0")
        if self.list.get("hide_title") == "":
            self.list.set("hide_title","0")

    def get_design_panel(self,parent):
        return listbox_edit_panel(parent,self)

    def get_use_panel(self,parent):
        return listbox_panel(parent,self)

    def get_type(self):
        return int(self.list.get("type"))

    def set_type(self,type):
        self.list.set("type",str(type))

    def is_hide_title(self):
        return int(self.list.get("hide_title",0))

    # single selection methods
    def get_selected_node(self):
        for opt in self.options:
            if opt.get("selected") == "1": return opt
        return None

    def get_selected_index(self):
        i = 0
        for opt in self.options:
            if opt.get("selected") == "1":
                return i
            i += 1
        return 0

    def get_selected_text(self):
        node = self.get_selected_node()
        if node:
            return getText(node)
        else:
            return ""


    # mult selection methods

    def get_selections(self):
        opts = []
        for opt in self.options:
            if opt.get("selected") == "1":
                opts.append(opt)
        return opts

    def get_selections_text(self):
        opts = []
        for opt in self.options:
            if opt.get("selected") == "1":
                opts.append(getText(opt))
        return opts

    def get_selections_index(self):
        opts = []
        i = 0
        for opt in self.options:
            if opt.get("selected") == "1":
                opts.append(i)
            i += 1
        return opts

    # setting selection method

    def set_selected_node(self,index,selected=1):
        if self.get_type() != L_CHECK:
            self.clear_selections()
        self.options[index].set("selected", str(bool2int(selected)))

    def clear_selections(self):
        for opt in self.options:
            opt.set("selected","0")

    # misc methods

    def get_options(self):
        opts = []
        for opt in self.options:
            opts.append(getText(opt))
        return opts

    def get_option(self,index):
        return getText(self.options[index])

    def add_option(self,opt):
        elem = ET.Element('option')
        elem.set("value","0")
        elem.set("selected","0")
        elem.text = opt
        self.list.append(elem)
        self.options = self.list.findall('option')

    def remove_option(self,index):
        self.list.remove(self.options[index])
        self.options = self.list.findall('option')

    def edit_option(self,index,value):
        self.options[index].text = value

    def has_send_button(self):
        if self.list.get("send_button") == '0':
            return False
        else:
            return True

    def get_size_constraint(self):
        if self.get_type() == L_DROP:
            return 0
        else:
            return 1

    def tohtml(self):
        opts = self.get_selections_text()
        text = ""
        if not self.is_hide_title():
            text = "<b>"+self.xml.get("name")+":</b> "
        comma = ", "
        text += comma.join(opts)
        return text

    def get_value(self):
        return "\n".join(self.get_selections_text())

F_LIST = wx.NewId()
F_SEND = wx.NewId()


class listbox_panel(wx.Panel):
    def __init__(self, parent, handler):
        wx.Panel.__init__(self, parent, -1)
        self.handler = handler
        self.chat = handler.chat
        opts = handler.get_options()
        cur_opt = handler.get_selected_text()
        type = handler.get_type()
        label = handler.xml.get('name')

        if type == L_DROP:
            self.list = wx.ComboBox(self, F_LIST, cur_opt, choices=opts, style=wx.CB_READONLY)
            if self.list.GetSize()[0] > 200:
                self.list.Destroy()
                self.list = wx.ComboBox(self, F_LIST, cur_opt, size=(200, -1), choices=opts, style=wx.CB_READONLY)
        elif type == L_LIST:
            self.list = wx.ListBox(self,F_LIST,choices=opts)
        elif type == L_RADIO:
            self.list = wx.RadioBox(self,F_LIST,label,choices=opts,majorDimension=3)
        elif type == L_CHECK:
            self.list = wx.CheckListBox(self,F_LIST,choices=opts)
            self.set_checks()

        for i in handler.get_selections_text():
            if type == L_DROP:
                self.list.SetValue( i )
            else:
                self.list.SetStringSelection( i )

        if type == L_DROP:
            sizer = wx.BoxSizer(wx.HORIZONTAL)

        else:
            sizer = wx.BoxSizer(wx.VERTICAL)

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

        if type == L_DROP:
            self.Bind(wx.EVT_COMBOBOX, self.on_change, id=F_LIST)
        elif type == L_LIST:
            self.Bind(wx.EVT_LISTBOX, self.on_change, id=F_LIST)
        elif type == L_RADIO:
            self.Bind(wx.EVT_RADIOBOX, self.on_change, id=F_LIST)
        elif type == L_CHECK:
            self.Bind(wx.EVT_CHECKLISTBOX, self.on_check, id=F_LIST)


        self.type = type


    def on_change(self,evt):
        self.handler.set_selected_node(self.list.GetSelection())

    def on_check(self,evt):
        for i in xrange(self.list.GetCount()):
            self.handler.set_selected_node(i, bool2int(self.list.IsChecked(i)))

    def set_checks(self):
        for i in self.handler.get_selections_index():
            self.list.Check(i)



BUT_ADD = wx.NewId()
BUT_REM = wx.NewId()
BUT_EDIT = wx.NewId()
F_TYPE = wx.NewId()
F_NO_TITLE = wx.NewId()

class listbox_edit_panel(wx.Panel):
    def __init__(self, parent, handler):
        wx.Panel.__init__(self, parent, -1)
        self.handler = handler
        sizer = wx.StaticBoxSizer(wx.StaticBox(self, -1, "List Box Properties"), wx.VERTICAL)

        self.text = wx.TextCtrl(self, P_TITLE, handler.xml.get('name'))

        opts = handler.get_options()
        self.listbox = wx.ListBox(self, F_LIST, choices=opts, style=wx.LB_HSCROLL|wx.LB_SINGLE|wx.LB_NEEDED_SB)
        opts = ['Drop Down', 'List Box', 'Radio Box', 'Check List']
        self.type_radios = wx.RadioBox(self,F_TYPE,"List Type",choices=opts)
        self.type_radios.SetSelection(handler.get_type())

        self.send_button = wx.CheckBox(self, F_SEND_BUTTON, " Send Button")
        self.send_button.SetValue(handler.has_send_button())

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

    def on_type(self,evt):
        self.handler.set_type(evt.GetInt())

    def on_add(self,evt):
        dlg = wx.TextEntryDialog(self, 'Enter option?','Add Option', '')
        if dlg.ShowModal() == wx.ID_OK:
            self.handler.add_option(dlg.GetValue())
        dlg.Destroy()
        self.reload_options()

    def on_remove(self,evt):
        index = self.listbox.GetSelection()
        if index >= 0:
            self.handler.remove_option(index)
            self.reload_options()

    def on_edit(self,evt):
        index = self.listbox.GetSelection()
        if index >= 0:
            txt = self.handler.get_option(index)
            dlg = wx.TextEntryDialog(self, 'Enter option?','Edit Option', txt)
            if dlg.ShowModal() == wx.ID_OK:
                self.handler.edit_option(index,dlg.GetValue())
            dlg.Destroy()
            self.reload_options()

    def reload_options(self):
        self.listbox.Clear()
        for opt in self.handler.get_options():
            self.listbox.Append(opt)

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
        return "<a href=\""+href+"\" >"+title+"</a>"

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
        elif id == P_URL:
            self.handler.link.set('href',txt)

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
        if not img is None:
            return wx.StaticBitmap(parent,-1,img,size= wx.Size(img.GetWidth(),img.GetHeight()))
        return wx.EmptyBitmap(1, 1)

    def tohtml(self):
        href = self.link.get("href")
        title = self.xml.get("name")
        return "<img src=\""+href+"\" alt="+title+" >"



#######################
## resource handler
#######################

class resource_handler(node_handler):
    """
    <nodehandler class="resource_handler" module="forms" name="">
        <resource base="5" current="4" checks="1">Multi-line macro</resource>
    </nodehandler>
    """
    def __init__(self,xml,tree_node):
        node_handler.__init__(self,xml,tree_node)
        self.resource = self.xml.find('resource')
        if self.resource.get("checks") == "":
            self.resource.set("checks","1")
        if self.resource.get("base") == "":
            self.resource.set("base","1")
        if self.resource.get("current") == "":
            self.resource.set("current", self.resource.get("base"))

    def get_design_panel(self,parent):
        return resource_edit_panel(parent,self)

    def get_use_panel(self,parent):
        return resource_panel(parent,self)

    def tohtml(self):
        # decrement the current value or post a "nothing left" message
        # print the multi-line macro
        return "resource"

    def use_checks(self):
        if self.resource.get("checks") == "1":
            return True
        return False

    def get_base(self):
        return int(self.resource.get("base",0))

    def get_current(self):
        return int(self.resource.get("current",0))

    def get_macro(self):
        return getText(self.resource)

    def get_value(self):
        return self.resource.get("current")

    def set_value(self, new_value):
        self.resource.set("current", new_value)


RESOURCE_RESET  = wx.NewId()
RESOURCE_CHECKS = wx.NewId()
RESOURCE_NUMBER = wx.NewId()
RESOURCE_DONE   = wx.NewId()


class resource_panel(wx.Panel):
    def __init__(self, parent, handler):
        wx.Panel.__init__(self, parent, -1)
        self.handler = handler
        self.chat = handler.chat

        sizer = wx.BoxSizer(wx.HORIZONTAL)
 #       sizer.Add(wx.Button(self, RESOURCE_RESET, "Reset"))
        sizer.Add(wx.StaticText(self, -1, handler.xml.get('name')+": "), 1, wx.ALIGN_RIGHT)
        if self.handler.use_checks():
            grid = wx.GridSizer(1, 11, 0, 0)
            sizer.Add(grid, 0, wx.ALIGN_RIGHT)
            self.checks = []
            used = self.handler.get_base() - self.handler.get_current()
            for i in range(self.handler.get_base()):
                self.checks.append(wx.CheckBox(self, RESOURCE_CHECKS, ""))
                checked = False
                if i < used:
                    checked = True
                self.checks[i].SetValue(checked)
                grid.Add(self.checks[i])
                if i-int(i/10)*10==4:
                    grid.Add(wx.Size(1,1))
        else:
            self.number = wx.TextCtrl(self, RESOURCE_NUMBER, self.handler.resource.get("current"))
            sizer.Add(self.number, 0, wx.ALIGN_RIGHT)
        sizer.Add(wx.Size(10,10), 0, wx.ALIGN_RIGHT)
        sizer.Add(wx.Button(self, RESOURCE_DONE,  "Apply"), 0, wx.ALIGN_RIGHT)
  #      self.chat.InfoPost("res 10")
        sizer.SetMinSize(wx.Size(380,10))
        self.sizer = sizer
        self.SetSizer(sizer)
        self.SetAutoLayout(True)
        self.Fit()
   #     self.chat.InfoPost("res 20")
        self.Bind(wx.EVT_BUTTON, self.on_reset, id=RESOURCE_RESET)
        self.Bind(wx.EVT_BUTTON, self.on_done,   id=RESOURCE_DONE)


    def on_reset(self,evt):
        # uncheck all the check boxes or set the text to max
        if self.handler.use_checks():
            for c in self.checks:
                c.SetValue(False)
        else:
            self.number.SetValue(self.handler.resource.get("base"))
        self.handler.resource.set("current", self.handler.resource.get("base"))

    def on_done(self,evt):
        # save the changes back to the handler
        current = 0
        if self.handler.use_checks():
            for c in self.checks:
                if not c.GetValue():
                    current += 1
        else:
            # validate text
            current = int(self.number.GetValue())
        change = self.handler.get_current()-current
        if change > 0:
            macro_text = self.handler.get_macro()
            macro_text = macro_text.replace("_NAME_",self.handler.xml.get("name"))
            macro_text = macro_text.replace("_CHANGE_", str(change))
            macro_text = macro_text.replace("_CURRENT_", str(current))
            self.handler.chat.ParsePost(macro_text, True, True)
            self.handler.resource.set("current",str(current))


RES_EDIT_TITLE    = wx.NewId()
RES_EDIT_BASE     = wx.NewId()
RES_EDIT_CURRENT  = wx.NewId()
RES_EDIT_CHECKS   = wx.NewId()
RES_EDIT_MACRO    = wx.NewId()


class resource_edit_panel(wx.Panel):
    def __init__(self, parent, handler):
        wx.Panel.__init__(self, parent, -1)
        self.handler = handler

        sizer = wx.StaticBoxSizer(wx.StaticBox(self, -1, "Resource Properties"), wx.VERTICAL)
        sizer.Add(wx.StaticText(self, -1, "Name of resource:"), 0, wx.EXPAND)
        self.title = wx.TextCtrl(self, RES_EDIT_TITLE, self.handler.xml.get('name'))
        sizer.Add(self.title, 0, wx.EXPAND)
        sizer.Add(wx.Size(10,10))

        sizer.Add(wx.StaticText(self, -1, "Base amount of resource:"), 0, wx.EXPAND)
        self.base = wx.TextCtrl(self, RES_EDIT_BASE, self.handler.resource.get("base"))
        sizer.Add(self.base, 0, wx.EXPAND)
        sizer.Add(wx.Size(10,10))

        sizer.Add(wx.StaticText(self, -1, "Current amount of resource:"), 0, wx.EXPAND)
        self.current = wx.TextCtrl(self, RES_EDIT_CURRENT, self.handler.resource.get("current"))
        sizer.Add(self.current, 0, wx.EXPAND)
        sizer.Add(wx.Size(10,10))

        opts = ['Text Number', 'Check Boxes']
        self.radio = wx.RadioBox(self, RES_EDIT_CHECKS, "Amount of resource is represented by:", choices=opts)
        if self.handler.use_checks():
            self.radio.SetSelection(1)
        else:
            self.radio.SetSelection(0)
        sizer.Add(self.radio, 0, wx.EXPAND)
        sizer.Add(wx.Size(10,10))

        sizer.Add(wx.StaticText(self, -1, "Send the following macro:"), 0, wx.EXPAND)
        self.macro = wx.TextCtrl(self, RES_EDIT_MACRO, self.handler.get_macro(), style=wx.TE_MULTILINE)
        sizer.Add(self.macro, 1,  wx.EXPAND)

        self.SetSizer(sizer)
        self.SetAutoLayout(True)
        self.Fit()
        parent.SetSize(self.GetBestSize())

        self.Bind(wx.EVT_TEXT, self.on_title, id=RES_EDIT_TITLE)
        self.Bind(wx.EVT_TEXT, self.on_base, id=RES_EDIT_BASE)
        self.Bind(wx.EVT_TEXT, self.on_current, id=RES_EDIT_CURRENT)
        self.Bind(wx.EVT_RADIOBOX, self.on_type, id=RES_EDIT_CHECKS)
        self.Bind(wx.EVT_TEXT, self.on_macro, id=RES_EDIT_MACRO)


    def on_title(self, evt):
        if len(self.title.GetValue()):
            self.handler.xml.set('name', self.title.GetValue())
            self.handler.rename(self.title.GetValue())

    def on_base(self, evt):
        try:
            b = int(self.base.GetValue())
            self.handler.resource.set("base",str(b))
        except:
            pass

    def on_current(self, evt):
        try:
            c = int(self.current.GetValue())
            self.handler.resource.set("current",str(c))
        except:
            pass

    def on_type(self,evt):
        self.handler.resource.set("checks",str(self.radio.GetSelection()))

    def on_macro(self,evt):
        self.handler.resource.text = self.macro.GetValue()


#######################
## bonus handler
#######################

class bonus_handler(node_handler):
    """
    <nodehandler class="bonus_handler" module="forms" name="">
        <bonus value="2" type="optional">Multi-line list of node references</bonus>
    </nodehandler>
    """
    def __init__(self,xml,tree_node):
        node_handler.__init__(self,xml,tree_node)
        self.bonus_xml = self.xml.find('bonus')
        self.add_to_bonus_map()

    def get_design_panel(self,parent):
        return bonus_edit_panel(parent,self)

    def get_use_panel(self,parent):# there is no 'use' for a bonus
        return bonus_edit_panel(parent,self)

    def tohtml(self):
        return "bonus"# there is no 'send to chat' or 'pretty print'

    def get_value(self):
        return self.bonus_xml.get('value', '')

    def delete(self):
        self.remove_from_bonus_map()
        return node_handler.delete(self)

    def add_to_bonus_map(self):
        for target in getText(self.bonus_xml).split('\n'):
            self.tree.AddBonus(target, self)

    def remove_from_bonus_map(self):
        for target in getText(self.bonus_xml).split('\n'):
            self.tree.RemoveBonus(target, self)
        


BONUS_EDIT_TITLE = wx.NewId()
BONUS_EDIT_VALUE = wx.NewId()
BONUS_EDIT_TYPE = wx.NewId()
BONUS_EDIT_REF = wx.NewId()


class bonus_edit_panel(wx.Panel):
    def __init__(self, parent, handler):
        wx.Panel.__init__(self, parent, -1)
        self.handler = handler

        sizer = wx.StaticBoxSizer(wx.StaticBox(self, -1, "Bonus Properties"), wx.VERTICAL)
        sizer.Add(wx.StaticText(self, -1, "Name of bonus:"), 0, wx.EXPAND)
        self.title = wx.TextCtrl(self, BONUS_EDIT_TITLE, self.handler.xml.get('name'))
        sizer.Add(self.title, 0, wx.EXPAND)
        sizer.Add(wx.Size(10,10))

        sizer.Add(wx.StaticText(self, -1, "Size of bonus:"), 0, wx.EXPAND)
        self.value = wx.TextCtrl(self, BONUS_EDIT_VALUE, self.handler.bonus_xml.get('value', ''))
        sizer.Add(self.value, 0, wx.EXPAND)
        sizer.Add(wx.Size(10,10))

        sizer.Add(wx.StaticText(self, -1, "Type of bonus:"), 0, wx.EXPAND)
        self.type = wx.TextCtrl(self, BONUS_EDIT_TYPE, self.handler.bonus_xml.get("type"))
        sizer.Add(self.type, 0, wx.EXPAND)
        sizer.Add(wx.Size(10,10))

        sizer.Add(wx.StaticText(self, -1, "Add to the following nodes:"), 0, wx.EXPAND)
        self.ref = wx.TextCtrl(self, BONUS_EDIT_REF, getText(self.handler.bonus_xml), style=wx.TE_MULTILINE)
        sizer.Add(self.ref, 1,  wx.EXPAND)

        self.SetSizer(sizer)
        self.SetAutoLayout(True)
        self.Fit()
        parent.SetSize(self.GetBestSize())

        self.Bind(wx.EVT_TEXT, self.on_title, id=BONUS_EDIT_TITLE)# too many calls - should call only upon close
        self.Bind(wx.EVT_TEXT, self.on_value, id=BONUS_EDIT_VALUE)
        self.Bind(wx.EVT_TEXT, self.on_type, id=BONUS_EDIT_TYPE)
        self.Bind(wx.EVT_TEXT, self.on_ref, id=BONUS_EDIT_REF)


    def on_title(self, evt):
        if len(self.title.GetValue()):
            self.handler.xml.set('name', self.title.GetValue())
            self.handler.rename(self.title.GetValue())

    def on_value(self, evt):
        self.handler.bonus_xml.set('value', self.value.GetValue())

    def on_type(self, evt):
        self.handler.bonus_xml.set('type', self.type.GetValue())

    def on_ref(self, evt):
        self.handler.remove_from_bonus_map()
        self.handler.bonus_xml.text = self.ref.GetValue()
        self.handler.add_to_bonus_map()
