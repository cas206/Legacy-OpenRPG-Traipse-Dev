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
# File: d20.py
# Author: Chris Davis
# Maintainer:
# Version:
#   $Id: d20.py,v Traipse 'Ornery-Orc' prof.ebral Exp $
#
# Description: The file contains code for the d20 nodehanlers
#

__version__ = "$Id: d20.py,v Traipse 'Ornery-Orc' prof.ebral Exp $"

from core import *
from containers import *
import re
from xml.etree.ElementTree import ElementTree, Element, iselement
from xml.etree.ElementTree import fromstring, tostring, parse, XML
from orpg.tools.orpg_log import debug
from orpg.tools.InterParse import Parse

D20_EXPORT = wx.NewId()
############################
## d20 character node handler
############################
## Spells code - added by Dragonstar
##Powers, Divine spells, inventory, howto, power points by Digitalxero
##The whole look and easy of use redone by Digitalxero
class container_handler(node_handler):
    """ should not be used! only a base class!
    <nodehandler name='?'  module='core' class='container_handler'  />
    """
    def __init__(self,xml,tree_node):
        node_handler.__init__(self,xml,tree_node)
        self.load_children()

    def load_children(self):
        children = self.xml.getchildren()
        for c in children:
            self.tree.load_xml(c,self.mytree_node)

    def on_drop(self,evt):
        drag_obj = self.tree.drag_obj
        if drag_obj == self: return
        opt = wx.MessageBox("Add node as child?","Container Node",wx.YES_NO|wx.CANCEL)
        if opt == wx.YES:
            xml = self.tree.drag_obj.delete()
            xml = self.xml.append(xml,None)
            self.tree.load_xml(xml, self.mytree_node)
            self.tree.Expand(self.mytree_node)
        elif opt == wx.NO: node_handler.on_drop(self,evt)

    def tohtml(self):
        cookie = 0
        html_str = "<table border=\"1\" ><tr><td>"
        html_str += "<b>"+self.xml.get("name") + "</b>"
        html_str += "</td></tr>\n"
        html_str += "<tr><td>"
        max = tree.GetChildrenCount(handler.mytree_node,0)
        try: (child,cookie)=self.tree.GetFirstChild(self.mytree_node,cookie)
        # If this happens we probably have a newer version of wxPython
        except: (child,cookie)=self.tree.GetFirstChild(self.mytree_node)
        obj = self.tree.GetPyData(child)
        for m in range(max):
            html_str += "<p>" + obj.tohtml()
            if m < max-1:
                child = self.tree.GetNextSibling(child)
                if child.IsOk(): obj = self.tree.GetPyData(child)
        html_str += "</td></tr></table>"
        return html_str

    def get_size_constraint(self):
        return 1

    def get_char_name( self ):
        return self.child_handlers['general'].get_char_name()

    def set_char_pp(self,attr,evl):
        return self.child_handlers['pp'].set_char_pp(attr,evl)

    def get_char_pp( self, attr ):
        return self.child_handlers['pp'].get_char_pp(attr)

    def get_char_lvl( self, attr ):
        return self.child_handlers['classes'].get_char_lvl(attr)


class d20char_handler(node_handler):
    """ Node handler for a d20 charactor
        <nodehandler name='?'  module='d20' class='d20char_handler2'  />
    """
    def __init__(self,xml,tree_node):
        node_handler.__init__(self,xml,tree_node)
        self.frame = component.get('frame')
        self.child_handlers = {}
        self.new_child_handler('howtouse','HowTO use this tool',d20howto,'note')
        self.new_child_handler('general','General Information',d20general,'gear')
        self.new_child_handler('inventory','Money and Inventory',d20inventory,'money')
        self.new_child_handler('abilities','Abilities Scores',d20ability,'gear')
        self.new_child_handler('classes','Classes',d20classes,'knight')
        self.new_child_handler('saves','Saves',d20saves,'skull')
        self.new_child_handler('skills','Skills',d20skill,'book')
        self.new_child_handler('feats','Feats',d20feats,'book')
        self.new_child_handler('spells','Spells',d20spells,'book')
        self.new_child_handler('divine','Divine Spells',d20divine,'book')
        self.new_child_handler('powers','Powers',d20powers,'questionhead')
        self.new_child_handler('hp','Hit Points',d20hp,'gear')
        self.new_child_handler('pp','Power Points',d20pp,'gear')
        self.new_child_handler('attacks','Attacks',d20attacks,'spears')
        self.new_child_handler('ac','Armor',d20armor,'spears')
        self.myeditor = None

    def on_version(self,old_version):
        node_handler.on_version(self,old_version)
        if old_version == "":
            data = parse(orpg.dirpath.dir_struct["nodes"]+"d20character.xml").getroot()
            for tag in ("howtouse","inventory","powers","divine","pp"):
                self.xml.append(data.find(tag))

            ## add new atts
            melee_attack = self.xml.find('melee')
            melee_attack.set("second","0")
            melee_attack.set("third","0")
            melee_attack.set("forth","0")
            melee_attack.set("fifth","0")
            melee_attack.set("sixth","0")
            range_attack = self.xml.find('ranged')
            range_attack.set("second","0")
            range_attack.set("third","0")
            range_attack.set("forth","0")
            range_attack.set("fifth","0")
            range_attack.set("sixth","0")

            gen_list = self.xml.find('general')

            for tag in ("currentxp","xptolevel"): gen_list.append(data.find(tag))
        print old_version


    def get_char_name( self ):
        return self.child_handlers['general'].get_char_name()

    def set_char_pp(self,attr,evl):
        return self.child_handlers['pp'].set_char_pp(attr,evl)

    def get_char_pp( self, attr ):
        return self.child_handlers['pp'].get_char_pp(attr)

    def get_char_lvl( self, attr ):
        return self.child_handlers['classes'].get_char_lvl(attr)

    def new_child_handler(self,tag,text,handler_class,icon='gear'):
        tree = self.tree
        i = self.tree.icons[icon]
        new_tree_node = tree.AppendItem(self.mytree_node,text,i,i)
        handler = handler_class(self.xml.find(tag),new_tree_node,self)
        tree.SetPyData(new_tree_node,handler)
        self.child_handlers[tag] = handler

    def get_design_panel(self,parent):
        return tabbed_panel(parent,self,1)

    def get_use_panel(self,parent):
        return tabbed_panel(parent,self,2)

    def tohtml(self):
        html_str = "<table><tr><td colspan=2 >"+self.child_handlers['general'].tohtml()+"</td></tr>"
        html_str += "<tr><td width='50%' valign=top >"+self.child_handlers['abilities'].tohtml()
        html_str += "<P>" + self.child_handlers['saves'].tohtml()
        html_str += "<P>" + self.child_handlers['attacks'].tohtml()
        html_str += "<P>" + self.child_handlers['ac'].tohtml()
        html_str += "<P>" + self.child_handlers['feats'].tohtml()
        html_str += "<P>" + self.child_handlers['spells'].tohtml()
        html_str += "<P>" + self.child_handlers['divine'].tohtml()
        html_str += "<P>" + self.child_handlers['powers'].tohtml()
        html_str += "<P>" + self.child_handlers['inventory'].tohtml() +"</td>"
        html_str += "<td width='50%' valign=top >"+self.child_handlers['classes'].tohtml()
        html_str += "<P>" + self.child_handlers['hp'].tohtml()
        html_str += "<P>" + self.child_handlers['pp'].tohtml()
        html_str += "<P>" + self.child_handlers['skills'].tohtml() +"</td>"
        html_str += "</tr></table>"
        return html_str

    def about(self):
        """html_str = "<img src='" + orpg.dirpath.dir_struct["icon"]+'d20_logo.gif' "><br /><b>d20 Character Tool v0.7 beta</b>"
        html_str += "<br />by Chris Davis<br />chris@rpgarchive.com"
        return html_str"""
        text = 'd20 Character Tool 0.7 beta\n'
        text += 'by Chris Davis chris@rpgarchive.com'
        return text

    def get_char_name( self ):
        return self.child_handlers['general'].get_char_name()
    def get_armor_class( self ):
        return self.child_handlers['ac'].get_armor_class()
    def get_max_hp( self ):
        return self.child_handlers['hp'].get_max_hp()
    def get_current_hp( self ):
        return self.child_handlers['hp'].get_current_hp()

    def set_char_pp(self,attr,evl):
        return self.child_handlers['pp'].set_char_pp(attr,evl)

    def get_char_pp( self, attr ):
        return self.child_handlers['pp'].get_char_pp(attr)

    def get_char_lvl( self, attr ):
        return self.child_handlers['classes'].get_char_lvl(attr)

""" Removed to use the supplied Tabbed Panel
class tabbed_panel(wx.Notebook):
    def __init__(self, parent, handler, mode):
        wx.Notebook.__init__(self, parent, -1, size=(1200,800))
        self.handler = handler
        self.parent = parent
        tree = self.handler.tree
        max = tree.GetChildrenCount(handler.mytree_node)
        cookie = 0

        try: (child,cookie)=tree.GetFirstChild(handler.mytree_node,cookie)
        # If this happens we probably have a newer version of wxPython
        except: (child,cookie)=tree.GetFirstChild(handler.mytree_node)
        if not child.IsOk(): return
        obj = tree.GetPyData(child)
        for m in range(max):
            if mode == 1: panel = obj.get_design_panel(self)
            else: panel = obj.get_use_panel(self)
            name = obj.xml.get("name")
            if panel: self.AddPage(panel,name)
            if m < max-1:
                child = tree.GetNextSibling(child)
                if child.IsOk(): obj = tree.GetPyData(child)
                else: break

    def about(self):
        html_str = "<img src='" + orpg.dirpath.dir_struct["icon"]+'d20_logo.gif' "><br /><b>d20 Character Tool v0.7 beta</b>"
        html_str += "<br />by Chris Davis<br />chris@rpgarchive.com"
        return html_str

    def get_char_name( self ):
        return self.child_handlers['general'].get_char_name()

    def set_char_pp(self,attr,evl):
        return self.child_handlers['pp'].set_char_pp(attr,evl)

    def get_char_pp( self, attr ):
        return self.child_handlers['pp'].get_char_pp(attr)

    def get_char_lvl( self, attr ):
        return self.child_handlers['classes'].get_char_lvl(attr)
"""
class d20_char_child(node_handler):
    """ Node Handler for skill.  This handler will be
        created by d20char_handler.
    """
    def __init__(self,xml,tree_node,parent):
        node_handler.__init__(self,xml,tree_node)
        self.char_hander = parent
        self.drag = False
        self.frame = component.get('frame')
        self.myeditor = None

    def on_drop(self,evt):
        pass

    def on_rclick(self,evt):
        pass

    def on_ldclick(self,evt):
        return
        if self.myeditor == None or self.myeditor.destroyed:
            title = self.xml.get('name') + " Editor"
            self.myeditor = wx.Frame(self.frame, -1, title)
            if wx.Platform == '__WXMSW__':
                icon = wx.Icon(orpg.dirpath.dir_struct["icon"]+'grid.ico', wx.BITMAP_TYPE_ICO)
                self.myeditor.SetIcon(icon)
                del icon
            wnd = self.get_design_panel(self.myeditor)
            self.myeditor.panel = wnd
            self.wnd = wnd
            self.myeditor.Show(1)
        else:
            self.myeditor.Raise()

    def on_html(self,evt):
        html_str = self.tohtml()
        wnd = http_html_window(self.frame.note,-1)
        wnd.title = self.xml.get('name')
        self.frame.add_panel(wnd)
        wnd.SetPage(html_str)

    def get_design_panel(self,parent):
        pass

    def get_use_panel(self,parent):
        return self.get_design_panel(parent)

    def delete(self):
        pass


