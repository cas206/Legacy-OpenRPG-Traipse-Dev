import os
import orpg.pluginhandler
try: from orpg.orpgCore import component
except: from orpg.orpgCore import open_rpg
import wx

class Plugin(orpg.pluginhandler.PluginHandler):
    # Initialization subroutine.
    #
    # !self : instance of self
    # !openrpg : instance of the the base openrpg control
    def __init__(self, plugindb, parent):
        orpg.pluginhandler.PluginHandler.__init__(self, plugindb, parent)

        # The Following code should be edited to contain the proper information
        self.name = 'Mouse Zoom'
        self.author = 'Tyler Starke (Prof. Ebral)'
        self.help = 'This plugin allows users to zoom their map with super ease.  Hold Ctrl or Cmd and scroll your mouse '
        self.help += 'wheel and the map will zoom in or out.  And FAST too! \n'
        self.help += 'This plugin is designed for Grumpy Goblin and Ornery Orc.'

    def plugin_enabled(self):
        try: self.canvas = component.get('map').canvas
        except: self.canvas = open_rpg.get_component('map').canvas
        self.canvas.Bind(wx.EVT_MOUSEWHEEL, self.MouseWheel)

    def MouseWheel(self, evt):
        if evt.CmdDown():
            print evt.GetWheelRotation()
            if evt.GetWheelRotation() > 0: self.canvas.on_zoom_in(None)
            elif evt.GetWheelRotation() < 0: self.canvas.on_zoom_out(None)
            else: pass
        else: self.canvas.on_scroll(evt)

    def plugin_disabled(self):
        self.canvas.Disconnect(-1, -1, wx.wxEVT_MOUSEWHEEL)

