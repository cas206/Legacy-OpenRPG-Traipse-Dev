# This class implements the basic chat commands available in the chat interface.
#
# Defines:
#   __init__(self,chat)
#   docmd(self,text)
#   on_help(self)
#   on_whisper(self,text)
#


import string
import time
import orpg.orpg_version
import orpg.orpg_windows
import traceback

from orpg.tools.orpg_log import logger
from orpg.tools.decorators import debugging

##--------------------------------------------------------------
## dynamically loading module for extended developer commands
## allows developers to work on new chat commands without
## integrating them directly into the ORPG code allowing
## updating of their code without merging changes
## cmd_ext.py should NOT be included in the CVS or Actual Releases

try:
    import cmd_ext
    print "Importing Developer Extended Command Set"
except:
    pass
##----------------------------------------------------------------

ANTI_LOG_CHAR = '!'

class chat_commands:

    # Initialization subroutine.
    #
    # !self : instance of self
    # !chat : instance of the chat window to write to
    @debugging
    def __init__(self,chat):
        self.post = chat.Post
        self.colorize = chat.colorize
        self.session = chat.session
        #self.send = chat.session.send
        self.settings = chat.settings
        self.chat = chat
        self.cmdlist = {}
        self.shortcmdlist = {}
        self.defaultcmds()
        self.defaultcmdalias()
        # def __init__ - end
        self.previous_whisper = []


        # This subroutine will take a text string and attempt to match to a series
        # of implemented emotions.
        #
        # !self : instance of self
        # !text : string of text matching an implemented emotion
    @debugging
    def addcommand(self, cmd, function, helpmsg):
        if not self.cmdlist.has_key(cmd) and not self.shortcmdlist.has_key(cmd):
            self.cmdlist[cmd] = {}
            self.cmdlist[cmd]['function'] = function
            self.cmdlist[cmd]['help'] = helpmsg
            #print 'Command Added: ' + cmd

    @debugging
    def addshortcmd(self, shortcmd, longcmd):
        if not self.shortcmdlist.has_key(shortcmd) and not self.cmdlist.has_key(shortcmd):
            self.shortcmdlist[shortcmd] = longcmd

    @debugging
    def removecmd(self, cmd):
        if self.cmdlist.has_key(cmd):
            del self.cmdlist[cmd]
        elif self.shortcmdlist.has_key(cmd):
            del self.shortcmdlist[cmd]

        #print 'Command Removed: ' + cmd


    @debugging
    def defaultcmds(self):
        self.addcommand('/help', self.on_help, '- Displays this help message')
        self.addcommand('/version', self.on_version, ' - Displays current version of OpenRPG.')
        self.addcommand('/me', self.chat.emote_message, ' - Alias for **yourname does something.**')
        self.addcommand('/ignore', self.on_ignore, '[player_id,player_id,... | ignored_ip,ignored_ip,... | list] - Toggle ignore for user associated with that player ID. Using the IP will remove only not toggle.')
        self.addcommand('/load', self.on_load, 'filename - Loads settings from another ini file from the myfiles directory.')
        self.addcommand('/role', self.on_role, '[player_id = GM | Player | Lurker] - Get player roles from ther server, self.or change the role of a player.')
        self.addcommand('/font', self.on_font, 'fontname - Sets the font.')
        self.addcommand('/fontsize', self.on_fontsize, 'size - Sets the size of your fonts.  Recomended 8 or better for the size.')
        self.addcommand('/close', self.on_close, 'Close the chat tab')
        self.addcommand('/set', self.on_set, '[setting[=value]] - Displays one or all settings, self.or sets a setting.')
        self.addcommand('/whisper', self.on_whisper, 'player_id_number, ... = message - Whisper to player(s). Can contain multiple IDs.')
        self.addcommand('/gw', self.on_groupwhisper, 'group_name=message - Type /gw help for more information')
        self.addcommand('/gm', self.on_gmwhisper, 'message - Whispers to all GMs in the room')
        self.addcommand('/name', self.on_name, 'name - Change your name.')
        self.addcommand('/time', self.on_time, '- Display the local and GMT time and date.')
        self.addcommand('/status', self.on_status, 'your_status - Set your online status (afk,away,etc..).')
        self.addcommand('/dieroller', self.on_dieroller, '- Set your dieroller or list the available rollers.')
        self.addcommand('/log', self.on_log, '[ on | off | to <em>filename</em> ] - Check log state, additionally turn logging on, self.off, self.or set the log filename prefix.')
        self.addcommand('/update', self.on_update, '[get] - Get the latest version of OpenRPG.')
        self.addcommand('/moderate', self.on_moderate, '[ on | off ][player_id=on|off] - Show who can speak in a moderated room, self.or turn room moderation on or off.')
        self.addcommand('/tab', self.invoke_tab, 'player_id - Creates a tab so you can whisper rolls to youror what ever')
        self.addcommand('/ping', self.on_ping, '- Ask for a response from the server.')
        self.addcommand('/admin', self.on_remote_admin, '- Remote admin commands')
        self.addcommand('/description', self.on_description, 'message - Creates a block of text, used for room descriptions and such')
        self.addcommand('/sound', self.on_sound, 'Sound_URL - Plays a sound for all clients in the room.')
        self.addcommand('/purge', self.on_purge, 'This will clear the entire chat window')
        self.addcommand('/advfilter', self.on_filter, 'This will toggle the Advanced Filter')

    @debugging
    def defaultcmdalias(self):
        self.addshortcmd('/?', '/help')
        self.addshortcmd('/he', '/me')
        self.addshortcmd('/she', '/me')
        self.addshortcmd('/i', '/ignore')
        self.addshortcmd('/w', '/whisper')
        self.addshortcmd('/nick', '/name')
        self.addshortcmd('/date', '/time')
        self.addshortcmd('/desc', '/description')
        self.addshortcmd('/d', '/description')

        #This is just an example or a differant way the shorcmd can be used
        self.addshortcmd('/sleep', '/me falls asleep')

    @debugging
    def docmd(self,text):
        cmdsearch = string.split(text,None,1)
        cmd = string.lower(cmdsearch[0])
        start = len(cmd)
        end = len(text)
        cmdargs = text[start+1:end]

        if self.cmdlist.has_key(cmd):
            self.cmdlist[cmd]['function'](cmdargs)
        elif self.shortcmdlist.has_key(cmd):
            self.docmd(self.shortcmdlist[cmd] + " " + cmdargs)
        else:
            msg = "Sorry I don't know what %s is!" % (cmd)
            self.chat.InfoPost(msg)

    @debugging
    def on_filter(self, cmdargs):
        #print self.chat.advancedFilter
        test = not self.chat.advancedFilter
        #print test

        for tab in self.chat.parent.whisper_tabs:
            tab.advancedFilter = not self.chat.advancedFilter

        for tab in self.chat.parent.null_tabs:
            tab.advancedFilter = not self.chat.advancedFilter

        for tab in self.chat.parent.group_tabs:
            tab.advancedFilter = not self.chat.advancedFilter

        if self.chat.parent.GMChatPanel != None:
            self.chat.parent.GMChatPanel.advancedFilter = not self.chat.advancedFilter

        self.chat.advancedFilter = not self.chat.advancedFilter

        if self.chat.advancedFilter:
            self.chat.InfoPost("Advanced Filtering has been turned On")
        else:
            self.chat.InfoPost("Advanced Filtering has been turned Off")

    @debugging
    def on_purge(self, cmdargs):
        self.chat.PurgeChat()
        self.chat.InfoPost('Chat Buffer has been Purged!')

    @debugging
    def on_sound(self, cmdargs):
        if len(cmdargs) < 8:
            self.chat.InfoPost("You must provide a URL for the file name, it does not work for just local sound files")
            return
        args = string.split(cmdargs, None, -1)

        if args[0] == 'loop':
            snd = args[1].replace('&', '&amp;')
            loop = '1'
        else:
            snd = cmdargs.replace('&', '&amp;')
            loop = ''

        type = 'remote'

        (name, ip, id, text_status, version, protocol_version, client_string, role) = self.session.get_my_info()
        group_id = self.session.group_id
        if (role != 'Lurker' and group_id != '0') or self.session.get_status() != 1:
            try:
                self.chat.sound_player.play(snd, type, loop)
                if type == 'remote':
                    snd_xml = '<sound url="' + snd + '" group_id="' + group_id + '" from="' + id + '" loop="' + str(loop) + '" />'
                    self.session.send_sound(snd_xml)
            except Exception, e:
                print e
                self.chat.InfoPost("Invalid sound file!")
        elif role == 'Lurker':
            self.chat.InfoPost("You must be a player or a GM to send a sound file!")
        elif group_id == '0':
            self.chat.InfoPost("You cannot send sound files to the lobby!")
        else:
            self.chat.InfoPost("Something dun fuckered up Frank!")

    @debugging
    def on_version(self, cmdargs=""):
        self.chat.InfoPost("Version is OpenRPG " + self.chat.version)

    @debugging
    def on_load(self, cmdargs):
        args = string.split(cmdargs,None,-1)
        try:
            self.settings.setup_ini(args[0])
            self.settings.reload_settings(self.chat)
            self.chat.InfoPost("Settings Loaded from file " + args[0] )
        except Exception,e:
            print e
            self.chat.InfoPost("ERROR Loading settings")

    @debugging
    def on_font(self, cmdargs):
        try:
            fontsettings = self.chat.set_default_font(fontname=cmdargs, fontsize=None)
        except:
            self.chat.InfoPost("ERROR setting default font")

    @debugging
    def on_fontsize(self, cmdargs):
        args = string.split(cmdargs,None,-1)
        try:
            fontsettings = self.chat.set_default_font(fontname=None, fontsize=int(args[0]))
        except Exception, e:
            print e
            self.chat.InfoPost("ERROR setting default font size")

    @debugging
    def on_close(self, cmdargs):
        try:
            chatpanel = self.chat
            if (chatpanel.sendtarget == "all"):
                chatpanel.InfoPost("Error:  cannot close public chat tab.")
            else:
                chatpanel.chat_timer.Stop()
                chatpanel.parent.onCloseTab(0)
        except:
            self.chat.InfoPost("Error:  cannot close private chat tab.")

    @debugging
    def on_time(self, cmdargs):
        local_time = time.localtime()
        gmt_time = time.gmtime()
        format_string = "%A %b %d, %Y  %I:%M:%S%p"
        self.chat.InfoPost("<br />Local: " + time.strftime(format_string)+\
                           "<br />GMT: "+time.strftime(format_string,gmt_time))

    @debugging
    def on_dieroller(self, cmdargs):
        args = string.split(cmdargs,None,-1)
        rm = self.chat.DiceManager
        try:
            rm.setRoller(args[0])
            self.chat.SystemPost("You have changed your die roller to the <b>\"" + args[0] + "\"</b> roller.")
            self.settings.set_setting('dieroller',args[0])
        except Exception, e:
            print e
            self.chat.InfoPost("Available die rollers: " + str(rm.listRollers()))
            self.chat.InfoPost("You are using the <b>\"" + rm.getRoller() + "\"</b> die roller.")

    @debugging
    def on_ping(self, cmdargs):
        ct = time.clock()
        msg = "<ping player='"+self.session.id+"' time='"+str(ct)+"' />"
        self.session.outbox.put(msg)

    @debugging
    def on_log(self,cmdargs):
        args = string.split(cmdargs,None,-1)
        logfile = self.settings.get_setting( 'GameLogPrefix' )

        if len( args ) == 0:
            self.postLoggingState()
        elif args[0] == "on" and logfile != '':
            try:
                while logfile[ 0 ] == ANTI_LOG_CHAR:
                    #print logfile
                    logfile = logfile[ 1: ]
            except IndexError,e:
                self.chat.SystemPost("log filename is blank, system will *not* be logging until a valid filename is specified" )
                self.settings.set_setting( 'GameLogPrefix', logfile )
                return
            self.settings.set_setting( 'GameLogPrefix', logfile )
            self.postLoggingState()
        elif args[0] == "off":
            logfile = ANTI_LOG_CHAR+logfile
            self.settings.set_setting( 'GameLogPrefix', logfile )
            self.postLoggingState()
        elif args[0] == "to":
            if len( args ) > 1:
                logfile = args[1]
                self.settings.set_setting( 'GameLogPrefix', logfile )
            else:
                self.chat.SystemPost('You must also specify a filename with the <em>/log to</em> command.' )
            self.postLoggingState()
        else:
            self.chat.InfoPost("Unknown logging command, use 'on' or 'off'"  )

    @debugging
    def postLoggingState( self ):
        logfile = self.settings.get_setting( 'GameLogPrefix' )
        try:
            if logfile[0] != ANTI_LOG_CHAR:
                comment = 'is'
            else:
                comment = 'is not'
        except:
            comment = 'is not'
        suffix = time.strftime( '-%d-%m-%y.html', time.localtime( time.time() ) )
        self.chat.InfoPost('Log filename is "%s%s", system is %s logging.' % (logfile, suffix, comment) )

        # This subroutine will set the players netork status.
        #
        #!self : instance of self

    @debugging
    def on_name(self, cmdargs):
        #only 20 chars no more! :)
        if cmdargs == "":
            self.chat.InfoPost("**Incorrect syntax for name.")
        else:
            #txt = txt[:50]
            self.settings.set_setting('player', cmdargs)
            self.session.set_name(str(cmdargs))

    # def on_status - end

        # This subroutine will set the players netork status.
        #
        # !self : instance of self
    @debugging
    def on_status(self, cmdargs):
        if cmdargs ==  "":
            self.chat.InfoPost("Incorrect synatx for status.")
        else:
        #only 20 chars no more! :)
            txt = cmdargs[:20]
            self.session.set_text_status(str(txt))
    # def on_status - end

    @debugging
    def on_set(self, cmdargs):
        args = string.split(cmdargs,None,-1)
        keys = self.settings.get_setting_keys()
        #print keys
        if len(args) == 0:
            line = "<table border='2'>"
            for m in keys:
                line += "<tr><td>" + str(m) + "</td><td> " + str(self.settings.get_setting(m)) + "</td></tr>"
            line += "</table>"
            self.chat.InfoPost(line)
        else:
            split_name_from_data = cmdargs.find("=")
            if split_name_from_data == -1:
                for m in keys:
                    if m == args[0]:
                        return_string = "<table border='2'><tr><td>" + args[0] + "</td><td>"\
                        + self.settings.get_setting(args[0]) + "</td></tr></table>"
                        self.chat.InfoPost(return_string)
            else:
                name = cmdargs[:split_name_from_data].strip()
                for m in keys:
                    if m == name:
                        setting = cmdargs[split_name_from_data+1:].strip()
                        self.settings.set_setting(name,setting)
                        return_string = name + " changed to " + setting
                        self.chat.InfoPost(return_string)
                        self.session.set_name(self.settings.get_setting("player"))
                        self.chat.set_colors()
                        self.chat.set_buffersize()

        # This subroutine will display the correct usage of the different emotions.
        #
        #!self : instance of self

    @debugging
    def on_help(self, cmdargs=""):
        cmds = self.cmdlist.keys()
        cmds.sort()
        shortcmds = self.shortcmdlist.keys()
        shortcmds.sort()
        msg = '<br /><b>Command Alias List:</b>'
        for shortcmd in shortcmds:
            msg += '<br /><b><font color="#0000CC">%s</font></b> is short for <font color="#000000">%s</font>' % (shortcmd, self.shortcmdlist[shortcmd])
        msg += '<br /><br /><b>Command List:</b>'
        for cmd in cmds:
            msg += '<br /><b><font color="#000000">%s</font></b>' % (cmd)
            for shortcmd in shortcmds:
                if self.shortcmdlist[shortcmd] == cmd:
                    msg += ', <b><font color="#0000CC">%s</font></b>' % (shortcmd)
            msg += ' %s' % (self.cmdlist[cmd]['help'])

        self.chat.InfoPost(msg)

        # This subroutine will either show the list of currently ignored users
        # !self : instance of self
        # !text : string that is comprised of a list of users to toggle the ignore flag

    @debugging
    def on_ignore(self, cmdargs):
        args = string.split(cmdargs,None,-1)
        (ignore_list, ignore_name) = self.session.get_ignore_list()
        ignore_output = self.colorize(self.chat.syscolor,"<br /><u>Player IDs Currently being Ignored:</u><br />")
        if cmdargs == "":
            if len(ignore_list) == 0:
                ignore_output += self.colorize(self.chat.infocolor,"No players are currently being ignored.<br />")
            else:
                for m in ignore_list:
                    ignore_txt = m + " " + ignore_name[ignore_list.index(m)] + "<br />"
                    ignore_output += self.colorize(self.chat.infocolor,ignore_txt)
            self.chat.Post(ignore_output)
        else:
            players = cmdargs.split(",")
            for m in players:
                try:
                    id = `int(m)`
                    (result, id, name) = self.session.toggle_ignore(id)
                    if result == 0:
                        self.chat.InfoPost("Player " + name + " with ID:" + id + " no longer ignored")
                    if result == 1:
                        self.chat.InfoPost("Player " + name + " with ID:" + id + " now being ignored")
                except:
                    self.chat.InfoPost(m + " was ignored because it is an invalid player ID")
                    traceback.print_exc()

    @debugging
    def on_role(self, cmdargs):
        if cmdargs == "":
            self.session.display_roles()
            return
        delim = cmdargs.find("=")
        if delim < 0:
            self.chat.InfoPost("**Incorrect synatax for Role." + str(delim))
            return
        player_ids = string.split(cmdargs[:delim],",")
        role = cmdargs[delim+1:].strip()
        role = role.lower()
        if (role.lower() == "player") or (role.lower() == "gm") or (role.lower() == "lurker"):
            if role.lower() == "player": role = "Player"
            elif role.lower() == "gm":   role = "GM"
            else: role = "Lurker"
            try:
                role_pwd = self.session.orpgFrame_callback.password_manager.GetPassword("admin",int(self.session.group_id))
                if role_pwd != None:
                    for m in player_ids:
                        self.session.set_role(m.strip(),role,role_pwd)
            except:
                traceback.print_exc()
