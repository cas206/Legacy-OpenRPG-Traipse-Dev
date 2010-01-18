# Copyright (C) 2000-2001 The OpenRPG Project
#
#    openrpg-dev@lists.sourceforge.net
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
# File: mapper/min_dialogs.py
# Author: Chris Davis
# Maintainer:
# Version:
#   $Id: min_dialogs.py,v Traipse 'Ornery-Orc' prof.ebral Exp $
#
# Description: This file contains some of the basic definitions for the chat
# utilities in the orpg project.

##-----------------------------
## Miniature List Panel
##-----------------------------

from miniatures import *

class min_list_panel(wx.Dialog):

    def __init__(self, parent,layers, log, pos =(-1,-1)):
        wx.Dialog.__init__(self,  parent,-1, log,pos = (-1,-1), size = (785,175), style=wx.RESIZE_BORDER)
        listID = wx.NewId()
        self.parent = parent
        self.min = layers['miniatures'].miniatures
        self.grid = layers['grid']
        self.layers = layers
        self.listID = listID
        list_sizer = wx.BoxSizer(wx.VERTICAL)
        self.list_sizer = list_sizer
        listctrl = wx.ListCtrl(self, listID, style=wx.LC_REPORT | wx.SUNKEN_BORDER)
        self.listctrl = listctrl
        self.Centre(wx.BOTH)
        self.log = log
        self.list_sizer.Add(self.listctrl,1,wx.EXPAND)
        self.listctrl.InsertColumn(0,"POS    ")
        self.listctrl.InsertColumn(0,"LOCKED")
        self.listctrl.InsertColumn(0,"HEADING")
        self.listctrl.InsertColumn(0,"FACING")
        self.listctrl.InsertColumn(0,"LABEL")
        self.listctrl.InsertColumn(0,"PATH")
        self.listctrl.SetColumnWidth(1, wx.LIST_AUTOSIZE_USEHEADER)
        self.listctrl.SetColumnWidth(2, wx.LIST_AUTOSIZE_USEHEADER)
        self.listctrl.SetColumnWidth(3, wx.LIST_AUTOSIZE_USEHEADER)
        self.listctrl.SetColumnWidth(4, wx.LIST_AUTOSIZE_USEHEADER)
        self.listctrl.SetColumnWidth(5, wx.LIST_AUTOSIZE_USEHEADER)
        self.list_sizer.Add(wx.Button(self, wx.ID_OK, "DONE"),0,wx.ALIGN_CENTER)
        self.refresh()
        self.Bind(wx.EVT_BUTTON, self.on_ok, id=wx.ID_OK)
        self.listctrl.Bind(wx.EVT_COMMAND_RIGHT_CLICK, self.OnRightClick, id=listID)
        self.listctrl.Bind(wx.EVT_RIGHT_UP, self.OnRightClick)
        self.listctrl.Bind(wx.EVT_RIGHT_DOWN, self.OnRightDown)
        self.SetSizer(self.list_sizer)
        self.SetAutoLayout(True)
        self.Fit()

    def OnRightClick(self,event):
        if self.listctrl.GetSelectedItemCount() > 0:
            menu = wx.Menu()
            lPopupID1 = wx.NewId()
            lPopupID2 = wx.NewId()
            lPopupID3 = wx.NewId()
            menu.Append(lPopupID1, "&Edit")
            menu.Append(lPopupID2, "&Delete")
            menu.Append(lPopupID3, "To &Gametree")
            self.Bind(wx.EVT_MENU, self.onEdit, id=lPopupID1)
            self.Bind(wx.EVT_MENU, self.onDelete, id=lPopupID2)
            self.Bind(wx.EVT_MENU, self.onToGametree, id=lPopupID3)
            self.PopupMenu(menu, cmpPoint(self.x, self.y))
            menu.Destroy()
        event.Skip()

    def refresh(self):
        self.SetMinSize((600,175));
        for m in self.min:
            self.listctrl.InsertStringItem(self.min.index(m),self.min[self.min.index(m)].path)
            self.listctrl.SetStringItem(self.min.index(m),1,self.min[self.min.index(m)].label)
            self.listctrl.SetStringItem(self.min.index(m),2,`self.min[self.min.index(m)].heading`)
            self.listctrl.SetStringItem(self.min.index(m),3,`self.min[self.min.index(m)].face`)
            self.listctrl.SetStringItem(self.min.index(m),4,`self.min[self.min.index(m)].locked`)
            self.listctrl.SetStringItem(self.min.index(m),5,`self.min[self.min.index(m)].pos`)
            oldcolumnwidth = self.listctrl.GetColumnWidth(0)
            self.listctrl.SetColumnWidth(0, wx.LIST_AUTOSIZE)
            if oldcolumnwidth < self.listctrl.GetColumnWidth(0): self.listctrl.SetColumnWidth(0, wx.LIST_AUTOSIZE)
            else: self.listctrl.SetColumnWidth(0, oldcolumnwidth)
        self.list_sizer=self.list_sizer

    def onEdit(self,event):
        min_list = []
        min_index = []
        loop_count = 0
        item =-1
        while True:
            loop_count += 1
            item = self.listctrl.GetNextItem(item,wx.LIST_NEXT_ALL, wx.LIST_STATE_SELECTED)
            if item == -1: break
            min_list.append(self.min[item])
            min_index.append(item-loop_count+1)
        if len(min_list) > 0: dlg = min_list_edit_dialog(self.parent,min_index, min_list,self.layers)
        if dlg.ShowModal() == wx.ID_OK: pass
        self.listctrl.DeleteAllItems()
        self.refresh()
        event.Skip()

    def onDelete(self,event):
        loop_count = 0
        item = -1
        while True:
            loop_count += 1
            item = self.listctrl.GetNextItem(item,wx.LIST_NEXT_ALL, wx.LIST_STATE_SELECTED)
            if item == -1: break
            self.layers["miniatures"].del_miniature(self.min[item-loop_count+1])
        self.listctrl.DeleteAllItems()
        self.refresh()
        event.Skip()

    def onToGametree(self,event):
        min_list = []
        min_index = []
        loop_count = 0
        item =-1
        while True:
            loop_count += 1
            item = self.listctrl.GetNextItem(item,wx.LIST_NEXT_ALL, wx.LIST_STATE_SELECTED)
            if item == -1: break
            min_list.append(self.min[item])
            min_index.append(item-loop_count+1)
        if len(min_list) > 0:
            for sel_rmin in min_list:
             #############
                min_xml = sel_rmin.toxml(action="new")
                node_begin = "<nodehandler module='map_miniature_nodehandler' class='map_miniature_handler' name='"
                if sel_rmin.label: node_begin += sel_rmin.label + "'"
                else: node_begin += "Unnamed Miniature'"
                node_begin += ">"
                gametree = component.get('tree')
                node_xml = node_begin + min_xml + '</nodehandler>'
                print "Sending this XML to insert_xml:" + node_xml
                gametree.insert_xml(node_xml)
             #############
        self.listctrl.DeleteAllItems()
        self.refresh()
        event.Skip()

    def OnRightDown(self,event):
        self.x = event.GetX()
        self.y = event.GetY()
        event.Skip()

    def on_ok(self,evt):
        self.EndModal(wx.ID_OK)

