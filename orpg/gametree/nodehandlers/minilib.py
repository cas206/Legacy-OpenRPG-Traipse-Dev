# Copyright (C) 2000-2001 The OpenRPG Project
#
#   openrpg-dev@lists.sourceforge.net
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
# File: minilib.py
# Author: Ted Berg
# Maintainer:
# Version:
#   $Id: minilib.py,v 1.28 2007/04/22 22:00:18 digitalxero Exp $
#
# Description: nodehandler for a collection of miniatures.
#

__version__ = "$Id: minilib.py,v 1.28 2007/04/22 22:00:18 digitalxero Exp $"

"""Nodehandler for collections of miniatures.  User can add, delete, edit
miniatures as sending them to the map singly or in batches.
"""
from core import *
from orpg.dirpath import dir_struct
import string
import map_miniature_nodehandler
import orpg.mapper.map_msg
# import scriptkit

# Constants
TO_MINILIB_MAP = {'path':'url', 'label':'name', 'id':None, 'action':None}
FROM_MINILIB_MAP = {'url':'path', 'name':'label', 'unique':None}
CORE_ATTRIBUTES = ['name', 'url', 'unique', 'posy', 'posx', 'hide', 'face', 'heading', 'align', 'locked', 'width', 'height']

ATTRIBUTE_NAME = 'name'
ATTRIBUTE_URL = 'url'
ATTRIBUTE_UNIQUE = 'unique'
ATTRIBUTE_ID = 'id'
ATTRIBUTE_POSX = 'posx'
ATTRIBUTE_POSY = 'posy'

TAG_MINIATURE = 'miniature'

COMPONENT_MAP = 'map'
COMPONENT_SESSION = 'session'
# <nodehandler name='?' module='minilib' class='minilib_handler'>
#     <miniature name='?' url='?' unique='?'></miniature>
# </nodehandler>