class d20skill(d20_char_child):
    """ Node Handler for skill.  This handler will be
        created by d20char_handler.
    """
    def __init__(self,xml,tree_node,parent):
        d20_char_child.__init__(self,xml,tree_node,parent)
        tree = self.tree
        icons = self.tree.icons
        self.skills={}
        for n in self.xml.findall('skill'):
            name = n.get('name')
            self.skills[name] = n
            new_tree_node = tree.AppendItem(self.mytree_node,name,icons['gear'],icons['gear'])
            tree.SetPyData(new_tree_node,self)

    def get_mod(self,name):
        skill = self.skills[name]
        stat = skill.get('stat')
        ac = int(skill.get('armorcheck'))
        if ac:
            ac = self.char_hander.child_handlers['ac'].get_check_pen()
        stat_mod = self.char_hander.child_handlers['abilities'].get_mod(stat)
        rank = int(skill.get('rank'))
        misc = int(skill.get('misc'))
        total = stat_mod + rank + misc + ac
        return total

    def on_rclick(self,evt):
        item = self.tree.GetSelection()
        name = self.tree.GetItemText(item)
        if item == self.mytree_node: d20_char_child.on_ldclick(self,evt)
        else:
            skill = self.skills[name];
            untrained = skill.get('untrained');
            rank = skill.get('rank');
            if untrained == "0" and rank == "0": txt = '%s Skill Check: Untrained' % (name)
            else:
                mod = self.get_mod(name)
                if mod >= 0: mod1 = "+"
                else: mod1 = ""
                txt = '%s Skill Check: [1d20%s%s]' % (name, mod1, mod)
            chat = self.chat
            Parse.Post( txt, self.chat, True, True )

    def get_design_panel(self,parent):
        wnd = outline_panel(parent,self,skill_grid,"Skills")
        wnd.title = "Skills (edit)"
        return wnd

    def tohtml(self):
        html_str = """<table border='1' width=100% ><tr BGCOLOR=#E9E9E9 ><th width='30%'>Skill</th><th>Key</th>
                    <th>Rank</th><th>Abil</th><th>Misc</th><th>Total</th></tr>"""
        for n in self.xml.findall('skill'):
            name = n.get('name')
            stat = n.get('stat')
            rank = n.get('rank')
            html_str = html_str + "<tr ALIGN='center'><td>"+name+"</td><td>"+stat+"</td><td>"+rank+"</td>"
            stat_mod = str(self.char_hander.child_handlers['abilities'].get_mod(stat))
            misc = n.get('misc')
            mod = str(self.get_mod(name))
            if mod >= 0: mod1 = "+"
            else: mod1 = ""
            html_str = html_str + "<td>"+stat_mod+"</td><td>"+misc+'</td><td>%s%s</td></tr>' % (mod1, mod)
        html_str = html_str + "</table>"
        return html_str


class d20ability(d20_char_child):
    """ Node Handler for ability.   This handler will be
        created by d20char_handler.
    """
    def __init__(self,xml,tree_node,parent):
        d20_char_child.__init__(self,xml,tree_node,parent)
        self.abilities = {}
        tree = self.tree
        icons = tree.icons
        for n in self.xml.findall('stat'):
            name = n.get('abbr')
            self.abilities[name] = n
            new_tree_node = tree.AppendItem( self.mytree_node, name, icons['gear'], icons['gear'] )
            tree.SetPyData( new_tree_node, self )

    def on_rclick( self, evt ):
        item = self.tree.GetSelection()
        name = self.tree.GetItemText( item )
        if item == self.mytree_node:
            d20_char_child.on_ldclick( self, evt )
        else:
            mod = self.get_mod( name )
            if mod >= 0: mod1 = "+"
            else: mod1 = ""
            chat = self.chat
            txt = '%s check: [1d20%s%s]' % ( name, mod1, mod )
            Parse.Post( txt, self.chat, True, True )

    def get_mod(self,abbr):
        score = int(self.abilities[abbr].get('base'))
        mod = (score - 10) / 2
        return mod

    def set_score(self,abbr,score):
        if score >= 0:
            self.abilities[abbr].set("base",str(score))

    def get_design_panel(self,parent):
        wnd = outline_panel(parent,self,abil_grid,"Abilities")
        wnd.title = "Abilities (edit)"
        return wnd

    def tohtml(self):
        html_str = """<table border='1' width=100%><tr BGCOLOR=#E9E9E9 ><th width='50%'>Ability</th>
                    <th>Base</th><th>Modifier</th></tr>""" 
        for n in self.xml.findall('stat'):
            name = n.get('name')
            abbr = n.get('abbr')
            base = n.get('base')
            mod = str(self.get_mod(abbr))
            if mod >= 0: mod1 = "+"
            else: mod1 = ""
            html_str = html_str + "<tr ALIGN='center'><td>"+name+"</td><td>"+base+'</td><td>%s%s</td></tr>' % (mod1, mod)
        html_str = html_str + "</table>"
        return html_str


class d20saves(d20_char_child):
    """ Node Handler for saves.   This handler will be
        created by d20char_handler.
    """
    def __init__(self,xml,tree_node,parent):
        d20_char_child.__init__(self,xml,tree_node,parent)
        tree = self.tree
        icons = self.tree.icons
        self.saves={}
        for n in self.xml.findall('save'):
            name = n.get('name')
            self.saves[name] = n
            new_tree_node = tree.AppendItem(self.mytree_node,name,icons['gear'],icons['gear'])
            tree.SetPyData(new_tree_node,self)

    def get_mod(self,name):
        save = self.saves[name]
        stat = save.get('stat')
        stat_mod = self.char_hander.child_handlers['abilities'].get_mod(stat)
        base = int(save.get('base'))
        miscmod = int(save.get('miscmod'))
        magmod = int(save.get('magmod'))
        total = stat_mod + base + miscmod + magmod
        return total

    def on_rclick(self,evt):
        item = self.tree.GetSelection()
        name = self.tree.GetItemText(item)
        if item == self.mytree_node:
            d20_char_child.on_ldclick(self,evt)

        else:
            mod = self.get_mod(name)
            if mod >= 0: mod1 = "+"
            else: mod1 = ""
            chat = self.chat
            txt = '%s save: [1d20%s%s]' % (name, mod1, mod)
            Parse.Post( txt, self.chat, True, True )

    def get_design_panel(self,parent):
        wnd = outline_panel(parent,self,save_grid,"Saves")
        wnd.title = "Saves"
        return wnd

    def tohtml(self):
        html_str = """<table border='1' width=100% ><tr BGCOLOR=#E9E9E9 ><th width='30%'>Save</th>
                    <th>Key</th><th>Base</th><th>Abil</th><th>Magic</th>
                    <th>Misc</th><th>Total</th></tr>"""
        for n in self.xml.findall('save'):
            name = n.get('name')
            stat = n.get('stat')
            base = n.get('base')
            html_str = html_str + "<tr ALIGN='center'><td>"+name+"</td><td>"+stat+"</td><td>"+base+"</td>"
            stat_mod = str(self.char_hander.child_handlers['abilities'].get_mod(stat))
            mag = n.get('magmod')
            misc = n.get('miscmod')
            mod = str(self.get_mod(name))
            if mod >= 0:  mod1 = "+"
            else: mod1 = ""
            html_str = html_str + "<td>"+stat_mod+"</td><td>"+mag+"</td>"
            html_str = html_str + '<td>'+misc+'</td><td>%s%s</td></tr>' % (mod1, mod)
        html_str = html_str + "</table>"
        return html_str


class d20general(d20_char_child):
    """ Node Handler for general information.   This handler will be
        created by d20char_handler.
    """
    def __init__(self,xml,tree_node,parent):
        d20_char_child.__init__(self,xml,tree_node,parent)

    def get_design_panel(self,parent):
        wnd = outline_panel(parent,self,gen_grid,"General Information")
        wnd.title = "General Info"
        return wnd

    def tohtml(self):
        html_str = "<table width=100% border=1 ><tr BGCOLOR=#E9E9E9 ><th>General Information</th></tr><tr><td>"
        for n in self.xml:
            html_str += "<B>"+n.tag.capitalize() +":</B> "
            html_str += n.text + ", "
        html_str = html_str[:len(html_str)-2] + "</td></tr></table>"
        return html_str

    def on_name_change(self,name):
        self.char_hander.rename(name)

    def get_char_name( self ):
        return self.xml.find( 'name' ).text


class d20classes(d20_char_child):
    """ Node Handler for classes.  This handler will be
        created by d20char_handler.
    """
    def __init__(self,xml,tree_node,parent):
        d20_char_child.__init__(self,xml,tree_node,parent)

    def get_design_panel(self,parent):
        wnd = outline_panel(parent,self,class_panel,"Classes")
        wnd.title = "Classes"
        return wnd

    def tohtml(self):
        html_str = "<table width=100% border=1 ><tr BGCOLOR=#E9E9E9 ><th>Classes</th></tr><tr><td>"
        for n in self.xml: html_str += n.get('name') + " ("+n.get('level')+"), "
        html_str = html_str[:len(html_str)-2] + "</td></tr></table>"
        return html_str

    def get_char_lvl( self, attr ):
        for n in self.xml.findall('class'):
            lvl = n.get('level')
            type = n.get('name')
            if attr == "level": return lvl
            elif attr == "class": return type


class d20feats(d20_char_child):
    """ Node Handler for classes.  This handler will be
        created by d20char_handler.
    """
    def __init__(self,xml,tree_node,parent):
        d20_char_child.__init__(self,xml,tree_node,parent)

    def get_design_panel(self,parent):
        wnd = outline_panel(parent,self,feat_panel,"Feats")
        wnd.title = "Feats"
        return wnd

    def tohtml(self):
        html_str = "<table width=100% border=1 ><tr BGCOLOR=#E9E9E9 ><th>Feats</th></tr><tr><td>"
        for n in self.xml: html_str += n.get('name')+ ", "
        html_str = html_str[:len(html_str)-2] + "</td></tr></table>"
        return html_str


class d20spells(d20_char_child):
    """ Node Handler for classes.  This handler will be
        created by d20char_handler.
    """
    def __init__(self,xml,tree_node,parent):
        d20_char_child.__init__(self,xml,tree_node,parent)
        self.spells = {}
        tree = self.tree
        icons = self.tree.icons
        for n in self.xml.findall( 'spell' ):
            name = n.get('name')
            self.spells[ name ] = n
            new_tree_node = tree.AppendItem( self.mytree_node, name, icons['gear'], icons['gear'] )
            tree.SetPyData( new_tree_node, self )

    def on_rclick( self, evt ):
        item = self.tree.GetSelection()
        name = self.tree.GetItemText( item )
        if item == self.mytree_node:
            d20_char_child.on_ldclick( self, evt )
        else:
            level = self.spells[ name ].get( 'level' )
            descr = self.spells[ name ].get( 'desc' )
            use = self.spells[ name ].get( 'used' )
            memrz = self.spells[ name ].get( 'memrz' )
            cname = self.char_hander.get_char_name()
            use += '+1'
            left = eval( '%s - ( %s )' % ( memrz, use ) )
            if left < 0:
                txt = '%s Tried to cast %s but has used all of them for today, "Please rest so I can cast more."' % ( cname, name )
                Parse.Post( txt, self.chat, True, False )
            else:
                txt = '%s casts %s ( level %s, "%s" )' % ( cname, name, level, descr )
                Parse.Post( txt, self.chat, True, False )
                s = ''
                if left != 1: s = 's'
                txt = '%s can cast %s %d more time%s' % ( cname, name, left, s )
                Parse.Post( txt, self.chat, False, False )
                self.spells[ name ].set( 'used', `eval( use )` )

    def refresh_spells(self):
        self.spells = {}
        tree = self.tree
        icons = self.tree.icons
        tree.CollapseAndReset(self.mytree_node)
        for n in self.xml.findall('spell'):
            name = n.get('name')
            new_tree_node = tree.AppendItem(self.mytree_node,name,icons['gear'],icons['gear'])
            tree.SetPyData(new_tree_node,self)
            self.spells[name]=n

    def get_design_panel(self,parent):
        wnd = outline_panel(parent,self,spell_panel,"Spells")
        wnd.title = "Spells"
        return wnd

    def tohtml(self):
        html_str = "<table width=100% border=1 ><tr BGCOLOR=#E9E9E9 ><th>Arcane Spells</th></tr><tr><td><br />"
        for n in self.xml: html_str += "(" + n.get('level') + ") " + n.get('name')+ ", "
        html_str = html_str[:len(html_str)-2] + "</td></tr></table>"
        return html_str

    def get_char_lvl( self, attr ):
        return self.char_hander.get_char_lvl(attr)

