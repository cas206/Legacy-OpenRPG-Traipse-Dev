#!/usr/bin/python2.1
# Copyright (C) 2000-2001 The OpenRPG Project
#
# openrpg-dev@lists.sourceforge.net
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
# File: meta_server_lib.py
# Author: Chris Davis
# Maintainer:
# Version:
#   $Id: meta_server_lib.py,v 1.40 2007/04/04 01:18:42 digitalxero Exp $
#
# Description: A collection of functions to communicate with the meta server.
#


#added debug flag for meta messages to cut console server spam --Snowdog
META_DEBUG = 0

__version__ = "$Id: meta_server_lib.py,v 1.40 2007/04/04 01:18:42 digitalxero Exp $"

from orpg.orpg_version import PROTOCOL_VERSION
from orpg.orpgCore import component
from orpg.tools.validate import validate
from orpg.dirpath import dir_struct
import urllib
import orpg.minidom
from threading import *
import time
import sys
import random
import traceback
import re

metacache_lock = RLock()

def get_server_dom(data=None,path=None):
    # post data at server and get the resulting DOM

    if path == None:
        # get meta server URI
        path = getMetaServerBaseURL()

    # POST the data
    if META_DEBUG:
        print
        print "Sending the following POST info to Meta at " + path + ":"
        print "=========================================="
        print data
        print
    file = urllib.urlopen(path, data)
    data = file.read()
    file.close()

    # Remove any leading or trailing data.  This can happen on some satellite connections
    p = re.compile('(<servers>.*?</servers>)',re.DOTALL|re.IGNORECASE)
    mo = p.search(data)
    if mo: data = mo.group(0)

    if META_DEBUG:
        print
        print "Got this string from the Meta at " + path + ":"
        print "==============================================="
        print data
        print
    # build dom
    xml = component.get('xml')
    xml_dom = xml.parseXml(data)
    xml_dom = xml_dom._get_documentElement()
    return xml_dom

def post_server_data( name, realHostName=None):
    if realHostName:
        data = urllib.urlencode( {"server_data[name]":name,
                                  "server_data[version]":PROTOCOL_VERSION,
                                  "act":"new",
                                  "REMOTE_ADDR": realHostName } )

    else:
        #print "Letting meta server decide the hostname to list..."
        data = urllib.urlencode( {"server_data[name]":name,
                                  "server_data[version]":PROTOCOL_VERSION,
                                  "act":"new"} )

    #xml_dom = get_server_dom( data , "http://openrpg.sf.net/openrpg_servers.php")#Sourceforge still?
    path = component.get('settings').get_setting('MetaServerBaseURL') #getMetaServerBaseURL()
    xml_dom = get_server_dom(data, path)
    ret_val = int( xml_dom.getAttribute( "id" ) )
    return ret_val

def post_failed_connection(id,meta=None,address=None,port=None):
    #  For now, turning this off.  This needs to be re-vamped for
    #  handling multiple Metas.
    return 0
    #data = urllib.urlencode({"id":id,"act":"failed"});
    #xml_dom = get_server_dom(data)
    #ret_val = int(xml_dom.getAttribute("return"))
    #return ret_val

def remove_server(id):
    data = urllib.urlencode({"id":id,"act":"del"});
    xml_dom = get_server_dom(data)
    ret_val = int(xml_dom.getAttribute("return"))
    return ret_val


def byStartAttribute(first,second):
    #  This function is used to easily sort a list of nodes
    #  by their start time

    if first.hasAttribute("start"): first_start = int(first.getAttribute("start"))
    else: first_start = 0

    if second.hasAttribute("start"): second_start = int(second.getAttribute("start"))
    else: second_start = 0

    # Return the result of the cmp function on the two strings
    return cmp(first_start,second_start)

def byNameAttribute(first,second):
    #  This function is used to easily sort a list of nodes
    #  by their name attribute

    # Ensure there is something to sort with for each

    if first.hasAttribute("name"): first_name = str(first.getAttribute("name")).lower()
    else: first_name = ""

    if second.hasAttribute("name"): second_name = str(second.getAttribute("name")).lower()
    else: second_name = ""

    # Return the result of the cmp function on the two strings
    return cmp(first_name,second_name)