#        return

        # This subroutine implements the whisper functionality that enables a user
        # to whisper to another user.
        #
        # !self : instance of self
        # !text : string that is comprised of a list of users and the message to
        #whisper.

    @debugging
    def on_whisper(self, cmdargs):
        delim = cmdargs.find("=")

        if delim < 0:
            if self.previous_whisper:
                player_ids = self.previous_whisper
            else:
                self.chat.InfoPost("**Incorrect syntax for whisper." + str(delim))
                return
        else:
            player_ids = string.split(cmdargs[:delim], ",")
        self.previous_whisper = player_ids
        mesg = string.strip(cmdargs[delim+1:])
        self.chat.whisper_to_players(mesg,player_ids)

#---------------------------------------------------------
# [START] Digitalxero Multi Whisper Group 1/1/05
#---------------------------------------------------------
    @debugging
    def on_groupwhisper(self, cmdargs):
        args = string.split(cmdargs,None,-1)
        delim = cmdargs.find("=")

        if delim > 0:
            group_ids = string.split(cmdargs[:delim], ",")
        elif args[0] == "add":
            if not orpg.player_list.WG_LIST.has_key(args[2]):
                orpg.player_list.WG_LIST[args[2]] = {}
            orpg.player_list.WG_LIST[args[2]][int(args[1])] = int(args[1])
            return
        elif args[0] == "remove" or args[0] == "delete":
            del orpg.player_list.WG_LIST[args[2]][int(args[1])]
            if len(orpg.player_list.WG_LIST[args[2]]) == 0:
                del orpg.player_list.WG_LIST[args[2]]
            return
        elif args[0] == "create" or args[0] == "new_group":
            if not orpg.player_list.WG_LIST.has_key(args[1]):
                orpg.player_list.WG_LIST[args[1]] = {}
            return
        elif args[0] == "list":
            if orpg.player_list.WG_LIST.has_key(args[1]):
                for n in orpg.player_list.WG_LIST[args[1]]:
                    player = self.session.get_player_info(str(n))
                    self.chat.InfoPost(str(player[0]))
            else:
                self.chat.InfoPost("Invalid Whisper Group Name")
            return
        elif args[0] == "clear":
            if orpg.player_list.WG_LIST.has_key(args[1]):
                orpg.player_list.WG_LIST[args[1]].clear()
            else:
                self.chat.InfoPost("Invalid Whisper Group Name")
            return
        elif args[0] == "clearall":
            orpg.player_list.WG_LIST.clear()
            return
        else:
            self.chat.InfoPost("<b>/gw add</b> (player_id) (group_name) - Adds [player_id] to [group_name]")
            self.chat.InfoPost("<b>/gw remove</b> (player_id) (group_name) - Removes [player_id] from [group_name]")
            self.chat.InfoPost("<b>/gw</b> (group_name)<b>=</b>(message) - Sends [message] to [group_name]")
            self.chat.InfoPost("<b>/gw create</b> (group_name) - Creates a whisper group called [group_name]")
            self.chat.InfoPost("<b>/gw list</b> (group_name) - Lists all players in [group_name]")
            self.chat.InfoPost("<b>/gw clear</b> (group_name) - Removes all players from [group_name]")
            self.chat.InfoPost("<b>/gw clearall</b> - Removes all existing whisper groups")
            return
        msg = string.strip(cmdargs[delim+1:])
        for gid in group_ids:
            idList = ""
            for n in orpg.player_list.WG_LIST[gid]:
                if idList == "":
                    idList = str(n)
                else:
                    idList = str(n) + ", " + idList
            self.on_whisper(idList + "=" + self.settings.get_setting("gwtext") + msg)

