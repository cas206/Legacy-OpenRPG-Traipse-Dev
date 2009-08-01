import wx
import wx.html
import webbrowser
import urllib
import zipfile
import traceback
import hashlib
import orpg.dirpath
from orpg.orpgCore import *
import orpg.orpg_version
import orpg.tools.orpg_log
import orpg.orpg_xml
import orpg.dirpath
import orpg.tools.orpg_settings
import orpg.tools.validate
from mercurial import ui, hg, commands, repo, revlog, cmdutil
dir_struct = open_rpg.get_component("dir_struct")

u = ui.ui()
r = hg.repository(u, ".")
c = r.changectx('tip')

#repo = hg.repository(ui.ui(), 'http://hg.assembla.com/traipse')
#b = []

#b = commands.branches(u, r, True)
#print b

"""
u = ui.ui()
r = hg.repository(u, ".")
l2 =[]
b = r.branchtags()
heads = dict.fromkeys(r.heads(), 1)
l = [((n in heads), r.changelog.rev(n), n, t) for t, n in b.items()]
l.sort()
l.reverse()
for ishead, r, n, t in l: l2.append(t)
print l2
"""

#print heads
#b = []
#b = c.branch()
#print c.branch()
#print c.tags()

##Process
#Pull
#Gather Changeset Info
#Display window with Branch + Changesets
#Update from Branch -Revision.




#         --------------------
#        |        |           |
#        | Change | Download  |
#        |   Log  |   List    |
#        |        |-----------|
#        |        | butons    |
#        ----------------------
# Buttons area includes, []Auto Update, <advanced>
#


class AboutHTMLWindow(wx.Panel):
    "Window used to display the About dialog box"
    # Init using the derived from class
    def __init__( self, parent, id):
        wx.Panel.__init__( self, parent, id, size=(400, -1))

    def OnLinkClicked( self, ref ):
        "Open an external browser to resolve our About box links!!!"
        href = ref.GetHref()
        webbrowser.open( href )


