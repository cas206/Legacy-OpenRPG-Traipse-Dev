import os
import sys
import orpg.pluginhandler
from orpg.mapper.map import *
from orpg.orpgCore import component
import wx

from orpg.mapper.images import ImageHandler
from orpg.mapper.whiteboard_handler import *
from orpg.mapper.background_handler import *
from orpg.mapper.grid_handler import *
from orpg.mapper.map_handler import *
from orpg.mapper.fog_handler import *

from bcg.token_handler import *
from bcg.tokens import *


class Plugin(orpg.pluginhandler.PluginHandler):
    # Initialization subroutine.
    #
    # !self : instance of self
    # !openrpg : instance of the the base openrpg control
    def __init__(self, plugindb, parent):
        orpg.pluginhandler.PluginHandler.__init__(self, plugindb, parent)

        # The Following code should be edited to contain the proper information
        self.name = 'Board / Card Game'
        self.author = 'Tyler Starke (Prof. Ebral)'
        self.help = 'Start Here'
        self.parent = parent
        #You can set variables below here. Always set them to a blank value in this section. Use plugin_enabled
        #to set their proper values.
        self.sample_variable = {}

        self.canvas = component.get('map').canvas ## Obtain MapCanvas

    def plugin_enabled(self):
        tabs = component.get('map_tabs')
        layers = component.get('map_layers')
        map_wnd = component.get('map_wnd')
        pages = tabs.GetPageCount()
        self.layers = []
        while pages:
            pages -= 1
            if tabs.GetPageText(pages) != 'Background':
                if tabs.GetPageText(pages) != 'Whiteboard': 
                    tabs.RemovePage(pages)
        #tabs.InsertPage(2, layers[0], 'Tiles') # Removed for testing.
        map_wnd.handlers[6]=(token_handler(tabs, -1, map_wnd.canvas))
        tabs.InsertPage(3, map_wnd.handlers[6], 'Tokens')

        ## Re Direct MapCanvas OnPaint event.
        self.canvas.Disconnect(-1, -1, wx.wxEVT_PAINT)
        self.canvas.Bind(wx.EVT_PAINT, self.on_paint)

        ## Add to MapCanvas proccessImages
        self.canvas.Bind(wx.EVT_TIMER, self.processImages, self.canvas.image_timer)

        ## Create Token Layer
        self.canvas.layers['token'] = token_layer(self.canvas)
        #self.canvas.layers['tiles'] = tile_layer(self.canvas) #Not ready.

        ### Define Grid / Background
        self.canvas.layers['grid'].snap = False
        self.canvas.layers['grid'].line = 0
        #self.canvas.layers['bg'].set_texture(component.get('cherrypy')+'Textures/versa_anigre.jpg')
        pass

    def processImages(self, evt=None):
        self.session = component.get("session")
        if self.session.my_role() == self.session.ROLE_LURKER or (str(self.session.group_id) == '0' and str(self.session.status) == '1'):
            cidx = self.canvas.parent.get_tab_index("Tiles")
            self.canvas.parent.tabs.EnableTab(cidx, False)
            cidx = self.canvas.parent.get_tab_index("Tokens")
            self.canvas.parent.tabs.EnableTab(cidx, False)
        else:
            cidx = self.canvas.parent.get_tab_index("Tiles")
            self.canvas.parent.tabs.EnableTab(cidx, True)
            cidx = self.canvas.parent.get_tab_index("Tokens")
            self.canvas.parent.tabs.EnableTab(cidx, True)
        if not self.canvas.cacheSizeSet:
            self.canvas.cacheSizeSet = True
            cacheSize = component.get('settings').get_setting("ImageCacheSize")
            if len(cacheSize): self.canvas.cacheSize = int(cacheSize)
            else: pass
        if not ImageHandler.Queue.empty():
            (path, image_type, imageId) = ImageHandler.Queue.get()
            img = wx.ImageFromMime(path[1], path[2]).ConvertToBitmap()
            try:
                # Now, apply the image to the proper object
                if image_type == "miniature":
                    min = self.canvas.layers['miniatures'].get_miniature_by_id(imageId)
                    min.set_bmp(img)
                elif image_type == "background" or image_type == "texture":
                    self.canvas.layers['bg'].bg_bmp = img
                    if image_type == "background": self.canvas.set_size([img.GetWidth(), img.GetHeight()])
                elif image_type == "token":
                    min = self.canvas.layers['token'].get_token_by_id(imageId)
                    min.set_bmp(img)
            except: pass

    def on_paint(self, evt):
        if self.canvas.layers.has_key('token') == False: self.canvas.layers['token'] = token_layer(self.canvas)
        print 'BCG onpaint'
        scale = self.canvas.layers['grid'].mapscale
        scrollsize = self.canvas.GetScrollPixelsPerUnit()
        clientsize = self.canvas.GetClientSize()
        topleft1 = self.canvas.GetViewStart()
        topleft = [topleft1[0]*scrollsize[0], topleft1[1]*scrollsize[1]]
        if (clientsize[0] > 1) and (clientsize[1] > 1):
            dc = wx.MemoryDC()
            bmp = wx.EmptyBitmap(clientsize[0]+1, clientsize[1]+1)
            dc.SelectObject(bmp)
            dc.SetPen(wx.TRANSPARENT_PEN)
            dc.SetBrush(wx.Brush(self.canvas.GetBackgroundColour(), wx.SOLID))
            dc.DrawRectangle(0,0,clientsize[0]+1,clientsize[1]+1)
            dc.SetDeviceOrigin(-topleft[0], -topleft[1])
            dc.SetUserScale(scale, scale)
            self.canvas.layers['bg'].layerDraw(dc, scale, topleft, clientsize)
            self.canvas.layers['grid'].layerDraw(dc, [topleft[0]/scale, topleft[1]/scale], 
                [clientsize[0]/scale, clientsize[1]/scale])


            self.canvas.layers['token'].layerDraw(dc, [topleft[0]/scale, topleft[1]/scale], 
                [clientsize[0]/scale, clientsize[1]/scale])


            self.canvas.layers['whiteboard'].layerDraw(dc)
            self.canvas.layers['fog'].layerDraw(dc, topleft, clientsize)
            dc.SetPen(wx.NullPen)
            dc.SetBrush(wx.NullBrush)
            dc.SelectObject(wx.NullBitmap)
            del dc
            wdc = self.canvas.preppaint()
            wdc.DrawBitmap(bmp, topleft[0], topleft[1])
            if settings.get_setting("AlwaysShowMapScale") == "1":
                self.canvas.showmapscale(wdc)
        try: evt.Skip()
        except: pass

    def plugin_disabled(self):
        tabs = component.get('map_tabs')
        map_wnd = component.get('map_wnd')
        pages = tabs.GetPageCount()
        while pages:
            pages -= 1
            if tabs.GetPageText(pages) != 'Background':
                if tabs.GetPageText(pages) != 'Whiteboard': 
                    tabs.RemovePage(pages)
        layers = component.get('map_layers')
        tabs.InsertPage(1, layers[1],"Grid")
        tabs.InsertPage(2, layers[2],"Miniatures")
        tabs.InsertPage(4, layers[4],"Fog")
        tabs.InsertPage(5, layers[5],"General")
        map_wnd.current_layer = 2
        map_wnd.tabs.SetSelection(map_wnd.current_layer)
    
        ## Re Connect original MapCanvas OnPaint event.
        self.canvas.Disconnect(-1, -1, wx.wxEVT_PAINT)
        self.canvas.Bind(wx.EVT_PAINT, self.canvas.on_paint)

        ## Disconnect new proccessImages addition
        self.canvas.Disconnect(-1, -1, wx.wxEVT_TIMER)
        self.canvas.Bind(wx.EVT_TIMER, self.canvas.processImages, self.canvas.image_timer)

        self.canvas.layers['grid'].snap = True
        self.canvas.layers['grid'].line = 1

        #Here you need to remove any commands you added, and anything else you want to happen when you disable the plugin
        #such as closing windows created by the plugin
        #self.plugin_removecmd('/test')
        #self.plugin_removecmd('/example')

        #This is the command to delete a message handler
        #self.plugin_delete_msg_handler('xxblank')

        #This is how you should destroy a frame when the plugin is disabled
        #This same method should be used in close_module as well
        try:
            self.frame.Destroy()
        except:
            pass

    def on_test(self, cmdargs):
        #this is just an example function for a command you create.
        # cmdargs contains everything you typed after the command
        # so if you typed /test this is a test, cmdargs = this is a test
        # args are the individual arguments split. For the above example
        # args[0] = this , args[1] = is , args[2] = a , args[3] = test
        self.plugin_send_msg(cmdargs, '<xxblank>' + cmdargs + '</xxblank>')
        args = cmdargs.split(None,-1)
        msg = 'cmdargs = %s' % (cmdargs)
        self.chat.InfoPost(msg)

        if len(args) == 0:
            self.chat.InfoPost("You have no args")
        else:
            i = 0
            for n in args:
                msg = 'args[' + str(i) + '] = ' + n
                self.chat.InfoPost(msg)
                i += 1

    def on_xml_recive(self,id, data,xml_dom):
        self.chat.InfoPost(self.name + ":: Message recived<br />" + data.replace("<","&lt;").replace(">","&gt;") +'<br />From id:' + str(id))

    def pre_parse(self, text):
        #This is called just before a message is parsed by openrpg
        return text

    def send_msg(self, text, send):
        #This is called when a message is about to be sent out.
        #It covers all messages sent by the user, before they have been formatted.
        #If send is set to 0, the message will not be sent out to other
        #users, but it will still be posted to the user's chat normally.
        #Otherwise, send defaults to 1. (The message is sent as normal)
        return text, send

    def plugin_incoming_msg(self, text, type, name, player):
        #This is called whenever a message from someone else is received, no matter
        #what type of message it is.
        #The text variable is the text of the message. If the type is a regular
        #message, it is already formatted. Otherwise, it's not.
        #The type variable is an integer which tells you the type: 1=chat, 2=whisper
        #3=emote, 4=info, and 5=system.
        #The name variable is the name of the player who sent you the message.
        #The player variable contains lots of info about the player sending the
        #message, including name, ID#, and currently-set role.
        #Uncomment the following line to see the format for the player variable.
        #print player
        return text, type, name

    def post_msg(self, text, myself):
        #This is called whenever a message from anyone is about to be posted
        #to chat; it doesn't affect the copy of the message that gets sent to others
        #Be careful; system and info messages trigger this too.
        return text

    def refresh_counter(self):
        #This is called once per second. That's all you need to know.
        pass
