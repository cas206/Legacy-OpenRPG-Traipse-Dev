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
# File: mapper/whiteboard_hander.py
# Author: OpenRPG Team
# Maintainer:
# Version:
#   $Id: token_handler.py,v 1.43 2007/12/07 20:39:50 digitalxero Exp $
#
# Description: Token layer handler; derived from token Layer handler
#
__version__ = "$Id: token_handler.py,v 1.43 2007/12/07 20:39:50 madmathlabs Exp $"

from orpg.mapper.base_handler import *
from tok_dialogs import *
import thread
import time
import mimetypes
import urllib
import xml.dom.minidom as minidom
import wx

## rewrite Grid
from orpg.mapper.grid import GRID_RECTANGLE
from orpg.mapper.grid import GRID_HEXAGON
from orpg.mapper.grid import GRID_ISOMETRIC
import os

from orpg.tools.orpg_settings import settings

## Jesus H! No Face, rotate!
TOK_ROT_LEFT = wx.NewId()
ROT_LEFT_45 = wx.NewId()
LABEL_TOOL = wx.NewId()
LAYER_TOOL = wx.NewId()
TOK_LIST_TOOL = wx.NewId()
TOK_TOOL = wx.NewId()
TOK_URL = wx.NewId()
SERIAL_TOOL = wx.NewId()
TOK_MOVE = wx.NewId()
TOK_REMOVE = wx.NewId()
TOK_PROP_DLG = wx.NewId()
TOK_FACING_NONE = wx.NewId()
TOK_FACING_MATCH = wx.NewId()
TOK_FACING_EAST = wx.NewId()
TOK_FACING_WEST = wx.NewId()
TOK_FACING_NORTH = wx.NewId()
TOK_FACING_SOUTH = wx.NewId()
TOK_FACING_NORTHEAST = wx.NewId()
TOK_FACING_SOUTHEAST = wx.NewId()
TOK_FACING_SOUTHWEST = wx.NewId()
TOK_FACING_NORTHWEST = wx.NewId()
TOK_HEADING_NONE = wx.NewId()
TOK_HEADING_MATCH = wx.NewId()
TOK_HEADING_EAST = wx.NewId()
TOK_HEADING_WEST = wx.NewId()
TOK_HEADING_NORTH = wx.NewId()
TOK_HEADING_SOUTH = wx.NewId()
TOK_HEADING_NORTHEAST = wx.NewId()
TOK_HEADING_SOUTHEAST = wx.NewId()
TOK_HEADING_SOUTHWEST = wx.NewId()
TOK_HEADING_NORTHWEST = wx.NewId()
TOK_HEADING_SUBMENU = wx.NewId()
TOK_FACING_SUBMENU = wx.NewId()
TOK_ALIGN_SUBMENU = wx.NewId()
TOK_ALIGN_GRID_CENTER = wx.NewId()
TOK_ALIGN_GRID_TL = wx.NewId()
TOK_TITLE_HACK = wx.NewId()
TOK_TO_GAMETREE = wx.NewId()
TOK_BACK_ONE = wx.NewId()
TOK_FORWARD_ONE = wx.NewId()
TOK_TO_BACK = wx.NewId()
TOK_TO_FRONT = wx.NewId()
TOK_LOCK_BACK = wx.NewId()
TOK_LOCK_FRONT = wx.NewId()
TOK_FRONTBACK_UNLOCK = wx.NewId()
TOK_ZORDER_SUBMENU = wx.NewId()
TOK_SHOW_HIDE = wx.NewId()
TOK_LOCK_UNLOCK = wx.NewId()
MAP_REFRESH_MINI_URLS = wx.NewId()

class myFileDropTarget(wx.FileDropTarget):
    def __init__(self, handler):
        wx.FileDropTarget.__init__(self)
        self.m_handler = handler
    def OnDropFiles(self, x, y, filenames):
        self.m_handler.on_drop_files(x, y, filenames)

