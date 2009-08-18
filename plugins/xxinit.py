import os
import orpg.pluginhandler
from string import find, replace
from orpg.dirpath import dir_struct

class Plugin(orpg.pluginhandler.PluginHandler):
    # Initialization subroutine.
    #
    # !self : instance of self
    # !chat : instance of the chat window to write to
    def __init__(self, plugindb, parent):
        orpg.pluginhandler.PluginHandler.__init__(self, plugindb, parent)

        # The Following code should be edited to contain the proper information
        self.name = 'Initiative Tool'
        self.author = 'Woody, Darloth, updated by mDuo13'
        self.help = "This is the ever-popular init tool. To learn how to use it, type\n"
        self.help += "'/init help'. It will load the a help node into your game tree."

        self.toggle = ''
        self.init_list = ''
        self.backup_list = ''
        self.tool_type = ''
        self.wod_counter = ''

    def plugin_enabled(self):
        #This is where you set any variables that need to be initalized when your plugin starts

        self.plugin_addcommand('/init', self.on_init, '[help|type|clear|new|start|add|del|list|sortlow|sorthigh|run|go|change] - Init tool. Use /init help to get details about how to use the tool')


        self.toggle = 1
        self.init_list = []
        self.backup_list = []
        self.tool_type = 'std'
        self.wod_counter = 0

    def plugin_disabled(self):
        #Here you need to remove any commands you added, and anything else you want to happen when you disable the plugin
        #such as closing windows created by the plugin
        self.plugin_removecmd('/init')

    def on_init(self, cmdargs):
        #this is just an example function for a command you create create your own
        args = cmdargs.split(None,-1)

        if len(args) == 0:
            if self.toggle:
                self.toggle = 0
                self.post_my_msg("<font color='#ff0000'>Init recording off</font>")
            else:
                self.post_my_msg("<font color='#ff0000'>Init recording on</font>")
                self.toggle = 1
        elif args[0] == 'help':
            f = open(dir_struct["plugins"]+ "inittool.xml","r")
            self.gametree.insert_xml(f.read())
            f.close()
        elif args[0] == 'type':
            if len(args) == 2:
                if args[1] == 'std' or args[1] == 'wod' or args[1] == '3e' or args[1] == 'srun':
                    self.tool_type = args[1]
                    self.post_my_msg("<font color='#ff0000'>Initiative tool now set to '" + self.tool_type + "'</font>")
                else:
                    self.post_my_msg("<font color='#ff0000'>Unknown Initiative tool type: " + args[1])
            else:
                self.chat.Post("<font color='#ff0000'>currently using the '" + self.tool_type + "' Initiative tool type</font>")
        elif args[0] == 'clear' or args[0] == 'new' or args[0] == 'start':
            self.init_list = []
            self.backup_list = []
            self.post_my_msg("<hr><font color='#ff0000'>New Initiative</font><br /><font color='#0000ff'>Roll new Initiatives</font>",1)
        elif args[0] == 'add':
            try:
                new_init = int(args[1])
                self.init_list += [[new_init, args[2]]]
                self.backup_list += [[new_init, arge[2]]]
                self.list_inits()
            except:
                self.post_my_msg("<font color='#ff0000'>Invalid format.  correct command is: /add init_number description</font>")
        elif args[0] == 'del':
            try:
                del self.init_list[int(args[1])-1]
                del self.backup_list[int(args[1])-1]
                self.list_inits()
            except:
                self.post_my_msg("<font color='#ff0000'>Invalid format.  correct command is: /del list_number</font>")
        elif args[0] == 'list':
            self.list_inits()
        elif args[0] == 'backuplist':
            self.list_backups()
        elif args[0] == 'sortlow':
            self.init_list.sort()
            self.backup_list.sort()
            self.list_inits()
        elif args[0] == 'sorthigh':
            self.init_list.sort()
            self.init_list.reverse()
            self.backup_list.sort()
            self.backup_list.reverse()
            self.list_inits()
        elif args[0] == 'run' or args[0] == 'go':
            if len(self.init_list):
                id = str(self.init_list[0][0])
                player = str(self.init_list[0][1])
                del self.init_list[0]
                self.post_my_msg("<hr><font color='#ff0000'>Next init:</font><br /><font color='#0000ff'><b>("+id+")</b>: "+player+"</font>",1)
            else:
                if self.tool_type == 'std' or (self.tool_type == 'wod' and self.wod_counter == 1):
                    self.backup_list = []
                    self.init_list = []
                    self.wod_counter = 0
                    self.post_my_msg("<hr><font color='#ff0000'>End of Initiative Round</font>",1)
                elif self.tool_type == '3e':
                    self.init_list += self. backup_list
                    self.post_my_msg("<hr><font color='#ff0000'>End of Initiative Round, Starting New Initiative Round</font>",1)
                elif self.tool_type == 'wod' and self.wod_counter == 0 and len(self.backup_list) > 0:
                    self.post_my_msg("<hr><font color='#ff0000'>Starting physical initiatives:</font>",1)
                    self.wod_counter = 1
                    self.init_list = self.backup_list
                    self.init_list.sort()
                    self.init_list.reverse()
                elif self.tool_type == 'srun':
                    for m in self.backup_list[:]:
                        m[0] -= 10
                        if m[0] <= 10:
                            self.backup_list.remove(m)
                    if len(self.backup_list):
                        self.post_my_msg("<hr><font color='#ff0000'>End of Initiative Pass, starting next Pass</font>",1)
                        self.init_list += self.backup_list
                    else:
                        self.post_my_msg("<hr><font color='#ff0000'>End of Combat Turn, roll new initiatives please</font>",1)
                        self.init_list = []
                        self.backup_list = []
        elif args[0] == 'change':
            try:
                id = int(args[1])
                new_init = int(args[2])
                self.init_list[id][0] = new_init
                self.backup_list[id][0] = new_init
                self.list_inits()
            except:
                self.post_my_msg("<font color='#0000ff'>Invalid format.  correct command is: /change list_# new_init_# (example: /change 1 4)</font>")
        else:
            self.post_my_msg("<font color='#0000ff'>Invalid Command, type /init help and read the manual please</font>")

    def post_msg(self, text, myself):
        if self.toggle:
            if myself == 1:
                if text.lower().find("init") != -1:
                    player = text[:text.find("[")]
                    init = text[text.rfind("(")+1:text.rfind(")")]
            else:
                if text.lower().find("init") != -1:
                    player=text[text.find("</B>")+4:text.find("[")]
                    init=text[text.rfind("(")+1:text.rfind(")")]
            try:
                if text.lower().find("init") != -1:
                    init = int(init)
                    self.init_list += [[init,player]]
                    self.backup_list += [[init,player]]
            except:
                pass
        return text


    def post_my_msg(self, msg, send=0):
        tmp = self.toggle
        self.toggle = 0
        self.chat.Post(msg,send)
        self.toggle = tmp


    def list_inits(self):
        msg = 'Initiatives:<br />'
        for m in self.init_list:
            msg += " <font color='#ff0000'>" + str(self.init_list.index(m) + 1) + "</font>"
            msg += ": <font color='#0000ff'>(" + str(m[0]) + ") "
            msg += m[1] + "</font><br />"
        self.post_my_msg(msg)


    def list_backups(self):
        msg = 'backup list:<br />'
        for m in self.backup_list:
            msg += " <font color='#ff0000'>" + str(self.backup_list.index(m) + 1) + "</font>"
            msg += ": <font color='#0000ff'>(" + str(m[0]) + ") "
            msg += m[1] + "</font><br />"
        self.post_my_msg(msg)