class d20divine(d20_char_child):
    """ Node Handler for classes.  This handler will be
        created by d20char_handler.
    """
    def __init__(self,xml,tree_node,parent):
        d20_char_child.__init__(self,xml,tree_node,parent)
        self.spells = {}
        tree = self.tree
        icons = self.tree.icons
        for n in self.xml.findall( 'gift' ):
            name = n.get('name')
            self.spells[ name ] = n
            new_tree_node = tree.AppendItem( self.mytree_node, name, icons['flask'], icons['flask'] )
            tree.SetPyData( new_tree_node, self )

    def on_rclick( self, evt ):
        item = self.tree.GetSelection()
        name = self.tree.GetItemText( item )
        if item == self.mytree_node:
            d20_char_child.on_ldclick( self, evt )
        else:
            level = self.spells[ name ].get( 'level' )
            descr = self.spells[ name ].get( 'desc' )
            use = self.spells[ name ].get( 'used' )
            memrz = self.spells[ name ].get( 'memrz' )
            cname = self.char_hander.get_char_name()
            use += '+1'
            left = eval( '%s - ( %s )' % ( memrz, use ) )
            if left < 0:
                txt = '%s Tried to cast %s but has used all of them for today, "Please rest so I can cast more."' % ( cname, name )
                Parse.Post( txt, self.chat, True, False )
            else:
                txt = '%s casts %s ( level %s, "%s" )' % ( cname, name, level, descr )
                Parse.Post( txt, self.chat, True, False )
                s = ''
                if left != 1: s = 's'
                txt = '%s can cast %s %d more time%s' % ( cname, name, left, s )
                Parse.Post( txt, self.chat, False, False )
                self.spells[ name ].set( 'used', `eval( use )` )

    def refresh_spells(self):
        self.spells = {}
        tree = self.tree
        icons = self.tree.icons
        tree.CollapseAndReset(self.mytree_node)
        for n in self.xml.findall('gift'):
            name = n.get('name')
            new_tree_node = tree.AppendItem(self.mytree_node,name,icons['flask'],icons['flask'])
            tree.SetPyData(new_tree_node,self)
            self.spells[name]=n
            
    def get_design_panel(self,parent):
        wnd = outline_panel(parent,self,divine_panel,"Spells")
        wnd.title = "Spells"
        return wnd

    def tohtml(self):
        html_str = "<table width=100% border=1 ><tr BGCOLOR=#E9E9E9 ><th>Divine Spells</th></tr><tr><td><br />"
        for n in self.xml: html_str += "(" + n.get('level') + ") " + n.get('name')+ ", "
        html_str = html_str[:len(html_str)-2] + "</td></tr></table>"
        return html_str

    def get_char_lvl( self, attr ):
        return self.char_hander.get_char_lvl(attr)

class d20powers(d20_char_child):
    """ Node Handler for classes.  This handler will be
        created by d20char_handler.
    """
    def __init__(self,xml,tree_node,parent):
        d20_char_child.__init__(self,xml,tree_node,parent)
        #cpp = self.xml.findall( 'pp' ).get('current1')
        self.powers = {}
        tree = self.tree
        icons = self.tree.icons
        for n in self.xml.findall( 'power' ):
            name = n.get('name')
            self.powers[ name ] = n
            new_tree_node = tree.AppendItem( self.mytree_node, name, icons['gear'], icons['gear'] )
            tree.SetPyData( new_tree_node, self )

    def on_rclick( self, evt ):
        item = self.tree.GetSelection()
        name = self.tree.GetItemText( item )
        if item == self.mytree_node:
            d20_char_child.on_ldclick( self, evt )
        else:
            level = self.powers[ name ].get( 'level' )
            descr = self.powers[ name ].get( 'desc' )
            use = self.powers[ name ].get( 'used' )
            points = self.powers[ name ].get( 'point' )
            cpp = self.char_hander.get_char_pp('current1')
            fre = self.char_hander.get_char_pp('free')
            cname = self.char_hander.get_char_name()
            if level == "0" and fre != "0":
                left = eval('%s - ( %s )' % ( fre, points ))
                numcast = eval('%s / %s' % (left, points))
                if left < 0:
                    txt = '%s doesnt have enough PowerPoints to use %s' % ( cname, name )
                    Parse.Post( txt, self.chat, True, False )
                else:
                    txt = '%s uses %s as a Free Talent ( level %s, "%s" )' % ( cname, name, level, descr )
                    Parse.Post( txt, self.chat, True, False )
                    s = ''
                    if left != 1: s = 's'
                    txt = '%s can use %s %d more time%s' % ( cname, name, numcast, s )
                    Parse.Post( txt, self.chat, False, False )
                    self.char_hander.set_char_pp('free', left)
            else:
                left = eval('%s - ( %s )' % ( cpp, points ))
                numcast = eval('%s / %s' % (left, points))
                if left < 0:
                    txt = '%s doesnt have enough PowerPoints to use %s' % ( cname, name )
                    Parse.Post( txt, self.chat, True, False )
                else:
                    txt = '%s uses %s ( level %s, "%s" )' % ( cname, name, level, descr )
                    Parse.Post( txt, self.chat, True, False )
                    s = ''
                    if left != 1: s = 's'
                    txt = '%s can use %s %d more time%s' % ( cname, name, numcast, s )
                    txt += ' - And has %d more Powerpoints left' % (left)
                    Parse.Post( txt, self.chat, False, False )
                    self.char_hander.set_char_pp('current1', left)

    def refresh_powers(self):
        self.powers = {}
        tree = self.tree
        icons = self.tree.icons
        tree.CollapseAndReset(self.mytree_node)
        for n in self.xml.findall('power'):
            name = n.get('name')
            new_tree_node = tree.AppendItem(self.mytree_node,name,icons['questionhead'],icons['questionhead'])
            tree.SetPyData(new_tree_node,self)
            self.powers[name]=n

    def get_design_panel(self,parent):
        wnd = outline_panel(parent,self,power_panel,"Powers")
        wnd.title = "Powers"
        return wnd

    def tohtml(self):
        html_str = "<table width=100% border=1 ><tr BGCOLOR=#E9E9E9 ><th>Powers</th></tr><tr><td><br />"
        for n in self.xml: html_str += "(" + n.get('level') + ") " + n.get('name')+ ", "
        html_str = html_str[:len(html_str)-2] + "</td></tr></table>"
        return html_str

    def get_char_lvl( self, attr ):
        return self.char_hander.get_char_lvl(attr)

    def set_char_pp(self,attr,evl):
        return self.char_hander.set_char_pp(attr,evl)

    def get_char_pp( self, attr ):
        return self.char_hander.get_char_pp(attr)

class d20howto(d20_char_child):
    """ Node Handler for hit points.  This handler will be
        created by d20char_handler.
    """
    def __init__(self,xml,tree_node,parent):
        d20_char_child.__init__(self,xml,tree_node,parent)

    def get_design_panel(self,parent):
        wnd = outline_panel(parent,self,howto_panel,"How To")
        wnd.title = "How To"
        return wnd

class d20inventory(d20_char_child):
    """ Node Handler for general information.   This handler will be
        created by d20char_handler.
    """
    def __init__(self,xml,tree_node,parent):
        d20_char_child.__init__(self,xml,tree_node,parent)

    def get_design_panel(self,parent):
        wnd = outline_panel(parent,self,inventory_grid,"Inventory")
        wnd.title = "General Info"
        return wnd

    def tohtml(self):
        html_str = "<table width=100% border=1 ><tr BGCOLOR=#E9E9E9 ><th>General Information</th></tr><tr><td>"
        for n in self.xml:
            html_str += "<B>"+n.tag.capitalize() +":</B> "
            html_str += n.text + "<br />"
        html_str = html_str[:len(html_str)-2] + "</td></tr></table>"
        return html_str

    def on_name_change(self,name):
        self.char_hander.rename(name)

    def get_char_name( self ):
        return self.xml.find( 'name' ).text


class d20hp(d20_char_child):
    """ Node Handler for hit points.  This handler will be
        created by d20char_handler.
    """
    def __init__(self,xml,tree_node,parent):
        d20_char_child.__init__(self,xml,tree_node,parent)

    def get_design_panel(self,parent):
        wnd = outline_panel(parent,self,hp_panel,"Hit Points")
        wnd.title = "Hit Points"
        return wnd

    def tohtml(self):
        html_str = "<table width=100% border=1 ><tr BGCOLOR=#E9E9E9 ><th colspan=4>Hit Points</th></tr>"
        html_str += "<tr><th>Max:</th><td>"+self.xml.get('max')+"</td>"
        html_str += "<th>Current:</th><td>"+self.xml.get('current')+"</td>"
        html_str += "</tr></table>"
        return html_str

    def get_max_hp( self ):
        try: return eval( self.xml.get( 'max' ) )
        except: return 0
    def get_current_hp( self ):
        try: return eval( self.xml.get( 'current' ) )
        except: return 0

class d20pp(d20_char_child):
    """ Node Handler for power points.  This handler will be
        created by d20char_handler.
    """
    def __init__(self,xml,tree_node,parent):
        d20_char_child.__init__(self,xml,tree_node,parent)

    def get_design_panel(self,parent):
        wnd = outline_panel(parent,self,pp_panel,"Power Points")
        wnd.title = "Power Points"
        return wnd

    def tohtml(self):
        html_str = "<table width=100% border=1 ><tr BGCOLOR=#E9E9E9 ><th colspan=8>Power Points</th></tr>"
        html_str += "<tr><th>Max:</th><td>"+self.xml.get('max1')+"</td>"
        html_str += "<th>Current:</th><td>"+self.xml.get('current1')+"</td>"
        html_str += "<th>Current Talents/day:</th><td>"+self.xml.get('free')+"</td>"
        html_str += "<th>Max Talents/day:</th><td>"+self.xml.get('maxfree')+"</td>"
        html_str += "</tr></table>"
        return html_str

    def get_char_pp( self, attr ):
        pp = self.xml.get(attr)
        return pp

    def set_char_pp( self, attr, evl ):
        pp = self.xml.set(attr, evl)
        return pp

