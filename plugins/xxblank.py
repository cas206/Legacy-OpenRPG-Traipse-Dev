import os, wx
import orpg.pluginhandler

class Plugin(orpg.pluginhandler.PluginHandler):
    # Initialization subroutine.
    #
    # !self : instance of self
    # !openrpg : instance of the the base openrpg control
    def __init__(self, plugindb, parent):
        orpg.pluginhandler.PluginHandler.__init__(self, plugindb, parent)

        # The Following code should be edited to contain the proper information
        self.name = 'Example Plugin'
        self.author = 'Your Name'
        self.help = 'Info About your plugin'

        #You can set variables below here. Always set them to a blank value in this section. Use plugin_enabled
        #to set their proper values.
        self.sample_variable = {}

    def plugin_menu(self):
        ## This is a standardized Menu item.  It connects to plugin_toggle where you can set events.
        self.menu = wx.Menu()
        self.toggle = self.menu.AppendCheckItem(wx.ID_ANY, 'On')
        self.topframe.Bind(wx.EVT_MENU, self.plugin_toggle, self.toggle)
        self.toggle.Check(True)

    def plugin_toggle(self, evt):
        pass


    def plugin_enabled(self):
        #You can add new /commands like
        # self.plugin_addcommand(cmd, function, helptext)
        self.plugin_addcommand('/test', self.on_test, '- This is an example plugin command')

        #If you want your plugin to have more then one way to call the same function you can
        #use self.plugin_commandalias(alias name, command name)
        #You can also make shortcut commands like the following
        self.plugin_commandalias('/example', '/me is giving you an example')

        #if you want your plugin to use custom messages to comunicate with other people using the same plugin
        #you can add a message handler in a simmilar way to adding a new slash command. The first variable
        #'xxblank' in this case is the tage name for your custom xml message. The second variable is the function
        #you want to handle proccessing your messages when one is recived.
        #Be sure to delete your handler in plugin_disabled
        self.plugin_add_msg_handler('xxblank', self.on_xml_recive)

        #if you want your plugin to store some settings in the settings window
        #you can add them here, the system checks to make sure it does not already exist so you dont
        #have to worry about it adding copies every time the plugin loads or it overwriting the users changes to it.
        #This should be used for simple short settings that you would like the user to be able to change in the settings window
        #variables:
        #setting - The setting name, cannot contain spaces
        #value - The default value
        #options - The type of value that is expected
        #help - a help message to explain what this variable does.
        self.plugin_add_setting('Setting', 'Value', 'Options', 'Help message')

        #This is where you set any variables that need to be initalized when your plugin starts
        self.sample_variable = {1:'one', 2:'two'}

    def plugin_disabled(self):
        #Here you need to remove any commands you added, and anything else you want to happen when you disable the plugin
        #such as closing windows created by the plugin
        self.plugin_removecmd('/test')
        self.plugin_removecmd('/example')

        #This is the command to delete a message handler
        self.plugin_delete_msg_handler('xxblank')

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