class minilib_handler( node_handler ):
    """A nodehandler that manages a collection of miniatures for the
    map.
    <pre>
        &lt;nodehandler name='?' module='minilib' class='minilib_handler'&gt;
            &lt;miniature name='?' url='?' unique='?'&gt;&lt;/miniature&gt;
        &lt;/nodehandler&gt;
    </pre>
    """
    def __init__(self, xml_dom, tree_node):
        """Instantiates the class, and sets all vars to their default state
        """
        node_handler.__init__(self, xml_dom, tree_node)

        self.myeditor = None
        self.mywindow = None
        self.tree_node = tree_node
        # self.xml_dom = xml_dom
        self.update_leaves()
        self.sanity_check_nodes()

    def get_design_panel( self, parent ):
        """returns an instance of the miniature library edit control ( see
        on_design ).  This is for use with the the 'edit multiple nodes in a
        single frame' code.
        """
        return minpedit( parent, self )

    def get_use_panel( self, parent ):
        """returns an instance of the miniature library view control ( see
        on_use ).  This is for use with the the 'view multiple nodes in a
        single frame' code.
        """
        return minilib_use_panel( parent, self )

    def tohtml( self ):
        """Returns an HTML representation of this node in string format.
        The table columnwidths are currently being forced, as the wxHTML
        widgets being used don't handle cells wider than the widgets are
        expecting for a given column.
        """
        str = '<table border="2" >'
        list = self.master_dom.getElementsByTagName(TAG_MINIATURE)
        str += "<tr><th width='20%'>Label</th><th>Image</th><th width='65%'>URL</th><th>Unique</th></t>"
        for mini in list:
            url = mini.getAttribute(ATTRIBUTE_URL)
            label = mini.getAttribute(ATTRIBUTE_NAME)
            flag = 0
            try:
                flag = eval( mini.getAttribute(ATTRIBUTE_UNIQUE) )
            except:
                pass

            show = 'yes'
            if flag:
                show = 'no'

            str += """<tr>
                <td> %s </td>
                <td><img src="%s"></td>
                <td> %s </td>
                <td> %s </td>
            </tr>""" % ( label, url, url, show )

        str += "</table>"
        print str
        return str

    def html_view( self ):
        """see to_html
        """
        return self.tohtml()

    def on_drop(self, evt):
        drag_obj = self.tree.drag_obj
        if drag_obj == self or self.tree.is_parent_node( self.mytree_node, drag_obj.mytree_node ):
            return
        if isinstance( drag_obj, minilib_handler ):
            item = self.tree.GetSelection()
            name = self.tree.GetItemText( item )
        if isinstance( drag_obj, map_miniature_nodehandler.map_miniature_handler ):
            xml_dom = self.tree.drag_obj.master_dom#.delete()
            obj = xml_dom.firstChild
            print obj.getAttributeKeys()
            dict = {}
            unique = ''
            for attrib in obj.getAttributeKeys():
                key = TO_MINILIB_MAP.get( attrib, attrib )
                if key != None:
                    dict[ key ] = obj.getAttribute( attrib )
            dict[ ATTRIBUTE_UNIQUE ] = unique
            self.new_mini( dict )


    def new_mini( self, data={}, add=1 ):
        mini = minidom.Element( TAG_MINIATURE )
        for key in data.keys():
            mini.setAttribute( key, data[ key ] )
        for key in CORE_ATTRIBUTES:
            if mini.getAttribute( key ) == '':
                mini.setAttribute( key, '0' )
        if add:
            self.add_mini( mini )
            self.add_leaf( mini )
        return mini

    def add_mini( self, mini ):
        self.master_dom.appendChild( mini )

    def add_leaf( self, mini, icon='gear' ):
        tree = self.tree
        icons = tree.icons
        key = mini.getAttribute( ATTRIBUTE_NAME )
        self.mydata.append( mini )

    def update_leaves( self ):
        self.mydata = []
        nl = self.master_dom.getElementsByTagName( TAG_MINIATURE )
        for n in nl:
            self.add_leaf( n )


    def on_drag( self, evt ):
        print 'drag event caught'

    def send_mini_to_map( self, mini, count=1, addName=True ):
        if mini == None:
            return
        if mini.getAttribute( ATTRIBUTE_URL ) == '' or mini.getAttribute( ATTRIBUTE_URL ) == 'http://':
            self.chat.ParsePost( self.chat.colorize(self.chat.syscolor, '"%s" is not a valid URL, the mini "%s" will not be added to the map' % ( mini.getAttribute( ATTRIBUTE_URL ), mini.getAttribute( ATTRIBUTE_NAME ) )) )
            return
        session = component.get( COMPONENT_SESSION )
        if (session.my_role() != session.ROLE_GM) and (session.my_role() != session.ROLE_PLAYER):
            component.get("chat").InfoPost("You must be either a player or GM to use the miniature Layer")
            return
        map = component.get(COMPONENT_MAP)
        for loop in range( count ):
            msg = self.get_miniature_XML( mini, addName)
            msg = str("<map action='update'><miniatures>" + msg + "</miniatures></map>")
            map.new_data( msg )
            session.send( msg )

    def get_miniature_XML( self, mini, addName = True ):
        msg = orpg.mapper.map_msg.mini_msg()
        map = component.get( COMPONENT_MAP )
        session = component.get( COMPONENT_SESSION )
        msg.init_prop( ATTRIBUTE_ID, session.get_next_id() )
        for k in mini.getAttributeKeys():
            # translate our attributes to map attributes
            key = FROM_MINILIB_MAP.get( k, k )
            if key != None:
                if not addName and k == 'name':
                    pass
                else:
                    msg.init_prop( key, mini.getAttribute( k ) )
        unique = self.is_unique( mini )
        if addName:
            label = mini.getAttribute( ATTRIBUTE_NAME )
        else:
            label = ''
        return msg().get_all_xml()

    def is_unique( self, mini ):
        unique = mini.getAttribute( ATTRIBUTE_UNIQUE )
        val = 0
        try:
            val = eval( unique )
        except:
            val = len( unique )
        return val

    def sanity_check_nodes( self ):
        nl = self.master_dom.getElementsByTagName( TAG_MINIATURE )
        for node in nl:
            if node.getAttribute( ATTRIBUTE_POSX ) == '':
                node.setAttribute( ATTRIBUTE_POSX, '0' )
            if node.getAttribute( ATTRIBUTE_POSY ) == '':
                node.setAttribute( ATTRIBUTE_POSY, '0' )

    def get_mini( self, index ):
        try:
            nl = self.master_dom.getElementsByTagName( TAG_MINIATURE )
            return nl[ index ]
        except:
            return None

