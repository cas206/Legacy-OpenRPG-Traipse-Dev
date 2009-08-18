import os
import orpg.pluginhandler
from orpg.dirpath import dir_struct

class Plugin(orpg.pluginhandler.PluginHandler):
    # Initialization subroutine.
    #
    # !self : instance of self
    # !chat : instance of the chat window to write to
    def __init__(self, plugindb, parent):
        orpg.pluginhandler.PluginHandler.__init__(self, plugindb, parent)

        # The Following code should be edited to contain the proper information
        self.name = 'Smilies!'
        self.author = 'mDuo13'
        self.help = "This plugin turns text smilies like >=) or :D into images. There are 15\n"
        self.help += "images. Also, you can type '/smiley' to get a list of what emoticons are\n"
        self.help += "converted to what images."

        self.smileylist = {}

    def plugin_enabled(self):
        #This is where you set any variables that need to be initalized when your plugin starts

        self.plugin_addcommand('/smiley', self.on_smiley, '- [add|remove|help] The Smiley command')

        smlist = {
                    '>:-('   :       ' <img src="' + dir_struct['plugins'] + 'images/smiley7.gif" /> ',
                    ':/'     :       ' <img src="' + dir_struct['plugins'] + 'images/smiley5.gif" /> ',
                    ':|'     :       ' <img src="' + dir_struct['plugins'] + 'images/smiley6.gif" /> ',
                    ':('     :       ' <img src="' + dir_struct['plugins'] + 'images/smiley9.gif" /> ',
                    ' />:('  :       ' <img src="' + dir_struct['plugins'] + 'images/smiley7.gif" /> ',
                    ' />=('  :       ' <img src="' + dir_struct['plugins'] + 'images/smiley7.gif" /> ',
                    '=)'     :       ' <img src="' + dir_struct['plugins'] + 'images/smiley0.gif" /> ',
                    '=D'     :       ' <img src="' + dir_struct['plugins'] + 'images/smiley1.gif" /> ',
                    ';)'     :       ' <img src="' + dir_struct['plugins'] + 'images/smiley3.gif" /> ',
                    '=/'     :       ' <img src="' + dir_struct['plugins'] + 'images/smiley5.gif" /> ',
                    '=|'     :       ' <img src="' + dir_struct['plugins'] + 'images/smiley6.gif" /> ',
                    '=('     :       ' <img src="' + dir_struct['plugins'] + 'images/smiley9.gif" /> ',
                    ':)'     :       ' <img src="' + dir_struct['plugins'] + 'images/smiley0.gif" /> ',
                    ':D'     :       ' <img src="' + dir_struct['plugins'] + 'images/smiley1.gif" /> ',
                    'B)'     :       ' <img src="' + dir_struct['plugins'] + 'images/smiley2.gif" /> ',
                    ':p'     :       ' <img src="' + dir_struct['plugins'] + 'images/smiley4.gif" /> ',
                    '=\\'    :       ' <img src="' + dir_struct['plugins'] + 'images/smiley5.gif" /> ',
                    ':P'     :       ' <img src="' + dir_struct['plugins'] + 'images/smiley4.gif" /> ',
                    '=P'     :       ' <img src="' + dir_struct['plugins'] + 'images/smiley4.gif" /> ',
                    '^_^'    :       ' <img src="' + dir_struct['plugins'] + 'images/smiley12.gif" /> ',
                    '^-^'    :       ' <img src="' + dir_struct['plugins'] + 'images/smiley12.gif" /> ',
                    '^.^'    :       ' <img src="' + dir_struct['plugins'] + 'images/smiley12.gif" /> ',
                    'n_n'    :       ' <img src="' + dir_struct['plugins'] + 'images/smiley12.gif" /> ',
                    'n.n'    :       ' <img src="' + dir_struct['plugins'] + 'images/smiley12.gif" /> ',
                    'n,n'    :       ' <img src="' + dir_struct['plugins'] + 'images/smiley12.gif" /> ',
                    'I-)'    :       ' <img src="' + dir_struct['plugins'] + 'images/smiley13.gif" /> ',
                    'n.n;'   :       ' <img src="' + dir_struct['plugins'] + 'images/smiley14.gif" /> ',
                    'n.n;;'  :       ' <img src="' + dir_struct['plugins'] + 'images/smiley14.gif" /> ',
                    'n_n;'   :       ' <img src="' + dir_struct['plugins'] + 'images/smiley14.gif" /> ',
                    ':-)'    :       ' <img src="' + dir_struct['plugins'] + 'images/smiley0.gif" /> ',
                    ':-D'    :       ' <img src="' + dir_struct['plugins'] + 'images/smiley1.gif" /> ',
                    ':-P'    :       ' <img src="' + dir_struct['plugins'] + 'images/smiley2.gif" /> ',
                    ':-p'    :       ' <img src="' + dir_struct['plugins'] + 'images/smiley4.gif" /> ',
                    ':-/'    :       ' <img src="' + dir_struct['plugins'] + 'images/smiley5.gif" /> ',
                    ':-|'    :       ' <img src="' + dir_struct['plugins'] + 'images/smiley6.gif" /> ',
                    ':-('    :       ' <img src="' + dir_struct['plugins'] + 'images/smiley9.gif" /> ',
                    ':-\\'   :       ' <img src="' + dir_struct['plugins'] + 'images/smiley5.gif" /> ',
                    '-)'          :       ' <img src="' + dir_struct['plugins'] + 'images/icon_smile.gif" /> ',
                    ';-)'         :       ' <img src="' + dir_struct['plugins'] + 'images/icon_wink.gif" /> ',
                    ':->'         :       ' <img src="' + dir_struct['plugins'] + 'images/icon_smile2.gif" /> ',
                    ':-D'         :       ' <img src="' + dir_struct['plugins'] + 'images/icon_biggrin.gif" /> ',
                    ':-P'         :       ' <img src="' + dir_struct['plugins'] + 'images/icon_razz.gif" /> ',
                    ':-o'         :       ' <img src="' + dir_struct['plugins'] + 'images/icon_surprised.gif" /> ',
                    ':mrgreen:'   :       ' <img src="' + dir_struct['plugins'] + 'images/icon_mrgreen.gif" /> ',
                    ':lol:'       :       ' <img src="' + dir_struct['plugins'] + 'images/icon_lol.gif" /> ',
                    ':-('         :       ' <img src="' + dir_struct['plugins'] + 'images/icon_sad.gif" /> ',
                    ':-|'         :       ' <img src="' + dir_struct['plugins'] + 'images/icon_neutral.gif" /> ',
                    ':-?'         :       ' <img src="' + dir_struct['plugins'] + 'images/icon_confused.gif" /> ',
                    ':-x'         :       ' <img src="' + dir_struct['plugins'] + 'images/icon_mad.gif" /> ',
                    ':shock:'     :       ' <img src="' + dir_struct['plugins'] + 'images/icon_eek.gif" /> ',
                    ':cry:'       :       ' <img src="' + dir_struct['plugins'] + 'images/icon_cry.gif" /> ',
                    ';_;'         :       ' <img src="' + dir_struct['plugins'] + 'images/icon_cry.gif" /> ',
                    ':oops:'      :       ' <img src="' + dir_struct['plugins'] + 'images/icon_redface.gif" /> ',
                    '8-)'         :       ' <img src="' + dir_struct['plugins'] + 'images/icon_cool.gif" /> ',
                    ':evil:'      :       ' <img src="' + dir_struct['plugins'] + 'images/icon_evil.gif" /> ',
                    ':twisted:'      :       ' <img src="' + dir_struct['plugins'] + 'images/icon_twisted.gif" /> ',
                    ':roll:'      :       ' <img src="' + dir_struct['plugins'] + 'images/icon_rolleyes.gif" /> ',
                    ':!:'         :       ' <img src="' + dir_struct['plugins'] + 'images/icon_exclaim.gif" /> ',
                    ':?:'         :       ' <img src="' + dir_struct['plugins'] + 'images/icon_question.gif" /> ',
                    ':idea:'      :       ' <img src="' + dir_struct['plugins'] + 'images/icon_idea.gif" /> ',
                    ':arrow:'     :       ' <img src="' + dir_struct['plugins'] + 'images/icon_arrow.gif" /> ',
                    ':ubergeek:'  :       ' <img src="' + dir_struct['plugins'] + 'images/icon_e_ugeek.gif" /> ',
                    ':geek:'      :       ' <img src="' + dir_struct['plugins'] + 'images/icon_e_geek.gif" /> ',
                    ':fairy:'    :       ' <img src="' + dir_struct['plugins'] + 'images/fairy.gif" /> ',
                    ':hood:'    :       ' <img src="' + dir_struct['plugins'] + 'images/hood.gif" /> ',
                    ':gnome:'    :       ' <img src="' + dir_struct['plugins'] + 'images/gnome.gif" /> ',
                    ':link:'    :       ' <img src="' + dir_struct['plugins'] + 'images/link.gif" /> ',
                    ':mummy:'    :       ' <img src="' + dir_struct['plugins'] + 'images/mummy.gif" /> ',
                    ':ogre:'    :       ' <img src="' + dir_struct['plugins'] + 'images/ogre.gif" /> ',
                    ':medusa:'    :       ' <img src="' + dir_struct['plugins'] + 'images/medusa.gif" /> ',
                    ':mimic:'    :       ' <img src="' + dir_struct['plugins'] + 'images/mimic.gif" /> ',
                    ':skull:'    :       ' <img src="' + dir_struct['plugins'] + 'images/skull.gif" /> ',
                    ':zombie:'    :       ' <img src="' + dir_struct['plugins'] + 'images/zombie.gif" /> ',
                    ':chocobo:'    :       ' <img src="' + dir_struct['plugins'] + 'images/chocobo.gif" /> ',
                    ':darkside:'    :       ' <img src="' + dir_struct['plugins'] + 'images/darkside.gif" /> ',
                    ':flyingspaghetti:'    :       ' <img src="' + dir_struct['plugins'] + 'images/flyingspaghetti.gif" /> ',
                    ':rupee:'    :       ' <img src="' + dir_struct['plugins'] + 'images/rupee.gif" /> ',
                    ':ros:'    :       ' <img src="' + dir_struct['plugins'] + 'images/ros.gif" /> ',
                    ':skeleton:'    :       ' <img src="' + dir_struct['plugins'] + 'images/skeleton.gif" /> ',
                    ':samurai:'    :       ' <img src="' + dir_struct['plugins'] + 'images/samurai.gif" /> '}

        self.smileylist = self.plugindb.GetDict("xxsmiley", "smileylist", smlist)

    def plugin_disabled(self):
        #Here you need to remove any commands you added, and anything else you want to happen when you disable the plugin
        #such as closing windows created by the plugin

        self.plugin_removecmd('/smiley')
        self.plugindb.SetDict("xxsmiley", "smileylist", self.smileylist)

    def on_smiley(self, cmdargs):
        #this is just an example function for a command you create create your own
        if not len(cmdargs):
            self.chat.InfoPost("Available Smilies:")
            the_list = ' <table border="1">'
            for key in self.smileylist.keys():
                the_list += ' <tr><td>' + key + ' </td><td>' + self.smileylist[key] + ' </td></tr>'
            the_list += "</table>"
            self.chat.InfoPost(the_list)
            return

        args = cmdargs.split(None, -1)

        if args[0] == 'add' and len(args) == 3:
            if args[2].find('http') > -1:
                self.smileylist[args[1]] = ' <img src="' + args[2] + '" alt="' + args[1] + '" />'
            else:
                self.smileylist[args[1]] = ' <img src="' + dir_struct["plugins"] + 'images/' + args[2] + '" />' + "\n"

            self.chat.InfoPost('Added ' + args[1] + '&nbsp&nbsp&nbsp : &nbsp&nbsp&nbsp' + self.smileylist[args[1]])

        elif args[0] == 'remove' and len(args) == 2:
            if self.smileylist.has_key(args[1]):
                del self.smileylist[args[1]]
                self.chat.InfoPost('Removed ' + args[1])
            else:
                self.chat.InfoPost(args[1] + ' was not a smiley!')

        else:
            self.chat.InfoPost('/smiley - Lists all avaliable smilies')
            self.chat.InfoPost('/smiley add {smiley} {imagefile} - Add a smily to the list. The {smiley} can be any string of text that does not contain a space. The {imagefile} should be an image in the openrpg/plugins/images directory')
            self.chat.InfoPost('/smiley remove {smiley} - Remove {smiley} from the list')

        self.plugindb.SetDict("xxsmiley", "smileylist", self.smileylist)

    def doSmiley(self, text):
        for key, value in self.smileylist.iteritems():
            text = text.replace(key, value)

        return text

    def plugin_incoming_msg(self, text, type, name, player):
        text = self.doSmiley(text)

        return text, type, name

    def post_msg(self, text, myself):
        if myself:
            text = self.doSmiley(text)

        return text