class min_list_edit_dialog(wx.Dialog):
    def __init__(self,parent,min_index, min_list, layers):
        wx.Dialog.__init__(self,parent,-1,"Miniature List",wx.DefaultPosition,wx.Size(600,530))
        self.layers = layers
        grid = layers['grid']
        min = layers['miniatures']
        self.min_list = min_list
        self.min_index = min_index
        self.min = min
        sizer1 = wx.BoxSizer(wx.VERTICAL)
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.grid = grid
        editor = min_list_edit_panel(self, min_index, min_list,layers)
        sizer1.Add(editor, 1, wx.EXPAND)
        sizer.Add(wx.Button(self, wx.ID_OK, "OK"), 1, wx.EXPAND)
        sizer.Add(wx.Size(10,10))
        sizer.Add(wx.Size(10,10))
        sizer.Add(wx.Button(self, wx.ID_CANCEL, "Cancel"), 1, wx.EXPAND)
        sizer1.Add(sizer, 0, wx.EXPAND)
        self.editor = editor
        self.Bind(wx.EVT_BUTTON, self.on_ok, id=wx.ID_OK)
        self.SetSizer(sizer1)
        self.SetAutoLayout(True)
        self.Fit()

    def on_revert(self,evt):
        pass

    def on_ok(self,evt):
        self.editor.on_ok(self.layers)
        self.EndModal(wx.ID_OK)

