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
# File: rpg_grid.py
# Author: Chris Davis
# Maintainer:
# Version:
#   $Id: rpg_grid.py,v 1.20 2006/11/15 12:11:24 digitalxero Exp $
#
# Description: The file contains code for the grid nodehanlers
#

__version__ = "$Id: rpg_grid.py,v 1.20 2006/11/15 12:11:24 digitalxero Exp $"

from core import *
from forms import *
from orpg.minidom import Element, Text

class rpg_grid_handler(node_handler):
    """ Node handler for rpg grid tool
<nodehandler module='rpg_grid' class='rpg_grid_handler' name='sample'>
  <grid border='' autosize='1' >
    <row>
      <cell size='?'></cell>
      <cell></cell>
    </row>
    <row>
      <cell></cell>
      <cell></cell>
    </row>
  </grid>
  <macros>
    <macro name=''/>
  </macros>
</nodehandler>
    """
    def __init__(self,xml_dom,tree_node):
        node_handler.__init__(self,xml_dom,tree_node)
        self.grid = self.master_dom.getElementsByTagName('grid')[0]
        if self.grid.getAttribute("border") == "":
            self.grid.setAttribute("border","1")
        if self.grid.getAttribute("autosize") == "":
            self.grid.setAttribute("autosize","1")
        self.macros = self.master_dom.getElementsByTagName('macros')[0]
        self.myeditor = None
        self.refresh_rows()

    def refresh_die_macros(self):
        pass

    def refresh_rows(self):
        self.rows = {}
        tree = self.tree
        icons = self.tree.icons
        tree.CollapseAndReset(self.mytree_node)
        node_list = self.master_dom.getElementsByTagName('row')
        for n in node_list:
            cells = n.getElementsByTagName('cell')
            t_node = cells[0]._get_firstChild()
            if t_node == None:
                name = "Row"
            else:
                name = t_node._get_nodeValue()
            if name == "":
                name = "Row"
            new_tree_node = tree.AppendItem(self.mytree_node,name,icons['gear'],icons['gear'])
            handler = grid_row_handler(n,new_tree_node,self)
            tree.SetPyData(new_tree_node,handler)


    def tohtml(self):
        border = self.grid.getAttribute("border")
        name = self.master_dom.getAttribute('name')
        rows = self.grid.getElementsByTagName('row')
        colspan = str(len(rows[0].getElementsByTagName('cell')))
        html_str = "<table border=\""+border+"\" align=center><tr bgcolor=\""+TH_BG+"\" ><th colspan="+colspan+">"+name+"</th></tr>"
        for r in rows:
            cells = r.getElementsByTagName('cell')
            html_str += "<tr>"
            for c in cells:
                #html_str += "<td width='"+c.getAttribute('size')+"' >" bug here
                html_str += "<td >"
                t_node = c._get_firstChild()
                if t_node == None:
                    html_str += "<br /></td>"
                else:
                    html_str += t_node._get_nodeValue() + "</td>"
            html_str += "</tr>"
        html_str += "</table>"
        return html_str

    def get_design_panel(self,parent):
        return rpg_grid_edit_panel(parent,self)

    def get_use_panel(self,parent):
        return rpg_grid_panel(parent,self)

    def get_size_constraint(self):
        return 1

    def is_autosized(self):
        return self.grid.getAttribute("autosize")

    def set_autosize(self,autosize=1):
        self.grid.setAttribute("autosize",str(autosize))

class grid_row_handler(node_handler):
    """ Node Handler grid row.
    """
    def __init__(self,xml_dom,tree_node,parent):
        node_handler.__init__(self,xml_dom,tree_node)
        self.drag = False

    def on_drop(self,evt):
        pass

    def can_clone(self):
        return 0;

    def tohtml(self):
        cells = self.master_dom.getElementsByTagName('cell')
        html_str = "<table border=1 align=center><tr >"
        for c in cells:
            html_str += "<td >"
            t_node = c._get_firstChild()
            if t_node == None:
                html_str += "<br /></td>"
            else:
                html_str += t_node._get_nodeValue() + "</td>"
            html_str += "</tr>"
        html_str += "</table>"
        return html_str