class token_handler(base_layer_handler):

    def __init__(self, parent, id, canvas):
        self.sel_min = None
        self.auto_label = 1
        self.use_serial = 1
        self.auto_label_cb = None
        self.canvas = canvas
        self.settings = settings
        self.mini_rclick_menu_extra_items = {}
        self.background_rclick_menu_extra_items = {}
        base_layer_handler.__init__(self, parent, id, canvas)
        # id is the index of the last good menu choice or 'None'
        # if the last menu was left without making a choice
        # should be -1 at other times to prevent events overlapping
        self.lastMenuChoice = None
        self.drag_mini = None
        self.tooltip_delay_miliseconds = 500
        self.tooltip_timer = wx.CallLater(self.tooltip_delay_miliseconds, self.on_tooltip_timer)
        self.tooltip_timer.Stop()
        dt = myFileDropTarget(self)
        self.canvas.SetDropTarget(dt)
        #wxInitAllImageHandlers()

    def build_ctrls(self):
        base_layer_handler.build_ctrls(self)
        # add controls in reverse order! (unless you want them after the default tools)
        self.auto_label_cb = wx.CheckBox(self, wx.ID_ANY, ' Auto Label ', (-1,-1),(-1,-1))
        self.auto_label_cb.SetValue(self.auto_label)
        self.min_url = wx.ComboBox(self, wx.ID_ANY, "http://", style=wx.CB_DROPDOWN | wx.CB_SORT)
        self.localBrowse = wx.Button(self, wx.ID_ANY, 'Browse', style=wx.BU_EXACTFIT)
        minilist = createMaskedButton( self, dir_struct["icon"]+'questionhead.gif', 'Edit token properties', wx.ID_ANY)
        miniadd = wx.Button(self, wx.ID_OK, "Add Token", style=wx.BU_EXACTFIT)
        self.sizer.Add(self.auto_label_cb,0,wx.ALIGN_CENTER)
        self.sizer.Add((6, 0))
        self.sizer.Add(self.min_url, 1, wx.ALIGN_CENTER)
        self.sizer.Add((6, 0))
        self.sizer.Add(miniadd, 0, wx.ALIGN_CENTER)
        self.sizer.Add((6, 0))
        self.sizer.Add(self.localBrowse, 0, wx.ALIGN_CENTER)
        self.sizer.Add((6, 0))
        self.sizer.Add(minilist, 0, wx.ALIGN_CENTER)
        self.Bind(wx.EVT_BUTTON, self.on_min_list, minilist)
        self.Bind(wx.EVT_BUTTON, self.on_token, miniadd)
        self.Bind(wx.EVT_BUTTON, self.on_browse, self.localBrowse)
        self.Bind(wx.EVT_CHECKBOX, self.on_label, self.auto_label_cb)

    def on_browse(self, evt):
        if not self.role_is_gm_or_player(): return
        dlg = wx.FileDialog(None, "Select a Token to load", dir_struct["user"]+'webfiles/', 
            wildcard="Image files (*.bmp, *.gif, *.jpg, *.png)|*.bmp;*.gif;*.jpg;*.png", style=wx.OPEN)
        if not dlg.ShowModal() == wx.ID_OK:
            dlg.Destroy()
            return
        file = open(dlg.GetPath(), "rb")
        imgdata = file.read()
        file.close()
        filename = dlg.GetFilename()
        (imgtype,j) = mimetypes.guess_type(filename)
        postdata = urllib.urlencode({'filename':filename, 'imgdata':imgdata, 'imgtype':imgtype})

        ## Removal of Remote Server?
        if self.settings.get_setting('LocalorRemote') == 'Remote':
            # make the new mini appear in top left of current viewable map
            dc = wx.ClientDC(self.canvas)
            self.canvas.PrepareDC(dc)
            dc.SetUserScale(self.canvas.layers['grid'].mapscale,self.canvas.layers['grid'].mapscale)
            x = dc.DeviceToLogicalX(0)
            y = dc.DeviceToLogicalY(0)
            thread.start_new_thread(self.canvas.layers['token'].upload, 
                                    (postdata, dlg.GetPath()), {'pos':cmpPoint(x,y)})
        else:
            try: min_url = component.get("cherrypy") + filename
            except: return #chat.InfoPost('CherryPy is not started!')
            min_url = dlg.GetDirectory().replace(dir_struct["user"]+'webfiles' + os.sep, 
                component.get("cherrypy")) + '/' + filename
            # build url
            if min_url == "" or min_url == "http://": return
            if min_url[:7] != "http://": min_url = "http://" + min_url
            # make label
            if self.auto_label and min_url[-4:-3] == '.':
                start = min_url.rfind("/") + 1
                min_label = min_url[start:len(min_url)-4]
                if self.use_serial: min_label = '%s %d' % ( min_label, self.canvas.layers['token'].next_serial() )
            else: min_label = ""
            if self.min_url.FindString(min_url) == -1: self.min_url.Append(min_url)
            try:
                id = 'mini-' + self.canvas.frame.session.get_next_id()
                # make the new mini appear in top left of current viewable map
                dc = wx.ClientDC(self.canvas)
                self.canvas.PrepareDC(dc)
                dc.SetUserScale(self.canvas.layers['grid'].mapscale,self.canvas.layers['grid'].mapscale)
                x = dc.DeviceToLogicalX(0)
                y = dc.DeviceToLogicalY(0)
                self.canvas.layers['token'].add_token(id, min_url, pos=cmpPoint(x,y), label=min_label)
            except:
                # When there is an exception here, we should be decrementing the serial_number for reuse!!
                unablemsg= "Unable to load/resolve URL: " + min_url + " on resource \"" + min_label + "\"!!!\n\n"
                dlg = wx.MessageDialog(self,unablemsg, 'Url not found',wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                self.canvas.layers['token'].rollback_serial()
            self.canvas.send_map_data()
            self.canvas.Refresh(False)


    def build_menu(self,label = "Token"):
        ## Menu Changes: Rotate
        ## Menu into Component
        ## Remove To GameTree option
        base_layer_handler.build_menu(self,label)
        self.main_menu.AppendSeparator()
        self.main_menu.Append(LABEL_TOOL,"&Auto label","",1)
        self.main_menu.Check(LABEL_TOOL,self.auto_label)
        self.main_menu.Append(SERIAL_TOOL,"&Number minis","",1)
        self.main_menu.Check(SERIAL_TOOL, self.use_serial)
        self.main_menu.Append(MAP_REFRESH_MINI_URLS,"&Refresh tokens")       #  Add the menu item
        self.main_menu.AppendSeparator()
        self.main_menu.Append(TOK_MOVE, "Move")
        self.canvas.Bind(wx.EVT_MENU, self.on_map_board_menu_item, id=MAP_REFRESH_MINI_URLS) #  Set the handler
        self.canvas.Bind(wx.EVT_MENU, self.on_label, id=LABEL_TOOL)
        self.canvas.Bind(wx.EVT_MENU, self.on_serial, id=SERIAL_TOOL)
        # build token menu
        self.min_menu = wx.Menu()
        # Rectangles and hexagons require slightly different menus because of
        # facing and heading possibilities.

        rot_left = wx.Menu()
        rot_left_45 = rot_left.Append(-1, '45*')
        self.canvas.Bind(wx.EVT_MENU, self.rot_left_45, rot_left_45)
        rot_right = wx.Menu()

        rot_right_45 = rot_right.Append(-1, '45*')
        self.canvas.Bind(wx.EVT_MENU, self.rot_right_45, rot_right_45)
        ## Replace with Rotate. Left - Right, 45 - 90 degress.
        """
        face_menu = wx.Menu()
        face_menu.Append(TOK_FACING_NONE,"&None")
        face_menu.Append(TOK_FACING_NORTH,"&North")
        face_menu.Append(TOK_FACING_NORTHEAST,"Northeast")
        face_menu.Append(TOK_FACING_EAST,"East")
        face_menu.Append(TOK_FACING_SOUTHEAST,"Southeast")
        face_menu.Append(TOK_FACING_SOUTH,"&South")
        face_menu.Append(TOK_FACING_SOUTHWEST,"Southwest")
        face_menu.Append(TOK_FACING_WEST,"West")
        face_menu.Append(TOK_FACING_NORTHWEST,"Northwest")
        """
        ###

        heading_menu = wx.Menu()
        heading_menu.Append(TOK_HEADING_NONE,"&None")
        heading_menu.Append(TOK_HEADING_NORTH,"&North")
        heading_menu.Append(TOK_HEADING_NORTHEAST,"Northeast")
        heading_menu.Append(TOK_HEADING_EAST,"East")
        heading_menu.Append(TOK_HEADING_SOUTHEAST,"Southeast")
        heading_menu.Append(TOK_HEADING_SOUTH,"&South")
        heading_menu.Append(TOK_HEADING_SOUTHWEST,"Southwest")
        heading_menu.Append(TOK_HEADING_WEST,"West")
        heading_menu.Append(TOK_HEADING_NORTHWEST,"Northwest")

        align_menu = wx.Menu()
        align_menu.Append(TOK_ALIGN_GRID_CENTER,"&Center")
        align_menu.Append(TOK_ALIGN_GRID_TL,"&Top-Left")
        #  This is a hack to simulate a menu title, due to problem in Linux
        if wx.Platform == '__WXMSW__': self.min_menu.SetTitle(label)
        else:
            self.min_menu.Append(TOK_TITLE_HACK,label)
            self.min_menu.AppendSeparator()
        self.min_menu.Append(TOK_SHOW_HIDE,"Show / Hide")
        self.min_menu.Append(TOK_LOCK_UNLOCK, "Lock / Unlock")
        self.min_menu.Append(TOK_REMOVE,"&Remove")

        ##Remove
        #self.min_menu.Append(TOK_TO_GAMETREE,"To &Gametree")
        ###

        self.min_menu.AppendMenu(TOK_HEADING_SUBMENU,"Set &Heading",heading_menu)

        ##Remove
        self.min_menu.AppendMenu(TOK_ROT_LEFT,"&Rotate Left",rot_left)
        self.min_menu.AppendMenu(wx.ID_ANY,"&Rotate Right",rot_right)
        ###

        self.min_menu.AppendMenu(TOK_ALIGN_SUBMENU,"Snap-to &Alignment",align_menu)
        self.min_menu.AppendSeparator()
        zorder_menu = wx.Menu()
        zorder_menu.Append(TOK_BACK_ONE,"Back one")
        zorder_menu.Append(TOK_FORWARD_ONE,"Forward one")
        zorder_menu.Append(TOK_TO_BACK,"To back")
        zorder_menu.Append(TOK_TO_FRONT,"To front")
        zorder_menu.AppendSeparator()
        zorder_menu.Append(TOK_LOCK_BACK,"Lock to back")
        zorder_menu.Append(TOK_LOCK_FRONT,"Lock to front")
        zorder_menu.Append(TOK_FRONTBACK_UNLOCK,"Unlock Front/Back")
        self.min_menu.AppendMenu(TOK_ZORDER_SUBMENU, "Token Z-Order",zorder_menu)
        #self.min_menu.Append(TOK_LOCK,"&Lock")
        self.min_menu.AppendSeparator()
        self.min_menu.Append(TOK_PROP_DLG,"&Properties")


        #self.min_menu.AppendSeparator()
        #self.min_menu.Append(TOK_MOVE, "Move")

        self.canvas.Bind(wx.EVT_MENU, self.on_min_menu_item, id=TOK_MOVE)
        self.canvas.Bind(wx.EVT_MENU, self.on_min_menu_item, id=TOK_SHOW_HIDE)
        self.canvas.Bind(wx.EVT_MENU, self.on_min_menu_item, id=TOK_LOCK_UNLOCK)
        self.canvas.Bind(wx.EVT_MENU, self.on_min_menu_item, id=TOK_REMOVE)

        ##Remove
        #self.canvas.Bind(wx.EVT_MENU, self.on_min_menu_item, id=TOK_TO_GAMETREE)
        ###

        #self.canvas.Bind(wx.EVT_MENU, self.on_min_menu_item, id=TOK_LOCK)
        self.canvas.Bind(wx.EVT_MENU, self.on_min_menu_item, id=TOK_PROP_DLG)

        ##Remove
        self.canvas.Bind(wx.EVT_MENU, self.on_min_menu_item, id=TOK_FACING_NONE)
        self.canvas.Bind(wx.EVT_MENU, self.on_min_menu_item, id=TOK_FACING_EAST)
        self.canvas.Bind(wx.EVT_MENU, self.on_min_menu_item, id=TOK_FACING_WEST)
        self.canvas.Bind(wx.EVT_MENU, self.on_min_menu_item, id=TOK_FACING_NORTH)
        self.canvas.Bind(wx.EVT_MENU, self.on_min_menu_item, id=TOK_FACING_SOUTH)
        self.canvas.Bind(wx.EVT_MENU, self.on_min_menu_item, id=TOK_FACING_NORTHEAST)
        self.canvas.Bind(wx.EVT_MENU, self.on_min_menu_item, id=TOK_FACING_SOUTHEAST)
        self.canvas.Bind(wx.EVT_MENU, self.on_min_menu_item, id=TOK_FACING_SOUTHWEST)
        self.canvas.Bind(wx.EVT_MENU, self.on_min_menu_item, id=TOK_FACING_NORTHWEST)
        ###

        self.canvas.Bind(wx.EVT_MENU, self.on_min_menu_item, id=TOK_HEADING_NONE)
        self.canvas.Bind(wx.EVT_MENU, self.on_min_menu_item, id=TOK_HEADING_EAST)
        self.canvas.Bind(wx.EVT_MENU, self.on_min_menu_item, id=TOK_HEADING_WEST)
        self.canvas.Bind(wx.EVT_MENU, self.on_min_menu_item, id=TOK_HEADING_NORTH)
        self.canvas.Bind(wx.EVT_MENU, self.on_min_menu_item, id=TOK_HEADING_SOUTH)
        self.canvas.Bind(wx.EVT_MENU, self.on_min_menu_item, id=TOK_HEADING_NORTHEAST)
        self.canvas.Bind(wx.EVT_MENU, self.on_min_menu_item, id=TOK_HEADING_SOUTHEAST)
        self.canvas.Bind(wx.EVT_MENU, self.on_min_menu_item, id=TOK_HEADING_SOUTHWEST)
        self.canvas.Bind(wx.EVT_MENU, self.on_min_menu_item, id=TOK_HEADING_NORTHWEST)
        self.canvas.Bind(wx.EVT_MENU, self.on_min_menu_item, id=TOK_ALIGN_GRID_CENTER)
        self.canvas.Bind(wx.EVT_MENU, self.on_min_menu_item, id=TOK_ALIGN_GRID_TL)
        self.canvas.Bind(wx.EVT_MENU, self.on_min_menu_item, id=TOK_BACK_ONE)
        self.canvas.Bind(wx.EVT_MENU, self.on_min_menu_item, id=TOK_FORWARD_ONE)
        self.canvas.Bind(wx.EVT_MENU, self.on_min_menu_item, id=TOK_TO_BACK)
        self.canvas.Bind(wx.EVT_MENU, self.on_min_menu_item, id=TOK_TO_FRONT)
        self.canvas.Bind(wx.EVT_MENU, self.on_min_menu_item, id=TOK_LOCK_BACK)
        self.canvas.Bind(wx.EVT_MENU, self.on_min_menu_item, id=TOK_LOCK_FRONT)
        self.canvas.Bind(wx.EVT_MENU, self.on_min_menu_item, id=TOK_FRONTBACK_UNLOCK)
        ######### add plugin added menu items #########
        if len(self.mini_rclick_menu_extra_items)>0:
            self.min_menu.AppendSeparator()
            for item in self.mini_rclick_menu_extra_items.items(): self.min_menu.Append(item[1], item[0])
        if len(self.background_rclick_menu_extra_items)>0:
            self.main_menu.AppendSeparator()
            for item in self.background_rclick_menu_extra_items.items():
                self.main_menu.Append(item[1], item[0])

    def do_min_menu(self,pos):
        self.canvas.PopupMenu(self.min_menu,pos)

    def rot_left_45(self, evt):
        #self.sel_rmin.rotate += 0.785
        self.sel_rmin.rotate += 1.046
        #component.get('drawn')[self.sel_rmin] = False

    def rot_right_45(self, evt):
        #self.sel_rmin.rotate -= 0.785
        self.sel_rmin.rotate -= 1.046

    def do_min_select_menu(self, min_list, pos):
        # to prevent another event being processed
        self.lastMenuChoice = None
        self.min_select_menu = wx.Menu()
        self.min_select_menu.SetTitle("Select Token")
        loop_count = 1
        try:
            for m in min_list:
                # Either use the token label for the selection list
                if m.label: self.min_select_menu.Append(loop_count, m.label)
                # Or use part of the images filename as an identifier
                else:
                    string_split = string.split(m.path,"/",)
                    last_string = string_split[len(string_split)-1]
                    self.min_select_menu.Append(loop_count, 'Unlabeled - ' + last_string[:len(last_string)-4])
                self.canvas.Bind(wx.EVT_MENU, self.min_selected, id=loop_count)
                loop_count += 1
            self.canvas.PopupMenu(self.min_select_menu,pos)
        except: pass

    def min_selected(self,evt):
        # this is the callback function for the menu that is used to choose
        # between minis when you right click, left click or left double click
        # on a stack of two or more
        self.canvas.Refresh(False)
        self.canvas.send_map_data()
        self.lastMenuChoice = evt.GetId()-1

    def on_min_menu_item(self,evt):
        id = evt.GetId()
        if id == TOK_MOVE:
            if self.sel_min:
                self.moveSelectedMini(self.last_rclick_pos)
                self.deselectAndRefresh()
            return
        elif id == TOK_REMOVE: self.canvas.layers['token'].del_token(self.sel_rmin)

        ##Remove
        elif id == TOK_TO_GAMETREE:
            min_xml = self.sel_rmin.toxml(action="new")
            node_begin = "<nodehandler module='map_token_nodehandler' class='map_token_handler' name='"
            if self.sel_rmin.label: node_begin += self.sel_rmin.label + "'"
            else:  node_begin += "Unnamed token'"
            node_begin += ">"
	    gametree = component.get('tree')
            node_xml = node_begin + min_xml + '</nodehandler>'
            #print "Sending this XML to insert_xml:" + node_xml
            gametree.insert_xml(str(node_xml))

        elif id == TOK_SHOW_HIDE:
            if self.sel_rmin.hide:  self.sel_rmin.hide = 0
            else: self.sel_rmin.hide = 1
        elif id == TOK_LOCK_UNLOCK:
            if self.sel_rmin.locked: self.sel_rmin.locked = False
            else: self.sel_rmin.locked = True
            if self.sel_rmin == self.sel_min:
                # when we lock / unlock the selected mini make sure it isn't still selected
                # or it might easily get moved by accident and be hard to move back
                self.sel_min.selected = False
                self.sel_min.isUpdated = True
                self.sel_min = None
	recycle_bin = {TOK_HEADING_NONE: FACE_NONE, TOK_HEADING_NORTH: FACE_NORTH, 
        TOK_HEADING_NORTHWEST: FACE_NORTHWEST, TOK_HEADING_NORTHEAST: FACE_NORTHEAST, 
        TOK_HEADING_EAST: FACE_EAST, TOK_HEADING_SOUTHEAST: FACE_SOUTHEAST, TOK_HEADING_SOUTHWEST: FACE_SOUTHWEST, 
        TOK_HEADING_SOUTH: FACE_SOUTH, TOK_HEADING_WEST: FACE_WEST}
	if recycle_bin.has_key(id):
	    self.sel_rmin.heading = recycle_bin[id]
	    del recycle_bin
	recycle_bin = {TOK_FACING_NONE: FACE_NONE, TOK_FACING_NORTH: FACE_NORTH, 
        TOK_FACING_NORTHWEST: FACE_NORTHWEST, TOK_FACING_NORTHEAST: FACE_NORTHEAST, 
        TOK_FACING_EAST: FACE_EAST, TOK_FACING_SOUTHEAST: FACE_SOUTHEAST, TOK_FACING_SOUTHWEST: FACE_SOUTHWEST, 
        TOK_FACING_SOUTH: FACE_SOUTH, TOK_FACING_WEST: FACE_WEST}
	if recycle_bin.has_key(id):
	    self.sel_rmin.face = recycle_bin[id]
	    del recycle_bin
        elif id == TOK_ALIGN_GRID_CENTER: self.sel_rmin.snap_to_align = SNAPTO_ALIGN_CENTER
        elif id == TOK_ALIGN_GRID_TL: self.sel_rmin.snap_to_align = SNAPTO_ALIGN_TL
        elif id == TOK_PROP_DLG:
            old_lock_value = self.sel_rmin.locked
            dlg = min_edit_dialog(self.canvas.frame.GetParent(),self.sel_rmin)
            if dlg.ShowModal() == wx.ID_OK:
                if self.sel_rmin == self.sel_min and self.sel_rmin.locked != old_lock_value:
                    # when we lock / unlock the selected mini make sure it isn't still selected
                    # or it might easily get moved by accident and be hard to move back
                    self.sel_min.selected = False
                    self.sel_min.isUpdated = True
                    self.sel_min = None
                self.canvas.Refresh(False)
                self.canvas.send_map_data()
                return

        elif id == TOK_BACK_ONE:
            #  This assumes that we always start out with a z-order
            #     that starts at 0 and goes up to the number of
            #     minis - 1.  If this isn't the case, then execute
            #     a self.canvas.layers['token'].collapse_zorder()
            #     before getting the oldz to test
            #  Save the selected minis current z-order
            oldz = self.sel_rmin.zorder
            # Make sure the mini isn't sticky front or back
            if (oldz != TOK_STICKY_BACK) and (oldz != TOK_STICKY_FRONT):
		##   print "old z-order = " + str(oldz)
                self.sel_rmin.zorder -= 1
                #  Re-collapse to normalize
                #  Note:  only one update (with the final values) will be sent
                self.canvas.layers['token'].collapse_zorder()

        elif id == TOK_FORWARD_ONE:
            #  This assumes that we always start out with a z-order
            #     that starts at 0 and goes up to the number of
            #     minis - 1.  If this isn't the case, then execute
            #     a self.canvas.layers['token'].collapse_zorder()
            #     before getting the oldz to test
            #  Save the selected minis current z-order
            oldz = self.sel_rmin.zorder
	    ##  print "old z-order = " + str(oldz)
            self.sel_rmin.zorder += 1

            #  Re-collapse to normalize
            #  Note:  only one update (with the final values) will be sent
            self.canvas.layers['token'].collapse_zorder()

        elif id == TOK_TO_FRONT:
            #  This assumes that we always start out with a z-order
            #     that starts at 0 and goes up to the number of
            #     minis - 1.  If this isn't the case, then execute
            #     a self.canvas.layers['token'].collapse_zorder()
            #     before getting the oldz to test
            #  Save the selected minis current z-order
            oldz = self.sel_rmin.zorder

            # Make sure the mini isn't sticky front or back
            if (oldz != TOK_STICKY_BACK) and (oldz != TOK_STICKY_FRONT):
	    ##  print "old z-order = " + str(oldz)
                #  The new z-order will be one more than the last index
                newz = len(self.canvas.layers['token'].token)
	    ##  print "new z-order = " + str(newz)
                self.sel_rmin.zorder = newz
                #  Re-collapse to normalize
                #  Note:  only one update (with the final values) will be sent
                self.canvas.layers['token'].collapse_zorder()

        elif id == TOK_TO_BACK:
            #  This assumes that we always start out with a z-order
            #     that starts at 0 and goes up to the number of
            #     minis - 1.  If this isn't the case, then execute
            #     a self.canvas.layers['token'].collapse_zorder()
            #     before getting the oldz to test
            #  Save the selected minis current z-order
            oldz = self.sel_rmin.zorder
            # Make sure the mini isn't sticky front or back
            if (oldz != TOK_STICKY_BACK) and (oldz != TOK_STICKY_FRONT):
	    ##  print "old z-order = " + str(oldz)

                #  Since 0 is the lowest in a normalized order, be one less
                newz = -1
	    ##  print "new z-order = " + str(newz)
                self.sel_rmin.zorder = newz
                #  Re-collapse to normalize
                #  Note:  only one update (with the final values) will be sent
                self.canvas.layers['token'].collapse_zorder()

        elif id == TOK_FRONTBACK_UNLOCK:
            #print "Unlocked/ unstickified..."
            if self.sel_rmin.zorder == TOK_STICKY_BACK: self.sel_rmin.zorder = TOK_STICKY_BACK + 1
            elif self.sel_rmin.zorder == TOK_STICKY_FRONT: self.sel_rmin.zorder = TOK_STICKY_FRONT - 1
        elif id == TOK_LOCK_BACK: self.sel_rmin.zorder = TOK_STICKY_BACK
        elif id == TOK_LOCK_FRONT: self.sel_rmin.zorder = TOK_STICKY_FRONT
        # Pretty much, we always want to refresh when we go through here
        # This helps us remove the redundant self.Refresh() on EVERY menu event
        # that we process above.
        self.sel_rmin.isUpdated = True
        self.canvas.Refresh(False)
        self.canvas.send_map_data()

    def on_token(self, evt):
        session = self.canvas.frame.session
        if (session.my_role() != session.ROLE_GM) and (session.my_role() != session.ROLE_PLAYER) and (session.use_roles()):
            self.infoPost("You must be either a player or GM to use the token Layer")
            return
        min_url = self.min_url.GetValue()
        # build url
        if min_url == "" or min_url == "http://": return
        if min_url[:7] != "http://" : min_url = "http://" + min_url
        # make label
        if self.auto_label and min_url[-4:-3] == '.':
            start = min_url.rfind("/") + 1
            min_label = min_url[start:len(min_url)-4]
            if self.use_serial:
                min_label = '%s %d' % ( min_label, self.canvas.layers['token'].next_serial() )
        else: min_label = ""
        if self.min_url.FindString(min_url) == -1: self.min_url.Append(min_url)
        try:
            id = 'mini-' + self.canvas.frame.session.get_next_id()
            # make the new mini appear in top left of current viewable map
            dc = wx.ClientDC(self.canvas)
            self.canvas.PrepareDC(dc)
            dc.SetUserScale(self.canvas.layers['grid'].mapscale,self.canvas.layers['grid'].mapscale)
            x = dc.DeviceToLogicalX(0)
            y = dc.DeviceToLogicalY(0)
            self.canvas.layers['token'].add_token(id, min_url, pos=cmpPoint(x,y), label=min_label)
        except:
            # When there is an exception here, we should be decrementing the serial_number for reuse!!
            unablemsg= "Unable to load/resolve URL: " + min_url + " on resource \"" + min_label + "\"!!!\n\n"
            #print unablemsg
            dlg = wx.MessageDialog(self,unablemsg, 'Url not found',wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.canvas.layers['token'].rollback_serial()
        self.canvas.send_map_data()
        self.canvas.Refresh(False)
        #except Exception, e:
            #wx.MessageBox(str(e),"token Error")

    def on_label(self,evt):
        self.auto_label = not self.auto_label
        self.auto_label_cb.SetValue(self.auto_label)
        #self.send_map_data()
        #self.Refresh()

    def on_min_list(self,evt):
        session = self.canvas.frame.session
        if (session.my_role() != session.ROLE_GM):
            self.infoPost("You must be a GM to use this feature")
            return
        #d = min_list_panel(self.frame.GetParent(),self.canvas.layers,"token list")
        d = min_list_panel(self.canvas.frame,self.canvas.layers,"token list")
        if d.ShowModal() == wx.ID_OK: d.Destroy()
        self.canvas.Refresh(False)

    def on_serial(self, evt):
        self.use_serial = not self.use_serial

    def on_map_board_menu_item(self,evt):
        id = evt.GetId()
        if id == MAP_REFRESH_MINI_URLS:   # Note: this doesn't change the mini, so no need to update the map
            for mini in self.canvas.layers['token'].tokens:       #  For all minis
                mini.set_bmp(ImageHandler.load(mini.path, 'token', mini.id))      #  Reload their bmp member
            self.canvas.Refresh(False)

####################################################################
    ## old functions, changed an awful lot

    def on_left_down(self, evt):
        if not self.role_is_gm_or_player() or self.alreadyDealingWithMenu(): return
        mini = self.find_mini(evt, evt.CmdDown() and self.role_is_gm())
        if mini:
            deselecting_selected_mini = (mini == self.sel_min) #clicked on the selected mini
            self.deselectAndRefresh()
            self.drag_mini = mini
            if deselecting_selected_mini: return
            self.sel_min = mini
            self.sel_min.selected = True
            self.canvas.Refresh()
        else:
            self.drag_mini = None
            pos = self.getLogicalPosition(evt)
            self.moveSelectedMini(pos)
            self.deselectAndRefresh()

    def on_right_down(self, evt):
        if not self.role_is_gm_or_player() or self.alreadyDealingWithMenu(): return
        self.last_rclick_pos = self.getLogicalPosition(evt)
        mini = self.find_mini(evt, evt.CmdDown() and self.role_is_gm())
        if mini:
            self.sel_rmin = mini
            if self.sel_min: self.min_menu.Enable(TOK_MOVE, True)
            else: self.min_menu.Enable(TOK_MOVE, False)
            self.prepare_mini_rclick_menu(evt)
            self.do_min_menu(evt.GetPosition())
        else:# pass it on
            if self.sel_min: self.main_menu.Enable(TOK_MOVE, True)
            else: self.main_menu.Enable(TOK_MOVE, False)
            self.prepare_background_rclick_menu(evt)
            base_layer_handler.on_right_down(self, evt)

####################################################################
    ## new functions

    def on_drop_files(self, x, y, filepaths):
        # currently we ignore multiple files
        filepath = filepaths[0]
        start1 = filepath.rfind("\\") + 1 # check for both slashes in path to be on the safe side
        start2 = filepath.rfind("/") + 1
        if start1 < start2: start1 = start2
        filename = filepath[start1:]
        pos = filename.rfind('.')
        ext = filename[pos:].lower()
        #ext = filename[-4:].lower()
        if(ext != ".bmp" and ext != ".gif" and ext != ".jpg" and ext != ".jpeg" and ext != ".png"):
            self.infoPost("Supported file extensions are: *.bmp, *.gif, *.jpg, *.jpeg, *.png")
            return
        file = open(filepath, "rb")
        imgdata = file.read()
        file.close()
        dc = wx.ClientDC(self.canvas)
        self.canvas.PrepareDC(dc)
        dc.SetUserScale(self.canvas.layers['grid'].mapscale,self.canvas.layers['grid'].mapscale)
        x = dc.DeviceToLogicalX(x)
        y = dc.DeviceToLogicalY(y)
        (imgtype,j) = mimetypes.guess_type(filename)
        postdata = urllib.urlencode({'filename':filename, 'imgdata':imgdata, 'imgtype':imgtype})
        thread.start_new_thread(self.canvas.layers['token'].upload, (postdata, filepath), {'pos':cmpPoint(x,y)})

    def on_tooltip_timer(self, *args):
        pos = args[0]
        dc = wx.ClientDC(self.canvas)
        self.canvas.PrepareDC(dc)
        dc.SetUserScale(self.canvas.layers['grid'].mapscale,self.canvas.layers['grid'].mapscale)
        pos = wx.Point(dc.DeviceToLogicalX(pos.x), dc.DeviceToLogicalY(pos.y))
        mini_list = self.getMiniListOrSelectedMini(pos)
        if len(mini_list) > 0:
            print mini_list
            tooltip = self.get_mini_tooltip(mini_list); print tooltip
            self.canvas.SetToolTipString(tooltip)
        else: self.canvas.SetToolTipString("")

    def on_motion(self,evt):
        if evt.Dragging() and evt.LeftIsDown():
            if self.canvas.drag is None and self.drag_mini is not None:
                drag_bmp = self.drag_mini.bmp
                if self.drag_mini.width and self.drag_mini.height:
                    tmp_image = drag_bmp.ConvertToImage()
                    tmp_image.Rescale(int(self.drag_mini.width * self.canvas.layers['grid'].mapscale), 
                        int(self.drag_mini.height * self.canvas.layers['grid'].mapscale))
                    tmp_image.ConvertAlphaToMask()

                    ### Should show rotated image when dragging.
                    if self.drag_mini.rotate != 0 :
                        tmp_image = tmp_image.Rotate(self.drag_mini.rotate, 
                                                    (self.drag_mini.width/2, self.drag_mini.height/2))

                    drag_bmp = tmp_image.ConvertToBitmap()
                    mask = wx.Mask(drag_bmp, wx.Colour(tmp_image.GetMaskRed(), 
                        tmp_image.GetMaskGreen(), tmp_image.GetMaskBlue()))
                    drag_bmp.SetMask(mask)
                    tmp_image = tmp_image.ConvertToGreyscale()
                    self.drag_mini.gray = True
                    self.drag_mini.isUpdated = True
                    def refresh():
                        self.canvas.drag.Hide()
                        self.canvas.Refresh(False)
                    wx.CallAfter(refresh)
                self.canvas.drag = wx.DragImage(drag_bmp)
                self.drag_offset = self.getLogicalPosition(evt)- self.drag_mini.pos
                self.canvas.drag.BeginDrag((int(self.drag_offset.x * self.canvas.layers['grid'].mapscale), 
                    int(self.drag_offset.y * self.canvas.layers['grid'].mapscale)), self.canvas, False)
            elif self.canvas.drag is not None:
                self.canvas.drag.Move(evt.GetPosition())
                self.canvas.drag.Show()
        # reset tool tip timer
        self.canvas.SetToolTipString("")
        self.tooltip_timer.Restart(self.tooltip_delay_miliseconds, evt.GetPosition())

    def on_left_up(self,evt):
        if self.canvas.drag:
            self.canvas.drag.Hide()
            self.canvas.drag.EndDrag()
            self.canvas.drag = None
            pos = self.getLogicalPosition(evt)
            pos = pos - self.drag_offset
            if self.canvas.layers['grid'].snap:
                nudge = int(self.canvas.layers['grid'].unit_size/2)
                if self.canvas.layers['grid'].mode != GRID_ISOMETRIC:
                    if self.drag_mini.snap_to_align == SNAPTO_ALIGN_CENTER:
                        pos = pos + (int(self.drag_mini.bmp.GetWidth()/2),int(self.drag_mini.bmp.GetHeight()/2))
                    else: pos = pos + (nudge, nudge)
                else:# GRID_ISOMETRIC
                    if self.drag_mini.snap_to_align == SNAPTO_ALIGN_CENTER:
                        pos = pos + (int(self.drag_mini.bmp.GetWidth()/2), self.drag_mini.bmp.GetHeight())
                    else: pass # no nudge for the isomorphic / top-left
            self.sel_min = self.drag_mini
            # check to see if the mouse is inside the window still
            w = self.canvas.GetClientSizeTuple() # this is the window size, minus any scrollbars
            p = evt.GetPosition() # compare the window size, w with the non-logical position
            c = self.canvas.size # this is the grid size, compare with the logical position, pos
            # both are [width, height]
            if p.x>=0 and pos.x<c[0] and p.x<w[0] and p.y>=0 and pos.y<c[1] and p.y<w[1]:
                self.moveSelectedMini(pos)
            self.sel_min.gray = False
            self.sel_min.selected = False
            self.sel_min.isUpdated = True
            self.canvas.Refresh(False)
            self.canvas.send_map_data()
            self.sel_min = None
        self.drag_mini = None

    def on_left_dclick(self,evt):
        if not self.role_is_gm_or_player() or self.alreadyDealingWithMenu(): return
        mini = self.find_mini(evt, evt.CmdDown() and self.role_is_gm())
        if mini: self.on_mini_dclick(evt, mini)
        else: base_layer_handler.on_left_dclick(self, evt)


####################################################################
    ## hook functions (although with python you can override any of the functions)

    def prepare_mini_rclick_menu(self, evt):
        # override the entire right-click on a mini menu
        pass

    def prepare_background_rclick_menu(self, evt):
        # override the entire right-click on the map menu
        pass

    def get_mini_tooltip(self, mini_list):
        # override to create a tooltip
        return ""

    def on_mini_dclick(self, evt, mini):
        # do something after the mini was left double clicked
        pass

####################################################################
    ## easy way to add a single menu item

    def set_mini_rclick_menu_item(self, label, callback_function):
        # remember you might want to call these at the end of your callback function:
        # mini_handler.sel_rmin.isUpdated = True
        # canvas.Refresh(False)
        # canvas.send_map_data()
        if callback_function == None: del self.mini_rclick_menu_extra_items[label]
        else:
            if not self.mini_rclick_menu_extra_items.has_key(label):
                self.mini_rclick_menu_extra_items[label]=wx.NewId()
            menu_id = self.mini_rclick_menu_extra_items[label]
            self.canvas.Bind(wx.EVT_MENU, callback_function, id=menu_id)
        self.build_menu()

    def set_background_rclick_menu_item(self, label, callback_function):
        if callback_function == None: del self.background_rclick_menu_extra_items[label]
        else:
            if not self.background_rclick_menu_extra_items.has_key(label):
                self.background_rclick_menu_extra_items[label]=wx.NewId()
            menu_id = self.background_rclick_menu_extra_items[label]
            self.canvas.Bind(wx.EVT_MENU, callback_function, id=menu_id)
        self.build_menu()


####################################################################
    ## helper functions

    def infoPost(self, message):
        component.get("chat").InfoPost(message)

    def role_is_gm_or_player(self):
        session = self.canvas.frame.session
        if (session.my_role() <> session.ROLE_GM) and (session.my_role() <> session.ROLE_PLAYER) and (session.use_roles()):
            self.infoPost("You must be either a player or GM to use the token Layer")
            return False
        return True

    def role_is_gm(self):
        session = self.canvas.frame.session
        if (session.my_role() <> session.ROLE_GM) and (session.use_roles()): return False
        return True

    def alreadyDealingWithMenu(self):
        return self.lastMenuChoice is not None

    def getLastMenuChoice(self):
        choice = self.lastMenuChoice
        self.lastMenuChoice = None
        return choice

    def getLogicalPosition(self, evt):
        dc = wx.ClientDC(self.canvas)
        self.canvas.PrepareDC(dc)
        dc.SetUserScale(self.canvas.layers['grid'].mapscale,self.canvas.layers['grid'].mapscale)
        pos = evt.GetLogicalPosition(dc)
        return pos

    def getMiniListOrSelectedMini(self, pos, include_locked=False):
        if self.sel_min and self.sel_min.hit_test(pos):
            # clicked on the selected mini - assume that is the intended target
            # and don't give a choice of it and any other minis stacked with it
            mini_list = []
            mini_list.append(self.sel_min)
            return mini_list
        mini_list = self.canvas.layers['token'].find_token(pos, (not include_locked))
        if mini_list: return mini_list
        mini_list = []
        return mini_list

    def deselectAndRefresh(self):
        if self.sel_min:
            self.sel_min.selected = False
            self.sel_min.isUpdated = True
            self.canvas.Refresh(False)
            self.canvas.send_map_data()
            self.sel_min = None

    def moveSelectedMini(self, pos):
        if self.sel_min: self.moveMini(pos, self.sel_min)

    def moveMini(self, pos, mini):
        grid = self.canvas.layers['grid']
        mini.pos = grid.get_snapped_to_pos(pos, mini.snap_to_align, mini.bmp.GetWidth(), mini.bmp.GetHeight())

    def find_mini(self, evt, include_locked):
        if not self.role_is_gm_or_player() or self.alreadyDealingWithMenu(): return
        pos = self.getLogicalPosition(evt)
        mini_list = self.getMiniListOrSelectedMini(pos, include_locked)
        mini = None
        if len(mini_list) > 1:
            try: self.do_min_select_menu(mini_list, evt.GetPosition())
            except: pass
            choice = self.getLastMenuChoice()
            if choice == None: return None # left menu without making a choice, eg by clicking outside menu
            mini = mini_list[choice]
        elif len(mini_list) == 1: mini = mini_list[0]
        return mini

