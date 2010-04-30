import os, wx
import orpg.pluginhandler
from orpg.orpgCore import *
from orpg.tools.InterParse import Parse

class Plugin(orpg.pluginhandler.PluginHandler):
    # Initialization subroutine.
    #
    # !self : instance of self
    # !openrpg : instance of the the base openrpg control
    def __init__(self, plugindb, parent):
        orpg.pluginhandler.PluginHandler.__init__(self, plugindb, parent)
        self.orpgframe = component.get('frame')

        # The Following code should be edited to contain the proper information
        self.name = 'Simple Init'
        self.author = 'Dj Gilcrease + Tyler Starke'
        self.help = 'This is a simplistic Init tool that does not rely on Chat message parsing'

        #You can set variables below here. Always set them to a blank value in this section. Use plugin_enabled
        #to set their proper values.

    def plugin_menu(self):
        self.menu = wx.Menu()

        self.toggle = self.menu.AppendCheckItem(wx.ID_ANY, 'Show')
        self.topframe.Bind(wx.EVT_MENU, self.on_init, self.toggle)
        self.toggle.Check(True)


    def plugin_enabled(self):
        self.plugin_addcommand('/inittoggle', self.on_init, '- This will Show or Hide the Init window')
        self.plugin_addcommand('/rollinit', self.rollInit, '- This will roll a new set of Inits', False)
        self.plugin_addcommand('/startcombat', self.startInit, '- This will start the combat', False)
        self.plugin_addcommand('/nextplayer', self.advanceInit, '- This will advance the Initiative to the next Player', False)
        self.plugin_addcommand('/stopcombat', self.stopInit, '- This will end the combat', False)
        self.plugin_addcommand('/pausecombat', self.pauseInit, '- This will pause the auto Advancer', False)

        self.InitSaves = self.plugindb.GetDict("xxsimpleinit", "InitSaves", {})
        self.frame = InitFrame(self)
        self.frame.Show()
        self.advanceTimer = wx.Timer(self.frame, wx.NewId())
        self.frame.Bind(wx.EVT_TIMER, self.advanceInit, self.advanceTimer)
        self.buttonTimer = wx.Timer(self.frame, wx.NewId())
        self.frame.Bind(wx.EVT_TIMER, self.buttonCheck, self.buttonTimer)
        self.buttonTimer.Start(250)
        self.autoAdvancePaused = False

    def plugin_disabled(self):
        self.plugin_removecmd('/inittoggle')
        self.plugin_removecmd('/rollinit')
        self.plugin_removecmd('/startcombat')
        self.plugin_removecmd('/nextplayer')
        self.plugin_removecmd('/stopcombat')
        self.plugin_removecmd('/pausecombat')

        self.advanceTimer.Stop()
        del self.advanceTimer

        self.buttonTimer.Stop()
        del self.buttonTimer

        try: self.frame.Destroy()
        except: pass

    def on_init(self, cmdargs):
        if self.frame.IsShown():
            self.toggle.Check(False)
            self.frame.Hide()
        else:
            self.toggle.Check(True)
            self.frame.Show()

    def startInit(self, evt=None):
        if self.frame.initList.GetItemCount() == 0:
            self.chat.InfoPost('You need to add some stuff to the Init list before you start')
            return

        if not self.frame.startButton.IsEnabled():
            self.chat.InfoPost('Combat Round has already started! You must Stop the current combat to start a new one.')
            return

        self.orpgframe.Freeze()
        self.frame.Freeze()
        self.frame.nextButton.Enable()
        self.frame.stopButton.Enable()
        self.frame.startButton.Disable()
        self.frame.rollButton.Disable()
        self.frame.autoAdvanceCheck.Disable()
        self.frame.autoAdvanceList.Disable()
        self.frame.autoAdvanceToggle.Enable()
        self.frame.addButton.Disable()
        self.frame.editButton.Disable()
        self.frame.deleteButton.Disable()
        self.frame.saveButton.Disable()
        self.frame.loadButton.Disable()
        self.frame.clearButton.Disable()

        self.frame.currentInit = -1
        self.round = 0

        self.chat.Post('<center><font color="#00ff00"><b>== START COMBAT ==</b></font></center>', True, True, c='simpleinit-combat')
        self.advanceInit()
        self.frame.Thaw()

        if self.frame.autoAdvanceCheck.IsChecked():
            time = int(60000*int(self.frame.autoAdvanceList.GetStringSelection()))
            self.advanceTimer.Start(time)
        else:
            self.frame.addButton.Enable()
            self.frame.editButton.Enable()
            self.frame.deleteButton.Enable()

        if self.frame.IsShown():
            wx.CallAfter(self.frame.SetFocus)

        wx.CallAfter(self.orpgframe.Thaw)

    def stopInit(self, evt=None):
        if not self.frame.stopButton.IsEnabled():
            self.chat.InfoPost('Combat is already ended!')
            return

        self.frame.Freeze()
        self.frame.nextButton.Disable()
        self.frame.stopButton.Disable()
        self.frame.startButton.Enable()
        self.frame.rollButton.Enable()
        self.frame.autoAdvanceCheck.Enable()
        self.frame.autoAdvanceList.Enable()
        self.frame.autoAdvanceToggle.Disable()
        self.frame.addButton.Enable()
        self.frame.editButton.Enable()
        self.frame.deleteButton.Enable()
        self.frame.saveButton.Enable()
        self.frame.loadButton.Enable()
        self.frame.clearButton.Enable()

        for i in xrange(0, self.frame.initList.GetItemCount()):
            self.frame.currentInit = i
            if self.frame.currentInit.type == 'Effect':
                self.frame.initList.DeleteItem(i)

        self.frame.currentInit = 0

        if self.autoAdvancePaused and self.frame.autoAdvanceCheck.IsChecked():
            self.pauseInit('No Adv')
        self.frame.Thaw()

        self.advanceTimer.Stop()
        self.chat.Post('<center><font color="#ff0000" ><b>== END COMBAT ==</b></font></center>', True, True, c='simpleinit-combat')

    def advanceInit(self, evt=None):
        if not self.frame.nextButton.IsEnabled():
            self.chat.InfoPost('You must first Start combat inorder to advance the initiative turn!')
            return

        self.frame.currentInit = self.frame.initIdx+1
        if self.frame.currentInit.type == 'Effect':
            newDur = str(int(self.frame.currentInit.duration)-1)
            self.frame.initList.SetStringItem(self.frame.initIdx, 2, newDur)
            msg = '<br><table width="100%" border="1"><tr><td align="center"><center><u><b><font color="#ff0000" >EFFECT NOTICE</font></b></u></center></td></tr>'
            msg += '<tr><td align="center"><font color="#000000">' + self.frame.currentInit.name + ' has ' + newDur + ' rounds remaining</font></td></tr></table><br />'
            self.chat.Post(msg, True, True, c='simpleinit-effect')
            wx.CallAfter(self.advanceInit)
        else:
            msg = '<table width="100%" border="1"><tr><td align="center"><u><font color="#ff0000" ><b>' + self.frame.nextMessage.GetValue() + '</b></font></u></td></tr>'
            msg += '<tr><td align="center"><b><font color="#ff0000">' + str(self.frame.initIdx+1) + ':</font> '
            msg += '<font color="#0000ff">(' + self.frame.currentInit.init + ')</font> '
            msg += '<font color="#000000">' + self.frame.currentInit.name + '</b></font></td></tr></table><br />'
            self.chat.Post(msg, True, True, c='simpleinit-pc')

        if self.frame.currentInit.type == 'Effect' and int(self.frame.currentInit.duration) <= 0:
            self.frame.Freeze()
            cidx = self.frame.initIdx
            self.frame.initList.DeleteItem(cidx)
            self.frame.currentInit = cidx
            self.frame.Thaw()

    def pauseInit(self, evt=None):
        self.frame.Freeze()
        if not self.autoAdvancePaused:
            self.frame.autoAdvanceToggle.SetLabel('Resume Auto Advance')
            self.autoAdvancePaused = True
            self.advanceTimer.Stop()
            self.frame.nextButton.Disable()
            self.frame.addButton.Enable()
            self.frame.editButton.Enable()
            self.frame.deleteButton.Enable()
        else:
            self.frame.autoAdvanceToggle.SetLabel('Pause Auto Advance')
            self.frame.nextButton.Enable()
            self.frame.addButton.Disable()
            self.frame.editButton.Disable()
            self.frame.deleteButton.Disable()
            self.autoAdvancePaused = False
            if evt != 'No Adv':
                self.advanceInit()
            self.advanceTimer.Start()
        self.frame.Thaw()

    def newRound(self):
        self.round += 1
        msg = '<br><hr><font color="#ff0000" ><b>End of Round #' + str(self.round-1) + ', Starting Round #' + str(self.round) + '</b></font><hr>'
        self.chat.Post(msg, True, True)

    def rollD20Init(self):
        if not self.frame.rollButton.IsEnabled():
            self.chat.InfoPost("You cannot roll new Inits at this time")
            return
        self.orpgframe.Freeze()
        self.frame.Freeze()
        msg = '<br><center><font color="#0000ff" ><b>== START INIT LIST ==</b></font></center><br>'
        msg += '<font color="#000000"><b>'
        for i in xrange(0, self.frame.initList.GetItemCount()):
            self.frame.currentInit = i
            if self.frame.currentInit.manual == 'No':
                initRoll = Parse.Dice('[1d20' + self.frame.currentInit.initMod + ']')

                initRoll = initRoll.split('(')
                initRoll = initRoll[1].replace(')','')
                self.frame.initList.SetStringItem(i, 4, initRoll)
                self.frame.initList.SetItemData(i, int(initRoll))
            else:
                initRoll = self.frame.currentInit.init

            if self.frame.currentInit.type != 'Effect':
                msg += '<br>' + self.frame.currentInit.name + ' = <font color="#ff0000">' + initRoll + '</font>'

        msg += '</b></font><br>'

        self.frame.initList.SortItems(self.frame.initSort)
        msg += '<center><font color="#0000ff" ><b>== END INIT LIST ==</b></center></font>'
        self.chat.Post(msg, True, True, c='simpleinit-lst')

        self.frame.Thaw()
        if self.frame.IsShown():
            wx.CallAfter(self.frame.SetFocus)
        wx.CallAfter(self.orpgframe.Thaw)

    #Events
    def rollInit(self, evt):
        if self.frame.initRollType.GetStringSelection() == 'd20':
            self.rollD20Init()

    def buttonCheck(self, evt):
        if self.frame.initList.GetItemCount() == 0:
            self.frame.Freeze()
            self.advanceTimer.Stop()
            self.frame.startButton.Disable()
            self.frame.rollButton.Disable()
            self.frame.nextButton.Disable()
            self.frame.stopButton.Disable()
            self.frame.editButton.Disable()
            self.frame.deleteButton.Disable()
            self.frame.saveButton.Disable()
            self.frame.clearButton.Disable()
            self.frame.Thaw()
        elif not self.frame.stopButton.IsEnabled():
                self.frame.startButton.Enable()
                self.frame.rollButton.Enable()
                self.frame.editButton.Enable()
                self.frame.deleteButton.Enable()
                self.frame.saveButton.Enable()
                self.frame.clearButton.Enable()
        if self.autoAdvancePaused:
            return

        if not self.frame.autoAdvanceCheck.IsChecked():
            self.frame.autoAdvanceToggle.Disable()
            self.autoAdvancePaused = True
        elif self.frame.autoAdvanceCheck.IsChecked() and self.frame.stopButton.IsEnabled():
            self.frame.autoAdvanceToggle.Enable()

