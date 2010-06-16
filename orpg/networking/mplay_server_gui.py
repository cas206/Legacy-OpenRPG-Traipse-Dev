#!/usr/bin/env python
#
#   OpenRPG Server Graphical Interface
#        GNU General Public License
#

__appname__=' OpenRPG GUI Server v0.7 '
__version__='$Revision: 1.26 $'[11:-2]
__cvsinfo__="$Id: mplay_server_gui.py,v Traipse 'Ornery-Orc' prof.ebral Exp $"[5:-2]
__doc__="""OpenRPG Server Graphical Interface"""

import os, sys, time, types, webbrowser

from orpg.dirpath import dir_struct
from orpg.tools.validate import validate
from orpg.orpg_wx import *
from threading import Thread

from meta_server_lib import post_server_data, remove_server
from mplay_server import mplay_server, server

from xml.dom import minidom
from orpg.orpgCore import component
from orpg.tools.orpg_log import debug, DebugConsole
from orpg.tools.orpg_settings import settings

from xml.etree.ElementTree import ElementTree, Element, iselement
from xml.etree.ElementTree import fromstring, tostring, parse

# Constants ######################################
SERVER_RUNNING = 1
SERVER_STOPPED = 0
MENU_MODIFY_BANLIST = wx.NewId()
MENU_PLAYER_CREATE_ROOM = wx.NewId()

# Our new event type that gets posted from one
# thread to another
wxEVT_LOG_MESSAGE = wx.NewEventType()
wxEVT_FUNCTION_MESSAGE = wx.NewEventType()

# Our event connector -- wxEVT_LOG_MESSAGE
EVT_LOG_MESSAGE = wx.PyEventBinder(wxEVT_LOG_MESSAGE, 1)

# Our event connector -- wxEVT_FUNCTION_MESSAGE
EVT_FUNCTION_MESSAGE = wx.PyEventBinder(wxEVT_FUNCTION_MESSAGE, 1)

# Utils ##########################################
def format_bytes(b):
    f = ['b', 'Kb', 'Mb', 'Gb']
    i = 0
    while i < 3:
        if b < 1024: return str(b) + f[i]
        else: b = b/1024
        i += 1
    return str(b) + f[3]

# wxEVT_LOG_MESSAGE
# MessageLogEvent ###############################
class MessageLogEvent(wx.PyEvent):
    def __init__( self, message ):
        wx.PyEvent.__init__( self )
        self.SetEventType(wxEVT_LOG_MESSAGE)
        self.message = message

# wxEVT_TUPLE_MESSAGE
# MessageLogEvent ###############################
class MessageFunctionEvent(wx.PyEvent):
    def __init__( self, func, message ):
        wx.PyEvent.__init__( self )
        self.SetEventType(wxEVT_FUNCTION_MESSAGE)
        self.func = func
        self.message = message

# ServerConfig Object ############################
class ServerConfig:
    """ This class contains configuration
        setting used to control the server."""

    def __init__(self, owner ): 
        """ Loads default configuration settings."""
        validate.config_file("server_ini.xml", "default_server_ini.xml")
        config_xml = parse(dir_struct['user'] + 'server_ini.xml').getroot()
        port = config_xml.find('service').get('port')
        OPENRPG_PORT = 6774 if port == '' else int(port)
        self.owner = owner

    def load_xml(self, xml):
        """ Load configuration from XML data.
            xml (xml) -- xml string to parse """
        pass

    def save_xml(self):
        """ Returns XML file representing
            the active configuration. """
        pass

# Server Monitor #################################

class ServerMonitor(Thread):
    """ Monitor thread for GameServer. """
    def __init__(self, cb, conf, name, pwd):
        """ Setup the server. """
        Thread.__init__(self)
        self.cb = cb
        self.conf = conf
        self.serverName = name
        self.bootPwd = pwd

    def log(self, mesg):
        if type(mesg) == types.TupleType:
            func, msg = mesg
            event = MessageFunctionEvent( func, msg )
        else: event = MessageLogEvent( mesg )
        wx.PostEvent( self.conf.owner, event )
        del event

    def run(self):
        """ Start the server. """
        self.server = mplay_server(self.log, self.serverName )
        self.server.initServer(bootPassword=self.bootPwd, reg="No")
        self.alive = 1
        while self.alive: time.sleep(3)

    def stop(self):
        """ Stop the server. """
        self.server.kill_server()
        self.alive = 0

