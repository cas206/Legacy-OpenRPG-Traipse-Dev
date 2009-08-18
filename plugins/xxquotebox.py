import os
from orpg.dirpath import dir_struct
import orpg.plugindb
import orpg.pluginhandler
from orpg.tools.rgbhex import RGBHex
import wx

__version__ = "2.0" # updated for OpenRPG+ 1.7.0

class Plugin(orpg.pluginhandler.PluginHandler):
    # Initialization subroutine.
    #
    # !self : instance of self
    # !openrpg : instance of the the base openrpg control
    def __init__(self, plugindb, parent):
        orpg.pluginhandler.PluginHandler.__init__(self, plugindb, parent)

        # The Following code should be edited to contain the proper information
        self.name = "Quote Box"
        self.author = "frobnic8 (erskin@eldritch.org), mDuo13, Veggiesama"
        self.help = """This plugin allows you to put your text in a special box. Again, while
            it could (except for the color selection) be easily done with a text node,
            this plugin makes it faster, presents a consistant appearance, and saves
            you from silly HTML errors. Just type "/box" and some text to get started.

            Type /quotebox to load a help node into your game tree.

            Advanced commands:
            '/box': Displays the current settings.
            '/box *text*': Displays *text* in the box.
            '/box_size *size*': Lets you set the size of the text
            \tin the box, where *size* is a number from 1 to 7. The default is 3.
            '/box_bgcol': Brings up a color selection dialog for picking the background
            \tcolor of the box. The default is pale grey.
            '/box_fontcol': Brings up a color selection dialog for picking the color of
            \tthe font in the box. The default is black.
            '/box_border': Toggles a small black border around the box.
            '/box_italics': Toggles whether the text in the box should be italicized or not.
            '/box_bold': Toggles whether the text in the box should be bolded or not.
            '/box_type': Toggles between the old and new versions of the box. Defaults to new.
            '/box_default': Sets plugin to default settings.

            Credits go out to Travis for the original HTML code and Sunless DM for
            bringing it to mDuo13's attention."""

        self.version = __version__
        self.orpg_min_version="1.7.0"

        self.fontcolor = "#000000"
        self.bgcolor="#aaaaaa"
        self.size = 3
        self.border = 0
        self.italics = 0
        self.bold = 1
        self.boxtype = 1
        self.r_h = RGBHex()

    def plugin_enabled(self):
        self.fontcolor  = str(self.plugindb.GetString("xxquotebox", "fontcolor", "#000000"))
        self.bgcolor    = str(self.plugindb.GetString("xxquotebox", "bgcolor", "#aaaaaa"))
        self.size       = int(self.plugindb.GetString("xxquotebox", "size", "3"))
        self.border     = int(self.plugindb.GetString("xxquotebox", "border", "0"))
        self.italics    = int(self.plugindb.GetString("xxquotebox", "italics", "0"))
        self.bold       = int(self.plugindb.GetString("xxquotebox", "bold", "1"))
        self.boxtype    = int(self.plugindb.GetString("xxquotebox", "boxtype", "1"))

        self.plugin_addcommand('/box',          self.on_box,        "'/box': Displays the current settings <b>OR</b> '/box *text*': Displays *text* in the box.")
        self.plugin_addcommand('/box_size',     self.on_box_size,   "'/box_size *size*': Lets you set the size of the text in the box, where *size* is a number from 1 to 7. The default is 3.", False)
        self.plugin_addcommand('/box_bgcol',    self.on_box_bgcol,  "'/box_bgcol': Brings up a color selection dialog for picking the background color of the box. The default is pale grey.", False)
        self.plugin_addcommand('/box_fontcol',  self.on_box_fontcol,"'/box_fontcol': Brings up a color selection dialog for picking the color of the font in the box. The default is black.", False)
        self.plugin_addcommand('/box_border',   self.on_box_border, "'/box_border': Toggles a small black border around the box.", False)
        self.plugin_addcommand('/box_italics',  self.on_box_italics,"'/box_italics': Toggles whether the text in the box should be italicized or not.", False)
        self.plugin_addcommand('/box_bold',     self.on_box_bold,   "'/box_bold': Toggles whether the text in the box should be bolded or not.", False)
        self.plugin_addcommand('/box_type',     self.on_box_type,   "'/box_type': Toggles between the old and new versions of the box. Defaults to new.", False)
        self.plugin_addcommand('/box_default',  self.on_box_default,"'/box_default': Sets plugin to default settings.", False)
        self.plugin_addcommand('/quotebox',     self.on_quotebox,   "<b>TYPE /QUOTEBOX TO BEGIN.</b> Loads up a help node into gametree.")

    def plugin_disabled(self):
        self.plugin_removecmd('/box')
        self.plugin_removecmd('/box_size')
        self.plugin_removecmd('/box_bgcol')
        self.plugin_removecmd('/box_fontcol')
        self.plugin_removecmd('/box_border')
        self.plugin_removecmd('/box_italics')
        self.plugin_removecmd('/box_bold')
        self.plugin_removecmd('/box_type')
        self.plugin_removecmd('/box_default')
        self.plugin_removecmd('/box_quotebox')

    def save_changes(self):
        self.plugindb.SetString("xxquotebox", "fontcolor",str(self.fontcolor))
        self.plugindb.SetString("xxquotebox", "bgcolor",  str(self.bgcolor))
        self.plugindb.SetString("xxquotebox", "size",     str(self.size))
        self.plugindb.SetString("xxquotebox", "border",   str(self.border))
        self.plugindb.SetString("xxquotebox", "italics",  str(self.italics))
        self.plugindb.SetString("xxquotebox", "bold",     str(self.bold))
        self.plugindb.SetString("xxquotebox", "boxtype",  str(self.boxtype))

    def on_box(self, cmdargs):
        #this is just an example function for a command you create.
        # cmdargs contains everything you typed after the command
        # so if you typed /test this is a test, cmdargs = this is a test
        # args are the individual arguments split. For the above example
        # args[0] = this , args[1] = is , args[2] = a , args[3] = test
        args = cmdargs.split(None,-1)

        # shows status information of the plugin in a dialog window
        if len(args) == 0:
            if self.boxtype == 0:
                msg_boxtype = "old"
            else:
                msg_boxtype = "new"

            self.dlg = wx.MessageDialog(None,
                 'Current settings used by the Quote Box plugin:\n'+
                 '\nsize: '+str(self.size)+'\nbgcolor: '+self.bgcolor+
                 '\nfontcolor: '+self.fontcolor+'\nborder: '+str(self.border)+
                 '\nitalics: '+str(self.italics)+'\nbold: '+str(self.bold)+
                 '\nboxtype: '+msg_boxtype+'\n'+
                 '\nSee the Plugin Info from the Tools/Plugin menu for '+
                 'more information.', 'Quote Box Current Settings', wx.OK)
            self.dlg.ShowModal()
            self.dlg.Destroy()

        # making a box and using the cmdargs as the text inside
        else:
            msg = cmdargs
            if self.boxtype == 0: #old
                box = '<table bgcolor="' + self.bgcolor + '" border="0" cellpadding="0" cellspacing="0" width="100%">'
                box += '<tr><td><font size="' + str(self.size) + '" color="' + self.fontcolor + '">'
                box += '<b>' + msg + '</b></font></table>'
                self.chat.Post(box, True, True)
            else: #new
                if self.border:
                    border = " border='1'"
                else:
                    border = ""

                if self.italics:
                    italics = "<i>"
                    enditalics = "</i>"
                else:
                    italics = ""
                    enditalics = ""

                if self.bold:
                    bold = "<b>"
                    endbold = "</b>"
                else:
                    bold = ""
                    endbold = ""

                box = '<br><center><table bgcolor="' + self.bgcolor + '" width="80%"'
                box += 'cellpadding="' + str(int(self.size * 5)) + '" cellspacing="0" ' + border + '>'
                box += '<tr><td><font size="' + str(self.size) + '" color="' + self.fontcolor + '">'
                box += bold + italics + msg + enditalics + endbold
                box += '</font></td></tr></table></center>'
                self.chat.Post(box, True, True)

    # changes size of font, as well as cell-padding size
    # cell padding size = font size * 5
    def on_box_size(self, cmdargs):
        try:
            self.size = int(cmdargs)
            self.save_changes()
            self.chat.InfoPost("Box size set to <b>" + str(self.size) + "</b>.")
        except:
            self.chat.InfoPost("That is not a valid font size.")

    # opens a color-choosing dialog for background color of table
    def on_box_bgcol(self, cmdargs):
        color = self.r_h.do_hex_color_dlg(None)
        if color != None:
            self.bgcolor = color
        self.save_changes()

    # opens a color-choosing dialog for font color of text
    def on_box_fontcol(self, cmdargs):
        color = self.r_h.do_hex_color_dlg(None)
        if color != None:
            self.fontcolor = color
        self.save_changes()

    # toggles whether border should be on or off
    def on_box_border(self, cmdargs):
        if self.border:
            self.border=0
            self.chat.InfoPost("No longer using border on table.")
        else:
            self.border=1
            self.chat.InfoPost("Using border on table.")
        self.save_changes()

    # toggles whether text should be italics or not
    def on_box_italics(self, cmdargs):
        if self.italics:
            self.italics=0
            self.chat.InfoPost("No longer using italic text.")
        else:
            self.italics=1
            self.chat.InfoPost("Using italic text.")
        self.save_changes()

    # toggles whether text should be bold or not
    def on_box_bold(self, cmdargs):
        if self.bold:
            self.bold=0
            self.chat.InfoPost("No longer using bold text.")
        else:
            self.bold=1
            self.chat.InfoPost("Using bold text.")
        self.save_changes()

    # toggles between old-style and new-style boxes
    def on_box_type(self, cmdargs):
        if self.boxtype:
            self.boxtype=0
            self.chat.InfoPost("Now using old-style boxes (thin, full-width, left-aligned)")
        else:
            self.boxtype=1
            self.chat.InfoPost("Now using new-style boxes (in middle, with thick borders)")
        self.save_changes()

    # reverts all quotebox settings back to default
    def on_box_default(self, cmdargs):
        self.fontcolor = "#000000"
        self.bgcolor="#aaaaaa"
        self.size = 3
        self.border = 0
        self.italics = 0
        self.bold = 1
        self.boxtype = 1

        self.chat.InfoPost("Quotebox plugin reverted to default settings.")
        self.save_changes()

    # loads up quotebox.xml as a node in the gametree
    def on_quotebox(self, cmdargs):
        f = open(dir_struct["plugins"]+ "quotebox.xml","r")
        self.gametree.insert_xml(f.read())
        f.close()
        return 1

