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
# File: mplay_client.py
# Author: Chris Davis
# Maintainer:
# Version:
#   $Id: mplay_client.py,v 1.71 2007/05/12 20:41:54 digitalxero Exp $
#
# Description: This file contains the code for the client stubs of the multiplayer
# features in the orpg project.
#

__version__ = "$Id: mplay_client.py,v 1.71 2007/05/12 20:41:54 digitalxero Exp $"

### Alpha ### 
##import orpg.minidom ## Deprecated. xml.parseXml calls minidom.parseString so it was superfluous and wasteful.
import socket
import Queue
import thread
import traceback
from threading import Event, Lock
from xml.sax.saxutils import escape
from struct import pack, unpack, calcsize
from string import *
from orpg.orpg_version import CLIENT_STRING, PROTOCOL_VERSION, VERSION
import errno
import os
import time
from orpg.orpgCore import component
from orpg.orpg_xml import xml

try:
    import bz2
    cmpBZ2 = True
except: cmpBZ2 = False

try:
    import zlib
    cmpZLIB = True
except: cmpZLIB = False


# This should be configurable
OPENRPG_PORT = 9557

# We should be sending a length for each packet
MPLAY_LENSIZE = calcsize( 'i' )
MPLAY_DISCONNECTED = 0
MPLAY_CONNECTED = 1
MPLAY_DISCONNECTING = 3
MPLAY_GROUP_CHANGE = 4
MPLAY_GROUP_CHANGE_F = 5
PLAYER_NEW = 1
PLAYER_DEL = 2
PLAYER_GROUP = 3

#  The next two messages are used to inform others that a player is typing
PLAYER_TYPING = 4
PLAYER_NOT_TYPING = 5
PLAYER_UPDATE = 6
GROUP_JOIN = 1
GROUP_NEW = 2
GROUP_DEL = 3
GROUP_UPDATE = 4
STATUS_SET_URL = 1

def parseXml(data):
    "parse and return doc"
    #print data
    doc = xml.parseXml(data)
    doc.normalize()
    return doc

def myescape(data):
    return escape(data,{"\"":""})

class mplay_event:
    def __init__(self,id,data=None):
        self.id = id
        self.data = data

    def get_id(self):
        return self.id

    def get_data(self):
        return self.data

BOOT_MSG = "YoU ArE ThE WeAkEsT LiNk. GoOdByE."

