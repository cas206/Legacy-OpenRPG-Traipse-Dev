#!/usr/bin/env python

# Copyright (C) 2000-2001 The OpenRPG Project
#
#   openrpg-dev@lists.sourceforge.net
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
# File: server_probe.py
# Author: Chris Davis
# Maintainer:
# Version:
#   $Id: server_probe.py,v Traipse 'Ornery-Orc' prof.ebral Exp $
#
# Description: This is a periodic maintenance script for removing
# Unresponsive servers from the meta list.
#

from threading import Event
from orpg.networking import mplay_client
from orpg.networking import meta_server_lib
import time



class server_probe:
    def __init__(self):
        self.evts = { }
        self.evts['on_receive'] = self.on_receive
        self.evts['on_mplay_event'] = self.on_mplay_event
        self.evts['on_group_event'] = self.on_group_event
        self.evts['on_player_event'] = self.on_player_event
        self.evts['on_status_event'] = self.on_status_event
        self.session = mplay_client.mplay_client("Server Probe",self.evts)
        self.removed=0
        self.ok =0
        self.lock = Event()


    def probe_servers(self):
        names = []
        addresses = []
        node_list = None
        try:
            xml_dom = meta_server_lib.get_server_list();
            node_list = xml_dom.getElementsByTagName('server')
            for n in node_list:
                address = n.getAttribute('address')
                name = n.getAttribute( 'name' )
                id = n.getAttribute('id')
                if address not in addresses and name not in names:
                    names.append( name )
                    addresses.append( address )
                    self.probe_server(address,id)
                else:
                    # If we are here, we found a duplicate
                    print "Duplicate entry, \"" + name + "\", is being removed."
                    self.removed = self.removed + 1
                    meta_server_lib.remove_server(id)

        except:
            print "An exception has occured.  Attempting to ignore it..."

        print "\n\nServers probe done "
        if node_list != None:
            print "Total Servers:" + str(len(node_list))
        print "servers removed: " + str(self.removed)
        print "servers ok: " + str(self.ok)


    def probe_server(self,address,id):
        print "trying server: " + address

        if address == "asdfasdf":   # replace with address of server to force from list
            print "Forced removal of server!!!!!!!!!!"
            meta_server_lib.remove_server(id)
        else:
            if self.session.connect(address):
                self.lock.wait( timeout=20 )
                self.session.start_disconnect()
                while self.session.is_connected():
                    time.sleep( 1 )
                    self.session.check_my_status()
                print "server: " + address + " ok\n"
                self.ok = self.ok + 1
                print "disconnected from valid server."
            else:
                print "**********>failed connnection!"
                print "**********>removng server " + address + "\n"
                self.removed = self.removed + 1
                meta_server_lib.remove_server(id)
 ##               meta_server_lib.post_failed_connection( id )

        while self.session.is_connected():
            time.sleep(1)


    def on_receive( self, evt, data ):
        """Not used
        """
        self.lock.set()



    def on_mplay_event( self, evt ):
        """Not used
        """
        self.lock.set()



    def on_group_event( self, evt ):
        """Not used
        """
        self.lock.set()



    def on_player_event( self, evt ):
        """Disconnects from the server if a 'new player' event is generated.
        """
        self.lock.set()

    def on_status_event( self, evt ):
        """Not used
        """
        self.lock.set()




if __name__ == "__main__":
    probe = server_probe()
    probe.probe_servers()
