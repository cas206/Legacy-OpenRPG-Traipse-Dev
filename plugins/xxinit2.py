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
#
##############################################################################

from string import find, replace
import wx

import os
from orpg.dirpath import dir_struct
import orpg.orpg_version
import orpg.plugindb
import orpg.pluginhandler
import hashlib
import random

__version__ = "2.2.8"

class v:
    init_list = []

class Plugin(orpg.pluginhandler.PluginHandler):
    # Initialization subroutine.
    #
    # !self : instance of self
    # !openrpg : instance of the the base openrpg control
    def __init__(self, plugindb, parent):
        orpg.pluginhandler.PluginHandler.__init__(self, plugindb, parent)

        self.name = "Initiative Tool " + str(__version__)
        self.author = "Woody, Darloth, updated by mDuo13, Veggiesama, magoo"
        self.help =  "Type /inittool2 to load a help node into your game tree. Check out\n"
        self.help += "the readme, and double-click Commands & Help if you want to see examples."

        self.version = __version__
        self.orpg_min_version="1.7.0"


    def plugin_enabled(self):
        # Setup variables.
        self.loaded = 0     #  1 = config has been loaded on startup
        self.init_debug = 0
        v.init_list = [] # now an array of "Dict" (associative array):
                       #   name : name of the effect of character
                       #   type : 0 = character; 1 = effect
                       #   init : init score
                       #   duration : round remaining to the effect
                       #   hidden : type 0 = shows up in public list only on init
                       #            type 1 = does not print to public remaing rounds of effect
                       #   pass : for SR4
                       #   rank : when multiple character at same init count, the plugin
                       #          use the 'rank' to order them
                       #   tag  : unique tag assigned to each entry.
        self.init_round = 1
        self.init_recording = 1
        self.init_title = ""
        self.init_count = 0
        self.init_pass = 0
        self.init_listslot = 0
        self.init_listtag = ""
        self.init_end = 0
        self.init_system = "D20" # D20 (default), SR4, RQ
        self.sandglass_count = 0 # current count of the number of seconds of a character's turn
                            # Well, more or less true, it is a count of the number of time the function
                            # refresh_counter() has been called, which itself is supposed to be call each seconds.
        self.sandglass_delay = 0 # 0 = off, anything else is the timer delay
        self.sandglass_status = 0# 0 = running, 1 = pause
        self.sandglass_skip_interval = 0 # after a number of interval, do a init_next(). 0 = disable
        self.autosave_delay  = 60 # 0 = off, else, will autosave every 'autosave' seconds - VEG 2.2.8 (set to 60)
        self.autosave_count  = 0 # current count of the number of seconds since last autosave
        self.hide_id       = 0 # 1 = do not show IDs to everyone; 0 = show IDs to everyone
        self.hide_ondeck   = 0 # 1 = do not show "on deck" message after every turn; 0 = show it
        self.hide_justmovement = 0 # [SR4] 1 = do not show "just movement" messages
        self.message_nowup = "NEXT UP FOR THE KILLING" # customizable "now up" message
        self.msghand_timer = 0 # 0-60 = cycles the message handler to all players once every 60 seconds - VEG 2.2.6
        self.msghand_warning = 1 # 1 = manual override, removes the message warning if someone else in room has xxinit2 loaded - VEG 2.2.6
        self.reroll_type = 0 # 0 = reroll every round (normal), 1 = no reroll and keep last round inits - VEG 2.2.7
        self.ip_order = 0 # 0 = 1/2/3/4 (normal), 1 = 3/1/4/2 (Serbitar's house rule), 2 = 4/1/3/2 (TinkerGnome's house rule) - VEG 2.2.7

        # Add commands
        self.plugin_addcommand("/inittool2",            self.CMD_inittool2,             "Loads the help/example node into your game tree")
        self.plugin_addcommand("/inittoggle",           self.CMD_inittoggle,            "Toggles initiative system (D20/SR4/RuneQuest")
        self.plugin_addcommand("/initdebug",            self.CMD_initdebug,             "???")
        self.plugin_addcommand("/initgui",              self.CMD_initgui,               "???")
        #self.plugin_addcommand("/initsaveconfig",       self.CMD_initsaveconfig,        "Saves current configuration") #VEG 2.2.6
        #self.plugin_addcommand("/initloadconfig",       self.CMD_initloadconfig,        "Loads a previous configuration") #VEG 2.2.6
        self.plugin_addcommand("/initdefaultconfig",    self.CMD_initdefaultconfig,     "Loads the default configuration")
        self.plugin_addcommand("/initshowconfig",       self.CMD_initshowconfig,        "Displays current configuration")
        self.plugin_addcommand("/togglehideid",         self.CMD_togglehideid,          "Shows IDs in a public list")
        self.plugin_addcommand("/togglehideondeck",     self.CMD_togglehideondeck,          "Shows 'On Deck' message after every turn")
        self.plugin_addcommand("/togglehidejustmovement", self.CMD_togglehidejustmovement,  "Shows 'Just Movement' messages in SR4")
        self.plugin_addcommand("/init",                 self.CMD_init,                  "Toggles whether to record typed intiativies and textual initiative commands")
        self.plugin_addcommand("/clear",                self.CMD_clear,                 "Clears current initiative list")
        self.plugin_addcommand("/start",                self.CMD_start,                 "Clears current initiative list and prompts players to roll")
        self.plugin_addcommand("/addfxhidden",          self.CMD_addfxhidden,           "Adds a hidden effect to the list")
        self.plugin_addcommand("/addfx",                self.CMD_addfx,                 "Adds an effect to the list")
        self.plugin_addcommand("/addhidden",            self.CMD_addhidden,             "Adds a hidden character to the list")
        self.plugin_addcommand("/add",                  self.CMD_add,                   "Adds a character to the list")
        self.plugin_addcommand("/del",                  self.CMD_del,                   "Deletes a character/effect from the list")
        self.plugin_addcommand("/changepass",           self.CMD_changepass,            "Changes current initiative pass [SR4-only]")
        self.plugin_addcommand("/changedur",            self.CMD_changedur,             "Changes duration of specific effect")
        #self.plugin_addcommand("/changefx",             self.CMD_changefx,              "Changes the initiative count of a specific effect")
        self.plugin_addcommand("/change",               self.CMD_change,                "Changes the initiative count of a specific character")
        self.plugin_addcommand("/togglehidden",         self.CMD_togglehidden,          "Toggles whether to show hidden characters in initiative list or not")
        self.plugin_addcommand("/initsetslot",          self.CMD_initsetslot,           "Sets the initiative turn to the designated list slot")
        self.plugin_addcommand("/rankup",               self.CMD_rankup,                "Alters turn priority of one character/effect in the same initiative count as other characters/effects (higher)")
        self.plugin_addcommand("/rankdown",             self.CMD_rankdown,              "Alters turn priority of one character/effect in the same initiative count as other characters/effects (lower)")
        self.plugin_addcommand("/initdelaynow",         self.CMD_initdelaynow,          "???")
        self.plugin_addcommand("/sandglass",            self.CMD_sandglass,             "Toggles sandglass functionality and sets duration of timer")
        self.plugin_addcommand("/sandglasspause",       self.CMD_sandglasspause,        "Pauses the sandglass")
        self.plugin_addcommand("/sandglassresume",      self.CMD_sandglassresume,       "Resumes the sandglass from pause")
        self.plugin_addcommand("/sandglassforceskip",   self.CMD_sandglassforceskip,    "Forces the turn to skip after a number of sandglass duration intervals")
        self.plugin_addcommand("/list",                 self.CMD_list,                  "Displays a list of characters, effects, and turn order to yourself")
        self.plugin_addcommand("/publiclist",           self.CMD_publiclist,            "Displays a list of characters, effects, and turn order to the room")
        self.plugin_addcommand("/rnd",                  self.CMD_rnd,                   "Displays the current round")
        self.plugin_addcommand("/pass",                 self.CMD_pass,                  "Displays the current pass [SR4-only]")
        self.plugin_addcommand("/go",                   self.CMD_go,                    "Advances the turn order to the next character/effect")
        self.plugin_addcommand("/initsave",             self.CMD_initsave,              "Saves current list of initiatives")
        self.plugin_addcommand("/initload",             self.CMD_initload,              "Loads previous list of initiatives")
        self.plugin_addcommand("/initautosave",         self.CMD_initautosave,          "Toggles autosave")
        self.plugin_addcommand("/initautoload",         self.CMD_initautoload,          "Loads previous autosave of initiative")
        self.plugin_addcommand("/nowupmsg",             self.CMD_nowupmsg,              "Customize your own Now Up Message")
        self.plugin_addcommand("/msghandwarning",       self.CMD_msghandwarning,        "Toggles the message handler warning when multiple xxinit2's are loaded in the room") #VEG 2.2.6
        self.plugin_addcommand("/toggleroundreroll",    self.CMD_toggleroundreroll,     "Toggles method of round-by-round initiative in SR4") #VEG 2.2.7
        self.plugin_addcommand("/toggleiporder",        self.CMD_toggleiporder,         "Toggles order of IP execution in SR4") #VEG 2.2.7

        # Add message handlers
        self.plugin_add_msg_handler("xxinit2_checkifloaded", self.received_checkifloaded) #VEG 2.2.6
        self.plugin_add_msg_handler("xxinit2_returnloaded", self.received_returnloaded) #VEG 2.2.6

        self.init_load(0) #VEG 2.2.8 - auto-loads last autosave at startup (helps if you crash)

    def plugin_disabled(self):
        self.plugin_removecmd("/inittool2")
        self.plugin_removecmd("/inittoggle")
        self.plugin_removecmd("/initdebug")
        self.plugin_removecmd("/initgui")
        #self.plugin_removecmd("/initsaveconfig") #VEG 2.2.6
        #self.plugin_removecmd("/initloadconfig") #VEG 2.2.6
        self.plugin_removecmd("/initdefaultconfig")
        self.plugin_removecmd("/initshowconfig")
        self.plugin_removecmd("/togglehideid")
        self.plugin_removecmd("/togglehideondeck")
        self.plugin_removecmd("/togglehidejustmovement")
        self.plugin_removecmd("/init")
        self.plugin_removecmd("/clear")
        self.plugin_removecmd("/start")
        self.plugin_removecmd("/addfxhidden")
        self.plugin_removecmd("/addfx")
        self.plugin_removecmd("/addhidden")
        self.plugin_removecmd("/add")
        self.plugin_removecmd("/del")
        self.plugin_removecmd("/changepass")
        self.plugin_removecmd("/changedur")
        #self.plugin_removecmd("/changefx")
        self.plugin_removecmd("/change")
        self.plugin_removecmd("/togglehidden")
        self.plugin_removecmd("/initsetslot")
        self.plugin_removecmd("/rankup")
        self.plugin_removecmd("/rankdown")
        self.plugin_removecmd("/initdelaynow")
        self.plugin_removecmd("/sandglass")
        self.plugin_removecmd("/sandglasspause")
        self.plugin_removecmd("/sandglassresume")
        self.plugin_removecmd("/sandglassforceskip")
        self.plugin_removecmd("/list")
        self.plugin_removecmd("/publiclist")
        self.plugin_removecmd("/rnd")
        self.plugin_removecmd("/pass")
        self.plugin_removecmd("/go")
        self.plugin_removecmd("/initsave")
        self.plugin_removecmd("/initload")
        self.plugin_removecmd("/initautosave")
        self.plugin_removecmd("/initautoload")
        self.plugin_removecmd("/nowupmsg")
        self.plugin_removecmd("/msghandwarning")
        self.plugin_removecmd("/toggleroundreroll")
        self.plugin_removecmd("/toggleiporder")

        self.plugin_delete_msg_handler("xxinit2_checkifloaded") #VEG 2.2.6
        self.plugin_delete_msg_handler("xxinit2_returnloaded") #VEG 2.2.6

        self.loaded = 0

        try:
            self.frame.Destroy()
        except:
            pass

    # Just received a query from another player; returning a "yes, I have xxinit2 loaded" message
    def received_checkifloaded(self, playerid, data, xml_dom): #VEG 2.2.6
        #print "receive_checkifloaded called: id=" + str(playerid) + "... data = " + str(data)
        self.plugin_send_msg(playerid, "<xxinit2_returnloaded/>")

    # Just received the "yes, I have xxinit2 loaded" message; printing a warning message
    def received_returnloaded(self, playerid, data, xml_dom): #VEG 2.2.6
        if self.msghand_warning:
            self.post_syserror("Warning: xxinit2 plugin detected on "
                               + str(self.session.get_player_by_player_id(playerid)[0]) + "'s system. \
                               Having multiple copies of the xxinit2 plugin in the same room is not \
                               advisable, because it may cause problems. It is suggested that only \
                               one person in the room (the GM) have the xxinit2 plugin loaded. Go to \
                               Tools-Plugins and uncheck the Initiative Tool 2.x to unload it. Type \
                               /msghandwarning to simply turn this warning reminder off.")

    def post_msg(self, text, myself):
        #This is called whenever a message from anyone is about to be posted
        #to chat; it doesn't affect the copy of the message that gets sent to others
        #Be careful; system and info messages trigger this too.
        if self.init_recording:
            if text.lower().find("showinits") != -1:
                self.inits_list(1)
                return text
            elif text.lower().find("nextinit") != -1:
                self.init_next()
                return text
            # all collected, certain values only valid in following systems:
            # d20: player, init, effect, duration
            # sr4: player, init, passes
            # VEG 2.2.7 - The lines that "won't work with macros" are unable to function properly because of the double-layers
            #             of <font> tags that accompany macro sends. The string parsing gets screwed up. It's probably fixable
            #             without changing the way macros are handled, but it's beyond my skill level. =( =( =(
            if myself==1:
                if text.find(" effect ") != -1:
                    effect=text[text.rfind("'>")+2:text.find("[")]
                    duration=text[text.rfind("effect ")+7:text.find("</font>")]
                    init=text[text.rfind("=> ")+3:text.rfind(" effect")]
                elif text.find(" init") != -1:
                    player=text[:text.find("[")]
                    passes=text[text.find("init ")+5:text.find("</font>")]
                    init=text[text.rfind("(")+1:text.rfind(")")]
            else:
                if text.find(" effect ") != -1:
                    effect=text[text.find("</b>: ")+6:text.find("[")]
                    duration=text[text.find("effect ")+7:-7]
                    init=text[text.rfind("=> ")+3:text.rfind(" effect")]
                elif text.find(" init") != -1:
                    player=text[text.find("</b>: ")+6:text.find("[")]
                    passes=text[text.find("init ")+5:-7]
                    init=text[text.rfind("(")+1:text.rfind(")")]
            try:
                if self.isD20() or self.isRQ():
                    if text.find(" effect ") != -1:
                        init=int(init)
                        duration=int(duration)
                        self.init_add([init,duration,effect], 1, 0)
                    elif text.find(" init") != -1:
                        init=int(init)
                        self.init_add([init,player], 0, 0)
                elif self.isSR4():
                    if text.find(" init ") != -1:
                        init=int(init)
                        passes=int(passes)
                        self.init_add([init,passes,player], 0, 0)
            except:
                print("Detected some sort of initiative input... failed!")

        return text


    def refresh_counter(self):
        #This is called once per second. That's all you need to know.
        # load system config once at startup
        if not self.loaded:
            self.loaded = 1
            self.config_load()
            self.config_show()
            self.check_version()

        # do sandglass stuff it has to do
        if not self.isEnded():
           self.sandglass()

        # do the autosaving stuff if needed
        self.autosave()

        # VEG 2.2.6
        self.msghand_timer += 1
        if self.msghand_timer >= 60: # cycle playerlist only 1x every 60 sec
            self.msghand_timer = 0
            self.plugin_send_msg("all", "<xxinit2_checkifloaded/>")

    ###############################################################
    ####    Command Functions
    ###############################################################

    def CMD_inittool2(self, cmdargs):
        f = open(dir_struct["plugins"]+ "inittool2.xml","r")
        f2 = open(dir_struct["plugins"]+ "inittool2_player.xml","r")
        self.gametree.insert_xml(f.read())
        self.gametree.insert_xml(f2.read())
        f.close()
        f2.close()
        return 1

    def CMD_inittoggle(self, cmdargs):
        if self.isSR4():
            self.init_system = "RQ"
            self.init_clear()
            self.post_sysmsg("Now using <font color='#0000ff'><i>RuneQuest</font></i> system.", 1)
        elif self.isD20():
            self.init_system = "SR4"
            self.init_clear()
            self.post_sysmsg("Now using <font color='#0000ff'><i>Shadowrun 4th</font></i> system.", 1)
        elif self.isRQ():
            self.init_system = "D20"
            self.init_clear()
            self.post_sysmsg("Now using <font color='#0000ff'><i>d20</font></i> system.", 1)
        self.config_save() # VEG 2.2.6

    def CMD_initdebug(self, cmdargs):
       cmdargs = cmdargs.split(None,-1)
       if cmdargs[0] == "on":
          self.init_debug = 1
          self.post_sysmsg("Init debugging <font color='#0000ff'><i>on</i></font>.",1)
       elif cmdargs[0] == "off":
          self.init_debug = 0
          self.post_sysmsg("Init debugging <font color='#0000ff'><i>off</i></font>.",1)

    #def CMD_initsaveconfig(self, cmdargs):
    #    self.config_save()

    #def CMD_initloadconfig(self, cmdargs):
    #    self.config_load()

    def CMD_initdefaultconfig(self, cmdargs):
        self.config_default()

    def CMD_initshowconfig(self, cmdargs):
        self.config_show()

    def CMD_togglehideid(self, cmdargs):
        self.hide_id = not self.hide_id
        self.post_sysmsg("Hide IDs: " + str(self.hide_id), 1)
        self.config_save() # VEG 2.2.6

    def CMD_togglehideondeck(self, cmdargs):
        self.hide_ondeck = not self.hide_ondeck
        self.post_sysmsg("Hide 'On Deck': " + str(self.hide_ondeck), 1)
        self.config_save() # VEG 2.2.6

    def CMD_togglehidejustmovement(self, cmdargs):
        self.hide_justmovement = not self.hide_justmovement
        self.post_sysmsg("Hide 'Just Movement' [SR4-only]: " + str(self.hide_justmovement), 1)
        self.config_save() # VEG 2.2.6

    def CMD_init(self, cmdargs):
        if self.init_recording:
            self.init_recording=0
            self.post_sysmsg("Init recording <font color='#0000ff'><i>off</i></font>.")
        else:
            self.init_recording=1
            self.post_sysmsg("Init recording <font color='#0000ff'><i>on</i></font>.")
        self.config_save() # VEG 2.2.6

    def CMD_clear(self, cmdargs):
        self.init_clear()
        self.post_sysmsg("Clearing Initiative List !", 1)

    def CMD_start(self, cmdargs):
        self.init_clear()
        self.post_my_msg("<hr><font color='#ff0000'><b>Starting Round</font> <font color='#0000ff'># <i>1</font> [" + self.init_system + "]</b>", 1)
        self.post_my_msg("<font color='#0000ff'><b>Roll New Initiatives</b></font><hr>", 1)

    def CMD_addfxhidden(self, cmdargs):
        cmdargs = cmdargs.split(None,2)
        if self.isD20() or self.isRQ():
            self.init_add(cmdargs, 1, 1)
        else:
            self.post_syserror("Invalid input. Effects and durations do not work with " + str(self.init_system) + " system.")

    def CMD_addfx(self, cmdargs):
        cmdargs = cmdargs.split(None,2)
        if self.isD20() or self.isRQ():
            self.init_add(cmdargs, 1, 0)
        else:
            self.post_syserror("Invalid input. Effects and durations do not work with " + str(self.init_system) + " system.")

    def CMD_addhidden(self, cmdargs):
        if self.isD20() or self.isRQ():
            cmdargs = cmdargs.split(None,1)
        elif self.isSR4():
            cmdargs = cmdargs.split(None,2)
        self.init_add(cmdargs, 0, 1)

    def CMD_add(self, cmdargs):
        if self.isD20() or self.isRQ():
            cmdargs = cmdargs.split(None,1)
        elif self.isSR4():
            cmdargs = cmdargs.split(None,2)
        self.init_add(cmdargs, 0, 0)

    def CMD_del(self, cmdargs):
        id = int(cmdargs)
        self.init_delete(id-1, 1) # subtract 1 because public lists shows with +1

    def CMD_changepass(self, cmdargs):
        cmdargs = cmdargs.split(None,-1)
        if self.isSR4():
            try:
                id       = int(cmdargs[0])-1 # subtract 1 because public lists shows with +1
                new_pass = int(cmdargs[1])
                if new_pass < 1 or new_pass > 4:
                    self.post_syserror("Invalid input [" + str(self.init_system) + "]. Passes must be greater than/equal to 1 and less than/equal to 4.")
                else:
                    v.init_list[id]["passes"] = new_pass
                    self.post_sysmsg("<font color='#0000ff'><i>" + str(v.init_list[id]["name"]) + "</font></i>'s initiative \
                        pass total has been changed to <font color='#0000ff'><i>" + str(new_pass) + "</font></i> passes !", 1)
            except:
                self.post_syserror("Invalid input [" + str(self.init_system) + "]. That command only works on passes. Correct command is /changepass init_# new_pass_#")

        else:
            self.post_syserror("Invalid input. There are no initiative passes in the " + str(self.init_system) + " system. Try SR4 !")

    def CMD_changedur(self, cmdargs):
        cmdargs = cmdargs.split(None,-1)
        if self.isD20() or self.isRQ():
            try:
                id           = int(cmdargs[0])-1 # subtract 1 because public lists shows with +1
                new_duration = int(cmdargs[1])
                hidden       = v.init_list[id]["hidden"]

                if self.init_debug == 1:
                   print "id : " + str(id)
                   print "new_dur : " + str(new_duration)
                   print "hidden : " + str(hidden)

                if new_duration == 0:
                    self.post_syserror("Invalid input [" + str(self.init_system) + "]. Set duration to '1' if you want the effect to end next time it comes up. \
                        Otherwise, delete the effect with the /del command.", not hidden)
                    return
                elif new_duration < 0:
                    self.post_syserror("Invalid input [" + str(self.init_system) + "]. New duration must be greater than or equal to 1.", not hidden)
                    return

                if self.isEffect(id):
                    v.init_list[id]["duration"] = new_duration
                    self.post_sysmsg("<font color='#0000ff'><i>" + str(v.init_list[id]["name"]) + "</font></i> has been changed \
                        to last <font color='#0000ff'><i>" + str(new_duration) + "</font></i> round(s) !", not hidden)
                else:
                    self.post_syserror("Invalid input [" + str(self.init_system) + "]. That command only works on effects. Correct command is /changedur init_# new_duration_#")

            except Exception, e:
                #print str(e)
                self.post_syserror("Invalid input [" + str(self.init_system) + "]. That command only works on effects. Correct command is /changedur init_# new_duration_#")

        else:
            self.post_syserror("Invalid input. Effects and durations do not work with " + str(self.init_system) + ".")

    #def CMD_changefx(self, cmdargs):
    #    cmdargs = cmdargs.split(None,-1)
    #    if self.isD20() or self.isRQ():
    #        self.init_change(cmdargs,1)
    #    else:
    #        self.post_syserror(">Invalid input. Effects and durations do not work with " + str(self.init_system) + ".")

    #def CMD_change(self, cmdargs):
    #    cmdargs = cmdargs.split(None,-1)
    #    self.init_change(cmdargs,0)

    def CMD_change(self, cmdargs): # VEG 2.2.7
        cmdargs = cmdargs.split(None,-1)
        id = int(cmdargs[0])-1
        new_init = int(cmdargs[1])
        if self.isEffect(id):
            if self.isD20() or self.isRQ():
                self.init_change(id, new_init, 1)
            else:
                self.post_syserror(">Invalid input. Effects and durations do not work with " + str(self.init_system) + ".")
        else:
            self.init_change(id, new_init, 0)

    def CMD_togglehidden(self, cmdargs):
        id = int(cmdargs) - 1
        self.toggle_hidden(id)

    def CMD_initsetslot(self, cmdargs):
        id = int(cmdargs) - 1
        self.init_set_slot(id)

    def CMD_rankup(self, cmdargs):
        cmdargs = cmdargs.split(None,-1)
        id = int(cmdargs[0]) - 1
        try:
            cmdargs[1]
            n = 0 - int(cmdargs[1])
        except:
           # default num of steps to move
           n = -1
        self.init_move(id, n)

    def CMD_rankdown(self, cmdargs):
        cmdargs = cmdargs.split(None,-1)
        id = int(cmdargs[0]) - 1
        try:
            cmdargs[1]
            n = int(cmdargs[1])
        except:
            n = 1
        self.init_move(id, n)

    def CMD_initdelaynow(self, cmdargs):
        id = int(cmdargs) - 1
        self.init_delay_now(id)

    def CMD_sandglass(self, cmdargs):
        try:
            delay = int(cmdargs)
            self.set_sandglass(delay)
        except:
            self.post_syserror("Invalid input. /sandglass (#_of_secs)")

    def CMD_sandglasspause(self, cmdargs):
       self.sandglass_pause()
       self.post_sysmsg("<br><b>Sandglass paused</b>", 1)

    def CMD_sandglassresume(self, cmdargs):
       self.sandglass_resume()
       self.post_sysmsg("<br><b>Sandglass resumed</b>", 1)

    def CMD_sandglassforceskip(self, cmdargs):
        try:
           interval = int(cmdargs)
           self.set_sandglass_force_skip(interval)
        except Exception, e:
          #self.post_my_msg(str(e))
          self.post_syserror("Invalid input. /sandglassforceskip (#_of_intervals)")

    def CMD_list(self, cmdargs):
        self.inits_list(0)

    def CMD_publiclist(self, cmdargs):
        self.inits_list(1)

    def CMD_rnd(self, cmdargs):
        try:
            new_round = int(cmdargs)
            self.init_round = new_round
            self.post_sysmsg("Round number has been changed. It is now Round # <font color='#ff0000'>" + str(new_round) + "</font>",1)
        except:
            self.post_sysmsg("It is currently Round # <font color='#ff0000'>" + str(self.init_round) + "</font>",1)

    def CMD_pass(self, cmdargs):
        try:
            new_pass = int(cmdargs)
            if self.isSR4() and new_pass >= 1 and new_pass <= 4:
                self.init_pass = new_pass
                self.init_count = 0
                self.init_listslot = 0
                self.post_sysmsg("Initiative Pass has been changed. It is currently Pass # <font color='#ff0000'>" + str(self.init_pass) + "</font>",1)
            elif not self.isSR4():
                self.post_syserror("Invalid input. Initiative system must be set to SR4 for passes to function.")
            else:
                self.post_syserror("Invalid input. Passes must be greater than/equal to 1 and less than/equal to 4.")
        except:
            if self.isSR4():
                self.post_sysmsg("It is currently Pass # <font color='#ff0000'>" + str(self.init_pass) + "</font>",1)
            else:
                self.post_syserror("Invalid input. Initiative system must be set to SR4 for passes to function.")

    def CMD_go(self, cmdargs):
        self.init_next()

    def CMD_initsave(self, cmdargs):
        cmdargs = cmdargs.split(None,1)
        slot = int(cmdargs[0])
        try:
            self.init_title = cmdargs[1]
        except:
            self.init_title = "untitled"

        if slot < 1 or slot > 5:
            self.post_syserror("Invalid input. Slot # must be between 1 and 5.")
        else:
            self.init_save(slot, 1)

    def CMD_initload(self, cmdargs):
        try:
            slot = int(cmdargs)
        except:
            slot = 1

        if slot < 1 or slot > 5:
            self.post_syserror("Invalid input. Slot # must be between 1 and 5.")
        else:
            self.init_load(slot)

    def CMD_initautosave(self, cmdargs):
        delay = int(cmdargs)
        self.set_autosave(delay)

    def CMD_initautoload(self, cmdargs):
        self.init_load(0)

    def CMD_nowupmsg(self, cmdargs):
        self.message_nowup = str(cmdargs)
        self.post_my_msg("<b>Now Up Message: </b>" + self.message_nowup)
        self.config_save() # VEG 2.2.6

    def CMD_msghandwarning(self, cmdargs): # VEG 2.2.6
        if self.msghand_warning:
            self.msghand_warning=0
            self.post_sysmsg("Message handler warning <font color='#0000ff'><i>off</i></font>.")
        else:
            self.msghand_warning=1
            self.post_sysmsg("Message handler warning <font color='#0000ff'><i>on</i></font>.")
        self.config_save()

    def CMD_toggleroundreroll(self, cmdargs): # VEG 2.2.7
        if self.reroll_type:
            self.reroll_type=0
            self.post_sysmsg("Reroll toggle set to <font color='#0000ff'><i>Reroll Every Round (default)</i></font>.")
        else:
            self.reroll_type=1
            self.post_sysmsg("Reroll toggle set to <font color='#0000ff'><i>Keep Same Inits Every Round (house rule)</i></font>.")
        self.config_save()

    def CMD_toggleiporder(self, cmdargs): # VEG 2.2.7
        if self.ip_order == 0: # changes IP order to 3/1/4/2 (Serbitar's house rule)
            self.ip_order=1
            self.post_sysmsg("IP order set to <font color='#0000ff'><i>3/1/4/2 (Serbitar's)</i></font>.")
        elif self.ip_order == 1: # changes IP order to 4/1/3/2 (TinkerGnome's house rule)
            self.ip_order=2
            self.post_sysmsg("IP order set to <font color='#0000ff'><i>4/1/3/2 (TinkerGnome's)</i></font>.")
        elif self.ip_order == 2: # changes IP order to 1/2/3/4
            self.ip_order=0
            self.post_sysmsg("IP order set to <font color='#0000ff'><i>1/2/3/4 (normal)</i></font>.")
        self.config_save()

    ###############################################################
    ####    Base Functions
    ###############################################################

    def init_clear(self):
        v.init_list = []
        self.init_round = 1
        self.init_count = 0
        self.init_pass = 0
        self.init_listslot = 0
        self.init_listtag = ""
        self.init_end = 0
        self.sandglass_count = 0
        self.sandglass_status = 0


    def init_add(self, text, effect, hidden):
        if (effect==1) and (self.isD20() or self.isRQ()): #d20 effects
            try:
                if len(text) == 3:
                    h = {}
                    count = int(text[0]) + 1 # effects only decrement (and end)
                                             # before the count in which they
                                             # were added on, so add 1
                    h["type"]     = 1 # effect
                    h["init"]     = count
                    h["name"]     = "*" + str(text[2])
                    h["duration"] = int(text[1])
                    h["rank"]     = self.get_next_rank(h["init"])
                    h["hidden"]   = hidden
                    h["tag"]      = self.get_unique_tag(h["name"])

                    if hidden == 1:
                       duration_str = "?"
                    else:
                       duration_str = str(h["duration"])

                    v.init_list += [h]

                    self.post_sysmsg("<i><font color='#0000ff'>" + h["name"] + "</font></i> effect added to list at init count <i><font color='#0000ff'>" + str(h["init"]) + "</font></i>, lasting <font color='#0000ff'><i>" + duration_str + "</i></font> round(s) !", 1)
                    self.init_sort()
            except:
                self.post_syserror("Invalid input [" + str(self.init_system) + "]. Correct command is: /addfx init_# duration_# description")

        elif self.isD20(): #d20 characters
            try:
                if len(text) == 2:
                    h = {}
                    h["type"]     = 0 # character
                    h["init"]     = int(text[0])
                    h["name"]     = str(text[1])
                    h["rank"]     = self.get_next_rank(h["init"])
                    h["hidden"]   = hidden
                    h["tag"]      = self.get_unique_tag(h["name"])

                    v.init_list += [h]

                    self.post_sysmsg("<font color='#0000ff'><i>" + h["name"] + "</font></i> added to list at init count <i><font color='#0000ff'>" + str(h["init"]) + "</font></i> !", not hidden)
                    self.init_sort()
            except:
                self.post_syserror("Invalid input [" + str(self.init_system) + "]. Correct command is: /add init_# description", not hidden)

        elif self.isSR4(): #SR4 characters
            try:
                if len(text) == 3:
                    h = {}
                    h["type"]     = 0 # character
                    h["init"]     = int(text[0])
                    h["name"]     = str(text[2])
                    h["passes"]   = int(text[1])
                    h["rank"]     = self.get_next_rank(h["init"])
                    h["hidden"]   = hidden
                    h["tag"]      = self.get_unique_tag(h["name"])

                    v.init_list+=[h]

                    self.post_sysmsg("<font color='#0000ff'><i>" + h["name"] + "</font></i> added to list at init count \
                        <font color='#0000ff'><i>" + str(h["init"]) + "</font></i> with <font color='#0000ff'><i>" + str(h["passes"])+ "</font></i> \
                        passes !", not hidden)

                    self.init_sort()

            except:
                self.post_syserror("Invalid input [" + str(self.init_system) + "]. Correct command is: /add init_# passes_# description", not hidden)

        elif self.isRQ(): #RQ characters
            try:
                if len(text) == 2:
                    h = {}
                    h["type"]     = 0 # character
                    h["init"]     = int(text[0])
                    h["name"]     = str(text[1])
                    h["rank"]     = self.get_next_rank(h["init"])
                    h["hidden"]   = hidden
                    h["tag"]      = self.get_unique_tag(h["name"])

                    v.init_list += [h]

                    self.post_sysmsg("<font color='#0000ff'><i>" + h["name"] + "</font></i> added to list at Strike Rank \
                        <font color='#0000ff'><i>" + str(h["init"]) + "</font></i> !", not hidden)

                    self.init_sort()
            except:
                self.post_syserror("Invalid input [" + str(self.init_system) + "]. Correct command is: /add SR description", not hidden)


    def init_delete(self, id, public):
        try:
            name = v.init_list[id]["name"]
            is_last = 0
            is_self = 0
            is_effect = 0
            if public == 1:
                self.post_sysmsg("<font color='#0000ff'><i>" + name + "</font></i> has been removed from the initiative list !", not v.init_list[id]["hidden"])
            if self.isLast(id):
                is_last = 1
            if self.init_listslot == id:
                is_self = 1
            if self.isEffect(id):
                is_effect = 1

            del v.init_list[id]

            if is_effect:
                self.init_listslot -= 1
            elif is_last and is_self:
                self.init_next()
            elif is_self == 1:
                self.init_listslot -= 1
                self.init_next()
            self.init_sort()
        except:
            if public == 1:
                self.post_syserror("Invalid input [" + str(self.init_system) + "]. Correct command is: /del list_number")


    def init_change(self, id, new_init, effect):
        try:
            proceed = 0
            old_name = v.init_list[id]["name"]

            if v.init_list[id]["init"] == new_init:
               self.post_syserror("Invalid input [" + str(self.init_system) + "]. Already at init count <font color='#0000ff'>" + str(new_init) + "</font>. Try /rankup or /rankdown instead.")
               return

            if effect == 1 and (self.isD20() or self.isRQ()): #d20 and RQ effects
                if self.isEffect(id):
                    proceed  = 1
                    self.post_sysmsg("<font color='#0000ff'><i>" + old_name + "</font></i> has had its init count changed \
                        to <font color='#0000ff'><i>" + str(new_init) + "</font></i>.", not v.init_list[id]["hidden"])
                else:
                    self.post_syserror("Invalid input [" + str(self.init_system) + "]. Not an effect. Try /change instead.")

            else: #d20, SR4, RQ characters
                if self.isEffect(id):
                    self.post_syserror("Invalid input [" + str(self.init_system) + "]. Not a character. Try /changefx instead.")
                else:
                    proceed  = 1
                    self.post_sysmsg("<font color='#0000ff'><i>" + old_name + "</font></i>'s init count has changed to \
                        <font color='#0000ff'><i>" + str(new_init) + "</font></i>.", not v.init_list[id]["hidden"])
            if proceed==1:

                listslot_as_changed = 0
                # hacks if currently selected listslot /change's, we select the next tag
                if not self.isEnded() and id == self.init_listslot:
                    if not self.isLast(id):
                       self.init_listtag = v.init_list[id + 1]["tag"]
                       listslot_as_changed = 1
                       self.sandglass_reset()
                    else:
                       self.init_listtag = v.init_list[self.getLast()]["tag"]
                       self.init_next()

                v.init_list[id]["init"] = new_init

                # set the rank to the lowest rank available...
                v.init_list[id]["rank"] = self.get_next_rank(v.init_list[id]["init"])

                self.init_sort()

                # tell if listslot as changed
                if listslot_as_changed == 1:
                   if self.init_count >= v.init_list[id]['init']:
                       self.init_listslot -= 1
                       self.init_count = v.init_list[self.init_listslot]['init']
                   else:
                       self.init_listslot -= 1
                       self.init_next()
                   #self.post_now_up(self.init_listslot, self.message_nowup + ": ")
                   #self.init_next()

        except:
            if effect == 1:
                self.post_syserror("Invalid input [" + str(self.init_system) + "]. Correct command is: /changefx list_# new_init_# (example: /change 1 4)")
            else:
                self.post_syserror("Invalid input [" + str(self.init_system) + "]. Correct command \
                    is: /change list_# new_init_# (example: /change 1 4)")


    def init_sort(self):
        if self.isD20():
            self.sort_high()
        elif self.isSR4():
            self.sort_high()
        elif self.isRQ():
            self.sort_low()
        else:
            self.sort_high()


    def sort_low(self):
        v.init_list.sort(self.sort_low_initlist)
        # this part readjusts the listslot when other objects are
        # changed, added, moved or deleted from v.init_list
        #count = self.init_count
        if self.isEnded():
           return
        n = 0
        last_tag = self.init_listtag
        last_id = self.init_listslot
        found = 0

        for m in v.init_list:
            id = v.init_list.index(m) # first listslot's id

            if v.init_list[id]["tag"] == last_tag:
               self.init_listslot = id
               found = 1
               break

        # if can't find, it got /del'd
        if found == 0 and self.init_listtag != "":
            # next slot should've been bumped up, we re selecting it
            try:
               self.init_listtag = v.init_list[self.init_listslot]["tag"]
            except:
               #we del'd the last one... do nuttin
               pass


    def sort_high(self):
        v.init_list.sort(self.sort_high_initlist)
        v.init_list.reverse()
        # this part readjusts the listslot when other objects are
        # changed, added, moved or deleted from v.init_list
        #count = self.init_count

        if self.isEnded():
           return
        n = 0
        last_tag = self.init_listtag
        last_id = self.init_listslot
        found = 0
        for m in v.init_list:
            id = v.init_list.index(m) # first listslot's id
            #print "sid : " + str(id)
            if v.init_list[id]["tag"] == last_tag:
               self.init_listslot = id
               found = 1
               break
        # if can't find, it got /del'd
        if found == 0 and self.init_listtag != "":
            # next slot should've been bumped up, we re selecting it
            try:
               self.init_listtag = v.init_list[self.init_listslot]["tag"]
            except:
               #we del'd the last one... do nuttin
               pass


    def sort_low_initlist(self, x, y):
       if x['init'] < y['init']:
          return -1
       elif x['init'] > y['init']:
          return 1
       elif x['init'] == y['init']:
          # if same init, we sort by rank
          if x['rank'] > y['rank']:
             return -1
          elif x['rank'] < y['rank']:
             return 1
          else:
                return 0
       else: # shouldnt enter here
          return 0


    def sort_high_initlist(self, x, y):
        if x['init'] < y['init']:
            return -1
        elif x['init'] > y['init']:
            return 1
        elif x['init'] == y['init']:
            # if same init, we sort by rank
            if x['rank'] < y['rank']:
                return -1
            elif x['rank'] > y['rank']:
                return 1
            else:
                return 0
        else: # shouldnt enter here
            return 0


    def init_next(self):
       if self.isD20():
          self.init_next_D20()
       elif self.isSR4():
          self.init_next_SR4()
       elif self.isRQ():
          self.init_next_RQ()


    def init_next_D20(self):

        if self.isEnded():
            self.init_listslot = -1  # offsets +1 coming later, starts 0
            self.init_listtag = ""
            self.init_end = 1

        if not self.isEnded():
            try:
                self.init_listslot += 1 #toldya
                id   = self.init_listslot
                init = str(v.init_list[id]["init"])
                name = str(v.init_list[id]["name"])
                self.init_listtag = v.init_list[id]["tag"]
                self.init_count = v.init_list[id]["init"]

                if self.isEffect(id):
                    v.init_list[id]["duration"] -= 1     #subtract 1 rnd from duration
                    if self.getRoundsLeftInEffect(id) == 0:
                        self.post_effect(id, "EFFECT ENDING:")
                        self.init_delete(id, 0)

                        #nextslot = id #this effect got deleted, so id = former id+1

                        # hack if two consecutive effects and this one has ended
                        #if self.isEffect(nextslot):
                        #    print "nextslot IS an effect"
                        #    self.init_listslot -= 1 # zalarian
                        #    id = self.init_listslot # zalarian
                        #else:
                        #    print "nextslot IS NOT an effect"
                        #    v.init_list[id]["hidden"] = 0
                        #    self.post_now_up(id, self.message_nowup + ": ")

                        # reset the sandglass for this turn
                        self.sandglass_reset()
                    else:
                        if v.init_list[id]["hidden"] == 1:
                           rounds_left = "?"
                        else:
                           rounds_left = self.getRoundsLeftInEffect(id)

                        if self.hide_id == 0:
                           str_id = str(id+1) + ":"
                        else:
                           str_id = ""

                        self.post_effect(id, "EFFECT:")

                        nextslot = id + 1

                        if self.isEffect(nextslot):
                            self.init_next_D20()
                else:   #normal character, not effect
                    v.init_list[id]["hidden"] = 0

                    self.post_now_up(id, self.message_nowup + ": ")

                    # reset the sandglass for this turn
                    self.sandglass_reset()

            except Exception, e:

                self.init_end = 0
                self.init_round += 1
                self.init_count = 0
                self.post_sysmsg("<hr><font color='#ff0000'>End of Round<br>Starting Round <font color='#0000ff'><i># " + str(self.init_round) + "</font></i></font><hr>",1)


    def init_next_SR4(self, do_not_advance_past_init=0):
        if self.isEnded():
            self.init_listslot = -1  # offsets +1 coming later, starts 0
            self.init_listtag = ""
            self.init_end = 1

        if not self.isEnded():
            if self.init_pass == 0:
                self.init_pass +=1
            if self.init_pass > 4:
                self.init_end = 0
                self.init_round += 1
                self.init_pass = 0
                msg = "<hr><font color='#ff0000'>End of Round<br>Starting Round <font color='#0000ff'><i># " + str(self.init_round) + "</font></i></font><hr>"

                if self.reroll_type == 0: # Reroll Every Round (default) - VEG 2.2.7
                    v.init_list = []
                    msg += "<font color='#0000ff'>Roll New Initiatives</font><hr>"
                else: # Keep Same Inits Every Round - VEG 2.2.7
                    pass
                self.post_sysmsg(msg,1)

            else:
                try:
                    valid_char = 0
                    just_movement = 0
                    while valid_char != 1:
                        self.init_listslot += 1 #toldya
                        id   = self.init_listslot
                        passes = v.init_list[id]["passes"] #exception raised here if noone left

                        if self.ip_order == 0: # ip order: 1/2/3/4 (normal) - VEG 2.2.7
                            if passes >= self.init_pass:
                                valid_char = 1
                            elif self.hide_justmovement != 1: # not enough passes, but still gain movement
                                just_movement = 1
                                valid_char = 1

                        else: # ip order: 3/1/4/2 (Serbitar's house rule) or 4/1/3/2 (TinkerGnome's house rule) - VEG 2.2.7
                            if self.init_pass == 1: # first pass: only people with 3+ (S) or 4+ (TG) IPs go
                                if self.ip_order == 1 and passes >= 3: # ip order: 3/1/4/2
                                    valid_char = 1
                                elif self.ip_order == 2 and passes >= 4: # ip order: 4/1/3/2
                                    valid_char = 1
                                elif self.hide_justmovement != 1:
                                    just_movement = 1
                                    valid_char = 1
                            elif self.init_pass == 2: # second pass: only people with 1+ IPs go
                                if passes >= 1:
                                    valid_char = 1
                                elif self.hide_justmovement != 1:
                                    just_movement = 1
                                    valid_char = 1
                            elif self.init_pass == 3: # third pass: only people with 4+ (S) or 3+ (TG) IPs go
                                if self.ip_order == 1 and passes >= 4: # ip order: 4/1/4/2
                                    valid_char = 1
                                elif self.ip_order == 2 and passes >= 3: # ip order: 3/1/3/2
                                    valid_char = 1
                                elif self.hide_justmovement != 1:
                                    just_movement = 1
                                    valid_char = 1
                            elif self.init_pass == 4: # fourth pass: only people with 2+ IPs go
                                if passes >= 2:
                                    valid_char = 1
                                elif self.hide_justmovement != 1:
                                    just_movement = 1
                                    valid_char = 1

                    init = str(v.init_list[id]["init"])
                    name = str(v.init_list[id]["name"])
                    self.init_listtag = v.init_list[id]["tag"]
                    self.init_count = v.init_list[id]["init"]
                    v.init_list[id]["hidden"] = 0  # no more hidden

                    if just_movement == 0:
                        self.post_now_up(id, self.message_nowup + ": ")
                    else:
                        self.post_movement(id, " JUST MOVEMENT:")

                    # reset the sandglass for this turn
                    self.sandglass_reset()

                    if just_movement==1 and self.isMovement(id + 1) and do_not_advance_past_init==0:
                        self.init_next_SR4() # for convenience sake, characters who only have movement
                                        #     will be grouped together.
                                        # do_not_advance_past_init is a hackfix to avoid some
                                        #     problems found with this trick
                    elif self.sharesInit(id + 1):  # rules say characters who share an init take
                        self.init_next_SR4(1)      # actions simultaneously (for the most part)

                except:
                    old_pass = self.init_pass
                    self.init_pass += 1
                    self.init_count = 0
                    self.init_end = 0
                    if self.init_pass != 5:
                        self.post_sysmsg("<hr><font color='#ff0000'>End of Pass <font color='#0000ff'><i>#"\
                            + str(old_pass) + "</font></i><br>Starting New Pass <font color='#0000ff'><i># " \
                            + str(self.init_pass) + "</font></i></font><hr>", 1)
                    else:
                        self.init_next_SR4()


    def init_next_RQ(self):
        if self.isEnded():
            self.init_listslot = -1  # offsets +1 coming later, starts 0
            self.init_listtag = ""
            self.init_end = 1

        if not self.isEnded():
            try:
                self.init_listslot += 1 #toldya
                id   = self.init_listslot
                init = str(v.init_list[id]["init"])
                name = str(v.init_list[id]["name"])
                self.init_listtag = v.init_list[id]["tag"]
                self.init_count = v.init_list[id]["init"]

                if self.isEffect(id):
                    v.init_list[id]["duration"] -= 1     #subtract 1 rnd from duration
                    if self.getRoundsLeftInEffect(id) == 0:
                        self.post_effect(id, "EFFECT ENDING:")
                        self.init_delete(id, 0)

                        # hack if two consecutive effects and this one has ended
                        #if self.isEffect(nextslot):
                        #   self.init_listslot -= 1 # zalarian
                        #   id = self.init_listslot # zalarian
                        #else:
                        #   v.init_list[id]["hidden"] = 0

                        #   self.post_now_up(id, self.message_nowup + ": ")

                        # reset the sandglass for this turn
                        self.sandglass_reset()
                    else:
                        if v.init_list[id]["hidden"] == 1:
                           rounds_left = "?"
                        else:
                           rounds_left = self.getRoundsLeftInEffect(id)


                        if self.hide_id == 0:
                           str_id = str(id+1) + ":"
                        else:
                           str_id = ""

                        self.post_effect(id, "EFFECT:")

                        nextslot = id + 1

                    if self.isEffect(nextslot):
                       self.init_next_RQ()
                else:   #normal character, not effect
                    v.init_list[id]["hidden"] = 0

                    self.post_now_up(id, self.message_nowup + ": ")

                    # reset the sandglass for this turn
                    self.sandglass_reset()

            except Exception, e:
                self.init_end = 0
                self.init_round += 1
                self.init_count = 0
                self.post_sysmsg("<hr><font color='#ff0000'>End of Round<br>Starting Round <font color='#0000ff'><i># " + str(self.init_round) + "</font></i></font><hr>",1)

    def init_set_slot(self, id):
       try:
          if self.isEnded():
             raise
          else:
             if id == self.init_listslot:
                self.post_syserror("Slot <font color='#0000ff'>#" + str(id + 1) + "</font> already selected.")
             else:
                self.init_listtag = v.init_list[id]["tag"]
                self.init_listslot = id
                self.sandglass_reset()
                self.post_sysmsg("<font color='#0000ff'><i>" + v.init_list[id]["name"] + "</font></i> selected !")

       except:
          self.post_syserror("Can't select slot <font color='#0000ff'>#" + str(id) + "</font>. Round must be started.")

    def init_move(self, id, n):
       try:
          # how many inits we have so far
          list_size = len(v.init_list)

          if self.init_debug == 1:
             print "list_size : " + str(list_size)
             print "id : " + str(id)
             print "pre n : " + str(n)

          if id >= list_size:
             self.post_syserror("Can't move an unknown ID (<font color='#0000ff'>" + str(id+1) + "</font>) !")
             return

          # are we going UP or DOWN ?
          if n > 0:
             up = 0
             step = 1
             # can't move down last object
             if self.isLast(id):
                self.post_syserror("Can't move <font color='#0000ff'>" + v.init_list[id]["name"] + "</font> this way! (Already at the last init)")
                return

             max_move = list_size - id # maximum num of moves we could possibly do
             # cant move more than max_move position!!
             if n > max_move:
                n = max_move
          elif n < 0:
             up = 1
             step = -1
             #can't move up first object
             if self.isFirst(id):
                self.post_syserror("Can't move <font color='#0000ff'>" + v.init_list[id]["name"] + "</font> this way ! (Already at the first init)")
                return

             max_move = id # maximum num of move we could possibly do
             # cant move more than max_move position!!
             if n > max_move:
                n = -max_move
          else:
             # shouldnt be here
             self.post_syserror("Can't move <font color='#0000ff'>" + v.init_list[id]["name"] + "</font> !")
             return 1

          if self.init_debug == 1:
             print "n : " + str(n)
             print "step : " + str(step)
             print "max_move : " + str(max_move)
             print "up : " + str(up)
             print "len : " + str(len(range(id , (id + n + step), step)))

          # suppose we're not moving, id_n will be the target id we're moving to
          id_n = id

          # find the last init we can go with 'n' steps and staying on the init count of object 'id'
          for k in range(id + step , (id + n + step), step):
             #print "k... " + str(k)
             if v.init_list[k]["init"] != v.init_list[id]["init"]:
                # cant more further than k + step.. go away
                break
             else:
                id_n = k

          # we can't move if id_n is the same as id. probably only alone on this init count
          if id_n == id:
             self.post_syserror("Can't move <font color='#0000ff'>" + v.init_list[id]["name"] + "</font> ! (you may only rankup/rankdown within the same init value)</i>")
             return

          if self.init_debug == 1:
             print "id_n : " + str(id_n)

          # now we have to set the rank correctly
          if up and self.isFirst(id_n):
             # going up and we're moving in first position of all inits
             v.init_list[id]["rank"] = v.init_list[id_n]["rank"] + 1
          elif not up and self.isLast(id_n):
             # going down and we're moving in last position of all inits
             v.init_list[id]["rank"] = v.init_list[id_n]["rank"] - 1
          elif v.init_list[id_n + step]["init"] != v.init_list[id]["init"]:
             # moving in first (up) or last (down) position of the current init count
             v.init_list[id]["rank"] = v.init_list[id_n]["rank"] - step
          elif up and v.init_list[id_n + step]["init"] == v.init_list[id]["init"]:
             # moving up somewhere between multiple id of the same init count
             v.init_list[id]["rank"] = v.init_list[id_n]["rank"] - (step * (v.init_list[id_n + step]["rank"] - v.init_list[id_n]["rank"]) / 2.0)
          elif not up and v.init_list[id_n + step]["init"] == v.init_list[id]["init"]:
             # moving down somewhere between multiple id of the same init count
             v.init_list[id]["rank"] = v.init_list[id_n]["rank"] + (step * (v.init_list[id_n + step]["rank"] - v.init_list[id_n]["rank"]) / 2.0)

          self.post_sysmsg("<font color='#0000ff'><i>" + v.init_list[id]["name"] + "</font></i> moved !", not v.init_list[id]["hidden"])

          # hack, if we're moving the selected slot or at the selected
          # slot, we're staying at the same position.
          if not self.isEnded():
             if id_n == self.init_listslot:
                # we're moving AT the selected slot
                self.init_listtag = v.init_list[id]["tag"]
                self.sandglass_reset()
                self.post_now_up(id, self.message_nowup + ": ")
                # works fine unless you try to rank by more than one step, so
                # currently this section (or the other) is bugged
             if id == self.init_listslot:
                # we're moving THE selected slot
                if up:
                   self.init_listtag = v.init_list[id-1]["tag"]
                else:
                   self.init_listtag = v.init_list[id+1]["tag"]
                self.post_now_up(id_n, self.message_nowup + ": ")
                # works fine unless you try to rank by more than one step, so
                # currently this section (or the other) is bugged
                self.sandglass_reset()


          # sort that list again
          self.init_sort()

       except:
          self.post_syserror("Can't move <font color='#0000ff'>" + v.init_list[id]["name"] + "</font> ! (May only rankup/rankdown within the same init value)")


    def init_delay_now(self, id):
       try:
          # can't delay if round ended
          if self.isEnded():
             self.post_syserror("Can't delay until the round has started.", 0)
             return

          if self.isD20() or self.isRQ():
             # get current tag
             tag_current = v.init_list[self.init_listslot]["tag"]
             tag_delay = v.init_list[id]["tag"]
             name_delay = v.init_list[id]["name"]

             # can't delay current listslot
             if self.init_listslot == id:
                self.post_syserror("Can't delay current selected slot.", 0)
                return

             # if not on the same init count
             if v.init_list[self.init_listslot]["init"] != v.init_list[id]["init"]:
                # generate array needed by init_change() as first parameter
                tab = [ 0, id + 1, v.init_list[self.init_listslot]["init"]]
                self.init_change(tab, v.init_list[id]["type"])
                self.init_sort()

             #print "name_delay : " + str(name_delay)
             #print "tag_delay : " + str(tag_delay)
             #print "tag_current : " + str(tag_current)
             #print "slot_tag : " + str(v.init_list[self.init_listslot]["tag"])
             #print "listslot : " + str(self.init_listslot)

             # must rankup if needed (init_change() move at the end of a group if at same init count
             if not (v.init_list[self.init_listslot]["tag"] == tag_delay):
                # must find where is tag_delay and move it before tag_current
                for m in v.init_list:
                   if m["tag"] == tag_delay:
                      new_id_delay = v.init_list.index(m)
                      break

                step = (self.init_listslot - new_id_delay)
                self.init_move(new_id_delay, step)
                #self.init_listtag = tag_delay
                self.init_sort()

             self.post_now_up(self.init_listslot, "NOW UP FOR THE KILLING (DELAYED ACTION):")

             self.sandglass_reset()

          else:
             self.post_syserror(">Can't delay in " + str(self.init_system) + ".")

       except Exception, e:
          print str(e)
          self.post_syserror("Invalid input [" + str(self.init_system) + "]. Correct command is: /initdelaynow list_number")

    ###############################################################
    ####    Sandglass Functions
    ###############################################################

    # will send reminder to the chat if needed
    def sandglass(self):
       try:
          if self.sandglass_delay == 0 or self.sandglass_status == 1:
             pass
          # send reminder except for effect
          elif not self.isEnded() and not self.isEffect(self.init_listslot):
             self.sandglass_count += 1
             if self.sandglass_skip_interval and not (self.sandglass_count % (self.sandglass_delay * self.sandglass_skip_interval)):
                uname = v.init_list[self.init_listslot]["name"]
                self.post_sysmsg("TIME'S UP <font color='#0000ff'><i>" + uname + "</font></i>!!! (<i>" + str(self.sandglass_count) + " seconds elapsed</i>)", 1)
                self.init_next()
             elif not (self.sandglass_count % self.sandglass_delay):
                self.post_sysmsg("REMINDER to <font color='#0000ff'><i>" + v.init_list[self.init_listslot]["name"] + "</font></i> : IT'S YOUR TURN! (<i>" + str(self.sandglass_count) + " seconds elapsed</i>)", 1)

       except:
          pass


    def sandglass_reset(self):
       try:
          if self.sandglass_delay > 0:
             self.sandglass_count = 0
             self.sandglass_resume()
       except:
          pass


    # status :  0 = running
    #           1 = pause
    def sandglass_pause(self):
       try:
          if self.sandglass_delay > 0:
             self.sandglass_status = 1
       except:
          pass


    def sandglass_resume(self):
       try:
          if self.sandglass_delay > 0:
             self.sandglass_status = 0
       except:
          pass

    def set_sandglass_force_skip(self,interval):
       self.sandglass_skip_interval = interval
       if interval == 0:
          self.post_sysmsg("Sandglass force turn skip is now off.", 1)
       else:
          self.post_sysmsg("Sandglass force turn skip is now set to " + str(interval) + " interval(s).", 1)
       self.config_save() # VEG 2.2.6

    def set_sandglass(self, delay):
       self.sandglass_delay = delay
       if delay == 0:
          self.post_sysmsg("Sandglass is now off.", 1)
       else:
          self.post_sysmsg("Sandglass is now set to " + str(delay) + " seconds.", 1)
       self.config_save() # VEG 2.2.6

    ###############################################################
    ####    Config/Save/Load Functions
    ###############################################################

    def init_save(self, slot, public):
       try:
          modname = "xxinit2-" + str(slot)

          self.plugindb.SetString(modname, "init_recording",  str(self.init_recording))
          self.plugindb.SetString(modname, "init_round",      str(self.init_round))
          self.plugindb.SetString(modname, "init_title",      str(self.init_title))
          self.plugindb.SetString(modname, "init_count",      str(self.init_count))
          self.plugindb.SetString(modname, "init_pass",       str(self.init_pass))
          self.plugindb.SetString(modname, "init_listslot",   str(self.init_listslot))
          self.plugindb.SetString(modname, "init_listtag",    str(self.init_listtag))
          self.plugindb.SetString(modname, "init_end",        str(self.init_end))
          self.plugindb.SetString(modname, "init_system",     str(self.init_system))
          self.plugindb.SetString(modname, "init_list",       repr(v.init_list))
          self.plugindb.SetString(modname, "sandglass_status",       repr(self.sandglass_status))

          if self.init_title != "":
             title_str = " <i>[" + self.init_title + "]</i>"
          else:
             title_str = ""

          if slot == 0:
             #self.post_sysmsg("Initiative list autosaved successfully.", public)
             # this is annoying, so i disabled the text output
             pass
          else:
             self.post_sysmsg("Initiative list saved successfully on slot #" + str(slot) + title_str + ".", public)

       except Exception, e:
          print "err saving : " + str(e)


    def init_load(self, slot):
       try:
          self.init_clear()

          modname = "xxinit2-" + str(slot)

          self.init_recording  = int(self.plugindb.GetString(modname, "init_recording","0"))
          self.init_round      = int(self.plugindb.GetString(modname, "init_round", "0"))
          self.init_title      = str(self.plugindb.GetString(modname, "init_title", ""))
          self.init_count      = int(self.plugindb.GetString(modname, "init_count", "0"))
          self.init_pass       = int(self.plugindb.GetString(modname, "init_pass", "0"))
          self.init_listslot   = int(self.plugindb.GetString(modname, "init_listslot", "0"))
          self.init_listtag    = str(self.plugindb.GetString(modname, "init_listtag", ""))
          self.init_end        = int(self.plugindb.GetString(modname, "init_end", "0"))
          self.init_system     = str(self.plugindb.GetString(modname, "init_system", ""))
          v.init_list          = eval(self.plugindb.GetString(modname, "init_list", ""))
          self.sandglass_status = eval(self.plugindb.GetString(modname, "sandglass_status", "0"))

          if self.init_title != "":
             title_str = " <i>[" + self.init_title + "]</i>"
          else:
             title_str = ""

          if slot == 0:
             self.post_sysmsg("Last autosaved initiative list loaded successfully.")
          else:
             self.post_sysmsg("Initiative list slot #" + str(slot) + title_str + " loaded successfully.")
          self.config_save() # VEG 2.2.6

       except Exception, e:
          #print "err loading: " + e
          self.post_syserror("Error loading Initiative list.")


    def autosave(self):
       try:
          slot = 0
          if self.autosave_delay != 0:
             self.autosave_count += 1
             if not (self.autosave_count % self.autosave_delay):
                self.autosave_count = 0
                self.init_save(slot, 0)

       except Exception, e:
          print str(e)


    def set_autosave(self, delay):

       self.autosave_delay = delay

       if delay == 0:
          self.post_sysmsg("Autosave is now off.")
       else:
          self.post_sysmsg("Autosave is now done every " + str(delay) + " seconds.")


    def config_save(self):
       try:
          modname = "xxinit2-config"

          # don't want python to convert this to the strings "TRUE" or "FALSE"
          if self.init_recording == 0:
             self.init_recording = 0
          else:
             self.init_recording = 1

          if self.hide_id == 0:
             self.hide_id = 0
          else:
             self.hide_id = 1

          if self.hide_ondeck == 0:
             self.hide_ondeck = 0
          else:
             self.hide_ondeck = 1

          if self.hide_justmovement == 0:
             self.hide_justmovement = 0
          else:
             self.hide_justmovement = 1

          self.plugindb.SetString(modname, "init_recording",  str(self.init_recording))
          self.plugindb.SetString(modname, "init_system",     str(self.init_system))
          self.plugindb.SetString(modname, "sandglass_count", str(self.sandglass_count))
          self.plugindb.SetString(modname, "sandglass_delay", str(self.sandglass_delay))
          self.plugindb.SetString(modname, "sandglass_skip_interval", str(self.sandglass_skip_interval))
          self.plugindb.SetString(modname, "autosave_delay",  str(self.autosave_delay))
          self.plugindb.SetString(modname, "autosave_count",  str(self.autosave_count))
          self.plugindb.SetString(modname, "hide_id",         str(self.hide_id))
          self.plugindb.SetString(modname, "hide_ondeck",     str(self.hide_ondeck))
          self.plugindb.SetString(modname, "hide_justmovement",str(self.hide_justmovement))
          self.plugindb.SetString(modname, "message_nowup",   str(self.message_nowup))
          self.plugindb.SetString(modname, "msghand_timer",   str(self.msghand_timer)) # VEG 2.2.6
          self.plugindb.SetString(modname, "msghand_warning", str(self.msghand_warning)) # VEG 2.2.6
          self.plugindb.SetString(modname, "reroll_type",     str(self.reroll_type)) # VEG 2.2.7
          self.plugindb.SetString(modname, "ip_order",      str(self.ip_order)) # VEG 2.2.7

          #self.post_sysmsg("Configuration saved successfully.",0)
          print "Initiative configuration saved successfully."

       except:
          self.post_syserror("Error saving configuration.",0)


    def config_load(self):

       try:
          modname = "xxinit2-config"

          self.init_recording  = int(self.plugindb.GetString(modname, "init_recording","0"))
          self.init_system     = str(self.plugindb.GetString(modname, "init_system", ""))
          self.sandglass_count = int(self.plugindb.GetString(modname, "sandglass_count", "0"))
          self.sandglass_delay = int(self.plugindb.GetString(modname, "sandglass_delay", "0"))
          self.sandglass_skip_interval = int(self.plugindb.GetString(modname, "sandglass_skip_interval", "0"))
          self.autosave_delay  = int(self.plugindb.GetString(modname, "autosave_delay", "0"))
          self.autosave_count  = int(self.plugindb.GetString(modname, "autosave_count", "0"))
          self.hide_id         = int(self.plugindb.GetString(modname, "hide_id", "0"))
          self.hide_ondeck     = int(self.plugindb.GetString(modname, "hide_ondeck", "0"))
          self.hide_justmovement = int(self.plugindb.GetString(modname, "hide_justmovement", "0"))
          self.message_nowup   = str(self.plugindb.GetString(modname, "message_nowup", ""))
          self.msghand_timer   = int(self.plugindb.GetString(modname, "msghand_timer", "0")) # VEG 2.2.6
          self.msghand_warning = int(self.plugindb.GetString(modname, "msghand_warning", "0")) # VEG 2.2.6
          self.reroll_type     = int(self.plugindb.GetString(modname, "reroll_type", "0")) # VEG 2.2.7
          self.ip_order      = int(self.plugindb.GetString(modname, "ip_order", "0")) # VEG 2.2.7

          # if system blank... no config was loaded
          if self.init_system == "":
             raise

          self.post_sysmsg("Configuration loaded successfully.",0)
          self.config_save() # VEG 2.2.6

       except:
          self.config_default()


    def config_default(self):

          self.init_recording = 1
          self.init_system = "D20"
          self.sandglass_count = 0
          self.sandglass_delay = 0
          self.sandglass_status = 0
          self.sandglass_skip_interval = 0
          self.autosave_delay = 60
          self.autosave_count = 0
          self.hide_id = 0
          self.hide_ondeck = 0
          self.hide_justmovement = 0
          self.message_nowup = "NEXT UP FOR THE KILLING"
          self.msghand_timer = 0
          self.msghand_warning = 1
          self.reroll_type = 0
          self.ip_order = 0

          self.post_sysmsg("Default configuration loaded successfully.",0)
          self.config_save() # VEG 2.2.6

    def config_show(self):

       try:
          self.post_sysmsg("<br><u>Init Tool system config v" + str(self.version) + "</u><br>")

          if self.init_recording == 0:
             buf = "disabled";
          else:
             buf = "enabled";
          self.post_my_msg("<b>Init Recording:</b> " + str(buf))

          self.post_my_msg("<b>System:</b> " + str(self.init_system))

          if self.sandglass_delay == 0:
             buf = "disabled";
          else:
             buf = str(self.sandglass_delay) + " seconds"
             if self.sandglass_status == 1:
                buf += str(" [ paused ]")

          self.post_my_msg("<b>Sandglass:</b> " + str(buf))

          if self.sandglass_skip_interval == 0:
             buf = "disabled";
          else:
             buf = "every " + str(self.sandglass_skip_interval) + " interval(s)."
          self.post_my_msg("<b>Sandglass force skip:</b> " + str(buf))

          if self.autosave_delay == 0:
             buf = "disabled";
          else:
             buf = str(self.autosave_delay) + " seconds"
          self.post_my_msg("<b>Autosave:</b> " + str(buf))

          if self.msghand_warning == 0: # VEG 2.2.6
             buf = "disabled";
          else:
             buf = "enabled";
          self.post_my_msg("<b>Show Message Handler Warning:</b> " + str(buf))

          if self.hide_id == 0:
             buf = "disabled";
          else:
             buf = "enabled";
          self.post_my_msg("<b>Hide IDs:</b> " + str(buf))

          if self.hide_ondeck == 0:
             buf = "disabled";
          else:
             buf = "enabled";
          self.post_my_msg("<b>Hide 'On Deck':</b> " + str(buf))

          if self.hide_justmovement == 0:
             buf = "disabled";
          else:
             buf = "enabled";
          self.post_my_msg("<b>[SR4-only] Hide 'Just Movement':</b> " + str(buf))

          if self.reroll_type == 0: # VEG 2.2.7
             buf = "reroll inits every round (normal)";
          else:
             buf = "keep same inits every round (house rule)";
          self.post_my_msg("<b>[SR4-only] Init Reroll?:</b> " + str(buf))

          if self.ip_order == 0: # VEG 2.2.7
             buf = "1/2/3/4 (normal)";
          elif self.ip_order == 1:
             buf = "3/1/4/2 (Serbitar's house rule)"
          elif self.ip_order == 2:
             buf = "4/1/3/2 (TinkerGnome's house rule)";
          self.post_my_msg("<b>[SR4-only] IP Order:</b> " + str(buf))

          self.post_my_msg("<b>Now Up Message:</b> " + str(self.message_nowup))

       except:
          self.post_syserror("Error reading configuration.",0)

    ###############################################################
    ####    Display Functions
    ###############################################################

    def inits_list(self, public):
       if self.isD20():
          self.inits_list_D20(public)
       elif self.isSR4():
          self.inits_list_SR4(public)
       elif self.isRQ():
          self.inits_list_RQ(public)

    def inits_list_D20(self, public):

        current_count = str(self.init_count)

        if self.sandglass_delay == 0:
           current_sandglass = "off"
        else:
           current_sandglass = str(self.sandglass_delay) + " sec."
           if self.sandglass_status == 1:
              current_sandglass += str(" [ paused ]")

        msg = "<br><br><b>Initiatives (Current Count: " + current_count + "; Sandglass: " + current_sandglass + "):</b><br>"
        for m in v.init_list:

            # dont show public if character (type 0)
            if public and m["type"] == 0 and m["hidden"] == 1:
               continue

            # id in the list appears as 1 to (N+1), in reality it's 0 to N
            id   = v.init_list.index(m)
            idplusone = str(id+1)

            if not self.isEnded() and self.init_listslot == id:
               msg += "<b>"

            # we dont want to show IDs to everyone
            if public and self.hide_id:
               msg += " "
            else:
               msg += " <font color='#ff0000'>" + idplusone + ") :</font>"

            if self.isEffect(id):
                # example
                #   5: (*14) <i>Effect: Tlasco's Bless (4)</i>
                if public and m["hidden"] == 1:
                   duration = "?"
                else:
                   duration = m["duration"]
                msg += " [" + str(m["init"])+"] "
                msg += "<font color='#0000ff'><i>Effect: " + str(m["name"]) + " (" + str(duration) + ")</i>"
            else:
                # example
                #   6: (14) Tlasco
                msg+= " ["+str(m["init"])+"] <font color='#0000ff'>" + str(m["name"])
            if self.init_debug:
               #msg+= " [rank:" + str(m["rank"]) + "; tag: " + str(m["tag"]) + "]</font>"
               msg+= " [rank:" + str(m["rank"]) + "; type: " + str(m["type"]) + "]</font>"
               #msg+= " [rank:" + str(m["rank"]) + "]</font>"
            else:
               msg+= "</font>"

            if not public and m["hidden"] == 1:
               msg += " <i>[H]</i>"

            if not self.isEnded() and self.init_listslot == id:
               msg += "</b>"

            msg += "<br>"
        self.post_my_msg(msg,public)


    def inits_list_SR4(self, public):

        if self.sandglass_delay == 0:
           current_sandglass = "off"
        else:
           current_sandglass = str(self.sandglass_delay) + " sec."
           if self.sandglass_status == 1:
              current_sandglass += str(" [ paused ]")

        if self.ip_order == 0:
            current_ip_order = "1/2/3/4 (normal)"
        elif self.ip_order == 1:
            current_ip_order = "3/1/4/2 (Serbitar's house rule)"
        else:
            current_ip_order = "4/1/3/2 (TinkerGnome's house rule)"
        current_count = str(self.init_count)
        current_pass  = str(self.init_pass)

        msg = "<br><br><b>Initiatives (Current Pass: " + current_pass \
            + "; Current Count: " + current_count + "), Sandglass: " \
            + current_sandglass + ", IP Order: " + current_ip_order \
            + "</b><br>"
        msg += "<table border='1'><tr>&nbsp;<th></th>"

        if self.init_pass==1:
            msg += "<th><b><font color='#ff0000'>Pass 1</font></b></th>"
        else:
            msg += "<th>Pass 1</th>"

        if self.init_pass==2:
            msg += "<th><b><font color='#ff0000'>Pass 2</font></b></th>"
        else:
            msg += "<th>Pass 2</th>"

        if self.init_pass==3:
            msg += "<th><b><font color='#ff0000'>Pass 3</font></b></th>"
        else:
            msg += "<th>Pass 3</th>"

        if self.init_pass==4:
            msg += "<th><b><font color='#ff0000'>Pass 4</font></b></th></tr>"
        else:
            msg += "<th>Pass 4</th></tr>"

        for m in v.init_list:
            # id in the list appears as 1 to (N+1), in reality it's 0 to N
            id   = v.init_list.index(m)
            idplusone = str(id+1)
            # example
            #             | Init Pass 1 | Init Pass 2 | etc...  |          |
            #   ---------------------------
            #   6: Tlasco |     13      |     13      | (blank) |  (blank) |

            # we dont want to show IDs to everyone
            if public and self.hide_id:
               msg += " <tr><th>"
            else:
               msg += " <tr><td><font color='#ff0000'>" + idplusone + ":</font> "

            # bold the current player's name
            if not self.isEnded() and self.init_listslot == id:
               msg += "<b><font color='#0000ff'>" + str(m["name"]) + "</font></b></td>"
            else:
               msg += "<font color='#0000ff'>" + str(m["name"]) + "</font></td>"

            ip = self.ip_order #ip==0 is 1/2/3/4 (normal) - VEG 2.2.7
                               #ip==1 is 3/1/4/2 (Serbitar's house rule)
                               #ip==2 is 4/1/3/2 (TinkerGnome's house rule)
            passes = m["passes"]
            # pass one
            if (ip==0 and passes >= 1) or (ip==1 and passes >= 3) or (ip==2 and passes >= 4):
                msg += "<td align=center>"+str(m["init"]) + "</td>"
            else:
                msg += "<td>&nbsp;</td>"
            # pass two
            if (ip==0 and passes >= 2) or (ip==1 and passes >= 1) or (ip==2 and passes >= 1):
                msg += "<td align=center>"+str(m["init"]) + "</td>"
            else:
                msg += "<td>&nbsp;</td>"
            # pass three
            if (ip==0 and passes >= 3) or (ip==1 and passes >= 4) or (ip==2 and passes >= 3):
                msg += "<td align=center>" + str(m["init"]) + "</td>"
            else:
                msg += "<td>&nbsp;</td>"
            # pass four
            if (ip==0 and passes >= 4) or (ip==1 and passes >= 2) or (ip==2 and passes >= 2):
                msg += "<td align=center>" + str(m["init"]) + "</td>"
            else:
                msg += "<td>&nbsp;</td>"

            msg += "</tr>"

        msg += "</table>"
        self.post_my_msg(msg, public)


    def inits_list_RQ(self, public):
        current_count = str(self.init_count)

        if self.sandglass_delay == 0:
           current_sandglass = "off"
        else:
           current_sandglass = str(self.sandglass_delay) + " sec."
           if self.sandglass_status == 1:
              current_sandglass += str(" [ paused ]")

        msg = "<br><br><b>Initiatives (Current Strike Rank: " + current_count + "; Sandglass: " + current_sandglass + "):</b><br>"
        for m in v.init_list:

            # dont show public if character (type 0)
            if public and m["type"] == 0 and m["hidden"] == 1:
               continue

            # id in the list appears as 1 to (N+1), in reality it's 0 to N
            id   = v.init_list.index(m)
            idplusone = str(id+1)

            if not self.isEnded() and self.init_listslot == id:
               msg += "<b>"

            # we dont want to show IDs to everyone
            if public and self.hide_id:
               msg += " "
            else:
               msg += " <font color='#ff0000'>" + idplusone + ") :</font>"

            if self.isEffect(id):
                # example
                #   5: (*14) <i>Effect: Tlasco's Bless (4)</i>
                if public and m["hidden"] == 1:
                   duration = "?"
                else:
                   duration = m["duration"]
                msg += " [" + str(m["init"])+"] "
                msg += "<font color='#0000ff'><i>Effect: " + str(m["name"]) + " (" + str(duration) + ")</i>"
            else:
                # example
                #   6: (14) Tlasco
                msg+= " ["+str(m["init"])+"]  <font color='#0000ff'>" + str(m["name"])
            if self.init_debug:
               #msg+= " [rank:" + str(m["rank"]) + "; tag: " + str(m["tag"]) + "]</font>"
               msg+= " [rank:" + str(m["rank"]) + "; type: " + str(m["type"]) + "]</font>"
               #msg+= " [rank:" + str(m["rank"]) + "]</font>"
            else:
               msg+= "</font>"

            if not public and m["hidden"] == 1:
               msg += " <i>[H]</i>"

            if not self.isEnded() and self.init_listslot == id:
               msg += "</b>"

            msg += "<br>"
        self.post_my_msg(msg, public)


    def post_now_up(self, id, text):

       #if v.init_list[id]["hidden"] == 0:
       if self.hide_id == 0:
          id_str = "<font color='#000000'><b>" + str(id + 1) + ")</b></font>"
       else:
          id_str = ""

       try:
          id_next = self.getNext(id)
          str_on_deck = ""
          if id_next != -1:
             if self.hide_ondeck != 1:
                 str_on_deck = "<br><i><font color='#000000'>(on deck: [" + str(v.init_list[id_next]["init"]) + "] " + str(v.init_list[id_next]["name"]) + ")</font></i>"

       except Exception, e:
          print str(e)

       self.post_my_msg("<table border=1 width=100% align='center'>\
                     <tr>\
                      <td>" + str(id_str) + " <font color='#ff0000'><b><u>" + str(text)\
                            + "</u></b></font><font color='#0000ff'><b>"\
                            + " <font color='#000000'></b>[" + str(v.init_list[id]["init"]) + "]<b></font> "\
                             + str(v.init_list[id]["name"]) + "</b></font> " + str_on_deck + "\
                      </td>\
                     </tr>\
                    </table>", 1)

    def post_movement(self, id, text):

       #if v.init_list[id]["hidden"] == 0:
       if self.hide_id == 0:
          id_str = "<font color='#000000'><b>" + str(id + 1) + ")</b></font>"
       else:
          id_str = ""

       self.post_my_msg("<table border=1 width=100% align='center'>\
                     <tr>\
                      <td>" + str(id_str) + " <font color='#0000ff'><b><i>" + str(text)\
                            + "</i></b></font><font color='#0000ff'><b>"\
                            + " <font color='#000000'></b>[" + str(v.init_list[id]["init"]) + "]<b></font> "\
                             + str(v.init_list[id]["name"]) + "</b></font> \
                      </td>\
                     </tr>\
                    </table>", 1)

    def post_effect(self, id, text):

       if self.hide_id == 0:
          id_str = "<font color='#000000'><b>" + str(id + 1) + ")</b></font>"
       else:
          id_str = ""

       if v.init_list[id]["hidden"] == 1:
          rounds_left = "?"
       else:
          rounds_left = self.getRoundsLeftInEffect(id)

       if(self.getRoundsLeftInEffect(id) > 0):
          self.post_my_msg("<table border=1 width=100% align='center'>\
                     <tr>\
                      <td>" + str(id_str) + " <font color='#0000ff'><b><i>" + str(text)\
                             + "</i></b></font><font color='#0000ff'>"\
                             + " <font color='#000000'>[" + str(v.init_list[id]["init"]) + "]</font> <i>"\
                             + str(v.init_list[id]["name"]) + "</i></font> : <b>" + str(rounds_left) + "</b> round(s) remaining.\
                      </td>\
                     </tr>\
                    </table>", 1)
       else:
          self.post_my_msg("<table border=1 width=100% align='center'>\
                     <tr>\
                      <td>" + str(id_str) + " <font color='#0000ff'><b><i>" + str(text)\
                             + "</i></b></font><i>"\
                             + " [" + str(v.init_list[id]["init"]) + "] <font color='#0000ff'>"\
                             + str(v.init_list[id]["name"]) + "</font></i>\
                      </td>\
                     </tr>\
                    </table>", 1)


    def post_my_msg(self, msg,send=0):
        tmp = self.init_recording

        # have to disable the tool in order to post or else you get a clone
        self.init_recording = 0
        self.chat.Post(msg,send)

        self.init_recording = tmp


    def post_syserror(self, msg, send=0):
       self.post_my_msg("<font color='#ff0000'><b><i>" + msg + "</i></b></font>", send)


    def post_sysmsg(self, msg,send=0):
       self.post_my_msg("<b>" + msg + "</b>", send)


    def toggle_hidden(self, id):
       try:
          #print "id : " + str(id)
          v.init_list[id]["hidden"] = not v.init_list[id]["hidden"]
          if v.init_list[id]["hidden"] == 1:
             tmp = "hidden"
          else:
             tmp = "visible"
          self.post_sysmsg(str(v.init_list[id]["name"]) + " now " + tmp + ".")

       except:
          self.post_syserror("Invalid format. Correct command is: /togglehidden init_#")

    ###############################################################
    ####    Conditional + Other Functions
    ###############################################################

    def check_version(self):
       if(int(replace(orpg.orpg_version.VERSION, ".", "")) < int(replace(self.orpg_min_version, ".", ""))):
          self.post_sysmsg("<br><font color='#ff0000'>WARNING</font>: You are currently using OpenRPG " + str(orpg.orpg_version.VERSION) + " but you need OpenRPG " + str(self.orpg_min_version) + " or greater to run the Initiative Tool " + str(self.version) + "<br>Use it at your own risk!</b><br>")

    def isD20(self):
        if self.init_system == "D20":
            return 1
        else:
            return 0

    def isSR4(self):
        if self.init_system == "SR4":
            return 1
        else:
            return 0

    def isRQ(self):
        if self.init_system == "RQ":
            return 1
        else:
            return 0

    def isEnded(self):
       if self.init_end == 0:
          return 1
       else:
          return 0

    def getFirst(self):
       return(0)

    def getLast(self):
       return(len(v.init_list)-1)

    def isEffect(self, id):
        # if it's type 1, then it's an effect
        try:
            if (self.isD20() or self.isRQ()) and v.init_list[id]["type"] == 1:
                return 1
            else:
                return 0
        except:
            return 0

    def getRoundsLeftInEffect(self, id):
        rounds_left = v.init_list[id]["duration"]
        return rounds_left

    def isMovement(self, id): # sr4 only, used to spam movement-only characters
        try:                  # in passes where they receive no actions
            passes = v.init_list[id]["passes"]
            if self.ip_order == 0: # Normal 1/2/3/4 --- VEG 2.2.7
                if passes < self.init_pass:
                    return 1
                else:
                    return 0
            elif self.ip_order == 1: # Serbitar's 3/1/4/2 --- VEG 2.2.7
                if (self.init_pass == 1) and (passes < 3):
                    return 1
                elif (self.init_pass == 2) and (passes < 1):
                    return 1
                elif (self.init_pass == 3) and (passes < 4):
                    return 1
                elif (self.init_pass == 4) and (passes < 2):
                    return 1
                else:
                    return 0
            elif self.ip_order == 2: # TinkerGnome's 4/1/3/2 --- VEG 2.2.7
                if (self.init_pass == 1) and (passes < 4):
                    return 1
                elif (self.init_pass == 2) and (passes < 1):
                    return 1
                elif (self.init_pass == 3) and (passes < 3):
                    return 1
                elif (self.init_pass == 4) and (passes < 2):
                    return 1
                else:
                    return 0
        except:
            return 0

    def sharesInit(self,id):
        try:
            if v.init_list[id]["init"] == v.init_list[self.init_listslot]["init"]:
                return 1
            else:
                return 0
        except: # last init will be an error, don't start new round yet
            return 0

    # get the id of the next (non effect) non-hidden character after the given id
    # return -1 : no character is next
    def getNext(self, id):
       lst_size = len(v.init_list)

       # list empty
       if lst_size < 2:
          return(-1)

       lst = []
       id_found = -1

       # if we'r at the last init, the next one is at the beginning of the list
       if self.isLast(id):
          for m in v.init_list:
             id_m = v.init_list.index(m)
             if self.isHidden(id_m) or self.isEffect(id_m):
                pass
             else:
                id_found = id_m
                break;
       else:
          try:
             for id_m in range(id+1, self.getLast()+1):
                if self.isHidden(id_m) or self.isEffect(id_m):
                   pass
                else:
                   id_found = id_m
                   break;

          except Exception, e:
             return(-1)

          # maybe we haven't found yet, must search at the beginning of the list
          if id_found == -1 and not self.isFirst(id):
             for id_m in range(0, id):
                if self.isHidden(id_m) or self.isEffect(id_m):
                   pass
                else:
                   id_found = id_m
                   break;

       if id_found != id:
          return(id_found)
       else:
          return(-1)

    def isHidden(self, id):
       try:
          if v.init_list[id]["hidden"] == 1:
             return(1)
          else:
             return(0)

       except:
             return(0)

    def isFirst(self, id):
       if id == 0:
          return 1
       else:
          return 0

    def isLast(self, id):
       if id == (len(v.init_list)-1):
          return 1
       else:
          return 0

    def get_next_rank(self, init):
       # when adding/changing an object, this function is used to get a unique rank of this init count
       # new object are added at the end of an init count, so we need a 'rank' lower than the
       # other object of the same init count.
       rank = 0;
       for m in v.init_list:
          if m["init"] == init:
             x = m["rank"] - 1
             if rank > x:
                rank = x
       return rank

    def get_unique_tag(self, name):
        m = hashlib.md5()
        m.update(str(random.random()) + str(name))
        return m.hexdigest()