class client_base:

    # Player role definitions
    def __init__(self):
        self.outbox = Queue.Queue(0)
        self.inbox = Queue.Queue(0)
        self.startedEvent = Event()
        self.exitEvent = Event()
        self.sendThreadExitEvent = Event()
        self.recvThreadExitEvent = Event()
        self.id = "0"
        self.group_id = "0"
        self.name = ""
        self.role = "GM"
        ## Soon to be removed
        self.ROLE_GM = "GM"
        self.ROLE_PLAYER = "Player"
        self.ROLE_LURKER = "Lurker"
        ## --TaS
        self.ip = socket.gethostbyname(socket.gethostname())
        self.remote_ip = None
        self.version = VERSION
        self.protocol_version = PROTOCOL_VERSION
        self.client_string = CLIENT_STRING
        self.status = MPLAY_DISCONNECTED
        self.useCompression = False
        self.compressionType = 'Undefined'
        self.log_console = None
        self.sock = None
        self.text_status = "Idle"
        self.statLock = Lock()
        self.useroles = 0
        self.lastmessagetime = time.time()
        self.connecttime = time.time()

    def sendThread( self, arg ):
        "Sending thread.  This thread reads from the data queue and writes to the socket."

        # Wait to be told it's okay to start running
        self.startedEvent.wait()

        # Loop as long as we have a connection
        while( self.get_status() == MPLAY_CONNECTED ):
            try: readMsg = self.outbox.get( block=1 )
            except Exception, text:
                self.log_msg( ("outbox.get() got an exception:  ", text) )

            # If we are here, it's because we have data to send, no doubt!
            if self.status == MPLAY_CONNECTED:
                try:
                    # Send the entire message, properly formated/encoded
                    sent = self.sendMsg( self.sock, readMsg )
                except Exception, e:
                    self.log_msg( e )
            else:
                # If we are not connected, purge the data queue
                self.log_msg( "Data queued without a connection, purging data from queue..." )
        self.sendThreadExitEvent.set()
        self.log_msg( "sendThread has terminated..." )

    def recvThread( self, arg ):
        "Receiving thread.  This thread reads from the socket and writes to the data queue."

        # Wait to be told it's okay to start running
        self.startedEvent.wait()

        while( self.get_status() == MPLAY_CONNECTED ):
            readMsg = self.recvMsg( self.sock )
            try:
                if self.useCompression and self.compressionType != None:
                    readMsg = self.compressionType.decompress(readMsg)
            except: pass

            # Check the length of the message
            bytes = len( readMsg )

            # Make sure we are still connected
            if bytes == 0: break
            else:
                # Pass along the message so it can be processed
                self.inbox.put( readMsg )
                self.update_idle_time() #update the last message time
        if bytes == 0:
            self.log_msg( "Remote has disconnected!" )
            self.set_status( MPLAY_DISCONNECTING )
        self.outbox.put( "" )    # Make sure the other thread is woken up!
        self.sendThreadExitEvent.set()
        self.log_msg( "recvThread has terminated..." )

    def sendMsg( self, sock, msg ):
        """Very simple function that will properly encode and send a message to te
        remote on the specified socket."""

        if self.useCompression and self.compressionType != None:
            mpacket = self.compressionType.compress(msg)
            lpacket = pack('!i', len(mpacket))
            sock.send(lpacket)
            offset = 0
            while offset < len(mpacket):
                slice = buffer(mpacket, offset, len(mpacket)-offset)
                sent = sock.send(slice)
                offset += sent
            sentm = offset
        else:
            # Calculate our message length
            length = len(msg)

            # Encode the message length into network byte order
            lp = pack('!i', length)

            try:
                # Send the encoded length
                sentl = sock.send( lp )

                # Now, send the message the the length was describing
                sentm = sock.send( msg )
                if self.isServer(): self.log_msg(("data_sent", sentl+sentm))
            except socket.error, e: self.log_msg( e )
            except Exception, e: self.log_msg( e )
        return sentm

    def recvData( self, sock, readSize ):
        """Simple socket receive method.  This method will only return when the exact
        byte count has been read from the connection, if remote terminates our
        connection or we get some other socket exception."""
        data = ""
        offset = 0
        try:
            while offset != readSize:
                frag = sock.recv( readSize - offset )
                # See if we've been disconnected
                rs = len( frag )
                if rs <= 0:
                    # Loudly raise an exception because we've been disconnected!
                    raise IOError, "Remote closed the connection!"
                else:
                    # Continue to build complete message
                    offset += rs
                    data += frag
        except socket.error, e:
            self.log_msg( e )
            data = ""
        return data

    def recvMsg( self, sock ):
        """This method now expects to receive a message having a 4-byte prefix length.  It will ONLY read
        completed messages.  In the event that the remote's connection is terminated, it will throw an
        exception which should allow for the caller to more gracefully handle this exception event.

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
            if self.isServer():
                self.log_msg(("data_recv", length+4))
                # Make the peer IP address available for reference later
                if self.remote_ip is None:
                    self.remote_ip = self.sock.getpeername()
        except IOError, e: self.log_msg( e )
        except Exception, e: self.log_msg( e )
        return msgData

    def initialize_threads(self):
        "Starts up our threads (2) and waits for them to make sure they are running!"
        self.status = MPLAY_CONNECTED
        self.sock.setblocking(1)
        # Confirm that our threads have started
        thread.start_new_thread( self.sendThread,(0,) )
        thread.start_new_thread( self.recvThread,(0,) )
        self.startedEvent.set()

    def disconnect(self):
        self.set_status(MPLAY_DISCONNECTING)
        self.log_msg("client stub " + self.ip +" disconnecting...")
        self.log_msg("closing sockets...")
        try: self.sock.shutdown( 2 )
        except Exception, e:
            print "Caught exception:  " + str(e)
            print
            print "Continuing"
        self.set_status(MPLAY_DISCONNECTED)

    def reset(self,sock):
        self.disconnect()
        self.sock = sock
        self.initialize_threads()

    def update_role(self,role):
        self.useroles = 1
        self.role = role

    def use_roles(self):
        if self.useroles:
            return 1
        else:
            return 0
    def update_self_from_player(self, player):
        try: (self.name, self.ip, self.id, 
                self.text_status, self.version, 
                self.protocol_version, self.client_string, role) = player
        except Exception, e:
            print e
    """
     The IP field should really be deprecated as too many systems are NAT'd and/or behind firewalls for a
     client provided IP address to have much value.  As such, we now label it as deprecated.
    """
    def toxml(self,action):
        xml_data = '<player name="' + myescape(self.name) + '"'
        xml_data += ' action="' + action + '" id="' + self.id + '"'
        xml_data += ' group_id="' + self.group_id + '" ip="' + self.ip + '"'
        xml_data += ' status="' + self.text_status + '"'
        xml_data += ' version="' + self.version + '"'
        xml_data += ' protocol_version="' + self.protocol_version + '"'
        xml_data += ' client_string="' + self.client_string + '"'
        xml_data += ' useCompression="' + str(self.useCompression) + '"'
        if cmpBZ2 and (self.compressionType == 'Undefined' or self.compressionType == bz2):
            xml_data += ' cmpType="bz2"'
        elif cmpZLIB and (self.compressionType == 'Undefined' or self.compressionType == zlib):
            xml_data += ' cmpType="zlib"'
        else: xml_data += ' cmpType="None"'
        xml_data += ' />'
        return xml_data

    def log_msg(self,msg):
        if self.log_console:
            self.log_console(msg)

    def get_status(self):
        self.statLock.acquire()
        status = self.status
        self.statLock.release()
        return status

    def my_role(self):
        #Leaving this for testing.
        return self.role
        """
        if self.role == "GM":
            return self.ROLE_GM
        elif self.role == "Player":
            return self.ROLE_PLAYER
        elif self.role == "Lurker":
            return self.ROLE_LURKER
        return -1
        """

    def set_status(self,status):
        self.statLock.acquire()
        self.status = status
        self.statLock.release()

    def isServer( self ):
        # Return 1 if we are running as a server, else, return 0.
        # This method must be overloaded by whomever derives from us
        pass

    def __str__(self):
        return "%s(%s)\nIP:%s\ngroup_id:%s\n" % (self.name, self.id, self.ip, self.group_id)

    # idle time functions added by snowdog 3/31/04
    def update_idle_time(self):
        self.lastmessagetime = time.time()

    def idle_time(self):
        curtime = time.time()
        idletime = curtime - self.lastmessagetime
        return idletime

    def idle_status(self):
        idletime = self.idle_time()
        idlemins = idletime / 60
        status = "Unknown"
        if idlemins < 3: status = "Active"
        elif idlemins < 10:  status = "Idle ("+str(int(idlemins))+" mins)"
        else: status = "Inactive ("+str(int(idlemins))+" mins)"
        return status

    def connected_time(self):
        curtime = time.time()
        timeoffset = curtime - self.connecttime
        return timeoffset

    def connected_time_string(self):
        "returns the time client has been connected as a formated time string"
        ct = self.connected_time()
        d = int(ct/86400)
        h = int( (ct-(86400*d))/3600 )
        m = int( (ct-(86400*d)-(3600*h))/60)
        s = int( (ct-(86400*d)-(3600*h)-(60*m)) )
        cts =  zfill(d,2)+":"+zfill(h,2)+":"+zfill(m,2)+":"+zfill(s,2)
        return cts

#========================================================================
#
#
#                           MPLAY CLIENT
#
#
#========================================================================
class mplay_client(client_base):
    "mplay client"
    def __init__(self,name,callbacks):
        client_base.__init__(self)
        component.add('mp_client', self)
        self.xml = component.get('xml')
        self.set_name(name)
        self.on_receive = callbacks['on_receive']
        self.on_mplay_event = callbacks['on_mplay_event']
        self.on_group_event = callbacks['on_group_event']
        self.on_player_event = callbacks['on_player_event']
        self.on_status_event = callbacks['on_status_event']
        self.on_password_signal = callbacks['on_password_signal']
        # I know this is a bad thing to do but it has to be
        # be done to use the unified password manager.
        # Should really find a better solution. -- SD 8/03
        self.orpgFrame_callback = callbacks['orpgFrame']
        self.settings = self.orpgFrame_callback.settings
        self.ignore_id = []
        self.ignore_name = []
        self.players = {}
        self.groups = {}
        self.unique_cookie = 0
        self.msg_handlers = {}
        self.core_msg_handlers = []
        self.load_core_msg_handlers()

    # implement from our base class
    def isServer(self):
        return 0

    def get_chat(self):
        return self.orpgFrame_callback.chat

    def set_name(self,name):
        self.name =  name
        self.update()

    def set_text_status(self, status):
        if self.text_status != status:
            self.text_status = status
            self.update()

    def set_status_url(self, url="None"):
        self.on_status_event(mplay_event(STATUS_SET_URL,url))

    def update(self, evt=None):
        if self.status == MPLAY_CONNECTED:
            self.outbox.put(self.toxml('update'))
            self.inbox.put(self.toxml('update'))

    def get_group_info(self, id=0):
        self.statLock.acquire()
        id = self.groups[id]
        self.statLock.release()
        return id

    def get_my_group(self):
        self.statLock.acquire()
        id = self.groups[self.group_id]
        self.statLock.release()
        return id

    def get_groups(self):
        self.statLock.acquire()
        groups = self.groups.values()
        self.statLock.release()
        return groups

    def get_players(self):
        self.statLock.acquire()
        players = self.players.values()
        self.statLock.release()
        return players

    def get_player_info(self,id):
        self.statLock.acquire()
        player = self.players[id]
        self.statLock.release()
        return player

    def get_player_by_player_id(self,player):
        players = self.get_players()
        if self.players.has_key(player):
            for m in players:
                if player == m[2]: return m
        return -1

    def get_id(self):
        return self.id

    def get_my_info(self):
        return (self.name, self.ip, self.id, 
                self.text_status, self.version, 
                self.protocol_version, self.client_string, 
                self.role)

    def is_valid_id(self,id):
        self.statLock.acquire()
        value = self.players.has_key( id )
        self.statLock.release()
        return value

    def clear_players(self,save_self=0):
        self.statLock.acquire()
        keys = self.players.keys()
        for k in keys: del self.players[k]
        self.statLock.release()

    def clear_groups(self):
        self.statLock.acquire()
        keys = self.groups.keys()
        for k in keys: del self.groups[k]
        self.statLock.release()

    def find_role(self,id):
        return self.players[id].role

    def get_ignore_list(self):
        try: return (self.ignore_id, self.ignore_name)
        except: return (None, None)

    def toggle_ignore(self, id):
        for m in self.ignore_id:
            if `self.ignore_id[self.ignore_id.index(m)]` ==  `id`:
                name = self.ignore_name[self.ignore_id.index(m)]
                self.ignore_id.remove(m)
                self.ignore_name.remove(name)
                return (0,id,name)
        self.ignore_name.append(self.players[id][0])
        self.ignore_id.append(self.players[id][2])
        return (1,self.players[id][2],self.players[id][0])

    def boot_player(self,id,boot_pwd = ""):
        #self.send(BOOT_MSG,id)
        msg = '<boot boot_pwd="' + boot_pwd + '"/>'
        self.send(msg,id)

#---------------------------------------------------------
# [START] Snowdog Password/Room Name altering code 12/02
#---------------------------------------------------------

    def set_room_pass(self,npwd,pwd=""):
        recycle_bin = "<alter key=\"pwd\" "
        recycle_bin += "val=\"" +npwd+ "\" bpw=\"" + pwd + "\" "
        recycle_bin += "plr=\"" + self.id +"\" gid=\"" + self.group_id + "\" />"
        self.outbox.put(recycle_bin); del recycle_bin #makes line easier to read. --TaS
        self.update()

    def set_room_name(self,name,pwd=""):
        loc = name.find("&")
        oldloc=0
        while loc > -1:
            loc = name.find("&",oldloc)
            if loc > -1:
                b = name[:loc]
                e = name[loc+1:]
                name = b + "&amp;" + e
                oldloc = loc+1
        loc = name.find('"')
        oldloc=0
        while loc > -1:
            loc = name.find('"',oldloc)
            if loc > -1:
                b = name[:loc]
                e = name[loc+1:]
                name = b + "&quot;" + e
                oldloc = loc+1
        loc = name.find("'")
        oldloc=0
        while loc > -1:
            loc = name.find("'",oldloc)
            if loc > -1:
                b = name[:loc]
                e = name[loc+1:]
                name = b + "&#39;" + e
                oldloc = loc+1
        recycle_bin = "<alter key=\"name\" "
        recycle_bin += "val=\"" + name + "\" bpw=\"" + pwd + "\" "
        recycle_bin += "plr=\"" + self.id +"\" gid=\"" + self.group_id + "\" />"
        self.outbox.put(recycle_bin); del recycle_bin #makes line easier to read. --TaS
        self.update()

#---------------------------------------------------------
# [END] Snowdog Password/Room Name altering code  12/02
#---------------------------------------------------------

    def display_roles(self):
        self.outbox.put("<role action=\"display\" player=\"" + self.id +"\" group_id=\""+self.group_id + "\" />")

    def get_role(self):
        self.outbox.put("<role action=\"get\" player=\"" + self.id +"\" group_id=\""+self.group_id + "\" />")

    def set_role(self,player,role,pwd=""):
        recycle_bin = "<role action=\"set\" player=\"" + player + "\" "
        recycle_bin += "role=\"" +role+ "\" boot_pwd=\"" + pwd + "\" group_id=\"" + self.group_id + "\" />"
        self.outbox.put(recycle_bin); del recycle_bin #makes line easer to read. --TaS
        self.update()

    def send(self,msg,player="all"):
        if self.status == MPLAY_CONNECTED and player != self.id:
            self.outbox.put("<msg to='"+player+"' from='"+self.id+"' group_id='"+self.group_id+"' />"+msg)
        self.check_my_status()

    def send_sound(self, snd_xml):
        if self.status == MPLAY_CONNECTED:
            self.outbox.put(snd_xml)
        self.check_my_status()

    def send_create_group(self,name,pwd,boot_pwd,minversion):
        recycle_bin = "<create_group from=\""+self.id+"\" "
        recycle_bin += "pwd=\""+pwd+"\" name=\""+ name+"\" boot_pwd=\""+boot_pwd+"\" "
        recycle_bin += "min_version=\"" + minversion +"\" />"
        self.outbox.put(recycle_bin); del recycle_bin #makes line easier to read. --TaS

    def send_join_group(self,group_id,pwd):
        if (group_id != 0): self.update_role("Lurker")
        self.outbox.put("<join_group from=\""+self.id+"\" pwd=\""+pwd+"\" group_id=\""+str(group_id)+"\" />")

    def poll(self, evt=None):
        try:
            msg = self.inbox.get_nowait()
        except:
            if self.get_status() != MPLAY_CONNECTED:
                self.check_my_status()
        else:
            try: self.pretranslate(msg)
            except Exception, e:
                print "The following  message: " + str(msg)
                print "created the following exception: "
                traceback.print_exc()

    def add_msg_handler(self, tag, function, core=False):
        if not self.msg_handlers.has_key(tag):
            self.msg_handlers[tag] = function
            if core: self.core_msg_handlers.append(tag)
        else: print 'XML Messages ' + tag + ' already has a handler'

    def remove_msg_handler(self, tag):
        if self.msg_handlers.has_key(tag) and not tag in self.core_msg_handlers:
            del self.msg_handlers[tag]
        else: print 'XML Messages ' + tag + ' already deleted'

    def load_core_msg_handlers(self):
        self.add_msg_handler('msg', self.on_msg, True)
        self.add_msg_handler('ping', self.on_ping, True)
        self.add_msg_handler('group', self.on_group, True)
        self.add_msg_handler('role', self.on_role, True)
        self.add_msg_handler('player', self.on_player, True)
        self.add_msg_handler('password', self.on_password, True)
        self.add_msg_handler('sound', self.on_sound, True)

    def pretranslate(self,data):
        # Pre-qualify our data.  If we don't have atleast 5-bytes, then there is
        # no way we even have a valid message!
        if len(data) < 5: return
        end = data.find(">")
        head = data[:end+1]
        msg = data[end+1:]
        xml_dom = self.xml.parseXml(head)
        xml_dom = xml_dom._get_documentElement()
        tag_name = xml_dom._get_tagName()
        id = xml_dom.getAttribute("from")
        if id == '': id = xml_dom.getAttribute("id")
        if self.msg_handlers.has_key(tag_name): self.msg_handlers[tag_name](id, data, xml_dom)
        else:
            #Unknown messages recived ignoring
            #using pass insted or printing an error message
            #because plugins should now be able to send and proccess messages
            #if someone is using a plugin to send messages and this user does not
            #have the plugin they would be getting errors
            pass
        if xml_dom: xml_dom.unlink()

    def on_sound(self, id, data, xml_dom):
        (ignore_id,ignore_name) = self.get_ignore_list()
        for m in ignore_id:
            if m == id:
                # yes we are
                print "ignoring sound from player:"
                return
        chat = self.get_chat()
        snd = xml_dom.getAttribute("url")
        loop_sound = xml_dom.getAttribute("loop")
        chat.sound_player.play(snd, "remote", loop_sound)

    def on_msg(self, id, data, xml_dom):
        end = data.find(">")
        head = data[:end+1]
        msg = data[end+1:]
        if id == "0":
            self.on_receive(msg,None)      #  None get's interpreted in on_receive as the sys admin.
                                           #  Doing it this way makes it harder to impersonate the admin
        else:
            if self.is_valid_id(id): self.on_receive(msg,self.players[id])
        if xml_dom: xml_dom.unlink()

    def on_ping(self, id, msg, xml_dom):
        #a REAL ping time implementation by Snowdog 8/03
        # recieves special server <ping time="###" /> command
        # where ### is a returning time from the clients ping command
        #get current time, pull old time from object and compare them
        # the difference is the latency between server and client * 2
        ct = time.clock()
        ot = xml_dom.getAttribute("time")
        latency = float(float(ct) - float(ot))
        latency = int( latency * 10000.0 )
        latency = float( latency) / 10.0
        ping_msg = "Ping Results: " + str(latency) + " ms (parsed message, round trip)"
        self.on_receive(ping_msg,None)
        if xml_dom: xml_dom.unlink()

    def on_group(self, id, msg, xml_dom):
        name = xml_dom.getAttribute("name")
        players = xml_dom.getAttribute("players")
        act = xml_dom.getAttribute("action")
        pwd = xml_dom.getAttribute("pwd")
        group_data = (id, name, pwd, players)

        if act == 'new':
            self.groups[id] = group_data
            self.on_group_event(mplay_event(GROUP_NEW, group_data))
        elif act == 'del':
            del self.groups[id]
            self.on_group_event(mplay_event(GROUP_DEL, group_data))
        elif act == 'update':
            self.groups[id] = group_data
            self.on_group_event(mplay_event(GROUP_UPDATE, group_data))
        if xml_dom: xml_dom.unlink()

    def on_role(self, id, msg, xml_dom):
        act = xml_dom.getAttribute("action")
        role = xml_dom.getAttribute("role")
        if (act == "set") or (act == "update"):
            try:
                (a,b,c,d,e,f,g,h) = self.players[id]
                if id == self.id:
                    self.players[id] = (a,b,c,d,e,f,g,role)
                    self.update_role(role)
                else: self.players[id] = (a,b,c,d,e,f,g,role)
                self.on_player_event(mplay_event(PLAYER_UPDATE,self.players[id]))
            except: pass
        if xml_dom: xml_dom.unlink()

    def on_player(self, id, msg, xml_dom):
        act = xml_dom.getAttribute("action")
        ip = xml_dom.getAttribute("ip")
        name = xml_dom.getAttribute("name")
        status = xml_dom.getAttribute("status")
        version = xml_dom.getAttribute("version")
        protocol_version = xml_dom.getAttribute("protocol_version")
        client_string = xml_dom.getAttribute("client_string")
        try: player = (name, ip, id, status, 
                        version, protocol_version, 
                        client_string, self.players[id][7])
        except Exception, e:
            player = (name, ip, id, status, 
                        version, protocol_version, 
                        client_string, "Player")
        if act == "new":
            self.players[id] = player
            self.on_player_event(mplay_event(PLAYER_NEW, self.players[id]))
        elif act == "group":
            self.group_id = xml_dom.getAttribute("group_id")
            self.clear_players()
            self.on_mplay_event(mplay_event(MPLAY_GROUP_CHANGE, self.groups[self.group_id]))
            self.players[self.id] = self.get_my_info() #(self.name,self.ip,self.id,self.text_status)
            self.on_player_event(mplay_event(PLAYER_NEW, self.players[self.id]))
        elif act == "failed":
            self.on_mplay_event(mplay_event(MPLAY_GROUP_CHANGE_F))
        elif act == "del":
            self.on_player_event(mplay_event(PLAYER_DEL,self.players[id]))
            if self.players.has_key(id): del self.players[id]
            if id == self.id: self.do_disconnect()
        #  the next two cases handle the events that are used to let you know when others are typing
        elif act == "update":
            if id == self.id:
                self.players[id] = player
                self.update_self_from_player(player)
            else: self.players[id] = player
            dont_send = 0
            for m in self.ignore_id:
                if m == id: dont_send=1
            if dont_send != 1: self.on_player_event(mplay_event(PLAYER_UPDATE,self.players[id]))
        if xml_dom: xml_dom.unlink()

    def on_password(self, id, msg, xml_dom):
        signal = type = id = data = None
        id = xml_dom.getAttribute("id")
        type = xml_dom.getAttribute("type")
        signal = xml_dom.getAttribute("signal")
        data = xml_dom.getAttribute("data")
        self.on_password_signal( signal,type,id,data )
        if xml_dom:
            xml_dom.unlink()

    def check_my_status(self):
        status = self.get_status()
        if status == MPLAY_DISCONNECTING: self.do_disconnect()

    def connect(self, addressport):
        """Establish a connection to a server while still using sendThread & recvThread for its
        communication."""
        if self.is_connected():
            self.log_msg( "Client is already connected to a server?!?  Need to disconnect first." )
            return 0
        xml_dom = None
        self.inbox = Queue.Queue(0)
        self.outbox = Queue.Queue(0)
        addressport_ar = addressport.split(":")
        if len(addressport_ar) == 1:
            address = addressport_ar[0]
            port = OPENRPG_PORT
        else:
            address = addressport_ar[0]
            port = int(addressport_ar[1])
        self.host_server = addressport
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.sock.connect((address,port))
            # send client into with id=0
            self.sendMsg( self.sock, self.toxml("new") )
            data = self.recvMsg( self.sock )
            # get new id and group_id
            xml_dom = self.xml.parseXml(data)
            xml_dom = xml_dom._get_documentElement()
            self.id = xml_dom.getAttribute("id")
            self.group_id = xml_dom.getAttribute("group_id")
            if xml_dom.hasAttribute('useCompression') and xml_dom.getAttribute('useCompression') == 'True':
                self.useCompression = True
                if xml_dom.hasAttribute('cmpType'):
                    if cmpBZ2 and xml_dom.getAttribute('cmpType') == 'bz2':
                        self.compressionType = bz2
                    elif cmpZLIB and xml_dom.getAttribute('cmpType') == 'zlib':
                        self.compressionType = zlib
                    else: self.compressionType = None
                else: self.compressionType = bz2
            #send confirmation
            self.sendMsg( self.sock, self.toxml("new") )
        except Exception, e:
            self.log_msg(e)
            if xml_dom: xml_dom.unlink()
            return 0

        # Start things rollings along
        self.initialize_threads()
        self.on_mplay_event(mplay_event(MPLAY_CONNECTED))
        self.players[self.id] = (self.name, self.ip, self.id, 
                                self.text_status, self.version, 
                                self.protocol_version, self.client_string, self.role)
        self.on_player_event(mplay_event(PLAYER_NEW,self.players[self.id]))
        if xml_dom: xml_dom.unlink()
        return 1

    def start_disconnect(self):
        self.on_mplay_event(mplay_event(MPLAY_DISCONNECTING))
        self.outbox.put( self.toxml("del") )
        ## Client Side Disconect Forced -- Snowdog 10-09-2003
        #pause to allow GUI events time to sync.
        time.sleep(1)
        self.do_disconnect()

    def do_disconnect(self):
        client_base.disconnect(self)
        self.clear_players()
        self.clear_groups()
        self.useroles = 0
        self.on_mplay_event(mplay_event(MPLAY_DISCONNECTED))
        self.useCompression = False

    def is_connected(self):
        return (self.status == MPLAY_CONNECTED)

    def get_next_id(self):
        self.unique_cookie += 1
        return_str = self.id + "-" + str(self.unique_cookie)
        return return_str
