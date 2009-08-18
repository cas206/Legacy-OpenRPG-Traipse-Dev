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
# File: scriptkit.py
# Author: Ted Berg
# Maintainer:
# Version:
#   $Id: scriptkit.py,v 1.15 2006/11/04 21:24:22 digitalxero Exp $
#
# Description: Class that contains convenience methods for various operations.  Was created with the purpose
#       of exposing a simple API to users of an as yet uncreated scripting interface.
#


import time
from orpg.orpg_windows import *
from orpg.orpg_xml import *
from orpg.orpg_wx import *
import orpg.chat.chat_msg

class scriptkit:
    def __init__(self):
        """Simple constructor.  It currently only assigns the openrpg reference to a local variable.
        <ul>
            <li>openrpg - a reference to the application openrpg object.
        </ul>
        """
        self.chat = component.get( 'chat' )
        self.map = component.get( 'map' )
        self.settings = component.get( 'settings' )
        self.session = component.get('session')
        self.xml = component.get('xml')

    def addMiniatureToMap( self, min_label, min_url, unique=0 ):
        """Adds a new miniature icon to the map.  Miniature <em>will</em> be labeled unless autolabel is
        turned off on the map <em>and</em> the min_label field is blank.  Miniature will be numbered unless
        the 'unique' argument evaluates to True ( i.e. nonzero or a non-empty string ).
        <ul>
            <li>min_label - text string to be used as a label for the miniature
            <li>min_url - the URL for the image to be displayed on the map
            <li>unique - the mini will be numbered if this evaluates to False.
        </ul>
        """

        if min_url[:7] != "http://" :
            min_url = "http://"+min_url

        if self.map.canvas.auto_label:
            if min_label == '':
                start = min_url.rfind('/') + 1
                min_label = min_url[ start : len( min_url ) - 4 ]

            try:
                unique = eval( unique )
            except:
                pass

            if not unique:
                min_label = '%s %d' % ( min_label, self.map.canvas.layers['miniatures'].next_serial() )
        self.map.canvas.add_miniature( min_url, label, unique )

    def become( self, name ):
        try:
            self.chat.aliasList.SetStringSelection(name)
        except:
            msg = 'Alias: %s Does not exist' % (name)
            print msg

    def sendToChat( self, text ):
        """Broadcasts the specified text to the chatbuffer.
        <ul>
            <li>text - the text to send.
        </ul>
        """
        if text[0] != "/":
            self.chat.ParsePost(text, send=1, myself=1)
        else:
            self.chat.chat_cmds.docmd(text)

    def sendToChatAs( self, name, text ):
        """Broadcasts the specified text to the chatbuffer as the specified alias
        <ul>
            <li>name - The player's name will be temporarily changed to this value
            <li>text - The text to broadcast to the chatbuffer
        </ul>
        """
        self.become(name)
        self.sendToChat( text )
        self.become("Use Real Name")

    def emoteToChat( self, text):
        if text[0] != '/':
            text = '/me ' + text
        self.sendToChat( text )

    def emoteToChatAs( self, name, text ):
        text = '/me ' + text
        self.become(name)
        self.sendToChat( text )
        self.become("Use Real Name")

    def whisperToChat( self, who, text):
        if text[0] != '/':
            text = '/w %s=%s' % ( who, text )
        self.sendToChat( text )

    def whisperToChatAs( self, who, name, text ):
        if text[0] != '/':
            text = '/w %s=%s' % ( who, text )
        self.become(name)
        self.sendToChat( text )
        self.become("Use Real Name")

    def chatMessage( self, message ):
        self.chat.Post( self.chat.colorize( self.chat.syscolor, message ) )

    def get_input( self, message, title, default ):
        dlg = wx.TextEntryDialog( self, message, title, default )
        if dlg.ShowModal() == rpgutils.wx.ID_OK:
            return dlg.GetValue()
        dlg.Destroy()
        return None

    def show_info( self, title, message ):
        dlg = wx.MessageDialog( None, message, title, wx.OK | wx.ICON_INFORMATION )
        dlg.ShowModal()
        dlg.Destroy()
