from orpg.mapper.map_msg import *
from orpg.tools.orpg_log import debug
from xml.etree.ElementTree import parse, tostring

class game_group:
    def __init__( self, id, name, pwd, desc="", 
                    boot_pwd="", minVersion="", 
                    mapFile=None, messageFile=None, persist=0 ):
        self.id = id
        self.name = name
        self.desc = desc
        self.minVersion = minVersion
        self.messageFile = messageFile
        self.players = []
        self.pwd = pwd
        self.boot_pwd = boot_pwd
        self.game_map = map_msg()
        self.lock = Lock()
        self.moderated = 0
        self.voice = {}
        self.persistant = persist
        if mapFile != None: tree = parse(mapFile)
        else: tree = parse(dir_struct["template"] + "default_map.xml")
        tree = tree.getroot()
        self.game_map.init_from_xml(tostring(tree))

    def add_player(self,id):
        self.players.append(id)

    def remove_player(self,id):
        if self.voice.has_key(id): del self.voice[id]
        self.players.remove(id)

    def get_num_players(self):
        num =  len(self.players)
        return num

    def get_player_ids(self):
        tmp = self.players
        return tmp

    def check_pwd(self,pwd):
        return (pwd==self.pwd)

    def check_boot_pwd(self,pwd):
        return (pwd==self.boot_pwd)

    def check_version(self,ver):
        if (self.minVersion == ""):
            return 1
        minVersion=self.minVersion.split('.')
        version=ver.split('.')
        for i in range(min(len(minVersion),len(version))):
            w=max(len(minVersion[i]),len(version[i]))
            v1=minVersion[i].rjust(w);
            v2=version[i].rjust(w);
            if v1<v2: return 1
            if v1>v2: return 0

        if len(minVersion)>len(version): return 0
        return 1

    #depreciated - see send_group_list()
    def toxml(self, act="new"):
        #  Please don't add the boot_pwd to the xml, as this will give it away to players watching their console
        xml_data = "<group id='" + self.id
        xml_data += "' name='" + self.name
        xml_data += "' pwd='" + str(self.pwd!="")
        xml_data += "' players='" + str(self.get_num_players())
        xml_data += "' action='" + act + "' />"
        return xml_data
