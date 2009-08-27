# file: config_files.py
#
# Author: Todd Faris (Snowdog)
# Date:   5/10/2005
#
# Misc. config file service methods
#

from orpg.dirpath import dir_struct
import os

class Validate:
    def __init__(self, userpath=None):
        if userpath is None:
            userpath = dir_struct["home"] + os.sep + 'upmana' +os.sep
        self.__loadUserPath = userpath

    def config_file(self, user_file, template_file):
        #STEP 1: verify the template exists
        if (not os.path.exists(dir_struct["template"] + template_file)):
            return 0

        #STEP 2: verify the user file exists. If it doesn't then create it from template
        if (not os.path.exists(self.__loadUserPath + user_file)):
            default = open(dir_struct["template"] + template_file,"r")
            file = default.read()
            newfile = open(self.__loadUserPath + user_file,"w")
            newfile.write(file)
            default.close()
            newfile.close()
            return 2  #returning 2 (True) so calling method will know if file was created

        #STEP 3: user file exists (is openable) return 1 indicating no-create operation required
        else: return 1

    def ini_entry(self, entry_name, ini_file):
        pass

validate = Validate()
