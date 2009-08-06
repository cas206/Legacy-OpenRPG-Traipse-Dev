#!/usr/bin/env python

import sys
import os

HG = os.environ["HG"]

import pyver
pyver.checkPyVersion()

from orpg.orpg_wx import *
import upmana.updatemana
app = upmana.updatemana.updateApp(0)
app.MainLoop()
for key in sys.modules.keys():
    if 'orpg' in key:
        del sys.modules[key]

from orpg.orpg_wx import *
import orpg.main

if WXLOADED:
    mainapp = orpg.main.orpgApp(0)
    mainapp.MainLoop()
else:
    print "You really really need wx!"