class d20attacks(d20_char_child):
    """ Node Handler for attacks.  This handler will be
        created by d20char_handler.
    """
    def __init__(self,xml,tree_node,parent):
        d20_char_child.__init__(self,xml,tree_node,parent)
        node_list = self.xml.findall('melee')
        self.melee = node_list[0]
        node_list = self.xml.findall('ranged')
        self.ranged = node_list[0]
        self.refresh_weapons()

    def refresh_weapons(self):
        self.weapons = {}
        tree = self.tree
        icons = self.tree.icons
        tree.CollapseAndReset(self.mytree_node)
        node_list = self.xml.findall('weapon')
        for n in node_list:
            name = n.get('name')
            new_tree_node = tree.AppendItem(self.mytree_node,name,icons['sword'],icons['sword'])
            tree.SetPyData(new_tree_node,self)
            self.weapons[name]=n

    def get_attack_data(self):
        temp = self.melee
        base = int(temp.get('base'))
        base2 = int(temp.get('second'))
        base3 = int(temp.get('third'))
        base4 = int(temp.get('forth'))
        base5 = int(temp.get('fifth'))
        base6 = int(temp.get('sixth'))
        misc = int(temp.get('misc'))
        return (base, base2, base3, base4, base5, base6, misc)

    # Replace any 'S' and 'D' in an attack modifier and damage modifier with the
    # strength bonus or dexterity bonus respectively.
    def process_mod_codes( self, attack, damage ):
        str_mod = self.char_hander.child_handlers['abilities'].get_mod( 'Str' )
        dex_mod = self.char_hander.child_handlers['abilities'].get_mod( 'Dex' )
        str_re = re.compile('S')
        dex_re = re.compile('D')
        attack = str_re.sub( str( str_mod ), attack )
        attack = dex_re.sub( str( dex_mod ), attack )
        damage = str_re.sub( str( str_mod ), damage );
        damage = dex_re.sub( str( dex_mod ), damage );
        return (attack, damage)

    # Decompose a damage string (e.g. longsword +1 sneak attack "1d8+S+1+1d6")
    # into it's 4 seperate components <n>d<s>+<mods>+<extra dice>
    def decompose_damage( self, damage ):
        m = re.match( r"(?P<n>\d+)d(?P<s>\d+)(?P<mods>(\s*(\+|-|/|\*)\s*(\d+|D|S)*)*)(?P<extra>(\s*(\+|-)\s*\d+d\d+)?)\s*$", damage )
        return (int(m.group('n')), int(m.group('s')), m.group('mods'), m.group('extra'))

    def on_rclick(self,evt):
        item = self.tree.GetSelection()
        name = self.tree.GetItemText(item)
        if item == self.mytree_node:
            d20_char_child.on_ldclick(self,evt)
            #self.frame.add_panel(self.get_design_panel(self.frame.note))
        else:
            # Weapon/attack specific attack modifier (e.g. "S+1" for a longsword+1).
            attack_mod_str = self.weapons[name].get('mod')

            # Weapon/attack specific damage (e.g. "1d8+S+1" for a longsword+1).
            damage_str = self.weapons[name].get('damage')
            (num_damage_dice, damage_die, damage_mods, extra_damage) = self.decompose_damage( damage_str )

            # Replace any 'S' and 'D' in attack_mod_str and damage_str with the
            # strength bonus or dexterity bonus respectively.
            (attack_mod_str, damage_mods) = self.process_mod_codes( attack_mod_str, damage_mods )

            # Base attack bonuses for up to six attacks.
            bab_attributes = ['base', 'second', 'third', 'forth', 'fifth', 'sixth']
            bab = []
            for b in bab_attributes: bab.append( int(self.melee.get( b )) )

            # Misc. attack modifier to be applied to *all* attacks.
            misc_mod = int(self.melee.get( 'misc' ));

            # Attack modifier (except BAB)
            attack_mod = misc_mod + eval( attack_mod_str )

            # Total damage mod (except extra dice)
            if damage_mods != '': damage_mod = eval( damage_mods )
            else: damage_mod = 0

            # Determine critical hit range and multiplier.
            critical_str = self.weapons[name].get( 'critical' )
            m = re.match( r"(((?P<min>\d+)-)?\d+/)?x(?P<mult>\d+)", critical_str )
            crit_min = m.group( 'min' )
            crit_mult = m.group( 'mult' )
            if crit_min == None: crit_min = 20
            else: crit_min = int( crit_min )
            if crit_mult == None: crit_mult = 2
            else: crit_mult = int( crit_mult )

            # Simple matter to output all the attack/damage lines to the chat buffer.
            for i in range( 0, len( bab ) ):
                if bab[i] > 0 or i == 0:
                    attack_roll_str = '[1d20%+d]' % (bab[i] + attack_mod)
                    attack_roll_parsed = Parse.Dice( attack_roll_str )
                    damage_roll_str = '[%dd%d%+d%s]' % (num_damage_dice, damage_die, damage_mod, extra_damage)
                    damage_roll_parsed = Parse.Dice( damage_roll_str )
                    txt = '%s (%s): %s ===> Damage: %s' \
                          % (name, bab_attributes[i], attack_roll_parsed, damage_roll_parsed)
                    self.chat.Post( txt, True, True )

                    # Check for a critical hit
                    d20_roll = int(re.match( r".*\[(\d+),.*", attack_roll_parsed ).group(1));
                    dmg = damage_str
                    if d20_roll >= crit_min:
                        for j in range(1,crit_mult): dmg += '+%s' % damage_str
                        txt = 'Critical hit? [1d20%+d] ===> Damage: [%dd%d%+d%s]' \
                              % (bab[i] + attack_mod, crit_mult*num_damage_dice, \
                                 damage_die, crit_mult*damage_mod, extra_damage)
                        Parse.Post( txt, self.chat, True, True )

    def get_design_panel(self,parent):
        wnd = outline_panel(parent,self,attack_panel,"Attacks")
        wnd.title = "Attacks"
        return wnd

    def get_char_lvl( self, attr ):
        return self.char_hander.get_char_lvl(attr)

    def tohtml(self):
        babs = self.get_attack_data()
        html_str = "<table width=100% border=1 ><tr ALIGN='center'><th BGCOLOR=#E9E9E9>Base Attack Bonus</th>"
        html_str += '<td>%+d' % babs[0]
        for i in range(1,6):
            if babs[i] > 0: html_str += '/%+d' % babs[i]
        html_str += "</td></tr><tr ALIGN='center' ><th BGCOLOR=#E9E9E9>Misc. Attack Bonus</th>"
        html_str += '<td>%+d</td></tr></table>' % babs[6]

        n_list = self.xml.findall('weapon')
        for n in n_list:
            (attack_mod, damage_mod) = self.process_mod_codes( n.get( 'mod' ), \
                                                               n.get( 'damage' ) )
            attack_mod = eval( attack_mod )
            html_str += """<P><table width=100% border=1><tr BGCOLOR=#E9E9E9><th colspan=3>Weapon</th>
                    <th>Attack</th><th >Damage</th></tr>""" \
                      + "<tr ALIGN='center'><td colspan=3>" \
                      + n.get('name') + "</td><td>"
            html_str += '%+d</td><td>%s</td></tr>' % (attack_mod, damage_mod)
            html_str += """<tr BGCOLOR=#E9E9E9 ><th>Critical</th><th>Range</th><th>Weight</th>
                        <th>Type</th><th>Size</th></tr>""" \
                      + "<tr ALIGN='center'><td>" \
                      + n.get( 'critical' ) + "</td><td>" \
                      + n.get( 'range' ) + "</td><td>" \
                      + n.get( 'weight' )+"</td><td>" \
                      + n.get( 'type' ) + "</td><td>" \
                      + n.get( 'size' ) + "</td></tr></table>"
        return html_str

class d20armor(d20_char_child):
    """ Node Handler for ac.  This handler will be
        created by d20char_handler.
    """
    def __init__(self,xml,tree_node,parent):
        d20_char_child.__init__(self,xml,tree_node,parent)

    def get_spell_failure(self):
        return self.get_total('spellfailure')

    def get_total_weight(self):
        return self.get_total('weight')

    def get_check_pen(self):
        return self.get_total('checkpenalty')

    def get_armor_class(self):
        ac_total = 10
        ac_total += self.get_total('bonus')
        dex_mod = self.char_hander.child_handlers['abilities'].get_mod('Dex')
        max_dex = self.get_max_dex()
        if dex_mod < max_dex: ac_total += dex_mod
        else: ac_total += max_dex
        return ac_total

    def get_max_dex(self):
        armor_list = self.xml.findall('armor')
        dex = 10
        for a in armor_list:
            temp = int(a.get("maxdex"))
            if temp < dex: dex = temp
        return dex

    def get_total(self,attr):
        armor_list = self.xml.findall('armor')
        total = 0
        for a in armor_list: total += int(a.get(attr))
        return total

    def get_design_panel(self,parent):
        wnd = outline_panel(parent,self,ac_panel,"Armor")
        wnd.title = "Armor"
        return wnd

    def tohtml(self):
        html_str = """<table width=100% border=1 ><tr BGCOLOR=#E9E9E9 ><th>AC</th>
                    <th>Check Penalty</th><th >Spell Failure</th><th>Max Dex</th><th>Total Weight</th></tr>"""
        html_str += "<tr ALIGN='center' ><td>"+str(self.get_armor_class())+"</td>"
        html_str += "<td>"+str(self.get_check_pen())+"</td>"
        html_str += "<td>"+str(self.get_spell_failure())+"</td>"
        html_str += "<td>"+str(self.get_max_dex())+"</td>"
        html_str += "<td>"+str(self.get_total_weight())+"</td></tr></table>"
        for n in self.xml:
            html_str += """<P><table width=100% border=1 ><tr BGCOLOR=#E9E9E9 ><th colspan=3>Armor</th>
                    <th>Type</th><th >Bonus</th></tr>"""
            html_str += "<tr ALIGN='center' ><td  colspan=3>"+n.get('name')+"</td>"
            html_str += "<td>"+n.get('type')+"</td>"
            html_str += "<td>"+n.get('bonus')+"</td></tr>"
            html_str += """<tr BGCOLOR=#E9E9E9 ><th>Check Penalty</th><th>Spell Failure</th>
                        <th>Max Dex</th><th>Speed</th><th>Weight</th></tr>"""
            html_str += "<tr ALIGN='center'><td>"+n.get('checkpenalty')+"</td>"
            html_str += "<td>"+n.get('spellfailure')+"</td>"
            html_str += "<td>"+n.get('maxdex')+"</td>"
            html_str += "<td>"+n.get('speed')+"</td>"
            html_str += "<td>"+n.get('weight')+"</td></tr></table>"
        return html_str


########################
##  d20 char windows
########################

class base_panel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, -1)

        #self.build_ctrls()
        self.Bind(wx.EVT_SIZE, self.on_size)

    def on_size(self,event):
        s = self.GetClientSizeTuple()
        #self.splitter.SetDimensions(0,0,s[0],s[1])

class outline_panel(wx.Panel):
    def __init__(self, parent, handler, wnd, txt,):
        wx.Panel.__init__(self, parent, -1)
        self.panel = wnd(self,handler)
        self.outline = wx.StaticBox(self,-1,txt)
        self.Bind(wx.EVT_SIZE, self.on_size)

    def on_size(self,event):
        s = self.GetClientSizeTuple()
        self.panel.SetDimensions(20,20,s[0]-40,s[1]-40)
        self.outline.SetDimensions(5,5,s[0]-10,s[1]-10)

