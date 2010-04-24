import os, re, wx
import orpg.pluginhandler

class Plugin(orpg.pluginhandler.PluginHandler):
    # Initialization subroutine.
    #
    # !self : instance of self
    # !chat : instance of the chat window to write to
    def __init__(self, plugindb, parent):
        orpg.pluginhandler.PluginHandler.__init__(self, plugindb, parent)

        # The Following code should be edited to contain the proper information
        self.name = 'URL to link conversion'
        self.author = 'tdb30 tbaleno@wrathof.com'
        self.help = "This plugin automaticaly wraps urls in link tags\n"
        self.help += "making them clickable."

        self.url_regex = None
        self.mailto_regex = None

    def plugin_menu(self):
        self.menu = wx.Menu()
        self.toggle = self.menu.AppendCheckItem(wx.ID_ANY, 'On')
        self.topframe.Bind(wx.EVT_MENU, self.plugin_toggle, self.toggle)
        self.toggle.Check(True)

    def plugin_toggle(self, evt):
        pass

    def plugin_enabled(self):
        #This is where you set any variables that need to be initalized when your plugin starts
        self.url_regex = re.compile("(?<![\[=\"a-z0-9:/.])((?:http|ftp|gopher)://)?(?<![@a-z])((?:[a-z0-9\-]+[-.]?[a-z0-9]+)*\.(?:[a-z]{2,4})(?:[a-z0-9_=\?\#\&~\%\.\-/\:\+;]*))", re.I)

        self.mailto_regex = re.compile("(?<![=\"a-z0-9:/.])((?:[a-z0-9]+[_]?[a-z0-9]*)+@{1}(?:[a-z0-9]+[-.]?[a-z0-9]+)*\.(?:[a-z]{2,4}))", re.I)

    def plugin_disabled(self):
        #Here you need to remove any commands you added, and anything else you want to happen when you disable the plugin
        #such as closing windows created by the plugin
        pass

    def pre_parse(self, text):
        if self.toggle.IsChecked() == True:
            text = self.mailto_regex.sub(self.regmailsub, text)
            text = self.url_regex.sub(self.regurlsub, text)
        return text

    def plugin_incoming_msg(self, text, type, name, player):
        if self.toggle.IsChecked() == True:
            text = self.mailto_regex.sub(self.regmailsub, text)
            text = self.url_regex.sub(self.regurlsub, text)
        return text, type, name

    def regmailsub(self, m):
        term = m.group(0).lower()
        return '<a href="mailto:' + term + '">' + m.group(0) + '</a>'

    def regurlsub(self, m):
        link = m.group(2)
        if m.group(1) != None:
            return '<a href="' + m.group(1).lower() + link + '">' + m.group(0) + '</a>'
        else:
            return '<a href="http://' + link + '">' + link + '</a>'
