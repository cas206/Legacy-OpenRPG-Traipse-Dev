import os, wx
import random
import orpg.pluginhandler

ID_ROLL = wx.NewId()

class Plugin(orpg.pluginhandler.PluginHandler):
    # Initialization subroutine.
    #
    # !self : instance of self
    # !chat : instance of the chat window to write to
    def __init__(self, plugindb, parent):
        orpg.pluginhandler.PluginHandler.__init__(self, plugindb, parent)

        self.name = 'Game Status Controller'
        self.author = 'Woody, updated by mDuo13 and Calchexas'
        self.help = 'This plugin lets you quickly and easily manage a status that includes \n'
        self.help += 'your HP and AC for AD&D 2nd Edition. Type /gsc to open up the manager\n'
        self.help += 'window, and from there just change the values as necessary and the changes\n'
        self.help += 'will be reflected in your status. To revert to your regular status, close\n'
        self.help += 'the GSC window.'

        self.frame = None

    def plugin_enabled(self):
        self.plugin_addcommand('/gsc', self.on_gsc, '- The GSC command')
        self.frame = RollerFrame(None, -1, "Game Status Controller (GSC)", self)
        self.frame.Hide()

    def plugin_menu(self):
        self.menu = wx.Menu()
        self.toggle = self.menu.AppendCheckItem(wx.ID_ANY, 'GSC Window')
        self.topframe.Bind(wx.EVT_MENU, self._toggleWindow, self.toggle)
        self.toggle.Check(False)

    def plugin_disabled(self):
        self.plugin_removecmd('/gsc')
        try:
            self.frame.TimeToQuit(1)
        except:
            pass

    def on_gsc(self, cmdargs):
        item = self.menu.FindItemById(self.menu.FindItem("GSC Window"))
        item.Check(True)
        self.frame.Show()
        self.frame.Raise()

    #Events
    def _toggleWindow(self, evt):
        if self.frame.IsShown():
            self.frame.Hide()
            self.toggle.Check(False)
        else:
            self.frame.Show()
            self.toggle.Check(True)


class RollerFrame(wx.Frame):
    def __init__(self, parent, ID, title, plugin):
        wx.Frame.__init__(self, parent, ID, title,
                         wx.DefaultPosition, wx.Size(250, 110))

        self.settings = plugin.settings
        self.session = plugin.session
        self.plugin = plugin

        self.panel = wx.Panel(self,-1)
        sizer = wx.GridBagSizer(1, 2)
        self.panel.SetSizer(sizer)
        menu = wx.Menu()
        menu.AppendSeparator()
        menu.Append(wx.ID_EXIT, "&Close", "Close this window")
        menuBar = wx.MenuBar()
        menuBar.Append(menu, "&File");
        self.SetMenuBar(menuBar)

        self.old_idle = self.settings.get_setting('IdleStatusAlias')

        ac_text = wx.StaticText(self.panel, -1, "AC:", wx.Point(0, 5))
        self.ac = wx.SpinCtrl(self.panel, ID_ROLL, "", 
                                wx.Point(18, 0), wx.Size(45, -1), min = -100, max = 100, initial = 10)
        self.ac.SetValue(10)

        touch_text = wx.StaticText(self.panel, -1, "Touch:", wx.Point(0, 25))
        self.touch = wx.SpinCtrl(self.panel, ID_ROLL, "", 
                                wx.Point(60, 25), wx.Size(45, -1), min = -100, max = 100, initial = 10)
        self.touch.SetValue(10)

        ff_text = wx.StaticText(self.panel, -1, "FF:", wx.Point(115, 25))
        self.ff = wx.SpinCtrl(self.panel, ID_ROLL, "", 
                                wx.Point(165, 25), wx.Size(45, -1), min = -100, max = 100, initial = 10)
        self.ff.SetValue(10)
        
        max_hp_text = wx.StaticText(self.panel, -1, "/", wx.Point(150, 5))
        self.max_hp = wx.SpinCtrl(self.panel, ID_ROLL, "", 
                                wx.Point(158, 0), wx.Size(48, -1), min = -999, max = 999, initial = 10)
        self.max_hp.SetValue(10)

        hp_text = wx.StaticText(self.panel, -1, "HP:", wx.Point(80, 5))
        self.hp = wx.SpinCtrl(self.panel, ID_ROLL, "", 
                                wx.Point(98, 0), wx.Size(48, -1), min = -999, max = 999, initial = 10)
        self.hp.SetValue(10)

        sizer.Add(ac_text, (1,0), span=(1,1))
        sizer.Add(self.ac, (1,1), span=(1,1))
        sizer.Add(touch_text, (1,2), span=(1,1))
        sizer.Add(self.touch, (1,3), span=(1,1))
        sizer.Add(ff_text, (1,4), span=(1,1))
        sizer.Add(self.ff, (1,5), span=(1,1))
        sizer.Add(hp_text, (0,0), span=(1,1))
        sizer.Add(self.hp, (0,1), span=(1,1))
        sizer.Add(max_hp_text, (0,2), span=(1,1))
        sizer.Add(self.max_hp, (0,3), span=(1,1))
        self.SetMinSize((350,100))
        self.Bind(wx.EVT_SPINCTRL, self.SetStatus, id=ID_ROLL)
        self.Bind(wx.EVT_TEXT, self.SetStatus, id=ID_ROLL)
        self.Bind(wx.EVT_MENU, self.TimeToQuit, id=wx.ID_EXIT)
        self.Bind(wx.EVT_CLOSE, self._close)
        self.SetStatus(None)

    def SetStatus(self, evt):
        new_status = "AC: " + str(self.ac.GetValue()) + " (Touch: " + str(self.touch.GetValue()) + " FF: " + str(self.ff.GetValue()) + ")" + " HP: " + str(self.hp.GetValue()) + "/" + str(self.max_hp.GetValue())
        self.settings.set_setting('IdleStatusAlias',new_status)
        self.session.set_text_status(new_status)

    def TimeToQuit(self, event):
        self.settings.set_setting('IdleStatusAlias',self.old_idle)
        self.session.set_text_status(self.old_idle)
        self.frame = None
        self.Destroy()

    def _close(self, evt):
        self.Hide()
        item = self.plugin.menu.FindItemById(self.plugin.menu.FindItem("GSC Window"))
        item.Check(False)