class MyCellEditor(wx.grid.PyGridCellEditor):
    """
    This is a sample GridCellEditor that shows you how to make your own custom
    grid editors.  All the methods that can be overridden are show here.  The
    ones that must be overridden are marked with "*Must Override*" in the
    docstring.

    Notice that in order to call the base class version of these special
    methods we use the method name preceded by "base_".  This is because these
    methods are "virtual" in C++ so if we try to call wxGridCellEditor.Create
    for example, then when the wxPython extension module tries to call
    ptr->Create(...) then it actually calls the derived class version which
    looks up the method in this class and calls it, causing a recursion loop.
    If you don't understand any of this, don't worry, just call the "base_"
    version instead.

    ----------------------------------------------------------------------------
    This class is copied from the wxPython examples directory and was written by
    Robin Dunn.

    I have pasted it directly in and removed all references to "log"

    -- Andrew

    """
    def __init__(self):
        wx.grid.PyGridCellEditor.__init__(self)


    def Create(self, parent, id, evtHandler):
        """
        Called to create the control, which must derive from wxControl.
        *Must Override*
        """
        self._tc = wx.TextCtrl(parent, id, "", style=wx.TE_PROCESS_ENTER | wx.TE_PROCESS_TAB)
        self._tc.SetInsertionPoint(0)
        self.SetControl(self._tc)
        if evtHandler:
            self._tc.PushEventHandler(evtHandler)


    def SetSize(self, rect):
        """
        Called to position/size the edit control within the cell rectangle.
        If you don't fill the cell (the rect) then be sure to override
        PaintBackground and do something meaningful there.
        """
        self._tc.SetDimensions(rect.x+1, rect.y+1, rect.width+2, rect.height+2)


    #def Show(self, show, attr): #deprecated DeprecationWarning: Please use PyGridCellEditor.Show instead.
    #    """
    #    Show or hide the edit control.  You can use the attr (if not None)
    #    to set colours or fonts for the control.
    #    """
    #    self.base_Show(show, attr) # Removed to prevent recursive error type.


    def BeginEdit(self, row, col, grid):
        """
        Fetch the value from the table and prepare the edit control
        to begin editing.  Set the focus to the edit control.
        *Must Override*
        """
        self.startValue = grid.GetTable().GetValue(row, col)
        self._tc.SetValue(self.startValue)
        self._tc.SetInsertionPointEnd()
        self._tc.SetFocus()

        # For this example, select the text
        self._tc.SetSelection(0, self._tc.GetLastPosition())


    def EndEdit(self, row, col, grid):
        """
        Complete the editing of the current cell. Returns True if the value
        has changed.  If necessary, the control may be destroyed.
        *Must Override*
        """
        changed = False

        val = self._tc.GetValue()
        if val != self.startValue:
            changed = True
            grid.GetTable().SetValue(row, col, val) # update the table

        self.startValue = ''
        self._tc.SetValue('')
        return changed


    def Reset(self):
        """
        Reset the value in the control back to its starting value.
        *Must Override*
        """
        self._tc.SetValue(self.startValue)
        self._tc.SetInsertionPointEnd()


    def IsAcceptedKey(self, evt):
        """
        Return True to allow the given key to start editing: the base class
        version only checks that the event has no modifiers.  F2 is special
        and will always start the editor.
        """

        ## Oops, there's a bug here, we'll have to do it ourself..
        ##return self.base_IsAcceptedKey(evt)

        return (not (evt.ControlDown() or evt.AltDown()) and
                evt.GetKeyCode() != wx.WXK_SHIFT)


    def StartingKey(self, evt):
        """
        If the editor is enabled by pressing keys on the grid, this will be
        called to let the editor do something about that first key if desired.
        """
        key = evt.GetKeyCode()
        ch = None
        if key in [wx.WXK_NUMPAD0, wx.WXK_NUMPAD1, wx.WXK_NUMPAD2, wx.WXK_NUMPAD3, wx.WXK_NUMPAD4,
                   wx.WXK_NUMPAD5, wx.WXK_NUMPAD6, wx.WXK_NUMPAD7, wx.WXK_NUMPAD8, wx.WXK_NUMPAD9]:
            ch = ch = chr(ord('0') + key - wx.WXK_NUMPAD0)

        elif key < 256 and key >= 0 and chr(key) in string.printable:
            ch = chr(key)
            if not evt.ShiftDown():
                ch = string.lower(ch)

        if ch is not None:
            # For this example, replace the text.  Normally we would append it.
            self._tc.AppendText(ch)
        else:
            evt.Skip()


    def Destroy(self):
        """final cleanup"""
        self.base_Destroy()


    def Clone(self):
        """
        Create a new object which is the copy of this one
        *Must Override*
        """
        return MyCellEditor()