# GUI Server #####################################
# Parent = notebook
# Main = GUI
class Groups(wx.ListCtrl):
    def __init__(self, parent, main):
        wx.ListCtrl.__init__(self, parent, -1, wx.DefaultPosition,
                            wx.DefaultSize, wx.LC_REPORT|wx.SUNKEN_BORDER|wx.EXPAND|wx.LC_HRULES)

        """Not completed.  Creates room, delets rooms.  Does not track players.  Nor does gsclient, ftm."""
        validate.config_file("server_ini.xml", "default_server_ini.xml" )
        config_xml = parse(dir_struct["user"] + 'server_ini.xml').getroot()
        lobbyname = config_xml.get('lobbyname')

        self.main = main
        self.roomList = { 0 : lobbyname }
        self.InsertColumn(0, 'Group ID')
        self.InsertColumn(1, 'Game')
        self.InsertColumn(2, 'Players')
        self.InsertColumn(3, 'Passworded')
        self.AddGroup((self.roomList[0], '0', '0', 'No'))

    def AddGroup(self, data):
        (room, room_id, players, passworded) = data
        i = self.InsertStringItem(0, str(room_id))
        self.SetStringItem(i, 1, room)
        self.SetStringItem(i, 2, str(players))
        self.SetStringItem(i, 3, passworded)

    def DeleteGroup(self, data):
        i = self.FindItem(-1, str(data))
        self.DeleteItem(i)        

    def UpdateGroup(self, data):
        (room, room_id, players) = data
        i = self.FindItem( -1, str(room_id))
        self.SetStringItem( i, 1, room )
        self.SetStringItem(i, 2, str(players))
        ### Need to add room for Password Updates ###