### VEG 2.2.6
### Init GUI stuff below

    def CMD_initgui(self, cmdargs):
        self.frame = InitToolFrame(NULL, -1, "Initiative Tool GUI")
        self.frame.Show(true)

class InitToolFrame(wx.Frame):
    def __init__(self, parent, ID, title):
        wx.Frame.__init__(self, parent, ID, title, size=(400, 300))

        self.panel = wx.Panel(self,-1) #, style=wx.SUNKEN_BORDER)

        #self.panel.SetBackgroundColour("RED")

        self.x_id = 5
        self.x_name = 25
        self.x_init = 200
        self.x_change = 225
        self.x_delete = 275
        self.y = 0
        b = 0

        wx.StaticText ( self.panel, -1, "ID", (self.x_id, self.y) )
        wx.StaticText ( self.panel, -1, "Name", (self.x_name, self.y) )
        wx.StaticText ( self.panel, -1, "Init#", (self.x_init, self.y) )
        self.y+=20

        var_ID=0
        var_Name=0
        var_Init=0

        for m in v.init_list:
            var_ID = str(v.init_list.index(m)+1) + ")"
            var_Name = self.strip_html(m["name"])
            var_Init = str(m["init"])

            wx.StaticText ( self.panel, -1, var_ID, (self.x_id, self.y) )
            wx.StaticText ( self.panel, -1, var_Name, (self.x_name, self.y) )
            wx.TextCtrl ( self.panel, -1, var_Init, (self.x_init, self.y), (20,20), wx.TE_READONLY)
            wx.Button(self.panel, -1, "Change", (self.x_change, self.y), (50,20) )
            wx.Button(self.panel, -1, "Delete", (self.x_delete, self.y), (50,20) )
            self.y+=20

        #for i in range(0,4):
        #    if i == 0:
        #        var_ID   = str(0)
        #        var_Name = "Hignar"
        #        var_Init = str(14)
        #    elif i == 1:
        #        var_ID   = str(1)
        #        var_Name = "Aiur"
        #        var_Init = str(12)
        #    elif i == 2:
        #        var_ID   = str(2)
        #        var_Name = "Effect: Tlasco's Bless"
        #        var_Init = str(4)
        #    elif i == 3:
        #        var_ID   = str(3)
        #        var_Name = "Tlasco"
        #        var_Init = str(3)
        #    wxStaticText ( self.panel, -1, var_ID, (self.x_id, self.y) )
        #    wxStaticText ( self.panel, -1, var_Name, (self.x_name, self.y) )
        #    wxStaticText ( self.panel, -1, var_Init, (self.x_init, self.y) )
        #    wxButton(self.panel, -1, "Change", (self.x_change, self.y), (50,20) )
        #    wxButton(self.panel, -1, "Delete", (self.x_delete, self.y), (50,20) )
        #    self.y+=20

    def strip_html(self, text):
        finished = 0
        while not finished:
            finished = 1
            # check if there is an open tag left
            start = text.find("<")
            if start >= 0:
                # if there is, check if the tag gets closed
                stop = text[start:].find(">")
                if stop >= 0:
                    # if it does, strip it, and continue loop
                    text = text[:start] + text[start+stop+1:]
                    finished = 0
        return text
