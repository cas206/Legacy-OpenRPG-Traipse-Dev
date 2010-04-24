import os
import orpg.pluginhandler
from orpg.mapper.miniatures_handler import *
from orpg.orpgCore import *
import wx


class QuickNoteDialog(wx.Dialog):
    def __init__(self):
        wx.Dialog.__init__(self, None, -1, "Quick Note", size=(250, 210))
        self.text = wx.TextCtrl(self, -1, "", style=wx.TE_MULTILINE)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.text, 1, wx.EXPAND)
        self.SetSizer(sizer)

class Plugin(orpg.pluginhandler.PluginHandler):
    def __init__(self, plugindb, parent):
        orpg.pluginhandler.PluginHandler.__init__(self, plugindb, parent)
        self.name = 'Mini Quick Notes'
        self.author = 'David'
        self.help = """Allows you to add private notes when you right-click on a mini on the map.

Note: it will try to save data between sessions but you must load plugin AFTER the map has been loaded
so do not auto-load this plugin.  Also these notes are NOT shared with other users.

Look at the mini superscript plugin for an example of how to do that.

Modified for Traipse (Prof. Ebral)
EXPERIMENTAL! In the process of being updated."""
        self.save_on_exit = False;

    def plugin_menu(self):
        pass
        
    def plugin_enabled(self):
        m = component.get("map").layer_handlers[2]
        m.set_mini_rclick_menu_item("Quick Notes", self.on_quick_note)

        db_notes_list = self.plugindb.GetList("xxminiquicknote", "notes", [])
        matched = 0;
        for mini in component.get("map").canvas.layers['miniatures'].miniatures:
            print 'label:'+mini.label
            print 'posx:'+str(mini.pos.x)
            print 'posy:'+str(mini.pos.y)
            for db_note in db_notes_list:
                print 'db_note:'+str(db_note)
                if mini.label == db_note[0] and mini.pos.x == db_note[1] and mini.pos.y == db_note[2]:
                    mini.quicknote = db_note[3]
                    db_notes_list.remove(db_note)
                    matched += 1
                    break

    def plugin_disabled(self):
        m = component.get("map").layer_handlers[2]
        m.set_mini_rclick_menu_item("Quick Notes", None)

        if self.save_on_exit:
            db_notes_list = []
            for mini in component.get("map").canvas.layers['miniatures'].miniatures:
                if 'quicknote' in mini.__dict__:
                    db_notes_list.append([mini.label, mini.pos.x, mini.pos.y, mini.quicknote])
            self.plugindb.SetList("xxminiquicknote", "notes", db_notes_list)

    def on_quick_note(self, event):
        self.save_on_exit = True
        m = component.get("map").layer_handlers[2]
        # m.sel_rmin is the mini that was just right-clicked
        if 'quicknote' not in m.sel_rmin.__dict__:
            m.sel_rmin.quicknote = ''
        dlg = QuickNoteDialog()
        dlg.text.SetValue(m.sel_rmin.quicknote)
        dlg.ShowModal()
        m.sel_rmin.quicknote = dlg.text.GetValue()
        dlg.Destroy()
