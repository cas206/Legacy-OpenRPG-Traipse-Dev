import sys
import os
import errno
from orpg.orpg_wx import *

if WXLOADED:
    class tmpApp(wx.App):
        def OnInit(self):
            return True


#-------------------------------------------------------
# void load_paths( dir_struct_reference )
# moved structure loading from dirpath.py by Snowdog 3-8-05
#-------------------------------------------------------
def load_paths(dir_struct, root_dir):
    dir_struct["home"] = root_dir + os.sep
    dir_struct["core"] = dir_struct["home"] + "orpg"+ os.sep
    dir_struct["data"] = dir_struct["home"] + "data"+ os.sep
    dir_struct["d20"] = dir_struct["data"] + "d20" + os.sep
    dir_struct["dnd3e"] = dir_struct["data"] + "dnd3e" + os.sep
    dir_struct["dnd35"] = dir_struct["data"] + "dnd35" + os.sep
    dir_struct["SWd20"] = dir_struct["data"] + "SWd20" + os.sep
    dir_struct["icon"] = dir_struct["home"] + "images" + os.sep
    dir_struct["template"] = dir_struct["core"] + "templates" + os.sep
    dir_struct["plugins"] = dir_struct["home"] + "plugins" + os.sep
    dir_struct["nodes"] = dir_struct["template"] + "nodes" + os.sep
    dir_struct["rollers"] = dir_struct["core"] + "dieroller" + os.sep + "rollers" + os.sep


    _userbase_dir = _userbase_dir = os.environ['OPENRPG_BASE']
    _user_dir = _userbase_dir + os.sep + "myfiles" + os.sep


    try:
        os.makedirs(_user_dir)
        os.makedirs(_user_dir + "runlogs" + os.sep);
        os.makedirs(_user_dir + "logs" + os.sep);
        os.makedirs(_user_dir + "webfiles" + os.sep);
    except OSError, e:
        if e.errno != errno.EEXIST:
            raise

    dir_struct["user"] = _user_dir

    dir_struct["logs"] = dir_struct["user"] + "logs" + os.sep



#-------------------------------------------------------
# int verify_home_path( directory_name )
# added by Snowdog 3-8-05
# updated with bailout code. Snowdog 7-25-05
#-------------------------------------------------------
def verify_home_path( path ):
    """checks for key ORPG files in the openrpg tree
       and askes for user intervention if their is a problem"""

    try:
        #verify that the root dir (as supplied) exists
        if not verify_file(path): return 0

        #These checks require that 'path' have a separator at the end.
        #Check and temporarily add one if needed
        if (path[(len(path)-len(os.sep)):] != os.sep):
            path = path + os.sep

        # These files should always exist at the root orpg dir
        check_files = ["orpg","data","images"]
        for n in range(len(check_files)):
            if not verify_file(path + check_files[n]): return 0

    except:
        # an error occured while verifying the directory structure
        # bail out with error signal
        return 0

    #all files and directories exist.
    return 1



#-------------------------------------------------------
# int verify_file( absolute_path )
# added by Snowdog 3-8-05
#-------------------------------------------------------
def verify_file(abs_path):
    """Returns True if file or directory exists"""
    try:
        os.stat(abs_path)
        return 1
    except OSError:
        #this exception signifies the file or dir doesn't exist
        return 0


#-------------------------------------------------------
# pathname get_user_help()
# added by Snowdog 3-8-05
# bug fix (SF #1242456) and updated with bailout code. Snowdog 7-25-05
#-------------------------------------------------------
def get_user_located_root():
    """Notify the user of directory problems
    and show directory selection dialog """

    if WXLOADED:
        app = tmpApp(0)
        app.MainLoop()

        dir = None

        try:
            msg = "OpenRPG cannot locate critical files.\nPlease locate the /System/ directory in the following window"
            alert= wx.MessageDialog(None,msg,"Warning",wx.OK|wx.ICON_ERROR)
            alert.Show()
            if alert.ShowModal() == wx.OK:
                alert.Destroy()
            dlg = wx.DirDialog(None, "Locate the openrpg1 directory:",style=wx.DD_DEFAULT_STYLE)
            if dlg.ShowModal() == wx.ID_OK:
                dir = dlg.GetPath()
            dlg.Destroy()
            app.Destroy()
            return dir
        except Exception, e:
            print e
            print "OpenRPG encountered a problem while attempting to load file dialog to locate the OpenRPG root directory."
            print "please delete the files ./openrpg/orpg/dirpath/aproot.py and ./openrpg/orpg/dirpath/aproot.pyc and try again."
    else:
        dir = raw_input("Enter the full path to your openrpg folder:  ")
        return dir