class updaterFrame(wx.Frame):
    def __init__(self, parent, title, openrpg):

        ### Update Manager
        self.ui = ui.ui()
        self.repo = hg.repository(u, ".")
        self.c = self.repo.changectx('tip')


        self.openrpg = openrpg
        self.parent = parent
        self.log = self.openrpg.get_component("log")
        self.log.log("Enter updaterFrame", ORPG_DEBUG)

        wx.Frame.__init__(self, None, wx.ID_ANY, title, size=(640,480), 
            style=wx.FRAME_NO_TASKBAR | wx.STAY_ON_TOP | wx.DEFAULT_FRAME_STYLE)
        self.SetBackgroundColour(wx.WHITE)
        self.CenterOnScreen()
        self.settings = openrpg.get_component('settings')
        self.xml = openrpg.get_component('xml')
        self.dir_struct = self.openrpg.get_component("dir_struct")
        self.sizer = wx.GridBagSizer(hgap=1, vgap=1)
        self.changelog = wx.TextCtrl(self, wx.ID_ANY, size=(400, -1), style=wx.TE_MULTILINE | wx.TE_READONLY)

        self.filelist = wx.TextCtrl(self, wx.ID_ANY, size=(250, 300), style=wx.TE_MULTILINE | wx.TE_READONLY)
        self.buttons = {}
        self.buttons['progress_bar'] = wx.Gauge(self, wx.ID_ANY, 100)
        self.buttons['auto_text'] = wx.StaticText(self, wx.ID_ANY, "Auto Update")
        self.buttons['auto_check'] = wx.CheckBox(self, wx.ID_ANY)
        self.buttons['advanced'] = wx.Button(self, wx.ID_ANY, "Package Select")
        self.buttons['update'] = wx.Button(self, wx.ID_ANY, "Update Now")
        self.buttons['finish'] = wx.Button(self, wx.ID_ANY, "Finish")

        self.sizer.Add(self.changelog, (0,0), span=(3,1), flag=wx.EXPAND)
        self.sizer.Add(self.filelist, (0,1), span=(1,3), flag=wx.EXPAND)

        self.sizer.Add(self.buttons['progress_bar'], (1,1), span=(1,3), flag=wx.EXPAND)
        self.sizer.Add(self.buttons['auto_text'], (2,1))
        self.sizer.Add(self.buttons['auto_check'], (2,2), flag=wx.EXPAND)
        self.sizer.Add(self.buttons['advanced'], (2,3), flag=wx.EXPAND)
        self.sizer.Add(self.buttons['update'], (3,1), flag=wx.EXPAND)
        self.sizer.Add(self.buttons['finish'], (3,2), span=(1,2), flag=wx.EXPAND)
        self.sizer.AddGrowableCol(0)
        self.sizer.AddGrowableRow(0)
        self.SetSizer(self.sizer)
        self.SetAutoLayout(True)
        self.initPrefs()



        if self.package == None: wx.CallAfter(self.Advanced)
        #if self.autoupdate == "On": self.buttons['auto_check'].SetValue(True)

        ## Event Handlers
        self.Bind(wx.EVT_BUTTON, self.Update, self.buttons['update'])
        self.Bind(wx.EVT_BUTTON, self.Finish, self.buttons['finish'])
        self.Bind(wx.EVT_BUTTON, self.Advanced, self.buttons['advanced'])
        self.Bind(wx.EVT_CHECKBOX, self.ToggleAutoUpdate, self.buttons['auto_check'])

        try:  self.check()
        except:
            self.buttons['finish'].Show()
            self.buttons['update'].Show()

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

    def check(self):
        self.buttons['finish'].Hide()
        self.buttons['update'].Hide()
        self.updatelist = []
        wx.CallAfter(self.showFinish)
        #Do the MD5 Check & DL
        files = self.package._get_childNodes()
        self.buttons['progress_bar'].SetRange(len(files))
        try:
            i = 1
            for file in files:
                checksum = md5.new()
                self.buttons['progress_bar'].SetValue(i)
                if file._get_tagName() == 'file':
                    file_name = file.getAttribute("name")
                    file_url = file.getAttribute("url").replace(' ', '%20') + '/' + file_name
                    file_path = file.getAttribute("path")
                    read_type = file.getAttribute("read_type")
                    file_checksum = file.getAttribute("checksum")
                    full_path = self.dir_struct["home"].replace("\\","/") + file_path + os.sep + file_name
                    full_path = full_path.replace("/", os.sep)

                    if self.verify_file(full_path):
                        if read_type == 'rb': f = open(full_path, "rb")
                        else: f = open(full_path, "r")
                        data = f.read()
                        f.close()
                        checksum.update(data)
                        if(checksum.hexdigest() != file_checksum):
                            self.log.log("Read Type: " + read_type, ORPG_DEBUG)
                            self.log.log("Filename: " + file_name + "\n\tLocal Checksum:\t" + checksum.hexdigest() + "\n\tWeb Checksum:\t" + file_checksum, ORPG_DEBUG)
                            self.updatelist.append((file_url, full_path, file_name, read_type))
                    else: self.updatelist.append((file_url, full_path, file_name, read_type))
                elif file._get_tagName() == 'dir':
                    dir_path = file.getAttribute("path")
                    full_path = self.dir_struct['home'] + dir_path
                    if not self.verify_file(full_path):
                        self.filelist.SetValue(self.filelist.GetValue() + "Creating Directory " + dir_path + " ...\n")
                        os.makedirs(full_path)
                i += 1
            if len(self.updatelist) == 0:
                wx.CallAfter(self.Finish)
                return False
        except: #error handing update check. Likely no internet connection. skip update check
            self.log.log("[WARNING] Automatic update check failed.\n" + traceback.format_exc(), ORPG_GENERAL)
            self.filelist.SetValue("[WARNING] Automatic update check failed.\n" + traceback.format_exc())
            return False
        dmsg = "A newer version is available.\n"
        for file in self.updatelist: dmsg += file[2] + " is out of date\n"
        dmsg += "Would you like to update Now?"
        self.filelist.SetValue(dmsg)
        data = urllib.urlretrieve(self.package.getAttribute("notes").replace(' ', '%20'))
        file = open(data[0])
        changelog = file.read()
        file.close()
        self.changelog.SetPage(changelog)

        if self.autoupdate == "Off": self.buttons['update'].Show()
        if self.autoupdate == "On": wx.CallAfter(self.Update)
        return True

    def Update(self, evt=None):

        hg.clean(self.repo, self.current)

        """old code
        self.buttons['finish'].Hide()
        self.buttons['update'].Hide()
        self.buttons['advanced'].Hide()
        self.buttons['progress_bar'].SetRange(len(self.updatelist))
        self.filelist.SetValue("")
        self.log.log("Starting Update Proccess!", ORPG_DEBUG)
        i = 1
        for file in self.updatelist:
            self.downloadFile(file[0], file[1], file[2], i, file[3])
            i += 1
        self.Updated = True
        self.parent.updated = True
        wx.CallAfter(self.showFinish)
        if self.autoupdate == 'On': wx.CallAfter(self.Finish)
        """

    def downloadFile(self, file_url, abs_path, file_name, i, read_type):
        self.buttons['progress_bar'].SetValue(i)
        self.buttons['finish'].Hide()
        self.log.log("Downloading " + file_name, ORPG_DEBUG)
        try:
            self.filelist.SetValue(self.filelist.GetValue() + "Downloading " + file_name + " ...\n")
            wx.Yield()
            checksum = md5.new()
            data = urllib.urlretrieve("http://openrpg.digitalxero.net/" + file_url)

            if read_type == 'rb': file = open(data[0], "rb")
            else: file = open(data[0], "r")

            file_data = file.read()
            file.close()
            checksum.update(file_data)
            self.log.log("Read Type: " + read_type, ORPG_DEBUG)
            self.log.log("Downloaded filename: " + file_name + "\n\tDownloaded Checksum:\t" + checksum.hexdigest(), ORPG_DEBUG)

            if read_type == 'rb': file = open(abs_path, 'wb')
            else: file = open(abs_path, 'w')
            file.write(file_data)
            file.close()

            #Debug Stuff
            checksum = md5.new()
            f = open(abs_path, read_type)
            file_data = f.read()
            f.close()
            checksum.update(file_data)
            self.log.log("Written filename: " + file_name + "\n\tWritten Checksum:\t" + checksum.hexdigest(), ORPG_DEBUG)
        except:
            self.log.log("Failed to download file: " + abs_path, ORPG_GENERAL)
            self.log.log(traceback.format_exc(), ORPG_GENERAL)

    def Finish(self, evt=None):
        #self.settings.updateIni()
        self.Finished = True
        self.Destroy()

    def Advanced(self, evt=None):
        dlg = wx.Dialog(self, wx.ID_ANY, "Package Selector", style=wx.DEFAULT_DIALOG_STYLE)
        icon = None
        if wx.Platform == '__WXMSW__': icon = wx.Icon(self.dir_struct["icon"]+'d20.ico', wx.BITMAP_TYPE_ICO)
        else: icon = wx.Icon(self.dir_struct["icon"]+"d20.xpm", wx.BITMAP_TYPE_XPM )
        if icon != None: dlg.SetIcon(icon)

        dlgsizer = wx.GridBagSizer(hgap=1, vgap=1)
        Yes = wx.Button( dlg, wx.ID_OK, "Ok" )
        Yes.SetDefault()
        rgroup = wx.RadioButton(dlg, wx.ID_ANY, "group_start", style=wx.RB_GROUP)
        rgroup.Hide()

        if self.packages == None: self.get_packages()
        if self.package_list == None: return


        types = self.package_list
        row=0
        col=0
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
            u = ui.ui()
            r = hg.repository(u, ".")
            #r = hg.islocal()
            c = r.changectx('tip')
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

            self.filelist.SetValue('')
            self.filelist.AppendText("Files that will change\n\n")

            self.changelog.SetValue('')
            changelog = "This is Dev Build 0.1 of the Update Manager. It has limited functionality.\n\nThe full release will search your Revision log and show the contents here."
            self.changelog.AppendText(changelog + '\n')
            self.filelist.AppendText("Update to " + self.current + "\n\n The full release will show the files to be changed here.")

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

    def is_up2date(self, version, build):
        if self.package == None:
            self.SelectPackage == True
            return False
        vg = (version > self.package.getAttribute("version"))
        ve = (version == self.package.getAttribute("version"))
        b = (build >= self.package.getAttribute("build"))

        if vg: return True
        if (not ve) or (not b): return False
        return True

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
        self.updater = updaterFrame(self, "OpenRPG Update Manager Beta 0.1", self.open_rpg)
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
