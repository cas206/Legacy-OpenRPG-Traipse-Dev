import wx
import manifest
import orpg.dirpath
from orpg.orpgCore import *
import orpg.orpg_version
import orpg.tools.orpg_log
import orpg.orpg_xml
import orpg.dirpath
import upmana.validate
import tempfile
import shutil
from mercurial import ui, hg, commands, repo, revlog, cmdutil, util


class Updater(wx.Panel):
    def __init__(self, parent, open_rpg, manifest):
        wx.Panel.__init__(self, parent)

        ### Update Manager
        self.ui = ui.ui()
        self.repo = hg.repository(self.ui, ".")
        self.c = self.repo.changectx('tip')
        self.manifest = manifest
        self.xml = open_rpg.get_component('xml')
        self.dir_struct = open_rpg.get_component("dir_struct")
        self.parent = parent
        self.log = open_rpg.get_component("log")
        self.log.log("Enter updaterFrame", ORPG_DEBUG)
        self.SetBackgroundColour(wx.WHITE)
        self.sizer = wx.GridBagSizer(hgap=1, vgap=1)
        self.changelog = wx.TextCtrl(self, wx.ID_ANY, size=(325, -1), style=wx.TE_MULTILINE | wx.TE_READONLY)
        self.filelist = wx.TextCtrl(self, wx.ID_ANY, size=(275, 300), style=wx.TE_MULTILINE | wx.TE_READONLY)
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
        self.buttons['finish'].Disable()
        self.sizer.AddGrowableCol(0)
        self.sizer.AddGrowableRow(0)
        self.SetSizer(self.sizer)
        self.SetAutoLayout(True)
        self.get_package

        self.current = self.repo.dirstate.branch()
        self.BranchInfo(self.current)

        if self.manifest.GetString("updatemana", "no_update", "") == 'on': self.buttons['no_check'].SetValue(True)
        else: self.buttons['no_check'].SetValue(False)
        if self.manifest.GetString("updatemana", "auto_update", "") == 'on': self.buttons['auto_check'].SetValue(True)
        else: self.buttons['auto_check'].SetValue(False)

        ## Event Handlers
        self.Bind(wx.EVT_BUTTON, self.Update, self.buttons['update'])
        self.Bind(wx.EVT_BUTTON, self.Finish, self.buttons['finish'])
        self.Bind(wx.EVT_BUTTON, self.ChooseBranch, self.buttons['advanced'])
        self.Bind(wx.EVT_CHECKBOX, self.ToggleAutoUpdate, self.buttons['auto_check'])
        self.Bind(wx.EVT_CHECKBOX, self.ToggleNoUpdate, self.buttons['no_check'])

    def ToggleAutoUpdate(self, event):
        if self.buttons['auto_check'].GetValue() == True:
            if self.buttons['no_check'].GetValue() == True: 
                self.buttons['no_check'].SetValue(False)
                self.manifest.SetString("updatemana", "no_update", "off")
            self.manifest.SetString("updatemana", "auto_update", "on")
        else: self.manifest.SetString("updatemana", "auto_update", "off")

    def ToggleNoUpdate(self, event):
        if self.buttons['no_check'].GetValue() == True:
            if self.buttons['auto_check'].GetValue() == True: 
                self.buttons['auto_check'].SetValue(False)
                self.manifest.SetString("updatemana", "auto_update", "off")
            self.manifest.SetString("updatemana", "no_update", "on")
        else: self.manifest.SetString("updatemana", "no_update", "off")

    def Update(self, evt=None):
        self.ui = ui.ui()
        self.repo = hg.repository(self.ui, ".")
        self.c = self.repo.changectx('tip')

        filename = 'ignorelist.txt'
        self.filename = orpg.dirpath.dir_struct["home"] + 'upmana' + os.sep + filename
        upmana.validate.Validate(orpg.dirpath.dir_struct["home"] + 'upmana' + os.sep).config_file(filename, "default_ignorelist.txt")
        self.mana = self.LoadDoc()
        for ignore in self.ignorelist:
            shutil.copy(ignore, orpg.dirpath.dir_struct["home"] + 'upmana' + os.sep + 'tmp' + os.sep +ignore.split('/')[len(ignore.split('/')) - 1])
        hg.clean(self.repo, self.current)
        for ignore in self.ignorelist:
            shutil.copyfile(orpg.dirpath.dir_struct["home"] + 'upmana' + os.sep + 'tmp' + os.sep + ignore.split('/')[len(ignore.split('/')) - 1], ignore)
            os.remove(orpg.dirpath.dir_struct["home"] + 'upmana' + os.sep + 'tmp' + os.sep + ignore.split('/')[len(ignore.split('/')) - 1])

    def LoadDoc(self):
        ignore = open(self.filename)
        self.ignorelist = []
        for i in ignore: self.ignorelist.append(str(i [:len(i)-1]))
        manifest = ignore.readlines()
        ignore.close()

    def Finish(self, evt=None):
        try: self.parent.Destroy()
        except:
            print 'Fail'; exit()

    def ChooseBranch(self, evt=None):
        dlg = wx.Dialog(self, wx.ID_ANY, "Package Selector", style=wx.DEFAULT_DIALOG_STYLE)
        if wx.Platform == '__WXMSW__': icon = wx.Icon(self.dir_struct["icon"]+'d20.ico', wx.BITMAP_TYPE_ICO)
        else: icon = wx.Icon(self.dir_struct["icon"]+"d20.xpm", wx.BITMAP_TYPE_XPM )
        dlg.SetIcon(icon)

        self.ui = ui.ui()
        self.repo = hg.repository(self.ui, ".")
        self.c = self.repo.changectx('tip')

        dlgsizer = wx.GridBagSizer(hgap=1, vgap=1)
        Yes = wx.Button( dlg, wx.ID_OK, "Ok" )
        Yes.SetDefault()
        rgroup = wx.RadioButton(dlg, wx.ID_ANY, "group_start", style=wx.RB_GROUP)
        rgroup.Hide()

        self.get_packages()
        if self.package_list == None: return
        types = self.package_list
        row=0; col=0
        self.current = self.repo.dirstate.branch()
        self.package_type = self.current
        self.btnlist = {}; self.btn = {}
        self.id = 1

        for t in types:
            self.btnName = str(t)
            self.btn[self.id] = wx.RadioButton(dlg, wx.ID_ANY, str(t), name=self.btnName)
            if self.btnName == self.current: self.btn[self.id].SetValue(True)
            self.btnlist[self.id] = self.btnName
            dlgsizer.Add(self.btn[self.id], (row, col))
            col += 1; self.id += 1
            if col == 3: row += 1; col = 0

        dlgsizer.Add(Yes, (row+1,col/2))
        dlgsizer.AddGrowableCol(0)
        dlgsizer.AddGrowableRow(0)
        dlg.SetAutoLayout( True )
        dlg.SetSizer( dlgsizer )
        dlgsizer.Fit( dlg )
        dlg.Centre()
        dlg.Bind(wx.EVT_RADIOBUTTON, self.PackageSet)
        if dlg.ShowModal(): dlg.Destroy()

    def PackageSet(self, event):
        for btn in self.btn:
            if self.btn[btn].GetValue() == True: self.current = self.btnlist[btn]

        branches = self.repo.branchtags()
        heads = dict.fromkeys(self.repo.heads(), 1)
        l = [((n in heads), self.repo.changelog.rev(n), n, t) for t, n in branches.items()]

        if self.current != type:
            heads = dict.fromkeys(self.repo.heads(), self.repo.branchtags())
            branches = dict.copy(self.repo.branchtags())
            self.BranchInfo(self.current)

    def BranchInfo(self, branch):
        cs = self.repo.changectx( self.current ).changeset()
        rev = self.repo.changelog.rev(self.repo.branchtags()[self.current]) #Current revision number. Use in Controls
        self.changelog.SetValue('')
        changelog = cs[4]
        self.changelog.AppendText(changelog + '\n')
        self.filelist.SetValue('')
        self.filelist.AppendText("Currently selected branch: " + branch + "\n\nAuthor: "+cs[1]+"\n\nFiles Modified (in update): \n")
        for f in cs[3]: self.filelist.AppendText(f+"\n")

    def get_packages(self, type=None):
        #Fixed and ready for Test. Can be cleaner
        self.package_list = []
        b = self.repo.branchtags()
        heads = dict.fromkeys(self.repo.heads(), 1) #The code below looks superfluous but there is good info inside
        l = [((n in heads), self.repo.changelog.rev(n), n, t) for t, n in b.items()]
        l.sort()
        l.reverse()
        for ishead, r, n, t in l: self.package_list.append(t)

    def get_package(self):
        self.get_packages()
        if self.package_list == None: return None
        return None

