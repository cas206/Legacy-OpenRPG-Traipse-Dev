#!/usr/bin/env python

#import os
import sys

import pyver
pyver.checkPyVersion()

from orpg.orpg_wx import *

if WXLOADED:
    import orpg.networking.mplay_server_gui
    app = orpg.networking.mplay_server_gui.ServerGUIApp(0)
    app.MainLoop()
