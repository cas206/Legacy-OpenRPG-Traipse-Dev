import os
import wx
import orpg.plugindb # VEG
import orpg.pluginhandler
from orpg.orpgCore import *
import urllib
import thread
import socket
import cherrypy._cpserver as server
from xml.dom.minidom import parseString

 # VEG (march 21, 2007): Now remembers your last web server on/off setting

class Plugin(orpg.pluginhandler.PluginHandler):
    # Initialization subroutine.
    #
    # !self : instance of self
    # !openrpg : instance of the the base openrpg control
    def __init__(self, plugindb, parent):
        orpg.pluginhandler.PluginHandler.__init__(self, plugindb, parent)

        # The Following code should be edited to contain the proper information
        self.name = 'CherryPy Web Server'
        self.author = 'Dj Gilcrease & Sir. Ebral'
        self.help = 'This plugin turns OpenRPG into a Web server\n'
        self.help += 'allowing you to host your map and mini files locally.'

        #You can set variables below here. Always set them to a blank value in this section. Use plugin_enabled
        #to set their proper values.
        self.isServerRunning = 'off'
        self.host = 0

    def plugin_menu(self):
        self.menu = wx.Menu()
        self.toggle = self.menu.AppendCheckItem(wx.ID_ANY, 'On')
        self.topframe.Bind(wx.EVT_MENU, self.cherrypy_toggle, self.toggle)

    def cherrypy_toggle(self, evt): #TAS
        if self.toggle.IsChecked() == True: self.on_cherrypy("on") 
        if self.toggle.IsChecked() == False: self.on_cherrypy("off")

    def plugin_enabled(self):
        self.host = parseString(
            urllib.urlopen("http://orpgmeta.appspot.com/myip").read()
        ).documentElement.getAttribute("ip")

        self.port = int(self.plugindb.GetString("xxcherrypy", "port", 8080)) or 6775

        self.plugin_addcommand('/cherrypy', self.on_cherrypy, 
            '[on | off | port | status] - This controls the CherryPy Web Server')

        self.on_cherrypy(self.plugindb.GetString("xxcherrypy", "auto_start", None))  # VEG

        self.cherryhost = 'http://' + self.host + ':' + str(self.port) + '/webfiles/'
        open_rpg.add_component("cherrypy", self.cherryhost)

    def plugin_disabled(self):
        #Here you need to remove any commands you added, and anything else you want to happen when you disable the plugin
        #such as closing windows created by the plugin
        self.plugin_removecmd('/cherrypy')
        if self.isServerRunning == 'on':
            server.stop()
            self.isServerRunning = 'off'
        else:
            pass
        open_rpg.del_component("cherrypy")

    def on_cherrypy(self, cmdargs):
        args = cmdargs.split(None,-1)

        if len(args) == 0 or args[0] == 'status':
            self.chat.InfoPost("CherryPy Web Server is currently: " + self.isServerRunning)
            self.chat.InfoPost("CherryPy Web Server address is: " + self.cherryhost)

        elif args[0] == 'on' and self.isServerRunning == 'off':
            self.webserver = thread.start_new_thread(self.startServer, (self.port,))
            self.isServerRunning = 'on'
            self.toggle.Check(True)
            self.plugindb.SetString("xxcherrypy", "auto_start", "on") # VEG

        elif args[0] == 'off' and self.isServerRunning == 'on':
            server.stop()
            self.isServerRunning = 'off'
            self.toggle.Check(False)
            self.chat.InfoPost("CherryPy Web Server is currently: " + self.isServerRunning)
            self.plugindb.SetString("xxcherrypy", "auto_start", "off") # VEG

        elif args[0] == 'port': #TAS
            if self.isServerRunning == 'on':
                self.chat.InfoPost('Please turn CherryPy off first!')
                return
            self.port = int(args[1])
            self.plugindb.SetString("xxcherrypy", "port", str(self.port)) # TAS
            self.chat.InfoPost("CherryPy Web Server is currently: " + self.isServerRunning)
            self.cherryhost = 'http://' + self.host + ':' + str(self.port) + '/webfiles/'
            open_rpg.del_component("cherrypy"); open_rpg.add_component("cherrypy", self.cherryhost)
            self.chat.InfoPost('CherryPy Web Server address is: ' + self.cherryhost)

    def startServer(self, port):
        try:
            if self.host == 0:
                raise Exception("Invalid IP address.<br />This error means you are behind a router or some other form of network that is giving you a Privet IP only (ie. 192.168.x.x, 10.x.x.x, 172.16 - 32.x.x)")

            self.chat.InfoPost("CherryPy Web Server is now running on http://" + str(self.host) + ':' + str(self.port) + '/webfiles/')
            server.start(configMap =
                        {'staticContentList': [['', r''+orpg.dirpath.dir_struct["user"]+'webfiles/'],
                                               ['webfiles', r''+orpg.dirpath.dir_struct["user"]+'webfiles/']],
                        'socketPort': port,
                        'logToScreen': 0,
                        'logFile':orpg.dirpath.dir_struct["user"]+'webfiles/log.txt',
                        'sessionStorageType':'ram',
                        'threadPool':10,
                        'sessionTimeout':30,
                        'sessionCleanUpDelay':30})

        except Exception, e:
            self.chat.InfoPost("FAILED to start server!")
            self.chat.InfoPost(str(e))
            self.isServerRunning = 'off'
            self.toggle.Check(False)
