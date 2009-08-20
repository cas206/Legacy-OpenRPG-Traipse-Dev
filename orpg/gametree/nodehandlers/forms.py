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
from wx.lib.scrolledpanel import ScrolledPanel

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

    def __init__(self,xml_dom,tree_node):
        container_handler.__init__(self,xml_dom,tree_node)

    def load_children(self):
        self.atts = None
        children = self.master_dom._get_childNodes()
        for c in children:
            if c._get_tagName() == "form":
                self.atts = c
            else:
                self.tree.load_xml(c,self.mytree_node)
        if not self.atts:
            elem = self.xml.minidom.Element('form')
            elem.setAttribute("width","400")
            elem.setAttribute("height","600")
            self.atts = self.master_dom.appendChild(elem)

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
        self.height = int(handler.atts.getAttribute("height"))
        self.width = int(handler.atts.getAttribute("width"))


        self.SetSize((0,0))
        self.handler = handler
        self.parent = parent
        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
        tree = self.handler.tree
        child = tree.GetFirstChild(handler.mytree_node)
        if child[0].IsOk():
            handler.traverse(child[0], self.create_child_wnd, 0, None, False)

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


    def create_child_wnd(self, obj, evt):
        panel = obj.get_use_panel(self)
        size = obj.get_size_constraint()
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
        self.text = {   P_TITLE : wx.TextCtrl(self, P_TITLE, handler.master_dom.getAttribute('name')),
                        F_HEIGHT : wx.TextCtrl(self, F_HEIGHT, handler.atts.getAttribute('height')),
                        F_WIDTH : wx.TextCtrl(self, F_WIDTH, handler.atts.getAttribute('width'))
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
            self.handler.master_dom.setAttribute('name',txt)
            self.handler.rename(txt)
        elif id == F_HEIGHT or id == F_WIDTH:
            try:
                int(txt)
            except:
                return 0
            if id == F_HEIGHT:
                self.handler.atts.setAttribute("height",txt)
            elif id == F_WIDTH:
                self.handler.atts.setAttribute("width",txt)





##########################
## control handler
##########################
class control_handler(node_handler):
    """ A nodehandler for form controls.
        <nodehandler name='?' module='forms' class='control_handler' />
    """
    def __init__(self,xml_dom,tree_node):
        node_handler.__init__(self,xml_dom,tree_node)

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
    def __init__(self,xml_dom,tree_node):
        node_handler.__init__(self,xml_dom,tree_node)
        self.text_elem = self.master_dom.getElementsByTagName('text')[0]
        self.text = component.get('xml').safe_get_text_node(self.text_elem)
        if self.text_elem.getAttribute("send_button") == "":
            self.text_elem.setAttribute("send_button","0")
        if self.text_elem.getAttribute("raw_mode") == "":
            self.text_elem.setAttribute("raw_mode","0")
        if self.text_elem.getAttribute("hide_title") == "":
            self.text_elem.setAttribute("hide_title","0")

    def get_design_panel(self,parent):
        return textctrl_edit_panel(parent,self)

    def get_use_panel(self,parent):
        return text_panel(parent,self)

    def get_size_constraint(self):
        return int(self.text_elem.getAttribute("multiline"))

    def is_multi_line(self):
        return int(self.text_elem.getAttribute("multiline"))

    def is_raw_send(self):
        return int(self.text_elem.getAttribute("raw_mode"))

    def is_hide_title(self):
        return int(self.text_elem.getAttribute("hide_title"))

    def has_send_button(self):
        return int(self.text_elem.getAttribute("send_button"))


    def tohtml(self):
        txt = self.text._get_nodeValue()
        txt = string.replace(txt,'\n',"<br />")
        if not self.is_hide_title():
            txt = "<b>"+self.master_dom.getAttribute("name")+":</b> "+txt
        return txt


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

        txt = handler.text._get_nodeValue()
        self.text = wx.TextCtrl(self, FORM_TEXT_CTRL, txt, style=text_style)
        sizer.Add(wx.StaticText(self, -1, handler.master_dom.getAttribute('name')+": "), 0, sizer_style)
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
        self.handler.text._set_nodeValue(txt)

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

        self.title = wx.TextCtrl(self, P_TITLE, handler.master_dom.getAttribute('name'))
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
        self.text = wx.TextCtrl(self, F_TEXT, handler.text._get_nodeValue(),style=text_style)
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
            self.handler.master_dom.setAttribute('name',txt)
            self.handler.rename(txt)
        if id == F_TEXT:
            txt = self.text.GetValue()
            txt = strip_text(txt)
            self.handler.text._set_nodeValue(txt)

    def on_button(self,evt):
        self.handler.text_elem.setAttribute("multiline",str(bool2int(evt.Checked())))

    def on_raw_button(self,evt):
        self.handler.text_elem.setAttribute("raw_mode",str(bool2int(evt.Checked())))

    def on_hide_button(self,evt):
        self.handler.text_elem.setAttribute("hide_title",str(bool2int(evt.Checked())))

    def on_send_button(self,evt):
        self.handler.text_elem.setAttribute("send_button",str(bool2int(evt.Checked())))






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
    def __init__(self,xml_dom,tree_node):
        node_handler.__init__(self,xml_dom,tree_node)
        self.list = self.master_dom.getElementsByTagName('list')[0]
        self.options = self.list.getElementsByTagName('option')
        if self.list.getAttribute("send_button") == "":
            self.list.setAttribute("send_button","0")
        if self.list.getAttribute("hide_title") == "":
            self.list.setAttribute("hide_title","0")

    def get_design_panel(self,parent):
        return listbox_edit_panel(parent,self)

    def get_use_panel(self,parent):
        return listbox_panel(parent,self)

    def get_type(self):
        return int(self.list.getAttribute("type"))

    def set_type(self,type):
        self.list.setAttribute("type",str(type))

    def is_hide_title(self):
        return int(self.list.getAttribute("hide_title"))

    # single selection methods
    def get_selected_node(self):
        for opt in self.options:
            if opt.getAttribute("selected") == "1": return opt
        return None

    def get_selected_index(self):
        i = 0
        for opt in self.options:
            if opt.getAttribute("selected") == "1":
                return i
            i += 1
        return 0

    def get_selected_text(self):
        node = self.get_selected_node()
        if node:
            return component.get('xml').safe_get_text_node(node)._get_nodeValue()
        else:
            return ""


    # mult selection methods

    def get_selections(self):
        opts = []
        for opt in self.options:
            if opt.getAttribute("selected") == "1":
                opts.append(opt)
        return opts

    def get_selections_text(self):
        opts = []
        for opt in self.options:
            if opt.getAttribute("selected") == "1":
                opts.append(component.get('xml').safe_get_text_node(opt)._get_nodeValue())
        return opts

    def get_selections_index(self):
        opts = []
        i = 0
        for opt in self.options:
            if opt.getAttribute("selected") == "1":
                opts.append(i)
            i += 1
        return opts

    # setting selection method

    def set_selected_node(self,index,selected=1):
        if self.get_type() != L_CHECK:
            self.clear_selections()
        self.options[index].setAttribute("selected", str(bool2int(selected)))

    def clear_selections(self):
        for opt in self.options:
            opt.setAttribute("selected","0")

    # misc methods

    def get_options(self):
        opts = []
        for opt in self.options:
            opts.append(component.get('xml').safe_get_text_node(opt)._get_nodeValue())
        return opts

    def get_option(self,index):
        return component.get('xml').safe_get_text_node(self.options[index])._get_nodeValue()

    def add_option(self,opt):
        elem = minidom.Element('option')
        elem.setAttribute("value","0")
        elem.setAttribute("selected","0")
        t_node = minidom.Text(opt)
        t_node = elem.appendChild(t_node)
        self.list.appendChild(elem)
        self.options = self.list.getElementsByTagName('option')

    def remove_option(self,index):
        self.list.removeChild(self.options[index])
        self.options = self.list.getElementsByTagName('option')

    def edit_option(self,index,value):
        component.get('xml').safe_get_text_node(self.options[index])._set_nodeValue(value)

    def has_send_button(self):
        if self.list.getAttribute("send_button") == '0':
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
            text = "<b>"+self.master_dom.getAttribute("name")+":</b> "
        comma = ", "
        text += comma.join(opts)
        return text



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
        label = handler.master_dom.getAttribute('name')

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

        self.text = wx.TextCtrl(self, P_TITLE, handler.master_dom.getAttribute('name'))

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
            self.handler.master_dom.setAttribute('name',txt)
            self.handler.rename(txt)

    def on_send_button(self,evt):
        self.handler.list.setAttribute("send_button", str( bool2int(evt.Checked()) ))

    def on_hide_button(self,evt):
        print "hide_title, " + str(bool2int(evt.Checked()))
        self.handler.list.setAttribute("hide_title", str( bool2int(evt.Checked()) ))


###############################
## link image handlers
###############################

class link_handler(node_handler):
    """ A nodehandler for URLs. Will open URL in a wxHTMLFrame
        <nodehandler name='?' module='forms' class='link_handler' >
                <link  href='http//??.??'  />
        </nodehandler >
    """
    def __init__(self,xml_dom,tree_node):
        node_handler.__init__(self,xml_dom,tree_node)
        self.link = self.master_dom._get_firstChild()

    def on_use(self,evt):
        href = self.link.getAttribute("href")
        wb = webbrowser.get()
        wb.open(href)

    def get_design_panel(self,parent):
        return link_edit_panel(parent,self)

    def get_use_panel(self,parent):
        return link_panel(parent,self)

    def tohtml(self):
        href = self.link.getAttribute("href")
        title = self.master_dom.getAttribute("name")
        return "<a href=\""+href+"\" >"+title+"</a>"

class link_panel(wx.StaticText):
    def __init__(self,parent,handler):
        self.handler = handler
        label = handler.master_dom.getAttribute('name')
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
        self.text[P_TITLE] = wx.TextCtrl(self, P_TITLE, handler.master_dom.getAttribute('name'))
        self.text[P_URL] = wx.TextCtrl(self, P_URL, handler.link.getAttribute('href'))

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
            self.handler.master_dom.setAttribute('name',txt)
            self.handler.rename(txt)
        elif id == P_URL:
            self.handler.link.setAttribute('href',txt)

##########################
## webimg node handler
##########################
class webimg_handler(node_handler):
    """ A nodehandler for URLs. Will open URL in a wxHTMLFrame
        <nodehandler name='?' module='forms' class='webimg_handler' >
                <link  href='http//??.??'  />
        </nodehandler >
    """
    def __init__(self,xml_dom,tree_node):
        node_handler.__init__(self,xml_dom,tree_node)
        self.link = self.master_dom._get_firstChild()

    def get_design_panel(self,parent):
        return link_edit_panel(parent,self)

    def get_use_panel(self,parent):
        img = img_helper().load_url(self.link.getAttribute("href"))
        #print img
        if not img is None:
            return wx.StaticBitmap(parent,-1,img,size= wx.Size(img.GetWidth(),img.GetHeight()))
        return wx.EmptyBitmap(1, 1)

    def tohtml(self):
        href = self.link.getAttribute("href")
        title = self.master_dom.getAttribute("name")
        return "<img src=\""+href+"\" alt="+title+" >"
