# Old dirpath.py replaced with new dirpath 'package/module' to allow dynamic
# checking on directory structure at dirpath import without requiring alteration
# of almost every openrpg1 python file
#
# This module is functionally identical to the dirpath.py file it replaces.
# All directory locations are now handled by the load_paths() function
# in the dirpath_tools.py file  -- Snowdog 3-8-05

# CHANGE LOG
# -----------------------------
# * Reworked path verification process to attempt to fall back on the
#   current working directory if approot fails to verify before
#   asking the user to locate the root directory -- Snowdog 12-20-05
# -----------------------------
# * Removed reference to approot. It was a superflous creation that carried an object
#   that dirpath_tools already creates. It wasted system resources by creating a files
#   and by referencing a file to fill an object that was already created. -- SirEbral 07-19-09

import sys
import os
from dirpath_tools import *

root_dir = None

t = __file__.split(os.sep)
if len(t) > 2:
    root_dir = os.sep.join(t[:-3])
else:
    root_dir = os.getcwd()   #default ORPG root dir

dir_struct = {}

if not verify_home_path(root_dir):
    root_dir = os.getcwd()
    if not verify_home_path(root_dir):
        root_dir = get_user_located_root()
        while not verify_home_path(root_dir):
            root_dir = get_user_located_root()

#switch backslashes to forward slashes just for display on screen only (avoids issues with escaped characters)
clean = str(root_dir)
clean = str.replace(clean,'\\','/')
print "Rooting OpenRPG at: " + clean

load_paths(dir_struct, root_dir)
