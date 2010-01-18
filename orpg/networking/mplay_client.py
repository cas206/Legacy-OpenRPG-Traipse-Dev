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
#   $Id: mplay_client.py,v Traipse 'Ornery-Orc' prof.ebral Exp $
#
# Description: This file contains the code for the client stubs of the multiplayer
# features in the orpg project.
#

__version__ = "$Id: mplay_client.py,v Traipse 'Ornery-Orc' prof.ebral Exp $"

import socket, Queue, thread, traceback, errno, os, time

from threading import Event, Lock
from xml.sax.saxutils import escape
from struct import pack, unpack, calcsize
from string import *
from orpg.orpg_version import CLIENT_STRING, PROTOCOL_VERSION, VERSION

from orpg.orpgCore import component
from orpg.orpg_xml import xml
from orpg.tools.orpg_log import debug
from orpg.tools.settings import settings

from xml.etree.ElementTree import ElementTree, Element, iselement
from xml.etree.ElementTree import fromstring, tostring
from xml.parsers.expat import ExpatError

try:
    import bz2
    cmpBZ2 = True
except: cmpBZ2 = False

try:
    import zlib
    cmpZLIB = True
except: cmpZLIB = False

# Default, is configurable
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
    doc = xml.parseXml(data)
    doc.normalize()
    return doc

def myescape(data):
    return escape(data,{"\"":""})

