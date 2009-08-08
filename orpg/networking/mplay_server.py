#!/usr/bin/python2.1
# Copyright (C) 2000-2001 The OpenRPG Project
#
#        openrpg-dev@lists.sourceforge.net
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
# File: mplay_server.py
# Author: Chris Davis
# Maintainer:
# Version:
#   $Id: mplay_server.py,v 1.155 2008/01/24 03:52:03 digitalxero Exp $
#
# Description: This file contains the code for the server of the multiplayer
# features in the orpg project.
#


# 04-15-2005 [Snowdog]: Added patch from Brandan Yares (xeriar). Reference: patch tracker id #1182076

__version__ = "$Id: mplay_server.py,v 1.155 2008/01/24 03:52:03 digitalxero Exp $"

#!/usr/bin/env python
"""
<msg to='' from='' group_id='' />
<player id='' ip='' group_id='' name='' action='new,del,group,update' status="" version=""/>
<group id='' name='' pwd='' players='' action='new,del,update' />
<create_group from='' pwd='' name='' />
<join_group from='' pwd='' group_id='' />
<role action='set,get,display' player='' group_id='' boot_pwd='' role=''/>
"""

from mplay_client import *
from mplay_client import MPLAY_LENSIZE
import orpg.dirpath
import orpg.tools.validate
import gc
import cgi
import sys
import string
import time
import urllib
from orpg.mapper.map_msg import *
from threading import Lock, RLock
from struct import pack, unpack, calcsize
from meta_server_lib import *
import traceback
import re

# Import the minidom XML module
from xml.dom import minidom

# Snag the version number
from orpg.orpg_version import *

#Plugins
from server_plugins import ServerPlugins

def id_compare(a,b):
    "converts strings to intergers for list sort comparisons for group and player ids so they end up in numeric order"
    return cmp(int(a),int(b))


class game_group(object):
    def __init__( self, id, name, pwd, desc="", boot_pwd="", minVersion="", mapFile=None, messageFile=None, persist =0 ):
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
        self.mapFile = None

        if mapFile != None:
            self.mapFile = mapFile
            f = open( mapFile )
            tree = f.read()
            f.close()

        else:
            f = open(orpg.dirpath.dir_struct["template"] + "default_map.xml")
            tree = f.read()
            f.close()

        self.game_map.init_from_xml(tree)

    def save_map(self):
        if self.mapFile is not None and self.persistant == 1 and self.mapFile.find("default_map.xml") == -1:
            f = open(self.mapFile, "w")
            f.write(self.game_map.get_all_xml())
            f.close()


    def add_player(self,id):
        self.players.append(id)

    def remove_player(self,id):
        if self.voice.has_key(id):
            del self.voice[id]
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
        for i in xrange(min(len(minVersion),len(version))):
            w=max(len(minVersion[i]),len(version[i]))
            v1=minVersion[i].rjust(w);
            v2=version[i].rjust(w);
            if v1<v2:
                return 1
            if v1>v2:
                return 0

        if len(minVersion)>len(version):
            return 0
        return 1

    #depreciated - see send_group_list()
    def toxml(self,act="new"):
        #  Please don't add the boot_pwd to the xml, as this will give it away to players watching their console
        xml_data = "<group id=\"" + self.id
        xml_data += "\" name=\"" + self.name
        xml_data += "\" pwd=\"" + str(self.pwd!="")
        xml_data += "\" players=\"" + str(self.get_num_players())
        xml_data += "\" action=\"" + act + "\" />"
        return xml_data



class client_stub(client_base):
    def __init__(self,inbox,sock,props,log):
        client_base.__init__(self)
        self.ip = props['ip']
        self.role = props['role']
        self.id = props['id']
        self.group_id = props['group_id']
        self.name = props['name']
        self.version = props['version']
        self.protocol_version = props['protocol_version']
        self.client_string = props['client_string']
        self.inbox = inbox
        self.sock = sock
        self.timeout_time = None
        self.log_console = log
        self.ignorelist = {}

    # implement from our base class
    def isServer( self ):
        return 1

    def clear_timeout(self):
        self.timeout_time = None

    def check_time_out(self):
        if self.timeout_time==None:
            self.timeout_time = time.time()
        curtime = time.time()
        diff = curtime - self.timeout_time
        if diff > 1800:
            return 1
        else:
            return 0

    def send(self,msg,player,group):
        if self.get_status() == MPLAY_CONNECTED:
            self.outbox.put("<msg to='" + player + "' from='0' group_id='" + group + "' />" + msg)

    def change_group(self,group_id,groups):
        old_group_id = str(self.group_id)
        groups[group_id].add_player(self.id)
        groups[old_group_id].remove_player(self.id)
        self.group_id = group_id
        self.outbox.put(self.toxml('group'))
        msg = groups[group_id].game_map.get_all_xml()
        self.send(msg,self.id,group_id)
        return old_group_id

    def self_message(self,act):
        self.send(act,self.id,self.group_id)

    def take_dom(self,xml_dom):
        self.name = xml_dom.getAttribute("name")
        self.text_status = xml_dom.getAttribute("status")


######################################################################
######################################################################
##
##
##   MPLAY SERVER
##
##
######################################################################
######################################################################