class InitFrame(wx.Frame):
    def __init__(self, plugin):
        self.plugin = plugin
	self.toggle = plugin.toggle
        self.log = component.get('log')
        self.log.log("Enter InitFrame", ORPG_DEBUG)

        wx.Frame.__init__(self, None, wx.ID_ANY, title="Simple Init", style=wx.DEFAULT_FRAME_STYLE)
        self.SetOwnBackgroundColour('#EFEFEF')

        self.dir_struct = component.get('dir_struct')
        self.settings = component.get('settings')
        self.xml = component.get('xml')
        self.validate = component.get('validate')

        self.Freeze()
        self.buildMenu()
        self.buildButtons()
        self.buildGUI()
        wx.CallAfter(self.InitSetup)

        self.Bind(wx.EVT_CLOSE, self.onCloseWindow)

        self.log.log("Exit InitFrame", ORPG_DEBUG)

    def InitSetup(self):
        self.chat = component.get('chat')
        self.gametree = component.get('tree')
        self.map = component.get('map')
        self.session = component.get('session')

        self.initIdx = -1
        self.Thaw()

    def initSort(self, item1, item2):
        if item1 == item2:
            return 0
        elif item1 > item2:
            return -1
        elif item1 < item2:
            return 1

        return 0

    def onCloseWindow(self, evt):
        self.Hide()
	self.toggle.Check(False)

    def buildMenu(self):
        self.log.log("Enter InitFrame->buildMenu(self)", ORPG_DEBUG)

        initmenu = wx.Menu()

        item = wx.MenuItem(initmenu, wx.ID_ANY, "Add\tInsert", "Add")
        self.Bind(wx.EVT_MENU, self.OnMB_InitAdd, item)
        initmenu.AppendItem(item)

        item = wx.MenuItem(initmenu, wx.ID_ANY, "Edit\tCtrl+E", "Edit")
        self.Bind(wx.EVT_MENU, self.OnMB_InitEdit, item)
        initmenu.AppendItem(item)

        item = wx.MenuItem(initmenu, wx.ID_ANY, "Delete\tCtrl+D", "Delete")
        self.Bind(wx.EVT_MENU, self.OnMB_InitDelete, item)
        initmenu.AppendItem(item)

        item = wx.MenuItem(initmenu, wx.ID_ANY, "Clear\tCtrl+C", "Clear")
        self.Bind(wx.EVT_MENU, self.OnMB_InitClear, item)
        initmenu.AppendItem(item)

        initmenu.AppendSeparator()

        item = wx.MenuItem(initmenu, wx.ID_ANY, "Next\tEnter", "Next")
        self.Bind(wx.EVT_MENU, self.plugin.advanceInit, item)
        initmenu.AppendItem(item)

        initmenu.AppendSeparator()

        item = wx.MenuItem(initmenu, wx.ID_ANY, "Save\tCtrl+S", "Save Current Init List")
        self.Bind(wx.EVT_MENU, self.OnMB_InitSave, item)
        initmenu.AppendItem(item)

        item = wx.MenuItem(initmenu, wx.ID_ANY, "Load", "Load New Init List")
        self.Bind(wx.EVT_MENU, self.OnMB_InitLoad, item)
        initmenu.AppendItem(item)

        menu = wx.MenuBar()
        menu.Append(initmenu, "&Init")

        self.SetMenuBar(menu)

        self.log.log("Exit InitFrame->buildMenu(self)", ORPG_DEBUG)

    def buildButtons(self):
        self.log.log("Enter InitFrame->buildButtons(self)", ORPG_DEBUG)

        self.autoAdvanceCheck = wx.CheckBox(self, wx.ID_ANY, "")
        self.autoAdvanceCheck.SetValue(True)
        self.autoAdvanceList = wx.Choice(self, wx.ID_ANY, choices=['1','2','3','4','5'])
        self.autoAdvanceList.SetSelection(2)
        self.autoAdvanceToggle = wx.Button(self, wx.ID_ANY, "Pause Auto Advance")
        self.Bind(wx.EVT_BUTTON, self.plugin.pauseInit, self.autoAdvanceToggle)
        self.autoAdvanceToggle.Disable()

        self.psizer = wx.BoxSizer(wx.HORIZONTAL)
        self.psizer.Add(wx.StaticText(self, wx.ID_ANY, "Auto Advance"), 0, wx.ALIGN_CENTER|wx.ALL, 5)
        self.psizer.Add(self.autoAdvanceCheck, 0, wx.ALIGN_CENTER|wx.ALL, 0)
        self.psizer.Add(wx.StaticText(self, wx.ID_ANY, "Every"), 0, wx.ALIGN_CENTER|wx.ALL, 5)
        self.psizer.Add(self.autoAdvanceList, 0, wx.ALIGN_CENTER|wx.ALL, 0)
        self.psizer.Add(wx.StaticText(self, wx.ID_ANY, "Minutes"), 0, wx.ALIGN_CENTER|wx.ALL, 5)
        self.psizer.Add(self.autoAdvanceToggle, 0, wx.ALIGN_CENTER|wx.ALL, 10)

        self.addButton = wx.Button(self, wx.ID_ANY, "Add")
        self.Bind(wx.EVT_BUTTON, self.OnMB_InitAdd, self.addButton)
        self.editButton = wx.Button(self, wx.ID_ANY, "Edit")
        self.editButton.Disable()
        self.Bind(wx.EVT_BUTTON, self.OnMB_InitEdit, self.editButton)
        self.deleteButton = wx.Button(self, wx.ID_ANY, "Delete")
        self.deleteButton.Disable()
        self.Bind(wx.EVT_BUTTON, self.OnMB_InitDelete, self.deleteButton)
        self.saveButton = wx.Button(self, wx.ID_ANY, "Save")
        self.saveButton.Disable()
        self.Bind(wx.EVT_BUTTON, self.OnMB_InitSave, self.saveButton)
        self.loadButton = wx.Button(self, wx.ID_ANY, "Load")
        self.Bind(wx.EVT_BUTTON, self.OnMB_InitLoad, self.loadButton)
        self.clearButton = wx.Button(self, wx.ID_ANY, "Clear")
        self.clearButton.Disable()
        self.Bind(wx.EVT_BUTTON, self.OnMB_InitClear, self.clearButton)


        self.esizer = wx.BoxSizer(wx.VERTICAL)
        self.esizer.Add(self.addButton, 0, wx.EXPAND|wx.ALL, 2)
        self.esizer.Add(self.editButton, 0, wx.EXPAND|wx.ALL, 3)
        self.esizer.Add(self.deleteButton, 0, wx.EXPAND|wx.ALL, 2)
        self.esizer.Add(self.saveButton, 0, wx.EXPAND|wx.ALL, 3)
        self.esizer.Add(self.loadButton, 0, wx.EXPAND|wx.ALL, 2)
        self.esizer.Add(self.clearButton, 0, wx.EXPAND|wx.ALL, 3)

        self.rollButton = wx.Button(self, wx.ID_ANY, "Roll New Inits")
        self.Bind(wx.EVT_BUTTON, self.plugin.rollInit, self.rollButton)
        self.startButton = wx.Button(self, wx.ID_ANY, "Start")
        self.Bind(wx.EVT_BUTTON, self.plugin.startInit, self.startButton)
        self.nextButton = wx.Button(self, wx.ID_ANY, "Next")
        self.nextButton.Disable()
        self.Bind(wx.EVT_BUTTON, self.plugin.advanceInit, self.nextButton)
        self.stopButton = wx.Button(self, wx.ID_ANY, "Stop")
        self.stopButton.Disable()
        self.Bind(wx.EVT_BUTTON, self.plugin.stopInit, self.stopButton)

        self.asizer = wx.BoxSizer(wx.HORIZONTAL)
        self.asizer.Add(self.rollButton, 0, wx.EXPAND|wx.ALL, 5)
        self.asizer.Add(self.startButton, 0, wx.EXPAND|wx.ALL, 5)
        self.asizer.Add(self.nextButton, 0, wx.EXPAND|wx.ALL, 5)
        self.asizer.Add(self.stopButton, 0, wx.EXPAND|wx.ALL, 5)

        self.log.log("Exit InitFrame->buildButtons(self)", ORPG_DEBUG)

    def buildGUI(self):
        self.log.log("Enter InitFrame->buildGUI(self)", ORPG_DEBUG)

        sizer = wx.GridBagSizer(hgap=1, vgap=1)

        self.initList = wx.ListCtrl(self, wx.ID_ANY, style=wx.LC_SINGLE_SEL|wx.LC_REPORT|wx.LC_HRULES)
        self.initList.InsertColumn(0, "Name")
        self.initList.InsertColumn(1, "Type")
        self.initList.InsertColumn(2, "Duration")
        self.initList.InsertColumn(3, "Init Mod")
        self.initList.InsertColumn(4, "Init")
        self.initList.InsertColumn(5, "Manualy Set")
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.selectInit, self.initList)
        self.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.deselectInit, self.initList)
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnMB_InitEdit, self.initList)
        self.Bind(wx.EVT_LIST_ITEM_FOCUSED, self.Test, self.initList)

        self.nextMessage = wx.TextCtrl(self, wx.ID_ANY, "UP NEXT FOR THE KILLING")
        msgsizer = wx.BoxSizer(wx.HORIZONTAL)
        msgsizer.Add(wx.StaticText(self, wx.ID_ANY, "Next Message"), 0, wx.ALIGN_CENTER|wx.ALL, 5)
        msgsizer.Add(self.nextMessage, 1, wx.EXPAND|wx.ALL, 5)

        self.initRollType = wx.Choice(self, wx.ID_ANY, choices=['d20'])
        self.initRollType.SetSelection(0)

        sizer.Add(self.psizer, (0,0), flag=wx.EXPAND)
        sizer.Add(wx.StaticText(self, wx.ID_ANY, 'Init Roll Type'), (0,1), flag=wx.ALIGN_BOTTOM|wx.ALIGN_CENTER_HORIZONTAL)
        sizer.Add(msgsizer, (1,0), flag=wx.EXPAND)
        sizer.Add(self.initRollType, (1,1), flag=wx.ALIGN_CENTER)
        sizer.Add(self.initList, (2,0), flag=wx.EXPAND)
        sizer.Add(self.esizer, (2,1), flag=wx.EXPAND)
        sizer.Add(self.asizer, (3,0), flag=wx.EXPAND)
        sizer.AddGrowableCol(0)
        sizer.AddGrowableRow(2)

        self.SetSizer(sizer)
        self.SetAutoLayout(True)
        self.Fit()

        self.log.log("Exit InitFrame->buildGUI(self)", ORPG_DEBUG)

    def updateInit(self, init, type):
        reset = False
        if not self.startButton.IsEnabled() and self.initList.GetItemCount() > 0:
            reset = True
            name = self.currentInit.name


        self.Freeze()

        if type == 'Add':
            i = self.initList.InsertStringItem(self.initList.GetItemCount(), init.name)
            self.initList.SetStringItem(i, 1, init.type)
            self.initList.SetStringItem(i, 2, init.duration)
            self.initList.SetStringItem(i, 3, init.initMod)
            self.initList.SetStringItem(i, 4, init.init)
            self.initList.SetStringItem(i, 5, init.manual)
            self.initList.SetItemData(i, init)
        else:
            self.initList.SetStringItem(self.initIdx, 0, init.name)
            self.initList.SetStringItem(self.initIdx, 1, init.type)
            self.initList.SetStringItem(self.initIdx, 2, init.duration)
            self.initList.SetStringItem(self.initIdx, 3, init.initMod)
            self.initList.SetStringItem(self.initIdx, 4, init.init)
            self.initList.SetStringItem(self.initIdx, 5, init.manual)
            self.initList.SetItemData(self.initIdx, init)

        self.initList.SortItems(self.initSort)
        self.initList.SetColumnWidth(0, wx.LIST_AUTOSIZE)
        self.initList.SetColumnWidth(1, wx.LIST_AUTOSIZE)
        self.initList.SetColumnWidth(2, wx.LIST_AUTOSIZE)
        self.initList.SetColumnWidth(3, wx.LIST_AUTOSIZE)

        if reset:
            for i in xrange(0, self.initList.GetItemCount()):
                self.currentInit = i
                if self.currentInit.name == name and type == 'Add':
                    break
                elif  self.currentInit.name == name and type == 'Edit':
                    self.currentInit = self.initIdx-1
                    break

            self.initList.Select(self.initIdx)
        else:
            self.currentInit = 0
        self.Thaw()

    #Events
    def Test(self, evt):
        pass

    def selectInit(self, evt):
        self.currentInit = evt.GetIndex()
        self.initList.SetItemState(self.initIdx, 0, wx.LIST_STATE_SELECTED)

    def deselectInit(self, evt):
        #self.currentInit = -1
        evt.Skip()

    def OnMB_InitAdd(self, evt):
        addeditwnd = AddEditWnd(self, Init('New'), 'Add')
        addeditwnd.Show()

    def OnMB_InitEdit(self, evt):
        addeditwnd = AddEditWnd(self, self.currentInit, 'Edit')
        addeditwnd.Show()

    def OnMB_InitDelete(self, evt):
        if self.initIdx != -1:
            self.initList.DeleteItem(self.initIdx)
            self.currentInit = 0

    def OnMB_InitClear(self, evt):
        self.initList.DeleteAllItems()
        self.initIdx = -1

    def OnMB_InitSave(self, evt):
        dlg = wx.TextEntryDialog(self, "Please Name This Init List", "New Init List")
        if dlg.ShowModal() == wx.ID_OK:
            saveas = dlg.GetValue()
            dlg.Destroy()
        else:
            dlg.Destroy()
            return

        self.Freeze()
        cidx = self.initIdx
        self.plugin.InitSaves[saveas] = []
        for i in xrange(0, self.initList.GetItemCount()):
            self.currentInit = i
            cinit = {}
            cinit['name'] = self.currentInit.name
            cinit['type'] = self.currentInit.type
            cinit['duration'] = self.currentInit.duration
            cinit['initMod'] = self.currentInit.initMod
            cinit['init'] = self.currentInit.init
            cinit['manual'] = self.currentInit.manual
            self.plugin.InitSaves[saveas].append(cinit)

        self.currentInit = cidx
        self.Thaw()

        self.plugin.plugindb.SetDict("xxsimpleinit", "InitSaves", self.plugin.InitSaves)


    def OnMB_InitLoad(self, evt):
        dlg = wx.Dialog(self, wx.ID_ANY, "Load Init List")
        sz = wx.BoxSizer(wx.HORIZONTAL)
        sz.Add(wx.StaticText(dlg, wx.ID_ANY, 'Select the Init List to Load'), 0, wx.ALIGN_CENTER)
        selectList = wx.Choice(dlg, wx.ID_ANY, choices=self.plugin.InitSaves.keys())
        selectList.SetSelection(0)
        sz.Add(selectList, 0, wx.EXPAND)
        sz.Add(wx.Button(dlg, wx.ID_OK, 'Load'), 0)
        sz.Add(wx.Button(dlg, wx.ID_CANCEL, 'Cancel'), 0)
        dlg.Show()

        dlg.SetSizer(sz)
        dlg.SetAutoLayout(True)
        dlg.Fit()

        if dlg.ShowModal() == wx.ID_OK:
            load = selectList.GetStringSelection()
            dlg.Destroy()
        else:
            dlg.Destroy()
            return

        self.Freeze()
        self.OnMB_InitClear(None)
        for newInit in self.plugin.InitSaves[load]:
            init = Init(newInit['name'], newInit['type'], newInit['duration'], newInit['initMod'], newInit['init'], newInit['manual'])
            self.updateInit(init, 'Add')
            del init

        self.initList.SortItems(self.initSort)
        self.currentInit = 0
        self.Thaw()

    #Getter/Setter
    def GetSelectedInit(self):
        return Init(self.initList.GetItem(self.initIdx, 0).GetText(),\
                self.initList.GetItem(self.initIdx, 1).GetText(),\
                self.initList.GetItem(self.initIdx, 2).GetText(),\
                self.initList.GetItem(self.initIdx, 3).GetText(),\
                self.initList.GetItem(self.initIdx, 4).GetText(),\
                self.initList.GetItem(self.initIdx, 5).GetText())

    def SetSelectedInit(self, idx):
        for i in xrange(0, self.initList.GetItemCount()):
            self.initList.SetItemBackgroundColour(i, (255,255,255))

        if idx >= self.initList.GetItemCount():
            self.initIdx = 0
            self.plugin.newRound()
        else:
            self.initIdx = idx

        if self.initIdx != -1:
            self.initList.SetItemBackgroundColour(self.initIdx, (0,255,0))

    #Properties
    currentInit = property(GetSelectedInit, SetSelectedInit)