class mplay_event:
    def __init__(self, id, data=None):
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
        try: self.ip = socket.gethostbyname(socket.gethostname())
        except: self.ip = socket.gethostbyname('localhost')
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
            try: readMsg = self.outbox.get(block=1)
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
        self.outbox.put("")    # Make sure the other thread is woken up!
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
            length = len(msg) # Calculate our message length
            lp = pack('!i', length) # Encode the message length into network byte order
            try:
                sentl = sock.send( lp ) # Send the encoded length
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

    def recvMsg(self, sock):
        """This method now expects to receive a message having a 4-byte prefix length.  It will ONLY read completed messages.  In the event that the remote's connection is terminated, it will throw an exception which should allow for the caller to more gracefully handle this exception event.

        Because we use strictly reading ONLY based on the length that is told to use, we no longer have to worry about partially adjusting for fragmented buffers starting somewhere within a buffer that we've read.  Rather, it will get ONLY a whole message and nothing more.  Everything else will remain buffered with the OS until we attempt to read the next complete message."""
        msgData = ""
        try:
            lenData = self.recvData( sock, MPLAY_LENSIZE )
            (length,) = unpack('!i', lenData) # Now, convert to a usable form
            msgData = self.recvData( sock, length ) # Read exactly the remaining amount of data
            if self.isServer():
                self.log_msg(("data_recv", length+4))
                if self.remote_ip is None: # Make the peer IP address available for reference later
                    self.remote_ip = self.sock.getpeername()
        except IOError, e: self.log_msg( e )
        except Exception, e: self.log_msg( e )
        return msgData

    def initialize_threads(self):
        "Starts up our threads (2) and waits for them to make sure they are running!"
        self.status = MPLAY_CONNECTED
        self.sock.setblocking(1)
        # Confirm that our threads have started
        thread.start_new_thread( self.sendThread,(0,))
        thread.start_new_thread( self.recvThread,(0,))
        self.startedEvent.set()

    def disconnect(self):
        self.set_status(MPLAY_DISCONNECTING)
        self.log_msg("client stub " + self.ip +" disconnecting...")
        self.log_msg("closing sockets...")
        try: self.sock.shutdown(2)
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
        if self.useroles: return 1
        else: return 0

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
    def toxml(self, action):
        el = Element('player')
        el.set('name', self.name)
        el.set('action', action)
        el.set('role', self.role)
        el.set('id', self.id)
        el.set('group_id', self.group_id)
        el.set('ip', self.ip)
        el.set('status', self.text_status)
        el.set('version', self.version)
        el.set('protocol_version', self.protocol_version)
        el.set('client_string', self.client_string)
        el.set('useCompression', str(self.useCompression))
        cmpType = 'None'
        if cmpBZ2 and (self.compressionType == 'Undefined' or self.compressionType == bz2): cmpType = 'bz2'
        elif cmpZLIB and (self.compressionType == 'Undefined' or self.compressionType == zlib): cmpType = 'zlib'
        el.set('cmpType', cmpType)
        return tostring(el)

    def log_msg(self,msg):
        if self.log_console: self.log_console(msg)

    def get_status(self):
        self.statLock.acquire()
        status = self.status
        self.statLock.release()
        return status

    def my_role(self):
        return self.role

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
        return (1, self.players[id][2], self.players[id][0])

    def boot_player(self,id,boot_pwd = ""):
        el = Element('boot')
        el.set('boot_pwd', boot_pwd)
        self.send(tostring(el), id)

    def set_room_pass(self, npwd, pwd=""):
        el = Element('alter')
        el.set('key', 'pwd')
        el.set('val', npwd)
        el.set('bpw', pwd)
        el.set('plr', self.id)
        el.set('gid', self.group_id)
        self.outbox.put(tostring(el))
        self.update()

    def set_room_name(self, name, pwd=""):
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
        el = Element('alter')
        el.set('key', 'pwd')
        #el.set('val', npwd)
        el.set('bpw', str(pwd))
        el.set('plr', self.id)
        el.set('gid', self.group_id)
        self.outbox.put(tostring(el))
        self.update()

    def display_roles(self):
        el = Element('role')
        el.set('action', 'display')
        el.set('player', self.id)
        el.set('group_id', self.group_id)
        self.outbox.put(tostring(el))

    def get_role(self):
        el = Element('role')
        el.set('action', 'get')
        el.set('player', self.id)
        el.set('group_id', self.group_id)
        self.outbox.put(tostring(el))

    def set_role(self, player, role, pwd=""):
        el = Element('role')
        el.set('action', 'set')
        el.set('player', player)
        el.set('role', role)
        el.set('boot_pwd', pwd)
        el.set('group_id', self.group_id)
        self.outbox.put(tostring(el))
        self.update()

    def send(self, msg, player="all"):
        if self.status == MPLAY_CONNECTED and player != self.id:
            ### Pre Alpha ###
            #el = Element('msg')
            #el.set('to', player)
            #el.set('from', self.id)
            #el.set('group_id', self.group_id)
            #el.append(fromstring(msg))
            #self.outbox.put(tostring(el))
            ### Current chat is not ready for Element Tree ###
            self.outbox.put("<msg to='"+player+"' from='"+self.id+"' group_id='"+self.group_id+"' />"+msg)
        self.check_my_status()

    def send_sound(self, snd_xml):
        if self.status == MPLAY_CONNECTED:
            self.outbox.put(snd_xml)
        self.check_my_status()

    def send_create_group(self, name, pwd, boot_pwd, min_version):
        el = Element('create_group')
        el.set('from', self.id)
        el.set('pwd', pwd)
        el.set('name', name)
        el.set('boot_pwd', boot_pwd)
        el.set('min_version', min_version)
        self.outbox.put(tostring(el))

    def send_join_group(self, group_id, pwd):
        if (group_id != 0): self.update_role("Lurker")
        el = Element('join_group')
        el.set('from', self.id)
        el.set('pwd', pwd)
        el.set('group_id', str(group_id))
        self.outbox.put(tostring(el))

    def poll(self, evt=None):
        try: msg = self.inbox.get_nowait()
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

    def pretranslate(self, data):
        # Pre-qualify our data.  If we don't have atleast 5-bytes, then there is
        # no way we even have a valid message!
        if len(data) < 5: return
        try: el = fromstring(data)
        except ExpatError:
            end = data.find(">")
            head = data[:end+1]
            msg = data[end+1:]
            ### This if statement should help close invalid messages. ###
            if head[end:] != '/':
                if head[end:] != '>': head = head[:end] + '/>' 
            try: el = fromstring(head)
            except: el = fromstring(head[:end] +'/>')
            ###########

            try:
                el1 = fromstring(msg)
                el.append(el1)
            except ExpatError:
                el.text = msg
        id = el.get('from') or el.get('id')
        if el.tag in self.msg_handlers: self.msg_handlers[el.tag](id, data, el)

    def on_sound(self, id, data, etreeEl):
        (ignore_id,ignore_name) = self.get_ignore_list()
        for m in ignore_id:
            if m == id:
                # yes we are
                print "ignoring sound from player:"
                return
        chat = self.get_chat()
        chat.sound_player.play(etreeEl.get('url'), 'remote', etreeEl.get('loop'))

    def on_msg(self, id, data, etreeEl):
        end = data.find(">")
        head = data[:end+1]
        msg = data[end+1:]
        if msg[-6:] == '</msg>': msg = msg[:-6]
        if id == "0": self.on_receive(msg, None)
        #  None get's interpreted in on_receive as the sys admin.
        #  Doing it this way makes it harder to impersonate the admin
        elif self.is_valid_id(id): self.on_receive(msg, self.players[id])

    def on_ping(self, id, msg, etreeEl):
        # A REAL ping time implementation by Snowdog 8/03
        # recieves special server <ping time="###" /> command
        # where ### is a returning time from the clients ping command
        # get current time, pull old time from object and compare them
        # the difference is the latency between server and client * 2
        ct = time.clock()
        ot = etreeEl.get("time")
        latency = float(float(ct) - float(ot))
        latency = int(latency * 10000.0)
        latency = float(latency) / 10.0
        ping_msg = "Ping Results: " + str(latency) + " ms (parsed message, round trip)"
        self.on_receive(ping_msg, None)

    def on_group(self, id, msg, etreeEl):
        act = etreeEl.get("action")
        group_data = (id, etreeEl.get("name"), etreeEl.get("pwd"), etreeEl.get("players"))
        if act == 'new' or act == 'update':
            self.groups[id] = group_data
            if act == 'update': self.on_group_event(mplay_event(GROUP_UPDATE, group_data))
            elif act == 'new': self.on_group_event(mplay_event(GROUP_NEW, group_data))
        elif act == 'del':
            del self.groups[id]
            self.on_group_event(mplay_event(GROUP_DEL, group_data))

    def on_role(self, id, msg, etreeEl):
        act = etreeEl.get("action")
        if (act == "set") or (act == "update"):
            try:
                (a,b,c,d,e,f,g,h) = self.players[id]
                if id == self.id:
                    self.players[id] = (a,b,c,d,e,f,g,etreeEl.get("role"))
                    self.update_role(etreeEl.get("role"))
                else: self.players[id] = (a,b,c,d,e,f,g,etreeEl.get("role"))
                self.on_player_event(mplay_event(PLAYER_UPDATE, self.players[id]))
            except: pass

    def on_player(self, id, msg, etreeEl):
        act = etreeEl.get("action")
        try: player = (etreeEl.get("name"), etreeEl.get("ip"), id, etreeEl.get("status"), 
                        etreeEl.get("version"), etreeEl.get("protocol_version"), 
                        etreeEl.get("client_string"), self.players[id][7])
        except Exception, e:
            player = (etreeEl.get("name"), etreeEl.get("ip"), id, etreeEl.get("status"), 
                        etreeEl.get("version"), etreeEl.get("protocol_version"), 
                        etreeEl.get("client_string"), "Player")
            print e
        if act == "new":
            self.players[id] = player
            self.on_player_event(mplay_event(PLAYER_NEW, self.players[id]))
        elif act == "group":
            self.group_id = etreeEl.get('group_id')
            self.clear_players()
            self.on_mplay_event(mplay_event(MPLAY_GROUP_CHANGE, self.groups[self.group_id]))
            self.players[self.id] = self.get_my_info() 
            self.on_player_event(mplay_event(PLAYER_NEW, self.players[self.id]))
        elif act == "failed":
            self.on_mplay_event(mplay_event(MPLAY_GROUP_CHANGE_F))
        elif act == "del":
            self.on_player_event(mplay_event(PLAYER_DEL, self.players[id]))
            if self.players.has_key(id): del self.players[id]
            if id == self.id: self.do_disconnect()
        elif act == "update":
            if id == self.id:
                self.players[id] = player
                self.update_self_from_player(player)
            else: self.players[id] = player
            dont_send = 0
            for m in self.ignore_id: 
                if m == id: dont_send=1
            if dont_send != 1: self.on_player_event(mplay_event(PLAYER_UPDATE, self.players[id]))

    def on_password(self, id, msg, etreeEl):
        self.on_password_signal(etreeEl.get("signal"), etreeEl.get("type"), 
                                etreeEl.get("id"), etreeEl.get("data"))

    def check_my_status(self):
        status = self.get_status()
        if status == MPLAY_DISCONNECTING: self.do_disconnect()

    def connect(self, addressport):
        """Establish a connection to a server while still using sendThread & recvThread for its
        communication."""
        if self.is_connected():
            self.log_msg( "Client is already connected to a server?!?  Need to disconnect first." )
            return 0
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
            outgoing = self.toxml('new')
            if iselement(outgoing): outgoing = tostring(outgoing)
            self.sendMsg(self.sock, outgoing)
            data = self.recvMsg(self.sock)
            # get new id and group_id
            el = fromstring(data)
            self.id = el.get('id')
            self.group_id = el.get('group_id')
            if el.get('useCompression') == 'True':
                self.useCompression = True
                if cmpBZ2 and el.get('cmpType') == 'bz2':
                    self.compressionType = bz2
                elif cmpZLIB and el.get('cmpType') == 'zlib':
                    self.compressionType = zlib
                else: self.compressionType = None
            #send confirmation
            outgoing = self.toxml('new')
            if iselement(outgoing): outgoing = tostring(outgoing)
            self.sendMsg(self.sock, outgoing)
        except Exception, e:
            print e
            self.log_msg(e)
            return 0
        # Start things rollings along
        self.initialize_threads()
        self.on_mplay_event(mplay_event(MPLAY_CONNECTED))
        self.players[self.id] = (self.name, self.ip, self.id, 
                                self.text_status, self.version, 
                                self.protocol_version, self.client_string, self.role)
        self.on_player_event(mplay_event(PLAYER_NEW,self.players[self.id]))
        return 1

    def start_disconnect(self):
        self.on_mplay_event(mplay_event(MPLAY_DISCONNECTING))
        outgoing = self.toxml('del')
        if iselement(outgoing): outgoing = tostring(outgoing)
        self.outbox.put(outgoing)
        ## Client Side Disconnect Forced -- Snowdog 10-09-2003
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