class mini_handler( node_handler ):
    def __init__( self, xml_dom, tree_node, handler ):
        node_handler.__init__( self, xml_dom, tree_node)
        self.handler = handler

    def on_ldclick( self, evt ):
        self.handler.send_mini_to_map( self.master_dom )

    def on_drop( self, evt ):
        pass

    def on_lclick( self, evt ):
        print 'hi'
        evt.Skip()

class minilib_use_panel(wx.Panel):
    """This panel will be displayed when the user double clicks on the
    miniature library node.  It is a sorted listbox of miniature labels,
    a text field for entering a count ( for batch adds ) and 'add'/'done'
    buttons.
    """
    def __init__( self, frame, handler ):
        """Constructor.
        """
        wx.Panel.__init__( self, frame, -1 )
        self.handler = handler
        self.frame = frame

        self.map = component.get('map')
        names = self.buildList()
        # self.keys = self.list.keys()
        # self.keys.sort()


        s = self.GetClientSizeTuple()

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        box = wx.BoxSizer(wx.HORIZONTAL)
        self.listbox = wx.ListBox(self, wx.ID_ANY, (10, 10), (s[0] - 10, s[1] - 30 ), names, wx.LB_EXTENDED)
        self.count = wx.TextCtrl(self, wx.ID_ANY, '1')

        box.Add( wx.StaticText( self, -1, 'Minis to add' ), 0, wx.EXPAND )
        box.Add(wx.Size(10,10))
        box.Add(self.count, 1, wx.EXPAND)

        self.sizer.Add( self.listbox, 1, wx.EXPAND )
        self.sizer.Add( box, 0, wx.EXPAND )

        box = wx.BoxSizer( wx.HORIZONTAL )
        self.okBtn = wx.Button(self, wx.ID_ANY, 'Add')
        box.Add(self.okBtn, 0, wx.EXPAND)
        self.addBtn = wx.Button(self, wx.ID_ANY, 'Add No Label')
        box.Add(self.addBtn, 0, wx.EXPAND)
        self.cancleBtn = wx.Button(self, wx.ID_ANY, 'Done')
        box.Add(self.cancleBtn, 0, wx.EXPAND)

        self.sizer.Add(wx.Size(10,10))
        self.sizer.Add(box, 0, wx.EXPAND)
        self.Bind(wx.EVT_BUTTON, self.on_ok, self.okBtn)
        self.Bind(wx.EVT_BUTTON, self.on_ok, self.addBtn)
        self.Bind(wx.EVT_BUTTON, self.on_close, self.cancleBtn)
        self.SetSizer(self.sizer)
        self.SetAutoLayout(True)
        self.Fit()

    def buildList( self ):
        """Returns a dictionary of label => game tree miniature DOM node mappings.
        """
        list = self.handler.master_dom.getElementsByTagName(TAG_MINIATURE)
        self.list = []
        for mini in list:
            self.list.append( mini.getAttribute( ATTRIBUTE_NAME ) )
        return self.list
        # self.list = {}
        # for mini in list:
        #     name = mini.getAttribute( ATTRIBUTE_NAME )
        #     if name == '':
        #         name = self.map.canvas.get_label_from_url( mini.getAttribute( ATTRIBUTE_URL ) )
        #     self.list[ name ] = mini

    def on_close(self, evt):
        self.frame.Close()

    def on_ok( self, evt ):
        """Event handler for the 'add' button.
        """
        btn = self.FindWindowById(evt.GetId())
        sendName = True
        try:
            count = eval( self.count.GetValue() )
        except:
            count = 1

        try:
            if eval( unique ):
                count = 1
            unique = eval( unique )
        except:
            pass

        if btn.GetLabel() == 'Add No Label':
            sendName = False
        for index in self.listbox.GetSelections():
            self.handler.send_mini_to_map( self.handler.get_mini( index ), count, sendName )


