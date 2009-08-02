import wx
#import wx.html
#import webbrowser
#import urllib
#import zipfile
#import traceback
import manifest
#import hashlib
import orpg.dirpath
from orpg.orpgCore import *
import orpg.orpg_version
import orpg.tools.orpg_log
import orpg.orpg_xml
import orpg.dirpath
#import orpg.tools.orpg_settings
import orpg.tools.validate
from mercurial import ui, hg, commands, repo, revlog, cmdutil

class Updater(wx.Panel):
    def __init__(self, parent, openrpg):
        wx.Panel.__init__(self, parent)

        ### Update Manager
        self.ui = ui.ui()
        self.repo = hg.repository(self.ui, ".")
        self.c = self.repo.changectx('tip')
        self.manifest = []
        self.manifest = self.c.manifest().keys()
        self.openrpg = openrpg
        #self.settings = openrpg.get_component('settings')
        self.xml = openrpg.get_component('xml')
        self.dir_struct = self.openrpg.get_component("dir_struct")
        self.parent = parent
        self.log = self.openrpg.get_component("log")
        self.log.log("Enter updaterFrame", ORPG_DEBUG)
        self.SetBackgroundColour(wx.WHITE)
        self.sizer = wx.GridBagSizer(hgap=1, vgap=1)
        self.changelog = wx.TextCtrl(self, wx.ID_ANY, size=(400, -1), style=wx.TE_MULTILINE | wx.TE_READONLY)
        self.filelist = wx.TextCtrl(self, wx.ID_ANY, size=(250, 300), style=wx.TE_MULTILINE | wx.TE_READONLY)
        self.buttons = {}
        self.buttons['progress_bar'] = wx.Gauge(self, wx.ID_ANY, 100)
        self.buttons['auto_text'] = wx.StaticText(self, wx.ID_ANY, "Auto Update")
        self.buttons['auto_check'] = wx.CheckBox(self, wx.ID_ANY)
        self.buttons['no_text'] = wx.StaticText(self, wx.ID_ANY, "No Update")
        self.buttons['no_check'] = wx.CheckBox(self, wx.ID_ANY)
        self.buttons['advanced'] = wx.Button(self, wx.ID_ANY, "Package Select")
        self.buttons['update'] = wx.Button(self, wx.ID_ANY, "Update Now")
        self.buttons['finish'] = wx.Button(self, wx.ID_ANY, "Finish")

        self.sizer.Add(self.changelog, (0,0), span=(4,1), flag=wx.EXPAND)
        self.sizer.Add(self.filelist, (0,1), span=(1,3), flag=wx.EXPAND)

        self.sizer.Add(self.buttons['progress_bar'], (1,1), span=(1,3), flag=wx.EXPAND)
        self.sizer.Add(self.buttons['auto_text'], (2,1))
        self.sizer.Add(self.buttons['auto_check'], (2,2), flag=wx.EXPAND)
        self.sizer.Add(self.buttons['no_text'], (3,1))
        self.sizer.Add(self.buttons['no_check'], (3,2), flag=wx.EXPAND)
        self.sizer.Add(self.buttons['advanced'], (2,3), flag=wx.EXPAND)
        self.sizer.Add(self.buttons['update'], (3,3), flag=wx.EXPAND)
        self.sizer.Add(self.buttons['finish'], (4,3), flag=wx.EXPAND)
        self.sizer.AddGrowableCol(0)
        self.sizer.AddGrowableRow(0)
        self.SetSizer(self.sizer)
        self.SetAutoLayout(True)
        self.initPrefs()

        self.current = self.c.branch()
        self.BranchInfo(self.current)
        #if self.autoupdate == "On": self.buttons['auto_check'].SetValue(True)

        ## Event Handlers
        self.Bind(wx.EVT_BUTTON, self.Update, self.buttons['update'])
        self.Bind(wx.EVT_BUTTON, self.Finish, self.buttons['finish'])
        self.Bind(wx.EVT_BUTTON, self.Advanced, self.buttons['advanced'])
        #self.Bind(wx.EVT_CHECKBOX, self.ToggleAutoUpdate, self.buttons['auto_check'])

    def showFinish(self):
        if self.Updated: self.filelist.SetValue(self.filelist.GetValue() + "Finished ... \n")
        self.buttons['finish'].Show()
        self.buttons['advanced'].Show()

    def initPrefs(self):
        #self.list_url = self.settings.get_setting("PackagesURL")
        #self.package_type = self.settings.get_setting("PackagesType")
        #self.package_name = self.settings.get_setting("PackagesName")
        self.SelectPackage = False
        #self.autoupdate = self.settings.get_setting("AutoUpdate")
        self.packages = None
        self.package = self.get_package()
        self.Updated = False
        self.Finished = False

    def isFinished(self):
        return self.Finished

    def ToggleAutoUpdate(self, event):
        if self.buttons['auto_check'].GetValue():
            self.autoupdate = "On"
            #self.settings.set_setting("AutoUpdate", "On")
            #self.Update(None)
        else:
            self.autoupdate = "Off"
            #self.settings.set_setting("AutoUpdate", "Off")

    def Update(self, evt=None):
        hg.clean(self.repo, self.current)

    def Finish(self, evt=None):
        #self.settings.updateIni()
        self.Finished = True
        self.Destroy() #destroys tab, pretty useless.

    def Advanced(self, evt=None):

        ## This part sucks.  Do they need to see the Branch List everytime?  No!! Press the button.
        dlg = wx.Dialog(self, wx.ID_ANY, "Package Selector", style=wx.DEFAULT_DIALOG_STYLE)
        if wx.Platform == '__WXMSW__': icon = wx.Icon(self.dir_struct["icon"]+'d20.ico', wx.BITMAP_TYPE_ICO)
        else: icon = wx.Icon(self.dir_struct["icon"]+"d20.xpm", wx.BITMAP_TYPE_XPM )
        dlg.SetIcon(icon)

        dlgsizer = wx.GridBagSizer(hgap=1, vgap=1)
        Yes = wx.Button( dlg, wx.ID_OK, "Ok" )
        Yes.SetDefault()
        rgroup = wx.RadioButton(dlg, wx.ID_ANY, "group_start", style=wx.RB_GROUP)
        rgroup.Hide()

        if self.packages == None: self.get_packages()
        if self.package_list == None: return
        types = self.package_list
        row=0; col=0
        self.current = self.c.branch()
        self.package_type = self.current
        self.btnlist = {}; self.btn = {}
        self.id = 1

        for t in types:
            self.btnName = str(t)
            self.btn[self.id] = wx.RadioButton(dlg, wx.ID_ANY, str(t), name=self.btnName)
            if self.btnName == self.current:
                self.btn[self.id].SetValue(True)
            self.btnlist[self.id] = self.btnName
            dlgsizer.Add(self.btn[self.id], (row, col))
            row += 1; self.id += 1

        dlgsizer.Add(Yes, (row+1,0))
        dlg.SetAutoLayout( True )
        dlg.SetSizer( dlgsizer )
        dlgsizer.Fit( dlg )
        dlg.Centre()
        dlg.Bind(wx.EVT_RADIOBUTTON, self.PackageSet)

        if dlg.ShowModal():
            dlg.Destroy()
            if self.Updated:
                self.Updated = False
                self.filelist.SetValue('')
                wx.CallAfter(self.check)

    def PackageSet(self, event):
        for btn in self.btn:
            if self.btn[btn].GetValue() == True: self.current = self.btnlist[btn]

        branches = self.repo.branchtags()
        heads = dict.fromkeys(self.repo.heads(), 1)
        l = [((n in heads), self.repo.changelog.rev(n), n, t) for t, n in branches.items()]

        #l.sort()
        #l.reverse()
        #for ishead, r, n, t in l: self.package_list.append(t)

        if self.current != type:
            #r = hg.islocal()
            files = self.c.files()
            #print commands.log(u, r, c)
            #print r.changelog

            ### Cleaning up for dev build 0.1
            ### The below material is for the Rev Log.  You can run hg log to see what data it will pull.
            #cs = r.changectx(c.rev()).changeset()
            #get = util.cachefunc(lambda r: repo.changectx(r).changeset())
            #changeiter, matchfn = cmdutil.walkchangerevs(u, r, 1, cs, 1)
            #for st, rev, fns in changeiter:
            #    revbranch = get(rev)[5]['branch']; print revbranch

            heads = dict.fromkeys(self.repo.heads(), self.repo.branchtags())
            branches = dict.copy(self.repo.branchtags())

            self.BranchInfo(self.current)


    def BranchInfo(self, branch):
        self.filelist.SetValue('')
        self.filelist.AppendText("Files that will change\n\n")
        self.changelog.SetValue('')
        changelog = "This is Dev Build 0.1 of the Update Manager. It has limited functionality.\n\nThe full release will search your Revision log and show the contents here."
        self.changelog.AppendText(changelog + '\n')
        self.filelist.AppendText("Update to " + branch + "\n\n The full release will show the files to be changed here.")

        #### Files works but not fully without the change log information, pulled for Dev 0.1
        #for f in files:
        #    fc = c[f]
        #    self.filelist.AppendText(str(f + '\n'))


    def verify_file(self, abs_path):
        """Returns True if file or directory exists"""
        try:
            os.stat(abs_path)
            return True
        except OSError:
            self.log.log("Invalid File or Directory: " + abs_path, ORPG_GENERAL)
            return False

    def get_packages(self, type=None):
        #Fixed and ready for Test. Can be cleaner
        self.package_list = []
        b = self.repo.branchtags()
        heads = dict.fromkeys(self.repo.heads(), 1)
        l = [((n in heads), self.repo.changelog.rev(n), n, t) for t, n in b.items()]
        l.sort()
        l.reverse()
        for ishead, r, n, t in l: self.package_list.append(t)

    def get_package(self):
        #Fixed and ready for test.
        if self.packages == None: self.get_packages()
        if self.package_list == None: return None
        return None

