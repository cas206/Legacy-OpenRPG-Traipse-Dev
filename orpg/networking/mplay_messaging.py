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
# File: mplay_messaging.py
# Author: Dj Gilcrease
# Maintainer:
# Version:
#   $Id: mplay_messaging.py,v Traipse 'Ornery-Orc' prof.ebral Exp $
#
# Description: This file contains the code for the client / server messaging
#

__version__ = "$Id: mplay_messaging.py,v Traipse 'Ornery-Orc' prof.ebral Exp $"

import socket, Queue, thread, traceback, os, time

from threading import Event, Lock
from xml.sax.saxutils import escape
from struct import pack, unpack, calcsize
from string import *
from orpg.orpg_version import VERSION, PROTOCOL_VERSION, CLIENT_STRING, SERVER_MIN_CLIENT_VERSION

from orpg.tools.orpg_log import logger
from orpg.orpgCore import component

def myescape(data):
    return escape(data,{"\"":""})

class messenger:
    def __init__(self, *args, **kwargs):
        self.dir_struct = component.get("dir_struct") #used?
        self.validate = component.get("validate") #used??
        if kwargs.has_key('isServer'):
            self.isServer = kwargs['isServer']
        else:
            self.isServer = False
        self.listen_event = Event()
        self.outbox = Queue.Queue(0)
        self.inbox_event = Event()
        self.inbox = Queue.Queue(0)
        self.startedEvent = Event()
        self.exitEvent = Event()
        self.sendThreadExitEvent = Event()
        self.recvThreadExitEvent = Event()
        self.port = int(component.get("settings").get_setting("port")) ##used even?
        self.ip = socket.gethostbyname(socket.gethostname())
        self.lensize = calcsize('i')
        self.mplay_type = ('disconnected', 'connected', 
                            'disconnecting', 'group change', 'group change failed')
        self.status = self.mplay_type[0]
        self.alive = False
        self.sock = None
        self.version = VERSION
        self.protocol_version = PROTOCOL_VERSION
        self.client_string = CLIENT_STRING
        self.minClientVersion = SERVER_MIN_CLIENT_VERSION
        self.id = "0"
        self.group_id = "0"
        self.name = ""
        self.role = "GM"
        self.ROLE_GM = "GM"
        self.ROLE_PLAYER = "PLAYER"
        self.ROLE_LURKER = "LURKER"
        self.text_status = "Idle"
        self.statLock = Lock()
        self.useroles = 0
        self.lastmessagetime = time.time()
        self.connecttime = time.time()
        self.timeout_time = None
        self.ignorelist = {}
        self.players = {}
        self.groups = {}

        ### Alpha ###
        self.inbox = kwargs['inbox'] or pass
        self.sock = kwargs['sock'] or pass
        self.ip = kwargs['ip'] or pass
        self.role = kwargs['role'] or pass
        self.id = kwargs['id'] or pass
        self.group_id = kwargs['group_id'] or pass
        self.name = kwargs['name'] or pass
        self.version = kwargs['version'] or pass
        self.protocol_version = kwargs['protocol_version'] or pass
        self.client_string = kwargs['client_string'] or pass


    def build_message(self, *args, **kwargs):
        message = '<' + args[0]

        #Setup the attributes of the message
        if len(kwargs) > 0:
            for attrib in kwargs.keys():
                message += ' ' + attrib + '="' + str(kwargs[attrib]) + '"'

        #Add the actual message if there is one
        if len(args) > 1:
            #Close the first part
            message += '>'
            message += escape(args[1])
            #Close the whole thing
            message += '</' + args[0] + '>'
        else: message += ' />'
        return message

    def disconnect(self):
        self.set_status(2)
        logger.debug("client stub " + self.ip +" disconnecting...")
        logger.debug("closing sockets...")
        try:
            self.sock.shutdown( 2 )
        except:
            logger.general("Caught exception:\n" + traceback.format_exc())
        self.set_status(0)

    def reset(self, sock):
        self.disconnect()
        self.sock = sock
        self.initialize_threads()

    def update_role(self, role):
        self.useroles = 1
        self.role = role

    def use_roles(self):
        return self.useroles

    def update_self_from_player(self, player):
        try:
            (self.name, self.ip, self.id, self.text_status, 
            self.version, self.protocol_version, self.client_string,role) = player
        except:
            logger.general("Exception:  messenger->update_self_from_player():\n" + traceback.format_exc())

    def toxml(self, act):
        logger.exception("DEPRECIATED! messenger->toxml()")
        xml_data = self.build_message('player',
                                name=myescape(self.name),
                                action=act,
                                id=self.id,
                                group_id=self.group_id,
                                ip=self.ip,
                                status=self.text_status,
                                version=self.version,
                                protocol_version=self.protocol_version,
                                client_string=self.client_string
                                )
        return xml_data

    def get_status(self):
        self.statLock.acquire()
        status = self.status
        self.statLock.release()
        return status

    def my_role(self):
        return self.role

    def set_status(self, status):
        self.statLock.acquire()
        self.status = status
        self.statLock.release()

    def initialize_threads(self):
        "Starts up our threads (2) and waits for them to make sure they are running!"
        self.status = 'connected'
        self.sock.setblocking(1)

        # Confirm that our threads have started
        thread.start_new_thread( self.sendThread,(0,) )
        thread.start_new_thread( self.recvThread,(0,) )
        self.startedEvent.set()

    def __str__(self):
        return "%s(%s)\nIP:%s\ngroup_id:%s\n%s (%s)" % (self.name, self.id, self.ip, self.group_id, self.idle_time(), self.connected_time())

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
        elif idlemins < 10: status = "Idle ("+str(int(idlemins))+" mins)"
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

    def clear_timeout(self):
        self.timeout_time = None

    def check_time_out(self):
        if self.timeout_time == None: self.timeout_time = time.time()
        curtime = time.time()
        diff = curtime - self.timeout_time
        if diff > 1800: return 1
        else: return 0

    def send(self, msg):
        if self.get_status() == 'connected': self.outbox.put(msg)

    def change_group(self, group_id, groups):
        old_group_id = str(self.group_id)
        groups[group_id].add_player(self.id)
        groups[old_group_id].remove_player(self.id)
        self.group_id = group_id
        self.outbox.put(self.toxml('group'))
        msg = groups[group_id].game_map.get_all_xml()
        self.send(msg)
        return old_group_id

    def take_dom(self, xml_dom):
        self.name = xml_dom.getAttribute("name")
        self.text_status = xml_dom.getAttribute("status")

    def add_msg_handler(self, tag, function, core=False):
        if not self.msg_handlers.has_key(tag):
            self.msg_handlers[tag] = function
            if core: self.core_msg_handlers.append(tag)
        else: print 'XML Messages ' + tag + ' already has a handler'

    def remove_msg_handler(self, tag):
        if self.msg_handlers.has_key(tag) and not tag in self.core_msg_handlers:
            del self.msg_handlers[tag]
        else: print 'XML Messages ' + tag + ' already deleted'

    #Message Handaling
    def message_handler(self, arg):
        xml_dom = None
        logger.note("message handler thread running...", ORPG_NOTE)
        while self.alive or self.status == 'connected':
            data = None
            try: data = self.inbox.get(0)
            except Queue.Empty:
                time.sleep(0.25) #sleep 1/4 second
                continue
            bytes = len(data)
            if bytes < 5: continue
            try:
                thread.start_new_thread(self.parse_incoming_dom,(str(data),))
                #data has been passed... unlink from the variable references
                #so data in passed objects doesn't change (python passes by reference)
                del data
                data = None
            except Exception, e:
                logger.general(traceback.format_exc())
                if xml_dom: xml_dom.unlink()
        if xml_dom: xml_dom.unlink()
        logger.note("message handler thread exiting...")
        self.inbox_event.set()

    def parse_incoming_dom(self, data):
        xml_dom = None
        try:
            xml_dom = component.get("xml").parseXml(data)
            xml_dom = xml_dom._get_documentElement()
            self.message_action(xml_dom, data)

        except Exception, e:
            logger.general("Error in parse of inbound message. Ignoring message.")
            logger.general("\tOffending data(" + str(len(data)) + "bytes)=" + data)
            logger.general("Exception=" + traceback.format_exc())
        if xml_dom: xml_dom.unlink()

    def message_action(self, xml_dom, data):
        tag_name = xml_dom._get_tagName()
        if self.msg_handlers.has_key(tag_name):
            self.msg_handlers[tag_name](xml_dom, data)
        else:
            logger.general("Unknown Message Type")
            logger.general(data)
        #Message Action thread expires and closes here.
        return

    def sendThread( self, arg ):
        "Sending thread.  This thread reads from the data queue and writes to the socket."
        # Wait to be told it's okay to start running
        self.startedEvent.wait()

        # Loop as long as we have a connection
        while( self.get_status() == 'connected' ):
            try: readMsg = self.outbox.get( block=1 )
            except Exception, text:
                logger.exception("Exception:  messenger->sendThread():  " + str(text)
            # If we are here, it's because we have data to send, no doubt!
            if self.status == 'connected':
                try:
                    # Send the entire message, properly formated/encoded
                    sent = self.sendMsg( self.sock, readMsg )
                except: logger.exception("Exception:  messenger->sendThread():\n" + traceback.format_exc()
            else:
                # If we are not connected, purge the data queue
                logger.note("Data queued without a connection, purging data from queue...")
        self.sendThreadExitEvent.set()
        logger.note( "sendThread has terminated...")

    def sendMsg( self, sock, msg ):
        """Very simple function that will properly encode and send a message to te
        remote on the specified socket."""
        length = len( msg )
        lp = pack( 'i', socket.htonl( length ) )

        try:
            # Send the encoded length
            sentl = sock.send( lp )
            # Now, send the message the the length was describing
            sentm = sock.send( msg )
            if self.isServer: logger.debug("('data_sent', " + str(sentl+sentm) + ")")
            return sentm
        except socket.error, e:
            logger.exception("Socket Error: messenger->sendMsg(): " +  traceback.format_exc())
        except:
            logger.exception("Exception:  messenger->sendMsg(): " +  traceback.format_exc())

    def recvThread( self, arg ):
        "Receiving thread.  This thread reads from the socket and writes to the data queue."

        # Wait to be told it's okay to start running
        self.startedEvent.wait()
        while( self.get_status() == 'connected' ):
            readMsg = self.recvMsg( self.sock )

            # Make sure we didn't get disconnected
            bytes = len( readMsg )
            if bytes == 0: break
            # Check the length of the message
            bytes = len( readMsg )
            # Make sure we are still connected
            if bytes == 0: break
            else:
                # Pass along the message so it can be processed
                self.inbox.put( readMsg )
                self.update_idle_time() #update the last message time
        if bytes == 0:
            logger.note("Remote has disconnected!")
            self.set_status(2)
        self.outbox.put( "" )    # Make sure the other thread is woken up!
        self.sendThreadExitEvent.set()
        logger.note("messenger->recvThread() has terminated...")

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
            logger.exception("Socket Error: messenger->recvData(): " +  str(e))
            data = ""
        return data

    def recvMsg( self, sock ):
        """This method now expects to receive a message having a 4-byte prefix length.  It will ONLY read
        completed messages.  In the event that the remote's connection is terminated, it will throw an
        exception which should allow for the caller to more gracefully handles this exception event.

        Because we use strictly reading ONLY based on the length that is told to use, we no longer have to
        worry about partially adjusting for fragmented buffers starting somewhere within a buffer that we've
        read.  Rather, it will get ONLY a whole message and nothing more.  Everything else will remain buffered
        with the OS until we attempt to read the next complete message."""

        msgData = ""
        try:
            lenData = self.recvData( sock, self.lensize )
            # Now, convert to a usable form
            (length,) = unpack( 'i', lenData )
            length = socket.ntohl( length )
            # Read exactly the remaining amount of data
            msgData = self.recvData( sock, length )
            if self.isServer: logger.debug("('data_recv', " + str(length+4) + ")")
        except: logger.exception("Exception: messenger->recvMsg():\n" + traceback.format_exc())
        return msgData

if __name__ == "__main__":
    test = messenger(None)
    print test.build_message('hello', "This is a test message", attrib1="hello world", attrib2="hello world2", attrib3="hello world3")

