from orpg.orpg_wx import *
from orpg.orpgCore import *
from orpg.plugindb import plugindb
from orpg.dirpath import dir_struct

#sys.path.append(dir_struct["plugins"])

class PluginFrame(wx.Frame):
    def __init__(self, parent):
        wx.Frame.__init__(self, parent, wx.ID_ANY, "Plugin Control Panel")
        self.panel = wx.Panel(self, wx.ID_ANY)
        self.parent = parent
        self.startplugs = plugindb.GetList("plugincontroller", "startup_plugins", [])
        self.available_plugins = {}
        self.enabled_plugins  = {}
        self.pluginNames = []
        self.SetMinSize((380, 480))
        self._selectedPlugin = None
        self.Bind(wx.EVT_CLOSE, self._close)

    #Public Methods
    def Start(self):
        self.__buildGUI()
        self._update(None)
        self.base_sizer = wx.BoxSizer(wx.VERTICAL)
        self.base_sizer.Add(self.panel, 1, wx.EXPAND)
        self.panel.SetSizer(self.main_sizer)
        self.panel.SetAutoLayout(True)
        self.panel.Fit()
        self.SetSizer(self.base_sizer)
        self.SetAutoLayout(True)
        self.Fit()

    def get_activeplugins(self):
        return self.enabled_plugins

    def get_startplugins(self):
        return self.startplugs

    #Private Methods
    def __buildGUI(self):
        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.btn_sizer2 = wx.BoxSizer(wx.HORIZONTAL)
        self.head_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.err_sizer = wx.BoxSizer(wx.VERTICAL)
        self.err_sizer.Add(self.head_sizer, 0, wx.EXPAND)
        self.errorMessage = wx.StaticText(self.panel, wx.ID_ANY, "")
        self.err_sizer.Add(self.errorMessage, 0, wx.EXPAND)
        self.main_sizer.Add(self.err_sizer, 0, wx.EXPAND)
        self.pluginList = wx.ListCtrl(self.panel, wx.ID_ANY, 
                              style=wx.LC_SINGLE_SEL|wx.LC_REPORT|wx.LC_HRULES|wx.LC_SORT_ASCENDING)
        self.pluginList.InsertColumn(0, "Name")
        self.pluginList.InsertColumn(1, "Author")
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self._selectPlugin, self.pluginList)
        self.Bind(wx.EVT_LIST_ITEM_DESELECTED, self._deselectPlugin, self.pluginList)
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self._togglePlugin, self.pluginList)
        self.Bind(wx.EVT_LIST_COL_CLICK, self._sort, self.pluginList)
        self.main_sizer.Add(self.pluginList, 1, wx.EXPAND)

        self.enableAllBtn = wx.Button(self.panel, wx.ID_ANY, "Enable All")
        self.enableBtn = wx.Button(self.panel, wx.ID_ANY, "Enable")
        self.disableAllBtn = wx.Button(self.panel, wx.ID_ANY, "Disable All")
        self.disableBtn = wx.Button(self.panel, wx.ID_ANY, "Disable")
        self.autostartBtn = wx.Button(self.panel, wx.ID_ANY, "Autostart")
        self.helpBtn = wx.Button(self.panel, wx.ID_ANY, "Plugin Info")
        self.updateBtn = wx.Button(self.panel, wx.ID_ANY, "Update List")

        self.Bind(wx.EVT_BUTTON, self._enableAll, self.enableAllBtn)
        self.Bind(wx.EVT_BUTTON, self._enable, self.enableBtn)
        self.Bind(wx.EVT_BUTTON, self._disableAll, self.disableAllBtn)
        self.Bind(wx.EVT_BUTTON, self._disable, self.disableBtn)
        self.Bind(wx.EVT_BUTTON, self._autostart, self.autostartBtn)
        self.Bind(wx.EVT_BUTTON, self._help, self.helpBtn)
        self.Bind(wx.EVT_BUTTON, self._update, self.updateBtn)

        self.btn_sizer.Add(self.enableBtn, 0, wx.EXPAND)
        self.btn_sizer.Add(self.disableBtn, 0, wx.EXPAND)
        self.btn_sizer.Add(self.autostartBtn, 0, wx.EXPAND)
        self.btn_sizer.Add(self.helpBtn, 0, wx.EXPAND)

        self.btn_sizer2.Add(self.updateBtn, 0, wx.EXPAND)
        self.btn_sizer2.Add(self.enableAllBtn, 0, wx.EXPAND)
        self.btn_sizer2.Add(self.disableAllBtn, 0, wx.EXPAND)

        self.__disablePluginBtns()

        self.main_sizer.Add(self.btn_sizer, 0, wx.EXPAND)
        self.main_sizer.Add(self.btn_sizer2, 0, wx.EXPAND)

        # Create Book Mark Image List
        self.pluginList.Bind(wx.EVT_LEFT_DOWN, self.on_hit)
        self._imageList = wx.ImageList( 16, 16, False )
        img = wx.Image(dir_struct["icon"]+"add_button.png", wx.BITMAP_TYPE_PNG).ConvertToBitmap()
        self._imageList.Add( img )
        img = wx.Image(dir_struct["icon"]+"check_button.png", wx.BITMAP_TYPE_PNG).ConvertToBitmap()
        self._imageList.Add( img )
        self.pluginList.SetImageList( self._imageList, wx.IMAGE_LIST_SMALL )

    def on_hit(self, evt):
        pos = wx.Point( evt.GetX(), evt.GetY() )
        (item, flag, sub) = self.pluginList.HitTestSubItem( pos )
        ## Item == list[server], flag == (32 = 0 colum, 128 = else) ##
        if flag == 32: self._autostart(item)
        evt.Skip()

    def __disablePluginBtns(self):
        self.enableBtn.Disable()
        self.disableBtn.Disable()
        self.autostartBtn.Disable()
        self.helpBtn.Disable()

    def __enablePluginBtns(self):
        self.autostartBtn.Label = "Autostart"
        self.enableBtn.Enable()
        self.disableBtn.Enable()
        self.autostartBtn.Enable()
        self.helpBtn.Enable()

    def __error(self, errMsg):
        self.errorMessage.Label += "\n" + str(errMsg)
        self.__doLayout()

    def __clearError(self):
        self.errorMessage.Label = ""
        self.__doLayout()

    def __checkIdx(self, evt):
        if isinstance(evt, int): return evt
        elif self._selectedPlugin is not None: return self._selectedPlugin
        else:
            dlg = wx.MessageDialog(None, 
                                   "You need to select a plugin before you can use this!", 
                                   'ERROR', wx.OK)
            dlg.ShowModal()
            dlg.Destroy()
            return None

    def __impPlugin(self, pname):
        try:
            if "plugins." + pname in sys.modules:
                del sys.modules["plugins." + pname] 
                #to ensure that the newly-imported one will be used correctly. 
                #No, reload() is not a better way to do this.
            mod = __import__("plugins." + pname)
            plugin = getattr(mod, pname)
            pdata = plugin.Plugin(plugindb, self.parent)
            self.available_plugins[pdata.name] = [pname, pdata, pdata.author, pdata.help]
            return plugin

        except Exception, e:
            self.__error(e)
            traceback.print_exc()
            print e

    def __doLayout(self):
        self.Freeze()
        self.panel.Layout()
        self.Fit()
        self.Thaw()

    def __pluginSort(self, item1, item2):
        return cmp(self.pluginNames[item1], self.pluginNames[item2])

    #Events
    def _selectPlugin(self, evt):
        self._selectedPlugin = evt.GetIndex()
        self.__enablePluginBtns()
        pname = self.pluginList.GetItem(self._selectedPlugin, 0).GetText()
        info = self.available_plugins[pname]

        if info[0] in self.enabled_plugins:
            self.enableBtn.Disable()
        else:
            self.disableBtn.Disable()
        if pname in self.startplugs:
            self.autostartBtn.Label = "Disable Autostart"

        self.__doLayout()
        self.pluginList.SetItemState(self._selectedPlugin, 
                                     wx.LIST_STATE_SELECTED, 
                                     wx.LIST_STATE_SELECTED)

    def _deselectPlugin(self, evt):
        self.__disablePluginBtns()
        self._selectedPlugin = None

    def _togglePlugin(self, evt):
        idx = evt.GetIndex()
        pname = self.pluginList.GetItem(idx, 0).GetText()
        info = self.available_plugins[pname]
        if info[0] in self.enabled_plugins: self._disable(idx)
        else: self._enable(idx)
        self.pluginList.SetItemState(self._selectedPlugin, 0, wx.LIST_STATE_SELECTED)

    def _enableAll(self, evt):
        for pname in self.available_plugins.iterkeys():
            info = self.available_plugins[pname]
            if info[0] not in self.enabled_plugins:
                idx = self.pluginList.FindItem(-1, pname)
                self._enable(idx)

    def _enable(self, evt):
        idx = self.__checkIdx(evt)
        if idx is None:
            return
        pname = self.pluginList.GetItem(idx, 0).GetText()
        info = self.available_plugins[pname]
        info[1].menu_start()

        try:
            info[1].plugin_enabled()
        except Exception, e:
            self.__error(e)
            traceback.print_exc()
            print e
            self.pluginList.SetItemBackgroundColour(idx, (255,0,0))
            info[1].menu_cleanup()
            return

        self.enabled_plugins[info[0]] = info[1]
        self.pluginList.SetItemBackgroundColour(idx, (0,255,0))
        self.enableBtn.Disable()
        self.disableBtn.Enable()

    def _disableAll(self, evt):
        for entry in self.enabled_plugins.keys():
            idx = self.pluginList.FindItem(0, self.enabled_plugins[entry].name)
            self._disable(idx)

    def _disable(self, evt):
        idx = self.__checkIdx(evt)
        if idx is None:
            return
        pname = self.pluginList.GetItem(idx, 0).GetText()
        info = self.available_plugins[pname]
        info[1].menu_cleanup()
        try:
            info[1].plugin_disabled()
            del self.enabled_plugins[info[0]]
        except Exception, e:
            self.__error(e)
            traceback.print_exc()
            print e
            self.pluginList.SetItemBackgroundColour(idx, (255,0,0))
            return
        self.pluginList.SetItemBackgroundColour(idx, (255,255,255))
        self.disableBtn.Disable()
        self.enableBtn.Enable()

    def _autostart(self, evt):
        idx = self.__checkIdx(evt)
        if idx is None: return
        pname = self.pluginList.GetItem(idx, 0).GetText()
        info = self.available_plugins[pname]
        if self.pluginList.GetItem(idx, 0).GetText() in self.startplugs:
            self.startplugs.remove(self.pluginList.GetItem(idx, 0).GetText())
            self.pluginList.SetItemImage(idx, 0, 0)
            self.autostartBtn.Label = "Autostart"
            if info[0] in self.enabled_plugins:
                dlg = wx.MessageDialog(None, 'Disable Plugin Now?', 'Plugin Enabled', 
                    wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION)
                dlg.ShowModal()
                if dlg.ShowModal() == wx.ID_YES: self._disable(evt)
        else:
            self.startplugs.append(self.pluginList.GetItem(idx, 0).GetText())
            self.pluginList.SetItemImage(idx, 1, 0)
            self.autostartBtn.Label = "Disable Autostart"
            if info[0] not in self.enabled_plugins:
                dlg = wx.MessageDialog(None, 'Enable Plugin Now?', 'Plugin Disabled', 
                    wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION)
                if dlg.ShowModal() == wx.ID_YES: self._enable(evt)

        plugindb.SetList("plugincontroller", "startup_plugins", self.startplugs)
        self.__doLayout()

    def _help(self, evt):
        if isinstance(evt, int): idx = evt
        elif self._selectedPlugin is not None: idx = self._selectedPlugin
        else:
            dlg = wx.MessageDialog(None, 
                                   "You need to select a plugin before you can use this!", 
                                   'ERROR', wx.OK)
            dlg.ShowModal()
            dlg.Destroy()
            return

        pname = self.pluginList.GetItem(idx, 0).GetText()
        info = self.available_plugins[pname]
        msg = "Author(s):\t" + info[2] + "\n\n" + info[3]
        dlg = wx.MessageDialog(None, msg, 'Plugin Information: ' + pname, wx.OK)
        dlg.ShowModal()
        dlg.Destroy()

    def _update(self, evt):
        self.__clearError()
        self._disableAll(None)
        self.available_plugins = {}
        self.errorMessage.Label = ""
        self.pluginList.DeleteAllItems()
        self.pluginNames = []

        list_of_plugin_dir = os.listdir(dir_struct["plugins"])
        for p in list_of_plugin_dir:
            if p[:2].lower()=="xx" and p[-3:]==".py":
                self.__impPlugin(p[:-3])
            elif p[:2].lower()=="xx" and p[-4:]==".pyc":
                self.__impPlugin(p[:-4])

        i = 0
        for plugname, info in self.available_plugins.iteritems():
            self.pluginNames.append(plugname)
            idx = self.pluginList.InsertStringItem(self.pluginList.GetItemCount(), plugname)
            self.pluginList.SetStringItem(idx, 1, info[2])
            self.pluginList.SetItemImage(idx, 0, 0)
            if plugname in self.startplugs:
                self.pluginList.SetItemImage(idx, 1, 0)
                self._enable(idx)
            self.pluginList.SetItemData(idx, i)
            i += 1
        self.pluginList.SetColumnWidth(0, wx.LIST_AUTOSIZE)
        self.pluginList.SetColumnWidth(1, wx.LIST_AUTOSIZE)
        self.__doLayout()
        self.__disablePluginBtns()

    def _close(self, evt):
        self.Hide()

    def _sort(self, evt):
        self.pluginList.SortItems(self.__pluginSort)
