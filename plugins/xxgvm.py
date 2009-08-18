import os
import orpg.pluginhandler
import string

class Plugin(orpg.pluginhandler.PluginHandler):
    # Initialization subroutine.
    #
    # !self : instance of self
    # !openrpg : instance of the the base openrpg control
    def __init__(self, plugindb, parent):
        orpg.pluginhandler.PluginHandler.__init__(self, plugindb, parent)

        # The Following code should be edited to contain the proper information
        self.name = 'Game Variable Manager'
        self.author = 'mDuo13'
        self.help = 'This plugin is used to manage variables in your idle status. That way,\n'
        self.help += 'you can keep as many numbers as you want in your idle status, and you can update \n'
        self.help += 'them without having to go to the Settings menu.\n'
        self.help += '\n'
        self.help += 'First you must create some variables. You can do that by typing \n'
        self.help += '"/gvm set *var*=*value*" where *var* is the variables name (no $ symbol), and\n'
        self.help += '*value* is the variables starting value. The variables name can be any word,\n'
        self.help += 'but dont put spaces between the variables name and value.\n'
        self.help += '\n'
        self.help += 'You can look up the value of a variable by typing "/gvm get *var*"\n'
        self.help += '\n'
        self.help += 'To set your status, type "/gvm status *message*" where *message* is the message \n'
        self.help += 'you want your status to have. To include variables, simply the variables name, \n'
        self.help += 'STARTING WITH A $ SYMBOL. For example, you could create a status with \n'
        self.help += '"/gvm status HP:$hp MP:$mp AC:$ac" which, if $hp was 20, $mp was 10, and $ac\n'
        self.help += 'was 5, would make your status "HP:20 MP:10 AC:5".\n'
        self.help += '\n'
        self.help += 'If you later change the values of any of the variables in your status, they will \n'
        self.help += 'be automatically updated; to update a value, just type\n'
        self.help += '"/gvm set *var*=*variable*" the same way you used it to create the variable.\n'
        self.help += '\n'
        self.help += 'You can list the current variables with the "/gvm list" command. You can also\n'
        self.help += 'now roll dice with curly brackets, and have filters apply to them, like this:\n'
        self.help += '"{4d6.takeHighest(3)+$bonus}". Any other filters you have (i.e. the Alias \n'
        self.help += 'Library) will also apply to curly bracket rolls automatically.\n'
        self.help += '\n'
        self.help += 'Note that the GVM plugin conflicts with the NowPlaying and GSC plugins, so if\n'
        self.help += 'you have both plugin enabled at the same time, they may not work quite right.\n'
        self.help += '\n'
        self.help += 'You can now save a group of variables with "/gvm save *name*". You can also load\n'
        self.help += 'a group of previously saved variables with "/gvm open *name*"\n'

        #You can set variables below here. Always set them to a blank value in this section. Use plugin_enabled
        #to set their proper values.
        self.vars = {}
        self.status_scrip=""
        self.status_on=0


    def plugin_enabled(self):
        #You can add new /commands like
        # self.plugin_addcommand(cmd, function, helptext)
        self.plugin_addcommand('/gvm', self.on_gvm, '[set name=value | calc name=value | get name | status | list | save set_name |  open set_name] - This plugin is used to manage variables that you can use in your status bar or in dice rolls')
        self.plugin_addcommand('/gvmq', self.on_gvmq, '[set name=value | calc name=value | get name | status | list | save set_name |  open set_name] - This plugin is used to manage variables that you can use in your status bar or in dice rolls', False)
        self.plugin_addcommand('/=', self.on_comment, '', False)

    def plugin_disabled(self):
        #Here you need to remove any commands you added, and anything else you want to happen when you disable the plugin
        #such as closing windows created by the plugin
        self.plugin_removecmd('/gvm')
        self.plugin_removecmd('/gvmq')
        self.plugin_removecmd('/=')

    def on_comment(self, cmdargs):
        pass

    def on_gvm(self, cmdargs):
        for key in self.vars.keys():
            cmdargs = cmdargs.replace("$" + key, self.vars[key])

        args = cmdargs.split(None,-1)
        if len(args) == 0:
            args = [' ']
        if args[0]=="set":
            cmd = cmdargs[len(args[0])+1:].strip().split("=")
            self.vars[cmd[0]] = cmd[1]
            self.chat.InfoPost("GVM: Set variable $" + cmd[0] + " to be: " + cmd[1])
            if self.status_on:
                self.gvm_status(self.status_scrip)

        elif args[0]=="calc":
            cmd = cmdargs[len(args[0])+1:].strip().split("=")
            val = str(eval(cmd[1]))
            self.vars[cmd[0]] = val
            self.chat.InfoPost("GVM: Set variable $" + cmd[0] + " to be: " + val)
            if self.status_on:
                self.gvm_status(self.status_scrip)

        elif args[0]=="get":
            if args[1] in self.vars.keys():
                self.chat.InfoPost("GVM: Variable $" + args[1] + " is: " + self.vars[args[1]])
            else:
                self.chat.InfoPost("GVM: Variable $" + args[1] + " does not exist!")

        elif args[0]=="status":
            self.status_scrip = cmdargs[len(args[0])+1:]
            status_on = 1
            self.gvm_status(self.status_scrip)

        elif args[0]=="save":
            fname = cmdargs[len(args[0])+1:]
            self.plugindb.SetDict("xxgvm", fname, self.vars)
            self.chat.InfoPost("GVM: Successfully saved variable set " + fname + "!")

        elif args[0]=="open":
            fname = cmdargs[len(args[0])+1:]
            self.vars = self.plugindb.GetDict("xxgvm", fname, {})
            self.chat.InfoPost("GVM: Loaded the file " + fname + ". Variables contained are:<br />" + self.make_list())

        elif args[0] == "list":
            self.chat.Post(self.make_list())

        else:
            self.chat.InfoPost("GVM: SYNTAX ERROR. <br />USEAGE: /gvm [set name=value | get name | status | list | save set_name |  open set_name]")

    def on_gvmq(self, cmdargs):
        for key in self.vars.keys():
            cmdargs = cmdargs.replace("$" + key, self.vars[key])
        args = cmdargs.split(None,-1)
        if len(args) == 0:
            args = [' ']
        if args[0]=="set":
            cmd = cmdargs[len(args[0])+1:].strip().split("=")
            self.vars[cmd[0]] = cmd[1]
            if self.status_on:
                self.gvm_status(self.status_scrip)

        elif args[0]=="calc":
            cmd = cmdargs[len(args[0])+1:].strip().split("=")
            self.vars[cmd[0]] = str(eval(cmd[1]))
            if self.status_on:
                self.gvm_status(self.status_scrip)

        elif args[0]=="get":
            if args[1] in self.vars.keys():
                self.chat.InfoPost("GVM: Variable $" + args[1] + " is: " + self.vars[args[1]])
            else:
                self.chat.InfoPost("GVM: Variable $" + args[1] + " does not exist!")

        elif args[0]=="status":
            self.status_scrip = cmdargs[len(args[0])+1:]
            status_on = 1
            self.gvm_status(self.status_scrip)

        elif args[0]=="save":
            fname = cmdargs[len(args[0])+1:]
            self.plugindb.SetDict("xxgvm", fname, self.vars)

        elif args[0]=="open":
            fname = cmdargs[len(args[0])+1:]
            self.vars = self.plugindb.GetDict("xxgvm", fname, {})

        elif args[0] == "list":
            self.chat.Post(self.make_list())

        else:
            self.chat.InfoPost("GVM: SYNTAX ERROR. <br />USEAGE: /gvmq [set name=value | get name | status | list | save set_name |  open set_name]")


    def pre_parse(self, text):
        try:
            for key in self.vars.keys():
                text = text.replace("$" + key, self.vars[key])
        except Exception, e:
            print e
            print key
            self.vars[key]

        return text

    def gvm_status(self, cmd):
        keychain = self.vars.keys()
        keychain.sort()
        newchain = []
        for key in keychain:
            newchain = [key] + newchain
        for key in keychain:
            cmd = cmd.replace("$" + key, self.vars[key])
        self.settings.set_setting("IdleStatusAlias", cmd)
        self.session.set_text_status(cmd)

    def make_list(self):
        keychain = self.vars.keys()
        lister = ""
        for key in keychain:
            lister += "$" + key + "\t::\t" + self.vars[key] + "<br />"
        if len(keychain)==0:
            return "No variables!"
        else:
            return lister