class char_panel(wx.ScrolledWindow):
    def __init__(self, parent, handler):
        pname = handler.xml.set("name", 'TWO')
        wx.ScrolledWindow.__init__(self, parent, -1,style=wx.VSCROLL | wx.SUNKEN_BORDER  )
        self.height = 1200
        self.SetScrollbars(10, 10,80, self.height/10)
        self.main_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.panels = {}
        keys = handler.child_handlers.keys()
        for k in keys: self.panels[k] = handler.child_handlers[k].get_design_panel(self, [k])
        self.sub_sizer = wx.BoxSizer(wx.VERTICAL)
        self.sub_sizer2 = wx.BoxSizer(wx.VERTICAL)
        self.sub_sizer.Add(self.panels['general'], 1, wx.EXPAND)
        self.sub_sizer.Add(self.panels['abilities'], 1, wx.EXPAND)

        self.sub_sizer.Add(self.panels['attacks'], 2, wx.EXPAND)
        self.sub_sizer.Add(self.panels['ac'], 1, wx.EXPAND)
        self.sub_sizer.Add(self.panels['spells'], 1, wx.EXPAND)

        self.sub_sizer2.Add(self.panels['classes'], 2, wx.EXPAND)
        self.sub_sizer2.Add(self.panels['hp'], 1, wx.EXPAND)
        self.sub_sizer2.Add(self.panels['pp'], 1, wx.EXPAND)
        self.sub_sizer2.Add(self.panels['saves'], 2, wx.EXPAND)

        self.sub_sizer2.Add(self.panels['feats'], 2, wx.EXPAND)
        self.sub_sizer2.Add(self.panels['powers'], 2, wx.EXPAND)
        self.sub_sizer2.Add(self.panels['skills'], 3, wx.EXPAND)

        self.main_sizer.Add(self.sub_sizer,   1, wx.EXPAND)
        self.main_sizer.Add(self.sub_sizer2,   1, wx.EXPAND)
        self.panels['abilities'].panel.char_wnd = self
        self.SetSizer(self.main_sizer)
        self.Bind(wx.EVT_SIZE, self.on_size)


    def on_size(self,evt):
        s = self.GetClientSizeTuple()
        self.SetScrollbars(10, 10,s[0]/10, self.height/10)
        dc = wx.ClientDC(self)
        x = dc.DeviceToLogicalX(0)
        y = dc.DeviceToLogicalY(0)
        self.main_sizer.SetDimension(x,y,s[0],self.height)
        evt.Skip()

    def refresh_data(self):
        self.panels['saves'].panel.refresh_data()
        self.panels['skills'].panel.refresh_data()
        self.panels['attacks'].panel.refresh_data()
        self.panels['powers'].panel.refresh_data()
        self.panels['spells'].panel.refresh_data()

HOWTO_MAX = wx.NewId()

class howto_panel(wx.Panel):
    def __init__(self, parent, handler):
        wx.Panel.__init__(self, parent, -1)
        pname = handler.xml.set("name", 'How To')
        self.sizer = wx.FlexGridSizer(2, 4, 2, 2)  # rows, cols, hgap, vgap
        self.sizer.AddMany([ (wx.StaticText(self, -1, 
                              handler.xml.find('howto').text), 
                              0, wx.ALIGN_CENTER_VERTICAL),
                            ])
        self.sizer.AddGrowableCol(1)
        self.SetSizer(self.sizer)


HP_CUR = wx.NewId()
HP_MAX = wx.NewId()

class hp_panel(wx.Panel):
    def __init__(self, parent, handler):
        wx.Panel.__init__(self, parent, -1)
        pname = handler.xml.set("name", 'HitPoints')
        self.sizer = wx.FlexGridSizer(2, 4, 2, 2)  # rows, cols, hgap, vgap
        self.xml = handler.xml
        self.sizer.AddMany([ (wx.StaticText(self, -1, "HP Current:"),   0, wx.ALIGN_CENTER_VERTICAL),
                 (wx.TextCtrl(self, HP_CUR, self.xml.get('current')),   0, wx.EXPAND),
                 (wx.StaticText(self, -1, "HP Max:"), 0, wx.ALIGN_CENTER_VERTICAL),
                 (wx.TextCtrl(self, HP_MAX, self.xml.get('max')),  0, wx.EXPAND),
                 ])
        self.sizer.AddGrowableCol(1)
        self.SetSizer(self.sizer)
        self.Bind(wx.EVT_SIZE, self.on_size)
        self.Bind(wx.EVT_TEXT, self.on_text, id=HP_MAX)
        self.Bind(wx.EVT_TEXT, self.on_text, id=HP_CUR)

    def on_text(self,evt):
        id = evt.GetId()
        if id == HP_CUR: self.xml.set('current',evt.GetString())
        elif id == HP_MAX: self.xml.set('max',evt.GetString())

    def on_size(self,evt):
        s = self.GetClientSizeTuple()
        self.sizer.SetDimension(0,0,s[0],s[1])

PP_CUR = wx.NewId()
PP_MAX = wx.NewId()
PP_FRE = wx.NewId()
PP_MFRE = wx.NewId()

class pp_panel(wx.Panel):
    def __init__(self, parent, handler):
        wx.Panel.__init__(self, parent, -1)
        pname = handler.xml.set("name", 'PowerPoints')
        self.sizer = wx.FlexGridSizer(2, 4, 2, 2)  # rows, cols, hgap, vgap
        self.xml = handler.xml

        self.sizer.AddMany([ (wx.StaticText(self, -1, "PP Current:"),   0, wx.ALIGN_CENTER_VERTICAL),
                 (wx.TextCtrl(self, PP_CUR, self.xml.get('current1')),   0, wx.EXPAND),
                 (wx.StaticText(self, -1, "PP Max:"), 0, wx.ALIGN_CENTER_VERTICAL),
                 (wx.TextCtrl(self, PP_MAX, self.xml.get('max1')),  0, wx.EXPAND),
                 (wx.StaticText(self, -1, "Current Free Talants per day:"), 0, wx.ALIGN_CENTER_VERTICAL),
                 (wx.TextCtrl(self, PP_FRE, self.xml.get('free')),  0, wx.EXPAND),
                 (wx.StaticText(self, -1, "Max Free Talants per day:"), 0, wx.ALIGN_CENTER_VERTICAL),
                 (wx.TextCtrl(self, PP_MFRE, self.xml.get('maxfree')),  0, wx.EXPAND),
                 ])
        self.sizer.AddGrowableCol(1)
        self.SetSizer(self.sizer)
        self.Bind(wx.EVT_SIZE, self.on_size)
        self.Bind(wx.EVT_TEXT, self.on_text, id=PP_MAX)
        self.Bind(wx.EVT_TEXT, self.on_text, id=PP_CUR)
        self.Bind(wx.EVT_TEXT, self.on_text, id=PP_FRE)
        self.Bind(wx.EVT_TEXT, self.on_text, id=PP_MFRE)

    def on_text(self,evt):
        id = evt.GetId()
        if id == PP_CUR: self.xml.set('current1',evt.GetString())
        elif id == PP_MAX: self.xml.set('max1',evt.GetString())
        elif id == PP_FRE: self.xml.set('free',evt.GetString())
        elif id == PP_MFRE: self.xml.set('maxfree',evt.GetString())

    def on_size(self,evt):
        s = self.GetClientSizeTuple()
        self.sizer.SetDimension(0,0,s[0],s[1])


class gen_grid(wx.grid.Grid):
    """grid for gen info"""
    def __init__(self, parent, handler):
        pname = handler.xml.set("name", 'General')
        wx.grid.Grid.__init__(self, parent, -1, style=wx.SUNKEN_BORDER | wx.WANTS_CHARS)
        self.Bind(wx.EVT_SIZE, self.on_size)
        self.Bind(wx.grid.EVT_GRID_CELL_CHANGE, self.on_cell_change)
        self.handler = handler
        n_list = handler.xml[:]
        self.CreateGrid(len(n_list),2)
        self.SetRowLabelSize(0)
        self.SetColLabelSize(0)
        self.n_list = n_list
        i = 0
        for i in range(len(n_list)): self.refresh_row(i)

    def on_cell_change(self,evt):
        row = evt.GetRow()
        col = evt.GetCol()
        value = self.GetCellValue(row,col)
        self.n_list[row].text = value
        if row==0: self.handler.on_name_change(value)

    def refresh_row(self,rowi):
        self.SetCellValue(rowi,0,self.n_list[rowi].tag)
        self.SetReadOnly(rowi,0)
        self.SetCellValue(rowi,1,self.n_list[rowi].text)

    def on_size(self,evt):
        (w,h) = self.GetClientSizeTuple()
        cols = self.GetNumberCols()
        col_w = w/(cols)
        for i in range(0,cols):  self.SetColSize(i,col_w)
        evt.Skip()
        self.Refresh()

class inventory_grid(wx.grid.Grid):
    """grid for gen info"""
    def __init__(self, parent, handler):
        pname = handler.xml.set("name", 'Money and Inventory')
        wx.grid.Grid.__init__(self, parent, -1, style=wx.SUNKEN_BORDER | wx.WANTS_CHARS)
        self.Bind(wx.EVT_SIZE, self.on_size)
        self.Bind(wx.grid.EVT_GRID_CELL_CHANGE, self.on_cell_change)
        self.handler = handler
        n_list = handler.xml[:]
        self.CreateGrid(len(n_list),2)
        self.SetRowLabelSize(0)
        self.SetColLabelSize(0)
        self.n_list = n_list
        i = 0
        for i in range(len(n_list)): self.refresh_row(i)

    def on_cell_change(self,evt):
        row = evt.GetRow()
        col = evt.GetCol()
        value = self.GetCellValue(row,col)
        self.n_list[row].text = value
        if row==0: self.handler.on_name_change(value)

    def refresh_row(self,rowi):
        self.SetCellValue(rowi,0,self.n_list[rowi].tag)
        self.SetReadOnly(rowi,0)
        self.SetCellValue(rowi,1,self.n_list[rowi].text)

    def on_size(self,evt):
        (w,h) = self.GetClientSizeTuple()
        cols = self.GetNumberCols()
        col_w = w/(cols)
        for i in range(0,cols): self.SetColSize(i,col_w)
        evt.Skip()
        self.Refresh()

class abil_grid(wx.grid.Grid):
    """grid for abilities"""
    def __init__(self, parent, handler):
        pname = handler.xml.set("name", 'Stats')
        wx.grid.Grid.__init__(self, parent, -1, style=wx.SUNKEN_BORDER | wx.WANTS_CHARS)
        self.Bind(wx.EVT_SIZE, self.on_size)
        self.Bind(wx.grid.EVT_GRID_CELL_CHANGE, self.on_cell_change)
        self.handler = handler
        stats = handler.xml.findall('stat')
        self.CreateGrid(len(stats),3)
        self.SetRowLabelSize(0)
        col_names = ['Ability','Score','Modifier']
        for i in range(len(col_names)): self.SetColLabelValue(i,col_names[i])
        self.stats = stats
        i = 0
        for i in range(len(stats)): self.refresh_row(i)
        self.char_wnd = None

    def on_cell_change(self,evt):
        row = evt.GetRow()
        col = evt.GetCol()
        value = self.GetCellValue(row,col)
        try:
            int(value)
            self.stats[row].set('base',value)
            self.refresh_row(row)
        except: self.SetCellValue(row,col,"0")
        if self.char_wnd: self.char_wnd.refresh_data()

    def refresh_row(self,rowi):
        s = self.stats[rowi]
        name = s.get('name')
        abbr = s.get('abbr')
        self.SetCellValue(rowi,0,name)
        self.SetReadOnly(rowi,0)
        self.SetCellValue(rowi,1,s.get('base'))
        self.SetCellValue(rowi,2,str(self.handler.get_mod(abbr)))
        self.SetReadOnly(rowi,2)

    def on_size(self,evt):
        (w,h) = self.GetClientSizeTuple()
        cols = self.GetNumberCols()
        col_w = w/(cols+2)
        self.SetColSize(0,col_w*3)
        for i in range(1,cols): self.SetColSize(i,col_w)
        evt.Skip()
        self.Refresh()

    def refresh_data(self):
        for r in range(self.GetNumberRows()-1): self.refresh_row(r)