class mplay_server:
    def __init__(self, log_console=None, name=None):
        self.log_to_console = 1
        self.log_console = log_console
        self.alive = 1
        self.players = {}
        self.listen_event = Event()
        self.incoming_event = Event()
        self.incoming = Queue.Queue(0)
        self.p_lock = RLock()
        self.next_player_id = 1
        self.plugin_player_id = -1
        self.next_group_id = 100
        self.metas = {}              #  This holds the registerThread objects for each meta
        self.be_registered = 0       #  Status flag for whether we want to be registered.
        self.serverName = name            #  Name of this server in the metas
        self.boot_pwd = ""
        self.server_address = None # IP or Name of server to post to the meta. None means the meta will auto-detect it.
        self.defaultMessageFile = None
        self.userPath = orpg.dirpath.dir_struct["user"]
        self.lobbyMapFile = "Lobby_map.xml"
        self.lobbyMessageFile = "LobbyMessage.html"
        self.banFile = "ban_list.xml"
        self.show_meta_messages = 0
        self.log_network_messages = 0
        self.allow_room_passwords = 1
        self.silent_auto_kick = 0
        self.zombie_time = 480 #time in minutes before a client is considered a ZOMBIE
        self.minClientVersion = SERVER_MIN_CLIENT_VERSION
        self.maxSendSize = 1024
        self.server_port = OPENRPG_PORT
        self.allowRemoteKill = False
        self.allowRemoteAdmin = True
        self.sendLobbySound = False
        self.lobbySound = 'http://www.digitalxero.net/music/mus_tavern1.bmu'

    def initServer(self, **kwargs):
        for atter, value in kwargs.iteritems():
            setattr(self, atter, value)
        self.validate = orpg.tools.validate.Validate(self.userPath)
        self.validate.config_file( self.lobbyMapFile, "default_Lobby_map.xml" )
        self.validate.config_file( self.lobbyMessageFile, "default_LobbyMessage.html" )
        self.server_start_time = time.time()

        # Since the server is just starting here, we read in the XML configuration
        # file.  Notice the lobby is still created here by default.
        self.groups = { '0': game_group('0','Lobby','','The game lobby', '', '', self.userPath + self.lobbyMapFile, self.userPath + self.lobbyMessageFile, 1)}
        # Make sure the server's name gets set, in case we are being started from
        # elsewhere.  Basically, if it's passed in, we'll over ride what we were
        # prompted for.  This should never really happen at any rate.

        self.initServerConfig()
        self.listen_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.listen_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.listen_thread = thread.start_new_thread(self.listenAcceptThread, (0,))
        self.in_thread = thread.start_new_thread(self.message_handler,(0,))

        #  Starts the player reaper thread.  See self.player_reaper_thread_func() for more explanation
        self.player_reaper_thread = thread.start_new_thread(self.player_reaper_thread_func,(0,))
        thread.start_new_thread(self.PluginThread,())
        self.svrcmds = {}
        self.initsvrcmds()
        self.ban_list = {}
        self.initBanList()

    def addsvrcmd(self, cmd, function):
        if not self.svrcmds.has_key(cmd):
            self.svrcmds[cmd] = {}
            self.svrcmds[cmd]['function'] = function

    def initsvrcmds(self):
        self.addsvrcmd('msg', self.incoming_msg_handler)
        self.addsvrcmd('player', self.incoming_player_handler)
        self.addsvrcmd('admin', self.remote_admin_handler)
        self.addsvrcmd('alter', self.do_alter)
        self.addsvrcmd('role', self.do_role)
        self.addsvrcmd('ping', self.do_ping)
        self.addsvrcmd('system', self.do_system)
        self.addsvrcmd('join_group', self.join_group)
        self.addsvrcmd('create_group', self.create_group)
        self.addsvrcmd('moderate', self.moderate_group)
        self.addsvrcmd('plugin', self.plugin_msg_handler)
        self.addsvrcmd('sound', self.sound_msg_handler)


    # This method reads in the server's ban list added by Darren
    def initBanList( self ):
        self.log_msg("Processing Ban List File...")

        # make sure the server_ini.xml exists!
        self.validate.config_file(self.banFile, "default_ban_list.xml" )

        # try to use it.
        try:
            self.banDom = minidom.parse(self.userPath + 'ban_list.xml')
            self.banDom.normalize()
            self.banDoc = self.banDom.documentElement

            for element in self.banDom.getElementsByTagName('banned'):
                playerName = element.getAttribute( 'name' ).replace("&", "&amp;").replace("<", "&lt;").replace('"', "&quot;").replace(">", "&gt;")
                playerIP = element.getAttribute('ip')
                self.ban_list[playerIP] = {}
                self.ban_list[playerIP]['ip'] = playerIP
                self.ban_list[playerIP]['name'] = playerName
                self.log_msg(str(playerName) + " " + str(playerIP) + " is banned.")
            self.saveBanList()
        except Exception, e:
            self.log_msg("Exception in initBanList() " + str(e))

    # This method writes out the server's ban list added by Darren
    def saveBanList( self ):
        self.log_msg("Saving Ban List File...")

        # try to use it.
        try:
            data = []
            data.append("<server>\n")
            for ip in self.ban_list:
                data.append('    <banned name="' + str(self.ban_list[ip]['name'].replace("&amp;", "&").replace("&lt;", "<").replace("&quot;", '"').replace("&gt;", ">")) + '" ip="' + str(self.ban_list[ip]['ip']) + '" />' + "\n")
            data.append("</server>")
            file = open(self.userPath + self.banFile ,"w")
            file.write("".join(data))
            file.close()
        except Exception, e:
            self.log_msg("Exception in saveBanList() " + str(e))

    # This method reads in the server's configuration file and reconfigs the server
    # as needed, over-riding any default values as requested.
    def initServerConfig(self):
        self.log_msg("Processing Server Configuration File... " + self.userPath)
        # make sure the server_ini.xml exists!
        self.validate.config_file( "server_ini.xml", "default_server_ini.xml" )
        # try to use it.
        try:
            self.configDom = minidom.parse(self.userPath + 'server_ini.xml')
            self.configDom.normalize()
            self.configDoc = self.configDom.documentElement

            if hasattr(self, 'bootPassword'): self.boot_pwd = self.bootPassword

            else:
                if self.configDoc.hasAttribute("admin"): self.boot_pwd = self.configDoc.getAttribute("admin") 
                elif self.configDoc.hasAttribute("boot"): self.boot_pwd = self.configDoc.getAttribute("boot") 

                if len(self.boot_pwd) < 1: self.boot_pwd = raw_input("Enter admin password:  ")

            if not hasattr(self, 'reg') and self.configDoc.hasAttribute("register"):
                self.reg = self.configDoc.getAttribute("register")
            if not len(self.reg) > 0 or self.reg[0].upper() not in ("Y", "N"):
                opt = raw_input("Do you want to post your server to the OpenRPG Meta Server list? (y,n) ")
                if len(opt) and (opt[0].upper() == 'Y'): self.reg = 'Y'
                else: self.reg = 'N'
            LobbyName = 'Lobby'
            if self.configDoc.hasAttribute("lobbyname"): LobbyName = self.configDoc.getAttribute("lobbyname")
            map_node = service_node = self.configDoc.getElementsByTagName("map")[0]
            msg_node = service_node = self.configDoc.getElementsByTagName("message")[0]
            mapFile = map_node.getAttribute('file')
            msgFile = msg_node.getAttribute('file')
            if mapFile == '': mapFile = 'Lobby_map.xml'
            if msgFile == '': msgFile = 'LobbyMessage.html'
            # Update the lobby with the passwords if they've been specified
            if len(self.boot_pwd):
                self.groups = {'0': game_group( '0', LobbyName, "", 'The game lobby', self.boot_pwd, "",
                                                 self.userPath + mapFile.replace("myfiles/", ""),
                                                 self.userPath + msgFile.replace("myfiles/", ""), 1 )
                                }

            # set ip or dns name to send to meta server
            service_node = self.configDoc.getElementsByTagName("service")[0]
            address = service_node.getAttribute("address")
            address = address.lower()
            if address == "" or address == "hostname/address" or address == "localhost": self.server_address = None
            else: self.server_address = address
            self.server_port = OPENRPG_PORT
            if service_node.hasAttribute("port"): self.server_port = int(service_node.getAttribute("port"))
            if self.configDoc.hasAttribute("name") and len(self.configDoc.getAttribute("name")) > 0 :
                self.name = self.configDoc.getAttribute("name")
            else:
                if self.reg[0].upper() == "Y":
                    if self.name == None: self.name = raw_input("Server Name? ")
                    self.register()

            # Get the minimum openrpg version from config if available
            # if it isn't set min version to internal default.
            #
            # server_ini.xml entry for version tag...
            # <version min="x.x.x">
            try:
                mver = self.configDoc.getElementsByTagName("version")[0]
                self.minClientVersion = mver.getAttribute("min")
            except: self.minClientVersion = SERVER_MIN_CLIENT_VERSION #from orpg/orpg_version.py
            self.defaultMessageFile = ""
            # This try/except bit is to allow older versions of python to continue without a list error.



            #------------------------[ START <AUTOKICK> TAG PROCESSING ]--------------
            # Auto-kick option defaults for silent booting and
            # setting the default zombie-client delay time --Snowdog 9/05
            #
            # server_ini.xml entry for autikick tag...
            # <autokick silent=["no","yes"] delay="(# of seconds)">

            try:
                ak = self.configDoc.getElementsByTagName("autokick")[0]
                if ak.hasAttribute("silent"):
                    if ((ak.getAttribute("silent")).lower() == "yes"): self.silent_auto_kick = 1
                    else: self.silent_auto_kick = 0
                if ak.hasAttribute("delay"):
                    try:
                        delay = int(ak.getAttribute("delay"))
                        self.zombie_time = delay
                    except:
                        #delay value cannot be converted into an int use defaut
                        self.zombie_time = 480 #(default 8 mins)
                        self.log_msg("**WARNING** Error with autokick delay string using default (480 sec)")

            except:
                self.silent_auto_kick = 0 #(default to off)
                self.zombie_time = 480 #(default 8 mins)
                self.log_msg("**WARNING** Error loading autokick settings... using defaults")

            alk = ""
            if (self.silent_auto_kick == 1): alk = "(Silent Mode)"
            self.log_msg("Auto Kick:  Delay="+str(self.zombie_time) + " " + alk)
            #------------------------[ END <AUTOKICK> TAG PROCESSING ]--------------



            #-------------------------------[ START <ROOM_DEFAULT> TAG PROCESSING ]--------------------
            #
            # New room_defaults configuration option used to set various defaults
            # for all user created rooms on the server. Incorporates akomans older
            # default room message code (from above)      --Snowdog 11/03
            #
            # option syntax
            # <room_defaults passwords="yes" map="myfiles/LobbyMap.xml" message="myfiles/LobbyMessage.html" />

            #default settings for tag options...
            roomdefault_msg = str(self.defaultMessageFile) #no message is the default
            roomdefault_map = "" #use lobby map as default
            roomdefault_pass = 1 #allow passwords


            #pull information from config file DOM
            try:
                roomdefaults = self.configDom.getElementsByTagName("room_defaults")[0]
                #rd.normalize()
                #roomdefaults = self.rd.documentElement
                try:
                    setting = roomdefaults.getElementsByTagName('passwords')[0]
                    rpw = setting.getAttribute('allow')
                    if rpw == "no" or rpw == "0":
                        roomdefault_pass = 0
                        self.log_msg("Room Defaults: Disallowing Passworded Rooms")
                    else: self.log_msg("Room Defaults: Allowing Passworded Rooms")
                except: self.log_msg("Room Defaults: [Warning] Allowing Passworded Rooms")
                try:
                    setting = roomdefaults.getElementsByTagName('map')[0]
                    map = setting.getAttribute('file')
                    if map != "":
                        roomdefault_map = self.userPath + map.replace("myfiles/", "")
                        self.log_msg("Room Defaults: Using " + str(map) + " for room map")
                except:
                    self.log_msg("Room Defaults: [Warning] Using Default Map")

                try:
                    setting = roomdefaults.getElementsByTagName('message')[0]
                    msg = setting.getAttribute('file')
                    if msg != "":
                        if msg[:4].lower() == 'http': roomdefault_msg = msg
                        else: roomdefault_msg = self.userPath + msg.replace("myfiles/", "")
                        self.log_msg("Room Defaults: Using " + str(msg) + " for room messages")
                except: print ("Room Defaults: [Warning] Using Default Message")
            except:
                traceback.print_exc()
                self.log_msg("**WARNING** Error loading default room settings from configuration file. Using internal defaults.")


            #set the defaults
            if roomdefault_msg != "" or roomdefault_msg != None:
                self.defaultMessageFile = roomdefault_msg  #<room_defaults> tag superceeds older <newrooms> tag
            else: self.defaultMessageFile = None

            if roomdefault_map != "" or roomdefault_map != None:
                self.defaultMapFile = roomdefault_map  #<room_defaults> tag superceeds older <newrooms> tag
            else: self.defaultMapFile = None

            ##### room default map not handled yet. SETTING IGNORED
            if roomdefault_pass == 0: self.allow_room_passwords = 0
            else: self.allow_room_passwords = 1

            #-------------------------------[ END <ROOM_DEFAULT> TAG PROCESSING ]--------------------


            ###Server Cheat message
            try:
                cheat_node = self.configDoc.getElementsByTagName("cheat")[0]
                self.cheat_msg = cheat_node.getAttribute("text")
            except:
                self.cheat_msg = "**FAKE ROLL**"
                self.log_msg("**WARNING** <cheat txt=\"\"> tag missing from server configuration file. Using empty string.")



            # should validate protocal
            validate_protocol_node = self.configDom.getElementsByTagName("validate_protocol ")

            self.validate_protocol = 1

            if(validate_protocol_node): self.validate_protocol = (validate_protocol_node[0].getAttribute("value") == "True")
            if(self.validate_protocol != 1): self.log_msg("Protocol Validation: OFF")
            self.makePersistentRooms()

            self.log_msg("Server Configuration File: Processing Completed.")

        except Exception, e:
            traceback.print_exc()
            self.log_msg("Exception in initServerConfig() " + str(e))


    def makePersistentRooms(self):
        'Creates rooms on the server as defined in the server config file.'

        for element in self.configDom.getElementsByTagName('room'):
            roomName = element.getAttribute('name')
            roomPassword = element.getAttribute('password')
            bootPassword = element.getAttribute('boot')

            # Conditionally check for minVersion attribute
            if element.hasAttribute('minVersion'): minVersion = element.getAttribute('minVersion')
            else: minVersion = ""

            # Extract the map filename attribute from the map node
            # we only care about the first map element found -- others are ignored
            mapElement = element.getElementsByTagName('map')[0]
            mapFile = self.userPath + mapElement.getAttribute('file').replace("myfiles/", "")

            messageElement = element.getElementsByTagName('message')[0]
            messageFile = messageElement.getAttribute('file')

            if messageFile[:4] != 'http': messageFile = self.userPath + messageFile.replace("myfiles/", "")

            # Make sure we have a message to even mess with
            if(len(messageFile) == 0): messageFile = self.defaultMessageFile

            if(len(mapFile) == 0): mapFile = self.defaultMapFile

            moderated = 0
            if element.hasAttribute('moderated') and element.getAttribute('moderated').lower() == "true": moderated = 1

            #create the new persistant group
            self.new_group(roomName, roomPassword, bootPassword, minVersion, mapFile, messageFile, persist = 1, moderated=moderated)



    def isPersistentRoom(self, id):
        'Returns True if the id is a persistent room (other than the lobby), otherwise, False.'

        # altered persistance tracking from simple room id based to per-group setting
        # allows arbitrary rooms to be marked as persistant without needing the self.persistRoomThreshold
        # -- Snowdog 4/04
        try:
            id = str(id) #just in case someone sends an int instead of a str into the function
            if id not in self.groups: return 0 #invalid room, can't be persistant
            pr = (self.groups[id]).persistant
            return pr
        except:
            self.log_msg("Exception occured in isPersistentRoom(self,id)")
            return 0



    #-----------------------------------------------------
    #  Toggle Meta Logging  -- Added by Snowdog 4/03
    #-----------------------------------------------------
    def toggleMetaLogging(self):
        if self.show_meta_messages != 0:
            self.log_msg("Meta Server Logging: OFF")
            self.show_meta_messages = 0
        else:
            self.log_msg("Meta Server Logging: ON")
            self.show_meta_messages = 1


    #-----------------------------------------------------
    #  Start/Stop Network Logging to File  -- Added by Snowdog 4/03
    #-----------------------------------------------------
    def NetworkLogging(self, mode = 0):
        if mode == 0:
            self.log_msg("Network Logging: OFF")
            self.log_network_messages = 0
        elif mode == 1:
            self.log_msg("Network Logging: ON (composite logfile)")
            self.log_network_messages = 1
        elif mode == 2:
            self.log_msg("Network Logging: ON (split logfiles)")
            self.log_network_messages = 2
        else: return
        #when log mode changes update all connection stubs
        for n in self.players:
            try: self.players[n].EnableMessageLogging = mode
            except: self.log_msg("Error changing Message Logging Mode for client #" + str(self.players[n].id))
    def NetworkLoggingStatus(self):
        if self.log_network_messages == 0: return "Network Traffic Log: Off"
        elif self.log_network_messages == 1: return "Network Traffic Log: Logging (composite file)"
        elif self.log_network_messages == 2: return "Network Traffic Log: Logging (inbound/outbound files)"
        else: self.log_msg("Network Traffic Log: [Unknown]")




    def register_callback(instance, xml_dom = None,source=None):
        if xml_dom:    # if we get something
            if source == getMetaServerBaseURL():    # if the source of this DOM is the authoritative meta
                try:
                    metacache_lock.acquire()
                    curlist = getRawMetaList()      #  read the raw meta cache lines into a list
                    updateMetaCache(xml_dom)        #  update the cache from the xml
                    newlist = getRawMetaList()      #  read it into a second list
                finally:
                    metacache_lock.release()

                if newlist != curlist:          #  If the two lists aren't identical
                                                #  then something has changed.
                    instance.register()             #  Call self.register()
                                                #  which will force a re-read of the meta cache and
                                                #  redo the registerThreads
        else: instance.register()

                # Eventually, reset the MetaServerBaseURL here

    ## Added to help clean up parser errors in the XML on clients
    ## due to characters that break welformedness of the XML from
    ## the meta server.
    ## NOTE: this is a stopgap measure -SD
    def clean_published_servername(self, name):
        #clean name of all apostrophes and quotes
        badchars = "\"\\`><"
        for c in badchars: name = name.replace(c,"")
        return name

    def registerRooms(self, args=None):
        rooms = ''
        id = '0'
        time.sleep(500)
        for rnum in self.groups.keys():
            rooms += urllib.urlencode( {"room_data[rooms][" + str(rnum) + "][name]":self.groups[rnum].name,
                                        "room_data[rooms][" + str(rnum) + "][pwd]":str(self.groups[rnum].pwd != "")})+'&'

            for pid in self.groups[rnum].players:
                rooms += urllib.urlencode( {"room_data[rooms][" + str(rnum) + "][players]["+str(pid)+"]":self.players[pid].name,})+'&'


        for meta in self.metas.keys():
            while id == '0':
                id, cookie = self.metas[meta].getIdAndCookie()
                data = urllib.urlencode( {"room_data[server_id]":id,
                                        "act":'registerrooms'})
            get_server_dom(data+'&'+rooms, self.metas[meta].path)


    def register(self,name_given=None):
        if name_given == None: name = self.name
        else: self.name = name = name_given

        name = self.clean_published_servername(name)

        #  Set up the value for num_users
        if self.players: num_players = len(self.players)
        else: num_players = 0

        #  request only Meta servers compatible with version 2
        metalist = getMetaServers(versions=["2"])
        if self.show_meta_messages != 0:
            self.log_msg("Found these valid metas:")
            for meta in metalist: self.log_msg("Meta:" + meta)

        #  Go through the list and see if there is already a running register
        #  thread for the meta.
        #  If so, call it's register() method
        #  If not, start one, implicitly calling the new thread's register() method


        #  iterate through the currently running metas and prune any
        #  not currently listed in the Meta Server list.
        if self.show_meta_messages != 0: self.log_msg( "Checking running register threads for outdated metas.")
        for meta in self.metas.keys():
            if self.show_meta_messages != 0: self.log_msg("meta:" + meta + ": ")
            if not meta in metalist:  # if the meta entry running is not in the list
                if self.show_meta_messages != 0: self.log_msg( "Outdated.  Unregistering and removing")
                self.metas[meta].unregister()
                del self.metas[meta]
            else: 
                if self.show_meta_messages != 0: self.log_msg( "Found in current meta list.  Leaving intact.")

        #  Now call register() for alive metas or start one if we need one
        for meta in metalist:
            if self.metas.has_key(meta) and self.metas[meta] and self.metas[meta].isAlive():
                self.metas[meta].register(name=name, realHostName=self.server_address, num_users=num_players)
            else:
                self.metas[meta] = registerThread(name=name, realHostName=self.server_address, num_users=num_players, MetaPath=meta, port=self.server_port,register_callback=self.register_callback)
                self.metas[meta].start()

        #The register Rooms thread

        self.be_registered = 1
        thread.start_new_thread(self.registerRooms,(0,))



    def unregister(self):
        #  loop through all existing meta entries
        #  Don't rely on getMetaServers(), as a server may have been
        #  removed since it was started.  In that case, then the meta
        #  would never get unregistered.
        #
        #  Instead, loop through all existing meta threads and unregister them

        for meta in self.metas.values():
            if meta and meta.isAlive(): meta.unregister()
        self.be_registered = 0

        #  This method runs as it's own thread and does the group_member_check every
        #    sixty seconds.  This should eliminate zombies that linger when no one is
        #    around to spook them.  GC: Frequency has been reduced as I question how valid
        #    the implementation is as it will only catch a very small segment of lingering
        #    connections.
    def player_reaper_thread_func(self,arg):
        while self.alive:
            time.sleep(60)

            self.p_lock.acquire()
            for group in self.groups.keys(): self.check_group_members(group)
            self.p_lock.release()

    #This thread runs ever 250 miliseconds, and checks various plugin stuff
    def PluginThread(self):
        while self.alive:
            self.p_lock.acquire()
            players = ServerPlugins.getPlayer()

            for player in players:
                if player is not None: pass #Do something here so they can show up in the chat room for non web users'
            data = ServerPlugins.preParseOutgoing()
            for msg in data:
                try:
                    xml_dom = parseXml(msg)
                    xml_dom = xml_dom._get_documentElement()

                    if xml_dom.hasAttribute('from') and int(xml_dom.getAttribute('from')) > -1:
                        xml_dom.setAttribute('from', '-1')

                    xml_dom.setAttribute('to', 'all')
                    self.incoming_msg_handler(xml_dom, msg)
                    xml_dom.unlink()
                except: pass

            self.p_lock.release()
            time.sleep(0.250)


    def sendMsg( self, sock, msg, useCompression=False, cmpType=None):
        """Very simple function that will properly encode and send a message to te
        remote on the specified socket."""

        if useCompression and cmpType != None:
            mpacket = cmpType.compress(msg)
            lpacket = pack('!i', len(mpacket))
            sock.send(lpacket)

            offset = 0
            while offset < len(mpacket):
                slice = buffer(mpacket, offset, len(mpacket)-offset)
                sent = sock.send(slice)
                offset += sent
            sentm = offset
        else: 
            length = len( msg ) # Calculate our message length
            lp = pack('!i', length) # Encode the message length into network byte order
            try:
                sentl = sock.send( lp ) # Send the encoded length
                sentm = sock.send( msg ) # Now, send the message the the length was describing
            except socket.error, e: self.log_msg( e )
            except Exception, e: self.log_msg( e )


    def recvData( self, sock, readSize ):
        """Simple socket receive method.  This method will only return when the exact
        byte count has been read from the connection, if remote terminates our
        connection or we get some other socket exception."""

        data = ""
        offset = 0
        try:
            while offset != readSize:
                frag = sock.recv( readSize - offset )
                rs = len( frag ) # See if we've been disconnected
                if rs <= 0:
                    # Loudly raise an exception because we've been disconnected!
                    raise IOError, "Remote closed the connection!"
                else: # Continue to build complete message
                    offset += rs
                    data += frag

        except socket.error, e:
            self.log_msg("Socket Error: recvData(): " +  e )
            data = ""
        return data

    def recvMsg(self, sock, useCompression=False, cmpType=None):
        """This method now expects to receive a message having a 4-byte prefix length.  It will ONLY read
        completed messages.  In the event that the remote's connection is terminated, it will throw an
        exception which should allow for the caller to more gracefully handles this exception event.

        Because we use strictly reading ONLY based on the length that is told to use, we no longer have to
        worry about partially adjusting for fragmented buffers starting somewhere within a buffer that we've
        read.  Rather, it will get ONLY a whole message and nothing more.  Everything else will remain buffered
        with the OS until we attempt to read the next complete message."""

        msgData = ""
        try:
            lenData = self.recvData( sock, MPLAY_LENSIZE )
            # Now, convert to a usable form
            (length,) = unpack('!i', lenData)
            # Read exactly the remaining amount of data
            msgData = self.recvData( sock, length )
            try:
                if useCompression and cmpType != None: msgData = cmpType.decompress(msgData)
            except: traceback.print_exc()

        except Exception, e: self.log_msg( "Exception: recvMsg(): " + str(e) )
        return msgData


    def kill_server(self):
        self.alive = 0
        self.log_msg("Server stopping...")
        self.unregister()                    # unregister from the Meta
        for p in self.players.itervalues():
            p.disconnect()
            self.incoming.put("<system/>")

        for g in self.groups.itervalues():
            g.save_map()

        try:
            ip = socket.gethostbyname(socket.gethostname())
            kill = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            kill.connect((ip, self.server_port))

            # Now, send the "system" command using the correct protocol format
            self.sendMsg( kill, "<system/>" )
            kill.close()
        except:
            pass

        self.listen_sock.close()
        self.listen_event.wait(10)
        self.incoming_event.wait(10)
        self.log_msg("Server stopped!")



    def log_msg(self,msg):
        if self.log_to_console:
            if self.log_console:
                self.log_console(msg)
            else:
                print str(msg)


    def print_help(self):
        print
        print "Commands: "
        print "'kill' or 'quit' - to stop the server"
        print "'broadcast' - broadcast a message to all players"
        print "'list' - list players and groups"
        print "'dump' - to dump player data"
        print "'dump groups' - to list the group names and ids only"
        print "'group n' - to list details about one group only"
        print "'register' - To register the server as name.  Also used to change the server's name if registered."
        print "'unregister' - To remove this server from the list of servers"
        print "'get lobby boot password' - to show the Lobby's boot password"
        print "'set lobby boot password' - to set the Lobby's boot password"
        print "'log' - toggles logging to the console off or on"
        print "'log meta' - toggles logging of meta server messages on or off"
        print "'logfile [off|on|split]' - timestamped network traffic log"
        print "'remove room' - to remove a room from the server"
        print "'kick' - kick a player from the server"
        print "'ban' - ban a player from the server"
        print "'remotekill' - This will toggle the ability to kill the server via the /admin command"
        print "'monitor (#)' - monitors raw network I/O stream to specific client"
        print "'purge clients' - boots all connected clients off the server immediately"
        print "'zombie [set [min]]' - view/set the auto-kick time for zombie clients"
        #drop any clients that are idle for more than 8 hours
        #as these are likely dead clientskick' - kick a player from the server"
        print "'uptime' - reports how long server has been running"
        print "'roompasswords' - allow/disallow room passwords (toggle)"
        print "'search' - will prompt for pattern and display results"
        print "'sendsize' - will ajust the send size limit"
        print "'remoteadmin' - will toggle remote admin commands"
        print "'togglelobbysound' - Will turn on or off the Auto sending of a sound to all players who join the loby"
        print "'lobbysound' - Lets you specify which sound file to send to players joining the lobby"
        print "'help' or '?' or 'h' - for this help message"
        print


    def broadcast(self,msg):
        self.send_to_all("0","<msg to='all' from='0' group_id='1'><font color='#FF0000'>" + msg + "</font>")


    def console_log(self):
        if self.log_to_console == 1:
            print "console logging now off"
            self.log_to_console = 0
        else:
            print "console logging now on"
            self.log_to_console = 1


    def groups_list(self):
        self.p_lock.acquire()
        try:
            keys = self.groups.keys()
            for k in keys:
                pw = "-"
                pr = " -"
                if self.groups[k].pwd != "":
                    pw = "P"
                if self.isPersistentRoom( k ):
                    pr = " S" #using S for static (P for persistant conflicts with password)
                print "Group: " + k + pr + pw + '  Name: ' + self.groups[k].name
            print

        except Exception, e:
            self.log_msg(str(e))

        self.p_lock.release()