def get_server_list(versions = None,sort_by="start"):
    data = urllib.urlencode({"version":PROTOCOL_VERSION,"ports":"%"})
    all_metas = getMetaServers(versions,1)  # get the list of metas
    base_meta = getMetaServerBaseURL()

    #all_metas.reverse()  # The last one checked will take precedence, so reverse the order
                        #  so that the top one on the actual list is checked last

    return_hash = {}  # this will end up with an amalgamated list of servers

    for meta in all_metas:                  # check all of the metas

        #get the server's xml from the current meta
        bad_meta = 0
        #print "Getting server list from " + meta + "..."
        try: xml_dom = get_server_dom(data=data,path=meta)
        except:
            #print "Trouble getting servers from " + meta + "..."
            bad_meta = 1

        if bad_meta:
            continue

        if base_meta == meta:
            #print "This is our base meta: " + meta
            updateMetaCache(xml_dom)

        node_list = xml_dom.getElementsByTagName('server')

        if len(node_list):                  # if there are entries in the node list
                                            #  otherwise, just loop to next meta

            #  for each node found, we're going to check the nodes from prior
            #  metas in the list.  If a match is found, then use the new values.
            for n in node_list:

                # set them from current node

                if not n.hasAttribute('name'): n.setAttribute('name','NO_NAME_GIVEN')
                name = n.getAttribute('name')
                if not n.hasAttribute('num_users'): n.setAttribute('num_users','N/A')
                num_users = n.getAttribute('num_users')
                if not n.hasAttribute('address'): n.setAttribute('address','NO_ADDRESS_GIVEN')
                address = n.getAttribute('address')
                if not n.hasAttribute('port'): n.setAttribute('port','6774')
                port = n.getAttribute('port')
                n.setAttribute('meta',meta)
                end_point = str(address) + ":" + str(port)
                if return_hash.has_key(end_point):
                    if META_DEBUG: print "Replacing duplicate server entry at " + end_point
                return_hash[end_point] = n

    #  At this point, we have an amalgamated list of servers
    #  Now, we have to construct a new DOM to pass back.

    #  Create a servers element
    return_dom = orpg.minidom.Element("servers")

    #  get the nodes stored in return_hash
    return_list = return_hash.values()

    #  sort them by their name attribute.  Uses byNameAttribute()
    #  defined above as a comparison function

    if sort_by == "start": return_list.sort(byStartAttribute)
    elif sort_by == "name": return_list.sort(byNameAttribute)

    #  Add each node to the DOM
    for n in return_list: return_dom.appendChild(n)
    return return_dom

## List Format:
## <servers>
## <server address=? id=? name=? failed_count=? >
## </servers>

def updateMetaCache(xml_dom):
    try:
        if META_DEBUG: print "Updating Meta Server Cache"
        metaservers = xml_dom.getElementsByTagName( 'metaservers' )   # pull out the metaservers bit
        if len(metaservers) == 0:
            cmetalist = getRawMetaList()
            xml_dom = get_server_dom(cmetalist[0])
            metaservers = xml_dom.getElementsByTagName( 'metaservers' )
        authoritative = metaservers[0].getAttribute('auth')
        if META_DEBUG: print "  Authoritive Meta: "+str(authoritative)
        metas = metaservers[0].getElementsByTagName("meta")                # get the list of metas
        if META_DEBUG: print "  Meta List ("+str(len(metas))+" servers)"
        try:
            metacache_lock.acquire()
            ini = open(dir_struct["user"]+"metaservers.cache","w")
            for meta in metas:
                if META_DEBUG: print "   Writing: "+str(meta.getAttribute('path'))
                ini.write(str(meta.getAttribute('path')) + " " + str(meta.getAttribute('versions')) + "\n")
            ini.close()
        finally:
            metacache_lock.release()
    except Exception, e:
        if META_DEBUG: traceback.print_exc()
        print "Meta Server Lib: UpdateMetaCache(): " + str(e)

def getRawMetaList():
    try:
        try:
            metacache_lock.acquire()
            #  Read in the metas
            validate.config_file("metaservers.cache","metaservers.cache")
            ini = open(dir_struct["user"]+"metaservers.cache","r")
            metas = ini.readlines()
            ini.close()
            return metas
        finally:
            metacache_lock.release()
    except Exception, e:
        if META_DEBUG: traceback.print_exc()
        print "Meta Server Lib: getRawMetaList(): " + str(e)
        return []