class save_grid(wx.grid.Grid):
    """grid for saves"""
    def __init__(self, parent, handler):
        pname = handler.xml.set("name", 'Saves')
        wx.grid.Grid.__init__(self, parent, -1, style=wx.SUNKEN_BORDER | wx.WANTS_CHARS)
        self.Bind(wx.EVT_SIZE, self.on_size)
        self.Bind(wx.grid.EVT_GRID_CELL_CHANGE, self.on_cell_change)
        self.handler = handler
        saves = handler.xml.findall('save')
        self.stats = handler.char_hander.child_handlers['abilities']
        self.CreateGrid(len(saves),7)
        self.SetRowLabelSize(0)
        col_names = ['Save','Key','base','Abil','Magic','Misc','Total']
        for i in range(len(col_names)): self.SetColLabelValue(i,col_names[i])
        self.saves = saves
        i = 0
        for i in range(len(saves)): self.refresh_row(i)

    def on_cell_change(self,evt):
        row = evt.GetRow()
        col = evt.GetCol()
        value = self.GetCellValue(row,col)
        try:
            int(value)
            if col == 2: self.saves[row].set('base',value)
            elif col == 4: self.saves[row].set('magmod',value)
            elif col == 4: self.saves[row].set('miscmod',value)
            self.refresh_row(row)
        except: self.SetCellValue(row,col,"0")

    def refresh_row(self,rowi):
        s = self.saves[rowi]
        name = s.get('name')
        self.SetCellValue(rowi,0,name)
        self.SetReadOnly(rowi,0)
        stat = s.get('stat')
        self.SetCellValue(rowi,1,stat)
        self.SetReadOnly(rowi,1)
        self.SetCellValue(rowi,2,s.get('base'))
        self.SetCellValue(rowi,3,str(self.stats.get_mod(stat)))
        self.SetReadOnly(rowi,3)
        self.SetCellValue(rowi,4,s.get('magmod'))
        self.SetCellValue(rowi,5,s.get('miscmod'))
        mod = str(self.handler.get_mod(name))
        self.SetCellValue(rowi,6,mod)
        self.SetReadOnly(rowi,6)

    def on_size(self,evt):
        (w,h) = self.GetClientSizeTuple()
        cols = self.GetNumberCols()
        col_w = w/(cols+2)
        self.SetColSize(0,col_w*3)
        for i in range(1,cols): self.SetColSize(i,col_w)
        evt.Skip()
        self.Refresh()

    def refresh_data(self):
        for r in range(self.GetNumberRows()): self.refresh_row(r)


class skill_grid(wx.grid.Grid):
    """ panel for skills """
    def __init__(self, parent, handler):
        pname = handler.xml.set("name", 'Skills')
        wx.grid.Grid.__init__(self, parent, -1, style=wx.SUNKEN_BORDER | wx.WANTS_CHARS)
        self.Bind(wx.EVT_SIZE, self.on_size)
        self.Bind(wx.grid.EVT_GRID_CELL_CHANGE, self.on_cell_change)
        self.handler = handler
        skills = handler.xml.findall('skill')
        self.stats = handler.char_hander.child_handlers['abilities']
        self.CreateGrid(len(skills),6)
        self.SetRowLabelSize(0)
        col_names = ['Skill','Key','Rank','Abil','Misc','Total']
        for i in range(len(col_names)): self.SetColLabelValue(i,col_names[i])
        rowi = 0
        self.skills = skills
        for i in range(len(skills)): self.refresh_row(i)

    def on_cell_change(self,evt):
        row = evt.GetRow()
        col = evt.GetCol()
        value = self.GetCellValue(row,col)
        try:
            int(value)
            if col == 2: self.skills[row].set('rank',value)
            elif col == 4: self.skills[row].set('misc',value)
            self.refresh_row(row)
        except: self.SetCellValue(row,col,"0")

    def refresh_row(self,rowi):
        s = self.skills[rowi]
        name = s.get('name')
        self.SetCellValue(rowi,0,name)
        self.SetReadOnly(rowi,0)
        stat = s.get('stat')
        self.SetCellValue(rowi,1,stat)
        self.SetReadOnly(rowi,1)
        self.SetCellValue(rowi,2,s.get('rank'))
        self.SetCellValue(rowi,3,str(self.stats.get_mod(stat)))
        self.SetReadOnly(rowi,3)
        self.SetCellValue(rowi,4,s.get('misc'))
        mod = str(self.handler.get_mod(name))
        self.SetCellValue(rowi,5,mod)
        self.SetReadOnly(rowi,5)

    def on_size(self,evt):
        (w,h) = self.GetClientSizeTuple()
        cols = self.GetNumberCols()
        col_w = w/(cols+2)
        self.SetColSize(0,col_w*3)
        for i in range(1,cols): self.SetColSize(i,col_w)
        evt.Skip()
        self.Refresh()

    def refresh_data(self):
        for r in range(self.GetNumberRows()): self.refresh_row(r)


class feat_panel(wx.Panel):
    def __init__(self, parent, handler):
        pname = handler.xml.set("name", 'Feats')
        wx.Panel.__init__(self, parent, -1)
        self.grid =wx.grid.Grid(self, -1, style=wx.SUNKEN_BORDER | wx.WANTS_CHARS)
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(wx.Button(self, 10, "Remove Feat"), 1, wx.EXPAND)
        sizer.Add(wx.Size(10,10))
        sizer.Add(wx.Button(self, 20, "Add Feat"), 1, wx.EXPAND)
        self.sizer = sizer
        self.Bind(wx.EVT_SIZE, self.on_size)
        self.Bind(wx.EVT_BUTTON, self.on_remove, id=10)
        self.Bind(wx.EVT_BUTTON, self.on_add, id=20)

        n_list = handler.xml[:]
        self.n_list = n_list
        self.xml = handler.xml
        self.grid.CreateGrid(len(n_list),2,1)
        self.grid.SetRowLabelSize(0)
        self.grid.SetColLabelValue(0,"Feat")
        self.grid.SetColLabelValue(1,"Type")
        for i in range(len(n_list)): self.refresh_row(i)
        self.temp_dom = None
        self.SetSizer(self.sizer)

    def refresh_row(self,i):
        feat = self.n_list[i]
        name = feat.get('name')
        type = feat.get('type')
        self.grid.SetCellValue(i,0,name)
        self.grid.SetReadOnly(i,0)
        self.grid.SetCellValue(i,1,type)
        self.grid.SetReadOnly(i,1)

    def on_remove(self,evt):
        rows = self.grid.GetNumberRows()
        for i in range(rows):
            if self.grid.IsInSelection(i,0):
                self.grid.DeleteRows(i)
                self.xml.removeChild(self.n_list[i])

    def on_add(self,evt):
        if not self.temp_dom:
            tree = parse(orpg.dirpath.dir_struct["d20"]+"d20feats.xml")
            self.temp_dom = tree.getroot()
        f_list = self.temp_dom.findall('feat')
        opts = []
        for f in f_list: opts.append(f.get('name'))
        dlg = wx.SingleChoiceDialog(self,'Choose Feat','Feats',opts)
        if dlg.ShowModal() == wx.ID_OK:
            i = dlg.GetSelection()
            new_node = self.xml.append(XML(tostring(f_list[i])))
            self.grid.AppendRows(1)
            self.n_list = self.xml.findall('feat')
            self.refresh_row(self.grid.GetNumberRows()-1)
        dlg.Destroy()

    def on_size(self,event):
        s = self.GetClientSizeTuple()
        self.grid.SetDimensions(0,0,s[0],s[1]-25)
        self.sizer.SetDimension(0,s[1]-25,s[0],25)
        (w,h) = self.grid.GetClientSizeTuple()
        cols = self.grid.GetNumberCols()
        col_w = w/(cols)
        for i in range(0,cols): self.grid.SetColSize(i,col_w)

class spell_panel(wx.Panel):
    def __init__(self, parent, handler):
        pname = handler.xml.set("name", 'Arcane Spells')
        wx.Panel.__init__(self, parent, -1)
        self.grid =wx.grid.Grid(self, -1, style=wx.SUNKEN_BORDER | wx.WANTS_CHARS)
        self.handler = handler
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(wx.Button(self, 10, "Remove Spell"), 1, wx.EXPAND)
        sizer.Add(wx.Size(10,10))
        sizer.Add(wx.Button(self, 20, "Add Spell"), 1, wx.EXPAND)
        sizer.Add(wx.Size(10,10))
        sizer.Add(wx.Button(self, 30, "Refresh Spells"), 1, wx.EXPAND)
        self.sizer = sizer
        self.SetSizer(self.sizer)
        self.Bind(wx.EVT_SIZE, self.on_size)
        self.Bind(wx.EVT_BUTTON, self.on_remove, id=10)
        self.Bind(wx.EVT_BUTTON, self.on_add, id=20)
        self.Bind(wx.EVT_BUTTON, self.on_refresh_spells, id=30)
        self.grid.Bind(wx.grid.EVT_GRID_CELL_CHANGE, self.on_cell_change)
        n_list = handler.xml[:]
        self.n_list = n_list
        self.xml = handler.xml
        self.grid.CreateGrid(len(n_list),4,1)
        self.grid.SetRowLabelSize(0)
        self.grid.SetColLabelValue(0,"No.")
        self.grid.SetColLabelValue(1,"Lvl")
        self.grid.SetColLabelValue(2,"Spell")
        self.grid.SetColLabelValue(3,"Desc")
        for i in range(len(n_list)): self.refresh_row(i)
        self.temp_dom = None

    def on_cell_change(self,evt):
        row = evt.GetRow()
        col = evt.GetCol()
        value = self.grid.GetCellValue(row,col)
        if col == 0: self.n_list[row].set('memrz',value)

    def refresh_row(self,i):
        spell = self.n_list[i]
        memrz = spell.get('memrz')
        name = spell.get('name')
        type = spell.get('desc')
        level = spell.get('level')
        self.grid.SetCellValue(i,0,memrz)
        self.grid.SetCellValue(i,2,name)
        self.grid.SetReadOnly(i,2)
        self.grid.SetCellValue(i,3,type)
        self.grid.SetReadOnly(i,3)
        self.grid.SetCellValue(i,1,level)
        self.grid.SetReadOnly(i,1)

    def on_remove(self,evt):
        rows = self.grid.GetNumberRows()
        for i in range(rows):
            if self.grid.IsInSelection(i,0):
                self.grid.DeleteRows(i)
                self.xml.removeChild(self.n_list[i])
                self.handler.refresh_spells()

    def on_add(self,evt):
        if not self.temp_dom:
            tree = parse(orpg.dirpath.dir_struct["d20"]+"d20spells.xml")
            self.temp_dom = tree.getroot()
        f_list = self.temp_dom.findall('spell')
        opts = []
        for f in f_list: opts.append("(" + f.get('level') + ")" + f.get('name'))
        dlg = wx.SingleChoiceDialog(self,'Choose Spell','Spells',opts)
        if dlg.ShowModal() == wx.ID_OK:
            i = dlg.GetSelection()
            new_node = self.xml.append(XML(tostring(f_list[i])))
            self.grid.AppendRows(1)
            self.n_list = self.xml.findall('spell')
            self.refresh_row(self.grid.GetNumberRows()-1)
            self.handler.refresh_spells()
        dlg.Destroy()

    def on_refresh_spells( self, evt ):
        f_list = self.xml.findall('spell')
        for spell in f_list: spell.set( 'used', '0' )

    def on_size(self,event):
        s = self.GetClientSizeTuple()
        self.grid.SetDimensions(0,0,s[0],s[1]-25)
        self.sizer.SetDimension(0,s[1]-25,s[0],25)
        (w,h) = self.grid.GetClientSizeTuple()
        cols = self.grid.GetNumberCols()
        col_w = w/(cols)
        for i in range(0,cols): self.grid.SetColSize(i,col_w)
        self.grid.SetColSize(0,w * 0.10)
        self.grid.SetColSize(1,w * 0.10)
        self.grid.SetColSize(2,w * 0.30)
        self.grid.SetColSize(3,w * 0.50)

    def refresh_data(self):
        for i in range(len(self.n_list)): self.refresh_row(i)