#----------------------------------------------------------------
#  Monitor Function  -- Added by snowdog 2/05
#----------------------------------------------------------------
    def monitor(self, pid, mode=1 ):
        "allows monitoring of a specific user(s) network i/o"
        #if mode is not set to 1 then monitor adds toggles the state
        #of monitoring on the given user

        if (mode == 1):
            for p in self.players:
                try: p.monitor("off")
                except: pass
        try:
            r = (self.players[pid]).set_traffic_monitor("toggle")
            self.log_msg("Monitor: Mode=" + str(r) + " on Player #" + str(pid))
        except:
            self.log_msg("Monitor: Invalid Player ID")
            traceback.print_exc()


    def search(self,patern):
        keys = self.groups.keys()
        print "Search results:"
        for k in keys:
            ids = self.groups[k].get_player_ids()
            for id in ids:
                if self.players[id].id.find(patern)>-1:
                    self.print_player_info(self.players[id])

                elif self.players[id].name.find(patern)>-1:
                    self.print_player_info(self.players[id])

                elif self.players[id].ip.find(patern)>-1:
                    self.print_player_info(self.players[id])

                elif self.players[id].group_id.find(patern)>-1:
                    self.print_player_info(self.players[id])

                elif self.players[id].role.find(patern)>-1:
                    self.print_player_info(self.players[id])

                elif self.players[id].version.find(patern)>-1:
                    self.print_player_info(self.players[id])

                elif self.players[id].protocol_version.find(patern)>-1:
                    self.print_player_info(self.players[id])

                elif self.players[id].client_string.find(patern)>-1:
                    self.print_player_info(self.players[id])


    def print_player_info(self,player):
        print player.id,player.name,player.ip,player.group_id, player.role,player.version,player.protocol_version,player.client_string

    #----------------------------------------------------------------
    #  Uptime Function  -- Added by snowdog 4/03
    #----------------------------------------------------------------
    def uptime(self , mode = 0):
        "returns string containing how long server has been in operation"
        ut = time.time() - self.server_start_time
        d = int(ut/86400)
        h = int( (ut-(86400*d))/3600 )
        m = int( (ut-(86400*d)-(3600*h))/60)
        s = int( (ut-(86400*d)-(3600*h)-(60*m)) )
        uts =  str( "This server has been running for:\n " + str(d) + " days  " + str(h) + " hours  " + str(m) + " min. " + str(s) + " sec.  [" + str(int(ut)) + " seconds]")
        if mode == 0: print uts
        else: return uts

    #-----------------------------------------------------
    #  Toggle Room Password Allow  -- Added by Snowdog 11/03
    #-----------------------------------------------------
    def RoomPasswords(self):
        if self.allow_room_passwords != 0:
            self.allow_room_passwords = 0
            return "Client Created Room Passwords: Disallowed"
        else:
            self.allow_room_passwords = 1
            return "Client Created Room Passwords: Allowed"


    def group_dump(self,k):
        self.p_lock.acquire()
        try:
            print "Group: " + k
            print "    Name:  %s" % self.groups[k].name
            print "    Desc:  %s" % self.groups[k].desc
            print "    Pass:  %s" % self.groups[k].pwd
            print "    Boot:  %s" % self.groups[k].boot_pwd
            print "    Moderated:  %s" % self.groups[k].moderated
            print "    Map:  %s" % self.groups[k].game_map.get_all_xml()
            print
        except Exception, e:
            self.log_msg(str(e))
        self.p_lock.release()

    #----------------------------------------------------------------
    #  Player List  -- Added by snowdog 4/03
    #----------------------------------------------------------------
    def player_list(self):
        "display a condensed list of players on the server"
        self.p_lock.acquire()
        try:
            print "------------[ PLAYER LIST ]------------"
            keys = self.groups.keys()
            keys.sort(id_compare)
            for k in keys:
                groupstring = "Group " + str(k)  + ": " +  self.groups[k].name
                if self.groups[k].pwd != "":
                    groupstring += " (Pass: \"" + self.groups[k].pwd + "\" )"
                print groupstring
                ids = self.groups[k].get_player_ids()
                ids.sort(id_compare)
                for id in ids:
                    if self.players.has_key(id):
                        print "  (%s)%s [IP: %s] %s (%s)" % ((self.players[id]).id, (self.players[id]).name, (self.players[id]).ip, (self.players[id]).idle_status(), (self.players[id]).connected_time_string())
                    else:
                        self.groups[k].remove_player(id)
                        print "Bad Player Ref (#" + id + ") in group"
                if len(ids) > 0: print ""
            print "--------------------------------------"
            print "\nStatistics: groups: " + str(len(self.groups)) + "  players: " +  str(len(self.players))
        except Exception, e:
            self.log_msg(str(e))
        self.p_lock.release()


    def player_dump(self):
        self.p_lock.acquire()
        try:
            keys = self.groups.keys()
            for k in keys:
                print "Group: %s  %s (pass: \"%s\")" % (str(k),self.groups[k].name, self.groups[k].pwd)

                ids = self.groups[k].get_player_ids()
                for id in ids:
                    if self.players.has_key(id):
                        print str(self.players[id])
                    else:
                        self.groups[k].remove_player(id)
                        print "Bad Player Ref (#" + id + ") in group"
        except Exception, e:
            self.log_msg(str(e))

        self.p_lock.release()


    def update_request(self,newsock,xml_dom):
        # handle reconnects

        self.log_msg( "update_request() has been called." )

        # get player id
        id = xml_dom.getAttribute("id")
        group_id = xml_dom.getAttribute("group_id")

        self.p_lock.acquire()
        if self.players.has_key(id):
            self.sendMsg( newsock, self.players[id].toxml("update"), self.players[id].useCompression, self.players[id].compressionType )
            self.players[id].reset(newsock)
            self.players[id].clear_timeout()
            need_new = 0
        else:
            need_new = 1
        self.p_lock.release()

        if need_new:
            self.new_request(newsock,xml_dom)
        else:
            msg = self.groups[group_id].game_map.get_all_xml()
            self.send(msg,id,group_id)


    def new_request(self,newsock,xml_dom,LOBBY_ID='0'):
        #build client stub
        props = {}
        # Don't trust what the client tells us...trust what they connected as!
        props['ip'] = socket.gethostbyname( newsock.getpeername()[0] )

        try:
            props['role'] = xml_dom.getAttribute("role")
        except:
            props['role'] = "GM"

        props['name'] = xml_dom.getAttribute("name")
        props['group_id'] = LOBBY_ID
        props['id'] = str(self.next_player_id)
        props['version'] = xml_dom.getAttribute("version")
        props['protocol_version'] = xml_dom.getAttribute("protocol_version")
        props['client_string'] = xml_dom.getAttribute("client_string")
        self.next_player_id += 1
        new_stub = client_stub(self.incoming,newsock,props,self.log_console)
        if xml_dom.hasAttribute('useCompression'):
            new_stub.useCompression = True

            if xml_dom.hasAttribute('cmpType'):
                cmpType = xml_dom.getAttribute('cmpType')
                if cmpBZ2 and cmpType == 'bz2':
                    new_stub.compressionType = bz2
                elif cmpZLIB and cmpType == 'zlib':
                    new_stub.compressionType = zlib
                else:
                    new_stub.compressionType = None
            else:
                new_stub.compressionType = bz2

        else:
            new_stub.useCompression = False

        #update newly create client stub with network logging state
        new_stub.EnableMessageLogging = self.log_network_messages

        self.sendMsg(newsock, new_stub.toxml("new"), False, None)

        #  try to remove circular refs
        if xml_dom:
            xml_dom.unlink()

        # send confirmation
        data = self.recvMsg(newsock, new_stub.useCompression, new_stub.compressionType)
        try:
            xml_dom = parseXml(data)
            xml_dom = xml_dom._get_documentElement()
        except Exception, e:
            print e
            (remote_host,remote_port) = newsock.getpeername()
            bad_xml_string =  "Your client sent an illegal message to the server and will be disconnected. "
            bad_xml_string += "Please report this bug to the development team at:<br /> "
            bad_xml_string += "<a href=\"http://sourceforge.net/tracker/?group_id=2237&atid=102237\">OpenRPG bugs "
            bad_xml_string += "(http://sourceforge.net/tracker/?group_id=2237&atid=102237)</a><br />"
            self.sendMsg( newsock, "<msg to='" + props['id'] + "' from='" + props['id'] + "' group_id='0' />" + bad_xml_string, new_stub.useCompression, new_stub.compressionType)

            time.sleep(2)
            newsock.close()
            print "Error in parse found from " + str(remote_host) + ".  Disconnected."
            print "  Offending data(" + str(len(data)) + "bytes)=" + data
            print "Exception=" + str(e)

            if xml_dom:
                xml_dom.unlink()
            return

        #start threads and store player

        allowed = 1
        version_string = ""

        if ((props['protocol_version'] != PROTOCOL_VERSION) and self.validate_protocol):
            version_string = "Sorry, this server can't handle your client version. (Protocol mismatch)<br />"
            allowed = 0

        if not self.checkClientVersion(props['version']):
            version_string = "Sorry, your client is out of date. <br />"
            version_string += "This server requires your client be version " + self.minClientVersion + " or higher to connect.<br />"
            allowed = 0

        if not allowed:
            version_string += '  Please go to <a href="http://openrpg.digitalxero.net">http://openrpg.digitalxero.net</a> to find a compatible client.<br />'
            version_string += "If you can't find a compatible client on the website, chances are that the server is running an unreleased development version for testing purposes.<br />"

            self.sendMsg( newsock, "<msg to='" + props['id'] + "' from='0' group_id='0' />" + version_string, new_stub.useCompression, new_stub.compressionType)
            #  Give messages time to flow
            time.sleep(1)
            self.log_msg("Connection terminating due to version incompatibility with client (ver: " + props['version'] + "  protocol: " + props['protocol_version'] + ")" )
            newsock.close()
            if xml_dom:
                xml_dom.unlink()
            return None

        ip = props['ip']
        if self.ban_list.has_key(ip):
            banmsg = "You have been banned from this server.<br />"
            cmsg = "Banned Client: (" + str(props['id']) + ") " + str(props['name']) + " [" + str(props['ip']) + "]"
            self.log_msg(cmsg)
            allowed = 0

            self.sendMsg( newsock, "<msg to='" + props['id'] + "' from='0' group_id='0' />" + banmsg, new_stub.useCompression, new_stub.compressionType)
            #  Give messages time to flow
            time.sleep(1)
            newsock.close()
            if xml_dom:
                xml_dom.unlink()
            return None

        #---- Connection order changed by Snowdog 1/05
        #---- Attempt to register player and send group data
        #---- before displaying lobby message
        #---- Does not solve the Blackhole bug but under some conditions may
        #---- allow for a graceful server response. -SD

        #---- changed method of sending group names to user 8/05
        #---- black hole bug causes the group information to not be sent
        #---- to clients. Not sure why the group messages were being sent to the
        #---- incomming message queue, when they should be sent directly to user
        #---- Does not solve the black hole bug totally -SD

        try:
            if xml_dom.getAttribute("id") == props['id']:
                new_stub.initialize_threads()
                self.p_lock.acquire()
                self.players[props['id']] = new_stub
                self.groups[LOBBY_ID].add_player(props['id']) #always add to lobby on connection.
                self.send_group_list(props['id'])
                self.send_player_list(props['id'],LOBBY_ID)
                self.p_lock.release()

                msg = self.groups[LOBBY_ID].game_map.get_all_xml()
                self.send(msg,props['id'],LOBBY_ID)
                self.send_to_group(props['id'],LOBBY_ID,self.players[props['id']].toxml('new'))
                self.return_room_roles(props['id'],LOBBY_ID)

                # Re-initialize the role for this player incase they came from a different server
                self.handle_role("set",props['id'], "GM",self.groups[LOBBY_ID].boot_pwd, LOBBY_ID)

                cmsg = "Client Connect: (" + str(props['id']) + ") " + str(props['name']) + " [" + str(props['ip']) + "]"
                self.log_msg(cmsg)
                cmsg = ("connect", props) #################################################
                self.log_msg(cmsg)

                #  If already registered then re-register, thereby updating the Meta
                #    on the number of players
                if self.be_registered:
                    self.register()
        except:
            traceback.print_exc()

            #something didn't go right. Notify client and drop the connection
            err_string = "<center>"
            err_string +=  "<hr><b>The server has encountered an error while processing your connection request.</b><hr>"
            err_string += "<br /><i>You are being disconnected from the server.</i><br />"
            err_string += "This error may represent a problem with the server. If you continue to get this message "
            err_string += "please contact the servers administrator to correct the issue.</center> "
            self.sendMsg( newsock, "<msg to='" + props['id'] + "' from='" + props['id'] + "' group_id='0' />" + err_string, new_stub.useCompression, new_stub.compressionType )
            time.sleep(2)
            newsock.close()


        #  Display the lobby message
        self.SendLobbyMessage(newsock,props['id'])

        if xml_dom:
            xml_dom.unlink()


    def checkClientVersion(self, clientversion):
        minv = self.minClientVersion.split('.')
        cver = clientversion.split('.')
        for i in xrange(min(len(minv),len(cver))):
            w=max(len(minv[i]),len(cver[i]))
            v1=minv[i].rjust(w);
            v2=cver[i].rjust(w);
            if v1<v2:
                return 1
            if v1>v2:
                return 0

        if len(minv)>len(cver):
            return 0
        return 1



    def SendLobbyMessage(self, socket, player_id):
        #######################################################################
        #  Display the lobby message
        #  prepend this server's version string to the the lobby message
        try:
            lobbyMsg = "You have connected to an <a href=\"http://www.openrpg.com\">OpenRPG</a> server, version '" + VERSION + "'"

            # See if we have a server name to report!

            if len(self.serverName):
                lobbyMsg += ", named '" + self.serverName + "'."

            else:
                lobbyMsg += "."

            # Add extra line spacing
            lobbyMsg += "\n\n"

            try:
                self.validate.config_file("LobbyMessage.html","default_LobbyMessage.html")
            except:
                pass
            else:
                open_msg = open( self.userPath + "LobbyMessage.html", "r" )
                lobbyMsg += open_msg.read()
                open_msg.close()

            # Send the server's lobby message to the client no matter what
            self.sendMsg(socket, "<msg to='" + player_id + "' from='0' group_id='0' />" + lobbyMsg, self.players[player_id].useCompression, self.players[player_id].compressionType)
            if self.sendLobbySound:
                self.sendMsg(socket, '<sound url="' + self.lobbySound + '" group_id="0" from="0" loop="True" />', self.players[player_id].useCompression, self.players[player_id].compressionType)
            return
        except:
            traceback.print_exc()
        #  End of lobby message code
        #######################################################################


    def listenAcceptThread(self,arg):
        #  Set up the socket to listen on.
        try:
            self.log_msg("\nlisten thread running...")
            adder = ""
            if self.server_address is not None:
                adder = self.server_address
            self.listen_sock.bind(('', self.server_port))
            self.listen_sock.listen(5)

        except Exception, e:
            self.log_msg(("Error binding request socket!", e))
            self.alive = 0


        while self.alive:

            #  Block on the socket waiting for a new connection
            try:
                (newsock, addr) = self.listen_sock.accept()
                ## self.log_msg("New connection from " + str(addr)+ ". Interfacing with server...")

                # Now that we've accepted a new connection, we must immediately spawn a new
                # thread to handle it...otherwise we run the risk of having a DoS shoved into
                # our face!  :O  After words, this thread is dead ready for another connection
                # accept to come in.
                thread.start_new_thread(self.acceptedNewConnectionThread, ( newsock, addr ))

            except:
                print "The following exception caught accepting new connection:"
                traceback.print_exc()

        #  At this point, we're done and cleaning up.
        self.log_msg("server socket listening thread exiting...")
        self.listen_event.set()



    def acceptedNewConnectionThread( self, newsock, addr ):
        """Once a new connection comes in and is accepted, this thread starts up to handle it."""

        # Initialize xml_dom
        xml_dom = None
        data = None

        # get client info and send othe client info
        # If this receive fails, this thread should exit without even attempting to process it
        self.log_msg("Connection from " + str(addr) + " has been accepted.  Waiting for data...")

        data = self.recvMsg( newsock )

        if data=="" or data == None:
            self.log_msg("Connection from " + str(addr) + " failed. Closing connection.")
            try:
                newsock.close()
            except Exception, e:
                self.log_msg( str(e) )
                print str(e)
            return #returning causes connection thread instance to terminate


        if data == "<system/>":
            try:
                newsock.close()
            except:
                pass
            return #returning causes connection thread instance to terminate

        #  Clear out the xml_dom in preparation for new stuff, if necessary
        try:
            if xml_dom:
                xml_dom.unlink()

        except:
            self.log_msg( "The following exception caught unlinking xml_dom:")
            self.log_msg("Continuing")

            try:
                newsock.close()
            except:
                pass
            return #returning causes connection thread instance to terminate

        #  Parse the XML received from the connecting client
        try:
            xml_dom = parseXml(data)
            xml_dom = xml_dom._get_documentElement()

        except:
            try:
                newsock.close()
            except:
                pass
            self.log_msg( "Error in parse found from " + str(addr) + ".  Disconnected.")
            self.log_msg("  Offending data(" + str(len(data)) + "bytes)=" + data)
            self.log_msg( "Exception:")
            traceback.print_exc()
            return #returning causes connection thread instance to terminate

        #  Determine the correct action and execute it
        try:
            # get action
            action = xml_dom.getAttribute("action")

            # Figure out what type of connection we have going on now
            if action == "new":
                self.new_request(newsock,xml_dom)

            elif action == "update":
                self.update_request(newsock,xml_dom)

            else:
                self.log_msg("Unknown Join Request!")

        except Exception, e:
            print "The following  message: " + str(data)
            print "from " + str(addr) + " created the following exception: "
            traceback.print_exc()
            return #returning causes connection thread instance to terminate

        #  Again attempt to clean out DOM stuff
        try:
            if xml_dom:
                xml_dom.unlink()
        except:
            print "The following exception caught unlinking xml_dom:"
            traceback.print_exc()
            return #returning causes connection thread instance to terminate



    #========================================================
    #
    #   Message_handler
    #
    #========================================================
    #
    # Changed thread organization from one continuous parsing/handling thread
    # to multiple expiring parsing/handling threads to improve server performance
    # and player load capacity -- Snowdog 3/04

    def message_handler(self,arg):
        xml_dom = None
        self.log_msg( "message handler thread running..." )
        while self.alive:
            data = None
            try:
                data=self.incoming.get(0)
            except Queue.Empty:
                time.sleep(0.5) #sleep 1/2 second
                continue

            bytes = len(data)
            if bytes <= 0:
                continue
            try:
                thread.start_new_thread(self.parse_incoming_dom,(str(data),))
                #data has been passed... unlink from the variable references
                #so data in passed objects doesn't change (python passes by reference)
                del data
                data = None
            except Exception, e:
                self.log_msg(str(e))
                if xml_dom: xml_dom.unlink()
        if xml_dom: xml_dom.unlink()
        self.log_msg("message handler thread exiting...")
        self.incoming_event.set()

    def parse_incoming_dom(self,data):
        end = data.find(">") #locate end of first element of message
        head = data[:end+1]
        #self.log_msg(head)
        xml_dom = None
        try:
            xml_dom = parseXml(head)
            xml_dom = xml_dom._get_documentElement()
            self.message_action(xml_dom,data)

        except Exception, e:
            print "Error in parse of inbound message. Ignoring message."
            print "  Offending data(" + str(len(data)) + "bytes)=" + data
            print "Exception=" + str(e)

        if xml_dom: xml_dom.unlink()


    def message_action(self, xml_dom, data):
        tag_name = xml_dom._get_tagName()
        if self.svrcmds.has_key(tag_name):
            self.svrcmds[tag_name]['function'](xml_dom,data)
        else:
            raise Exception, "Not a valid header!"
        #Message Action thread expires and closes here.
        return


    def do_alter(self, xml_dom, data):
        target = xml_dom.getAttribute("key")
        value = xml_dom.getAttribute("val")
        player = xml_dom.getAttribute("plr")
        group_id = xml_dom.getAttribute("gid")
        boot_pwd = xml_dom.getAttribute("bpw")
        actual_boot_pwd = self.groups[group_id].boot_pwd

        if self.allow_room_passwords == 0:
            msg ="<msg to='" + player + "' from='0' group_id='0' /> Room passwords have been disabled by the server administrator."
            self.players[player].outbox.put(msg)
            return
        elif boot_pwd == actual_boot_pwd:
            if target == "pwd":
                lmessage = "Room password changed to from \"" + self.groups[group_id].pwd + "\" to \"" + value  + "\" by " + player
                self.groups[group_id].pwd = value
                msg ="<msg to='" + player + "' from='0' group_id='0' /> Room password changed to \"" +  value + "\"."
                self.players[player].outbox.put(msg)
                self.log_msg(lmessage)
                self.send_to_all('0',self.groups[group_id].toxml('update'))
            elif target == "name":
                # Check for & in name.  We want to allow this because of its common
                # use in d&d games
                result = self.change_group_name(group_id,value,player)
                msg ="<msg to='" + player + "' from='0' group_id='0' />" + result
                self.players[player].outbox.put(msg)
        else:
            msg ="<msg to='" + player + "' from='0' group_id='0'>Invalid Administrator Password."
            self.players[player].outbox.put(msg)


    def do_role(self, xml_dom, data):
        role = ""
        boot_pwd = ""
        act = xml_dom.getAttribute("action")
        player = xml_dom.getAttribute("player")
        group_id = xml_dom.getAttribute("group_id")
        if act == "set":
            role = xml_dom.getAttribute("role")
            boot_pwd = xml_dom.getAttribute("boot_pwd")
        xml_dom.unlink()
        if group_id != "0":
            self.handle_role(act, player, role, boot_pwd, group_id)
            self.log_msg(("role", (player, role)))

    def do_ping(self, xml_dom, data):
        player = xml_dom.getAttribute("player")
        group_id = xml_dom.getAttribute("group_id")
        sent_time = ""
        msg = ""
        try:
            sent_time = xml_dom.getAttribute("time")
        except:
            pass

        if sent_time != "":
            #because a time was sent return a ping response
            msg ="<ping time='" + str(sent_time) + "' />"
        else:
            msg ="<msg to='" + player + "' from='" + player + "' group_id='" + group_id + "'><font color='#FF0000'>PONG!?!</font>"

        self.players[player].outbox.put(msg)
        xml_dom.unlink()

    def do_system(self, xml_dom, data):
        pass

    def moderate_group(self,xml_dom,data):
        try:
            action = xml_dom.getAttribute("action")
            from_id = xml_dom.getAttribute("from")
            if xml_dom.hasAttribute("pwd"):
                pwd=xml_dom.getAttribute("pwd")
            else:
                pwd=""
            group_id=self.players[from_id].group_id

            if action == "list":
                if (self.groups[group_id].moderated):
                    msg = ""
                    for i in self.groups[group_id].voice.keys():
                        if msg != "":
                            msg +=", "
                        if self.players.has_key(i):
                            msg += '('+i+') '+self.players[i].name
                        else:
                            del self.groups[group_id].voice[i]
                    if (msg != ""):
                        msg = "The following users may speak in this room: " + msg
                    else:
                        msg = "No people are currently in this room with the ability to chat"
                    self.players[from_id].self_message(msg)
                else:
                    self.players[from_id].self_message("This room is currently unmoderated")
            elif action == "enable":
                if not self.groups[group_id].check_boot_pwd(pwd):
                    self.players[from_id].self_message("Failed - incorrect admin password")
                    return
                self.groups[group_id].moderated = 1
                self.players[from_id].self_message("This channel is now moderated")
            elif action == "disable":
                if not self.groups[group_id].check_boot_pwd(pwd):
                    self.players[from_id].self_message("Failed - incorrect admin password")
                    return
                self.groups[group_id].moderated = 0
                self.players[from_id].self_message("This channel is now unmoderated")
            elif action == "addvoice":
                if not self.groups[group_id].check_boot_pwd(pwd):
                    self.players[from_id].self_message("Failed - incorrect admin password")
                    return
                users = xml_dom.getAttribute("users").split(',')
                for i in users:
                    self.groups[group_id].voice[i.strip()]=1
            elif action == "delvoice":
                if not self.groups[group_id].check_boot_pwd(pwd):
                    self.players[from_id].self_message("Failed - incorrect admin password")
                    return
                users = xml_dom.getAttribute("users").split(',')
                for i in users:
                    if self.groups[group_id].voice.has_key(i.strip()):
                        del self.groups[group_id].voice[i.strip()]
            else:
                print "Bad input: " + data

        except Exception,e:
            self.log_msg(str(e))




    def join_group(self,xml_dom,data):
        try:
            from_id = xml_dom.getAttribute("from")
            pwd = xml_dom.getAttribute("pwd")
            group_id = xml_dom.getAttribute("group_id")
            ver = self.players[from_id].version
            allowed = 1

            if not self.groups[group_id].check_version(ver):
                allowed = 0
                msg = 'failed - invalid client version ('+self.groups[group_id].minVersion+' or later required)'

            if not self.groups[group_id].check_pwd(pwd):
                allowed = 0

                #tell the clients password manager the password failed -- SD 8/03
                pm = "<password signal=\"fail\" type=\"room\" id=\"" +  group_id  + "\" data=\"\"/>"
                self.players[from_id].outbox.put(pm)

                msg = 'failed - incorrect room password'

            if not allowed:
                self.players[from_id].self_message(msg)
                #the following line makes sure that their role is reset to normal,
                #since it is briefly set to lurker when they even TRY to change
                #rooms
                msg = "<role action=\"update\" id=\"" + from_id  + "\" role=\"" + self.players[from_id].role + "\" />"
                self.players[from_id].outbox.put(msg)
                return

            #move the player into their new group.
            self.move_player(from_id, group_id)

        except Exception, e:
            self.log_msg(str(e))




    #----------------------------------------------------------------------------
    # move_player function -- added by Snowdog 4/03
    #
    # Split join_group function in half. separating the player validation checks
    # from the actual group changing code. Done primarily to impliment
    # boot-from-room-to-lobby behavior in the server.

    def move_player(self, from_id, group_id ):
        "move a player from one group to another"
        try:
            try:
                if group_id == "0":
                    self.players[from_id].role = "GM"
                else:
                    self.players[from_id].role = "Lurker"
            except Exception, e:
                print "exception in move_player() "
                traceback.print_exc()

            old_group_id = self.players[from_id].change_group(group_id,self.groups)
            self.send_to_group(from_id,old_group_id,self.players[from_id].toxml('del'))
            self.send_to_group(from_id,group_id,self.players[from_id].toxml('new'))
            self.check_group(from_id, old_group_id)

            # Here, if we have a group specific lobby message to send, push it on
            # out the door!  Make it put the message then announce the player...just
            # like in the lobby during a new connection.
            # -- only do this check if the room id is within range of known persistent id thresholds
            #also goes ahead if there is a defaultRoomMessage --akoman

            if self.isPersistentRoom(group_id) or self.defaultMessageFile != None:
                try:
                    if self.groups[group_id].messageFile[:4] == 'http':
                        data = urllib.urlretrieve(self.groups[group_id].messageFile)
                        roomMsgFile = open(data[0])
                    else:
                        roomMsgFile = open(self.groups[group_id].messageFile, "r")
                    roomMsg = roomMsgFile.read()
                    roomMsgFile.close()
                    urllib.urlcleanup()

                except Exception, e:
                    roomMsg = ""
                    self.log_msg(str(e))

                # Spit that darn message out now!
                self.players[from_id].outbox.put("<msg to='" + from_id + "' from='0' group_id='" + group_id + "' />" + roomMsg)

            if self.sendLobbySound and group_id == '0':
                self.players[from_id].outbox.put('<sound url="' + self.lobbySound + '" group_id="0" from="0" loop="True" />')

            # Now, tell everyone that we've arrived
            self.send_to_all('0', self.groups[group_id].toxml('update'))

            # this line sends a handle role message to change the players role
            self.send_player_list(from_id,group_id)

            #notify user about others in the room
            self.return_room_roles(from_id,group_id)
            self.log_msg(("join_group", (self.groups[group_id].name, group_id, from_id)))
            self.handle_role("set", from_id, self.players[from_id].role, self.groups[group_id].boot_pwd, group_id)

        except Exception, e:
            self.log_msg(str(e))

        thread.start_new_thread(self.registerRooms,(0,))

    def return_room_roles(self,from_id,group_id):
        for m in self.players.keys():
            if self.players[m].group_id == group_id:
                msg = "<role action=\"update\" id=\"" + self.players[m].id  + "\" role=\"" + self.players[m].role + "\" />"
                self.players[from_id].outbox.put(msg)


    # This is pretty much the same thing as the create_group method, however,
    # it's much more generic whereas the create_group method is tied to a specific
    # xml message.  Ack!  This version simply creates the groups, it does not
    # send them to players.  Also note, both these methods have race
    # conditions written all over them.  Ack! Ack!
    def new_group( self, name, pwd, boot, minVersion, mapFile, messageFile, persist = 0, moderated=0 ):
        group_id = str( self.next_group_id )
        self.next_group_id += 1
        self.groups[group_id] = game_group( group_id, name, pwd, "", boot, minVersion, mapFile, messageFile, persist )
        self.groups[group_id].moderated = moderated
        ins = ""
        if persist !=0: ins="Persistant "
        lmsg = "Creating " + ins + "Group... (" + str(group_id) + ") " + str(name)
        self.log_msg( lmsg )
        self.log_msg(("create_group", (str(name), int(group_id), 0) )) ##-99 works, could be better.


    def change_group_name(self,gid,name,pid):
        "Change the name of a group"
        # Check for & in name.  We want to allow this because of its common
        # use in d&d games.
        try:
            loc = name.find("&")
            oldloc = 0
            while loc > -1:
                loc = name.find("&",oldloc)
                if loc > -1:
                    b = name[:loc]
                    e = name[loc+1:]
                    value = b + "&amp;" + e
                    oldloc = loc+1

            loc = name.find("'")
            oldloc = 0
            while loc > -1:
                loc = name.find("'",oldloc)
                if loc > -1:
                    b = name[:loc]
                    e = name[loc+1:]
                    name = b + "&#39;" + e
                    oldloc = loc+1

            loc = name.find('"')
            oldloc = 0
            while loc > -1:
                loc = name.find('"',oldloc)
                if loc > -1:
                    b = name[:loc]
                    e = name[loc+1:]
                    name = b + "&quot;" + e
                    oldloc = loc+1

            oldroomname = self.groups[gid].name
            self.groups[gid].name = str(name)
            lmessage = "Room name changed to from \"" + oldroomname + "\" to \"" + name + "\""
            self.log_msg(lmessage  + " by " + str(pid) )
            self.send_to_all('0',self.groups[gid].toxml('update'))
            return lmessage
        except:
            return "An error occured during rename of room!"

        thread.start_new_thread(self.registerRooms,(0,))



    def create_group(self,xml_dom,data):
        try:
            from_id = xml_dom.getAttribute("from")
            pwd = xml_dom.getAttribute("pwd")
            name = xml_dom.getAttribute("name")
            boot_pwd = xml_dom.getAttribute("boot_pwd")
            minVersion = xml_dom.getAttribute("min_version")
            #added var reassign -- akoman
            messageFile = self.defaultMessageFile

            # see if passwords are allowed on this server and null password if not
            if self.allow_room_passwords != 1: pwd = ""


            #
            # Check for & in name.  We want to allow this because of its common
            # use in d&d games.

            loc = name.find("&")
            oldloc = 0
            while loc > -1:
                loc = name.find("&",oldloc)
                if loc > -1:
                    b = name[:loc]
                    e = name[loc+1:]
                    name = b + "&amp;" + e
                    oldloc = loc+1

            loc = name.find("'")
            oldloc = 0
            while loc > -1:
                loc = name.find("'",oldloc)
                if loc > -1:
                    b = name[:loc]
                    e = name[loc+1:]
                    name = b + "&#39;" + e
                    oldloc = loc+1

            loc = name.find('"')
            oldloc = 0
            while loc > -1:
                loc = name.find('"',oldloc)
                if loc > -1:
                    b = name[:loc]
                    e = name[loc+1:]
                    name = b + "&quot;" + e
                    oldloc = loc+1


            group_id = str(self.next_group_id)
            self.next_group_id += 1
            self.groups[group_id] = game_group(group_id,name,pwd,"",boot_pwd, minVersion, None, messageFile )
            self.groups[group_id].voice[from_id]=1
            self.players[from_id].outbox.put(self.groups[group_id].toxml('new'))
            old_group_id = self.players[from_id].change_group(group_id,self.groups)
            self.send_to_group(from_id,old_group_id,self.players[from_id].toxml('del'))
            self.check_group(from_id, old_group_id)
            self.send_to_all(from_id,self.groups[group_id].toxml('new'))
            self.send_to_all('0',self.groups[group_id].toxml('update'))
            self.handle_role("set",from_id,"GM",boot_pwd, group_id)
            lmsg = "Creating Group... (" + str(group_id) + ") " + str(name)
            self.log_msg( lmsg )
            jmsg = "moving to room " + str(group_id) + "."
            self.log_msg( jmsg )
            self.log_msg(("create_group", (str(name), group_id, from_id)))
            #even creators of the room should see the HTML --akoman
            #edit: jan10/03 - was placed in the except statement. Silly me.
            if self.defaultMessageFile != None:
                if self.defaultMessageFile[:4] == 'http':
                    data = urllib.urlretrieve(self.defaultMessageFile)
                    open_msg = open(data[0])
                    urllib.urlcleanup()
                else:
                    open_msg = open( self.defaultMessageFile, "r" )

                roomMsg = open_msg.read()
                open_msg.close()
                # Send the rooms message to the client no matter what
                self.players[from_id].outbox.put( "<msg to='" + from_id + "' from='0' group_id='" + group_id + "' />" + roomMsg )

        except Exception, e:
            self.log_msg( "Exception: create_group(): " + str(e))

        thread.start_new_thread(self.registerRooms,(0,))


    def check_group(self, from_id, group_id):
        try:
            if group_id not in self.groups: return
            if group_id == '0':
                self.send_to_all("0",self.groups[group_id].toxml('update'))
                return #never remove lobby *sanity check*
            if not self.isPersistentRoom(group_id)  and self.groups[group_id].get_num_players() == 0:
                self.send_to_all("0",self.groups[group_id].toxml('del'))
                del self.groups[group_id]
                self.log_msg(("delete_group", (group_id, from_id)))

            else:
                self.send_to_all("0",self.groups[group_id].toxml('update'))

            #The register Rooms thread
            thread.start_new_thread(self.registerRooms,(0,))

        except Exception, e:
            self.log_msg(str(e))

    def del_player(self,id,group_id):
        try:
            dmsg = "Client Disconnect: (" + str(id) + ") " + str(self.players[id].name)
            self.players[id].disconnect()
            self.groups[group_id].remove_player(id)
            del self.players[id]
            self.log_msg(dmsg)
            self.log_msg(("disconnect",id))


            #  If already registered then re-register, thereby updating the Meta
            #    on the number of players
            #  Note:  Upon server shutdown, the server is first unregistered, so
            #           this code won't be repeated for each player being deleted.
            if self.be_registered:
                self.register()


        except Exception, e:
            self.log_msg(str(e))

        self.log_msg("Explicit garbage collection shows %s undeletable items." % str(gc.collect()))



    def incoming_player_handler(self,xml_dom,data):
        id = xml_dom.getAttribute("id")
        act = xml_dom.getAttribute("action")
        #group_id = xml_dom.getAttribute("group_id")
        group_id = self.players[id].group_id
        ip = self.players[id].ip
        self.log_msg("Player with IP: " + str(ip) + " joined.")

        ServerPlugins.setPlayer(self.players[id])

        self.send_to_group(id,group_id,data)
        if act=="new":
            try:
                self.send_player_list(id,group_id)
                self.send_group_list(id)
            except Exception, e:
                traceback.print_exc()
        elif act=="del":
            #print "del player"
            self.del_player(id,group_id)
            self.check_group(id, group_id)
        elif act=="update":
            self.players[id].take_dom(xml_dom)
            self.log_msg(("update", {"id": id,
                                     "name": xml_dom.getAttribute("name"),
                                     "status": xml_dom.getAttribute("status"),
                                     "role": xml_dom.getAttribute("role"),
				     "ip":  str(ip),
				     "group": xml_dom.getAttribute("group_id"),
				     "room": xml_dom.getAttribute("name"),
				     "boot": xml_dom.getAttribute("rm_boot"),
				     "version": xml_dom.getAttribute("version"),
				     "ping": xml_dom.getAttribute("time") \
                                     }))


    def strip_cheat_roll(self, string):
        try:
            cheat_regex = re.compile('&amp;#91;(.*?)&amp;#93;')
            string = cheat_regex.sub( r'[ ' + self.cheat_msg + " \\1 " + self.cheat_msg + ' ]', string)
        except:
            pass
        return string

    def strip_body_tags(self, string):
        try:
            bodytag_regex = re.compile('&lt;\/?body(.*?)&gt;')
            string = bodytag_regex.sub('', string)
        except:
            pass
        return string

    def msgTooLong(self, length):
        if length > self.maxSendSize and not self.maxSendSize == 0:
            return True
        return False

    def incoming_msg_handler(self,xml_dom,data):
        xml_dom, data = ServerPlugins.preParseIncoming(xml_dom, data)

        to_id = xml_dom.getAttribute("to")
        from_id = xml_dom.getAttribute("from")
        group_id = xml_dom.getAttribute("group_id")
        end = data.find(">")
        msg = data[end+1:]

        if from_id == "0" or len(from_id) == 0:
            print "WARNING!! Message received with an invalid from_id.  Message dropped."
            return None

        #
        # check for < body to prevent someone from changing the background
        #

        data = self.strip_body_tags(data)

        #
        # check for &#91 and &#93  codes which are often used to cheat with dice.
        #
        if self.players[from_id].role != "GM":
            data = self.strip_cheat_roll(data)

        if group_id == '0' and self.msgTooLong(len(msg) and msg[:5] == '<chat'):
            self.send("Your message was too long, break it up into smaller parts please", from_id, group_id)
            self.log_msg('Message Blocked from Player: ' + self.players[from_id].name + ' attempting to send a message longer then ' + str(self.maxSendSize))
            return

        if msg[:4] == '<map':
            if group_id == '0':
                #attempt to change lobby map. Illegal operation.
                self.players[from_id].self_message('The lobby map may not be altered.')
            elif to_id.lower() == 'all':
                #valid map for all players that is not the lobby.
                self.send_to_group(from_id,group_id,data)
                self.groups[group_id].game_map.init_from_xml(msg)
            else:
                #attempting to send map to specific individuals which is not supported.
                self.players[from_id].self_message('Invalid map message. Message not sent to others.')

        elif msg[:6] == '<boot ':
            self.handle_boot(from_id,to_id,group_id,msg)

        else:
            if to_id == 'all':
                if self.groups[group_id].moderated and not self.groups[group_id].voice.has_key(from_id):
                    self.players[from_id].self_message('This room is moderated - message not sent to others')
                else:
                    self.send_to_group(from_id,group_id,data)
            else:
                self.players[to_id].outbox.put(data)

        self.check_group_members(group_id)
        return

    def sound_msg_handler(self, xml_dom, data):
        from_id = xml_dom.getAttribute("from")
        group_id = xml_dom.getAttribute("group_id")
        if group_id != 0:
            self.send_to_group(from_id, group_id, data)

    def plugin_msg_handler(self,xml_dom,data):
        to_id = xml_dom.getAttribute("to")
        from_id = xml_dom.getAttribute("from")
        group_id = xml_dom.getAttribute("group_id")
        end = data.find(">")
        msg = data[end+1:]

        if from_id == "0" or len(from_id) == 0:
            print "WARNING!! Message received with an invalid from_id.  Message dropped."
            return None


        if to_id == 'all':
            if self.groups[group_id].moderated and not self.groups[group_id].voice.has_key(from_id):
                self.players[from_id].self_message('This room is moderated - message not sent to others')
            else:
                self.send_to_group(from_id, group_id, msg)
        else:
            self.players[to_id].outbox.put(msg)

        self.check_group_members(group_id)
        return

    def handle_role(self, act, player, role, given_boot_pwd, group_id):
        if act == "display":
            msg = "<msg to=\"" + player + "\" from=\"0\" group_id=\"" + group_id + "\" />"
            msg += "Displaying Roles<br /><br /><u>Role</u>&nbsp&nbsp&nbsp<u>Player</u><br />"
            keys = self.players.keys()
            for m in keys:
                if self.players[m].group_id == group_id:
                    msg += self.players[m].role + " " + self.players[m].name + "<br />"
            self.send(msg,player,group_id)
        elif act == "set":
            try:
                actual_boot_pwd = self.groups[group_id].boot_pwd
                if self.players[player].group_id == group_id:
                    if actual_boot_pwd == given_boot_pwd:
                        self.log_msg( "Administrator passwords match -- changing role")

                        #  Send update role event to all
                        msg = "<role action=\"update\" id=\"" + player  + "\" role=\"" + role + "\" />"
                        self.send_to_group("0", group_id, msg)
                        self.players[player].role = role
                        if (role.lower() == "gm" or role.lower() == "player"):
                            self.groups[group_id].voice[player]=1
                    else:
                        #tell the clients password manager the password failed -- SD 8/03
                        pm = "<password signal=\"fail\" type=\"admin\" id=\"" + group_id + "\" data=\"\"/>"
                        self.players[player].outbox.put(pm)
                        self.log_msg( "Administrator passwords did not match")
            except Exception, e:
                print e
                print "Error executing the role change"
                print "due to the following exception:"
                traceback.print_exc()
                print "Ignoring boot message"

    def handle_boot(self,from_id,to_id,group_id,msg):
        xml_dom = None
        try:
            given_boot_pwd = None
            try:
                xml_dom = parseXml(msg)
                xml_dom = xml_dom._get_documentElement()
                given_boot_pwd = xml_dom.getAttribute("boot_pwd")

            except:
                print "Error in parse of boot message, Ignoring."
                print "Exception: "
                traceback.print_exc()

            try:
                actual_boot_pwd = self.groups[group_id].boot_pwd
                server_admin_pwd = self.groups["0"].boot_pwd

                self.log_msg("Actual boot pwd = " + actual_boot_pwd)
                self.log_msg("Given boot pwd = " + given_boot_pwd)

                if self.players[to_id].group_id == group_id:

                    ### ---CHANGES BY SNOWDOG 4/03 ---
                    ### added boot to lobby code.
                    ### if boot comes from lobby dump player from the server
                    ### any user in-room boot will dump to lobby instead
                    if given_boot_pwd == server_admin_pwd:
                        # Send a message to everyone in the room, letting them know someone has been booted
                        boot_msg = "<msg to='all' from='%s' group_id='%s'/><font color='#FF0000'>Booting '(%s) %s' from server...</font>" % (from_id, group_id, to_id, self.players[to_id].name)

                        self.log_msg("boot_msg:" + boot_msg)

                        self.send_to_group( "0", group_id, boot_msg )
                        time.sleep( 1 )

                        self.log_msg("Booting player " + str(to_id) + " from server.")

                        #  Send delete player event to all
                        self.send_to_group("0",group_id,self.players[to_id].toxml("del"))

                        #  Remove the player from local data structures
                        self.del_player(to_id,group_id)

                        #  Refresh the group data
                        self.check_group(to_id, group_id)

                    elif actual_boot_pwd == given_boot_pwd:
                        # Send a message to everyone in the room, letting them know someone has been booted
                        boot_msg = "<msg to='all' from='%s' group_id='%s'/><font color='#FF0000'>Booting '(%s) %s' from room...</font>" % (from_id, group_id, to_id, self.players[to_id].name)

                        self.log_msg("boot_msg:" + boot_msg)

                        self.send_to_group( "0", group_id, boot_msg )
                        time.sleep( 1 )

                        #dump player into the lobby
                        self.move_player(to_id,"0")

                        #  Refresh the group data
                        self.check_group(to_id, group_id)
                    else:
                        #tell the clients password manager the password failed -- SD 8/03
                        pm = "<password signal=\"fail\" type=\"admin\" id=\"" + group_id + "\" data=\"\"/>"
                        self.players[from_id].outbox.put(pm)
                        print "boot passwords did not match"

            except Exception, e:
                traceback.print_exc()
                self.log_msg('Exception in handle_boot() ' + str(e))

        finally:
            try:
                if xml_dom:
                    xml_dom.unlink()
            except Exception, e:
                traceback.print_exc()
                self.log_msg('Exception in xml_dom.unlink() ' + str(e))


    #---------------------------------------------------------------
    # admin_kick function -- by Snowdog 4/03
    # 9/17/05 updated to allow stealth boots (no client chat announce) -SD
    #---------------------------------------------------------------
    def admin_kick(self, id, message="", silent = 0 ):
        "Kick a player from a server from the console"

        try:
            group_id = self.players[id].group_id
            # Send a message to everyone in the victim's room, letting them know someone has been booted
            boot_msg = "<msg to='all' from='0' group_id='%s'/><font color='#FF0000'>Kicking '(%s) %s' from server... %s</font>" % ( group_id, id, self.players[id].name, str(message))
            self.log_msg("boot_msg:" + boot_msg)
            if (silent == 0):
                self.send_to_group( "0", group_id, boot_msg )
            time.sleep( 1 )

            self.log_msg("kicking player " + str(id) + " from server.")
            #  Send delete player event to all
            self.send_to_group("0",group_id,self.players[id].toxml("del"))

            #  Remove the player from local data structures
            self.del_player(id,group_id)

            #  Refresh the group data
            self.check_group(id, group_id)

        except Exception, e:
            traceback.print_exc()
            self.log_msg('Exception in admin_kick() ' + str(e))


    def admin_banip(self, ip, name="", silent = 0):
        "Ban a player from a server from the console"
        try:
            self.ban_list[ip] = {}
            self.ban_list[ip]['ip'] = ip
            self.ban_list[ip]['name'] = name
            self.saveBanList()

        except Exception, e:
            traceback.print_exc()
            self.log_msg('Exception in admin_banip() ' + str(e))

    def admin_ban(self, id, message="", silent = 0):
        "Ban a player from a server from the console"
        try:
            id = str(id)
            group_id = self.players[id].group_id
            ip = self.players[id].ip
            self.ban_list[ip] = {}
            self.ban_list[ip]['ip'] = ip
            self.ban_list[ip]['name'] = self.players[id].name
            self.saveBanList()

            # Send a message to everyone in the victim's room, letting them know someone has been booted
            ban_msg = "<msg to='all' from='0' group_id='%s'/><font color='#FF0000'>Banning '(%s) %s' from server... %s</font>" % ( group_id, id, self.players[id].name, str(message))
            self.log_msg("ban_msg:" + ban_msg)
            if (silent == 0):
                self.send_to_group("0", group_id, ban_msg)
            time.sleep( .1 )

            self.log_msg("baning player " + str(id) + " from server.")
            #  Send delete player event to all
            self.send_to_group("0", group_id, self.players[id].toxml("del"))

            #  Remove the player from local data structures
            self.del_player(id, group_id)

            #  Refresh the group data
            self.check_group(id, group_id)

        except Exception, e:
            traceback.print_exc()
            self.log_msg('Exception in admin_ban() ' + str(e))

    def admin_unban(self, ip):
        try:
            if self.ban_list.has_key(ip):
                del self.ban_list[ip]

            self.saveBanList()

        except Exception, e:
            traceback.print_exc()
            self.log_msg('Exception in admin_unban() ' + str(e))

    def admin_banlist(self):
        msg = []
        msg.append('<table border="1"><tr><td><b>Name</b></td><td><b>IP</b></td></tr>')
        for ip in self.ban_list.keys():
            msg.append("<tr><td>")
            msg.append(self.ban_list[ip]['name'])
            msg.append("</td><td>")
            msg.append(self.ban_list[ip]['ip'])
            msg.append("</td></tr>")
        msg.append("</table>")

        return "".join(msg)

    def admin_toggleSound(self):
        if self.sendLobbySound:
            self.sendLobbySound = False
        else:
            self.sendLobbySound = True

        return self.sendLobbySound

    def admin_soundFile(self, file):
        self.lobbySound = file

    def admin_setSendSize(self, sendlen):
        self.maxSendSize = sendlen
        self.log_msg('Max Send Size was set to ' + str(sendlen))

    def remove_room(self, group):
        "removes a group and boots all occupants"
        #check that group id exists
        if group not in self.groups:
            return "Invalid Room Id. Ignoring remove request."

        self.groups[group].persistant = 0
        try:
            keys = self.groups[group].get_player_ids()
            for k in keys:
                self.del_player(k, str(group))
            self.check_group("0", str(group))
        except:
            pass

    def send(self,msg,player,group):
        self.players[player].send(msg,player,group)


    def send_to_all(self,from_id,data):
        try:
            print data
            self.p_lock.acquire()
            keys = self.players.keys()
            self.p_lock.release()
            for k in keys:
                if k != from_id:
                    self.players[k].outbox.put(data)
        except Exception, e:
            traceback.print_exc()
            self.log_msg("Exception: send_to_all(): " + str(e))

    def send_to_group(self, from_id, group_id, data):
        msg = ("<msg to='all' from='0' group_id='"+group_id+"'><font color='#FF0000'>" + data + "</font>")
        #data = ServerPlugins.postParseIncoming(data)
        try:
            print data
            self.p_lock.acquire()
            keys = self.groups[group_id].get_player_ids()
            self.p_lock.release()
            print keys
            for k in keys:
                if k != from_id:
                    self.players[k].outbox.put(msg)
        except Exception, e:
            traceback.print_exc()
            self.log_msg("Exception: send_to_group(): " + str(e))

    def send_player_list(self,to_id,group_id):
        try:
            keys = self.groups[group_id].get_player_ids()
            for k in keys:
                if k != to_id:
                    data = self.players[k].toxml('new')
                    self.players[to_id].outbox.put(data)
        except Exception, e:
            traceback.print_exc()
            self.log_msg("Exception: send_player_list(): " + str(e))

    def send_group_list(self, to_id, action="new"):
        try:
            for key in self.groups:
                xml = self.groups[key].toxml(action)
                self.players[to_id].outbox.put(xml)
        except Exception, e:
            self.log_msg("Exception: send_group_list(): (client #"+to_id+") : " + str(e))
            traceback.print_exc()

    #--------------------------------------------------------------------------
    # KICK_ALL_CLIENTS()
    #
    # Convience method for booting all clients off the server at once.
    # used while troubleshooting mysterious "black hole" server bug
    # Added by Snowdog 11-19-04
    def kick_all_clients(self):
        try:
            keys = self.groups.keys()
            for k in keys:
                pl = self.groups[k].get_player_ids()
                for p in pl:
                    self.admin_kick(p,"Purged from server")
        except Exception, e:
            traceback.print_exc()
            self.log_msg("Exception: kick_all_clients(): " + str(e))


    # This really has little value as it will only catch people that are hung
    # on a disconnect which didn't complete.  Other idle connections which are
    # really dead go undeterred.
    #
    # UPDATED 11-29-04: Changed remove XML send to forced admin_kick for 'dead clients'
    #                   Dead clients now removed more effeciently as soon as they are detected
    #                        --Snowdog
    def check_group_members(self, group_id):
        try:
            keys = self.groups[group_id].get_player_ids()
            for k in keys:
                #drop any clients that are idle for more than 8 hours
                #as these are likely dead clients
                idlemins = self.players[k].idle_time()
                idlemins = idlemins/60
                if (idlemins > self.zombie_time):
                    self.admin_kick(k,"Removing zombie client", self.silent_auto_kick)
                elif self.players[k].get_status() != MPLAY_CONNECTED:
                    if self.players[k].check_time_out():
                        self.log_msg("Player #" + k + " Lost connection!")
                        self.admin_kick(k,"Removing dead client", self.silent_auto_kick)
        except Exception, e:
            self.log_msg("Exception: check_group_members(): " + str(e))


    def remote_admin_handler(self,xml_dom,data):
        # handle incoming remove server admin messages
        # (allows basic administration of server from a remote client)
        # base message format: <admin id="" pwd="" cmd="" [data for command]>

        if not self.allowRemoteAdmin:
            return

        try:
            pid = xml_dom.getAttribute("id")
            gid = ""
            given_pwd = xml_dom.getAttribute("pwd")
            cmd = xml_dom.getAttribute("cmd")
            server_admin_pwd = self.groups["0"].boot_pwd
            p_id = ""
            p_name= ""
            p_ip = ""


            #verify that the message came from the proper ID/Socket and get IP address for logging
            if self.players.has_key(pid):
                p_name=(self.players[pid]).name
                p_ip=(self.players[pid]).ip
                gid=(self.players[pid]).group_id
            else:
                #invalid ID.. report fraud and log
                m = "Invalid Remote Server Control Message (invalid id) #" + str(pid) + " does not exist."
                self.log_msg( m )
                return

            #log receipt of admin command   added by Darren
            m = "Remote Server Control Message ( "+ str(cmd) +" ) from #" + str(pid) + " (" + str(p_name) + ") " + str(p_ip)
            self.log_msg ( m )

            #check the admin password(boot password) against the supplied one in message
            #dump and log any attempts to control server remotely with invalid password
            if server_admin_pwd != given_pwd:
                #tell the clients password manager the password failed -- SD 8/03
                pm = "<password signal=\"fail\" type=\"server\" id=\"" + str(self.players[pid].group_id) + "\" data=\"\"/>"
                self.players[pid].outbox.put(pm)
                m = "Invalid Remote Server Control Message (bad password) from #" + str(pid) + " (" + str(p_name) + ") " + str(p_ip)
                self.log_msg( m )
                return

            #message now deemed 'authentic'
            #determine action to take based on command (cmd)

            if cmd == "list":
                #return player list to this user.
                msg ="<msg to='" + pid + "' from='0' group_id='" + gid + "'>" + self.player_list_remote()
                self.players[pid].outbox.put(msg)

            elif cmd == "banip":
                ip = xml_dom.getAttribute("bip")
                name = xml_dom.getAttribute("bname")
                msg = "<msg to='" + pid + "' from='0' group_id='" + gid + "'> Banned: " + str(ip)
                self.admin_banip(ip, name)

            elif cmd == "ban":
                id = xml_dom.getAttribute("bid")
                msg = "<msg to='" + id + "' from='0' group_id='" + gid + "'> Banned!"
                self.players[pid].outbox.put(msg)
                self.admin_ban(id, "")

            elif cmd == "unban":
                ip = xml_dom.getAttribute("ip")
                self.admin_unban(ip)
                msg = "<msg to='" + pid + "' from='0' group_id='" + gid + "'> Unbaned: " + str(ip)
                self.players[pid].outbox.put(msg)

            elif cmd == "banlist":
                msg = "<msg to='" + pid + "' from='0' group_id='" + gid + "'>" + self.admin_banlist()
                self.players[pid].outbox.put(msg)

            elif cmd == "killgroup":
                ugid = xml_dom.getAttribute("gid")
                if ugid == "0":
                    m = "<msg to='" + pid + "' from='0' group_id='" + gid + "'>Cannot Remove Lobby! Remote administrator request denied!"
                    self.players[pid].outbox.put(m)
                else:
                    result = self.prune_room(ugid)
                    msg = "<msg to='" + pid + "' from='0' group_id='" + gid + "'>" + str(result)
                    self.players[pid].outbox.put(msg)

            elif cmd == "message":
                tuid = xml_dom.getAttribute("to_id")
                msg = xml_dom.getAttribute("msg")
                pmsg = "<msg to='" + tuid + "' from='0' group_id='" + self.players[tuid].group_id + "' >" + msg
                try: self.players[tuid].outbox.put(pmsg)
                except:
                    msg = "<msg to='" + pid + "' from='0' group_id='" + gid + ">Unknown Player ID: No message sent."
                    self.players[pid].outbox.put(msg)

            elif cmd == "broadcast":
                bmsg = xml_dom.getAttribute("msg")
                self.broadcast(bmsg)

            elif cmd == "killserver" and self.allowRemoteKill:
                #dangerous command..once server stopped it must be restarted manually
                self.kill_server()

            elif cmd == "uptime":
                msg ="<msg to='" + pid + "' from='0' group_id='" + gid + "'>" + self.uptime(1)
                self.players[pid].outbox.put(msg)

            elif cmd == "help":
                msg = "<msg to='" + pid + "' from='0' group_id='" + gid + "'>"
                msg += self.AdminHelpMessage()
                self.players[pid].outbox.put( msg)

            elif cmd == "roompasswords":
                # Toggle if room passwords are allowed on this server
                msg = "<msg to='" + pid + "' from='0' group_id='" + gid + "'>"
                msg += self.RoomPasswords()
                self.players[pid].outbox.put( msg)

            elif cmd == "createroom":
                rm_name = xml_dom.getAttribute("name")
                rm_pass = xml_dom.getAttribute("pass")
                rm_boot = xml_dom.getAttribute("boot")
                result = self.create_temporary_persistant_room(rm_name, rm_boot, rm_pass)
                msg = "<msg to='" + pid + "' from='0' group_id='" + gid + "'>" + result
                self.players[pid].outbox.put(msg)

            elif cmd == "nameroom":
                rm_id   = xml_dom.getAttribute("rmid")
                rm_name = xml_dom.getAttribute("name")
                result = self.change_group_name(rm_id,rm_name,pid)
                msg ="<msg to='" + pid + "' from='0' group_id='" + gid + "'/>" + result
                self.players[pid].outbox.put(msg)

            elif cmd == "passwd":
                tgid = xml_dom.getAttribute("gid")
                npwd = xml_dom.getAttribute("pass")
                if tgid == "0":
                    msg ="<msg to='" + pid + "' from='0' group_id='" + gid + "'>Server password may not be changed remotely!"
                    self.players[pid].outbox.put(msg)
                else:
                    try:
                        self.groups[tgid].boot_pwd = npwd
                        msg ="<msg to='" + pid + "' from='0' group_id='" + gid + "'>Password changed for room " + tgid
                        self.players[pid].outbox.put(msg)
                    except: pass

            elif cmd == "savemaps":
                for g in self.groups.itervalues():
                    g.save_map()

                msg ="<msg to='" + pid + "' from='0' group_id='" + gid + "'>Persistent room maps saved"
                self.players[pid].outbox.put(msg)


            else:
                msg ="<msg to='" + pid + "' from='0' group_id='" + gid + "'><i>[Unknown Remote Administration Command]</i>"
                self.players[pid].outbox.put(msg)


        except Exception, e:
            self.log_msg("Exception: Remote Admin Handler Error: " + str(e))
            traceback.print_exc()


    def toggleRemoteKill(self):
        if self.allowRemoteKill:
            self.allowRemoteKill = False
        else:
            self.allowRemoteKill = True

        return self.allowRemoteKill

    def toggleRemoteAdmin(self):
        if self.allowRemoteAdmin:
            self.allowRemoteAdmin = False
        else:
            self.allowRemoteAdmin = True

        return self.allowRemoteAdmin