class Init:
    def __init__(self, *args, **kwargs):
        """__init__(self, name, type='Player', duration='0', initMod='+0', init='0', manual='No')"""
        if kwargs.has_key('name'):
            self.name = kwargs['name']
        else:
            try:
                self.name = args[0]
            except:
                print 'Exception: Invalid initilization of ' + __name__ + ' Message. Missing name'

        try:
            self.type = args[1]
        except:
            if kwargs.has_key('type'):
                self.type = kwargs['type']
            else:
                self.type = 'Player'

        try:
            self.duration = args[2]
        except:
            if kwargs.has_key('duration'):
                self.duration = kwargs['duration']
            else:
                self.duration = '0'

        try:
            self.initMod = args[3]
        except:
            if kwargs.has_key('initMod'):
                self.initMod = kwargs['initMod']
            else:
                self.initMod = '0'

        try:
            self.init = args[4]
        except:
            if kwargs.has_key('init'):
                self.init = kwargs['init']
            else:
                self.init = '0'

        try:
            self.manual = args[5]
        except:
            if kwargs.has_key('manual'):
                self.manual = kwargs['manual']
            else:
                self.manual = 'No'

    def __int__(self):
        return int(self.init)


class AddEditWnd(wx.Frame):
    def __init__(self, parent, Init, edittype="Add"):
        self.parent = parent
        self.edittype = edittype
        if edittype == 'Add':
            wndTitle = 'Add New Initiative Member'
        else:
            wndTitle = 'Edit Initive Member'

        wx.Frame.__init__(self, parent, wx.ID_ANY, title=wndTitle, style=wx.DEFAULT_FRAME_STYLE|wx.STAY_ON_TOP)
        #self.MakeModal(True)
        self.SetOwnBackgroundColour('#EFEFEF')

        self.currentInit = Init

        self.Freeze()
        self.buildGUI()
        self.Thaw()

    def buildGUI(self):
        sizer = wx.GridBagSizer(hgap=1, vgap=1)
        sizer.SetEmptyCellSize((0,0))

        self.stDuration = wx.StaticText(self, wx.ID_ANY, 'Duration')
        self.stInitiative = wx.StaticText(self, wx.ID_ANY, 'Initiative')

        sizer.Add(wx.StaticText(self, wx.ID_ANY, 'Name'), (0,0), flag=wx.ALIGN_BOTTOM)
        sizer.Add(wx.StaticText(self, wx.ID_ANY, 'Type'), (0,1), flag=wx.ALIGN_BOTTOM)
        sizer.Add(self.stDuration, (0,2), flag=wx.ALIGN_BOTTOM)
        sizer.Add(wx.StaticText(self, wx.ID_ANY, 'Int Mod'), (0,3), flag=wx.ALIGN_BOTTOM)
        sizer.Add(self.stInitiative, (0,4), flag=wx.ALIGN_BOTTOM)
        sizer.Add(wx.StaticText(self, wx.ID_ANY, 'Manualy Set'), (0,5), flag=wx.ALIGN_BOTTOM)

        self.name = wx.TextCtrl(self, wx.ID_ANY)
        self.type = wx.Choice(self, wx.ID_ANY, choices=['Player', 'NPC', 'Effect'])
        self.type.SetSelection(0)
        self.Bind(wx.EVT_CHOICE, self.typeSelect, self.type)
        self.duration = wx.TextCtrl(self, wx.ID_ANY, '', size=(40,-1))
        self.duration.SetMaxLength(4)
        self.duration.Bind(wx.EVT_CHAR, self.validateNumber)
        self.initMod = wx.Choice(self, wx.ID_ANY, choices=['-20', '-19', '-18', '-17', '-16', '-15', '-14', '-13', '-12', '-11', '-10', '-9', '-8', '-7', '-6', '-5', '-4', '-3', '-2', '-1', '+0', '+1', '+2', '+3', '+4', '+5', '+6', '+7', '+8', '+9','+10', '+11', '+12', '+13', '+14', '+15', '+16', '+17', '+18', '+19', '+20'])
        self.initMod.SetSelection(20)
        self.initiative = wx.TextCtrl(self, wx.ID_ANY, '0', size=(40,-1))
        self.initiative.SetMaxLength(4)
        self.initiative.Bind(wx.EVT_CHAR, self.validateNumber)
        self.manual = wx.Choice(self, wx.ID_ANY, choices=['No', 'Yes'])
        self.manual.SetSelection(0)
        self.Bind(wx.EVT_CHOICE, self.manualSelect, self.manual)

        self.initiative.Hide()
        self.stInitiative.Hide()
        self.stDuration.Hide()
        self.duration.Hide()

        if self.edittype == 'Edit':
            self.name.SetValue(self.currentInit.name)
            self.type.SetStringSelection(self.currentInit.type)
            self.duration.SetValue(self.currentInit.duration)
            self.initMod.SetStringSelection(self.currentInit.initMod)
            self.initiative.SetValue(self.currentInit.init)
            self.manual.SetStringSelection(self.currentInit.manual)

            self.manualSelect(None)
            self.typeSelect(None)

        sizer.Add(self.name, (1,0), flag=wx.ALIGN_CENTER)
        sizer.Add(self.type, (1,1), flag=wx.ALIGN_CENTER)
        sizer.Add(self.duration, (1,2), flag=wx.ALIGN_CENTER)
        sizer.Add(self.initMod, (1,3), flag=wx.ALIGN_CENTER)
        sizer.Add(self.initiative, (1,4), flag=wx.ALIGN_CENTER)
        sizer.Add(self.manual, (1,5), flag=wx.ALIGN_CENTER)

        self.okButton = wx.Button(self, wx.ID_OK, 'Ok')
        self.cancelButton = wx.Button(self, wx.ID_CANCEL, 'Cancel')

        sizer.Add(self.okButton, (0,6), flag=wx.EXPAND)
        sizer.Add(self.cancelButton, (1,6))
        self.Bind(wx.EVT_BUTTON, self.onOK, self.okButton)
        self.Bind(wx.EVT_BUTTON, self.onCancel, self.cancelButton)

        self.SetSizer(sizer)
        self.SetAutoLayout(True)
        self.Fit()


    #Events
    def validateNumber(self, evt):
        if evt.GetKeyCode() == wx.WXK_DELETE or evt.GetKeyCode() == wx.WXK_BACK or (evt.GetKeyCode() < 256 and chr(evt.GetKeyCode()) in string.digits):
            evt.Skip()
        else:
            wx.Bell()

    def manualSelect(self, evt):
        if self.manual.GetStringSelection() == 'Yes':
            self.initiative.Show()
            self.stInitiative.Show()
        else:
            self.initiative.Hide()
            self.stInitiative.Hide()

        self.Fit()

    def typeSelect(self, evt):
        if self.type.GetStringSelection() == 'Effect':
            self.stDuration.Show()
            self.duration.Show()
        else:
            self.stDuration.Hide()
            self.duration.Hide()

        self.Fit()

    def onOK(self, evt):
        self.currentInit.name = self.name.GetValue()
        self.currentInit.type = self.type.GetStringSelection()
        self.currentInit.duration = self.duration.GetValue()
        self.currentInit.initMod = self.initMod.GetStringSelection()
        self.currentInit.init = self.initiative.GetValue()
        self.currentInit.manual = self.manual.GetStringSelection()
        self.parent.updateInit(self.currentInit, self.edittype)
        self.Close()

    def onCancel(self, evt):
        self.Close()