class divine_panel(wx.Panel):
    def __init__(self, parent, handler):
        pname = handler.xml.set("name", 'Divine Spells')
        wx.Panel.__init__(self, parent, -1)
        self.grid =wx.grid.Grid(self, -1, style=wx.SUNKEN_BORDER | wx.WANTS_CHARS)
        self.handler = handler
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(wx.Button(self, 10, "Remove Spell"), 1, wx.EXPAND)
        sizer.Add(wx.Size(10,10))
        sizer.Add(wx.Button(self, 20, "Add Spell"), 1, wx.EXPAND)
        sizer.Add(wx.Size(10,10))
        sizer.Add(wx.Button(self, 30, "Refresh Spells"), 1, wx.EXPAND)
        self.sizer = sizer
        self.SetSizer(self.sizer)
        self.Bind(wx.EVT_SIZE, self.on_size)
        self.Bind(wx.EVT_BUTTON, self.on_remove, id=10)
        self.Bind(wx.EVT_BUTTON, self.on_add, id=20)
        self.Bind(wx.EVT_BUTTON, self.on_refresh_spells, id=30)
        self.grid.Bind(wx.grid.EVT_GRID_CELL_CHANGE, self.on_cell_change)
        n_list = handler.xml[:]
        self.n_list = n_list
        self.xml = handler.xml
        self.grid.CreateGrid(len(n_list),4,1)
        self.grid.SetRowLabelSize(0)
        self.grid.SetColLabelValue(0,"No.")
        self.grid.SetColLabelValue(1,"Lvl")
        self.grid.SetColLabelValue(2,"Spell")
        self.grid.SetColLabelValue(3,"Desc")
        for i in range(len(n_list)): self.refresh_row(i)
        self.temp_dom = None

    def on_cell_change(self,evt):
        row = evt.GetRow()
        col = evt.GetCol()
        value = self.grid.GetCellValue(row,col)
        if col == 0: self.n_list[row].set('memrz',value)


    def refresh_row(self,i):
        spell = self.n_list[i]
        memrz = spell.get('memrz')
        name = spell.get('name')
        type = spell.get('desc')
        level = spell.get('level')
        self.grid.SetCellValue(i,0,memrz)
        self.grid.SetCellValue(i,2,name)
        self.grid.SetReadOnly(i,2)
        self.grid.SetCellValue(i,3,type)
        self.grid.SetReadOnly(i,3)
        self.grid.SetCellValue(i,1,level)
        self.grid.SetReadOnly(i,1)

    def on_remove(self,evt):
        rows = self.grid.GetNumberRows()
        for i in range(rows):
            if self.grid.IsInSelection(i,0):
                self.grid.DeleteRows(i)
                self.xml.remove(self.n_list[i])
                self.handler.refresh_spells()

    def on_add(self,evt):
        if not self.temp_dom:
            tree = parse(orpg.dirpath.dir_struct["d20"]+"d20divine.xml")
            self.temp_dom = tree.getroot()
        f_list = self.temp_dom.findall('gift')
        opts = []
        for f in f_list: opts.append("(" + f.get('level') + ")" + f.get('name'))
        dlg = wx.SingleChoiceDialog(self,'Choose Spell','Spells',opts)
        if dlg.ShowModal() == wx.ID_OK:
            i = dlg.GetSelection()
            new_node = self.xml.append(XML(tostring(f_list[i])))
            self.grid.AppendRows(1)
            self.n_list = self.xml.findall('gift')
            self.refresh_row(self.grid.GetNumberRows()-1)
            self.handler.refresh_spells()
        dlg.Destroy()

    def on_refresh_spells( self, evt ):
        f_list = self.xml.findall('gift')
        for spell in f_list: spell.set( 'used', '0' )

    def on_size(self,event):
        s = self.GetClientSizeTuple()
        self.grid.SetDimensions(0,0,s[0],s[1]-25)
        self.sizer.SetDimension(0,s[1]-25,s[0],25)
        (w,h) = self.grid.GetClientSizeTuple()
        cols = self.grid.GetNumberCols()
        col_w = w/(cols)
        for i in range(0,cols): self.grid.SetColSize(i,col_w)
        self.grid.SetColSize(0,w * 0.10)
        self.grid.SetColSize(1,w * 0.10)
        self.grid.SetColSize(2,w * 0.30)
        self.grid.SetColSize(3,w * 0.50)

    def refresh_data(self):
        for i in range(len(self.n_list)): self.refresh_row(i)


class power_panel(wx.Panel):
    def __init__(self, parent, handler):
        pname = handler.xml.set("name", 'Pionic Powers')
        wx.Panel.__init__(self, parent, -1)
        self.grid =wx.grid.Grid(self, -1, style=wx.SUNKEN_BORDER | wx.WANTS_CHARS)
        self.handler = handler
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(wx.Button(self, 10, "Remove Power"), 1, wx.EXPAND)
        sizer.Add(wx.Size(10,10))
        sizer.Add(wx.Button(self, 20, "Add Power"), 1, wx.EXPAND)
        sizer.Add(wx.Size(10,10))
        sizer.Add(wx.Button(self, 30, "Refresh Powers"), 1, wx.EXPAND)
        self.sizer = sizer
        self.Bind(wx.EVT_SIZE, self.on_size)
        self.Bind(wx.EVT_BUTTON, self.on_remove, id=10)
        self.Bind(wx.EVT_BUTTON, self.on_add, id=20)
        self.Bind(wx.EVT_BUTTON, self.on_refresh_powers, id=30)
        self.grid.Bind(wx.grid.EVT_GRID_CELL_CHANGE, self.on_cell_change)
        n_list = handler.xml[:]
        self.n_list = n_list
        self.xml = handler.xml
        self.grid.CreateGrid(len(n_list),5,1)
        self.grid.SetRowLabelSize(0)
        self.grid.SetColLabelValue(0,"PP")
        self.grid.SetColLabelValue(1,"Lvl")
        self.grid.SetColLabelValue(2,"Power")
        self.grid.SetColLabelValue(3,"Desc")
        self.grid.SetColLabelValue(4,"Type")
        for i in range(len(n_list)): self.refresh_row(i)
        self.refresh_data()
        self.temp_dom = None
        self.SetSizer(self.sizer)

    def on_cell_change(self,evt):
        row = evt.GetRow()
        col = evt.GetCol()
        value = self.grid.GetCellValue(row,col)

    def refresh_row(self,i):
        power = self.n_list[i]
        point = power.get('point')
        name = power.get('name')
        type = power.get('desc')
        test = power.get('test')
        level = power.get('level')
        self.grid.SetCellValue(i,0,point)
        self.grid.SetReadOnly(i,0)
        self.grid.SetCellValue(i,1,level)
        self.grid.SetReadOnly(i,1)
        self.grid.SetCellValue(i,2,name)
        self.grid.SetReadOnly(i,2)
        self.grid.SetCellValue(i,3,type)
        self.grid.SetReadOnly(i,3)
        self.grid.SetCellValue(i,4,test)
        self.grid.SetReadOnly(i,4)

    def on_remove(self,evt):
        rows = self.grid.GetNumberRows()
        for i in range(rows):
            if self.grid.IsInSelection(i,0):
                self.grid.DeleteRows(i)
                self.xml.removeChild(self.n_list[i])
                self.handler.refresh_powers()

    def on_add(self,evt):
        if not self.temp_dom:
            tree = parse(orpg.dirpath.dir_struct["d20"]+"d20powers.xml")
            self.temp_dom = tree.getroot()
        f_list = self.temp_dom.findall('power')
        opts = []
        for f in f_list: opts.append("(" + f.get('level') + ") - " + f.get('name') + " - " + f.get('test'))
        dlg = wx.SingleChoiceDialog(self,'Choose Power','Powers',opts)
        if dlg.ShowModal() == wx.ID_OK:
            i = dlg.GetSelection()
            new_node = self.xml.append(XML(tostring(f_list[i])))
            self.grid.AppendRows(1)
            self.n_list = self.xml.findall('power')
            self.refresh_row(self.grid.GetNumberRows()-1)
            self.handler.refresh_powers()
        dlg.Destroy()

    def on_remove(self,evt):
        rows = self.grid.GetNumberRows()
        for i in range(rows):
            if self.grid.IsInSelection(i,0):
                self.grid.DeleteRows(i)
                self.xml.remove(self.n_list[i])
                self.n_list = self.xml.findall('weapon')
                self.handler.refresh_weapons()

    def on_refresh_powers( self, evt ):
        mfre = self.handler.get_char_pp('maxfree')
        mpp = self.handler.get_char_pp('max1')
        self.handler.set_char_pp( 'free', mfre )
        self.handler.set_char_pp( 'current1', mpp )

    def on_size(self,event):
        s = self.GetClientSizeTuple()
        self.grid.SetDimensions(0,0,s[0],s[1]-25)
        self.sizer.SetDimension(0,s[1]-25,s[0],25)
        (w,h) = self.grid.GetClientSizeTuple()
        cols = self.grid.GetNumberCols()
        col_w = w/(cols)
        for i in range(0,cols): self.grid.SetColSize(i,col_w)
        self.grid.SetColSize(0,w * 0.05)
        self.grid.SetColSize(1,w * 0.05)
        self.grid.SetColSize(2,w * 0.30)
        self.grid.SetColSize(3,w * 0.30)
        self.grid.SetColSize(4,w * 0.30)

    def refresh_data(self):
        for i in range(len(self.n_list)): self.refresh_row(i)

class attack_grid(wx.grid.Grid):
    """grid for attacks"""
    def __init__(self, parent, handler):
        pname = handler.xml.set("name", 'Melee')
        wx.grid.Grid.__init__(self, parent, -1, style=wx.SUNKEN_BORDER | wx.WANTS_CHARS)
        self.parent = parent
        self.handler = handler
        self.babs = self.handler.melee
        self.CreateGrid(1,7)
        self.SetRowLabelSize(0)
        col_names = ['base','base 2','base 3','base 4','base 5','base 6','misc']
        for i in range(len(col_names)): self.SetColLabelValue(i,col_names[i])
        self.refresh_data()
        self.Bind(wx.EVT_SIZE, self.on_size)
        self.Bind(wx.grid.EVT_GRID_CELL_CHANGE, self.on_cell_change)

    def on_cell_change(self,evt):
        row = evt.GetRow()
        col = evt.GetCol()
        value = self.GetCellValue(row,col)
        try: int(value)
        except:
            value = "0"
            self.SetCellValue( row, col, value )
        attribs = ['base','second','third','forth','fifth','sixth','misc']
        self.babs.set( attribs[col], value )
        self.parent.refresh_data()

    def refresh_data(self):
        attack_mods = self.handler.get_attack_data()
        for i in range(0,7): self.SetCellValue( 0, i, str(attack_mods[i]) )

    def on_size(self,evt):
        (w,h) = self.GetClientSizeTuple()
        cols = self.GetNumberCols()
        col_w = w/cols
        for i in range(0,cols): self.SetColSize(i,col_w)
        evt.Skip()
        self.Refresh()

