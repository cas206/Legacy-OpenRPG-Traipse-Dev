import os

from orpg.tools.orpg_log import logger
from orpg.tools.validate import validate
from xml.etree.ElementTree import ElementTree, Element, parse
from xml.etree.ElementTree import fromstring, tostring
from orpg.orpgCore import component
from orpg.dirpath import dir_struct

class Settings:
    def __init__(self):
        self.changes = []
        validate.config_file("settings.xml","default_settings.xml")
        self.filename = dir_struct["user"] + "settings.xml"
        xml_dom = parse(dir_struct["user"] + "settings.xml")
        if xml_dom == None: self.rebuildSettings()
        else: self.xml_dom = xml_dom.getroot()

    def rebuildSettings(self):
        logger.info("Settings file has be corrupted, rebuilding settings.", True)
        try: os.remove(self.filename)
        except: pass
        validate.config_file("settings.xml","default_settings.xml")
        self.xml_dom = parse(self.filename).getroot()

    def get_setting(self, name): ##Depricated
        return self.get(name)

    def get(self, name): 
        try: return self.xml_dom.getiterator(name)[0].get("value")
        except: return 0

    def get_setting_keys(self): ##Depricated
        return self.get_keys()

    def get_keys(self):
        keys = []
        tabs = self.xml_dom.getiterator("tab")
        for i in xrange(0, len(tabs)):
            if tabs[i].get("type") == 'grid':
                children = tabs[i].getchildren()
                for c in children: keys.append(c.tag)
        return keys

    def set_setting(self, name, value): ##Depricated
        self.change(name, value)

    def change(self, name, value):
        self.xml_dom.getiterator(name)[0].set("value", value)

    def add_setting(self, tab, setting, value, options, help): ##Depricated
        return self.add(tab, setting, value, options, help)

    def add(self, tab, setting, value, options, help):
        if len(self.xml_dom.getiterator(setting)) > 0: return False
        tabs = self.xml_dom.getiterator("tab")
        newsetting = fromstring('<' + setting + ' value="' + value + '" options="' + 
                                        options + '" help="' + help + '" />')
        for i in xrange(0, len(tabs)):
            if tabs[i].get("name") == tab and tabs[i].get("type") == 'grid':
                tabs[i].append(newsetting)
                return True
        return False

    def add_tab(self, parent, tabname, tabtype):
        tab_xml = '<tab '
        if tabtype == 'text': tab_xml += 'name="' + tabname + '" type="text" />'
        else: tab_xml += 'name="' + tabname + '" type="' + tabtype + '"></tab>'
        newtab = fromstring(tab_xml)
        if parent != None:
            tabs = self.xml_dom.getiterator("tab")
            for i in xrange(0, len(tabs)):
                if tabs[i].get("name") == parent and tabs[i].get("type") == 'tab':
                    children = tabs[i].getchildren()
                    for c in children:
                        if c.get("name") == tabname: return False
                    tabs[i].append(newtab)
                    return True
        else:
            children = self.xml_dom.getchildren()
            for c in children:
                if c.get("name") == tabname: return False
            self.xml_dom.append(newtab)
            return True
        return False

    def updateIni(self):
        defaultFile = orpg.dirpath.dir_struct['template'] + 'default_settings.xml'
        default_dom = parse(defaultfile)
        for child in default_dom.getchildren():
            if child.tag == 'tab': self.proccessChildren(child)

    def proccessChildren(self, dom, parent=None):
        if dom.tag == 'tab': self.add_tab(parent, dom.get("name"), dom.get("type"))

        for child in dom.getchildren():
            if child.tag == 'tab': self.proccessChildren(child, dom.get("name"))
            else:
                self.add_setting(dom.get("name"), child.tag, 
                                child.get("value"), child.get("options"), 
                                child.get("help"))

    def save(self):
        #self.xml_dom.write(self.filename)
        temp_file = open(self.filename, "w")
        temp_file.write(tostring(self.xml_dom))
        temp_file.close()

settings = Settings()
component.add('settings', settings)