#-----------------------------------------------------------------
# Remote Administrator Help (returns from server not client)
#-----------------------------------------------------------------
    def AdminHelpMessage(self):
        "returns a string to be sent as a message to a remote admin"

        #define the help command list information
        info = []
        info.append( ['list', '/admin list', 'Displays information about rooms and players on the server'] )
        info.append( ['uptime', '/admin uptime', 'Information on how long server has been running'] )
        info.append( ['help', '/admin help', 'This help message'])
        info.append( ['passwd', '/admin passwd &lt;group id&gt; &lt;new password&gt;', 'Changes a rooms bootpassword. Server(lobby) password may not be changed'])
        info.append( ['roompasswords', '/admin roompasswords', 'Allow/Disallow Room Passwords on the server (toggles)'])
        info.append( ['message', '/admin message &lt;user id&gt; &lt;message&gt;', 'Send a message to a specific user on the server'])
        info.append( ['broadcast', '/admin broadcast &lt;message&gt;', 'Broadcast message to all players on server'])
        info.append( ['createroom', '/admin createroom &lt;room name&gt; &lt;boot password&gt; [password]', 'Creates a temporary persistant room if possible.<i>Rooms created this way are lost on server restarts'])
        info.append( ['nameroom', '/admin nameroom &lt;group id&gt; &lt;new name&gt;', 'Rename a room'])
        info.append( ['killgroup', '/admin killgroup &lt;room id&gt;', 'Remove a room from the server and kick everyone in it.'])
        if self.allowRemoteKill:
            info.append( ['killserver', '/admin killserver', 'Shuts down the server. <b>WARNING: Server cannot be restarted remotely via OpenRPG</b>'])
        info.append( ['ban', '/admin ban {playerId}', 'Ban a player from the server.'])
        info.append( ['unban', '/admin unban {bannedIP}', 'UnBan a player from the server.'])
        info.append( ['banlist', '/admin banlist', 'List Banned IPs and the Names associated with them'])
        info.append( ['savemaps', '/admin savemaps', 'Save all persistent room maps that are not using the default map file.'])


        #define the HTML for the help display
        FS = "<font size='-1'>"
        FE = "<font>"

        help = "<hr><B>REMOTE ADMINISTRATOR COMMANDS SUPPORTED</b><br /><br />"
        help += "<table border='1' cellpadding='2'>"
        help += "<tr><td width='15%'><b>Command</b></td><td width='25%'><b>Format</b></td><td width='60%'><b>Description</b></td></tr>"
        for n in info:
            help += "<tr><td>" + FS + n[0] + FE + "</td><td><nobr>" + FS + n[1] + FE + "</nobr></td><td>" + FS + n[2] + FE + "</td></tr>"
        help += "</table>"
        return help


    #----------------------------------------------------------------
    # Create Persistant Group -- Added by Snowdog 6/03
    #
    # Allows persistant groups to be created on the fly.
    # These persistant groups are not added to the server.ini file
    # however and are lost on server restarts
    #
    # Updated function code to use per-group based persistance and
    # removed references to outdated persistRoomIdThreshold
    #----------------------------------------------------------------

    def create_temporary_persistant_room(self, roomname, bootpass, password=""):
        # if the room id just above the persistant room limit is available (not in use)
         # then it will be assigned as a persistant room on the server
        "create a temporary persistant room"

        group_id = str(self.next_group_id)
        self.next_group_id += 1
        self.groups[group_id] = game_group( group_id, roomname, password, "", bootpass, persist = 1 )
        cgmsg = "Create Temporary Persistant Group: (" + str(group_id) + ") " + str(roomname)
        self.log_msg( cgmsg )
        self.send_to_all('0',self.groups[group_id].toxml('new'))
        self.send_to_all('0',self.groups[group_id].toxml('update'))
        return str("Persistant room created (group " + group_id + ").")

    #----------------------------------------------------------------
    # Prune Room  -- Added by Snowdog 6/03
    #
    # similar to remove_room() except rooms are removed regardless
    # of them being persistant or not
    #
    # Added some error checking and updated room removal for per-room
    # based persistance -- Snowdog 4/04
    #----------------------------------------------------------------

    def prune_room(self,group):
        #don't allow lobby to be removed
        if group == '0': return "Lobby is required to exist and cannot be removed."

        #check that group id exists
        if group not in self.groups:
            return "Invalid Room Id. Ignoring remove request."

        try:
            keys = self.groups[group].get_player_ids()
            for k in keys:
                self.move_player(k,'0')

            ins = "Room"
            if self.isPersistentRoom(group) : ins="Persistant room"
            self.send_to_all("0",self.groups[group].toxml('del'))
            del self.groups[group]
            self.log_msg(("delete_group", ('0',group)))
            return ins + " removed."

        except:
            traceback.print_exc()
            return "An Error occured on the server during room removal!"