class Connections(wx.ListCtrl):
    def __init__( self, parent, main ):
        wx.ListCtrl.__init__( self, parent, -1, wx.DefaultPosition, 
                            wx.DefaultSize, wx.LC_REPORT|wx.SUNKEN_BORDER|wx.EXPAND|wx.LC_HRULES )

        validate.config_file("server_ini.xml", "default_server_ini.xml" ) 
        config_xml = parse(dir_struct["user"] + 'server_ini.xml').getroot()
        lobbyname = config_xml.get('lobbyname')

        self.main = main
        self.roomList = { 0 : lobbyname }
        self._imageList = wx.ImageList( 16, 16, False )
        img = wx.Image(dir_struct["icon"]+"player.gif", wx.BITMAP_TYPE_GIF).ConvertToBitmap()
        self._imageList.Add( img )
        img = wx.Image(dir_struct["icon"]+"player-whisper.gif", wx.BITMAP_TYPE_GIF).ConvertToBitmap()
        self._imageList.Add( img )
        self.SetImageList( self._imageList, wx.IMAGE_LIST_SMALL )

        # Set The columns
        self.InsertColumn(0, "ID")
        self.InsertColumn(1, "Player")
        self.InsertColumn(2, "Status")
        self.InsertColumn(3, "Room")
        self.InsertColumn(4, "Version")
        self.InsertColumn(5, "Role")
        self.InsertColumn(6, "IP")
        self.InsertColumn(7, "Ping")

        # Set the column widths
        self.AutoAjust()

        # Build our pop up menu to do cool things with the players in the list
        self.menu = wx.Menu()
        self.menu.SetTitle( "Player Menu" )
        self.menu.Append( 1, "Boot Player" )
        self.menu.Append( 2, 'Ban Player' )
        self.menu.Append( 3, "Player Version" )
        self.menu.AppendSeparator()
        self.menu.Append( 4, "Send Player Message" )
        self.menu.Append( 5, "Send Room Message" )
        self.menu.Append( 6, "Broadcast Server Message" )

        # Associate our events
        self.Bind(wx.EVT_RIGHT_DOWN, self.OnPopupMenu)
        self.Bind(wx.EVT_MENU, self.OnPopupMenuItem, id=1)
        self.Bind(wx.EVT_MENU, self.OnPopupMenuItem, id=2)
        self.Bind(wx.EVT_MENU, self.OnPopupMenuItem, id=4)
        self.Bind(wx.EVT_MENU, self.OnPopupMenuItem, id=5)
        self.Bind(wx.EVT_MENU, self.OnPopupMenuItem, id=6)
        self.Bind(wx.EVT_MENU, self.OnPopupMenuItem, id=3)

    def add(self, player):
        i = self.InsertImageStringItem( 0, player["id"], 0 )
        self.SetStringItem(i, 1, self.stripHtml(player["name"]))
        self.SetStringItem(i, 2, "NEW")
        self.SetStringItem(i, 3, self.roomList[0])
        self.SetStringItem(i, 4, self.stripHtml(player["version"]))
        self.SetStringItem(i, 5, 'Lurker' if player["role"] == None else self.stripHtml(player["role"]))
        self.SetStringItem(i, 6, self.stripHtml(player["ip"]))
        self.SetStringItem(i, 7, "PING")
        self.SetItemData(i, int(player["id"]))
        self.colorize_player_list(player)
        self.AutoAjust()

    def remove(self, id):
        i = self.FindItemData( -1, int(id))
        self.DeleteItem(i)
        self.AutoAjust()

    def AutoAjust(self):
        self.SetColumnWidth(0, -1)
        self.SetColumnWidth(1, -1)
        self.SetColumnWidth(2, -1)
        self.SetColumnWidth(3, -1)
        self.SetColumnWidth(4, -1)
        self.SetColumnWidth(5, -1)
        self.SetColumnWidth(6, -1)
        self.SetColumnWidth(7, -1)
        self.Refresh()

    def colorize_player_list(self, player):
        if player == 0: return
        for m in player.keys():
            id = player['id']
            item_list_location = self.FindItemData(-1, int(id))
            if item_list_location == -1: continue
            item = self.GetItem(item_list_location)
            role = player['role']
            try: #Players that turn up Blue are not passing the correct arguments.
                try: 
                    if player['group_id'] != "0": item.SetTextColour(settings.get_setting(role + "RoleColor"))
                except KeyError: # Needed because group_id turns into group somewhere.
                    if player['group'] != "0": item.SetTextColour(settings.get_setting(role + "RoleColor"))
            except: item.SetTextColour('BLUE')
            self.SetItem(item)

    def update(self, player):
        i = self.FindItemData( -1, int(player["id"]) )
        if i > -1:
            self.SetStringItem(i, 1, self.stripHtml(player["name"]))
            self.SetStringItem(i, 2, self.stripHtml(player["status"]))
            self.SetStringItem(i, 5, 'Lurker' if player["role"] == None else self.stripHtml(player["role"]))
            self.colorize_player_list(player)
            self.AutoAjust()
        else: self.add(player)

    def updateRoom( self, data ):
        (room, room_id, player) = data
        i = self.FindItemData( -1, int(player) )
        if player > 0: self.SetStringItem( i, 3, room )
        self.AutoAjust()
        #self.update(player) # player object doesn't send role object.

    def setPlayerRole( self, id, role ):
        i = self.FindItemData( -1, int(id) )
        self.SetStringItem( i, 5, role )
        self.AutoAjust()

    def stripHtml( self, name ):
        ret_string = ""
        x = 0
        in_tag = 0
        for x in range( len(name) ):
            if name[x] == "<" or name[x] == ">" or in_tag == 1 :
                if name[x] == "<": in_tag = 1
                elif name[x] == ">": in_tag = 0
                else: pass
            else: ret_string = ret_string + name[x]
        return ret_string

    # When we right click, cause our popup menu to appear
    def OnPopupMenu( self, event ):
        pos = wx.Point( event.GetX(), event.GetY() )
        (item, flag) = self.HitTest( pos )
        if item > -1:
            self.selectedItem = item
            self.PopupMenu( self.menu, pos )

    # Process the events associated with our popup menu
    def OnPopupMenuItem( self, event ):
        # if we are not running, the player list is empty anyways
        if self.main.STATUS == SERVER_RUNNING:
            menuItem = event.GetId()
            playerID = str( self.GetItemData( self.selectedItem ) )
            room = str(self.GetItem((int(playerID)-1), 3).GetText())
            idList = self.main.server.server.groups
            for r in self.roomList:
                if room == self.roomList[r]: groupID = r
                else: groupID = 0
            if menuItem == 1:
                self.main.server.server.admin_kick( playerID )
            elif menuItem == 2:
                message = 'Banishment'
                BanMsg = wx.TextEntryDialog( self, "Enter A Message To Send:",
                                                 "Ban Message", message, wx.OK|wx.CANCEL|wx.CENTRE )
                if BanMsg.ShowModal() == wx.ID_OK: message = BanMsg.GetValue()
                else: return
                Silent = wx.MessageDialog(None, 'Silent Ban?', 'Question', 
                    wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION)
                if Silent.ShowModal() == wx.ID_YES: silent = 1
                else: silent = 0
                self.main.server.server.admin_ban(playerID, message, silent)
                self.remove( playerID )
            elif menuItem == 4:
                msg = self.GetMessageInput( "Send a message to player" )

                broadcast = '<chat type="1" version="1.0"><font color="#FF0000">' +msg+ '</font></chat>'
                chat = Element('chat')
                chat.set('type', '1')
                chat.set('version', '1.0')
                chat.text = broadcast
                msg = self.main.server.server.buildMsg(str(playerID), '0', '1', msg)

                if len(msg): self.main.server.server.players[playerID].outbox.put(msg)
            #Leave this in for now.
            elif menuItem == 5:
                msg = self.GetMessageInput( "Send message to room of this player")

                broadcast = '<chat type="1" version="1.0"><font color="#FF0000">' +msg+ '</font></chat>'
                chat = Element('chat')
                chat.set('type', '1')
                chat.set('version', '1.0')
                chat.text = broadcast
                msg = self.main.server.server.buildMsg('all', 
                                                        '0', 
                                                        str(self.main.server.server.players[playerID]), 
                                                        tostring(chat))

                if len(msg): self.main.server.server.send_to_group('0', str(groupID), msg )
            elif menuItem == 6:
                msg = self.GetMessageInput( "Broadcast Server Message" )
                if len(msg): self.main.server.server.broadcast(msg )
            elif menuItem == 3:
                version_string = self.main.server.server.obtain_by_id(playerID, 'client_string')
                if version_string: wx.MessageBox("Running client version " + version_string,"Version")
                else: wx.MessageBox("No client version available for this player", "Version")

    def GetMessageInput( self, title ):
        prompt = "Please enter the message you wish to send:"
        msg = wx.TextEntryDialog(self, prompt, title)
        msg.ShowModal()
        msg.Destroy()
        return msg.GetValue()