class Repos(wx.Panel):
    def __init__(self, parent, openrpg):
        wx.Panel.__init__(self, parent)
        self.openrpg = openrpg
        self.settings = openrpg.get_component('settings')
        self.xml = openrpg.get_component('xml')

        self.buttons = {}
        self.texts = {}

        ## Section Sizers (with frame edges and text captions)
        self.box_sizers = {}
        self.box_sizers["newrepo"] = wx.StaticBox(self, -1, "Add New Repo")
        self.box_sizers["repolist"] = wx.StaticBox(self, -1, "Current Repo List")

        ## Layout Sizers
        self.sizers = {}
        self.sizers["main"] = wx.GridBagSizer(hgap=2, vgap=2)
        self.sizers["newrepo"] = wx.StaticBoxSizer(self.box_sizers["newrepo"], wx.VERTICAL)
        self.sizers["repolist"] = wx.StaticBoxSizer(self.box_sizers["repolist"], wx.VERTICAL)

        #Build Server Sizer Layout
        self.sizers["newrepo_layout"] = wx.FlexGridSizer(rows=1, cols=2, hgap=2, vgap=1)
        reponame = wx.StaticText(self, -1, "Name:")
        self.texts["reponame"] = wx.TextCtrl(self, -1)
        repodesc = wx.StaticText(self, -1, "Description:")
        self.texts["repodesc"] = wx.TextCtrl(self, -1)
        repoadd = wx.StaticText(self, -1, "Address:")
        self.texts["repoadd"] = wx.TextCtrl(self, -1)
        addrepo = wx.Button(self, wx.ID_ADD)

        ##Put GUI Together.
        self.sizers["newrepo_layout"].Add(reponame, -1, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.ALL)
        self.sizers["newrepo_layout"].Add(self.texts["reponame"], -1, wx.EXPAND)
        self.sizers["newrepo_layout"].Add(repodesc, -1, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.ALL)
        self.sizers["newrepo_layout"].Add(self.texts["repodesc"], -1, wx.EXPAND)
        self.sizers["newrepo_layout"].Add(repoadd, -1, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.ALL)
        self.sizers["newrepo_layout"].Add(self.texts["repoadd"], -1, wx.EXPAND)
        self.sizers["newrepo_layout"].Add(addrepo, -1)
        self.sizers["newrepo_layout"].AddGrowableCol(1)
        self.sizers["newrepo"].Add(self.sizers["newrepo_layout"], -1, wx.EXPAND)

        #Repo List Layout
        self.sizers["repolist_layout"] = wx.FlexGridSizer(rows=1, cols=2, hgap=2, vgap=1)
        #addrepo = wx.Button(self, wx.ID_ADD) ## Looks bad inside the Sizer, move out!
        #self.sizers["repolist_layout"].Add(addrepo, -1)
        self.sizers["repolist_layout"].AddGrowableCol(1)
        self.sizers["repolist"].Add(self.sizers["repolist_layout"], -1, wx.EXPAND)

        """
        grid = wx.GridSizer(3, 2)

        grid.AddMany([(wx.Button(self, wx.ID_CANCEL), 0, wx.TOP | wx.LEFT, 9),
            (wx.Button(self, wx.ID_DELETE), 0, wx.TOP, 9),
            (wx.Button(self, wx.ID_SAVE), 0, wx.LEFT, 9),
            (wx.Button(self, wx.ID_EXIT)),
            (wx.Button(self, wx.ID_STOP), 0, wx.LEFT, 9),
            (wx.Button(self, wx.ID_NEW))])

        self.Bind(wx.EVT_BUTTON, self.OnQuit, id=wx.ID_EXIT)
        self.SetSizer(grid)
        self.Centre()
        self.Show(True)


    def OnQuit(self, event):
        self.Close()
        """

        #Build Main Sizer
        self.sizers["main"].Add(self.sizers["newrepo"], (0,0), flag=wx.EXPAND)
        self.sizers["main"].Add(self.sizers["repolist"], (1,0), flag=wx.EXPAND)
        self.sizers["main"].AddGrowableCol(0)
        self.sizers["main"].AddGrowableCol(1)
        #self.sizers["main"].AddGrowableRow(1)
        self.SetSizer(self.sizers["main"])
        self.SetAutoLayout(True)
        self.Fit()

