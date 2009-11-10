import os

from orpg.tools.orpg_log import logger
from orpg.tools.validate import validate
from orpg.orpg_xml import xml
from orpg.orpgCore import component
from orpg.dirpath import dir_struct

class Settings:
    def __init__(self):
        self.xml = component.get("xml")
        self.changes = []
        validate.config_file("settings.xml","default_settings.xml")
        self.filename = dir_struct["user"] + "settings.xml"
        temp_file = open(self.filename)
        txt = temp_file.read()
        temp_file.close()

        self.xml_dom = xml.parseXml(txt)

        if self.xml_dom is None: self.rebuildSettings()
        self.xml_dom = self.xml_dom._get_documentElement()

    def rebuildSettings(self):
        logger.info("Settings file has be corrupted, rebuilding settings.", True)
        try: os.remove(self.filename)
        except: pass

        validate.config_file("settings.xml","default_settings.xml")
        temp_file = open(self.filename)
        txt = temp_file.read()
        temp_file.close()
        self.xml_dom = xml.parseXml(txt)

    def get_setting(self, name): ##Depricated
        return self.get(name)

    def get(self, name): 
        try: return self.xml_dom.getElementsByTagName(name)[0].getAttribute("value")
        except: return 0

    def get_setting_keys(self): ##Depricated
        return self.get_keys()

    def get_keys(self):
        keys = []
        tabs = self.xml_dom.getElementsByTagName("tab")
        for i in xrange(0, len(tabs)):
            if tabs[i].getAttribute("type") == 'grid':
                children = tabs[i]._get_childNodes()
                for c in children: keys.append(c._get_tagName())
        return keys

    def set_setting(self, name, value): ##Depricated
        self.change(name, value)

    def change(self, name, value):
        self.xml_dom.getElementsByTagName(name)[0].setAttribute("value", value)

    def add_setting(self, tab, setting, value, options, help): ##Depricated
        return self.add(tab, setting, value, options, help)

    def add(self, tab, setting, value, options, help):
        if len(self.xml_dom.getElementsByTagName(setting)) > 0: return False
        tabs = self.xml_dom.getElementsByTagName("tab")
        newsetting = xml.parseXml('<' + setting + ' value="' + value + '" options="' + 
                                        options + '" help="' + help + '" />')._get_documentElement()
        for i in xrange(0, len(tabs)):
            if tabs[i].getAttribute("name") == tab and tabs[i].getAttribute("type") == 'grid':
                tabs[i].appendChild(newsetting)
                return True
        return False

    def add_tab(self, parent, tabname, tabtype):
        tab_xml = '<tab '
        if tabtype == 'text': tab_xml += 'name="' + tabname + '" type="text" />'
        else: tab_xml += 'name="' + tabname + '" type="' + tabtype + '"></tab>'
        newtab = xml.parseXml(tab_xml)._get_documentElement()
        if parent != None:
            tabs = self.xml_dom.getElementsByTagName("tab")
            for i in xrange(0, len(tabs)):
                if tabs[i].getAttribute("name") == parent and tabs[i].getAttribute("type") == 'tab':
                    children = tabs[i]._get_childNodes()
                    for c in children:
                        if c.getAttribute("name") == tabname: return False
                    tabs[i].appendChild(newtab)
                    return True
        else:
            children = self.xml_dom._get_childNodes()
            for c in children:
                if c.getAttribute("name") == tabname: return False
            self.xml_dom.appendChild(newtab)
            return True
        return False

    def updateIni(self):
        defaultFile = orpg.dirpath.dir_struct['template'] + 'default_settings.xml'
        temp_file = open(defaultFile)
        txt = temp_file.read()
        temp_file.close()
        default_dom = xml.parseXml(txt)._get_documentElement()
        for child in default_dom.getChildren():
            if child._get_tagName() == 'tab' and child.hasChildNodes(): self.proccessChildren(child)
        default_dom.unlink()

    def proccessChildren(self, dom, parent=None):
        if dom._get_tagName() == 'tab':
            self.add_tab(parent, dom.getAttribute("name"), dom.getAttribute("type"))

        for child in dom.getChildren():
            if child._get_tagName() == 'tab' and child.hasChildNodes():
                self.proccessChildren(child, dom.getAttribute("name"))
            else:
                self.add_setting(dom.getAttribute("name"), child._get_tagName(), 
                                child.getAttribute("value"), child.getAttribute("options"), 
                                child.getAttribute("help"))

    def save(self):
        temp_file = open(self.filename, "w")
        temp_file.write(xml.toxml(self.xml_dom,1))
        temp_file.close()

settings = Settings()
component.add('settings', settings)