class Repos(wx.Panel):
    def __init__(self, parent, openrpg, manifest):
        wx.Panel.__init__(self, parent)

        ### Update Manager
        self.ui = ui.ui()
        self.r = hg.repository(self.ui, ".")
        self.c = self.r.changectx('tip')

        #mainpanel = self
        self.openrpg = openrpg
        self.manifest = manifest
        self.buttons = {}
        self.texts = {}

        ## Section Sizers (with frame edges and text captions)
        self.box_sizers = {}
        self.box_sizers["newbutton"] = wx.StaticBox(self, -1)

        ## Layout Sizers
        self.sizers = {}
        self.sizers["main"] = wx.GridBagSizer(hgap=2, vgap=2)
        self.sizers["button"] = wx.GridBagSizer(hgap=2, vgap=2)

        #Button Layout
        self.sizers["newbutton"] = wx.StaticBoxSizer(self.box_sizers["newbutton"], wx.VERTICAL)
        self.sizers["newrepo_layout"] = wx.FlexGridSizer(rows=1, cols=2, hgap=2, vgap=5)
        empty = wx.StaticText(self, -1, "")
        reponame = wx.StaticText(self, -1, "Name:")
        self.texts["reponame"] = wx.TextCtrl(self, -1, '')
        self.buttons['addrepo'] = wx.Button(self, wx.ID_NEW)

        ##Build Button
        self.sizers["newrepo_layout"].Add(self.buttons['addrepo'], -1, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.ALL)
        self.sizers["newrepo_layout"].Add(empty, -1)
        self.sizers["newrepo_layout"].Add(reponame, -1, wx.ALIGN_CENTER|wx.ALIGN_CENTER_VERTICAL|wx.ALL)
        self.sizers["newrepo_layout"].Add(self.texts["reponame"], -1, wx.EXPAND)
        self.sizers["newrepo_layout"].AddGrowableCol(1)
        self.sizers["newbutton"].Add(self.sizers["newrepo_layout"], -1, wx.EXPAND)

        #Repo List Panel
        self.repopanel = wx.ScrolledWindow(self)
        self.repopanel.SetScrollbars(20,20,55,40)
        self.repopanel.Scroll(50,10)
        self.box_sizers["repolist"] = wx.StaticBox(self.repopanel, -1, "Current Repo List")
        self.sizers["repolist"] = wx.StaticBoxSizer(self.box_sizers["repolist"], wx.VERTICAL)
        self.sizers["repo"] = wx.GridBagSizer(hgap=2, vgap=2)
        self.sizers["repolist_layout"] = wx.FlexGridSizer(rows=1, cols=1, hgap=2, vgap=5)
        self.manifest = manifest

        self.NewRepoList(None)
        self.BuildRepoList(None)

        self.sizers["repolist_layout"].AddGrowableCol(0)
        self.sizers["repolist"].Add(self.sizers["repolist_layout"], -1, wx.EXPAND)
        self.sizers["repo"].Add(self.sizers["repolist"], (0,0), flag=wx.EXPAND)
        self.sizers["repo"].AddGrowableCol(0)
        self.sizers['repo'].AddGrowableRow(0)
        self.sizers['repo'].AddGrowableRow(1)
        self.repopanel.SetSizer(self.sizers['repo'])
        self.repopanel.SetAutoLayout(True)

        #Build Main Sizer
        self.sizers["main"].Add(self.sizers["newbutton"], (0,0), flag=wx.EXPAND)
        self.sizers["main"].Add(self.repopanel, (1,0), flag=wx.EXPAND)
        self.sizers["main"].AddGrowableCol(0)
        self.sizers["main"].AddGrowableCol(1)
        self.sizers["main"].AddGrowableRow(1)
        self.SetSizer(self.sizers["main"])
        self.SetAutoLayout(True)
        self.Fit()
        self.Bind(wx.EVT_BUTTON, self.AddRepo, self.buttons['addrepo'])

    def NewRepoList(self, event):
        self.id = -1; self.box = {}; self.box_name= {}; self.main = {}; self.container = {}; self.layout = {}
        self.name = {}; self.url = {}; self.url_list = {}; self.pull = {}; self.uri = {}; self.delete = {}
        self.defaultcheck = {}; self.default = {}; self.repotrac = {}
        self.pull_list = {}; self.delete_list = {}; self.defchecklist = {}

    def BuildRepoList(self, event):
        self.repolist = self.manifest.GetList('UpdateManifest', 'repolist', '')
        try: self.repolist = self.repo
        except: pass

        #wx.Yeild()  For future refrence.

        for repo in self.repolist:
            self.id += 1
            #Build Constructs
            self.box[self.id] = wx.StaticBox(self.repopanel, -1, str(repo))
            self.main[self.id] = wx.GridBagSizer(hgap=2, vgap=2)
            self.container[self.id] = wx.StaticBoxSizer(self.box[self.id], wx.VERTICAL)
            self.layout[self.id] = wx.FlexGridSizer(rows=1, cols=4, hgap=2, vgap=5)
            self.name[self.id] = wx.StaticText(self.repopanel, -1, 'URL')
            self.uri[self.id] = self.manifest.GetString('updaterepo', repo, '')
            self.url[self.id] = wx.TextCtrl(self.repopanel, -1, self.uri[self.id])
            self.pull[self.id] = wx.Button(self.repopanel, wx.ID_REFRESH)
            self.delete[self.id] = wx.Button(self.repopanel, wx.ID_DELETE)
            self.delete_list[self.delete[self.id]] = self.id
            self.defaultcheck[self.id] = wx.CheckBox(self.repopanel, -1)
            self.default[self.id] = wx.StaticText(self.repopanel, -1, 'Default')
            #Build Retraceables
            self.box_name[self.id] = str(repo)
            self.pull_list[self.pull[self.id]] = self.id
            self.defchecklist[self.defaultcheck[self.id]] = self.id
            #Build Layout
            self.layout[self.id].Add(self.name[self.id], -1, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.ALL)
            self.layout[self.id].Add(self.url[self.id], -1, wx.EXPAND)
            self.layout[self.id].Add(self.pull[self.id], -1, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL|wx.ALL)
            self.layout[self.id].Add(self.delete[self.id], -1, wx.EXPAND)
            self.layout[self.id].Add(self.defaultcheck[self.id], -1, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL|wx.ALL)
            self.layout[self.id].Add(self.default[self.id], -1, wx.EXPAND)
            self.layout[self.id].AddGrowableCol(1)
            self.container[self.id].Add(self.layout[self.id], -1, wx.EXPAND)
            #Button Events
            self.Bind(wx.EVT_BUTTON, self.RefreshRepo, self.pull[self.id])
            self.Bind(wx.EVT_BUTTON, self.DelRepo, self.delete[self.id])
            self.Bind(wx.EVT_CHECKBOX, self.SetDefault, self.defaultcheck[self.id])
            self.sizers["repolist_layout"].Insert(0, self.container[self.id], -1, wx.EXPAND)
            self.sizers['repolist_layout'].Layout()

        #Set Default Repo Button
        capture = self.manifest.GetString('updaterepo', 'default', '')
        if capture != '':
            for caught in self.uri:
                if capture == self.uri[caught]: self.id = caught; pass
                else: continue
            self.defaultcheck[self.id].SetValue(True)

    def AddRepo(self, event):
        repo = self.texts['reponame'].GetValue(); repo = repo.replace(' ', '_'); repo = 'repo-' + repo
        self.manifest.SetString('updaterepo', repo, ''); self.repo = repo.split(',')
        repolist = self.manifest.GetList('UpdateManifest', 'repolist', '')
        if repolist == '': pass
        else: repolist = repolist + self.repo
        self.manifest.SetList('UpdateManifest', 'repolist', repolist)
        self.BuildRepoList(None)

    def DelRepo(self, event):
        self.id = self.delete_list[event.GetEventObject()]
        self.sizers["repolist_layout"].Hide(self.container[self.id])
        try: del self.box_name[self.id]
        except: pass
        self.manifest.SetList('UpdateManifest', 'repolist', list(self.box_name.values()))
        self.sizers['repolist_layout'].Layout()

    def RefreshRepo(self, event):
        self.id = self.pull_list[event.GetEventObject()]
        self.manifest.SetString('updaterepo', str(self.box_name[self.id]), self.url[self.id].GetValue())
        try: commands.pull(self.ui, self.r, self.url[self.id].GetValue(), rev='', update=False, force=True)
        except: pass

    def SetDefault(self, event):
        self.id = self.defchecklist[event.GetEventObject()]
        self.manifest.SetString('updaterepo', 'default', self.uri[self.id])
        for all in self.defaultcheck:
            self.defaultcheck[all].SetValue(False)
        self.defaultcheck[self.id].SetValue(True)