class rpg_grid(wx.grid.Grid):
    """grid for attacks"""
    def __init__(self, parent, handler):
        wx.grid.Grid.__init__(self, parent, -1, style=wx.SUNKEN_BORDER | wx.WANTS_CHARS)
        self.parent = parent
        self.handler = handler

        #  Registers a "custom" cell editor (really the example from Robin Dunn with minor mods
        self.RegisterDataType(wx.grid.GRID_VALUE_STRING, wx.grid.GridCellStringRenderer(),MyCellEditor())

        self.rows = handler.grid.getElementsByTagName('row')
        rows = len(self.rows)
        cols = len(self.rows[0].getElementsByTagName('cell'))
        self.CreateGrid(rows,cols)
        self.SetRowLabelSize(0)
        self.SetColLabelSize(0)
        self.set_col_widths()

        for i in range(0,len(self.rows)):
            self.refresh_row(i)

        self.Bind(wx.grid.EVT_GRID_CELL_CHANGE, self.on_cell_change)
        self.Bind(wx.grid.EVT_GRID_COL_SIZE, self.on_col_size)
        self.Bind(wx.grid.EVT_GRID_CELL_LEFT_DCLICK, self.on_leftdclick)


    def on_leftdclick(self,evt):
        if self.CanEnableCellControl():
            self.EnableCellEditControl()

    def on_col_size(self, evt):
        col = evt.GetRowOrCol()
        cells = self.rows[0].getElementsByTagName('cell')
        size = self.GetColSize(col)
        cells[col].setAttribute('size',str(size))
        evt.Skip()

    def on_cell_change(self,evt):
        row = evt.GetRow()
        col = evt.GetCol()
        value = self.GetCellValue(row,col)
        cells = self.rows[row].getElementsByTagName('cell')
        t_node = cells[col]._get_firstChild()
        t_node._set_nodeValue(value)
        if col == 0:
            self.handler.refresh_rows()

    def set_col_widths(self):
        cells = self.rows[0].getElementsByTagName('cell')
        for i in range(0,len(cells)):
            try:
                size = int(cells[i].getAttribute('size'))
                self.SetColSize(i,size)
            except:
                continue

    def refresh_row(self,rowi):
        cells = self.rows[rowi].getElementsByTagName('cell')
        for i in range(0,len(cells)):
            t_node = cells[i]._get_firstChild()
            if t_node == None:
                #doc = cells[i].ownerDocument
                #t_node = doc.createTextNode("")
                t_node = Text("")
                t_node = cells[i].appendChild(t_node)
            self.SetCellValue(rowi,i,t_node._get_nodeValue())

    def add_row(self,evt=None):
        cols = self.GetNumberCols()
        #doc = self.handler.grid.ownerDocument
        #row = doc.createElement('row')
        row = Element('row')
        for i in range(0,cols):
            #cell = doc.createElement('cell')
            cell = Element('cell')
            #t_node = doc.createTextNode("")
            t_node = Text("")
            t_node = cell.appendChild(t_node)
            row.appendChild(cell)
        self.handler.grid.appendChild(row)
        self.AppendRows(1)
        self.rows = self.handler.grid.getElementsByTagName('row')
        self.handler.refresh_rows()

    def add_col(self,evt=None):
        #doc = self.handler.grid.ownerDocument
        for r in self.rows:
            #cell = doc.createElement('cell')
            cell = Element('cell')
            #t_node = doc.createTextNode("")
            t_node = Text("")
            t_node = cell.appendChild(t_node)
            r.appendChild(cell)
        self.AppendCols(1)
        self.fit_cols()


    def del_row(self,evt=None):
        num = self.GetNumberRows()
        row = self.rows[num-1]
        self.handler.grid.removeChild(row)
        self.DeleteRows(num-1,1)
        self.rows = self.handler.grid.getElementsByTagName('row')
        self.handler.refresh_rows()

    def del_col(self,evt=None):
        num = self.GetNumberCols()
        for r in self.rows:
            cells = r.getElementsByTagName('cell')
            r.removeChild(cells[num-1])
        self.DeleteCols(num-1,1)
        self.fit_cols()