class Manifest(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        self.ui = ui.ui()
        self.repo = hg.repository(self.ui, ".")
        self.c = self.repo.changectx('tip')
        self.manifest = []
        self.manifest = self.c.manifest().keys()
        self.manifest.sort()
        self.SetBackgroundColour(wx.WHITE)
        self.sizer = wx.GridBagSizer(hgap=1, vgap=1)

        self.manifestlog = wx.TextCtrl(self, wx.ID_ANY, size=(400, -1), style=wx.TE_MULTILINE | wx.TE_READONLY)

        self.sizer.Add(self.manifestlog, (0,0), flag=wx.EXPAND)

        self.sizer.AddGrowableCol(0)
        self.sizer.AddGrowableRow(0)
        self.SetSizer(self.sizer)
        self.SetAutoLayout(True)
        self.BuildManifest()


    def BuildManifest(self):
        self.manifestlog.SetValue('')
        self.manifestlog.AppendText('Currently the Manifest Log shows your files only, later you will be able to select files to ingore on update\n')
        for i in self.manifest:
            self.manifestlog.AppendText(i + '\n')

class Control(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        t = wx.StaticText(self, -1, "Here you will be able to control your branches, delete branches, \nupdate to a sepcific revision, and that type of control.", (10,60))


class updaterFrame(wx.Frame):
    def __init__(self, parent, title, openrpg):
        wx.Frame.__init__(self, None, wx.ID_ANY, title, size=(640,480), 
            style=wx.FRAME_NO_TASKBAR | wx.STAY_ON_TOP | wx.DEFAULT_FRAME_STYLE)

        self.CenterOnScreen()

        ####### Panel Stuff ######
        p = wx.Panel(self)
        nb = wx.Notebook(p)

        # create the page windows as children of the notebook
        page1 = Updater(nb, openrpg)
        page2 = Repos(nb, openrpg)
        page3 = Manifest(nb)
        page4 = Control(nb)

        # add the pages to the notebook with the label to show on the tab
        nb.AddPage(page1, "Updater")
        nb.AddPage(page2, "Repos")
        nb.AddPage(page3, "Manifest")
        nb.AddPage(page4, "Control")

        # finally, put the notebook in a sizer for the panel to manage
        # the layout
        sizer = wx.BoxSizer()
        sizer.Add(nb, 1, wx.EXPAND)
        p.SetSizer(sizer)



class updateApp(wx.App):
    def OnInit(self):
        self.open_rpg = open_rpg
        self.log = orpg.tools.orpg_log.orpgLog(orpg.dirpath.dir_struct["user"] + "runlogs/")
        self.log.setLogToConsol(False)
        self.log.log("Updater Start", ORPG_NOTE)

        #Add the initial global components of the openrpg class
        #Every class should be passed openrpg
        self.open_rpg.add_component("log", self.log)
        self.open_rpg.add_component("xml", orpg.orpg_xml)
        self.open_rpg.add_component("dir_struct", orpg.dirpath.dir_struct)
        self.validate = orpg.tools.validate.Validate()
        self.open_rpg.add_component("validate", self.validate)
        #self.settings = orpg.tools.orpg_settings.orpgSettings(self.open_rpg)
        #self.open_rpg.add_component("settings", self.settings)
        #self.settings.updateIni()
        self.updater = updaterFrame(self, "OpenRPG Update Manager Beta 0.3", self.open_rpg)
        self.updated = False
        try:
            self.updater.Show()
            self.SetTopWindow(self.updater)
            self.updater.Fit()
        except: pass

        return True

    def OnExit(self):
        #self.settings.save()
        """
        imported = ['orpg.orpgCore', 'orpg.orpg_wx', 'orpg.orpg_version', 'orpg.tools.orpg_log', 'orpg.orpg_xml', 'orpg.dirpath', 'orpg.tools.orpg_settings', 'orpg.tools.validate', 'orpg.pulldom', 'orpg.tools.NotebookCtrl', 'orpg.tools.config_update', 'orpg.systempath', 'orpg.minidom', 'orpg.dirpath.dirpath_tools', 'orpg.tools.rgbhex', 'orpg.orpg_windows']

        for name in imported:
            if name in sys.modules:
                self.log.log("Unimported " + name, ORPG_DEBUG)
                del sys.modules[name]
        """
        self.log.log("Updater Exit\n\n", ORPG_NOTE)