#---------------------------------------------------------
# [END] Digitalxero Multi Whisper Group 1/1/05
#---------------------------------------------------------

    @debugging
    def on_gmwhisper(self, cmdargs):
        if cmdargs == "":
            self.chat.InfoPost("**Incorrect syntax for GM Whisper.")
        else:
            the_gms = self.chat.get_gms()
            if len(the_gms):
                gmstring = ""
                for each_gm in the_gms:
                    if gmstring != "":
                        gmstring += ","
                    gmstring += each_gm
                self.on_whisper(gmstring + "=" + cmdargs)
            else:
                self.chat.InfoPost("**No GMs to Whisper to.")

    @debugging
    def on_moderate(self, cmdargs):
        if cmdargs != "":
            pos = cmdargs.find("=")
            if (pos < 0):
                plist = ""
                if cmdargs.lower() == "on":
                    action = "enable"
                elif cmdargs.lower() == "off":
                    action="disable"
                else:
                    self.chat.InfoPost("Wrong syntax for moderate command!")
                    return
            else:
                plist = string.strip(cmdargs[:pos])
                tag = string.strip(cmdargs[pos+1:])
                if tag.lower() == "on":
                    action = "addvoice"
                elif tag.lower() == "off":
                    action = "delvoice"
                else:
                    self.chat.InfoPost("Wrong syntax for moderate command!")
                    return
            pwd = self.session.orpgFrame_callback.password_manager.GetPassword("admin",int(self.session.group_id))
            if pwd != None:
                msg = "<moderate"
                msg += " action = '" + action + "'"
                msg +=" from = '" + self.session.id + "' pwd='" + pwd + "'"
                if (plist != ""):
                    msg += " users='"+plist+"'"
                msg += " />"
                self.session.outbox.put(msg)
            pass
        else:
            msg = "<moderate action='list' from='"+self.session.id+"' />"
            self.session.outbox.put(msg)
        self.session.update()

    @debugging
    def on_update(self, cmdargs):
        self.chat.InfoPost("This command is no longer valid")

    @debugging
    def on_description(self, cmdargs):
        if len(cmdargs) <= 0:
            self.chat.InfoPost("**No description text to display." + str(delim))
            return
        mesg = "<table bgcolor='#c0c0c0' border='3' cellpadding='5' cellspacing='0' width='100%'><tr><td><font color='#000000'>"
        mesg += string.strip(cmdargs)
        mesg += "</font></td></tr></table>"
        self.chat.Post(mesg)
        self.chat.send_chat_message(mesg)

    @debugging
    def invoke_tab(self, cmdargs):
        ######START mDuo13's Tab Initiator########
        try:
            int(cmdargs)
            playerid = cmdargs.strip()
            # Check to see if parent notebook already has a private tab for player
            for panel in self.chat.parent.whisper_tabs:
                if (panel.sendtarget == playerid):
                    self.chat.Post("Cannot invoke tab: Tab already exists.")
                    return
            try:
                displaypanel = self.chat.parent.create_whisper_tab(playerid)
            except:
                self.chat.Post("That ID# is not valid.")
                return
            nidx = self.chat.parent.get_tab_index(displaypanel)
            self.chat.parent.newMsg(nidx)
            return
        except:
            displaypanel = self.chat.parent.create_null_tab(cmdargs)
            nidx = self.chat.parent.get_tab_index(displaypanel)
            self.chat.parent.newMsg(nidx)
            return
        #######END mDuo13's Tab Initiator#########

    @debugging
    def on_remote_admin(self, cmdargs):
        args = string.split(cmdargs,None,-1)
        #handles remote administration commands
        try:
            pass_state = 0
            pwd = self.session.orpgFrame_callback.password_manager.GetSilentPassword("server")
            if  pwd != None:
                pass_state = 1
            else: pwd = "<i>[NONE]</i>"

            if len( args ) == 0:
                #raw command return state info
                msg = "<br /><b>Remote Administrator Config:</b>"
                if pass_state != 1 : msg += " Password not set. Remote admin functions disabled<br />"
                else:
                    msg += " Enabled. Using password \""+pwd+"\"<br />"
                self.chat.SystemPost(msg)
                return

            if pass_state != 1 and args[0] != "set":
                #no commands under this point will execute unless an admin password has been previously set
                self.chat.SystemPost("Command ignored. No remote administrator password set!!")
                return
            msgbase = "<admin id=\""+self.session.id+"\" group_id=\""+self.session.group_id+"\" pwd=\""+pwd+"\" "
            if args[0] == "set":
                if len( args ) > 1:
                    self.session.orpgFrame_callback.password_manager.server = str( args[1] )
                    self.chat.SystemPost( "Remote administration commands using password: \""+str(self.session.orpgFrame_callback.password_manager.GetSilentPassword("server"))+"\"" )
                else:
                    pwd = self.session.orpgFrame_callback.password_manager.GetPassword("server")
                    if pwd != None:
                        self.chat.SystemPost( "Remote administration commands using password: \""+pwd+"\"" )

            elif args[0] == "ban":
                #Ban a player from the server
                msg = msgbase + ' cmd="ban" bid="' + str(args[1]) + '" />'
                self.session.outbox.put(msg)

            elif args[0] == "banip":
                #Ban a player from the server
                try:
                    bname = str(args[2])
                except:
                    bname = 'Unknown'
                msg = msgbase + ' cmd="banip" bip="' + str(args[1]) + '" bname="' + bname + '"/>'
                self.session.outbox.put(msg)

            elif args[0] == "unban":
                #remove a group from the server and drop all players within the group
                msg = msgbase + ' cmd="unban" ip="' + str(args[1]) + '" />'
                self.session.outbox.put(msg)

            elif args[0] == "banlist":
                #remove a group from the server and drop all players within the group
                msg = msgbase + ' cmd="banlist" />'
                self.session.outbox.put(msg)

            elif args[0] == "help":
                #request help from server
                msg = msgbase + " cmd=\"help\" />"
                self.session.outbox.put(msg)

            elif args[0] == "nameroom":
                #reqest room renaming on server
                msg = msgbase + " cmd=\"nameroom\" rmid=\""+ str(args[1])+"\" name=\""+ string.join(args[2:])+"\" />"
                self.session.outbox.put(msg)

            elif args[0] == "roompasswords":
                #reqest room renaming on server
                msg = msgbase + " cmd=\"roompasswords\"/>"
                self.session.outbox.put(msg)

            elif args[0] == "message":
                #send message to a specific player on the server via the system administrator
                msg = msgbase + " cmd=\"message\" to_id=\""+ str(args[1])+"\" msg=\""+ string.join(args[2:])+"\" />"
                self.session.outbox.put(msg)

            elif args[0] == "broadcast":
                #send a message to all players on server from the system administrator
                msg = msgbase + " cmd=\"broadcast\" msg=\""+ string.join(args[1:])+"\" />"
                self.session.outbox.put(msg)

            elif args[0] == "killgroup":
                #remove a group from the server and drop all players within the group
                msg = msgbase + " cmd=\"killgroup\" gid=\""+ str(args[1])+"\" />"
                self.session.outbox.put(msg)

            elif args[0] == "uptime":
                #request uptime report from server
                msg = msgbase + " cmd=\"uptime\" />"
                self.session.outbox.put(msg)

            elif args[0] == "createroom":
                #request creation of a (temporary) persistant room
                if len(args) < 2:
                    self.chat.SystemPost( "You must supply a name and boot password at least. <br />/admin createroom &lt;name&gt; &lt;boot password&gt; [password]" )
                    return
                if len(args) < 3:
                    self.chat.SystemPost( "You must supply a boot password also.<br />/admin createroom &lt;name&gt; &lt;boot password&gt; [password]" )
                    return
                if len(args) < 4: args.append("")
                msg = msgbase + " cmd=\"createroom\" name=\""+str(args[1])+"\" boot=\""+ str(args[2])+"\" pass=\""+ str(args[3])+"\" />"
                self.session.outbox.put(msg)

            elif args[0] == "passwd":
                #request boot password change on a room
                msg = msgbase + " cmd=\"passwd\" gid=\""+str(args[1])+"\" pass=\""+ str(args[2])+"\" />"
                self.session.outbox.put(msg)

            elif args[0] == "list":
                #request a list of rooms and players from server
                msg = msgbase + " cmd=\"list\" />"
                self.session.outbox.put(msg)

            elif args[0] == "killserver":
                #remotely kill the server
                msg = msgbase + " cmd=\"killserver\" />"
                self.session.outbox.put(msg)

            elif args[0] == "savemaps":
                msg = msgbase + ' cmd="savemaps" />'
                self.session.outbox.put(msg)

            else:
                self.chat.InfoPost("Unknown administrator command"  )
        except:
            self.chat.InfoPost("An error has occured while processing a Remote Administrator command!")
            traceback.print_exc()
