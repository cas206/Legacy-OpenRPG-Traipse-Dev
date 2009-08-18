import xmltramp
from orpg.dirpath import dir_struct
#import orpg.tools.validate
from types import *
from orpg.orpgCore import component

class PluginDB:
    def __init__(self, filename="plugindb.xml"):
        self.filename = dir_struct["user"] + filename
        component.get('validate').config_file(filename,"default_plugindb.xml")
        self.xml_dom = self.LoadDoc()

    def GetString(self, plugname, strname, defaultval, verbose=0):
        strname = self.safe(strname)
        for plugin in self.xml_dom:
            if plugname == plugin._name:
                for child in plugin._dir:
                    if child._name == strname:
                        #str() on this to make sure it's ASCII, not unicode, since orpg can't handle unicode.
                        if verbose: print "successfully found the value"
                        if len(child): return str( self.normal(child[0]) )
                        else: return ""
        else:
            if verbose:
                print "plugindb: no value has been stored for " + strname + " in " + plugname + " so the default has been returned"
            return defaultval

    def SetString(self, plugname, strname, val):
        val = self.safe(val)
        strname = self.safe(strname)
        for plugin in self.xml_dom:##this isn't absolutely necessary, but it saves the trouble of sending a parsed object instead of a simple string.
            if plugname == plugin._name:
                plugin[strname] = val
                plugin[strname]._attrs["type"] = "string"
                self.SaveDoc()
                return "found plugin"
        else:
            self.xml_dom[plugname] = xmltramp.parse("<" + strname + " type=\"string\">" + val + "</" + strname + ">")
            self.SaveDoc()
            return "added plugin"

    def FetchList(self, parent):
        retlist = []
        if not len(parent): return []
        for litem in parent[0]._dir:
            if len(litem):
                if litem._attrs["type"] == "int": retlist += [int(litem[0])]
                elif litem._attrs["type"] == "long": retlist += [long(litem[0])]
                elif litem._attrs["type"] == "float": retlist += [float(litem[0])]
                elif litem._attrs["type"] == "list": retlist += [self.FetchList(litem)]
                elif litem._attrs["type"] == "dict": retlist += [self.FetchDict(litem)]
                else: retlist += [str( self.normal(litem[0]) )]
            else: retlist += [""]
        return retlist

    def GetList(self, plugname, listname, defaultval, verbose=0):
        listname = self.safe(listname)
        for plugin in self.xml_dom:
            if plugname == plugin._name:
                for child in plugin._dir:
                    if child._name == listname and child._attrs["type"] == "list":
                        retlist = self.FetchList(child)
                        if verbose: print "successfully found the value"
                        return retlist
        else:
            if verbose:
                print "plugindb: no value has been stored for " + listname + " in " + plugname + " so the default has been returned"
            return defaultval

    def BuildList(self, val):
        listerine = "<list>"
        for item in val:
            if isinstance(item, basestring):#it's a string
                listerine += "<lobject type=\"str\">" + self.safe(item) + "</lobject>"
            elif isinstance(item, IntType):#it's an int
                listerine += "<lobject type=\"int\">" + str(item) + "</lobject>"
            elif isinstance(item, FloatType):#it's a float
                listerine += "<lobject type=\"float\">" + str(item) + "</lobject>"
            elif isinstance(item, LongType):#it's a long
                listerine += "<lobject type=\"long\">" + str(item) + "</lobject>"
            elif isinstance(item, ListType):#it's a list
                listerine += "<lobject type=\"list\">" + self.BuildList(item) + "</lobject>"
            elif isinstance(item, DictType):#it's a dictionary
                listerine += "<lobject type=\"dict\">" + self.BuildDict(item) + "</lobject>"
            else:
                return "type unknown"
        listerine += "</list>"
        return listerine

    def SetList(self, plugname, listname, val):
        listname = self.safe(listname)
        list = xmltramp.parse(self.BuildList(val))
        for plugin in self.xml_dom:
            if plugname == plugin._name:
                plugin[listname] = list
                plugin[listname]._attrs["type"] = "list"
                self.SaveDoc()
                return "found plugin"
        else:
            self.xml_dom[plugname] = xmltramp.parse("<" + listname + "></" + listname + ">")
            self.xml_dom[plugname][listname] = list
            self.xml_dom[plugname][listname]._attrs["type"] = "list"
            self.SaveDoc()
            return "added plugin"

    def BuildDict(self, val):
        dictator = "<dict>"
        for item in val.keys():
            if isinstance(val[item], basestring):
                dictator += "<dobject name=\"" + self.safe(item) + "\" type=\"str\">" + self.safe(val[item]) + "</dobject>"
            elif isinstance(val[item], IntType):#it's an int
                dictator += "<dobject name=\"" + self.safe(item) + "\" type=\"int\">" + str(val[item]) + "</dobject>"
            elif isinstance(val[item], FloatType):#it's a float
                dictator += "<dobject name=\"" + self.safe(item) + "\" type=\"float\">" + str(val[item]) + "</dobject>"
            elif isinstance(val[item], LongType):#it's a long
                dictator += "<dobject name=\"" + self.safe(item) + "\" type=\"long\">" + str(val[item]) + "</dobject>"
            elif isinstance(val[item], DictType):#it's a dictionary
                dictator += "<dobject name=\"" + self.safe(item) + "\" type=\"dict\">" + self.BuildDict(val[item]) + "</dobject>"
            elif isinstance(val[item], ListType):#it's a list
                dictator += "<dobject name=\"" + self.safe(item) + "\" type=\"list\">" + self.BuildList(val[item]) + "</dobject>"
            else:
                return str(val[item]) + ": type unknown"
        dictator += "</dict>"
        return dictator

    def SetDict(self, plugname, dictname, val, file="plugindb.xml"):
        dictname = self.safe(dictname)
        dict = xmltramp.parse(self.BuildDict(val))
        for plugin in self.xml_dom:
            if plugname == plugin._name:
                plugin[dictname] = dict
                plugin[dictname]._attrs["type"] = "dict"
                self.SaveDoc()
                return "found plugin"
        else:
            self.xml_dom[plugname] = xmltramp.parse("<" + dictname + "></" + dictname + ">")
            self.xml_dom[plugname][dictname] = dict
            self.xml_dom[plugname][dictname]._attrs["type"] = "dict"
            self.SaveDoc()
            return "added plugin"

    def FetchDict(self, parent):
        retdict = {}
        if not len(parent):
            return {}
        for ditem in parent[0]._dir:
            if len(ditem):
                ditem._attrs["name"] = self.normal(ditem._attrs["name"])
                if ditem._attrs["type"] == "int": retdict[ditem._attrs["name"]] = int(ditem[0])
                elif ditem._attrs["type"] == "long": retdict[ditem._attrs["name"]] = long(ditem[0])
                elif ditem._attrs["type"] == "float": retdict[ditem._attrs["name"]] = float(ditem[0])
                elif ditem._attrs["type"] == "list": retdict[ditem._attrs["name"]] = self.FetchList(ditem)
                elif ditem._attrs["type"] == "dict": retdict[ditem._attrs["name"]] = self.FetchDict(ditem)
                else: retdict[ditem._attrs["name"]] = str( self.normal(ditem[0]) )
            else: retdict[ditem._attrs["name"]] = ""
        return retdict

    def GetDict(self, plugname, dictname, defaultval, verbose=0):
        dictname = self.safe(dictname)
        for plugin in self.xml_dom:
            if plugname == plugin._name:
                for child in plugin._dir:
                    if child._name == dictname and child._attrs["type"] == "dict": return self.FetchDict(child)
        else:
            if verbose:
                print "plugindb: no value has been stored for " + dictname + " in " + plugname + " so the default has been returned"
            return defaultval

    def safe(self, string):
        return string.replace("<", "$$lt$$").replace(">", "$$gt$$").replace("&","$$amp$$").replace('"',"$$quote$$")

    def normal(self, string):
        return string.replace("$$lt$$", "<").replace("$$gt$$", ">").replace("$$amp$$","&").replace("$$quote$$",'"')

    def SaveDoc(self):
        f = open(self.filename, "w")
        f.write(self.xml_dom.__repr__(1, 1))
        f.close()

    def LoadDoc(self):
        xml_file = open(self.filename)
        plugindb = xml_file.read()
        xml_file.close()
        return xmltramp.parse(plugindb)
