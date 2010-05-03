import os, wx, re
import orpg.pluginhandler
from orpg.tools.InterParse import Parse
from orpg.orpgCore import component
from xml.etree.ElementTree import iselement

class Plugin(orpg.pluginhandler.PluginHandler):
    # Initialization subroutine.
    #
    # !self : instance of self
    # !openrpg : instance of the the base openrpg control
    def __init__(self, plugindb, parent):
        orpg.pluginhandler.PluginHandler.__init__(self, plugindb, parent)

        # The Following code should be edited to contain the proper information
        self.name = 'Standard Namespace'
        self.author = 'Prof. Ebral'
        self.help = 'The Standard Namespace plugin allows for users of Traipse to use '
        self.help += 'the Standard Namespace syntax of !@ :: @!\n\n'
        self.help += 'This plugin modifies the External method, so context sensivity\n'
        self.help += 'is not calculated when using the Standard syntax. References must '
        self.help += 'have a unique name.'

        self.parseMethods = {'Traipse': Parse.NameSpaceE, 'Standard': self.NameSpaceS}

    def NameSpaceS(self, s): ## Re define NameSpace External
        reg1 = re.compile("(!@(.*?)@!)") ## Inlcude 'Standard' method
        reg2 = re.compile("(!&(.*?)&!)")
        matches = reg1.findall(s) + reg2.findall(s)
        newstr = False
        nodeable = ['rpg_grid_handler', 'container_handler', 
                    'group_handler', 'tabber_handler', 
                    'splitter_handler', 'form_handler', 'textctrl_handler']
        for i in xrange(0,len(matches)):
            find = matches[i][1].split('::')
            node = component.get('tree').xml_root
            if not iselement(node): 
                s = s.replace(matches[i][0], 'Invalid Reference!', 1); 
                s = Parse.NameSpaceE(s)
                return s
            for x in xrange(0, len(find)):
                namespace = node.getiterator('nodehandler')
                for node in namespace:
                    if find[x] == node.get('name'):
                        if node.get('class') not in nodeable: continue
                        if node.get('class') == 'rpg_grid_handler':
                            try: newstr = self.NameSpaceGrid(find[x+1], node); break
                            except: newstr = 'Invalid Grid Reference!'
                        try:
                            if Parse.FutureCheck(node, find[x+1]): break
                            else: continue
                        except:
                            if x == len(find)-1:
                                if node.find('text') != None: newstr = str(node.find('text').text) 
                                else: newstr = 'Invalid Reference!'
                                break
                            else: break
            if not newstr: newstr = 'Invalid Reference!'
            s = s.replace(matches[i][0], newstr, 1)
            s = Parse.ParseLogic(s, node)
        return s

    def plugin_menu(self):
        ## This is a standardized Menu item.  It connects to plugin_toggle where you can set events.
        self.menu = wx.Menu()
        self.toggle = self.menu.AppendCheckItem(wx.ID_ANY, 'On')
        self.topframe.Bind(wx.EVT_MENU, self.plugin_toggle, self.toggle)
        self.toggle.Check(True)

    def plugin_toggle(self, evt):
        if self.toggle.IsChecked() == True: 
            Parse.NameSpaceI = self.parseMethods['Standard']
            self.plugindb.SetString('xxstdnamespace', 'Standard', 'True')
        if self.toggle.IsChecked() == False: 
            Parse.NameSpaceI = self.parseMethods['Traipse']
            self.plugindb.SetString('xxstdnamespace', 'Standard', 'False')
        pass

    def plugin_enabled(self):
        self.onoroff = self.plugindb.GetString('xxstdnamespace', 'Standard', '') or 'False'
        self.toggle.Check(True) if self.onoroff == 'True' else self.toggle.Check(False)
        Parse.NameSpaceE = self.parseMethods['Standard'] if self.onoroff == 'True' else self.parseMethods['Traipse']
        pass

    def plugin_disabled(self):
        Parse.NameSpaceE = self.parseMethods['Traipse']

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