class ServerGUI(wx.Frame):
    STATUS = SERVER_STOPPED
    def __init__(self, parent, id, title):
        wx.Frame.__init__(self, parent, id, title, size = (760, 560) )
        if wx.Platform == '__WXMSW__': icon = wx.Icon(dir_struct["icon"]+'WAmisc9.ico', wx.BITMAP_TYPE_ICO)
        else: icon = wx.Icon(dir_struct["icon"]+'connect.gif', wx.BITMAP_TYPE_GIF)
        self.SetIcon(icon)
        self.serverName = "Server Name"
        self.bootPwd = ""
        self.do_log = True

        # Register our events to process -- notice the custom event handler
        self.Bind(wx.EVT_CLOSE, self.OnExit)
        self.Bind(EVT_LOG_MESSAGE, self.OnLogMessage)
        self.Bind(EVT_FUNCTION_MESSAGE, self.OnFunctionMessage)

        # Creat GUI
        self.build_menu()
        self.build_body()
        self.build_status()
        self.BanListDialog = BanListDialog(self)

        # Server Callbacks
        cb = {}
        cb["log"]        = self.Log
        cb["connect"]    = self.OnConnect
        cb["disconnect"] = self.OnDisconnect
        cb["update"]     = self.OnUpdatePlayer
        cb["data_recv"]  = self.OnDataRecv
        cb["data_sent"]  = self.OnDataSent
        cb["create_group"] = self.OnCreateGroup
        cb["delete_group"] = self.OnDeleteGroup
        cb["join_group"] = self.OnJoinGroup
        cb['update_group'] = self.OnUpdateGroup
        cb['exception'] = self.OnException
        cb["role"] = self.OnSetRole
        self.callbacks = cb

        # Misc.
        self.conf = ServerConfig(self)
        self.total_messages_received = 0
        self.total_data_received = 0
        self.total_messages_sent = 0
        self.total_data_sent = 0

    """ Build GUI """
    def build_menu(self):
        """ Build the GUI menu. """
        self.mainMenu = wx.MenuBar()

        # File Menu
        menu = wx.Menu()
        menu.Append(1, 'Start', 'Start server.')
        menu.Append(2, 'Stop', 'Shutdown server.')
        menu.Append(16, 'Clear Log', 'Empty server log')
        menu.AppendSeparator()
        menu.Append(3, 'E&xit', 'Exit application.')
        self.Bind(wx.EVT_MENU, self.OnStart, id=1)
        self.Bind(wx.EVT_MENU, self.OnStop, id=2)
        self.Bind(wx.EVT_MENU, self.OnExit, id=3)
        self.mainMenu.Append(menu, '&Server')

        # Registration Menu
        menu = wx.Menu()
        menu.Append(4, 'Register', 'Register with OpenRPG server directory.')
        menu.Append(5, 'Unregister', 'Unregister from OpenRPG server directory.')
        self.Bind(wx.EVT_MENU, self.OnRegister, id=4)
        self.Bind(wx.EVT_MENU, self.OnUnregister, id=5)
        self.mainMenu.Append( menu, '&Registration' )

        # Server Configuration Menu
        menu = wx.Menu()
        menu.Append(6, 'Ban List', 'Modify Ban List.')
        menu.Append(11, 'Zombies', 'Set auto-kick time for zombie clients')
        menu.Append(14, 'Send Size', 'Adjust the send size limit')
        menu.AppendSeparator()
        menu.Append(7, 'Start Ping', 'Ping players to validate remote connection.' )
        menu.Append(8, 'Stop Ping', 'Stop validating player connections.' )
        menu.Append(9, 'Ping Interval', 'Change the ping interval.' )
        menu.AppendSeparator()
        menu.AppendCheckItem(10, 'Server Logging', 
                                'Turn on or off the Server GUI Log').Check(self.do_log)
        menu.AppendCheckItem(12, 'Room Passwords', 'Allow or Deny Room Passwords').Check(False)
        menu.AppendCheckItem(13, 'Remote Admin', 'Allow or Deny Remote Admin').Check(False)
        menu.AppendCheckItem(15, 'Remote Kill', 'Allow or Deny Remote Admin Server Kill').Check(False)
        self.Bind(wx.EVT_MENU, self.ModifyBanList, id=6)
        self.Bind(wx.EVT_MENU, self.PingPlayers, id=7)
        self.Bind(wx.EVT_MENU, self.StopPingPlayers, id=8)
        self.Bind(wx.EVT_MENU, self.ConfigPingInterval, id=9)
        self.Bind(wx.EVT_MENU, self.LogToggle, id=10)
        self.Bind(wx.EVT_MENU, self.ClearLog, id=16)
        self.mainMenu.Append( menu, '&Configuration')

        # Traipse Suite of Additions.
        self.traipseSuite = wx.Menu()
        self.debugger = DebugConsole(self)
        self.mainMenu.Insert(3, self.traipseSuite, "&Traipse Suite")

        #Debugger Console
        self.debugConsole = wx.MenuItem(self.traipseSuite, -1, "Debug Console", "Debug Console")
        self.Bind(wx.EVT_MENU, self.OnMB_DebugConsole, self.debugConsole)
        self.traipseSuite.AppendItem(self.debugConsole)

        self.SetMenuBar(self.mainMenu)

        self.mainMenu.Enable(2, False)
        self.mainMenu.Enable(4, False)
        self.mainMenu.Enable(5, False)

        # Disable the ping menu items
        self.mainMenu.Enable(7, False)
        self.mainMenu.Enable(8, False)
        self.mainMenu.Enable(9, False)

        # Disable placeholders
        self.mainMenu.Enable(11, False)
        self.mainMenu.Enable(14, False)
        self.mainMenu.Enable(12, False)
        self.mainMenu.Enable(13, False)
        self.mainMenu.Enable(15, False)

    def OnException(self, error):
        self.TraipseSuiteWarn('debug')
        self.debugger.console.AppendText(".. " + str(error) +'\n')

    def OnMB_DebugConsole(self, evt):
        self.TraipseSuiteWarnCleanup('debug')
        if self.debugger.IsShown() == True: self.debugger.Hide()
        else: self.debugger.Show()

    def TraipseSuiteWarn(self, menuitem):
        ### Allows for the reuse of the 'Attention' menu.
        ### component.get('frame').TraipseSuiteWarn('item') ### Portable
        self.mainMenu.Remove(3)
        self.mainMenu.Insert(3, self.traipseSuite, "&Traipse Suite!")
        if menuitem == 'debug':
            if self.debugger.IsShown() == True:
                self.mainMenu.Remove(3)
                self.mainMenu.Insert(3, self.traipseSuite, "&Traipse Suite")
            else:
                self.debugConsole.SetBitmap(wx.Bitmap(dir_struct["icon"] + 'spotlight.png'))
                self.traipseSuite.RemoveItem(self.debugConsole)
                self.traipseSuite.AppendItem(self.debugConsole)

    def TraipseSuiteWarnCleanup(self, menuitem):
        ### Allows for portable cleanup of the 'Attention' menu.
        ### component.get('frame').TraipseSuiteWarnCleanup('item') ### Portable
        self.mainMenu.Remove(3)
        self.mainMenu.Insert(3, self.traipseSuite, "&Traipse Suite")        
        if menuitem == 'debug':
            self.traipseSuite.RemoveItem(self.debugConsole)
            self.debugConsole.SetBitmap(wx.Bitmap(dir_struct["icon"] + 'clear.gif'))
            self.traipseSuite.AppendItem(self.debugConsole)

    def build_body(self):
        """ Create the ViewNotebook and logger. """
        splitter = wx.SplitterWindow(self, -1, style=wx.NO_3D | wx.SP_3D)
        nb = wx.Notebook(splitter, -1)
        self.conns = Connections(nb, self)
        self.groups = Groups(nb, self)
        self.msgWindow = HTMLMessageWindow(nb)
        nb.AddPage(self.conns, "Players")
        nb.AddPage(self.groups, 'Rooms')
        nb.AddPage(self.msgWindow, "Messages")

        log = wx.TextCtrl(splitter, -1, style=wx.TE_MULTILINE | wx.TE_READONLY | wx.HSCROLL)
        wx.Log.SetActiveTarget(wx.LogTextCtrl(log))
        splitter.SplitHorizontally(nb, log, 400)
        splitter.SetMinimumPaneSize(40)
        self.nb = nb
        self.log = log

    def build_status(self):
        """ Create status bar and set defaults. """
        sb = wx.StatusBar(self, -1)
        sb.SetFieldsCount(5)
        sb.SetStatusWidths([-1, 115, 115, 65, 200])
        sb.SetStatusText("Sent: 0", 1)
        sb.SetStatusText("Recv: 0", 2)
        sb.SetStatusText("Stopped", 3)
        sb.SetStatusText("Unregistered", 4)
        self.SetStatusBar(sb)
        self.sb = sb

    def show_error(self, mesg, title = "Error"):
        """ Display an error.
            mesg (str) -- error message to display
            title (str) -- title of window
        """
        dlg = wx.MessageDialog(self, mesg, title, wx.OK | wx.ICON_EXCLAMATION)
        dlg.ShowModal()
        dlg.Destroy()


    # Event handler for out logging event
    def LogToggle(self, event):
        self.do_log = event.IsChecked()

    def ClearLog(self, event):
        self.log.SetValue('')

    def OnLogMessage( self, event ):
        self.Log( event.message )

    # Event handler for out logging event
    def OnFunctionMessage(self, event):
        self.callbacks[event.func]( event.message )

    ### Server Callbacks #####################################
    def Log(self, log):
        if self.do_log: wx.LogMessage(str(log))

    def OnConnect(self, player):
        self.conns.add(player)

    def OnDisconnect(self, id):
        self.conns.remove(id)

    def OnUpdatePlayer(self, data):
        self.conns.update(data)

    def OnDataSent(self, bytes):
        self.total_messages_sent += 1
        self.total_data_sent += bytes
        self.sb.SetStatusText("Sent: %s (%d)" % (format_bytes(self.total_data_sent), 
                                self.total_messages_sent), 1)

    def OnDataRecv(self, bytes):
        self.total_messages_received += 1
        self.total_data_received += bytes
        self.sb.SetStatusText("Recv: %s (%d)" % (format_bytes(self.total_data_received), 
                                self.total_messages_received), 2)

    def OnCreateGroup( self, data ):
        (room, room_id, player, pwd) = data
        self.groups.AddGroup(data)
        self.conns.roomList[room_id] = room
        data = (room, room_id, player)
        self.conns.updateRoom(data)

    def OnDeleteGroup(self, data):
        (room_id, player) = data
        self.groups.DeleteGroup(room_id)
        del self.conns.roomList[room_id]

    def OnJoinGroup(self, data):
        self.conns.updateRoom(data)

    def OnUpdateGroup(self, data):
        (room, room_id, players) = data
        self.groups.UpdateGroup(data)

    def OnSetRole( self, data ):
        (id, role) = data
        self.conns.setPlayerRole(id, role)

    ### Misc. ################################################
    def OnStart(self, event = None):
        """ Start server. """
        if self.STATUS == SERVER_STOPPED:
            ## Set name and admin password as empty
            self.serverName = ''
            self.bootPwd = ''
            # see if we already have serverName and bootPwd specified
            try:
                validate.config_file( "server_ini.xml", "default_server_ini.xml" ) 
                configDoc = parse(dir_struct["user"] + 'server_ini.xml').getroot()
                self.serverName = configDoc.get("name")
                if configDoc.get("admin"): self.bootPwd = configDoc.get("admin") 
                elif configDoc.get("boot"): self.bootPwd = configDoc.get("boot") 
            except: pass 
            if self.serverName == '':
                self.serverName = 'Server Name'
                serverNameEntry = wx.TextEntryDialog(self, 
                                    "Please Enter The Server Name You Wish To Use:",
                                    "Server's Name", 
                                    self.serverName, wx.OK|wx.CANCEL|wx.CENTRE)
                if serverNameEntry.ShowModal() == wx.ID_OK: self.serverName = serverNameEntry.GetValue()
            if self.bootPwd == '': 
                serverPasswordEntry = wx.TextEntryDialog(self, 
                                    "Please Enter The Server Admin Password:", 
                                    "Server's Password", 
                                    self.bootPwd, wx.OK|wx.CANCEL|wx.CENTRE)
                if serverPasswordEntry.ShowModal() == wx.ID_OK: self.bootPwd = serverPasswordEntry.GetValue()
            if len(self.serverName):
                wx.BeginBusyCursor()
                self.server = ServerMonitor(self.callbacks, self.conf, self.serverName, self.bootPwd)
                self.server.start()
                self.STATUS = SERVER_RUNNING
                self.sb.SetStatusText("Running", 3)
                self.SetTitle(__appname__ + "- (running) - (unregistered)")
                self.mainMenu.Enable(1, False)
                self.mainMenu.Enable(2, True)
                self.mainMenu.Enable(4, True)
                wx.EndBusyCursor()
            else: self.show_error("Server is already running.", "Error Starting Server")

    def OnStop(self, event=None):
        """ Stop server. """
        if self.STATUS == SERVER_RUNNING:
            self.OnUnregister(event)
            self.server.stop()
            self.STATUS = SERVER_STOPPED
            if event != 'Quit':
                self.sb.SetStatusText("Stopped", 3)
                self.SetTitle(__appname__ + "- (stopped) - (unregistered)")
                self.mainMenu.Enable(1, True)
                self.mainMenu.Enable(2, False)
                self.mainMenu.Enable(4, False)
                self.mainMenu.Enable(5, False)
                self.conns.DeleteAllItems()

    def OnRegister(self, event = None):
        """ Call into mplay_server's register() function.
            This will begin registerThread(s) to keep server
            registered with configured metas
        """
        if len( self.serverName ):
            wx.BeginBusyCursor()
            self.server.server.register(self.serverName)
            self.sb.SetStatusText( ("%s" % (self.serverName)), 4 )
            self.mainMenu.Enable(4, False)
            self.mainMenu.Enable(5, True)
            #self.mainMenu.Enable( 2, False )
            self.SetTitle(__appname__ + "- (running) - (registered)")
            wx.EndBusyCursor()

    def OnUnregister(self, event = None):
        """ Call into mplay_server's unregister() function.
            This will kill any registerThreads currently running
            and result in the server being de-listed
            from all metas
        """
        wx.BeginBusyCursor()
        self.server.server.unregister()
        if event != 'Quit':
            self.sb.SetStatusText("Unregistered", 4)
            self.mainMenu.Enable(5, False)
            self.mainMenu.Enable(4, True)
            #self.mainMenu.Enable( 2, True )
            self.SetTitle(__appname__ + "- (running) - (unregistered)")
        wx.EndBusyCursor()

    def ModifyBanList(self, event):
        if self.BanListDialog.IsShown() == True: self.BanListDialog.Hide()
        else: self.BanListDialog.Show()

    def PingPlayers( self, event = None ):
        "Ping all players that are connected at a periodic interval, detecting dropped connections."
        wx.BeginBusyCursor()
        wx.Yield()
        wx.EndBusyCursor()

    def StopPingPlayers( self, event = None ):
        "Stop pinging connected players."

    def ConfigPingInterval( self, event = None ):
        "Configure the player ping interval.  Note that all players are pinged on a single timer."

    def OnExit(self, event):
        dlg = wx.MessageDialog(self, "Exit the Server?", "OpenRPG- Server", wx.YES_NO)
        if dlg.ShowModal() == wx.ID_YES:
            dlg.Destroy()
            self.ExitConfirmed()

    def ExitConfirmed(self, event=None):
        """ Quit the program. """
        self.OnStop('Quit')
        self.BanListDialog.Destroy()
        wx.CallAfter(self.Destroy)