class weapon_panel(wx.Panel):
    def __init__(self, parent, handler):
        pname = handler.xml.set("name", 'Weapons')
        wx.Panel.__init__(self, parent, -1)
        self.grid =wx.grid.Grid(self, -1, style=wx.SUNKEN_BORDER | wx.WANTS_CHARS)
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(wx.Button(self, 10, "Remove Weapon"), 1, wx.EXPAND)
        sizer.Add(wx.Size(10,10))
        sizer.Add(wx.Button(self, 20, "Add Weapon"), 1, wx.EXPAND)
        self.sizer = sizer
        self.Bind(wx.EVT_SIZE, self.on_size)
        self.Bind(wx.EVT_BUTTON, self.on_remove, id=10)
        self.Bind(wx.EVT_BUTTON, self.on_add, id=20)
        self.grid.Bind(wx.grid.EVT_GRID_CELL_CHANGE, self.on_cell_change)
        n_list = handler.xml.findall('weapon')
        self.n_list = n_list
        self.xml = handler.xml
        self.handler = handler
        self.grid.CreateGrid(len(n_list),8,1)
        self.grid.SetRowLabelSize(0)
        col_names = ['Name','damage','mod','critical','type','weight','range','size']
        for i in range(len(col_names)): self.grid.SetColLabelValue(i,col_names[i])
        self.refresh_data()
        self.temp_dom = None
        self.SetSizer(self.sizer)

    def on_cell_change(self,evt):
        row = evt.GetRow()
        col = evt.GetCol()
        value = self.grid.GetCellValue(row,col)
        if col == 0:
            self.n_list[row].set('name',value)
            self.handler.refresh_weapons();
        else: self.n_list[row].set(self.grid.GetColLabelValue(col),value)

    def refresh_row(self,i):
        n = self.n_list[i]
        name = n.get('name')
        mod = n.get('mod')
        ran = n.get('range')
        self.grid.SetCellValue(i,0,name)
        self.grid.SetCellValue(i,1,n.get('damage'))
        self.grid.SetCellValue(i,2,mod)
        self.grid.SetCellValue(i,3,n.get('critical'))
        self.grid.SetCellValue(i,4,n.get('type'))
        self.grid.SetCellValue(i,5,n.get('weight'))
        self.grid.SetCellValue(i,6,ran)
        self.grid.SetCellValue(i,7,n.get('size') )

    def on_remove(self,evt):
        rows = self.grid.GetNumberRows()
        for i in range(rows):
            if self.grid.IsInSelection(i,0):
                self.grid.DeleteRows(i)
                self.xml.remove(self.n_list[i])
                self.n_list = self.xml.findall('weapon')
                self.handler.refresh_weapons()

    def on_add(self,evt):
        if not self.temp_dom:
            tree = parse(orpg.dirpath.dir_struct["d20"]+"d20weapons.xml")
            self.temp_dom = tree.getroot()
        f_list = self.temp_dom.findall('weapon')
        opts = []
        for f in f_list: opts.append(f.get('name'))
        dlg = wx.SingleChoiceDialog(self,'Choose Weapon','Weapon List',opts)
        if dlg.ShowModal() == wx.ID_OK:
            i = dlg.GetSelection()
            new_node = self.xml.append(XML(tostring(f_list[i])))
            self.grid.AppendRows(1)
            self.n_list = self.xml.findall('weapon')
            self.refresh_row(self.grid.GetNumberRows()-1)
            self.handler.refresh_weapons()
        dlg.Destroy()

    def on_size(self,event):
        s = self.GetClientSizeTuple()
        self.grid.SetDimensions(0,0,s[0],s[1]-25)
        self.sizer.SetDimension(0,s[1]-25,s[0],25)
        (w,h) = self.grid.GetClientSizeTuple()
        cols = self.grid.GetNumberCols()
        col_w = w/(cols+1)
        self.grid.SetColSize(0,col_w*2)
        for i in range(1,cols): self.grid.SetColSize(i,col_w)

    def refresh_data(self):
        for i in range(len(self.n_list)): self.refresh_row(i)


class attack_panel(wx.Panel):
    def __init__(self, parent, handler):
        pname = handler.xml.set("name", 'Melee')
        wx.Panel.__init__(self, parent, -1)

        self.a_grid = attack_grid(self, handler)
        self.w_panel = weapon_panel(self, handler)
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.a_grid, 1, wx.EXPAND)
        self.sizer.Add(self.w_panel, 2, wx.EXPAND)
        self.Bind(wx.EVT_SIZE, self.on_size)
        self.SetSizer(self.sizer)

    def on_size(self,event):
        s = self.GetClientSizeTuple()
        self.sizer.SetDimension(0,0,s[0],s[1])

    def refresh_data(self):
        self.w_panel.refresh_data()
        self.a_grid.refresh_data()


class ac_panel(wx.Panel):
    def __init__(self, parent, handler):
        pname = handler.xml.set("name", 'Armor')
        wx.Panel.__init__(self, parent, -1)
        self.grid =wx.grid.Grid(self, -1, style=wx.SUNKEN_BORDER | wx.WANTS_CHARS)
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(wx.Button(self, 10, "Remove Armor"), 1, wx.EXPAND)
        sizer.Add(wx.Size(10,10))
        sizer.Add(wx.Button(self, 20, "Add Armor"), 1, wx.EXPAND)
        self.sizer = sizer
        self.Bind(wx.EVT_SIZE, self.on_size)
        self.Bind(wx.EVT_BUTTON, self.on_remove, id=10)
        self.Bind(wx.EVT_BUTTON, self.on_add, id=20)
        self.grid.Bind(wx.grid.EVT_GRID_CELL_CHANGE, self.on_cell_change)
        self.xml = handler.xml
        n_list = handler.xml[:]
        self.n_list = n_list
        col_names = ['Armor','bonus','maxdex','cp','sf','weight','speed','type']
        self.grid.CreateGrid(len(n_list),len(col_names),1)
        self.grid.SetRowLabelSize(0)
        for i in range(len(col_names)): self.grid.SetColLabelValue(i,col_names[i])
        self.atts =['name','bonus','maxdex','checkpenalty','spellfailure','weight','speed','type']
        for i in range(len(n_list)): self.refresh_row(i)
        self.temp_dom = None
        self.SetSizer(self.sizer)

    def on_cell_change(self,evt):
        row = evt.GetRow()
        col = evt.GetCol()
        value = self.grid.GetCellValue(row,col)
        if col >= 1 and col <= 5:
            try:
                int(value)
                self.n_list[row].set(self.atts[col],value)
            except: self.grid.SetCellValue(row,col,"0")
        else: self.n_list[row].set(self.atts[col],value)

    def refresh_row(self,i):
        n = self.n_list[i]
        for y in range(len(self.atts)):
            self.grid.SetCellValue(i,y,n.get(self.atts[y]))

    def on_remove(self,evt):
        rows = self.grid.GetNumberRows()
        for i in range(rows):
            if self.grid.IsInSelection(i,0):
                self.grid.DeleteRows(i)
                self.xml.remove(self.n_list[i])

    def on_add(self,evt):
        if not self.temp_dom:
            tree = parse(orpg.dirpath.dir_struct["d20"]+"d20armor.xml")
            self.temp_dom = tree.getroot()
        f_list = self.temp_dom.findall('armor')
        opts = []
        for f in f_list: opts.append(f.get('name'))
        dlg = wx.SingleChoiceDialog(self,'Choose Armor:','Armor List',opts)
        if dlg.ShowModal() == wx.ID_OK:
            i = dlg.GetSelection()
            new_node = self.xml.append(XML(tostring(f_list[i])))
            self.grid.AppendRows(1)
            self.n_list = self.xml.findall('armor')
            self.refresh_row(self.grid.GetNumberRows()-1)
        dlg.Destroy()

    def on_size(self,event):
        s = self.GetClientSizeTuple()
        self.grid.SetDimensions(0,0,s[0],s[1]-25)
        self.sizer.SetDimension(0,s[1]-25,s[0],25)
        (w,h) = self.grid.GetClientSizeTuple()
        cols = self.grid.GetNumberCols()
        col_w = w/(cols+2)
        self.grid.SetColSize(0,col_w*3)
        for i in range(1,cols): self.grid.SetColSize(i,col_w)


class class_panel(wx.Panel):
    def __init__(self, parent, handler):
        pname = handler.xml.set("name", 'Class')
        wx.Panel.__init__(self, parent, -1)
        self.grid =wx.grid.Grid(self, -1, style=wx.SUNKEN_BORDER | wx.WANTS_CHARS)
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(wx.Button(self, 10, "Remove Class"), 1, wx.EXPAND)
        sizer.Add(wx.Size(10,10))
        sizer.Add(wx.Button(self, 20, "Add Class"), 1, wx.EXPAND)
        self.sizer = sizer
        self.SetSizer(self.sizer)
        self.Bind(wx.EVT_SIZE, self.on_size)
        self.Bind(wx.EVT_BUTTON, self.on_remove, id=10)
        self.Bind(wx.EVT_BUTTON, self.on_add, id=20)
        self.grid.Bind(wx.grid.EVT_GRID_CELL_CHANGE, self.on_cell_change)

        n_list = handler.xml[:]
        self.n_list = n_list
        self.xml = handler.xml
        self.grid.CreateGrid(len(n_list),2,1)
        self.grid.SetRowLabelSize(0)
        self.grid.SetColLabelValue(0,"Class")
        self.grid.SetColLabelValue(1,"Level")
        for i in range(len(n_list)): self.refresh_row(i)
        self.temp_dom = None

    def on_cell_change(self,evt):
        row = evt.GetRow()
        col = evt.GetCol()
        value = self.grid.GetCellValue(row,col)
        try:
            int(value)
            self.n_list[row].set('level',value)
        except: self.grid.SetCellValue(row,col,"1")

    def refresh_row(self,i):
        n = self.n_list[i]
        name = n.get('name')
        level = n.get('level')
        self.grid.SetCellValue(i,0,name)
        self.grid.SetReadOnly(i,0)
        self.grid.SetCellValue(i,1,level)

    def on_remove(self,evt):
        rows = self.grid.GetNumberRows()
        for i in range(rows):
            if self.grid.IsInSelection(i,0):
                self.grid.DeleteRows(i)
                self.xml.remove(self.n_list[i])

    def on_add(self,evt):
        if not self.temp_dom:
            tree = parse(orpg.dirpath.dir_struct["d20"]+"d20classes.xml")
            self.temp_dom = tree.getroot()
        f_list = self.temp_dom.findall('class')
        opts = []
        for f in f_list: opts.append(f.get('name'))
        dlg = wx.SingleChoiceDialog(self,'Choose Class','Classes',opts)
        if dlg.ShowModal() == wx.ID_OK:
            i = dlg.GetSelection()
            new_node = self.xml.append(XML(tostring(f_list[i])))
            self.grid.AppendRows(1)
            self.n_list = self.xml.findall('class')
            self.refresh_row(self.grid.GetNumberRows()-1)
        dlg.Destroy()

    def on_size(self,event):
        s = self.GetClientSizeTuple()
        self.grid.SetDimensions(0,0,s[0],s[1]-25)
        self.sizer.SetDimension(0,s[1]-25,s[0],25)
        (w,h) = self.grid.GetClientSizeTuple()
        cols = self.grid.GetNumberCols()
        col_w = w/(cols)
        for i in range(0,cols): self.grid.SetColSize(i,col_w)