#----------------------------------------------------------------
#  Remote Player List  -- Added by snowdog 6/03
#
#  Similar to console listing except formated for web display
#  in chat window on remote client
#----------------------------------------------------------------
    def player_list_remote(self):
        COLOR1 = "\"#004080\""  #header/footer background color
        COLOR2 = "\"#DDDDDD\""  #group line background color
        COLOR3 = "\"#FFFFFF\""  #player line background color
        COLOR4 = "\"#FFFFFF\""  #header/footer text color
        PCOLOR = "\"#000000\""  #Player text color
        LCOLOR = "\"#404040\""  #Lurker text color
        GCOLOR = "\"#FF0000\""  #GM text color
        SIZE   = "size=\"-1\""  #player info text size
        FG = PCOLOR


        "display a condensed list of players on the server"
        self.p_lock.acquire()
        pl = "<br /><table border=\"0\" cellpadding=\"1\" cellspacing=\"2\">"
        pl += "<tr><td colspan='4' bgcolor=" + COLOR1 + "><font color=" + COLOR4 + "><b>GROUP &amp; PLAYER LIST</b></font></td></tr>"
        try:

            keys = self.groups.keys()
            keys.sort(id_compare)
            for k in keys:
                groupstring = "<tr><td bgcolor=" + COLOR2 + " colspan='2'><b>Group " + str(k)  + ": " +  self.groups[k].name  + "</b>"
                groupstring += "</td><td bgcolor=" + COLOR2 + " > <i>Password: \"" + self.groups[k].pwd + "\"</td><td bgcolor=" + COLOR2 + " > Boot: \"" + self.groups[k].boot_pwd + "\"</i></td></tr>"
                pl += groupstring
                ids = self.groups[k].get_player_ids()
                ids.sort(id_compare)
                for id in ids:
                    if self.players.has_key(id):
                        if k != "0":
                            if (self.players[id]).role == "GM": FG = GCOLOR
                            elif (self.players[id]).role == "Player": FG = PCOLOR
                            else: FG = LCOLOR
                        else: FG = PCOLOR
                        pl += "<tr><td bgcolor=" + COLOR3 + ">"
                        pl += "<font color=" + FG + " " + SIZE + ">&nbsp;&nbsp;(" +  (self.players[id]).id  + ") "
                        pl += (self.players[id]).name
                        pl += "</font></td><td bgcolor=" + COLOR3 + " ><font color=" + FG + " " + SIZE + ">[IP: " + (self.players[id]).ip + "]</font></td><td  bgcolor=" + COLOR3 + " ><font color=" + FG + " " + SIZE + "> "
                        pl += (self.players[id]).idle_status()
                        pl += "</font></td><td><font color=" + FG + " " + SIZE + ">"
                        pl += (self.players[id]).connected_time_string()
                        pl += "</font>"

                    else:
                        self.groups[k].remove_player(id)
                        pl +="<tr><td colspan='4' bgcolor=" + COLOR3 + " >Bad Player Ref (#" + id + ") in group"
                pl+="</td></tr>"
            pl += "<tr><td colspan='4' bgcolor=" + COLOR1 + "><font color=" + COLOR4 + "><b><i>Statistics: groups: " + str(len(self.groups)) + "  players: " +  str(len(self.players)) + "</i></b></font></td></tr></table>"
        except Exception, e:
            self.log_msg(str(e))
        self.p_lock.release()
        return pl