class BanListDialog(wx.Frame):
    def __init__(self, parent):
        super(BanListDialog, self).__init__(parent, -1, "Ban List")
        icon = wx.Icon(dir_struct["icon"]+'noplayer.gif', wx.BITMAP_TYPE_GIF)
        self.SetIcon( icon )
        self.BanList = wx.ListCtrl(self, wx.ID_ANY, style=wx.LC_SINGLE_SEL|wx.LC_REPORT|wx.LC_HRULES)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.BanList, 1, wx.EXPAND)
        self.BuildList()
        self.SetSizer(sizer)
        self.SetAutoLayout(True)
        self.SetSize((300, 175))
        self.Bind(wx.EVT_CLOSE, self.Min) 
        self.Min(None)

        # Ban List Dialog Pop Up Menu, more can be added
        self.menu = wx.Menu()
        self.menu.SetTitle( "Modify Ban List" )
        self.menu.Append( 1, "Un-Ban Player" )

        # Even Association
        self.BanList.Bind(wx.EVT_RIGHT_DOWN, self.BanPopupMenu)
        self.Bind(wx.EVT_MENU, self.BanPopupMenuItem, id=1)

    # When we right click, cause our popup menu to appear
    def BanPopupMenu( self, event ):
        pos = wx.Point( event.GetX(), event.GetY() )
        (item, flag) = self.BanList.HitTest( pos )
        if item > -1:
            self.selectedItem = item
            self.PopupMenu( self.menu, pos )

    def BanPopupMenuItem( self, event):
        menuItem = event.GetId()
        player = str(self.BanList.GetItemData(self.selectedItem))
        playerIP = str(self.BanList.GetItem((int(player)), 1).GetText())
        if menuItem == 1:
            server.admin_unban(playerIP)
            self.BanList.DeleteItem(self.BanList.GetItemData(self.selectedItem))
            self.BanList.Refresh()   

    def BuildList(self):
        # Build Dialog Columns
        self.BanList.ClearAll()
        self.BanList.InsertColumn(0, "User Name")
        self.BanList.InsertColumn(1, "IP")

        validate.config_file("ban_list.xml", "default_ban_list.xml" ) 
        configDom = parse(dir_struct["user"] + 'ban_list.xml').getroot()
        ban_dict = {}
        for element in configDom.findall('banned'):
            player = element.get('name').replace("&", "&amp;").replace("<", "&lt;").replace('"', "&quot;").replace(">", "&gt;")
            playerIP = element.get('ip')
            ban_dict[player] = playerIP
        for key in ban_dict:
            i = self.BanList.InsertImageStringItem( 0, key, 0 )
            self.BanList.SetStringItem(i, 1, ban_dict[key])
            self.BanList.RefreshItem(i)
        self.AutoAdjust()

    def AutoAdjust(self):
        self.BanList.SetColumnWidth(0, -1)
        self.BanList.SetColumnWidth(1, -1)
        self.BanList.Refresh()

    def Min(self, evt):
        self.BuildList()
        self.Hide()
