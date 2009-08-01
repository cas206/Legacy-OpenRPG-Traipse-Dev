#!/usr/bin/env python

import sys
import os

HG = os.environ["HG"]

import pyver
pyver.checkPyVersion()

#os.system(HG + ' pull "http://hg.assembla.com/traipse"')
os.system(HG + ' pull "http://hg.assembla.com/traipse_dev"')
#os.system(HG + ' pull "http://hg.assembla.com/openrpg"')
#os.system(HG + ' pull "http://hg.assembla.com/openrpg_dev"')

for key in sys.modules.keys():
    if 'orpg' in key:
        del sys.modules[key]

from orpg.orpg_wx import *
import orpg.main

if WXLOADED:
    import orpg.tools.updater
    app = orpg.tools.updater.updateApp(0)
    app.MainLoop()

    mainapp = orpg.main.orpgApp(0)
    mainapp.MainLoop()
else:
    print "You really really need wx!"
