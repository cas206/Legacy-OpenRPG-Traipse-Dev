import os, re, wx
import orpg.pluginhandler
from orpg.tools.InterParse import Parse

class Plugin(orpg.pluginhandler.PluginHandler):
    # Initialization subroutine.
    #
    # !self : instance of self
    # !openrpg : instance of the the base openrpg control
    def __init__(self, plugindb, parent):
        orpg.pluginhandler.PluginHandler.__init__(self, plugindb, parent)

        # The Following code should be edited to contain the proper information
        self.name = 'Hidden Dice'
        self.author = 'mDuo13'
        self.help = 'Roll with curly brackets to hide your roll,\n'
        self.help += 'having it display only for you. Other players will\n'
        self.help += 'get a message that only says you are rolling.\n'
        self.help += 'Useful for GMs who want to roll secretly.'

        #You can set variables below here. Always set them to a blank value in this section. Use plugin_enabled
        #to set their proper values.
        self.hiddenrolls = []
        self.dicere = "\{([0-9]*d[0-9]*.+)\}"

    def plugin_menu(self):
        self.menu = wx.Menu()
        self.toggle = self.menu.AppendCheckItem(wx.ID_ANY, 'On')
        self.topframe.Bind(wx.EVT_MENU, self.plugin_toggle, self.toggle)
        self.toggle.Check(True)

    def plugin_toggle(self, evt):
        pass

    def plugin_enabled(self):
        pass

    def plugin_disabled(self):
        pass

    def pre_parse(self, text):
        if self.toggle.IsChecked() == True:
            m = re.search(self.dicere, text)
            while m:
                roll = "[" + m.group(1) + "]"
                self.hiddenrolls += [Parse.Dice(roll)]
                text = text[:m.start()] + "(hidden roll)" + text[m.end():]
                m = re.search(self.dicere, text)
        return text

    def post_msg(self, text, myself):
        if self.toggle.IsChecked() == True:
            c = 0
            a = text.find("(hidden roll)")
            while len(self.hiddenrolls) > c and a > -1:
                text = text[:a+14].replace("(hidden roll)", self.hiddenrolls[c]) + text[a+14:]
                a = text.find("(hidden roll)")
                c += 1
            if c > 0:
                self.hiddenrolls = []
        return text
