#!/usr/bin/env python

import pyver
pyver.checkPyVersion()

#Update Manager
from orpg.orpg_wx import *
import upmana.updatemana
app = upmana.updatemana.updateApp(0)
app.MainLoop()

#Main Program
from orpg.orpg_wx import *
import orpg.main

if WXLOADED:
    mainapp = orpg.main.orpgApp(0)
    mainapp.MainLoop()
else:
    print "You really really need wx!"