class min_list_edit_panel(wx.Panel):
    def __init__(self, parent, min_index, min_list,layers):
        LABEL_COMBO = wx.NewId()
        PATH_COMBO = wx.NewId()
        POS_COMB = wx.NewId()
        MIN_POS = wx.NewId()
        POS_SPIN = wx.NewId()
        self.grid = layers['grid']
        self.min = layers['miniatures'].miniatures
        self.min_list = min_list
        self.min_index = min_index
        self.layers = layers
        wx.Panel.__init__(self, parent, -1)
        self.min=min
        listsizer = wx.StaticBoxSizer(wx.StaticBox(self,-1,"Miniature list properties"), wx.VERTICAL)
        labelsizer = wx.BoxSizer(wx.HORIZONTAL)
        self.labelcheck = wx.CheckBox(self,-1,"Serialize")
        labelsizer.Add(wx.StaticText(self, -1, "Label:          "), 0, wx.EXPAND)
        labelsizer.Add(self.labelcheck,wx.ALIGN_RIGHT,wx.EXPAND)
        listsizer.Add(labelsizer,0, wx.EXPAND)
        self.labelcombo = wx.ComboBox(self, LABEL_COMBO,"no change",style=wx.CB_DROPDOWN)
        listsizer.Add(self.labelcombo,0, wx.EXPAND)
        self.pathcombo = wx.ComboBox(self, PATH_COMBO, "no change",style=wx.CB_DROPDOWN)
        self.positioncombo = wx.ComboBox(self, POS_COMB, "no change", choices=["no change"], style=wx.CB_READONLY)
        self.labelcombo.Append("no change")
        self.pathcombo.Append("no change")
        for m in min_list:
            self.labelcombo.Append(min_list[min_list.index(m)].label)
            self.pathcombo.Append(min_list[min_list.index(m)].path)
            self.positioncombo.Append(`min_list[min_list.index(m)].pos`)
        listsizer.Add(wx.StaticText(self, -1, "Path:"), 0, wx.EXPAND)
        listsizer.Add(self.pathcombo, 0, wx.EXPAND)
        listsizer.Add(wx.Size(10,10))
        self.heading = wx.RadioBox(self, MIN_HEADING, "Heading", 
            choices=["None","N","NE","E","SE","S","SW","W","NW","no change"], majorDimension=5, style=wx.RA_SPECIFY_COLS)
        self.heading.SetSelection( 9 )
        listsizer.Add( self.heading, 0, wx.EXPAND )
        listsizer.Add(wx.Size(10,10))
        self.face = wx.RadioBox(self, MIN_FACE, "Facing", 
            choices=["None","N","NE","E","SE","S","SW","W","NW","no change"], majorDimension=5, style=wx.RA_SPECIFY_COLS)
        self.face.SetSelection(9)
        listsizer.Add(self.face, 0, wx.EXPAND)
        ###
        ###Group together locked, Hide, and snap radioboxes in group2 box
        ###
        group2 = wx.BoxSizer(wx.HORIZONTAL)
        self.locked = wx.RadioBox(self, MIN_LOCK, "Lock", 
            choices=["Don't lock","Lock","no change"],majorDimension=1,style=wx.RA_SPECIFY_COLS)
        self.locked.SetSelection(2)
        self.hide = wx.RadioBox(self, MIN_HIDE, "Hide", 
            choices=["Don't hide", "Hide", "no change"],majorDimension=1,style=wx.RA_SPECIFY_COLS)
        self.hide.SetSelection(2)
        self.snap = wx.RadioBox(self,MIN_ALIGN,"Snap",
            choices=["Center","Top left","no change"],majorDimension=1,style=wx.RA_SPECIFY_COLS)
        self.snap.SetSelection(2)
        group2.Add(self.locked, 0, wx.EXPAND)
        group2.Add(wx.Size(10,0))
        group2.Add(self.hide, 0, wx.EXPAND)
        group2.Add(wx.Size(10,0))
        group2.Add(self.snap, 0, wx.EXPAND)
        group2.Add(wx.Size(10,0))
        listsizer.Add(group2,0,0)
        ###
        ###Group together the postion radiobox and the and its selection elements
        ###
        xpos = int(min_list[0].pos[0])
        ypos = int(min_list[0].pos[1])
        self.scx = wx.SpinCtrl(self, POS_SPIN, "", (-1,-1), wx.Size(75,25))
        self.scx.SetRange(0,self.grid.return_grid()[0])
        self.scx.SetValue(xpos)
        self.scy = wx.SpinCtrl(self, POS_SPIN, "", (-1,-1), wx.Size(75,25))
        self.scy.SetRange(0,self.grid.return_grid()[1])
        self.scy.SetValue(1)
        self.scy.SetValue(ypos)
        positionbox = wx.BoxSizer(wx.HORIZONTAL)
        self.poschoice = wx.RadioBox(self,MIN_POS,"Position",
            choices=["Manual", "Existing", "no change"],majorDimension=1,style=wx.RA_SPECIFY_COLS)
        self.poschoice.SetSelection(2)
        positionbox.Add(self.poschoice,0,0)
        ###
        ### group together choices under position choice boxsizer
        ###
        poschoicebox = wx.BoxSizer(wx.VERTICAL)
            ###
            ### spinbox contains the x and y spinctrls
            ###
        spinbox = wx.BoxSizer(wx.HORIZONTAL)
        group2.Add(positionbox,0, wx.EXPAND)
        xpos = wx.StaticText(self, -1,"XPOS:  ")
        spinbox.Add(xpos,0, 0)
        spinbox.Add(self.scx, 0, 0)
        ypos = wx.StaticText(self, -1,"YPOS:  ")
        spinbox.Add(ypos,0, 0)
        spinbox.Add(self.scy, 0, 0)
        poschoicebox.Add(wx.Size(0,15))
        poschoicebox.Add(spinbox,0,0)
        ###
        ### kludge is just a way to horizontaly position text.  .Add doesn't seem to work.
        ###
        kluge = wx.BoxSizer(wx.HORIZONTAL)
        klugetext = wx.StaticText(self, -1, "            ")
        kluge.Add(klugetext,0,0)
        kluge.Add(self.positioncombo,0,0)
        poschoicebox.Add(wx.Size(0,1))
        poschoicebox.Add(kluge,0,0)
        positionbox.Add(poschoicebox,0,0)
        listsizer.Add(positionbox,0, 0)
        self.listsizer = listsizer
        self.SetSizer(listsizer)
        self.SetAutoLayout(True)
        self.Fit()
        self.Bind(wx.EVT_SPINCTRL, self.on_spin, id=POS_SPIN)
        self.Bind(wx.EVT_TEXT, self.on_combo_box, id=POS_COMB)
        self.Bind(wx.EVT_TEXT, self.on_text, id=MIN_LABEL)
        self.Bind(wx.EVT_RADIOBOX, self.on_radio_box, id=MIN_HEADING)
        self.Bind(wx.EVT_RADIOBOX, self.on_radio_box, id=MIN_FACE)

    def on_ok(self,min):
        self.min = min
        for m in self.min_list:
            if self.hide.GetSelection() !=2: m.hide = self.hide.GetSelection()
            if self.heading.GetSelection() !=9: m.heading = self.heading.GetSelection()
            if self.face.GetSelection() !=9: m.face = self.face.GetSelection()
            if self.locked.GetSelection() !=2: m.locked = self.locked.GetSelection()
            if self.snap.GetSelection() !=2: m.snap_to_align = self.snap.GetSelection()
            if self.labelcombo.GetValue() != "no change":
                m.label = self.labelcombo.GetValue()
                if self.labelcheck.GetValue(): m.label += " " + `self.layers['miniatures'].next_serial()`
            if self.pathcombo.GetValue() != "no change":
                path = self.pathcombo.GetValue()
                image = self.evaluate(path)
                if str(image[1]) != '-1':
                    m.path = image[0]
                    m.bmp = image[1]
                else:
                    image[-1] = -1
                    while image[1] == -1:
                        image = 0
                        self.dlg = wx.TextEntryDialog(self, 
                            'You entered an invalid URL for the image path.  Please Enter a valid URL or cancel to leave the old url unchanged')
                        if self.dlg.ShowModal() == wx.ID_OK:
                            path = self.dlg.GetValue()
                            image = self.evaluate(path)
                            if image[1] != -1:
                                m.path = image[0]
                                m.bmp = image[1]
                            self.dlg.Destroy()
                        else: break
            if self.poschoice.GetSelection() !=2:
                if self.poschoice.GetSelection() == 0: m.pos = cmpPoint(self.scx.GetValue(),self.scy.GetValue())
                else:
                    pos = self.positioncombo.GetValue()
                    m.pos = cmpPoint(int(`pos`[2:`pos`.index(",")]),int(`pos`[`pos`.rfind(',')+1:len(`pos`)-2]))
        self.layers["miniatures"].canvas.send_map_data()

    def evaluate(self, ckpath):
        path = []
        if ckpath[:7] != "http://": ckpath = "http://" + ckpath
        path = self.check_path(ckpath)
        return [ckpath, path]

    def check_path(self, path):
        if ImageHandler.Cache.has_key(path): return ImageHandler.Cache[path]
        img = ImageHandler.directLoad(path)
        if img is None: return -1
        return img

    def on_text(self,evt):
        id=evt.GetId()

    def on_spin(self,evt):
        self.poschoice.SetSelection(0)

    def on_combo_box(self,evt):
        self.poschoice.SetSelection(1)

    def on_radio_box(self,evt):
        id=evt.GetId()
        index = evt.GetInt()

    def on_size(self,evt):
        s = self.GetClientSizeTuple()
        self.listsizer.SetDimension(20,20,s[0]-40,s[1]-40)
        self.outline.SetDimensions(5,5,s[0]-10,s[1]-10)