class minpedit(wx.Panel):
    """Panel for editing game tree miniature nodes.  Node information
    is displayed in a grid, and buttons are provided for adding, deleting
    nodes, and for sending minis to the map ( singly and in batches ).
    """
    def __init__( self, frame, handler ):
        """Constructor.
        """
        wx.Panel.__init__( self, frame, -1 )
        self.handler = handler
        self.frame = frame

        self.sizer = wx.BoxSizer( wx.VERTICAL )
        self.grid = minilib_grid( self, handler )

        bbox = wx.BoxSizer( wx.HORIZONTAL )
        newMiniBtn = wx.Button( self, wx.ID_ANY, "New mini" )
        delMiniBtn = wx.Button( self, wx.ID_ANY, "Del mini" )
        addMiniBtn = wx.Button( self, wx.ID_ANY, "Add 1" )
        addBatchBtn = wx.Button( self, wx.ID_ANY, "Add Batch" )
        bbox.Add(newMiniBtn, 0, wx.EXPAND )
        bbox.Add(delMiniBtn, 0, wx.EXPAND )
        bbox.Add(wx.Size(10,10))
        bbox.Add(addMiniBtn, 0, wx.EXPAND )
        bbox.Add(addBatchBtn, 0, wx.EXPAND )

        self.sizer.Add( self.grid, 1, wx.EXPAND)
        self.sizer.Add( bbox, 0)
        self.SetSizer(self.sizer)
        self.SetAutoLayout(True)
        self.Fit()

        self.Bind(wx.EVT_BUTTON, self.add_mini, newMiniBtn)
        self.Bind(wx.EVT_BUTTON, self.del_mini, delMiniBtn)
        self.Bind(wx.EVT_BUTTON, self.send_to_map, addMiniBtn)
        self.Bind(wx.EVT_BUTTON, self.send_group_to_map, addBatchBtn)

    def add_mini( self, evt=None ):
        """Event handler for the 'New mini' button.  It calls
        minilib_grid.add_row
        """
        self.grid.add_row()

    def del_mini( self, evt=None ):
        """Event handler for the 'Del mini' button.  It calls
        minilib_grid.del_row
        """
        self.grid.del_row()

    def send_to_map( self, evt=None ):
        """Event handler for the 'Add 1' button.  Sends the
        miniature defined by the currently selected row to the map, once.
        """
        index = self.grid.GetGridCursorRow()
        self.handler.send_mini_to_map( self.handler.get_mini( index ) )

    def send_group_to_map( self, evt=None ):
        """Event handler for the 'Add batch' button.  Querys the user
        for a mini count and sends the miniature defined by the currently
        selected row to the map, the specified number of times.
        """
        if self.grid.GetNumberRows() > 0:
            dlg = wx.TextEntryDialog( self.frame,
                'How many %s\'s do you want to add?' %
                ( self.grid.getSelectedLabel() ), 'Batch mini add', '2' )
            if dlg.ShowModal() == wx.ID_OK:
                try:
                    value = eval( dlg.GetValue() )
                except:
                    value = 0
                # for loop in range( 0, value ):
                #     self.send_to_map()
                print 'getting selected index for batch send'
                index = self.grid.GetGridCursorRow()
                print 'sending batch to map'
                self.handler.send_mini_to_map( self.handler.get_mini( index ), value )

