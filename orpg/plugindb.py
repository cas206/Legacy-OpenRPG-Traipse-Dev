from __future__ import with_statement

from orpg.dirpath import dir_struct
from orpg.tools.validate import validate
from orpg.tools.orpg_log import logger

from xml.etree.ElementTree import ElementTree, Element, parse
from xml.etree.ElementPath import find

class PluginDB(object):
    etree = ElementTree()
    filename = dir_struct["user"] + "plugindb.xml"

    def __new__(cls, *args, **kwargs):
        it = cls.__dict__.get("__it__")
        if it is not None:
            return it
        cls.__it__ = it = object.__new__(cls)
        it._init()
        return it

    def _init(self):
        validate.config_file("plugindb.xml", "default_plugindb.xml")
        self.LoadDoc()

    def GetString(self, plugname, strname, defaultval="", verbose=False):
        strname = self.safe(strname)

        plugin = self.etree.find(plugname)
        if plugin is None or plugin.find(strname) is None:
            msg = ["plugindb: no value has been stored for", strname, "in",
                   plugname, "so the default has been returned"]
            logger.info(' '.join(msg), verbose)
            return defaultval

        logger.debug("successfully found the str value", verbose)
        return self.normal(plugin.find(strname).text)

    def SetString(self, plugname, strname, val):
        val = self.safe(val)
        strname = self.safe(strname)

        plugin = self.etree.find(plugname)
        if plugin is None:
            plugin = Element(plugname)
            self.etree.getroot().append(plugin)

        str_el = plugin.find(strname)
        if str_el is None:
            str_el = Element(strname)
            str_el.set('type', 'str')
            plugin.append(str_el)
        str_el.text = val
        self.SaveDoc()

    def FetchList(self, parent):
        retlist = []
        for litem in parent.find('list').findall('lobject'):
            if litem.get('type') == 'int': retlist.append(int(litem.text))
            if litem.get('type') == 'bool': retlist.append(litem.text == 'True')
            elif litem.get('type') == 'float': retlist.append(float(litem.text))
            elif litem.get('type') == 'list': retlist.append(self.FetchList(litem))
            elif litem.get('type') == 'dict': retlist.append(self.FetchDict(litem))
            else: retlist.append(str(self.normal(litem.text)))
        return retlist

    def GetList(self, plugname, listname, defaultval=list(), verbose=False):
        listname = self.safe(listname)
        plugin = self.etree.find(plugname)
        if plugin is None or plugin.find(listname) is None:
            msg = ["plugindb: no value has been stored for", listname, "in",
                   plugname, "so the default has been returned"]
            logger.info(' '.join(msg), verbose)
            return defaultval

        retlist = self.FetchList(plugin.find(listname))
        logger.debug("successfully found the list value", verbose)
        return retlist

    def BuildList(self, val):
        list_el = Element('list')
        for item in val:
            i = Element('lobject')
            if isinstance(item, bool):
                i.set('type', 'bool')
                i.text = str(item)
            elif isinstance(item, int):#it's an int
                i.set('type', 'int')
                i.text = str(item)
            elif isinstance(item, float):#it's a float
                i.set('type', 'float')
                i.text = str(item)
            elif isinstance(item, (list, tuple)):#it's a list
                i.set('type', 'list')
                i.append(self.BuildList(item))
            elif isinstance(item, dict):#it's a dictionary
                i.set('type', 'dict')
                i.append(self.BuildDict(item))
            else:
                i.set('type', 'str')
                i.text = self.safe(item)
            list_el.append(i)
        return list_el

    def SetList(self, plugname, listname, val):
        listname = self.safe(listname)
        plugin = self.etree.find(plugname)
        if plugin is None:
            plugin = Element(plugname)
            self.etree.getroot().append(plugin)
        list_el = plugin.find(listname)
        if list_el is None:
            list_el = Element(listname)
            list_el.set('type', 'list')
            plugin.append(list_el)
        else:
            list_el.remove(list_el.find('list'))
        list_el.append(self.BuildList(val))
        self.SaveDoc()

    def BuildDict(self, val):
        dict_el = Element('dict')
        for key, item in val.iteritems():
            i = Element('dobject')

            if isinstance(item, bool):
                i.set('type', 'bool')
                i.set('name', self.safe(key))
                i.text = str(item)
            elif isinstance(item, int):#it's an int
                i.set('type', 'int')
                i.set('name', self.safe(key))
                i.text = str(item)
            elif isinstance(item, float):#it's a float
                i.set('type', 'float')
                i.set('name', self.safe(key))
                i.text = str(item)
            elif isinstance(item, (list, tuple)):#it's a list
                i.set('type', 'list')
                i.set('name', self.safe(key))
                i.append(self.BuildList(item))
            elif isinstance(item, dict):#it's a dictionary
                i.set('type', 'dict')
                i.set('name', self.safe(key))
                i.append(self.BuildDict(item))
            else:
                i.set('type', 'str')
                i.set('name', self.safe(key))
                i.text = self.safe(item)
            dict_el.append(i)
        return dict_el

    def SetDict(self, plugname, dictname, val):
        dictname = self.safe(dictname)
        plugin = self.etree.find(plugname)
        if plugin is None:
            plugin = Element(plugname)
            self.etree.getroot().append(plugin)
        dict_el = plugin.find(dictname)
        if dict_el is None:
            dict_el = Element(dictname)
            dict_el.set('type', 'dict')
            plugin.append(dict_el)
        else: 
            refs = dict_el.findall('dict')
            keys = val.keys()
            for r in refs:
                if r.find('dobject').get('name') in keys: 
                    logger.debug('Duplicate Dictionary Reference', True); return
        dict_el.append(self.BuildDict(val))
        self.SaveDoc()

    def FetchDict(self, parent):
        retdict = {}
        for ditem in parent.find('dict').findall('dobject'):
            key = self.normal(ditem.get('name'))
            if ditem.get('type') == 'int': value = int(ditem.text)
            elif ditem.get('type') == 'bool': value = ditem.text == 'True'
            elif ditem.get('type') == 'float': value = float(ditem.text)
            elif ditem.get('type') == 'list': value = self.FetchList(ditem)
            elif ditem.get('type') == 'dict': value = self.FetchDict(ditem)
            else: value = str(self.normal(ditem.text))
            retdict[key] = value
        return retdict

    def GetDict(self, plugname, dictname, defaultval=dict(), verbose=False):
        dictname = self.safe(dictname)
        plugin = self.etree.find(plugname)
        if plugin is None or plugin.find(dictname) is None:
            msg = ["plugindb: no value has been stored for", dictname, "in",
                   plugname, "so the default has been returned"]
            logger.info(' '.join(msg), verbose)
            return defaultval
        retdict = self.FetchDict(plugin.find(dictname))
        logger.debug("successfully found dict value", verbose)
        return retdict

    def safe(self, string):
        return string.replace("<", "$$lt$$").replace(">", "$$gt$$")\
               .replace("&","$$amp$$").replace('"',"$$quote$$")

    def normal(self, string):
        return string.replace("$$lt$$", "<").replace("$$gt$$", ">")\
               .replace("$$amp$$","&").replace("$$quote$$",'"')

    def SaveDoc(self):
        with open(self.filename, "w") as f:
            self.etree.write(f)

    def LoadDoc(self):
        with open(self.filename) as f:
            self.etree.parse(f)

plugindb = PluginDB()
