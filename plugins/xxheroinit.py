import os
import orpg.pluginhandler

class Plugin(orpg.pluginhandler.PluginHandler):
    # Initialization subroutine.
    #
    # !self : instance of self
    # !openrpg : instance of the the base openrpg control
    def __init__(self, plugindb, parent):
        orpg.pluginhandler.PluginHandler.__init__(self, plugindb, parent)

        # The Following code should be edited to contain the proper information
        self.name = 'Hero Turn Tool'
        self.author = 'Heroman, based on xxxinit.py'
        self.help = """This is the Hero Games turn turn. It is a bit more complex than other games."""


    def plugin_enabled(self):
        #You can add new /commands like
        # self.plugin_addcommand(cmd, function, helptext)
        self.plugin_addcommand('/hinit', self.on_hinit, '- Toggle Init Recording on or off')
        self.plugin_addcommand('/hhelp', self.on_hhelp, '- List all of the Hero Init Commands')
        self.plugin_addcommand('/hstart', self.on_hstart, '- Start the Hero Init Tool', False)
        self.plugin_addcommand('/hact', self.on_hact, '- Start the Hero Init Tool', False)
        self.plugin_addcommand('/hseg', self.on_hseg, '- Start the Hero Init Tool', False)
        self.plugin_addcommand('/hdex', self.on_hdex, '- Start the Hero Init Tool', False)
        self.plugin_addcommand('/hclear', self.on_hclear, '- Start the Hero Init Tool', False)
        self.plugin_addcommand('/hadd', self.on_hadd, '- Start the Hero Init Tool', False)
        self.plugin_addcommand('/hdel', self.on_hdel, '- Start the Hero Init Tool', False)
        self.plugin_addcommand('/hown', self.on_hown, '- Start the Hero Init Tool', False)
        self.plugin_addcommand('/hlist', self.on_hlist, '- Start the Hero Init Tool', False)
        self.plugin_addcommand('/hsort', self.on_hsort, '- Start the Hero Init Tool', False)
        self.plugin_addcommand('/hrun', self.on_hrun, '- Start the Hero Init Tool', False)
        self.plugin_addcommand('/hchange', self.on_hchange, '- Start the Hero Init Tool', False)
        self.plugin_addcommand('/hset', self.on_hset, '- Start the Hero Init Tool', False)
        self.plugin_addcommand('/hchange', self.on_hchange, '- Start the Hero Init Tool', False)

        #If you want your plugin to have more then one way to call the same function you can
        #use self.plugin_commandalias(alias name, command name)
        #You can also make shortcut commands like the following
        self.plugin_commandalias('/hlow', '/hsort low', False)
        self.plugin_commandalias('/hsortlow', '/hsort low', False)
        self.plugin_commandalias('/hhigh', '/hsort high', False)
        self.plugin_commandalias('/hsorthigh', '/hsort high', False)
        self.plugin_commandalias('/hreverse', '/hsort high', False)
        self.plugin_commandalias('/hgo', '/hrun', False)

        #This is where you set any variables that need to be initalized when your plugin starts
        self.toggle = True
        self.init_list = []
        self.backup_list = []
        self.dexterity = 99
        self.segment = 12
        self.state_strings = ["0 Phase","1/2 Phase","Full Phase","Stunned","Not Gone", "Held Full", "Held Half", "Abort"]

    def plugin_disabled(self):
        #Here you need to remove any commands you added, and anything else you want to happen when you disable the plugin
        #such as closing windows created by the plugin
        self.plugin_removecmd('/test')
        self.plugin_removecmd('/example')

        #This is the command to delete a message handler
        self.plugin_delete_msg_handler('xxblank')

        #This is how you should destroy a frame when the plugin is disabled
        #This same method should be used in close_module as well
        try:
            self.frame.Destroy()
        except:
            pass

    def plugin_incoming_msg(self, text, type, name, player):
        #This is called whenever a message from someone else is received, no matter
        #what type of message it is.
        #The text variable is the text of the message. If the type is a regular
        #message, it is already formatted. Otherwise, it's not.
        #The type variable is an integer which tells you the type: 1=chat, 2=whisper
        #3=emote, 4=info, and 5=system.
        #The name variable is the name of the player who sent you the message.
        #The player variable contains lots of info about the player sending the
        #message, including name, ID#, and currently-set role.
        #Uncomment the following line to see the format for the player variable.
        #print player

        if self.toggle:
            if text.lower().find("heroinit") != -1:
                command = text[text.rfind("(")+1:text.rfind(")")]
                self.process_user(command, player)
        return text, type, name

    #Chat Commands
    def on_hinit(self, cmdargs):
        self.toggle = not self.toggle

        if self.toggle:
            self.chat.SystemPost("Init recording on.  Enter your info")
        else:
            self.chat.SystemPost("Init recording off")

    def on_hhelp(self, cmdargs):
            self.chat.InfoPost("Commands:<br>/hclear : Clears out list<br>" +
                        "/hstart : Sets you to segment 12, highest dex<br>" +
                        "/hgo : Proceed to the next DEX/segment<br>" +
                        "/hact <i>#</i> (full|half|abort|stunned)<br>" +
                        "/hseg SEGNO : Set segment to SEGNO<br>" +
                        "/hdex DEXNO : Set dex to DEXNO<br>" +
                        "/hadd DEX SPD NAME : Adds to the list<br>" +
                        "/hdel # : Delete character #<br>" +
                        "/hown # playerid : Change ownership of PC # to playerid<br>" +
                        "/hclear : Clears out player list<br>" +
                        "/hchange # NEWDEX NEWSPD : Change PC # to have Dex NEWDEX and SPD NEWSPD<br>" +
                        "/hset list_# state : Change player's state (state:" + self.statelist() + ")")

    def on_hstart(self, cmdargs):
        self.dexterity = self.highestdex()
        self.segment = 12

        for player in self.init_list:
            player[3] = 4
            if player[0] == self.dexterity:
                player[3] == 2

        self.chat.Post("Combat Starting.  ")
        self.call_time()

    def on_hact(self, cmdargs):
        cmds = cmdargs.split(None)

        if len(cmds) == 1:
            msg = self.do_action(-1, -1, cmds[0])
        elif len(cmds) == 2:
            msg = self.do_action(-1, int(cmds[0]), cmds[1])
        else:
            msg = "Error in command. See format with hero init"

        self.chat.InfoPost(msg)

    def on_hseg(self, cmdargs):
        cmds = cmdargs.split(None, 3)

        try:
            new_seg = int(cmds[0])
            self.segment = new_seg
            self.call_time()
        except:
            self.chat.SystemPost("Invalid format.  correct command is: /hseg SEGMENT#")

    def on_hdex(self, cmdargs):
        cmds = cmdargs.split(None, 3)

        try:
            new_dex = int(cmds[0])
            self.dexterity = new_dex
            self.call_time()
        except:
            self.chat.SystemPost("Invalid format.  correct command is: /hdex DEX#")

    def on_hclear(self, cmdargs):
        self.init_list = []
        self.backup_list = []
        self.dexterity = 99
        self.segment = 12
        self.chat.Post("<hr><font color='#ff0000'>New Initiative</font><br><font color='#0000ff'>Set new Initiatives</font>", True)

    def on_hadd(self, cmdargs):
        cmds = cmdargs.split(None, 3)
        try:
            if len(cmds) == 3:
                new_dex = int(txt[0])
                new_spd = int(txt[1])
                self.init_list.append([new_dex, new_spd, cmds[2], 0, -1])
                self.backup_list.append([new_dex, new_spd, cmds[2], 0, -1])
                self.list_inits()
            else:
                self.chat.SystemPost("Invalid format.  correct command is: /hadd dex spd description (" + str(len(cmds)) + " arguments give)")

        except:
            self.chat.SystemPost("Invalid format.  correct command is: /hadd dex spd description")

    def on_hdel(self, cmdargs):
        try:
            cmds = cmdargs.split(None, 1)
            self.init_list.remove(int(cmds[0]))
            self.backup_list.remove(int(cmds[0]))
            self.list_inits()
        except:
            self.chat.SystemPost("Invalid format.  correct command is: /del list_number")

    def on_hown(self, cmdargs):
        try:
            cmds = cmdargs.split(None)
            player = self.init_list[int(cmds[0])]
            player[4] = int(cmds[1])
            self.chat.InfoPost("Character " + player[2] + "(" + int(cmds[0]) + ") is now owned by ID " + int(cmds[1]))
        except:
            self.chat.SystemPost("Invalid format.  correct command is: /hown # playerid")

    def on_hlist(self, cmdargs):
        self.list_inits()

    def on_hsort(self, cmdargs):
        self.init_list.sort()
        self.backup_list.sort()

        if cmdargs == "high":
            self.init_list.reverse()
            self.backup_list.reverse()

        self.list_inits()

    def on_hrun(self, cmdargs):
        advance = True
        nextlowest = 0
        heldactions = False

        for player in self.init_list:
            if self.actson(player[1]. self.segment):
                if player[3] == 5 or player[3] == 6:
                    heltactions = True
                continue

            if player[3] == 1 or player[3] == 2:
                self.chat.InfoPost("Hero " + player[2] + " needs to act before we advance DEX")
                advance = False

            elif player[3] == 3 or player[3] == 4 or player[3] == 7:
                if player[0] > nextlowest:
                    nextlowest = player[0]

            elif player[3] == 5 or player[3] == 6:
                heltactions = True

        if not advance:
            return

        advanceseg = False

        if nextlowest == 0 and self.dexterity != 0:
            if heldactions or self.segment == 12:
                msg = "End of Segment " + str(self.segment) + "."
                if heldactions:
                    msg += " There are held actions."

                msg += "  Issue command again to advance to next segment."

                self.chat.InfoPost(msg)
                self.dexterity = 0
                return
            else:
                advanceseg = True
        elif nextlowest == 0 and self.dexterify == 0:
            advanceseg = True

        if advanceseg:
            self.dexterity = nextlowest
            for player in self.init_list:
                if player[0] == self.dexterity:
                    if player[3] == 3 or player[3] == 7:
                        player[3] = 0
                    elif player[3] == 4:
                        player[3] = 2
        else:
            nextsegment = 0
            while nextsegment == 0:
                self.segment += 1
                if self.segment == 13:
                    self.segment = 1

                elif self.segment == 12:
                    nextsegment = 12
                    break

                for player in self.init_list:
                    if self.actson(player[1], self.segment):
                        if player[3] == 0 or player[3] == 3 or player[3] == 7:
                            nextsegment = self.segment

                    if player[3] == 5 or player[3] == 6:
                        nextsegment = self.segment

            self.dexterity = self.highestdex()
            for player in self.init_list:
                heldactions = False
                if self.actson(player[1], self.segment):
                    if player[3] != 3 and player[3] != 7:
                        player[3] = 4

                    if player[0] == self.dexterity:
                        if player[3] == 3:
                            self.chat.InfoPost(player[2] + " unstuns.")
                            player[3] = 0
                        elif player[3] == 7:
                            self.chat.InfoPost(player[2] + " recovers from the abort")
                            player[3] = 0
                        else:
                            player[3] = 2

                    if player[3] == 5 or player[3] == 6 and self.dexterity == 0:
                        self.chat.InfoPost("There are held actions. Issue command again to advance to next segment.")
        self.call_time()

    def on_hchange(self, cmdargs):
        try:
            cmds = cmdargs.split()
            self.init_list[int(cmds[0])][0] = cmds[1]
            self.init_list[int(cmds[0])][1] = cmds[2]
            self.backup_list[int(cmds[0])][0] = cmds[1]
            self.backup_list[int(cmds[0])][1] = cmds[2]
            self.list_inits()
        except:
            self.chat.SystemPost('Invalid format.  correct command is: /hchange list_# new_dex new_spd (example: /hchange 1 18 4)')

    def on_hset(self, cmdargs):
        try:
            cmds = cmdargs.split()
            self.init_list[int(cmds[0])][3] = cmds[1]
            self.backup_list[int(cmds[0])][3] = cmds[1]
            self.list_inits()
        except:
            msg = "Invalid format.  correct command is: /hset list_# state (state:" + self.statelist() + ")"
            self.chat.InfoPost(msg)

    #Other Methods
    def statelist(self):
        msg = ""
        stateindex = 0
        for state in self.state_strings:
            if stateindex != 0:
                msg += ", "
            msg += str(stateindex) + "=" + state
            stateindex += 1
        return msg

    def is_index(self, value):
        try:
            if value[:1] == "+":
                offset = 1
            return True
        except:
            return False

    def actson(self, spd, segment):
        speeds=[[0,0,0,0,0,0,0,0,0,0,0,1],
                [0,0,0,0,0,1,0,0,0,0,0,1],
                [0,0,0,1,0,0,0,1,0,0,0,1],
                [0,0,1,0,0,1,0,0,1,0,0,1],
                [0,0,1,0,1,0,0,1,0,1,0,1],
                [0,1,0,1,0,1,0,1,0,1,0,1],
                [0,1,0,1,0,1,1,0,1,0,1,1],
                [0,1,1,0,1,1,0,1,1,0,1,1],
                [0,1,1,1,0,1,1,1,0,1,1,1],
                [0,1,1,1,1,1,0,1,1,1,1,1],
                [0,1,1,1,1,1,1,1,1,1,1,1],
                [1,1,1,1,1,1,1,1,1,1,1,1]]

        if spd < 1 or spd > 12:
            return False

        if speeds[spd-1][segment-1] == 1:
            return True

        return False

    def highestdex(self):
        dex = 0
        for player in self.init_list:
            if self.actson(player[1], self.segment) and player[0] > dex:
                dex = player[0]
        return dex

    def do_action(self, playerid, index, action):
        if index == -1:
            count = 1
            for player in self.init_list:
                if player[4] == playerid:
                    index = count
                count += 1

        if index == -1:
            return "You do not have any players in the combat list"

        index -= 1
        player = self.init_list[index]
        if playerid != -1 and playerid != player[4]:
            return "You do not own that player."

        # You can only perform a full action if you have a full or held full
        if action == "full":
            if player[3] != 2 and player[3] != 5:
                msg = player[2] + " cannot perform a full action."
            else:
                player[3] = 0
                msg = player[2] + " performs a full action."
        elif action == "half":
            if player[3] != 1 and player[3] != 2 and player[3] != 5 and player[3] != 6:
                msg = player[2] + " cannot perform a half action."
            else:
                if player[3] == 1 or player[3] == 6:
                    player[3] = 0
                    msg = player[2] + " performs a half action."
                else:
                    player[3] = 1
                    msg = player[2] + " performs a half action (half remaining)"
        elif action == "hold":
            if player[3] != 1 and player[3] != 2:
                msg = player[2] + " cannot hold an action."
            else:
                if player[3] == 2:
                    player[3] = 5
                    msg = player[2] + " holding a full action."
                else:
                    player[3] = 6
                    msg = player[2] + " holding a half action."
        elif action == "stunned":
            player[3] = 3
            msg = player[2] + " stunned!"
        elif action == "abort":
            # abort if full/half/not gone/held.  Those just lose this seg action
            if player[3] == 1 or player[3] == 2 or player[3] == 4 or player[3] == 5 or player[3] == 6:
                player[3] = 0
                msg = player[2] + " aborts!"
            # if you have 0 remaining and did not act this seg, regular abort
            elif player[3] == 0 and not self.actson(player[1], self.segment):
                player[3] = 7
                msg = player[2] + " aborts!"
            else:
                msg = player[2] + " cannot abort yet."
        else:
            msg = "Unknown command."

        return msg

    def list_inits(self, player=0, send=False):
        msg = "Combat Turn:<br>"
        msg += "<table border=1 cellspacing=1 cellpadding=1><tr><th><th></th></th><th></th><th></th><th></th><th></th><th colspan=12>Segments</th></tr>"
        msg += "<tr><th>#</th><th>Owner</th><th>Name</th><th>Spd</th><th>Dex</th><th>State</th>"
        for x in xrange(1,13):
            msg += "<th>" + str(x) + "</th>"
        msg += "</tr>"
        count=1
        for m in self.init_list:
            msg += "<tr><td align=center>"+str(count)+"</td>"
            if m[4]==-1:
                msg += "<td><font color=red>GM</font></td>"
            else:
                msg += "<td>" + m[4] + "</td>"
            msg += "<td><font color='#0000ff'>" + m[2] + "</font></td>"
            msg += "<td align=center><font color='#0000ff'>" + str(m[1]) + "</font></td>"
            msg += "<td align=center><font color='#0000ff'>" + str(m[0]) + "</font></td>"
            msg +="<td>" + self.state_strings[m[3]] + "</td>"

            for segment in xrange(1,13):
                if self.actson(m[1],segment):
                    msg += "<td align=center>" + str(m[0]) + "</td>"
                else:
                    msg += "<td></td>"
            msg += "</tr>"
            count += 1
        msg += "</table><br>"

        msg += "It is currently Segment " + str(v.segment) + ", DEX " + str(v.dexterity) + "<br>"

        if send and player != 0:
            chat.whisper_to_players(msg, [player])
        else:
            self.chat.InfoPost(msg)

    def call_time(self):
        plist = ""
        msg = "Segment is now " + str(self.segment) + ", DEX " + str(self.dexterity)
        for player in self.init_list:
            if player[3] == 1 or player[3] == 2 or player[3] == 5 or player[3] == 6:
                if plist != "":
                    plist += ", "
                plist += player[2] + "(" + self.state_strings[player[3]] + ")"
        if plist != "":
            msg += ": " + plist
        self.chat.Post(msg, True)

    def process_user(self, command, player):
        if command == "hadd":
            txt = command.split(None, 3)
            try:
                if len(txt) == 4:
                    new_dex = int(txt[1])
                    new_spd = int(txt[2])
                    self.init_list.append([new_dex, new_spd, txt[3], 0, player[2]])
                    self.backup_list.append([new_dex, new_spd, txt[3], 0, player[2]])
                    msg = "Character " + txt[3] + " added to initiative."
                else:
                    msg = "Error in command.  See format with heroinit"
            except:
                msg = "Error in command.  See format with heroinit"

            self.chat.whisper_to_players(msg, [player[2]])

        elif command == "hact":
            txt = command.split(None)
            if len(txt) == 2:
                index = -1
                action = txt[1]
                msg = self.do_action(player[2], index, action)
            elif len(txt) == 3:
                index = int(txt[1])
                action = txt[2]
                msg = self.do_action(player[2], index, action)
            else:
                msg = "Error in command.  See format with heroinit"

            self.chat.whisper_to_players(msg, [player[2]])

        elif command == "hlist":
            self.list_inits(player[2], True)

        else:
            msg = "Commands:<br>heroinit (hadd DEX SPEED CHARACTERNAME) : add character CHARACTERNAME with dex DEX and speed SPD to initiative list<br>"
            msg += " Example:  heroinit (hadd 18 4 Joey)<br>"
            msg += "heroinit (hact # (full|half|hold|stunned|abort) : Have character # perform an action.  # is the number from hlist.  If ommited, uses first owned character<br>"
            msg += " Example:  heroinit (hact 1 full)   : Make character index 1 perform a full action.<br>"
            msg += " Example:  heroinit (hact full)     : Have your first owned character perform a full action<br>"

            self.chat.whisper_to_players(msg, [player[2]])
