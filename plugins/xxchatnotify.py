import os
import orpg.pluginhandler
import wx
from orpg.orpgCore import *

class Plugin(orpg.pluginhandler.PluginHandler): #Attempting to pass the orpgFrame so that we can Bind events, not working.
    def __init__(self, plugindb, parent):
        orpg.pluginhandler.PluginHandler.__init__(self, plugindb, parent)

        # The Following code should be edited to contain the proper information
        self.name = 'Chat Notification'
        self.author = 'Dj Gilcrease'
        self.help = 'This plugin with either play a sound when a new chat message comes in, flash the taskbar or both'

    def plugin_menu(self):
	#Plugin Menu
        self.menu = wx.Menu()
        self.notifyToggle = self.menu.AppendCheckItem(wx.ID_ANY, 'On')
        self.topframe.Bind(wx.EVT_MENU, self.on_settings, self.notifyToggle)

        notify = wx.Menu()
        self.notifyBeep = notify.AppendRadioItem(wx.ID_ANY, 'Beep')
        self.notifyFlash = notify.AppendRadioItem(wx.ID_ANY, 'Flash')
        self.notifyBoth = notify.AppendRadioItem(wx.ID_ANY, 'Both')
        self.menu.AppendMenu(wx.ID_ANY, 'Notify', notify)
        self.topframe.Bind(wx.EVT_MENU, self.on_settings, self.notifyBeep)
        self.topframe.Bind(wx.EVT_MENU, self.on_settings, self.notifyFlash)
        self.topframe.Bind(wx.EVT_MENU, self.on_settings, self.notifyBoth)

        notifyType = wx.Menu()
        self.notifyAll = notifyType.AppendRadioItem(wx.ID_ANY, 'All')
        self.notifyWhisper = notifyType.AppendRadioItem(wx.ID_ANY, 'Whisper')
        self.menu.AppendMenu(wx.ID_ANY, 'Type', notifyType)
        self.topframe.Bind(wx.EVT_MENU, self.on_settings, self.notifyAll)
        self.topframe.Bind(wx.EVT_MENU, self.on_settings, self.notifyWhisper)

    def on_settings(self, evt):
        if self.notifyToggle.IsChecked() == False:
            self.notify = 'Off'
            self.plugindb.SetString('xxchatnotify', 'notify', self.notify)
            return
        if self.notifyBeep.IsChecked() == True:
            self.notify ='beep'
        elif self.notifyFlash.IsChecked() == True:
            self.notify = 'flash'
        elif self.notifyBoth.IsChecked() == True:
            self.notify = 'both'
        if self.notifyAll.IsChecked() == True:
            self.type = 'all'
        elif self.notifyWhisper.IsChecked() == True:
            self.type = 'whisper'
        self.plugindb.SetString('xxchatnotify', 'notify', self.notify)
        self.plugindb.SetString('xxchatnotify', 'type', self.type)


    def plugin_enabled(self):
        self.plugin_addcommand('/notify', self.on_notify, 'beep | flash | both | off | type all|whisper | clearsound | lsound soundfile [Local Sound Files only] | rsound http://to.sound.file [Remote Sound Files only] - This command turns on the chat notification. You can use sound files and flash by issuing /notify both')
        self.notify = self.plugindb.GetString('xxchatnotify', 'notify', string) or 'off'
        self.type = self.plugindb.GetString('xxchatnotify', 'type', string) or 'beep'
        self.mainframe = component.get('frame')
        self.sound_player = component.get('sound')
        self.soundloc = self.plugindb.GetString('xxchatnotify', 'soundloc', 'local')
        self.soundfile = self.plugindb.GetString('xxchatnotify', 'soundfile', 'None')
        self.chat_settings()

    def chat_settings(self):
        self.notifyToggle.Check(True)
        if self.notify == 'beep':
            self.notifyBeep.Check(True)
        elif self.notify == 'flash':
            self.notifyFlash.Check(True)
        elif self.notify == 'both':
            self.notifyBoth.Check(True)
        else:
            self.notifyToggle.Check(False)
        if self.type == 'all':
            self.notifyAll.Check(True)
        elif self.type == 'whisper':
            self.notifyWhisper.Check(True)

    def plugin_disabled(self):
        self.plugin_removecmd('/notify')

    def on_notify(self, cmdargs):
        args = cmdargs.split(None, 2)

        if len(args) == 0:
            self.chat.InfoPost('You must specify if you want it to beep, flash, both or be turned off or specify if you want to be notified for all messages or just whispers')

        if args[0] == 'type':
            self.type = args[1]
            self.plugindb.SetString('xxchatnotify', 'type', self.type)
            self.chat.InfoPost('Setting Notification on Message type to ' + args[1])
            self.chat_settings()
            return
        elif args[0] == 'lsound':
            self.soundloc = 'local'
            self.soundfile = orpg.dirpath.dir_struct['plugins'] + args[1]
            self.plugindb.SetString('xxchatnotify', 'soundfile', self.soundfile)
            self.plugindb.GetString('xxchatnotify', 'soundloc', self.soundloc)
            self.chat.InfoPost('Setting Sound file to ' + self.soundfile)
            self.notify = 'beep'
            return
        elif args[0] == 'rsound':
            self.soundloc = 'remote'
            self.soundfile = args[1]
            self.plugindb.SetString('xxchatnotify', 'soundfile', self.soundfile)
            self.plugindb.GetString('xxchatnotify', 'soundloc', self.soundloc)
            self.chat.InfoPost('Setting Sound file to ' + self.soundfile)
            self.notify = 'beep'
            return
        elif args[0] == 'clearsound':
            self.soundloc = 'local'
            self.soundfile = 'None'
            self.plugindb.SetString('xxchatnotify', 'soundfile', self.soundfile)
            self.plugindb.GetString('xxchatnotify', 'soundloc', self.soundloc)
            self.chat.InfoPost('Clearing Sound file')
            self.notify = 'off'
            return


        self.notify = args[0]
        self.plugindb.SetString('xxchatnotify', 'notify', self.notify)
        self.chat.InfoPost('Setting Notification type to ' + args[0])
        self.chat_settings()


    def plugin_incoming_msg(self, text, type, name, player):
        if (self.notify == 'beep' or self.notify == 'both') and (self.type == 'all' or type == 2):
            if self.soundfile == 'None':
                wx.CallAfter(wx.Bell)
                wx.CallAfter(wx.Bell)
            else:
                wx.CallAfter(self.sound_player.play, self.soundfile, self.soundloc)
        if (self.notify == 'flash' or self.notify == 'both') and (self.type == 'all' or type == 2):
            wx.CallAfter(self.mainframe.RequestUserAttention)
        return text, type, name