class Manifest(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        self.ui = ui.ui()
        self.repo = hg.repository(self.ui, ".")
        self.c = self.repo.changectx('tip')
        self.manifestlist = []
        self.manifestlist = self.c.manifest().keys()
        for mana in self.manifestlist: mana = os.sep + 'orpg' + os.sep + mana
        self.manifestlist.sort()
        self.SetBackgroundColour(wx.WHITE)
        self.sizer = wx.GridBagSizer(hgap=1, vgap=1)
        self.manifestlog = wx.CheckListBox( self, -1, wx.DefaultPosition, wx.DefaultSize, self.manifestlist, 
            wx.LC_REPORT|wx.SUNKEN_BORDER|wx.EXPAND|wx.LC_HRULES)
        filename = 'ignorelist.txt'
        self.filename = orpg.dirpath.dir_struct["home"] + 'upmana' + os.sep + filename
        upmana.validate.Validate(orpg.dirpath.dir_struct["home"] + 'upmana' + os.sep).config_file(filename, "default_ignorelist.txt")
        self.mana = self.LoadDoc()
        self.manifestlog.Bind(wx.EVT_CHECKLISTBOX, self.GetChecked)
        self.sizer.Add(self.manifestlog, (0,0), flag=wx.EXPAND)
        self.sizer.AddGrowableCol(0)
        self.sizer.AddGrowableRow(0)
        self.SetSizer(self.sizer)
        self.SetAutoLayout(True)

    def GetChecked(self, event):
        self.mana = []
        for manifest in self.manifestlog.GetChecked(): self.mana.append(self.manifestlist[manifest])
        self.SaveDoc()

    def SaveDoc(self):
        f = open(self.filename, "w")
        for mana in self.mana: f.write(mana+'\n')
        f.close()

    def LoadDoc(self):
        ignore = open(self.filename)
        ignorelist = []
        for i in ignore: ignorelist.append(str(i [:len(i)-1]))
        for i in ignorelist: #Adds previously ignored files to manifestlistlog if they are not in changesets.
            if self.c.manifest().has_key(i): continue
            else: self.manifestlist.append(i); self.manifestlist.sort()
        self.manifestlog = wx.CheckListBox( self, -1, wx.DefaultPosition, wx.DefaultSize, self.manifestlist, 
            wx.LC_REPORT|wx.SUNKEN_BORDER|wx.EXPAND|wx.LC_HRULES)
        self.manifestlog.SetCheckedStrings(ignorelist)
        manifest = ignore.readlines()
        ignore.close()

class Control(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)


class updaterFrame(wx.Frame):
    def __init__(self, parent, title, openrpg, manifest, main):
        self.dir_struct = open_rpg.get_component("dir_struct")

        wx.Frame.__init__(self, None, wx.ID_ANY, title, size=(600,480), style=wx.DEFAULT_FRAME_STYLE)
        if wx.Platform == '__WXMSW__': icon = wx.Icon(self.dir_struct["icon"]+'d20.ico', wx.BITMAP_TYPE_ICO)
        else: icon = wx.Icon(self.dir_struct["icon"]+"d20.xpm", wx.BITMAP_TYPE_XPM )
        self.SetIcon(icon)

        self.CenterOnScreen()
        self.main = main
        ####### Panel Stuff ######
        p = wx.Panel(self)
        nb = wx.Notebook(p)

        # create the page windows as children of the notebook
        page1 = Updater(nb, openrpg, manifest)
        page2 = Repos(nb, openrpg, manifest)
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
        self.Bind(wx.EVT_CLOSE, self.OnClose)

    def OnClose(self, event):
        if self.main == False: self.Destroy()
        if self.main == True: self.Hide()

class updateApp(wx.App):
    def OnInit(self):
        self.open_rpg = open_rpg
        self.main = False
        self.log = orpg.tools.orpg_log.orpgLog(orpg.dirpath.dir_struct["user"] + "runlogs/")
        self.log.setLogToConsol(False)
        self.log.log("Updater Start", ORPG_NOTE)
        self.manifest = manifest.ManifestChanges()
        self.open_rpg.add_component("log", self.log)
        self.open_rpg.add_component("xml", orpg.orpg_xml)
        self.open_rpg.add_component("dir_struct", orpg.dirpath.dir_struct)
        self.validate = upmana.validate.Validate()
        self.open_rpg.add_component("validate", self.validate)
        self.updater = updaterFrame(self, "OpenRPG Update Manager 0.7.2 (open beta)", self.open_rpg, self.manifest, self.main)
        if self.manifest.GetString("updatemana", "auto_update", "") == 'on' and self.main == False:
            self.AutoUpdate(); self.OnExit()
        else: pass
        if self.manifest.GetString('updatemana', 'no_update', '') == 'on' and self.main == False: 
            self.OnExit()
        else: pass
        try:
            self.updater.Show()
            self.updater.Fit()
        except: pass
        return True

    def AutoUpdate(self):
        self.ui = ui.ui()
        self.repo = hg.repository(self.ui, ".")
        self.c = self.repo.changectx('tip')
        self.current = self.repo.dirstate.branch()

        capture = self.manifest.GetString('updaterepo', 'default', '')
        if capture != '':
            commands.pull(self.ui, self.repo, capture, rev='', update=False, force=True)
            filename = 'ignorelist.txt'
            self.filename = orpg.dirpath.dir_struct["home"] + 'upmana' + os.sep + filename
            upmana.validate.Validate(orpg.dirpath.dir_struct["home"] + 'upmana' + os.sep).config_file(filename, "default_ignorelist.txt")
            self.mana = self.LoadDoc()
            for ignore in self.ignorelist:
                shutil.copy(ignore, orpg.dirpath.dir_struct["home"] + 'upmana' + os.sep + 'tmp' + os.sep +ignore.split('/')[len(ignore.split('/')) - 1])
            hg.clean(self.repo, self.current)
            for ignore in self.ignorelist:
                print ignore.split('/')[len(ignore.split('/')) - 1]
                shutil.copyfile(orpg.dirpath.dir_struct["home"] + 'upmana' + os.sep + 'tmp' + os.sep + ignore.split('/')[len(ignore.split('/')) - 1], ignore)
                os.remove(orpg.dirpath.dir_struct["home"] + 'upmana' + os.sep + 'tmp' + os.sep + ignore.split('/')[len(ignore.split('/')) - 1])
        else: print 'No default repository set, skipping Auto Update!'

    def LoadDoc(self):
        ignore = open(self.filename)
        self.ignorelist = []
        for i in ignore: self.ignorelist.append(str(i [:len(i)-1]))
        manifest = ignore.readlines()
        ignore.close()

    def OnExit(self):
        imported = ['manifest', 'orpg.dirpath', 'orpg.orpgCore', 'orpg.orpg_version', 'orpg.tools.orpg_log', 'orpg.tools.orpg_log', 'orpg.orpg_xml', 'orpg.dirpath', 'orpg.dirpath', 'upmana.validate', 'mercurial.ui', 'mercurial.hg', 'mercurial.commands', 'mercurial.repo', 'mercurial.revlog', 'mercurial.cmdutil', 'shutil']
        for name in imported:
            if name in sys.modules: del sys.modules[name]

        try: self.updater.Destroy()
        except: pass
