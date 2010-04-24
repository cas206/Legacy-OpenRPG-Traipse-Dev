# Copyright (C) 2000-2001 The OpenRPG Project
#
#   openrpg-dev@lists.sourceforge.net
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
# --
#
# File: orpg_log.py
# Author: Dj Gilcrease
# Maintainer:
# Version:
#   $Id: orpg_log.py,v Traipse 'Ornery-Orc' prof.ebral Exp $
#
# Description: classes for orpg log messages
#

from __future__ import with_statement
import sys, os, os.path, time, traceback, inspect, wx

from orpg.orpgCore import component
from orpg.external.terminalwriter import TerminalWriter
from orpg.tools.decorators import pending_deprecation
from orpg.dirpath import dir_struct

#########################
## Error Types
#########################
ORPG_PRINT          = 0
ORPG_CRITICAL       = 1
ORPG_GENERAL        = 2
ORPG_INFO           = 4
ORPG_NOTE           = 8
ORPG_DEBUG          = 16


def Crash(type, value, crash):
    crash_report = open(dir_struct["home"] + 'crash-report.txt', "w")
    traceback.print_exception(type, value, crash, file=crash_report)
    crash_report.close()
    msg = ''
    crash_report = open(dir_struct["home"] + 'crash-report.txt', "r")
    for line in crash_report: msg += line
    logger.exception(msg)
    crash_report.close()
    logger.exception("Crash Report Created!!")
    logger.info("Printed out crash-report.txt in your System folder", True)

class Term2Win(object):
    # A stdout redirector.  To be implemented later.
    def write(self, text):
        logger.stdout(text)
        wx.Yield()
        #sys.__stdout__.write(text)

class TrueDebug(object):
    """A simple debugger. Add debug() to a function and it prints the function name and any objects included. Add an object or a group of objects in ()'s.
    Adding True to locale prints the file name where the function is. Adding False to log turns the log off.
    Adding True to parents will print out the parent functions, starting from TrueDebug.
    This feature can be modified to trace deeper and find the bugs faster, ending the puzzle box."""
    def __init__(self, objects=None, locale=False, log=True, parents=False):
        if log == False: return
        current = inspect.currentframe()
        if parents: self.get_parents(current)
        else: self.true_debug(current, objects, locale)

    def true_debug(self, current, objects, locale):
        debug_string = 'Function: ' + str(inspect.getouterframes(current)[1][3])
        #if locale == 'all': print inspect.getouterframes(current)[4]; return
        if objects != None: debug_string += ' Objects: ' + str(objects)
        if locale: debug_string += ' File: ' + str(inspect.getouterframes(current)[1][1])
        logger.debug(debug_string, True)
        return

    def get_parents(self, current):
        debug_string = 'Function: ' + str(inspect.getouterframes(current)[1][3]) + ' Parents:'
        family = list(inspect.getouterframes(current))
        for parent in family:
            debug_string += ' ' + str(parent[4])
        logger.debug(debug_string, True)
        return
    
class DebugConsole(wx.Frame):
    def __init__(self, parent):
        super(DebugConsole, self).__init__(parent, -1, "Debug Console")
        icon = wx.Icon(dir_struct["icon"]+'note.ico', wx.BITMAP_TYPE_ICO)
        self.parent = parent
        self.SetIcon(icon)
        self.console = wx.TextCtrl(self, -1, style=wx.TE_MULTILINE | wx.TE_READONLY)
        self.bt_clear = wx.Button(self, wx.ID_CLEAR)
        self.report = wx.Button(self, wx.ID_ANY, 'Bug Report')
        sizer = wx.GridBagSizer(hgap=1, vgap=1)
        sizer.Add(self.console, (0,0), span=(1,2), flag=wx.EXPAND)
        sizer.Add(self.bt_clear, (1,0), span=(1,1), flag=wx.ALIGN_LEFT)
        sizer.Add(self.report, (1,1), span=(1,1), flag=wx.ALIGN_RIGHT|wx.EXPAND)
        sizer.AddGrowableCol(0)
        sizer.AddGrowableRow(0)
        self.SetSizer(sizer)
        #self.Layout()
        self.SetAutoLayout(True)
        self.SetSize((450, 275))
        self.SetMinSize((450, 275))
        self.Bind(wx.EVT_CLOSE, self.Min) 
        self.Bind(wx.EVT_BUTTON, self.clear, self.bt_clear)
        self.Bind(wx.EVT_BUTTON, self.bug_report, self.report)
        self.Min(None)
        #sys.stdout = Term2Win()
        component.add('debugger', self.console)

    def Min(self, evt):
        self.Hide()

    def clear(self, evt):
        self.console.SetValue('')

    def bug_report(self, evt):
        self.parent.OnMB_HelpReportaBug()

