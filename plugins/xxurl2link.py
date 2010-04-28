import os, re, wx
import orpg.pluginhandler

class Plugin(orpg.pluginhandler.PluginHandler):
    # Initialization subroutine.
    #
    # !self : instance of self
    # !chat : instance of the chat window to write to
    def __init__(self, plugindb, parent):
        orpg.pluginhandler.PluginHandler.__init__(self, plugindb, parent)

        self.name = 'URL to link conversion'
        self.author = 'tdb30 tbaleno@wrathof.com'
        self.help = "This plugin automaticaly wraps urls in link tags\n"
        self.help += "making them clickable."

    def plugin_menu(self):
        self.menu = wx.Menu()
        self.toggle = self.menu.AppendCheckItem(wx.ID_ANY, 'On')
        self.topframe.Bind(wx.EVT_MENU, self.plugin_toggle, self.toggle)

    def plugin_toggle(self, evt):
        if self.toggle.IsChecked() == True: self.plugindb.SetString('xxurl2link', 'url2link', 'True')
        if self.toggle.IsChecked() == False: self.plugindb.SetString('xxurl2link', 'url2link', 'False')
        pass

    def plugin_enabled(self):
        self.url_regex = re.compile( #from Paul Hayman of geekzilla
                    "((https?|ftp|gopher|telnet|file|notes|ms-help):((//)|(\\\\))+[\w\d:#@%/;$()~_?\+-=\\\.&]*)", re.I)
        self.mailto_regex = re.compile( #Taken from Django
                    r"(^[-!#$%&'*+/=?^_`{}|~0-9A-Z]+(\.[-!#$%&'*+/=?^_`{}|~0-9A-Z]+)*"  # dot-atom
                    r'|^"([\001-\010\013\014\016-\037!#-\[\]-\177]|\\[\001-011\013\014\016-\177])*"' # quoted-string
                    r')@(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?$', re.IGNORECASE)
        self.link = self.plugindb.GetString('xxurl2link', 'url2link', '') or 'False'
        self.toggle.Check(True) if self.link == 'True' else self.toggle.Check(False)

    def plugin_disabled(self):
        pass

    def pre_parse(self, text):
        text2 = text
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
        if m.group(1) != None: return '<a href="' + m.group(1).lower() + '">' + m.group(0) + '</a>'
        else: return '<a href="http://' + link + '">' + link + '</a>'
