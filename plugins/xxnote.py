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
        self.name = 'Quick Notes'
        self.author = 'Dj Gilcrease'
        self.help = "This plugin lets you take quick notes on a subject"
        self.notes = {}


    def plugin_enabled(self):
        self.notes = self.plugindb.GetDict("xxnote", "notes", {})

        self.plugin_addcommand('/newnote', self.on_newnote, '{Subject} - Will create a new note subject')
        self.plugin_addcommand('/appendnote', self.on_appendnote, '{Subject}={Note} - Will append a note to {Subject}')
        self.plugin_addcommand('/delnote', self.on_delnote, '{Subject}={Note_id}|all - Will delete {Note_id} from {Subject} or will delete the subject compleatly')
        self.plugin_addcommand('/editnote', self.on_editnote, '{Subject}={Note_id} {Note} - Will replace {Note_id} with {Note} for {Subject}')
        self.plugin_addcommand('/clearnotes', self.on_clearnotes, '- Will clear all of your notes')
        self.plugin_addcommand('/listnotes', self.on_listnotes, '- Will list all of the note subjects you have')
        self.plugin_addcommand('/viewnote', self.on_viewnote, '{Subject} - Will display the notes you have for {Subject}')
        self.plugin_addcommand('/notetonode', self.on_notetonode, '{Subject} - Will create a text node containing your notes for {Subject}')
        self.plugin_addcommand('/notehelp', self.on_notehelp, '- Will Display the help for each command of this plugin!')


    def plugin_disabled(self):
        self.plugin_removecmd('/newnote')
        self.plugin_removecmd('/appendnote')
        self.plugin_removecmd('/editnote')
        self.plugin_removecmd('/delnote')
        self.plugin_removecmd('/listnotes')
        self.plugin_removecmd('/viewnote')
        self.plugin_removecmd('/notetonode')
        self.plugin_removecmd('/notehelp')
        self.plugin_removecmd('/clearnotes')

    def on_newnote(self, cmdargs):
        if len(cmdargs) == 0:
            self.on_notehelp('')
            return

        subject = cmdargs
        if not self.notes.has_key(subject):
            self.notes[subject] = []
            self.plugindb.SetDict("xxnote", "notes", self.notes)
            self.chat.InfoPost("Created new note for " + subject)
        else:
            self.chat.InfoPost("You already have a note with the subject " + subject)

    def on_appendnote(self, cmdargs):
        args = cmdargs.split("=",-1)
        if len(args) < 2:
            self.on_notehelp('')
            return

        subject = args[0]
        note = args[1]
        if not self.notes.has_key(subject):
            self.notes[subject] = []
            self.notes[subject].append(note)
            self.plugindb.SetDict("xxnote", "notes", self.notes)
            self.chat.InfoPost("Created new note for " + subject)
        else:
            self.notes[subject].append(note)
            self.plugindb.SetDict("xxnote", "notes", self.notes)
            self.chat.InfoPost("Appended <i>" + note + "</i> to <b>" + subject + "</b>")

        self.on_viewnote(subject)

    def on_editnote(self, cmdargs):
        args = cmdargs.split("=",-1)
        if len(args) < 2:
            self.on_notehelp('')
            return

        s = args[1].find(" ")
        subject = args[0]
        note_id = int(args[1][:s])
        note = args[1][s:]
        if not self.notes.has_key(subject):
            self.notes[subject] = []
            self.notes[subject].append(note)
            self.plugindb.SetDict("xxnote", "notes", self.notes)
            self.chat.InfoPost("Created new note for " + subject)
        else:
            self.notes[subject][note_id] = note
            self.plugindb.SetDict("xxnote", "notes", self.notes)
            self.chat.InfoPost("Edited <i>" + str(note_id) + ': ' + note + "</i> to <b>" + subject + "</b>")

        self.on_viewnote(subject)

    def on_delnote(self, cmdargs):
        args = cmdargs.split("=",-1)
        if len(args) < 2:
            self.on_notehelp('')
            return

        subject = args[0]
        noteid = args[1]

        if noteid == 'all':
            del self.notes[subject]
            self.plugindb.SetDict("xxnote", "notes", self.notes)
            self.chat.InfoPost("Removed subject " + subject)
        else:
            del self.notes[subject][int(noteid)]
            self.plugindb.SetDict("xxnote", "notes", self.notes)
            self.chat.InfoPost("Removed note " + noteid + " from subject " + subject)
            self.on_viewnote(subject)

    def on_clearnotes(self, cmdargs):
        self.notes = {}
        self.plugindb.SetDict("xxnote", "notes", self.notes)
        self.chat.InfoPost("Cleared all of your notes")

    def on_listnotes(self, cmdargs):
        if len(self.notes) == 0:
            self.chat.InfoPost("You have no notes at this time, use /newnote to create one")
            return
        self.chat.InfoPost("The subjects you have notes on are:")
        for subject in self.notes.keys():
            self.chat.InfoPost("** " + subject)

    def on_viewnote(self, cmdargs):
        if len(cmdargs) == 0:
            self.on_notehelp('')
            return

        subject = cmdargs
        if self.notes.has_key(subject):
            msg = '<table bgcolor="#cccccc"><tr><td colspan="2"><b><font color="#000000">Notes for '
            msg += subject
            msg += ':</font></b></td></tr><tr><td width="10">ID</td><td>Note Text</td></tr>'
            noteid = 0
            for n in self.notes[subject]:
                msg += '<tr><td width="10"><font color="#000000">'
                msg += str(noteid)
                msg += '</font></td>'
                msg += '<td><font color="#000000">'
                msg += n
                msg += '</font></td></tr>'
                noteid += 1

            msg += '</table>'
            self.chat.InfoPost(msg)
        else:
            self.chat.InfoPost("You have no notes for " + subject)

    def on_notetonode(self, cmdargs):
        if len(cmdargs) == 0:
            self.on_notehelp('')
            return

        subject = cmdargs
        if self.notes.has_key(subject):
            node = '<nodehandler class="textctrl_handler" icon="note" module="forms" name="'
            node += subject
            node += '" version="1.0"><text multiline="1" send_button="1">'
            for note in self.notes[subject]:
                node += note + "\n"
            node += '</text></nodehandler>'
            self.gametree.insert_xml(node)
        else:
            self.chat.InfoPost("You have no notes for " + subject)

    def on_notehelp(self, cmdargs):
        self.chat.InfoPost('/newnote ' + self.cmdlist['/newnote']['help'])
        self.chat.InfoPost('/appendnote ' + self.cmdlist['/appendnote']['help'])
        self.chat.InfoPost('/delnote ' + self.cmdlist['/delnote']['help'])
        self.chat.InfoPost('/listnotes ' + self.cmdlist['/listnotes']['help'])
        self.chat.InfoPost('/clearnotes ' + self.cmdlist['/clearnotes']['help'])
        self.chat.InfoPost('/notetonode ' + self.cmdlist['/notetonode']['help'])
        self.chat.InfoPost('/viewnote ' + self.cmdlist['/viewnote']['help'])