class minilib_grid(wx.grid.Grid):
    """A wxGrid subclass designed for editing game tree miniature library
    nodes.
    """
    def __init__( self, parent, handler ):
        """Constructor.
        """
        wx.grid.Grid.__init__(self, parent, -1, style=wx.SUNKEN_BORDER | wx.WANTS_CHARS )
        self.parent = parent
        self.handler = handler
        #self.keys = [ ATTRIBUTE_NAME, ATTRIBUTE_URL, ATTRIBUTE_UNIQUE ]
        self.keys = CORE_ATTRIBUTES
        self.CreateGrid( 1, len( self.keys ) )
        # self.SetColLabelValue( 0, 'Name' )
        # self.SetColLabelValue( 1, 'URL' )
        # self.SetColSize( 1, 250 )
        # self.SetColLabelValue( 2, 'Unique' )
        for key in self.keys:
            self.SetColLabelValue( self.keys.index( key ), key )
        self.update_all()
        self.selectedRow = 0
        self.AutoSizeColumns()
        self.Bind(wx.grid.EVT_GRID_CELL_CHANGE, self.on_cell_change)
        self.Bind(wx.grid.EVT_GRID_SELECT_CELL, self.select_cell)

    def update_cols( self ):
        nl = self.handler.master_dom.getElementsByTagName( TAG_MINIATURE )
        for n in nl:
            for k in n.getAttributeKeys():
                if k not in self.keys:
                    self.keys.append( k )

    def select_cell( self, evt ):
        """Event handler for grid cell selection changes.  It stores the
        last selected row in a variable for use by the add[*] and del_row
        operations.
        """
        self.BeginBatch()
        self.selectedRow = evt.GetRow()
        self.SelectRow( self.selectedRow )
        self.EndBatch()
        evt.Skip()

    def getList( self ):
        """Returns the list of 'miniature' DOM elements associated with this
        miniature library.
        """
        return self.handler.master_dom.getElementsByTagName( TAG_MINIATURE )

    def add_row( self, count = 1 ):
        """creates a new miniature node, and then adds it to the current
        miniature library, and to the grid.
        """
        self.AppendRows( count )
        node = self.handler.new_mini( {
          ATTRIBUTE_NAME :' ',
          ATTRIBUTE_URL :'http://'} )# minidom.Element( TAG_MINIATURE )
        self.update_all()
        #self.handler.master_dom.appendChild( node )

    def del_row( self ):
        """deletes the miniature associated with the currently selected
        row. BUG BUG BUG this method should drop a child from the DOM but
        does not.
        """
        if self.selectedRow > -1:
            pos = self.selectedRow
            list = self.handler.master_dom.getElementsByTagName(TAG_MINIATURE)
            self.handler.master_dom.removeChild( list[pos] )
            self.DeleteRows( pos, 1 )
            list = self.getList()
            del list[ pos ]

    def on_cell_change( self, evt ):
        """Event handler for cell selection changes. selected row is used
        to update data for that row.
        """
        row = evt.GetRow()
        self.update_data_row( row )

    def update_all( self ):
        """ensures that the grid is displaying the correct number of
        rows, and then updates all data displayed by the grid
        """
        list = self.getList()
        count = 0
        for n in list:
            for k in n.getAttributeKeys():
                if k not in self.keys:
                    self.keys.append( k )
        count = len( self.keys )
        if self.GetNumberCols() < count:
            self.AppendCols( count - self.GetNumberCols() )
            for k in self.keys:
                self.SetColLabelValue( self.keys.index( k ), k )
        count = len( list )
        rowcount = self.GetNumberRows()
        if ( count > rowcount ):
            total = count - rowcount
            self.AppendRows( total )
        elif ( count < rowcount ):
            total = rowcount - count
            self.DeleteRows( 0, total );
        for index in range( 0, count ):
            self.update_grid_row( index )

    def getSelectedLabel( self ):
        """Returns the label for the selected row
        """
        return self.GetTable().GetValue( self.selectedRow, 0 )

    def getSelectedURL( self ):
        """Returns the URL for the selected row
        """
        return self.GetTable().GetValue( self.selectedRow, 1 )

    def getSelectedSerial( self ):
        """Returns the ATTRIBUTE_UNIQUE value for the selected row
        """
        return self.GetTable().GetValue( self.selectedRow, 2 )

    def update_grid_row( self, row ):
        """Updates the specified grid row with data from the DOM node
        specified by 'row'
        """
        list = self.getList()
        item = list[ row ]
        # self.GetTable().SetValue( row, 0, item.getAttribute(ATTRIBUTE_NAME) )
        # self.GetTable().SetValue( row, 1, item.getAttribute(ATTRIBUTE_URL) )
        # self.GetTable().SetValue( row, 2, item.getAttribute(ATTRIBUTE_UNIQUE) )
        for key in self.keys:
            self.GetTable().SetValue( row, self.keys.index( key ), item.getAttribute( key ) )

    def update_data_row( self, row ):
        """Updates the DOM nodw 'row' with grid data from 'row'
        """
        list = self.getList()
        item = list[ row ]
        for key in self.keys:
            item.setAttribute( key, string.strip( self.GetTable().GetValue( row, self.keys.index( key ) ) ) )
        # item.setAttribute( ATTRIBUTE_NAME, string.strip( self.GetTable().GetValue( row, 0 ) ) )
        # item.setAttribute( ATTRIBUTE_URL, string.strip( self.GetTable().GetValue( row, 1 ) ) )
        # item.setAttribute( ATTRIBUTE_UNIQUE, string.strip( self.GetTable().GetValue( row, 2 ) ) )
        # self.GetTable().SetValue( row, 0, item.getAttribute(ATTRIBUTE_NAME) )
        # self.GetTable().SetValue( row, 1, item.getAttribute(ATTRIBUTE_URL) )
        # self.GetTable().SetValue( row, 2, item.getAttribute(ATTRIBUTE_UNIQUE) )