def getMetaServers(versions = None, pick_random=0):
    """
     get meta server URLs as a list

      versions is a list of acceptable version numbers.
        A False truth value will use getMetaServerBaseURL()

     set a default if we have weird reading problems
     default_url = "http://www.openrpg.com/openrpg_servers.php"
    """

    meta_names = []

    if(versions):  #  If versions are supplied, then look in metaservers.conf
        try:
            """
              read in the metas from file
              format of file is one meta entry per line
              each entry will be the meta url, followed by one or more version numbers that it
              handle.  Generally, this will be either a 1 for the original Meta format, or
              2 for the new one.
            """

            #  Read in the metas
            metas = getRawMetaList()
            #print str(metas)

            # go through each one to check if it should be returned, based on the
            #   version numbers allowed.
            for meta in metas:

                # split the line on whitespace
                #   obviously, your meta servers urls shouldn't contain whitespace.  duh.
                words = meta.split()
                success = 0         #  init success flag for version check
                for version in versions:    # run through each allowed version from caller
                    if version in words[1:]:  #  if the allowed version token was found
                        success += 1          #  then increment the success indicator
                if success:          #  if the meta entry is acceptable to the caller
                    meta_names.append(words[0])    #  add the entry
                    if META_DEBUG: print "adding metaserver " + meta

            #  at this point, we should have at least one name from the cache.  If not ...
            if not meta_names:
                default_meta = getMetaServerBaseURL()       # grab the meta from ini.xml
                meta_names.append(default_meta)             # add it to the return list
            # print "Warning!!\nNo valid metaservers cached."
            # print "Using meta from MetaServerBaseURL: " + default_meta + "\n"
            # if we have more than one and want a random one
            elif pick_random:
                if META_DEBUG: print "choosing random meta from: " + str(meta_names)
                i = int(random.uniform(0,len(meta_names)))
                #meta = meta_names[i]
                meta_names = [meta_names[i]]
                if META_DEBUG: print "using: " + str(meta_names)
            else:
                if META_DEBUG: print "using all metas: " + str(meta_names)
            return meta_names
        except Exception,e:
            print e
            #print "using default meta server URI: " + default_url
            metas = []
            #metas.append(default_url)
            return metas   # return an empty list
    else:        #  otherwise, use MetaServerBaseURL()
        url = getMetaServerBaseURL()
        meta_names.append(url)
        return meta_names

def getMetaServerBaseURL():
    # get meta server URL
    url = "http://www.openrpg.com/openrpg_servers.php"
    try:
        component.get('validate').config_file("settings.xml","default_settings.xml")
        ini = open(dir_struct["user"]+"settings.xml","r")
        txt = ini.read()
        xml = component.get('xml')
        tree = xml.parseXml(txt)._get_documentElement()
        ini.close()
        node_list = tree.getElementsByTagName("MetaServerBaseURL")
        if node_list:
            url = node_list[0].getAttribute("value")

        # allow tree to be collected
        try: tree.unlink()
        except: pass

    except Exception,e:
        print e
    #print "using meta server URI: " + url
    return url

"""
  Beginning of Class registerThread

  A Class to Manage Registration with the Meta2
  Create an instance and call it's start() method
  if you want to be (and stay) registered.  This class
  will take care of registering and re-registering as
  often as necessary to stay in the Meta list.

  You may call register() yourself if you wish to change your
  server's name.  It will immediately update the Meta.  There
  is no need to unregister first.

  Call unregister() when you no longer want to be registered.
  This will result in the registerThread dying after
  attempting to immediately remove itself from the Meta.

  If you need to become registered again after that, you
  must create a new instance of class registerThread.  Don't
  just try to call register() on the old, dead thread class.
"""

