import os, wx
import orpg.pluginhandler

class Plugin(orpg.pluginhandler.PluginHandler):
    # Initialization subroutine.
    #
    # !self : instance of self
    # !chat : instance of the chat window to write to
    def __init__(self, plugindb, parent):
        orpg.pluginhandler.PluginHandler.__init__(self, plugindb, parent)

        # The Following code should be edited to contain the proper information
        self.name = 'Spelling Checker (aka Autoreplace)'
        self.author = 'Woody, mDuo13'
        self.help = "This plugin automatically replaces certain keys with other ones wheneve\nr"
        self.help += "it sees them. You can edit this plugin to change what it replaces. This one\n"
        self.help += "even corrects other people's spelling."
        self.checklist = {}

    def plugin_menu(self):
        self.menu = wx.Menu()
        self.toggle = self.menu.AppendCheckItem(wx.ID_ANY, 'On')
        self.topframe.Bind(wx.EVT_MENU, self.plugin_toggle, self.toggle)
        self.toggle.Check(True)

    def plugin_toggle(self, evt):
        pass

    def plugin_enabled(self):
        #This is where you set any variables that need to be initalized when your plugin starts
        #You can add new /commands like
        self.plugin_addcommand("/spell", self.on_spell, "[add {bad_word} {new_word} | list | remove {bad_word}] - This function allows you to add words to be auto replaced when they are sent or recived. If you want either word to have a space in it you will need to use the _ (underscore) as a space, it will be replaced with a space before it is added to the check list")
        self.checklist = self.plugindb.GetDict("xxspell", "checklist", {})

    def plugin_disabled(self):
        #Here you need to remove any commands you added, and anything else you want to happen when you disable the plugin
        #such as closing windows created by the plugin
        self.plugin_removecmd('/spell')

    def replace(self, text):
        for a in self.checklist.keys():
            text = text.replace(a, self.checklist[a])
        return text

    def plugin_incoming_msg(self, text, type, name, player):
        if self.toggle.IsChecked() == True:
            text = self.replace(text)
        return text, type, name

    def pre_parse(self, text):
        if self.toggle.IsChecked() == True:
            text = self.replace(text)
        return text

    def on_spell(self, cmdargs):
        args = cmdargs.split(None,-1)
        if len(args) == 0:
            args = [' ']
        if args[0] == 'list':
            self.chat.InfoPost(self.make_list())
        elif args[0] == 'remove':
            args = self.create_spaces(args)
            if self.checklist.has_key(args[1]):
                del self.checklist[args[1]]
                self.plugindb.SetDict("xxspell", "checklist", self.checklist)
                self.chat.InfoPost("%s removed from the check list" % args[1])
            else:
                self.chat.InfoPost("%s was not in the check list" % args[1])
        elif args[0] == 'add':
            args = self.create_spaces(args)
            self.checklist[args[1]] = args[2]
            self.plugindb.SetDict("xxspell", "checklist", self.checklist)
            self.chat.InfoPost("%s will now be replaced by %s" % (args[1], args[2]))
        else:
            helptxt = "Spelling Command Help:<br />"
            helptxt += "<b>/spell add bad_word new_word</b> - Here it is important to remember that any spaces in your bad or new words needs to be type as _ (an underscore).<br />"
            helptxt += "<b>/spell remove bad_word</b> - Here it is important to remember that any spaces in your bad word needs to be type as _ (an underscore).<br />"
            helptxt += "<b>/spell list</b> - This will list all of the bad words you are checking for, along with thier replacements.<br />"
            self.chat.InfoPost(helptxt)


    def create_spaces(self, list):
        i = 0
        for n in list:
            list[i] = n.replace("_"," ")
            i += 1
        return list

    def make_list(self):
        keychain = self.checklist.keys()
        lister = ""
        for key in keychain:
            lister += "<b>" + key.replace("<","&lt;").replace(">","&gt;") + "</b> :: <b>" + self.checklist[key].replace("<","&lt;").replace(">","&gt;") + "</b><br />"
        if len(keychain)==0:
            return "No variables!"
        else:
            return lister
