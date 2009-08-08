#!/usr/bin/env python
#
#   OpenRPG Server Graphical Interface
#        GNU General Public License
#

__appname__=' OpenRPG GUI Server v0.7 '
__version__='$Revision: 1.26 $'[11:-2]
__cvsinfo__='$Id: mplay_server_gui.py,v 1.26 2007/11/06 00:32:39 digitalxero Exp $'[5:-2]
__doc__="""OpenRPG Server Graphical Interface"""

import os
import sys
import time
import types
import orpg.dirpath
import orpg.systempath
from orpg.orpg_wx import *
import webbrowser
from threading import Thread
from meta_server_lib import post_server_data, remove_server
from mplay_server import mplay_server
from xml.dom import minidom

# Constants ######################################
SERVER_RUNNING = 1
SERVER_STOPPED = 0
MENU_START_SERVER = wx.NewId()
MENU_STOP_SERVER = wx.NewId()
MENU_EXIT = wx.NewId()
MENU_REGISTER_SERVER = wx.NewId()
MENU_UNREGISTER_SERVER = wx.NewId()
MENU_START_PING_PLAYERS = wx.NewId()
MENU_STOP_PING_PLAYERS = wx.NewId()
MENU_PING_INTERVAL = wx.NewId()

# Add our menu id's for our right click popup
MENU_PLAYER_BOOT = wx.NewId()
MENU_PLAYER_CREATE_ROOM = wx.NewId()
MENU_PLAYER_SEND_MESSAGE = wx.NewId()
MENU_PLAYER_SEND_ROOM_MESSAGE = wx.NewId()
MENU_PLAYER_SEND_SERVER_MESSAGE = wx.NewId()

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
        if b < 1024:
            return str(b) + f[i]
        else:
            b = b/1024
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
        setting used to control the server.
    """

    def __init__(self, owner ): 
        """ Loads default configuration settings."""
        userPath = orpg.dirpath.dir_struct["user"] 
        validate = orpg.tools.validate.Validate(userPath) 
        validate.config_file( "server_ini.xml", "default_server_ini.xml" ) 
        configDom = minidom.parse(userPath + 'server_ini.xml') 
        port = configDom.childNodes[0].childNodes[1].getAttribute('port')
        OPENRPG_PORT = 6774 if port == '' else int(port) #Pretty ugly, but I couldn't find the tag any other way.
        self.owner = owner

    def load_xml(self, xml):
        """ Load configuration from XML data.
            xml (xml) -- xml string to parse
        """
        pass

    def save_xml(self):
        """ Returns XML file representing
            the active configuration.
        """
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
class Connections(wx.ListCtrl):
    def __init__( self, parent, main ):
        wx.ListCtrl.__init__( self, parent, -1, wx.DefaultPosition, wx.DefaultSize, wx.LC_REPORT|wx.SUNKEN_BORDER|wx.EXPAND|wx.LC_HRULES )
        self.main = main
        self.roomList = { 0 : "Lobby" }
        self._imageList = wx.ImageList( 16, 16, False )
        img = wx.Image(orpg.dirpath.dir_struct["icon"]+"player.gif", wx.BITMAP_TYPE_GIF).ConvertToBitmap()
        self._imageList.Add( img )
        img = wx.Image(orpg.dirpath.dir_struct["icon"]+"player-whisper.gif", wx.BITMAP_TYPE_GIF).ConvertToBitmap()
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
        self.menu.Append( MENU_PLAYER_BOOT, "Boot Player" )
        self.menu.AppendSeparator()
        self.menu.Append( MENU_PLAYER_SEND_MESSAGE, "Send Player Message" )
        self.menu.Append( MENU_PLAYER_SEND_ROOM_MESSAGE, "Send Room Message" ) 
        self.menu.Append( MENU_PLAYER_SEND_SERVER_MESSAGE, "Broadcast Server Message" )

        # Associate our events
        self.Bind(wx.EVT_RIGHT_DOWN, self.OnPopupMenu)
        self.Bind(wx.EVT_MENU, self.OnPopupMenuItem, id=MENU_PLAYER_BOOT)
        self.Bind(wx.EVT_MENU, self.OnPopupMenuItem, id=MENU_PLAYER_SEND_MESSAGE)
        self.Bind(wx.EVT_MENU, self.OnPopupMenuItem, id=MENU_PLAYER_SEND_ROOM_MESSAGE)
        self.Bind(wx.EVT_MENU, self.OnPopupMenuItem, id=MENU_PLAYER_SEND_SERVER_MESSAGE)

    def add(self, player):
        i = self.InsertImageStringItem( 0, player["id"], 0 )
        self.SetStringItem( i, 1, self.stripHtml( player["name"] ) )
        self.SetStringItem( i, 2, "new" )
        self.SetStringItem( i, 3, self.roomList[0] )
        self.SetStringItem( i, 4, self.stripHtml( player["version"] ) )
        self.SetStringItem( i, 5, self.stripHtml( player["role"] ) )
        self.SetStringItem( i, 6, self.stripHtml( player["ip"] ) )
        self.SetStringItem (i, 7, "PING" )
        self.SetItemData( i, int(player["id"]) )
        self.AutoAjust()

    def remove(self, id):
        i = self.FindItemData( -1, int(id) )
        self.DeleteItem( i )
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

    def update(self, player):
        i = self.FindItemData( -1, int(player["id"]) )
        if i > -1:
            self.SetStringItem(i, 1, self.stripHtml(player["name"]))
            self.SetStringItem(i, 2, self.stripHtml(player["status"]))
            self.AutoAjust()
        else: self.add(player)

    def updateRoom( self, data ):
        (room, room_id, player) = data
        i = self.FindItemData( -1, int(player) )
        if i > 0: self.SetStringItem( i, 3, room )
        self.AutoAjust()

    def setPlayerRole( self, id, role ):
        i = self.FindItemData( -1, int(id) )
        self.SetStringItem( i, 5, role )

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
            if menuItem == MENU_PLAYER_BOOT:
                print "booting player: ", playerID
                self.main.server.server.del_player( playerID, groupID )
                self.main.server.server.check_group( playerID, groupID )
                self.remove( playerID )
            elif menuItem == MENU_PLAYER_SEND_MESSAGE:
                print "send a message..."
                msg = self.GetMessageInput( "Send a message to player" )
                if len(msg): self.main.server.server.send( msg, playerID, str(groupID) )
            #Leave this in for now.
            elif menuItem == MENU_PLAYER_SEND_ROOM_MESSAGE:
                print "Send message to room..."
                msg = self.GetMessageInput( "Send message to room of this player")
                if len(msg): self.main.server.server.send_to_group('0', str(groupID), msg )

            elif menuItem == MENU_PLAYER_SEND_SERVER_MESSAGE:
                print "broadcast a message..."
                msg = self.GetMessageInput( "Broadcast Server Message" )
                # If we got a message back, send it
                if len(msg):
                    self.main.server.server.broadcast( msg )

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
        if wx.Platform == '__WXMSW__': icon = wx.Icon( orpg.dirpath.dir_struct["icon"]+'WAmisc9.ico', wx.BITMAP_TYPE_ICO )
        else: icon = wx.Icon( orpg.dirpath.dir_struct["icon"]+'connect.gif', wx.BITMAP_TYPE_GIF )
        self.SetIcon(icon)
        self.serverName = "Server Name"
        self.bootPwd = ""

        # Register our events to process -- notice the custom event handler
        self.Bind(wx.EVT_CLOSE, self.OnExit)
        self.Bind(EVT_LOG_MESSAGE, self.OnLogMessage)
        self.Bind(EVT_FUNCTION_MESSAGE, self.OnFunctionMessage)

        # Creat GUI
        self.build_menu()
        self.build_body()
        self.build_status()

        # Server Callbacks
        cb = {}
        cb["log"]        = self.Log
        cb["connect"]    = self.OnConnect  ##Fixed!!
        cb["disconnect"] = self.OnDisconnect
        cb["update"]     = self.OnUpdatePlayer
        cb["data_recv"]  = self.OnDataRecv
        cb["data_sent"]  = self.OnDataSent
        cb["create_group"] = self.OnCreateGroup
        cb["delete_group"] = self.OnDeleteGroup
        cb["join_group"] = self.OnJoinGroup
        cb["role"] = self.OnSetRole
        self.callbacks = cb

        # Misc.
        self.conf = ServerConfig(self)
        self.total_messages_received = 0
        self.total_data_received = 0
        self.total_messages_sent = 0
        self.total_data_sent = 0

    ### Build GUI ############################################

    def build_menu(self):
        """ Build the GUI menu. """
        self.mainMenu = wx.MenuBar()
        # File Menu
        menu = wx.Menu()
        # Start
        menu.Append( MENU_START_SERVER, 'Start', 'Start server.')
        self.Bind(wx.EVT_MENU, self.OnStart, id=MENU_START_SERVER)
        # Stop
        menu.Append( MENU_STOP_SERVER, 'Stop', 'Shutdown server.')
        self.Bind(wx.EVT_MENU, self.OnStop, id=MENU_STOP_SERVER)
        # Exit
        menu.AppendSeparator()
        menu.Append( MENU_EXIT, 'E&xit', 'Exit application.')
        self.Bind(wx.EVT_MENU, self.OnExit, id=MENU_EXIT)
        self.mainMenu.Append(menu, '&Server')
        # Registration Menu
        menu = wx.Menu()
        # Register
        menu.Append( MENU_REGISTER_SERVER, 'Register', 'Register with OpenRPG server directory.')
        self.Bind(wx.EVT_MENU, self.OnRegister, id=MENU_REGISTER_SERVER)
        # Unregister
        menu.Append( MENU_UNREGISTER_SERVER, 'Unregister', 'Unregister from OpenRPG server directory.')
        self.Bind(wx.EVT_MENU, self.OnUnregister, id=MENU_UNREGISTER_SERVER)
        # Add the registration menu
        self.mainMenu.Append( menu, '&Registration' )
        # Server Configuration Menu
        menu = wx.Menu()
        # Ping Connected Players
        menu.Append( MENU_START_PING_PLAYERS, 'Start Ping', 'Ping players to validate remote connection.' )
        self.Bind(wx.EVT_MENU, self.PingPlayers, id=MENU_START_PING_PLAYERS)
        # Stop Pinging Connected Players
        menu.Append( MENU_STOP_PING_PLAYERS, 'Stop Ping', 'Stop validating player connections.' )
        self.Bind(wx.EVT_MENU, self.StopPingPlayers, id=MENU_STOP_PING_PLAYERS)
        # Set Ping Interval
        menu.Append( MENU_PING_INTERVAL, 'Ping Interval', 'Change the ping interval.' )
        self.Bind(wx.EVT_MENU, self.ConfigPingInterval, id=MENU_PING_INTERVAL)
        self.mainMenu.Append( menu, '&Configuration' )
        # Add the menus to the main menu bar
        self.SetMenuBar( self.mainMenu )
        # Disable register, unregister & stop server by default
        self.mainMenu.Enable( MENU_STOP_SERVER, False )
        self.mainMenu.Enable( MENU_REGISTER_SERVER, False )
        self.mainMenu.Enable( MENU_UNREGISTER_SERVER, False )
        # Disable the ping menu items
        self.mainMenu.Enable( MENU_START_PING_PLAYERS, False )
        self.mainMenu.Enable( MENU_STOP_PING_PLAYERS, False )
        self.mainMenu.Enable( MENU_PING_INTERVAL, False )

    def build_body(self):
        """ Create the ViewNotebook and logger. """
        splitter = wx.SplitterWindow(self, -1, style=wx.NO_3D | wx.SP_3D)
        nb = wx.Notebook( splitter, -1 )
        self.conns = Connections( nb, self )
        nb.AddPage( self.conns, "Players" )

        #Not sure why this is Remarked TaS - Sirebral
        #nb.AddPage( self.conns, "Rooms" )
        #self.msgWindow = HTMLMessageWindow( nb )
        #nb.AddPage( self.msgWindow, "Messages" )

        log = wx.TextCtrl(splitter, -1, style=wx.TE_MULTILINE | wx.TE_READONLY | wx.HSCROLL)
        wx.Log.SetActiveTarget( wx.LogTextCtrl(log) )
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
    def OnLogMessage( self, event ):
        self.Log( event.message )

    # Event handler for out logging event
    def OnFunctionMessage( self, event ):
        self.callbacks[event.func]( event.message )

    ### Server Callbacks #####################################
    def Log(self, log):
        wx.LogMessage(str(log))

    def OnConnect(self, player):
        self.conns.add(player)

    def OnDisconnect(self, id):
        self.conns.remove(id)

    def OnUpdatePlayer(self, data):
        self.conns.update(data)

    def OnDataSent(self, bytes):
        self.total_messages_sent += 1
        self.total_data_sent += bytes
        self.sb.SetStatusText("Sent: %s (%d)" % (format_bytes(self.total_data_sent), self.total_messages_sent), 1)

    def OnDataRecv(self, bytes):
        self.total_messages_received += 1
        self.total_data_received += bytes
        self.sb.SetStatusText("Recv: %s (%d)" % (format_bytes(self.total_data_received), self.total_messages_received), 2)

    def OnCreateGroup( self, data ):
        room_id = data[1]
        name = data[0]
        self.conns.roomList[room_id] = name
        (room, room_id, player) = data
        self.conns.updateRoom(data)

    def OnDeleteGroup( self, data ):
        (room_id, player) = data
        del self.conns.roomList[room_id]

    def OnJoinGroup( self, data ):
        self.conns.updateRoom( data )

    def OnSetRole( self, data ):
        (id, role) = data
        self.conns.setPlayerRole( id, role )

    ### Misc. ################################################
    def OnStart(self, event = None):
        """ Start server. """
        if self.STATUS == SERVER_STOPPED:
            # see if we already have name specified 
            try:
                userPath = orpg.dirpath.dir_struct["user"] 
                validate = orpg.tools.validate.Validate(userPath) 
                validate.config_file( "server_ini.xml", "default_server_ini.xml" ) 
                configDom = minidom.parse(userPath + 'server_ini.xml') 
                configDom.normalize() 
                configDoc = configDom.documentElement 
                if configDoc.hasAttribute("name"): self.serverName = configDoc.getAttribute("name")
            except: pass 
            if self.serverName == '': 
                serverNameEntry = wx.TextEntryDialog( self, "Please Enter The Server Name You Wish To Use:",
                                                 "Server's Name", self.serverName, wx.OK|wx.CANCEL|wx.CENTRE )
                if serverNameEntry.ShowModal() == wx.ID_OK: self.serverName = serverNameEntry.GetValue()
            # see if we already have password specified 
            try: 
                userPath = orpg.dirpath.dir_struct["user"] 
                validate = orpg.tools.validate.Validate(userPath) 
                validate.config_file( "server_ini.xml", "default_server_ini.xml" ) 
                configDom = minidom.parse(userPath + 'server_ini.xml') 
                configDom.normalize() 
                configDoc = configDom.documentElement 
                if configDoc.hasAttribute("admin"): self.bootPwd = configDoc.getAttribute("admin") 
                elif configDoc.hasAttribute("boot"): self.bootPwd = configDoc.getAttribute("boot") 
            except: pass 
            if self.bootPwd == '': 
                serverPasswordEntry = wx.TextEntryDialog(self, "Please Enter The Server Admin Password:", "Server's Password", self.bootPwd, wx.OK|wx.CANCEL|wx.CENTRE)
                if serverPasswordEntry.ShowModal() == wx.ID_OK: self.bootPwd = serverPasswordEntry.GetValue()

            if len(self.serverName):
                wx.BeginBusyCursor()
                self.server = ServerMonitor(self.callbacks, self.conf, self.serverName, self.bootPwd)
                self.server.start()
                self.STATUS = SERVER_RUNNING
                self.sb.SetStatusText("Running", 3)
                self.SetTitle(__appname__ + "- (running) - (unregistered)")
                self.mainMenu.Enable( MENU_START_SERVER, False )
                self.mainMenu.Enable( MENU_STOP_SERVER, True )
                self.mainMenu.Enable( MENU_REGISTER_SERVER, True )
                wx.EndBusyCursor()
            else: self.show_error("Server is already running.", "Error Starting Server")

    def OnStop(self, event = None):
        """ Stop server. """
        if self.STATUS == SERVER_RUNNING:
            self.OnUnregister()
            self.server.stop()
            self.STATUS = SERVER_STOPPED
            self.sb.SetStatusText("Stopped", 3)
            self.SetTitle(__appname__ + "- (stopped) - (unregistered)")
            self.mainMenu.Enable( MENU_STOP_SERVER, False )
            self.mainMenu.Enable( MENU_START_SERVER, True )
            self.mainMenu.Enable( MENU_REGISTER_SERVER, False )
            self.mainMenu.Enable( MENU_UNREGISTER_SERVER, False )
            # Delete any items that are still in the player list
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
            self.mainMenu.Enable( MENU_REGISTER_SERVER, False )
            self.mainMenu.Enable( MENU_UNREGISTER_SERVER, True )
            self.mainMenu.Enable( MENU_STOP_SERVER, False )
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
        self.sb.SetStatusText( "Unregistered", 4 )
        self.mainMenu.Enable( MENU_UNREGISTER_SERVER, False )
        self.mainMenu.Enable( MENU_REGISTER_SERVER, True )
        self.mainMenu.Enable( MENU_STOP_SERVER, True )
        self.SetTitle(__appname__ + "- (running) - (unregistered)")
        wx.EndBusyCursor()

    def PingPlayers( self, event = None ):
        "Ping all players that are connected at a periodic interval, detecting dropped connections."
        wx.BeginBusyCursor()
        wx.Yield()
        wx.EndBusyCursor()

    def StopPingPlayers( self, event = None ):
        "Stop pinging connected players."

    def ConfigPingInterval( self, event = None ):
        "Configure the player ping interval.  Note that all players are pinged on a single timer."

    def OnExit(self, event = None):
        """ Quit the program. """
        self.OnStop()
        wx.CallAfter(self.Destroy)

class ServerGUIApp(wx.App):
    def OnInit(self):
        # Make sure our image handlers are loaded before we try to display anything
        wx.InitAllImageHandlers()
        self.splash = wx.SplashScreen(wx.Bitmap(orpg.dirpath.dir_struct["icon"]+'splash.gif'),
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