class registerThread(Thread):
    """
      Originally, I wrote this as a sub-class of wxThread, but
           A)  I couldn't get it to import right
           B)  I realized that I want this to be used in a server,
               which I don't want needing wxWindows to run!
    
       Because of this fact, there are some methods from wxThread
       that I implemented to minimize changes to the code I had
       just written, i.e. TestDeleteStatus() and Delete()
    """

    def __init__(self,name=None,realHostName=None,num_users = "Hmmm",MetaPath=None,port=6774,register_callback=None):

        Thread.__init__(self,name="registerThread")
        self.rlock = RLock()                    #  Re-entrant lock used to make this class thread safe
        self.die_event = Event()                #  The main loop in run() will wait with timeout on this
        if name:
            self.name = name                        #  Name that the server want's displayed on the Meta
        else:
            self.name = "Unnamed server"             #  But use this if for some crazy reason no name is
                                                    #  passed to the constructor
        self.num_users = num_users               #  the number of users currently on this server
        self.realHostName = realHostName        #  Name to advertise for connection
        self.id = "0"                           #  id returned from Meta.  Defaults to "0", which
                                                #  indicates a new registration.
        self.cookie = "0"                       #  cookie returned from Meta.  Defaults to "0",which
                                                #  indicates a new registration.
        self.interval = 0                       #  interval returned from Meta.  Is how often to
                                                #  re-register, in minutes.
        self.destroy = 0                        #  Used to flag that this thread should die
        self.port = str(port)
        self.register_callback = register_callback  # set a method to call to report result of register
        """
          This thread will communicate with one and only one
          Meta.  If the Meta in ini.xml is changed after
          instantiation, then this instance must be
          unregistered and a new instance instantiated.
        
          Also, if MetaPath is specified, then use that.  Makes
          it easier to have multiple registerThreads going to keep the server registered
          on multiple (compatible) Metas.
        """

        if MetaPath == None:
            self.path = getMetaServerBaseURL()  #  Do this if no Meta specified
        else:
            self.path = MetaPath

    def getIdAndCookie(self):
        return self.id, self.cookie

    def TestDeleteStatus(self):
        try:
            self.rlock.acquire()
            return self.die_event.isSet()
        finally:
            self.rlock.release()

    def Delete(self):
        try:
            self.rlock.acquire()
            self.die_event.set()
        finally:
            self.rlock.release()

    def run(self):
        """
          This method gets called by Thread implementation
          when self.start() is called to begin the thread's
          execution
        
          We will basically enter a loop that continually
          re-registers this server and sleeps Interval
          minutes until the thread is ordered to die in place
        """
        while(not self.TestDeleteStatus()):         # Loop while until told to die
            #  Otherwise, call thread safe register().
            self.register(self.name, self.realHostName, self.num_users)
            if META_DEBUG: print "Sent Registration Data"
            #  register() will end up setting the state variables
            #  for us, including self.interval.
            try:
                self.rlock.acquire()            #  Serialize access to this state information

                if self.interval >= 3:          #  If the number of minutes is one or greater
                    self.interval -= 1          #  wake up with 30 seconds left to re-register
                else:
                    self.interval = .5           #  Otherwise, we probably experienced some kind
                                                #  of error from the Meta in register().  Sleep
                                                #  for 6 seconds and start from scratch.

            finally:                            # no matter what, release the lock
                self.rlock.release()
            #  Wait interval minutes for a command to die
            die_signal = self.die_event.wait(self.interval*60)

        #  If we get past the while loop, it's because we've been asked to die,
        #  so just let run() end.  Once this occurs, the thread is dead and
        #  calls to Thread.isAlive() return False.

    def unregister(self):
        """
          This method can (I hope) be called from both within the thread
          and from other threads.  It will attempt to unregister this
          server from the Meta database
          When this is either accomplished or has been tried hard enough
          (after which it just makes sense to let the Meta remove the
          entry itself when we don't re-register using this id),
          this method will either cause the thread to immediately die
          (if called from this thread's context) or set the Destroy flag
          (if called from the main thread), a positive test for which will cause
          the code in Entry() to exit() when the thread wakes up and
          checks TestDeleteStatus().
          lock the critical section.  The unlock will
          automatically occur at the end of the function in the finally clause
        """
        try:
            self.rlock.acquire()
            if not self.isAlive():      #  check to see if this thread is dead
                return 1                #  If so, return an error result
            #  Do the actual unregistering here
            data = urllib.urlencode( {"server_data[id]":self.id,
                                        "server_data[cookie]":self.cookie,
                                        "server_data[version]":PROTOCOL_VERSION,
                                        "act":"unregister"} )
            try:
                xml_dom = get_server_dom(data=data, path=self.path)  #  this POSTS the request and returns the result
                if xml_dom.hasAttribute("errmsg"):
                    print "Error durring unregistration:  " + xml_dom.getAttribute("errmsg")
            except:
                if META_DEBUG: print "Problem talking to Meta.  Will go ahead and die, letting Meta remove us."
            #  If there's an error, echo it to the console

            #  No special handling is required.  If the de-registration worked we're done.  If
            #  not, then it's because we've already been removed or have a bad cookie.  Either
            #  way, we can't do anything else, so die.
            self.Delete()            #  This will cause the registerThread to die in register()
            #  prep xml_dom for garbage collection
            try: xml_dom.unlink()
            except: pass
            return 0
        finally: self.rlock.release()

    def register(self, name=None, realHostName=None, num_users=None):
        """
          Designed to handle the registration, both new and
          repeated.
        
          It is intended to be called once every interval
            (or interval - delta) minutes.

          lock the critical section.  The unlock will
          automatically occur at the end of the function in the finally clause
        """
        try:
            self.rlock.acquire()
            if not self.isAlive():      #  check to see if this thread is dead
                return 1                #  If so, return an error result

            #  Set the server's attibutes, if specified.
            if name: self.name = name
            if num_users != None: self.num_users = num_users
            if realHostName: self.realHostName = realHostName
            # build POST data
            if self.realHostName:
                data = urllib.urlencode( {"server_data[id]":self.id,
                                        "server_data[cookie]":self.cookie,
                                        "server_data[name]":self.name,
                                        "server_data[port]":self.port,
                                        "server_data[version]":PROTOCOL_VERSION,
                                        "server_data[num_users]":self.num_users,
                                        "act":"register",
                                        "server_data[address]": self.realHostName } )
            else:
                if META_DEBUG:  print "Letting meta server decide the hostname to list..."
                data = urllib.urlencode( {"server_data[id]":self.id,
                                        "server_data[cookie]":self.cookie,
                                        "server_data[name]":self.name,
                                        "server_data[port]":self.port,
                                        "server_data[version]":PROTOCOL_VERSION,
                                        "server_data[num_users]":self.num_users,
                                        "act":"register"} )
            try:
                xml_dom = get_server_dom(data=data,path=self.path)  #  this POSTS the request and returns the result
            except:
                if META_DEBUG: print "Problem talking to server.  Setting interval for retry ..."
                if META_DEBUG: print data
                if META_DEBUG: print
                self.interval = 0
                """
                  If we are in the registerThread thread, then setting interval to 0
                  will end up causing a retry in about 6 seconds (see self.run())
                  If we are in the main thread, then setting interval to 0 will do one
                  of two things:
                  1)  Do the same as if we were in the registerThread
                  2)  Cause the next, normally scheduled register() call to use the values
                      provided in this call.
                
                  Which case occurs depends on where the registerThread thread is when
                  the main thread calls register().
                """
                return 0  # indicates that it was okay to call, not that no errors occurred

            #  If there is a DOM returned ....
            if xml_dom:
                #  If there's an error, echo it to the console
                if xml_dom.hasAttribute("errmsg"):
                    print "Error durring registration:  " + xml_dom.getAttribute("errmsg")
                    if META_DEBUG: print data
                    if META_DEBUG: print
                """
                  No special handling is required.  If the registration worked, id, cookie, and interval
                  can be stored and used for the next time.
                  If an error occurred, then the Meta will delete us and we need to re-register as
                  a new server.  The way to indicate this is with a "0" id and "0" cookie sent to
                  the server during the next registration.  Since that's what the server returns to
                  us on an error anyway, we just store them and the next registration will
                  automatically be set up as a new one.
                
                  Unless the server calls register() itself in the meantime.  Of course, that's okay
                  too, because a success on THAT register() call will set up the next one to use
                  the issued id and cookie.
                
                  The interval is stored unconditionally for similar reasons.  If there's an error,
                  the interval will be less than 1, and the main thread's while loop will reset it
                  to 6 seconds for the next retry.
                  Is it wrong to have a method where there's more comments than code?  :)
                """
                try:
                    self.interval = int(xml_dom.getAttribute("interval"))
                    self.id = xml_dom.getAttribute("id")
                    self.cookie = xml_dom.getAttribute("cookie")
                    if not xml_dom.hasAttribute("errmsg"):
                        updateMetaCache(xml_dom)
                except:
                    if META_DEBUG: print
                    if META_DEBUG: print "OOPS!  Is the Meta okay?  It should be returning an id, cookie, and interval."
                    if META_DEBUG: print "Check to see what it really returned.\n"
                #  Let xml_dom get garbage collected
                try:
                    xml_dom.unlink()
                except:
                    pass
            else:  #  else if no DOM is returned from get_server_dom()
                print "Error - no DOM constructed from Meta message!"
            return 0  # Let caller know it was okay to call us
        finally:
            self.rlock.release()
    #  End of class registerThread
    ################################################################################
