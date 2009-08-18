import os
import orpg.pluginhandler
from orpg.dirpath import dir_struct
import re
import string
from orpg.orpgCore import component

class Plugin(orpg.pluginhandler.PluginHandler):
    # Initialization subroutine.
    #
    # !self : instance of self
    # !openrpg : instance of the the base openrpg control
    def __init__(self, plugindb, parent):
        orpg.pluginhandler.PluginHandler.__init__(self, plugindb, parent)

        # The Following code should be edited to contain the proper information
        self.name = 'Name Sound'
        self.author = 'mDuo13'
        self.help = "This plays a 'hey!' sound whenever your name is said in chat. It is\n"
        self.help += "not HTML- or case-sensitive. You can also create nicknames to which the plugin\n"
        self.help += "will also respond. To add a nickname, type '/xxnick add *name*', where *name*\n"
        self.help += "is the nickname you want to add. Then, whenever *name* is said in chat, you'll\n"
        self.help += "hear the sound also. You can remove your nicknames by typing\n"
        self.help += "'/xxnick del*name*' where *name* is the nickname you wish to delete. Neither is\n"
        self.help += "case sensitive. Additionally, you can see what nicknames you currently have\n"
        self.help += "with '/xxnick list'."

        self.antispam = 0
        self.names = []
        self.soundfile = ''
        self.soundplayer = ''
        self.notify = False


    def plugin_enabled(self):
        self.plugin_addcommand('/xxnick', self.on_xxnick, 'add name|del name|list - This is the command for the namesound plugin')
        self.plugin_addcommand('/wnotify', self.on_wnotify, 'This will toggle notification on incoming whispers')
        self.plugin_addcommand('/sfile', self.on_sfile, 'This will set the sound file to use for notification')

        self.names = self.plugindb.GetList("xxnamesound", "names", [])

        self.soundplayer = self.sound_player = component.get('sound')

        tmp = self.plugindb.GetString('xxnamesound', 'wnotify', str(self.notify))
        if tmp == 'True':
            self.on_wnotify(None)

        self.soundfile = self.plugindb.GetString('xxnamesound', 'soundfile', dir_struct['plugins'] + 'heya.wav')


        reg = []

        if not self.chat.html_strip(self.session.name.lower()) in self.names:
            self.names.append(self.chat.html_strip(self.session.name.lower()))

        for name in self.names:
            reg.append("(?<![a-zA-Z0-9>/\#\-])" + name + "(?!\w+|[<])")

        reg = string.join(reg, "|")
        self.nameReg = re.compile(reg, re.I)


    def plugin_disabled(self):
        self.plugin_removecmd('/xxnick')
        self.plugin_removecmd('/wnotify')
        self.plugin_removecmd('/sfile')


    def on_wnotify(self, cmdargs):
        self.notify = not self.notify

        self.plugindb.SetString('xxnamesound', 'wnotify', str(self.notify))

        if self.notify:
            self.chat.InfoPost("Whisper Notification is On!")
        else:
            self.chat.InfoPost("Whisper Notification is Off!")


    def on_sfile(self, cmdargs):
        self.soundfile = cmdargs
        self.plugindb.SetString('xxnamesound', 'soundfile', cmdargs)

    def on_xxnick(self, cmdargs):
        args = cmdargs.split(None,-1)
        reg = []
        if len(args):
            name = cmdargs[len(args[0])+1:].lower().strip()

        if len(args) == 0 or args[0] == 'list':
            name_list = ''
            i = 0
            for name in self.names:
                name_list += name
                if i < len(self.names)-1:
                    name_list += ', '
                i += 1
            self.chat.InfoPost('Currently chacking for ' + name_list)
        elif args[0] == 'add':
            if name not in self.names and name != '':
                self.names.append(name)
                self.plugindb.SetList('xxnamesound', 'names', self.names)
                self.chat.InfoPost('The name ' + name + ' has been added to your nickname list. You will now hear a sound when someone says it in chat.')
            else:
                self.chat.InfoPost('The name ' + name + ' is already in your nickname list.')
        elif args[0] == 'del':
            if name in self.names:
                self.names.remove(name)
                self.plugindb.SetList('xxnamesound', 'names', self.names)
                self.chat.InfoPost('The name ' + name + ' has been removed from your nickname list.')
            else:
                self.chat.InfoPost('The name ' + name + ' is not in your nickname list.')

        for name in self.names:
            reg.append("(?<![a-zA-Z0-9>/\#\-])" + name + "['s]*(?!\w+|[<])")

        reg = string.join(reg, "|")
        self.nameReg = re.compile(reg, re.I)

    def plugin_incoming_msg(self, text, type, name, player):
        if self.antispam > 0:
            return text, type, name

        if self.nameReg.search(self.chat.html_strip(text.lower())) != None:
            self.soundplayer.play(self.soundfile)
            self.antispam = 1
        elif self.notify and type == 2:
            self.soundplayer.play(self.soundfile)
            self.antispam = 1


        return text, type, name

    def refresh_counter(self):
        #This is called once per second. That's all you need to know.
        if self.antispam:
            self.antispam -= 0.04
