from orpg.orpg_wx import *
from orpg.orpgCore import component
from xml.etree.ElementTree import ElementTree, Element, parse
from xml.etree.ElementTree import fromstring, tostring

class PluginHandler:
    # Initialization subroutine.
    #
    # !self : instance of self
    # !chat : instance of the chat window to write to
    def __init__(self, plugindb, parent):
        self.session = component.get("session")
        self.chat = component.get("chat")
        self.settings = component.get("settings")
        self.gametree = component.get("tree")
        self.startplugs = component.get("startplugs")
        self.xml = component.get("xml")
        self.validate = component.get("validate")
        self.topframe = component.get("frame")
        self.plugindb = plugindb
        self.parent = parent
        self.shortcmdlist = self.chat.chat_cmds.shortcmdlist
        self.cmdlist = self.chat.chat_cmds.cmdlist

    def plugin_enabled(self):
        pass

    def plugin_disabled(self):
        pass

    def menu_start(self):
        rootMenu = component.get("pluginmenu")
        try:
            self.plugin_menu()
            rootMenu.AppendMenu(wx.ID_ANY, self.name, self.menu)
        except:
            self.menu = wx.Menu()
            empty = wx.MenuItem(self.menu, wx.ID_ANY, 'Empty')
            self.menu.AppendItem(empty)
            rootMenu.AppendMenu(wx.ID_ANY, self.name, self.menu)

    def menu_cleanup(self):
        self.settings.save()
        rootMenu = component.get("pluginmenu")
        menus = rootMenu.MenuItems
        for mi in menus:
            if mi.GetText() == self.name:
                rootMenu.RemoveItem(mi)
		del self.menu

    def plugin_addcommand(self, cmd, function, helptext, show_msg=True):
        self.chat.chat_cmds.addcommand(cmd, function, helptext)
        if(show_msg):
            msg = '<br /><b>New Command added</b><br />'
            msg += '<b><font color="#000000">%s</font></b>  %s' % (cmd, helptext)
            self.chat.InfoPost(msg)

    def plugin_commandalias(self, shortcmd, longcmd, show_msg=True):
        self.chat.chat_cmds.addshortcmd(shortcmd, longcmd)
        if(show_msg):
            msg = '<br /><b>New Command Alias added:</b><br />'
            msg += '<b><font color="#0000CC">%s</font></b> is short for <font color="#000000">%s</font>' % (shortcmd, longcmd)
            self.chat.InfoPost(msg)

    def plugin_removecmd(self, cmd):
        self.chat.chat_cmds.removecmd(cmd)
        msg = '<br /><b>Command Removed:</b> %s' % (cmd)
        self.chat.InfoPost(msg)

    def plugin_add_nodehandler(self, nodehandler, nodeclass):
        self.gametree.add_nodehandler(nodehandler, nodeclass)

    def plugin_remove_nodehandler(self, nodehandler):
        self.gametree.remove_nodehandler(nodehandler)

    def plugin_add_msg_handler(self, tag, function):
        self.session.add_msg_handler(tag, function)

    def plugin_delete_msg_handler(self, tag):
        self.session.remove_msg_handler(tag)

    def plugin_add_setting(self, setting, value, options, help):
        self.settings.add_tab('Plugins', self.name, 'grid')
        self.settings.add_setting(self.name, setting, value, options, help)

    def plugin_send_msg(self, to, plugin_msg):
        xml_dom = fromstring(plugin_msg)
        #xml_dom = xml_dom.getroot()
        xml_dom.set('from', str(self.session.id))
        xml_dom.set('to', str(to))
        xml_dom.set('group_id', str(self.session.group_id))
        tag_name = xml_dom.tag
        if not tag_name in self.session.core_msg_handlers:
            xml_msg = '<plugin to="' + str(to)
            xml_msg += '" from="' + str(self.session.id)
            xml_msg += '" group_id="' + str(self.session.group_id)
            xml_msg += '" />' + tostring(xml_dom)
            self.session.outbox.put(xml_msg)
        else:
            #Spoofing attempt
            pass
        #xml_dom.unlink()

    def message(self, text):
        return text

    def pre_parse(self, text):
        return text

    def send_msg(self, text, send):
        return text, send

    def plugin_incoming_msg(self, text, type, name, player):
        return text, type, name

    def post_msg(self, text, myself):
        return text

    def refresh_counter(self):
        pass

    def close_module(self):
        #This is called when OpenRPG shuts down
        pass