class orpgLog(object):
    _log_level = 7
    _log_name = None
    _log_to_console = False
    _io = TerminalWriter(sys.stderr)
    _lvl_args = None

    def __new__(cls, *args, **kwargs):
        it = cls.__dict__.get("__it__")
        if it is not None:
            return it
        cls.__it__ = it = object.__new__(cls)
        return it

    def __init__(self, home_dir, filename='orpgRunLog '):
        self._lvl_args = {16: {'colorizer': {'green': True},
                               'log_string': 'DEBUG'},
                          8: {'colorizer': {'bold': True, 'green':True},
                              'log_string':'NOTE'},
                          4: {'colorizer': {'blue': True},
                              'log_string': 'INFO'},
                          2: {'colorizer': {'red': True},
                             'log_string': 'ERROR'},
                          1: {'colorizer': {'bold': True, 'red': True},
                             'log_string': 'EXCEPTION'}}

        if not self.log_name:
            self.log_name = home_dir + filename + time.strftime('%m-%d-%Y.txt',
                                                    time.localtime(time.time()))

    def debug(self, msg, to_console=False):
        self.log(msg, ORPG_DEBUG, to_console)

    def note(self, msg, to_console=False):
        self.log(msg, ORPG_NOTE, to_console)

    def info(self, msg, to_console=False):
        self.log(msg, ORPG_INFO, to_console)

    def general(self, msg, to_console=False):
        self.log(msg, ORPG_GENERAL, to_console)

    def stdout(self, msg, to_console=True):
        self.log(msg, ORPG_INFO, to_console)

    def exception(self, msg, to_console=True):
        component.get('frame').TraipseSuiteWarn('debug')
        self.log(msg, ORPG_CRITICAL, to_console)

    def log(self, msg, log_type, to_console=False):
        if self.log_to_console or to_console or log_type == ORPG_CRITICAL:
            try: self._io.line(str(msg), **self._lvl_args[log_type]['colorizer'])
            except: pass #Fails without the Debug Console
            try: component.get('debugger').AppendText(".. " + str(msg) +'\n')
            except: pass

        if log_type and (self.log_level or to_console):
            atr = {'msg': msg, 'level': self._lvl_args[log_type]['log_string']}
            atr['time'] = time.strftime('[%x %X]', time.localtime(time.time()))
            logMsg = '%(time)s (%(level)s) - %(msg)s\n' % (atr)

            with open(self.log_name, 'a') as f:
                f.write(logMsg)

    @pending_deprecation("use logger.log_level = #")
    def setLogLevel(self, log_level):
        self.log_level = log_level

    @pending_deprecation("use logger.log_level")
    def getLogLevel(self):
        return self.log_level

    @pending_deprecation("use logger.log_name = bla")
    def setLogName(self, log_name):
        self.log_name = log_name

    @pending_deprecation("use logger.log_name")
    def getLogName(self):
        return self.log_name

    @pending_deprecation("use logger.log_to_console = True/False")
    def setLogToConsol(self, true_or_false):
        self.log_to_consol = true_or_false

    @pending_deprecation("use logger.log_to_console")
    def getLogToConsol(self):
        return self.log_to_consol

    """
    Property Methods
    """
    def _get_log_level(self):
        return self._log_level
    def _set_log_level(self, log_level):
        if not isinstance(log_level, int) or log_level < 1 or log_level > 31:
            raise TypeError("The loggers level must be an int between 1 and 31")

        self._log_level = log_level

    def _get_log_name(self):
        return self._log_name
    def _set_log_name(self, name):
        if not os.access(os.path.abspath(os.path.dirname(name)), os.W_OK):
            raise IOError("Could not write to the specified location")

        self._log_name = name

    def _get_log_to_console(self):
        return self._log_to_console
    def _set_log_to_console(self, true_or_false):
        if not isinstance(true_or_false, bool):
            raise TypeError("log_to_console must be a boolean value")

        self._log_to_console = true_or_false

    log_level = property(_get_log_level, _set_log_level)
    log_name = property(_get_log_name, _set_log_name)
    log_to_console = property(_get_log_to_console, _set_log_to_console)

logger = orpgLog(dir_struct.get("user") + "runlogs/")
crash = sys.excepthook = Crash
debug = TrueDebug
