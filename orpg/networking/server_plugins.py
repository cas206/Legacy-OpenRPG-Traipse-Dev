import sys
import os
from orpg.dirpath import dir_struct

class _SingletonKey(object):
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '_inst'):
            cls._inst = super(_SingletonKey, cls).__new__(cls, *args, **kwargs)
        return cls._inst

class PluginData(object):
    """A holder class for inactive plugins"""
    def __init__(self, Name, File, Author="", Help=""):
        self.File = File
        self.Name = Name
        self.Author = Author
        self.Help = Help
        self.Activated = False

class BasePluginsClass(object):
    def __init__(self, ptype):
        self.__ptype = ptype
        self.__plugins = {}

    def initBase(self):
        self._startPlugins()

    #Methods
    def _startPlugins(self):
        autoload = []
        #Fill autoload from some file with the Plugin Names

        plugins = []
        for root, dirs, files in os.walk(dir_struct['plugins'] + self.__ptype):
            if '__init__.py' in files:
                files.remove('__init__.py')
            if 'base_plugin.py' in files:
                files.remove('base_plugin.py')

            for pfile in files:
                if pfile[-3:] == '.py':
                    plugins.append(PluginData('New Plugin', root + os.sep + pfile))

        for plugin in plugins:
            pdata = self._load(plugin)
            if pdata != None:
                if pdata.Name not in autoload:
                    self._unload(plugin)

    def activatePlugin(self, pluginName):
        if not self.__plugins.has_key(pluginName):
            #Print some error about invalid plugin
            return
        pluginData = self.__plugins[pluginName]
        #Unload it first, just incase it is already loaded
        self._unload(pluginData)

        #Now Load it
        self._load(pluginData)

        #Write to the autoload file for this plugin
        self.__plugins[pluginName].Activated = True
        self.__plugins[pluginName].start()

    def deactivatePugin(self, pluginData):
        if not self.__plugins.has_key(pluginName):
            #Print some error about invalid plugin
            return

        pluginData = self.__plugins[pluginName]
        self.__plugins[pluginName].stop()

        #Unload it
        self._unload(pluginData)
        #Remove this plugin from the autoload file

    #Private Methods
    def _findModule(self, pluginFile):
        s1 = pluginFile.split(os.sep)
        s2 = s1[-1].split('.')
        return ('plugins.' + self.__ptype + '.' + s2[0], s2[0])

    def _unload(self, pluginData):
        self.__plugins[pluginData.Name] = PluginData(pluginData.Name, 
                                                    pluginData.File, 
                                                    pluginData.Author, 
                                                    pluginData.Help)
        unload = []
        mod = self._findModule(pluginData.File)[0]
        for key, module in sys.modules.iteritems():
            if str(module).find(mod) > -1:
                unload.append(key)

        for plugin in unload:
            del sys.modules[plugin]

    def _load(self, pluginData):
        modinfo = self._findModule(pluginData.File)
        try:
            mod = __import__(modinfo[0])
            mod = getattr(mod,self.__ptype)
            tmp = getattr(mod, modinfo[1])
            self.__plugins[pluginData.Name] = tmp.Plugin()
            print "Loaded Module " + pluginData.File
            return self.__plugins[pluginData.Name]
        except Exception, e:
            print e
            print "Unable to load module" + pluginData.File

        return None

    #Property Methods
    def _getPlugins(self):
        return self.__plugins

    def _getType(self):
        return self.__ptype
    #Properties
    Plugins = property(_getPlugins, None)
    Type = property(_getType, None)

class ServerPluginsClass(BasePluginsClass):
    def __init__(self, singletonKey):
        if not isinstance(singletonKey, _SingletonKey):
            raise invalid_argument(_("Use ServerPlugins to get access to singleton"))

        BasePluginsClass.__init__(self, 'server')
        self.initBase()

    def preParseIncoming(self, xml_dom, data):
        sent = True
        errmsg = ""
        for pluginName, pluginData in self.Plugins.iteritems():
            if pluginData.Activated:
                xml_dom, data = pluginData.preParseIncoming(xml_dom, data)
        return xml_dom, data

    def postParseIncoming(self, data):
        for pluginName, pluginData in self.Plugins.iteritems():
            if pluginData.Activated:
                data = pluginData.postParseIncoming(data)
        return data

    def getPlayer(self):
        players = []
        for pluginName, pluginData in self.Plugins.iteritems():
            if pluginData.Activated:
                playerName = pluginData.addPlayer(data)
                players.append(playerName)
        return players

    def setPlayer(self, playerData):
        players = []
        for pluginName, pluginData in self.Plugins.iteritems():
            if pluginData.Activated:
                playerName = pluginData.addPlayer(data)
                players.append(playerName)
        return

    def preParseOutgoing(self):
        data = []
        for pluginName, pluginData in self.Plugins.iteritems():
            if pluginData.Activated:
                xml = pluginData.preParseOutgoing()
                for msg in xml:
                    data.append(msg)
        return data

    def postParseOutgoing(self):
        data = []
        for pluginName, pluginData in self.Plugins.iteritems():
            if pluginData.Activated:
                xml = pluginData.postParseOutgoing()
                for msg in xml:
                    data.append(msg)
        return data

__key = _SingletonKey()
ServerPlugins = ServerPluginsClass(__key)