###############

class ServerGUIApp(wx.App):
    def OnInit(self):
        # Make sure our image handlers are loaded before we try to display anything
        wx.InitAllImageHandlers()
        self.splash = wx.SplashScreen(wx.Bitmap(dir_struct["icon"]+'splash.gif'),
                              wx.SPLASH_CENTRE_ON_SCREEN|wx.SPLASH_TIMEOUT,
                              2000,
                              None)
        self.splash.Show(True)
        wx.Yield()
        wx.CallAfter(self.AfterSplash)
        return True

    def AfterSplash(self):
        self.splash.Close(True)
        frame = ServerGUI(None, -1, __appname__ + "- (stopped) - (unregistered)")
        frame.Show(True)
        frame.Raise()
        self.SetTopWindow(frame)

class HTMLMessageWindow(wx.html.HtmlWindow):
    "Widget used to present user to admin messages, in HTML format, to the server administrator"
    # Init using the derived from class
    def __init__( self, parent ):
        wx.html.HtmlWindow.__init__( self, parent )
    def OnLinkClicked( self, ref ):
        "Open an external browser to resolve our About box links!!!"
        href = ref.GetHref()
        webbrowser.open( href )

if __name__ == '__main__':
    app = ServerGUIApp(0)
    app.MainLoop()
