#!/usr/bin/env python
import os
import string
import sys
import time
import gc
import getopt
import traceback


# Simple usuage text for request via help or command line errors
def usage( retValue ):
    print "\nUsage: \n[-d --directory directory] - Directory of where to load config files\n" + \
    "[-n Server Name]\n" + \
    "[-p]\n" + \
    "[-l Lobby Boot Password]\n" + \
    "[-r Run From???]\n" + \
    "[-h --help]\n\n" + \
    "[-m --manual]\n\n" +\
    "Where -p is used to request meta registration.  If -p is given, the boot\n" + \
    "password and server name MUST be provided.  If no options are given, user\n" + \
    "will be prompted for information.\n\n"
    sys.exit( retValue )


import orpg.networking.mplay_server
import orpg.networking.meta_server_lib

print __name__
if __name__ == '__main__' or __name__ == 'start_server':
    gc.set_debug(gc.DEBUG_UNCOLLECTABLE)
    gc.enable()

    orpg_server = orpg.networking.mplay_server.mplay_server()
    lobby_boot_pwd = orpg_server.boot_pwd
    server_directory = orpg_server.userPath
    server_reg = orpg_server.be_registered
    server_name = orpg_server.serverName
    manualStart = False

    # See if we have command line arguments in need of processing
    try:
        (opts, args) = getopt.getopt( sys.argv[1:], "n:phml:m:d:", ["help","manual","directory="] )
        for o, a in opts:
            if o in ("-d", "--directory"):
                if (a[(len(a)-1):len(a)] != os.sep):
                    a = a + os.sep
                    if not (os.access(a, os.W_OK) and os.path.isdir(a)):
                        print "*** ERROR *** Directory '" + a + "' Either doesn't exist, or you don't have permission to write to it."
                        sys.exit(1)
                server_directory = a
            # Server Name
            if o in ( "-n", ):
                server_name = a
            # Post server to meta
            if o in ( "-p", ):
                server_reg = 'Y'
            # Lobby Password
            if o in ( "-l", ):
                lobby_boot_pwd = a
            # Help
            if o in ( "-h", "--help" ):
                usage( 0 )
            #Dont Auto Init Server
            if o in ("-m", "--manual"):
                manualStart = True
    except:
        print
        usage( 1 )


    # start server!
    orpg_server.serverName = server_name
    orpg_server.be_registered = server_reg
    orpg_server.boot_pwd = lobby_boot_pwd
    orpg_server.userPath = server_directory
    orpg_server.remoteadmin = 1

    if not manualStart:
        orpg_server.initServer()

    print "-----------------------------------------------------"
    print "Type 'help' or '?' or 'h' for server console commands"
    print "-----------------------------------------------------"

    opt = "None"
    orpg_server.console_log()
    try:
        while (opt != "kill") and ( opt != "quit"):
            opt = raw_input("action?:")
            words = opt.split()
            if opt == "initserver":
                userpath = raw_input("Please enter the directory you wish to load files from [myfile]:")
                orpg_server.initServer(userPath=userpath)
            elif opt == "broadcast":
                msg = raw_input("Message:")
                orpg_server.broadcast(msg)
            elif opt == "dump":
                orpg_server.player_dump()
            elif opt == "dump groups":
                orpg_server.groups_list()
            elif opt == "get lobby boot password":
                print "Lobby boot password is:  " + orpg_server.groups['0'].boot_pwd
                print
            elif opt == "register":
                msg = raw_input("Enter server name:  ")
                orpg_server.register(msg)
            elif opt == "unregister":
                orpg_server.unregister()
            elif opt == "set lobby boot password":
                lobby_boot_pwd = raw_input("Enter boot password for the Lobby:  ")
                orpg_server.groups['0'].boot_pwd = lobby_boot_pwd
            elif len(words) == 2 and words[0] == "group":
                orpg_server.group_dump(words[1])
            elif opt == "help" or opt == "?" or opt == "h":
                orpg_server.print_help()
            elif opt == "search":
                msg = raw_input("Pattern:")
                orpg_server.search(msg)
            elif opt == "remove room":
                print "Removing a room will kick everyone in that room off your server."
                print "You might consider going to that room and letting them know what you are about to do."
                groupnumber = raw_input("Room group number:")
                orpg_server.remove_room(groupnumber)
            elif opt == "remotekill":
                if orpg_server.toggleRemoteKill():
                    print "Remote Kill has been allowed!"
                else:
                    print "Remote Kill has been disallowed"
            elif opt == "uptime":
                orpg_server.uptime()
            elif opt == "roompasswords":
                print orpg_server.RoomPasswords()
            elif opt == "list":
                orpg_server.player_list()
            elif opt == "log":
                orpg_server.console_log()
            elif opt == "log meta":
                orpg_server.toggleMetaLogging()
            elif len(words) > 0 and words[0] == "logfile":
                if len(words) > 1:
                    if words[1] == "off":
                        orpg_server.NetworkLogging(0)
                    elif words[1] == "on":
                        orpg_server.NetworkLogging(1)
                    elif words[1] == "split":
                        orpg_server.NetworkLogging(2)
                    else:
                        print "<command useage> logfile [off|on|split]"
                else:
                    print orpg_server.NetworkLoggingStatus()
            elif (len(words) > 0 and words[0]) == "monitor":
                if len(words) >1:
                    print "Attempting to monitor client \""+str(words[1])+"\""
                    orpg_server.monitor(words[1])
                else: print "<command useage> monitor (player id #)"
            elif opt == "purge clients":
                try:
                    orpg_server.kick_all_clients()
                except Exception, e:
                    traceback.print_exc()
            elif len(words)>0 and words[0] == "zombie":
                if len(words) > 1:
                    if words[1] == "set":
                        if len(words) > 2:
                            try:
                                t = int(words[2])
                                orpg_server.zombie_time = t
                                print ("--> Zombie auto-kick time set to "+str(t)+" minutes");
                            except Exception, e:
                                print "Invalid zombie time!"
                                traceback.print_exc()
                        else:
                            orpg_server.zombie_time = 480
                            print "--> Zombie auto-kick time set to default (480 mins)";
                    else:
                        print "<command useage> zombie [set [mins]]"
                else:
                    timeout = int(orpg_server.zombie_time)
                    print ("--> Zombie auto-kick time set to "+str(timeout)+" minutes.  Use \"zombie set [min]\" to change.");
            elif opt == "kick":
                kick_id = raw_input("Kick Player #  ")
                kick_msg = raw_input("Reason(optional):  ")
                orpg_server.admin_kick(kick_id,kick_msg)
            elif opt == "ban":
                ban_id = raw_input("Ban Player #  ")
                ban_msg = raw_input("Reason(optional):  ")
                orpg_server.admin_ban(ban_id, ban_msg)
            elif opt == "sendsize":
                send_len = raw_input("Send Size #  ")
                orpg_server.admin_setSendSize(send_len)
            elif opt == "remoteadmin":
                if orpg_server.toggleRemoteAdmin():
                    print "Remote Admin has been allowed!"
                else:
                    print "Remote Admin has been disallowed"
            elif opt == "togglelobbysound":
                if orpg_server.admin_toggleSound():
                    print "Sending a lobby sound has been enabled!"
                    print 'Playing: ' + orpg_server.lobbySound
                else:
                    print "Sending a lobby sound has been disabled"
            elif opt == "lobbysound":
                soundfile = raw_input("Sound File URL: ")
                orpg_server.admin_soundFile(soundfile)
            else:
                if (opt == "kill") or (opt == "quit"):
                    orpg_server.saveBanList()
                    print ("Closing down OpenRPG server. Please wait...")
                else:
                    print ("[UNKNOWN COMMAND: \""+opt+"\" ]")

    except Exception, e:
        print "EXCEPTION: "+str(e)
        traceback.print_exc()
        raw_input("press <enter> key to terminate program")

    orpg_server.kill_server()