##-----------------------------
## Miniature Prop Panel
##-----------------------------

MIN_LABEL = wx.NewId()
MIN_HEADING = wx.NewId()
MIN_FACE = wx.NewId()
MIN_HIDE = wx.NewId()
MIN_LOCK = wx.NewId()
MIN_ALIGN = wx.NewId()
wxID_MIN_WIDTH = wx.NewId()
wxID_MIN_HEIGHT = wx.NewId()
wxID_MIN_SCALING = wx.NewId()

class min_edit_panel(wx.Panel):
    def __init__(self, parent, min):
        wx.Panel.__init__(self, parent, -1)
        self.min = min
        sizer = wx.StaticBoxSizer(wx.StaticBox(self,-1,"Miniature"), wx.VERTICAL)
        sizerSize = wx.BoxSizer(wx.HORIZONTAL)
        hSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.label = wx.TextCtrl(self, MIN_LABEL, min.label)
        sizer.Add(wx.StaticText(self, -1, "Label:"), 0, wx.EXPAND)
        sizer.Add(self.label, 0, wx.EXPAND)
        sizer.Add(wx.Size(10,10))
        self.heading = wx.RadioBox(self, MIN_HEADING, "Heading", 
            choices=["None","N","NE",
                     "E","SE","S",
                     "SW","W","NW"],majorDimension=5,style=wx.RA_SPECIFY_COLS)
        self.heading.SetSelection(min.heading)
        self.face = wx.RadioBox(self, MIN_FACE, "Facing", 
            choices=["None","N","NE",
                     "E","SE","S",
                     "SW","W","NW"],majorDimension=5,style=wx.RA_SPECIFY_COLS)
        self.face.SetSelection(min.face)
        self.locked = wx.CheckBox(self, MIN_LOCK, " Lock")
        self.locked.SetValue(min.locked)
        self.hide = wx.CheckBox(self, MIN_HIDE, " Hide")
        self.hide.SetValue(min.hide)
        sizer.Add(self.heading, 0, wx.EXPAND)
        sizer.Add(wx.Size(10,10))
        sizer.Add(self.face, 0, wx.EXPAND)
        sizer.Add(wx.Size(10,10))
        #
        #image resizing
        #
        self.min_width_old_value = str(self.min.bmp.GetWidth())
        self.min_width = wx.TextCtrl(self, wxID_MIN_WIDTH, self.min_width_old_value)
        sizerSize.Add(wx.StaticText(self, -1, "Width: "), 0, wx.ALIGN_CENTER)
        sizerSize.Add(self.min_width, 1, wx.EXPAND)
        sizerSize.Add(wx.Size(20, 25))

        #TODO:keep in mind that self.min is a local copy???
        self.min_height_old_value = str(self.min.bmp.GetHeight())
        self.min_height = wx.TextCtrl(self, wxID_MIN_HEIGHT, self.min_height_old_value)
        sizerSize.Add(wx.StaticText(self, -1, "Height: "),0,wx.ALIGN_CENTER)
        sizerSize.Add(self.min_height, 1, wx.EXPAND)
        self.min_scaling = wx.CheckBox(self, wxID_MIN_SCALING, "Lock scaling")
        self.min_scaling.SetValue(True)
        sizerSize.Add(self.min_scaling, 1, wx.EXPAND)
        sizer.Add(sizerSize, 0, wx.EXPAND)
        sizer.Add(wx.Size(10, 10))

        # Now, add the last items on in their own sizer
        hSizer.Add(self.locked, 0, wx.EXPAND)
        hSizer.Add(wx.Size(10,10))
        hSizer.Add(self.hide, 0, wx.EXPAND)

        # Add the hSizer to the main sizer
        sizer.Add( hSizer )
        self.sizer = sizer
        self.SetSizer(self.sizer)
        self.SetAutoLayout(True)
        self.Fit()

        #self.Bind(wx.EVT_SIZE, self.on_size)
        self.Bind(wx.EVT_TEXT, self.on_text, id=MIN_LABEL)
        self.Bind(wx.EVT_TEXT, self.on_scaling, id=wxID_MIN_WIDTH)
        self.Bind(wx.EVT_TEXT, self.on_scaling, id=wxID_MIN_HEIGHT)
        self.Bind(wx.EVT_RADIOBOX, self.on_radio_box, id=MIN_HEADING)
        self.Bind(wx.EVT_RADIOBOX, self.on_radio_box, id=MIN_FACE)

    def on_scaling(self, evt):
        if self.min_scaling.GetValue() == False: return
        elif self.min_width.GetValue() and wxID_MIN_WIDTH == evt.GetId() and self.min_width.GetInsertionPoint():
            self.min_height.SetValue(str(int((float(self.min_width.GetValue()) / float(self.min_width_old_value)) * float(self.min_height_old_value))) )
        elif self.min_height.GetValue() and wxID_MIN_HEIGHT == evt.GetId() and self.min_height.GetInsertionPoint():
            self.min_width.SetValue(str(int((float(self.min_height.GetValue()) / float(self.min_height_old_value)) * float(self.min_width_old_value))) )

    def update_min(self):
        self.min.set_min_props(self.heading.GetSelection(),
                               self.face.GetSelection(),
                               self.label.GetValue(),
                               self.locked.GetValue(),
                               self.hide.GetValue(),
                               self.min_width.GetValue(),
                               self.min_height.GetValue())

    def on_radio_box(self,evt):
        id = evt.GetId()
        index = evt.GetInt()

    def on_text(self,evt):
        id = evt.GetId()

    def on_size(self,evt):
        s = self.GetClientSizeTuple()
        self.sizer.SetDimension(20,20,s[0]-40,s[1]-40)
        self.outline.SetDimensions(5,5,s[0]-10,s[1]-10)

class min_edit_dialog(wx.Dialog):
    def __init__(self,parent,min):
        wx.Dialog.__init__(self,parent,-1,"Miniature",wx.DefaultPosition,wx.Size(520,350))
        (w,h) = self.GetClientSizeTuple()
        mastersizer = wx.BoxSizer(wx.VERTICAL)
        editor = min_edit_panel(self,min)
        self.editor = editor
        mastersizer.Add(editor, 1, wx.EXPAND)
        mastersizer.Add(wx.Size(10,10))
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(wx.Button(self, wx.ID_OK, "OK"), 1, wx.EXPAND)
        sizer.Add(wx.Size(10,10))
        sizer.Add(wx.Button(self, wx.ID_CANCEL, "Cancel"), 1, wx.EXPAND)
        mastersizer.Add(sizer, 0, wx.EXPAND)
        self.SetSizer(mastersizer)
        self.SetAutoLayout(True)
        self.Fit()
        self.Bind(wx.EVT_BUTTON, self.on_ok, id=wx.ID_OK)

    def on_ok(self,evt):
        self.editor.update_min()
        self.EndModal(wx.ID_OK)

