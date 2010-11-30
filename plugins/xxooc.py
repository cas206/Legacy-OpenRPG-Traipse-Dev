from orpg.tools.InterParse import Parse
import orpg.pluginhandler

class Plugin(orpg.pluginhandler.PluginHandler):
    # Initialization subroutine.
    #
    # !self : instance of self
    # !chat : instance of the chat window to write to
    def __init__(self, plugindb, parent):
        orpg.pluginhandler.PluginHandler.__init__(self, plugindb, parent)
        # The Following code should be edited to contain the proper information
        self.name = 'OOC Comments Tool'
        self.author = 'mDuo13'
        self.help = "Type '/ooc *message*' to send '(( *message* ))' -- it just preformats\n"
        self.help += "out of character comments for you."

    def plugin_enabled(self):
        #This is where you set any variables that need to be initalized when your plugin starts
        self.plugin_addcommand('/ooc', self.on_ooc, 'message - This puts (( message )) to let other players know you are talking out of character')


    def plugin_disabled(self):
        #Here you need to remove any commands you added, and anything else you want to happen when you disable the plugin
        #such as closing windows created by the plugin
        self.plugin_removecmd('/ooc')

    def on_ooc(self, cmdargs):
        #this is just an example function for a command you create create your own
        Parse.Post('(( ' + cmdargs + ' ))', False, True, True)