G_TITLE = wx.NewId()
GRID_BOR = wx.NewId()
class rpg_grid_panel(wx.Panel):
    def __init__(self, parent, handler):
        wx.Panel.__init__(self, parent, -1)
        self.handler = handler
        self.grid = rpg_grid(self,handler)
        label = handler.master_dom.getAttribute('name')
        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.main_sizer.Add(wx.StaticText(self, -1, label+": "), 0, wx.EXPAND)
        self.main_sizer.Add(self.grid,1,wx.EXPAND)
        self.SetSizer(self.main_sizer)
        self.SetAutoLayout(True)
        self.Fit()
        parent.SetSize(self.GetBestSize())


G_AUTO_SIZE = wx.NewId()
G_ADD_ROW = wx.NewId()
G_ADD_COL = wx.NewId()
G_DEL_ROW = wx.NewId()
G_DEL_COL = wx.NewId()

class rpg_grid_edit_panel(wx.Panel):
    def __init__(self, parent, handler):
        wx.Panel.__init__(self, parent, -1)
        self.handler = handler
        self.grid = rpg_grid(self,handler)
        self.title = wx.TextCtrl(self, G_TITLE, handler.master_dom.getAttribute('name'))

        radio_b = wx.RadioBox(self, GRID_BOR, "Border (HTML)", choices=["no","yes"])
        border = handler.grid.getAttribute("border")
        radio_b.SetSelection(int(border))

        self.auto_size = wx.CheckBox(self, G_AUTO_SIZE, " Auto Size")
        if handler.is_autosized() == '1':
            self.auto_size.SetValue(True)
        else:
            self.auto_size.SetValue(False)

        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(wx.Button(self, G_ADD_ROW, "Add Row"), 1, wx.EXPAND)
        sizer.Add(wx.Size(10,10))
        sizer.Add(wx.Button(self, G_DEL_ROW, "Remove Row"), 1, wx.EXPAND)
        sizer.Add(wx.Size(10,10))
        sizer.Add(wx.Button(self, G_ADD_COL, "Add Column"), 1, wx.EXPAND)
        sizer.Add(wx.Size(10,10))
        sizer.Add(wx.Button(self, G_DEL_COL, "Remove Column"), 1, wx.EXPAND)

        self.main_sizer = wx.StaticBoxSizer(wx.StaticBox(self,-1,"Grid"), wx.VERTICAL)
        self.main_sizer.Add(wx.StaticText(self, -1, "Title:"), 0, wx.EXPAND)
        self.main_sizer.Add(self.title, 0, wx.EXPAND)
        self.main_sizer.Add(radio_b, 0, 0)
        self.main_sizer.Add(self.auto_size, 0, 0)
        self.main_sizer.Add(self.grid,1,wx.EXPAND)
        self.main_sizer.Add(sizer,0,wx.EXPAND)

        self.SetSizer(self.main_sizer)
        self.SetAutoLayout(True)
        self.Fit()

        self.Bind(wx.EVT_TEXT, self.on_text, id=G_TITLE)
        self.Bind(wx.EVT_BUTTON, self.grid.add_row, id=G_ADD_ROW)
        self.Bind(wx.EVT_BUTTON, self.grid.del_row, id=G_DEL_ROW)
        self.Bind(wx.EVT_BUTTON, self.grid.add_col, id=G_ADD_COL)
        self.Bind(wx.EVT_BUTTON, self.grid.del_col, id=G_DEL_COL)
        self.Bind(wx.EVT_RADIOBOX, self.on_radio_box, id=GRID_BOR)
        self.Bind(wx.EVT_CHECKBOX, self.on_auto_size, id=G_AUTO_SIZE)

    def on_auto_size(self,evt):
        self.handler.set_autosize(bool2int(evt.Checked()))

    def on_radio_box(self,evt):
        id = evt.GetId()
        index = evt.GetInt()
        if id == GRID_BOR:
            self.handler.grid.setAttribute("border",str(index))

    def on_text(self,evt):
        txt = self.title.GetValue()
        if txt != "":
            self.handler.master_dom.setAttribute('name',txt)
            self.handler.rename(txt)
