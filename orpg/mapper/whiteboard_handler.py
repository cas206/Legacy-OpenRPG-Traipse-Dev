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
#   $Id: whiteboard_handler.py,v Traipse 'Ornery-Orc' prof.ebral Exp $
#
# Description: Whiteboard layer handler
#
__version__ = "$Id: whiteboard_handler.py,v Traipse 'Ornery-Orc' prof.ebral Exp $"

from base_handler import *
from math import floor, sqrt

class whiteboard_handler(base_layer_handler):
    def __init__(self, parent, id, canvas):
        self.drawing_mode = 'Freeform'
        self.line_string = "0,0;"
        self.drawing = False
        self.upperleft = wx.Point(0,0)
        self.lowerright = wx.Point(0,0)
        #polyline drawing vars
        self.polypoints = 0
        self.lastpoint = None
        self.selected = None
        #text drawing vars
        self.style = str(wx.NORMAL)
        self.weight = str(wx.NORMAL)
        self.pointsize = str(12)
        self.text_selected_item = None
        #self.r_h = RGBHex()
        base_layer_handler.__init__(self, parent, id, canvas)
        self.build_text_properties_menu()
        self.wb = self.canvas.layers['whiteboard']
        self.temp_circle = None
        self.cone_start = None
        self.temp_edge1 = None
        self.temp_edge2 = None

    def build_ctrls(self):
        base_layer_handler.build_ctrls(self)
        self.color_button = wx.Button(self, wx.ID_ANY, "Pen Color", style=wx.BU_EXACTFIT)
        self.color_button.SetBackgroundColour(wx.BLACK)
        self.color_button.SetForegroundColour(wx.WHITE)
        self.drawmode_ctrl = wx.Choice(self, wx.ID_ANY, choices = ["Freeform", "Polyline","Text", "Cone", "Circle"])
        self.drawmode_ctrl.SetSelection(0) #always start showing "Freeform"
        self.radius = wx.TextCtrl(self, wx.ID_ANY, size=(32,-1) )
        self.radius.SetValue("15")
        self.live_refresh = wx.CheckBox(self, wx.ID_ANY, " Live Refresh")
        self.live_refresh.SetValue(True)
        self.widthList= wx.Choice(self, wx.ID_ANY, size= wx.Size(40, 20), 
                                        choices=['1','2','3','4','5','6','7','8','9','10'])
        self.widthList.SetSelection(0)
        self.sizer.Add(wx.StaticText(self, wx.ID_ANY, "Line Width: "),0,wx.ALIGN_CENTER)
        self.sizer.Add(self.widthList, 0, wx.EXPAND)
        self.sizer.Add(wx.Size(10,25))
        self.sizer.Add(wx.StaticText(self, wx.ID_ANY, "Drawing Mode: "),0,wx.ALIGN_CENTER)
        self.sizer.Add(self.drawmode_ctrl, 0, wx.EXPAND)
        self.sizer.Add(wx.StaticText(self, -1, " Radius: "), 0, wx.ALIGN_CENTER|wx.ALL, 3)
        self.sizer.Add(self.radius, 0, wx.EXPAND|wx.ALL, 2)
        self.sizer.Add(wx.Size(10,25))
        self.sizer.Add(self.live_refresh, 0, wx.EXPAND)
        self.sizer.Add(wx.Size(20,25))
        self.sizer.Add(self.color_button, 0, wx.EXPAND)
        self.sizer.Add(wx.Size(20,25))
        self.Bind(wx.EVT_MOTION, self.on_motion)
        self.Bind(wx.EVT_CHOICE, self.check_draw_mode, self.drawmode_ctrl)
        self.Bind(wx.EVT_BUTTON, self.on_pen_color, self.color_button)
        self.Bind(wx.EVT_CHOICE, self.on_pen_width, self.widthList)

    def build_text_properties_menu(self, label="Text Properties"):
        self.text_properties_dialog = wx.Dialog(self, -1, "Text Properties",  name = "Text Properties")
        self.text_props_sizer = wx.BoxSizer(wx.VERTICAL)
        okay_boxer = wx.BoxSizer(wx.HORIZONTAL)
        okay_button = wx.Button(self.text_properties_dialog, wx.ID_OK, "APPLY")
        cancel_button = wx.Button(self.text_properties_dialog, wx.ID_CANCEL,"CANCEL")
        okay_boxer.Add(okay_button, 1, wx.ALIGN_LEFT)
        okay_boxer.Add(wx.Size(10,10))
        okay_boxer.Add(cancel_button, 1, wx.ALIGN_RIGHT)
        self.txt_boxer = wx.BoxSizer(wx.HORIZONTAL)
        self.txt_static = wx.StaticText(self.text_properties_dialog, -1, "Text: ")
        self.text_control = wx.TextCtrl(self.text_properties_dialog, wx.ID_ANY, "", name = "Text: ")
        self.txt_boxer.Add(self.txt_static,0,wx.EXPAND)
        self.txt_boxer.Add(wx.Size(10,10))
        self.txt_boxer.Add(self.text_control,1,wx.EXPAND)
        self.point_boxer = wx.BoxSizer(wx.HORIZONTAL)
        self.point_static = wx.StaticText(self.text_properties_dialog, -1, "Text Size: ")
        self.point_control = wx.SpinCtrl(self.text_properties_dialog, 
                                        wx.ID_ANY, value = "12",
                                        min = 1, initial = 12, 
                                        name = "Font Size: ")
        self.point_boxer.Add(self.point_static,1,wx.EXPAND)
        self.point_boxer.Add(wx.Size(10,10))
        self.point_boxer.Add(self.point_control,0,wx.EXPAND)
        self.text_color_control = wx.Button(self.text_properties_dialog, wx.ID_ANY, "TEXT COLOR",style=wx.BU_EXACTFIT)
        self.weight_control = wx.RadioBox(self.text_properties_dialog, wx.ID_ANY, "Weight", choices = ["Normal","Bold"])
        self.style_control = wx.RadioBox(self.text_properties_dialog, wx.ID_ANY, "Style", choices = ["Normal", "Italic"])
        self.text_props_sizer.Add(self.txt_boxer,0,wx.EXPAND)
        self.text_props_sizer.Add(self.point_boxer,0, wx.EXPAND)
        self.text_props_sizer.Add(self.weight_control,0, wx.EXPAND)
        self.text_props_sizer.Add(self.style_control,0, wx.EXPAND)
        self.text_props_sizer.Add(self.text_color_control, 0, wx.EXPAND)
        self.text_props_sizer.Add(wx.Size(10,10))
        self.text_props_sizer.Add(okay_boxer,0, wx.EXPAND)
        self.text_props_sizer.Fit(self)
        self.text_properties_dialog.SetSizer(self.text_props_sizer)
        self.text_properties_dialog.Fit()
        self.text_properties_dialog.Bind(wx.EVT_BUTTON, self.on_text_color, self.text_color_control)
        self.text_properties_dialog.Bind(wx.EVT_BUTTON, self.on_text_properties, okay_button)
        #self.text_properties_dialog.Destroy()

    def build_menu(self, label = "Whiteboard"):
        base_layer_handler.build_menu(self,label)
        self.main_menu.AppendSeparator()
        item = wx.MenuItem(self.main_menu, wx.ID_ANY, "&Change Pen Color", "Change Pen Color")
        self.canvas.Bind(wx.EVT_MENU, self.on_pen_color, item)
        self.main_menu.AppendItem(item)
        item = wx.MenuItem(self.main_menu, wx.ID_ANY, "Delete &All Lines", "Delete All Lines")
        self.canvas.Bind(wx.EVT_MENU, self.delete_all_lines, item)
        self.main_menu.AppendItem(item)
        item = wx.MenuItem(self.main_menu, wx.ID_ANY, "&Undo Last Deleted Line", "Undo Last Deleted Line")
        self.canvas.Bind(wx.EVT_MENU, self.undo_line, item)
        self.main_menu.AppendItem(item)
        self.line_menu = wx.Menu("Whiteboard Line")
        self.line_menu.SetTitle("Whiteboard Line")
        item = wx.MenuItem(self.line_menu, wx.ID_ANY, "&Remove", "Remove")
        self.canvas.Bind(wx.EVT_MENU, self.on_line_menu_item, item)
        self.line_menu.AppendItem(item)
        self.text_menu = wx.Menu("Whiteboard Text")
        self.text_menu.SetTitle("Whiteboard Text")
        item = wx.MenuItem(self.text_menu, wx.ID_ANY, "&Properties", "Properties")
        self.canvas.Bind(wx.EVT_MENU, self.get_text_properties, item)
        self.text_menu.AppendItem(item)
        item = wx.MenuItem(self.text_menu, wx.ID_ANY, "&Remove", "Remove")
        self.canvas.Bind(wx.EVT_MENU, self.on_text_menu_item, item)
        self.text_menu.AppendItem(item)

    def do_line_menu(self,pos):
        self.canvas.PopupMenu(self.line_menu, pos)

    def item_selected(self,evt):
        item = evt.GetId()
        self.item_selection = self.selection_list[item]

    def on_text_properties(self,evt):
        text_string = self.text_control.GetValue()
        if self.style_control.GetStringSelection() == 'Normal': style = wx.NORMAL
        else: style = wx.ITALIC
        if self.weight_control.GetStringSelection() == 'Normal': weight = wx.NORMAL
        else: weight = wx.BOLD
        point = str(self.point_control.GetValue())
        c = self.text_color_control.GetForegroundColour()
        color = self.canvas.layers['whiteboard'].r_h.hexstring(c.Red(), c.Green(), c.Blue())
        self.text_selected_item.set_text_props(text_string, style, point, weight, color)
        self.text_to_xml()
        self.text_properties_dialog.Show(False)
        self.text_selected_item.selected = False
        self.text_selected_item.isUpdated = True
        self.text_selected_item = None

    def on_text_color(self,evt):
        dlg = wx.ColourDialog(self)
        if dlg.ShowModal() == wx.ID_OK:
            c = dlg.GetColourData()
            self.text_color_control.SetForegroundColour(c.GetColour())
        dlg.Destroy()

    def text_to_xml(self):
        xml_str = "<map><whiteboard>"
        xml_str += self.text_selected_item.toxml('update')
        xml_str += "</whiteboard></map>"
        self.canvas.frame.session.send(xml_str)
        self.canvas.Refresh(False)

    def get_text_properties(self, event=None):
        self.text_color_control.SetForegroundColour(self.text_selected_item.textcolor)
        self.text_control.SetValue(self.text_selected_item.text_string)
        self.point_control.SetValue(int(self.text_selected_item.pointsize))
        if int(self.text_selected_item.weight) == wx.NORMAL: self.weight_control.SetSelection(0)
        else: self.weight_control.SetSelection(1)

        if int(self.text_selected_item.style) == wx.NORMAL: self.style_control.SetSelection(0)
        else: self.style_control.SetSelection(1)
        self.text_properties_dialog.Center()
        self.text_properties_dialog.Show(True)

    def do_text_menu(self, pos, items=None):
        if items == None: self.canvas.PopupMenu(self.text_menu)
        else:
            menu = wx.Menu()
            self.ItemList = items
            self.tmpPos = pos
            for i in xrange(len(items)):
                menu.Append(i+1, items[i].text_string)
                self.canvas.Bind(wx.EVT_MENU, self.onItemSelect, id=i+1)
            self.canvas.PopupMenu(menu)
        return

    def onItemSelect(self, evt):
        id = evt.GetId()-1
        self.text_selected_item = self.ItemList[id]
        self.text_selected_item.selected = True
        if self.tmpPos == 'right': self.canvas.PopupMenu(self.text_menu)
        self.ItemList = None
        self.tmpPos = None

    def on_right_down(self,evt):
        line = 0
        scale = self.canvas.layers['grid'].mapscale
        dc = wx.ClientDC(self.canvas)
        self.canvas.PrepareDC(dc)
        dc.SetUserScale(scale,scale)
        pos = evt.GetLogicalPosition(dc)
        if self.drawing_mode == 'Text': self.on_text_right_down(evt, dc)
        elif self.drawing and ((self.drawing_mode == 'Circle') or (self.drawing_mode == 'Cone')):
            self.check_draw_mode()
            self.drawing = False
        elif (self.drawing_mode == 'Freeform') or (self.drawing_mode == 'Polyline') or (self.drawing_mode == 'Circle') or (self.drawing_mode == 'Cone'):
            line_list = self.canvas.layers['whiteboard'].find_line(pos)
            if line_list:
                self.sel_rline = self.canvas.layers['whiteboard'].get_line_by_id(line_list.id)
                if self.sel_rline:
                    self.do_line_menu(evt.GetPosition())
                    self.canvas.Refresh(False)
            else: base_layer_handler.on_right_down(self,evt)
        else: base_layer_handler.on_right_down(self,evt)
        del dc

    def on_pen_color(self,evt):
        data = wx.ColourData()
        data.SetChooseFull(True)
        dlg = wx.ColourDialog(self.canvas, data)
        if dlg.ShowModal() == wx.ID_OK:
            data = dlg.GetColourData()
            color = data.GetColour()
            self.canvas.layers['whiteboard'].setcolor(color)
            self.color_button.SetBackgroundColour(color)
        dlg.Destroy()

    def on_pen_width(self,evt):
        width = int(self.widthList.GetStringSelection())
        self.canvas.layers['whiteboard'].setwidth(width)

    def undo_line(self,evt):
        session = self.canvas.frame.session
        if (session.my_role() != session.ROLE_GM) and (session.use_roles()):
            self.top_frame.openrpg.get("chat").InfoPost("You must be a GM to use this feature")
            return
        self.canvas.layers['whiteboard'].undo_line()
        dc = self.create_dc()
        self.un_highlight(dc)
        self.selected = None
        del dc  

    def delete_all_lines(self,evt):
        session = self.canvas.frame.session
        if (session.my_role() != session.ROLE_GM) and (session.use_roles()):
            component.get("chat").InfoPost("You must be a GM to use this feature")
            return
        dlg = wx.MessageDialog(self, 
                                "Are you sure you want to delete all lines?","Delete All Lines", 
                                wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION)
        if dlg.ShowModal() != wx.ID_YES: return
        self.canvas.layers['whiteboard'].del_all_lines()
        dc = self.create_dc()
        self.un_highlight(dc)
        self.selected = None
        del dc

    def on_line_menu_item(self, evt):
        dc = self.create_dc()
        self.un_highlight(dc)
        self.canvas.layers['whiteboard'].del_line(self.sel_rline)
        self.selected = None
        del dc

    def on_text_menu_item(self, evt):
        dc = self.create_dc()
        self.un_highlight(dc)
        self.canvas.layers['whiteboard'].del_text(self.selected)
        self.selected = None
        del dc

    # Check Draw Mode
    # Queries the GUI to see what mode to draw in
    # 05-09-2003 Snowdog

    def check_draw_mode(self, evt=None):
        self.drawing_mode = self.drawmode_ctrl.GetStringSelection()

        #because mode can be changed while a polyline is being created
        #clear the current linestring and reset the polyline data
        self.upperleft.x = self.upperleft.y = 0
        self.lowerright.x = self.lowerright.y = 0
        self.lastpoint = None #because the end check function is not called we must force its lastpoint var to None again
        self.polypoints = 0
        self.line_string = "0,0;"
        if self.temp_circle:
            self.canvas.layers['whiteboard'].del_temp_line(self.temp_circle)
            if self.selected == self.temp_circle: self.selected = None
            self.canvas.Refresh(True)
        self.temp_circle = None
        self.cone_start  = None

    # Altered on_left_up to toggle between
    # drawing modes freeform vs polyline
    # 05-09-2003  Snowdog
    def on_left_down(self,evt):
        if not self.drawing: self.check_draw_mode()
        if self.drawing_mode == 'Freeform': pass
        elif self.drawing_mode == 'Polyline': self.polyline_add_point( evt )
        elif self.drawing_mode == 'Text': self.on_text_left_down(evt)
        elif self.drawing_mode == 'Cone':
            if self.cone_start == None: self.on_start_cone(evt)
            else: self.draw_temporary_cone(evt)
        elif self.drawing_mode == 'Circle': self.draw_temporary_circle(evt)

    # Added handling for double clicks within the map
    # 05-09-2003  Snowdog
    def on_left_dclick(self, evt):
        if self.drawing_mode == 'Freeform': pass #Freeform mode ignores the double click
        elif self.drawing_mode == 'Polyline': self.polyline_last_point( evt )
        elif self.drawing_mode == 'Text': pass
        elif self.drawing_mode == 'Circle' or self.drawing_mode == 'Cone':
            self.canvas.layers['whiteboard'].del_temp_line(self.temp_circle)
            #pointArray = self.temp_circle.line_string.split(";")
            self.canvas.layers['whiteboard'].add_line(self.temp_circle.line_string)
            self.temp_circle = None
            self.cone_start  = None
            self.drawing = False

    # Altered on_left_up to toggle between
    # drawing modes freeform vs polyline
    # 05-09-2003  Snowdog
    def on_left_up(self,evt):
        if self.drawing_mode == 'Freeform': self.on_freeform_left_up(evt)
        elif self.drawing_mode == 'Polyline': pass
        elif self.drawing_mode == 'Text': pass

    # Altered on_left_up to toggle between
    # drawing modes freeform vs polyline
    # 05-09-2003  Snowdog
    def on_motion(self,evt):
        session = self.canvas.frame.session
        if (session.my_role() != session.ROLE_GM) \
            and (session.my_role()!=session.ROLE_PLAYER) \
            and (session.use_roles()):
            return
        if self.drawing_mode == 'Freeform':
            if evt.m_leftDown: self.freeform_motion(evt)
        elif self.drawing_mode == 'Polyline':
            if self.drawing: self.polyline_preview( evt )
        dc = self.create_dc()
        pos = evt.GetLogicalPosition(dc)
        hit = self.canvas.layers['whiteboard'].hit_test_lines(pos,dc)
        if hit: self.highlight(hit,dc)
        else:
            self.un_highlight(dc)
            hit = self.canvas.layers['whiteboard'].hit_test_text(pos,dc)
            if hit: self.highlight(hit,dc)
            else: self.un_highlight(dc)
        del dc

    def create_dc(self):
        scale = self.canvas.layers['grid'].mapscale
        dc = wx.ClientDC( self.canvas )
        self.canvas.PrepareDC( dc )
        dc.SetUserScale(scale,scale)
        return dc

    def highlight(self,hit,dc):
        if self.selected:
            self.selected.highlight(False)
            self.selected.draw(self.wb,dc)
        self.selected = hit[0]
        self.selected.highlight()
        self.selected.draw(self.wb,dc)

    def un_highlight(self,dc):
        if self.selected:
            self.selected.highlight(False)
            self.selected.draw(self.wb,dc)

    # Polyline Add Point
    # adds a new point to the polyline
    # 05-09-2003  Snowdog
    def polyline_add_point(self, evt):
        scale = self.canvas.layers['grid'].mapscale
        dc = wx.ClientDC( self.canvas )
        self.canvas.PrepareDC( dc )
        dc.SetUserScale(scale,scale)
        pos = evt.GetLogicalPosition(dc)
        #reset the bounding points
        if pos.x < self.upperleft.x: self.upperleft.x = pos.x
        elif pos.x > self.lowerright.x: self.lowerright.x = pos.x
        if pos.y < self.upperleft.y: self.upperleft.y = pos.y
        elif pos.y > self.lowerright.y: self.lowerright.y = pos.y

        #if this point doens't end the line
        #add a new point into the line string
        if not self.polyline_end_check( pos ):
            if self.drawing == True:
                self.polypoints += 1 #add one to the point counter.
                self.line_string += `pos.x` + "," + `pos.y` + ";"
                self.canvas.layers['whiteboard'].draw_working_line(dc,self.line_string)
            else: #start of line...
                self.polypoints += 1 #add one to the point counter.
                self.line_string = `pos.x` + "," + `pos.y` + ";"
                self.upperleft.x = pos.x
                self.upperleft.y = pos.y
                self.lowerright.x = pos.x
                self.lowerright.y = pos.y
                self.drawing = True
        else: #end of line. Send and reset vars for next line
            self.drawing = False
            if self.polypoints < 2: pass
            else:
                #have enough points to create valid line
                #check to role to make sure user can draw at all....
                session = self.canvas.frame.session
                if (session.my_role() != session.ROLE_GM) and (session.my_role()!=session.ROLE_PLAYER) and (session.use_roles()):
                    component.get("chat").InfoPost("You must be either a player or GM to use this feature")
                    self.canvas.Refresh(False)
                else: line = self.canvas.layers['whiteboard'].add_line(self.line_string,self.upperleft,self.lowerright)
            #resetting variables for next line
            self.upperleft.x = self.upperleft.y = 0
            self.lowerright.x = self.lowerright.y = 0
            self.polypoints = 0
            self.line_string = "0,0;"

    # Polyline Last Point
    # adds a final point to the polyline and ends it
    # 05-09-2003  Snowdog
    def polyline_last_point(self, evt):
        #if we haven't started a line already. Ignore the click
        if self.drawing != True: return
        scale = self.canvas.layers['grid'].mapscale
        dc = wx.ClientDC( self.canvas )
        self.canvas.PrepareDC( dc )
        dc.SetUserScale(scale,scale)
        pos = evt.GetLogicalPosition(dc)
        #reset the bounding points
        if pos.x < self.upperleft.x: self.upperleft.x = pos.x
        elif pos.x > self.lowerright.x: self.lowerright.x = pos.x
        if pos.y < self.upperleft.y: self.upperleft.y = pos.y
        elif pos.y > self.lowerright.y: self.lowerright.y = pos.y
        self.polypoints += 1 #add one to the point counter.
        self.line_string += `pos.x` + "," + `pos.y` + ";"
        self.canvas.layers['whiteboard'].draw_working_line(dc,self.line_string)
        #end of line. Send and reset vars for next line
        self.drawing = False
        if self.polypoints < 2: pass
        else:
            #have enough points to create valid line
            #check to role to make sure user can draw at all....
            session = self.canvas.frame.session
            if (session.my_role() != session.ROLE_GM) and (session.my_role()!=session.ROLE_PLAYER) and (session.use_roles()):
                component.get("chat").InfoPost("You must be either a player or GM to use this feature")
                self.canvas.Refresh(False)
            else: line = self.canvas.layers['whiteboard'].add_line(self.line_string,self.upperleft,self.lowerright)
        #resetting variables for next line
        self.upperleft.x = self.upperleft.y = 0
        self.lowerright.x = self.lowerright.y = 0
        self.lastpoint = None #becuase the end check function is not called we must force its lastpoint var to None again
        self.polypoints = 0
        self.line_string = "0,0;"

    # Polyline End Check
    # checks to see if a double click has occured
    # a second click on the LAST polyline point
    # (or very close proximity) should cause the
    # polyline even to complete and send
    # 05-09-2003  Snowdog
    def polyline_end_check(self, pos):
        # check to see if the position of the give point is within POLYLINE_END_TOLERANCE
        # if it is then the line has been completed and should be sent to the map just like
        # the original freeform version is. A line with fewer than 2 points should be ignored
        x_in = y_in = 0
        tol = 5

        #first point check
        if type(self.lastpoint) == type(None): self.lastpoint = wx.Point(pos.x,pos.y); return 0 #not end of line
        if ((self.lastpoint.x -tol) <= pos.x <= (self.lastpoint.x)): x_in = 1
        if ((self.lastpoint.y -tol) <= pos.y <= (self.lastpoint.y)): y_in = 1
        if x_in and y_in: self.lastpoint = None; return 1
        #if we've reached here the point is NOT a terminal point. Reset the lastpoint and return False
        self.lastpoint.x = pos.x
        self.lastpoint.y = pos.y
        return 0

    # Polyline Preview
    # display a temporary/momentary line to the user
    # from the last point to mouse position
    # 05-09-2003  Snowdog
    def polyline_preview(self, evt):
        if self.drawing != True: return
        if self.live_refresh.GetValue() == 0: return
        scale = self.canvas.layers['grid'].mapscale
        dc = wx.ClientDC( self.canvas )
        self.canvas.PrepareDC( dc )
        dc.SetUserScale(scale,scale)
        pos = evt.GetLogicalPosition(dc)

        #reset the bounding points
        if pos.x < self.upperleft.x: self.upperleft.x = pos.x
        elif pos.x > self.lowerright.x: self.lowerright.x = pos.x
        if pos.y < self.upperleft.y: self.upperleft.y = pos.y
        elif pos.y > self.lowerright.y: self.lowerright.y = pos.y

        #redraw the line with a line connected to the cursor
        temp_string = self.line_string
        temp_string += `pos.x` + "," + `pos.y` + ";"
        self.canvas.layers['whiteboard'].draw_working_line(dc,temp_string)
        self.canvas.Refresh(True)

    # moved original on_motion to this function
    # to allow alternate drawing method to be used
    # 05-09-2003  Snowdog
    def freeform_motion(self, evt):
        #if not self.drawing:
        #    return
        scale = self.canvas.layers['grid'].mapscale
        dc = wx.ClientDC( self.canvas )
        self.canvas.PrepareDC( dc )
        dc.SetUserScale(scale,scale)
        pos = evt.GetLogicalPosition(dc)
        if pos.x < self.upperleft.x: self.upperleft.x = pos.x
        elif pos.x > self.lowerright.x: self.lowerright.x = pos.x
        if pos.y < self.upperleft.y: self.upperleft.y = pos.y
        elif pos.y > self.lowerright.y: self.lowerright.y = pos.y
        if evt.m_leftDown:
            if self.drawing == True:
                self.line_string += `pos.x` + "," + `pos.y` + ";"
                self.canvas.layers['whiteboard'].draw_working_line(dc,self.line_string)
            else:
                self.line_string = `pos.x` + "," + `pos.y` + ";"
                self.upperleft.x = pos.x
                self.upperleft.y = pos.y
                self.lowerright.x = pos.x
                self.lowerright.y = pos.y
            self.drawing = True
        del dc

    # moved original on_left_up to this function
    # to allow alternate drawing method to be used
    # 05-09-2003  Snowdog
    def on_freeform_left_up(self,evt):
        if self.drawing == True:
            self.drawing = False
            session = self.canvas.frame.session
            if (session.my_role() != session.ROLE_GM) and (session.my_role()!=session.ROLE_PLAYER) and (session.use_roles()):
                component.get("chat").InfoPost("You must be either a player or GM to use this feature")
                self.canvas.Refresh(False)
                return
            line = self.canvas.layers['whiteboard'].add_line(self.line_string,self.upperleft,self.lowerright)
            dc = self.create_dc()
            for m in range(30):
                line.highlight()
                line.draw(self.wb,dc)
                line.highlight(False)
                line.draw(self.wb,dc)
            del dc
            self.upperleft.x = self.upperleft.y = 0
            self.lowerright.x = self.lowerright.y = 0

    def on_text_left_down(self, evt):
        session = self.canvas.frame.session
        if (session.my_role() != session.ROLE_GM) and (session.my_role()!=session.ROLE_PLAYER) and (session.use_roles()):
            component.get("chat").InfoPost("You must be either a player or GM to use this feature")
            self.canvas.Refresh(False)
            return
        scale = self.canvas.layers['grid'].mapscale
        dc = wx.ClientDC( self.canvas )
        self.canvas.PrepareDC( dc )
        dc.SetUserScale(scale,scale)
        pos = evt.GetLogicalPosition(dc)
        test_text = self.canvas.layers['whiteboard'].hit_test_text(pos,dc)
        if len(test_text) > 0:
            if len(test_text) > 1: self.do_text_menu('left', test_text)
            else:
                self.text_selected_item = test_text[0]
                self.text_selected_item.selected = True
            self.canvas.Refresh(True)
        else:
            if self.text_selected_item == None:
                dlg = wx.TextEntryDialog(self,"Text to add to whiteboard", caption="Enter text",defaultValue=" ")
                if dlg.ShowModal() == wx.ID_OK:
                    text_string = dlg.GetValue()
                    self.canvas.layers['whiteboard'].add_text(text_string,pos, self.style, 
                        self.pointsize, self.weight, self.canvas.layers['whiteboard'].color)
            else:
                self.text_selected_item.posx = pos.x
                self.text_selected_item.posy = pos.y
                self.text_selected_item.isUpdated = True
                self.text_to_xml()
                self.text_selected_item.selected = False
                self.text_selected_item = None
        del dc

    def on_text_right_down(self, evt, dc):
        session = self.canvas.frame.session
        if (session.my_role() != session.ROLE_GM) and (session.my_role()!=session.ROLE_PLAYER) and (session.use_roles()):
            component.get("chat").InfoPost("You must be either a player or GM to use this feature")
            self.canvas.Refresh(False)
            return
        pos = evt.GetLogicalPosition(dc)
        test_text = self.canvas.layers['whiteboard'].hit_test_text(pos, dc)
        if len(test_text) > 0:
            if len(test_text) > 1: self.do_text_menu('right', test_text)
            else:
                self.text_selected_item = test_text[0]
                self.do_text_menu('right')

    def on_start_cone(self, evt):
        session = self.canvas.frame.session
        if (session.my_role() != session.ROLE_GM) and (session.my_role()!=session.ROLE_PLAYER) and (session.use_roles()):
            component.get("chat").InfoPost("You must be either a player or GM to use this feature")
            self.canvas.Refresh(False)
            return
        self.cone_start = self.get_snapped_to_logical_pos(evt)
        self.drawing = True

    def get_snapped_to_logical_pos(self, evt):
        scale = self.canvas.layers['grid'].mapscale
        dc = wx.ClientDC( self.canvas )
        self.canvas.PrepareDC( dc )
        dc.SetUserScale(scale,scale)
        pos = evt.GetLogicalPosition(dc)
        if self.canvas.layers['grid'].snap:
            size = self.canvas.layers['grid'].unit_size
            pos.x = int((pos.x+size/2)/size)*size
            pos.y = int((pos.y+size/2)/size)*size
        return pos

    def draw_temporary_cone(self, evt):
        scale = self.canvas.layers['grid'].mapscale
        dc = wx.ClientDC( self.canvas )
        self.canvas.PrepareDC( dc )
        dc.SetUserScale(scale,scale)
        pos = evt.GetLogicalPosition(dc)
        pos2 = self.get_snapped_to_logical_pos(evt)
        size = self.canvas.layers['grid'].unit_size #60
        if abs(pos.x-pos2.x)<=size/10 and abs(pos.y-pos2.y)<=size/10: pos = pos2
        radius = int(int(self.radius.GetValue())/5) 
        curve  = self.calculate_circle(self.cone_start, radius, size)
        edge1 = []
        edge2 = []
        horizontal_inc = wx.Point(size,0)
        if pos.x <= self.cone_start.x: horizontal_inc = wx.Point(-size,0)
        vertical_inc = wx.Point(0,size)
        if pos.y <= self.cone_start.y: vertical_inc = wx.Point(0,-size)
        x_diff = float(pos.x - self.cone_start.x)
        y_diff = float(pos.y - self.cone_start.y)
        ratio = float(1)
        if abs(x_diff) <= abs(y_diff): ratio = x_diff / y_diff
        elif abs(y_diff) < abs(x_diff):
            ratio = -(y_diff / x_diff)
            horizontal_inc,vertical_inc = vertical_inc,horizontal_inc #swap
        horizontal_rotated = wx.Point(-horizontal_inc.y, horizontal_inc.x)
        vertical_rotated   = wx.Point(-vertical_inc.y,   vertical_inc.x)
        on_diagonal = True
        for v in range(radius):
            x = int(floor((v+1)*ratio)) - int(floor(v*ratio))
            if x < 0 and on_diagonal:
                edge1 += [vertical_inc]
                edge1 += [horizontal_inc]
            elif x != 0:
                edge1 += [horizontal_inc]
                edge1 += [vertical_inc]
            else:
                edge1 += [vertical_inc]
                on_diagonal = False
        on_diagonal = True
        for v in range(radius):
            x = int(floor((v+1)*(-ratio))) - int(floor(v*(-ratio)))
            if x < 0 and on_diagonal:
                edge2 += [vertical_rotated]
                edge2 += [horizontal_rotated]
            elif x != 0:
                edge2 += [horizontal_rotated]
                edge2 += [vertical_rotated]
            else:
                edge2 += [vertical_rotated]
                on_diagonal = False
        p = wx.Point(0,0)
        string1 =  self.point_to_string(p, [self.cone_start])
        string1 += self.point_to_string(p, edge1)
        p = wx.Point(0,0)
        string2 =  self.point_to_string(p, [self.cone_start])
        string2 += self.point_to_string(p, edge2)

        # truncate the edges where they meet the curve
        pointArray = string1.split(";")
        string1 = ""
        for p in pointArray:
            p += ";"
            index = (";"+curve).find(";"+p)
            if index >= 0:
                # found intersection, start circle at intersection
                curve = curve[index:]+curve[:index]
                break
            string1 += p

        # truncate the edges where they meet the curve
        pointArray = string2.split(";")
        string2 = ""
        for p in pointArray:
            p += ";"
            string2 = p + string2 #backwards
            index = (";"+curve).find(";"+p)
            if index >= 0:
                # found intersection, end circle at intersection
                curve = curve[:index]
                break
        curve = string1 + curve + string2

        # add the lines that define the real cone edges
        sz = sqrt(x_diff*x_diff + y_diff*y_diff)
        x_diff = radius*size*x_diff/sz
        y_diff = radius*size*y_diff/sz
        pos = wx.Point(self.cone_start.x+x_diff, self.cone_start.y+y_diff)
        qos = wx.Point(self.cone_start.x-y_diff, self.cone_start.y+x_diff)# 90 degree rotation
        curve = `pos.x`+","+`pos.y`+";" + curve + `qos.x`+","+`qos.y`+";"
        if(self.temp_circle):
            self.canvas.layers['whiteboard'].del_temp_line(self.temp_circle)
            if self.selected == self.temp_circle: self.selected = None
        self.temp_circle = self.canvas.layers['whiteboard'].add_temp_line(curve)
        self.canvas.Refresh(True)

    def draw_temporary_circle(self, evt):
        session = self.canvas.frame.session
        if (session.my_role() != session.ROLE_GM) and (session.my_role()!=session.ROLE_PLAYER) and (session.use_roles()):
            component.get("chat").InfoPost("You must be either a player or GM to use this feature")
            self.canvas.Refresh(False)
            return
        pos = self.get_snapped_to_logical_pos(evt)
        size = self.canvas.layers['grid'].unit_size #60
        radius = int(int(self.radius.GetValue())/5)
        center = wx.Point(pos.x, pos.y+size*radius)
        curve  = self.calculate_circle(center, radius, size)
        if(self.temp_circle):
            self.canvas.layers['whiteboard'].del_temp_line(self.temp_circle)
            self.selected = None
        self.temp_circle = self.canvas.layers['whiteboard'].add_temp_line(curve)
        self.drawing = True
        self.canvas.Refresh(True)

    def calculate_circle(self, center, radius, size):
        pos = wx.Point(center.x, center.y-size*radius)
        r = int(radius+2/3)
        right = wx.Point(size,0)
        left  = wx.Point(-size,0)
        up    = wx.Point(0,-size)
        down  = wx.Point(0,size)
        v1 = ([right, down, right]*r)[:radius]
        v2 = ([down, right, down]*r)[r*3-radius:]
        v3 = ([down, left, down]*r)[:radius]
        v4 = ([left, down, left]*r)[r*3-radius:]
        v5 = ([left, up, left]*r)[:radius]
        v6 = ([up, left, up]*r)[r*3-radius:]
        v7 = ([up, right, up]*r)[:radius]
        v8 = ([right, up, right]*r)[r*3-radius:]
        p = wx.Point(0,0)
        temp_string =  self.point_to_string(p, [pos])
        temp_string += self.point_to_string(p, v1+v2+v3+v4+v5+v6+v7+v8)
        return temp_string
        
    def point_to_string(self, pos, vec):
        str = ""
        for i in range(len(vec)):
            pos.x = pos.x + vec[i].x
            pos.y = pos.y + vec[i].y
            str += `pos.x` + "," + `pos.y` + ";"
        return str

