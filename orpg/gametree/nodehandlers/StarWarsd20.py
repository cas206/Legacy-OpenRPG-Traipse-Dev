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
# File: StarWarsd20.py
# Author: Chris Davis; Mark Twombley
# Maintainer: Mark Twombley
# Version:
#   $Id: StarWarsd20.py,v 1.18 2006/11/15 12:11:23 digitalxero Exp $
#
# Description: The file contains code for the StarWarsd20 nodehanlers
#

__version__ = "$Id: StarWarsd20.py,v 1.18 2006/11/15 12:11:23 digitalxero Exp $"

from core import *

SWD20_EXPORT = wx.NewId()
############################
## StarWarsd20 character node handler
############################
##The whole look and easy of use redone by Digitalxero
class container_handler(node_handler):
    """ should not be used! only a base class!
    <nodehandler name='?'  module='core' class='container_handler'  />
    """
    def __init__(self,xml_dom,tree_node):
        node_handler.__init__(self,xml_dom,tree_node)
        self.load_children()

    def load_children(self):
        children = self.master_dom._get_childNodes()
        for c in children:
            self.tree.load_xml(c,self.mytree_node)


    def on_drop(self,evt):
        drag_obj = self.tree.drag_obj
        #if self.is_my_child(self.mytree_node,drag_obj.mytree_node):
        #    return
        if drag_obj == self:
            return
        opt = wx.MessageBox("Add node as child?","Container Node",wx.YES_NO|wx.CANCEL)
        if opt == wx.YES:
            xml_dom = self.tree.drag_obj.delete()
            xml_dom = self.master_dom.insertBefore(xml_dom,None)
            self.tree.load_xml(xml_dom, self.mytree_node)
            self.tree.Expand(self.mytree_node)
        elif opt == wx.NO:
            node_handler.on_drop(self,evt)

    def tohtml(self):
        cookie = 0
        html_str = "<table border=\"1\" ><tr><td>"
        html_str += "<b>"+self.master_dom.getAttribute("name") + "</b>"
        html_str += "</td></tr>\n"
        html_str += "<tr><td>"
        max = tree.GetChildrenCount(handler.mytree_node)
        try:
            (child,cookie)=self.tree.GetFirstChild(self.mytree_node,cookie)
        except: # If this happens we probably have a newer version of wxPython
            (child,cookie)=self.tree.GetFirstChild(self.mytree_node)
        obj = self.tree.GetPyData(child)
        for m in xrange(max):
            html_str += "<p>" + obj.tohtml()
            if m < max-1:
                child = self.tree.GetNextSibling(child)
                obj = self.tree.GetPyData(child)
        html_str += "</td></tr></table>"
        return html_str

    def get_size_constraint(self):
        return 1

    def get_char_name( self ):
        return self.child_handlers['general'].get_char_name()

##    def set_char_pp(self,attr,evl):
##        return self.child_handlers['pp'].set_char_pp(attr,evl)
##
##    def get_char_pp( self, attr ):
##        return self.child_handlers['pp'].get_char_pp(attr)
##
    def get_char_lvl( self, attr ):
        return self.child_handlers['classes'].get_char_lvl(attr)



class SWd20char_handler(node_handler):
    """ Node handler for a SWd20 charactor
        <nodehandler name='?'  module='StarWarsd20' class='SWd20char_handler'  />
    """
    def __init__(self,xml_dom,tree_node):
        node_handler.__init__(self,xml_dom,tree_node)
        self.frame = component.get('frame')
        self.child_handlers = {}
        self.new_child_handler('howtouse','HowTO use this tool',SWd20howto,'note')
        self.new_child_handler('general','General Information',SWd20general,'gear')
        self.new_child_handler('inventory','Money and Inventory',SWd20inventory,'money')
        self.new_child_handler('abilities','Abilities Scores',SWd20ability,'gear')
        self.new_child_handler('classes','Classes',SWd20classes,'knight')
        self.new_child_handler('saves','Saves',SWd20saves,'skull')
        self.new_child_handler('skills','Skills',SWd20skill,'book')
        self.new_child_handler('feats','Feats',SWd20feats,'book')
        self.new_child_handler('wp','Wound Points',SWd20hp,'gear')
        self.new_child_handler('vp','Vitality Points',SWd20vp,'gear')
        self.new_child_handler('attacks','Attacks',SWd20attacks,'spears')
        self.new_child_handler('ac','Armor',SWd20armor,'spears')
        self.myeditor = None


    def on_version(self,old_version):
        node_handler.on_version(self,old_version)
        if old_version == "":
            tmp = open(dir_struct["nodes"]+"StarWars_d20character.xml","r")
            xml_dom = parseXml_with_dlg(self.tree,tmp.read())
            xml_dom = xml_dom._get_firstChild()
            tmp.close()
            ## add new nodes
            for tag in ("howtouse","inventory","powers","divine","pp"):
                node_list = xml_dom.getElementsByTagName(tag)
                self.master_dom.appendChild(node_list[0])

            ## add new atts
            melee_attack = self.master_dom.getElementsByTagName('melee')[0]
            melee_attack.setAttribute("second","0")
            melee_attack.setAttribute("third","0")
            melee_attack.setAttribute("forth","0")
            melee_attack.setAttribute("fifth","0")
            melee_attack.setAttribute("sixth","0")
            range_attack = self.master_dom.getElementsByTagName('ranged')[0]
            range_attack.setAttribute("second","0")
            range_attack.setAttribute("third","0")
            range_attack.setAttribute("forth","0")
            range_attack.setAttribute("fifth","0")
            range_attack.setAttribute("sixth","0")

            gen_list = self.master_dom.getElementsByTagName('general')[0]

            for tag in ("currentxp","xptolevel"):
                node_list = xml_dom.getElementsByTagName(tag)
                gen_list.appendChild(node_list[0])
            ## temp fix
            #parent = self.master_dom._get_parentNode()
            #old_dom = parent.replaceChild(xml_dom,self.master_dom)
            #self.master_dom = xml_dom
        print old_version


    def get_char_name( self ):
        return self.child_handlers['general'].get_char_name()

##    def set_char_pp(self,attr,evl):
##        return self.child_handlers['pp'].set_char_pp(attr,evl)
##
##    def get_char_pp( self, attr ):
##        return self.child_handlers['pp'].get_char_pp(attr)

    def get_char_lvl( self, attr ):
        return self.child_handlers['classes'].get_char_lvl(attr)


    def new_child_handler(self,tag,text,handler_class,icon='gear'):
        node_list = self.master_dom.getElementsByTagName(tag)
        tree = self.tree
        i = self.tree.icons[icon]
        new_tree_node = tree.AppendItem(self.mytree_node,text,i,i)
        handler = handler_class(node_list[0],new_tree_node,self)
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
        #html_str += "<P>" + self.child_handlers['spells'].tohtml()
        #html_str += "<P>" + self.child_handlers['divine'].tohtml()
        #html_str += "<P>" + self.child_handlers['powers'].tohtml()
        html_str += "<P>" + self.child_handlers['inventory'].tohtml() +"</td>"
        html_str += "<td width='50%' valign=top >"+self.child_handlers['classes'].tohtml()
        html_str += "<P>" + self.child_handlers['wp'].tohtml()
        html_str += "<P>" + self.child_handlers['vp'].tohtml()
        #html_str += "<P>" + self.child_handlers['pp'].tohtml()
        html_str += "<P>" + self.child_handlers['skills'].tohtml() +"</td>"
        html_str += "</tr></table>"
        return html_str

    def about(self):
        html_str = "<img src='" + dir_struct["icon"]+'d20_logo.gif' "><br /><b>d20 Character Tool v0.7 beta</b>"
        html_str += "<br />by Chris Davis<br />chris@rpgarchive.com"
        return html_str

    def get_char_name( self ):
        return self.child_handlers['general'].get_char_name()
    def get_armor_class( self ):
        return self.child_handlers['ac'].get_armor_class()
    def get_max_hp( self ):
        return self.child_handlers['wp'].get_max_hp()
    def get_current_hp( self ):
        return self.child_handlers['wp'].get_current_hp()
    def get_max_vp( self ):
        return self.child_handlers['vp'].get_max_vp()
    def get_current_vp( self ):
        return self.child_handlers['vp'].get_current_vp()

##    def set_char_pp(self,attr,evl):
##        return self.child_handlers['pp'].set_char_pp(attr,evl)
##
##    def get_char_pp( self, attr ):
##        return self.child_handlers['pp'].get_char_pp(attr)

    def get_char_lvl( self, attr ):
        return self.child_handlers['classes'].get_char_lvl(attr)

class tabbed_panel(wx.Notebook):
    def __init__(self, parent, handler, mode):
        wx.Notebook.__init__(self, parent, -1, size=(1200,800))
        self.handler = handler
        self.parent = parent
        tree = self.handler.tree
        max = tree.GetChildrenCount(handler.mytree_node, False)
        cookie = 0
        try:
            (child,cookie)=tree.GetFirstChild(handler.mytree_node,cookie)
        except: # If this happens we probably have a newer version of wxPython
            (child,cookie)=tree.GetFirstChild(handler.mytree_node)
        obj = tree.GetPyData(child)
        for m in xrange(max):
    
            if mode == 1:
                panel = obj.get_design_panel(self)
            else:
                panel = obj.get_use_panel(self)
            name = obj.master_dom.getAttribute("name")

            if panel:
                self.AddPage(panel,name)
            if m < max-1: 
                child = tree.GetNextSibling(child)
                obj = tree.GetPyData(child)


    def about(self):
        html_str = "<img src='" + dir_struct["icon"]+'d20_logo.gif' "><br /><b>d20 Character Tool v0.7 beta</b>"
        html_str += "<br />by Chris Davis<br />chris@rpgarchive.com"
        return html_str

    def get_char_name( self ):
        return self.child_handlers['general'].get_char_name()

##    def set_char_pp(self,attr,evl):
##        return self.child_handlers['pp'].set_char_pp(attr,evl)
##
##    def get_char_pp( self, attr ):
##        return self.child_handlers['pp'].get_char_pp(attr)

    def get_char_lvl( self, attr ):
        return self.child_handlers['classes'].get_char_lvl(attr)

class SWd20_char_child(node_handler):
    """ Node Handler for skill.  This handler will be
        created by SWd20char_handler.
    """
    def __init__(self, xml_dom, tree_node, parent):
        node_handler.__init__(self,xml_dom, tree_node)
        self.char_hander = parent
        self.drag = False
        self.frame = component.get('frame')
        self.myeditor = None


    def on_drop(self,evt):
        pass

    def on_rclick(self,evt):
        pass

    def on_ldclick(self,evt): #Function needs help. Needs an OnClose I think.
        if self.myeditor == None or self.myeditor.destroyed:
            title = self.master_dom.getAttribute('name') + " Editor"
            # Frame created in correctly.
            self.myeditor = wx.Frame(self.frame,title,dir_struct["icon"]+'grid.ico')
            wnd = self.get_design_panel(self.myeditor)
            self.myeditor.panel = wnd
            self.wnd = wnd
            self.myeditor.Show(1)
        else:
            self.myeditor.Raise()

    def on_html(self,evt):
        html_str = self.tohtml()
        wnd = http_html_window(self.frame.note,-1)
        wnd.title = self.master_dom.getAttribute('name')
        self.frame.add_panel(wnd)
        wnd.SetPage(html_str)

    def get_design_panel(self,parent):
        pass

    def get_use_panel(self,parent):
        return self.get_design_panel(parent)

    def delete(self):
        pass


class SWd20skill(SWd20_char_child):
    """ Node Handler for skill.  This handler will be
        created by SWd20char_handler.
    """
    def __init__(self, xml_dom, tree_node, parent):
        SWd20_char_child.__init__(self, xml_dom, tree_node, parent)
        tree = self.tree
        icons = self.tree.icons
        node_list = self.master_dom.getElementsByTagName('skill')
        self.skills={}
        for n in node_list:
            name = n.getAttribute('name')
            self.skills[name] = n
            new_tree_node = tree.AppendItem(self.mytree_node,name,icons['gear'],icons['gear'])
            tree.SetPyData(new_tree_node,self)

    def get_mod(self,name):
        skill = self.skills[name]
        stat = skill.getAttribute('stat')
        ac = int(skill.getAttribute('armorcheck'))
        if ac:
            ac = self.char_hander.child_handlers['ac'].get_check_pen()
        stat_mod = self.char_hander.child_handlers['abilities'].get_mod(stat)
        rank = int(skill.getAttribute('rank'))
        misc = int(skill.getAttribute('misc'))
        total = stat_mod + rank + misc + ac
        return total

    def on_rclick(self,evt):
        #updated with code for untrained use check
        item = self.tree.GetSelection()
        name = self.tree.GetItemText(item)
        skill = self.skills[name]
        rank = int(skill.getAttribute('rank'))
        untrained = int(skill.getAttribute('untrained'))
        chat = self.chat
        if item == self.mytree_node:
            SWd20_char_child.on_ldclick(self,evt)
        else:
            if rank == 0 and untrained == 0:
                chat.Post('Can\'t use untrained!',True,True)
            else:
                mod = self.get_mod(name)
                if mod >= 0:
                    mod1 = "+"
                else:
                    mod1 = ""
                txt = '%s Skill Check: [1d20%s%s]' % (name, mod1, mod)
                chat.ParsePost(txt,True,True)

    def get_design_panel(self,parent):
        wnd = outline_panel(parent,self,skill_grid,"Skills")
        wnd.title = "Skills (edit)"
        return wnd

    def tohtml(self):
        html_str = """<table border='1' width=100% ><tr BGCOLOR=#E9E9E9 ><th width='30%'>Skill</th><th>Key</th>
                    <th>Rank</th><th>Abil</th><th>Misc</th><th>Total</th></tr>"""
        node_list = self.master_dom.getElementsByTagName('skill')
        for n in node_list:
            name = n.getAttribute('name')
            stat = n.getAttribute('stat')
            rank = n.getAttribute('rank')
            html_str = html_str + "<tr ALIGN='center'><td>"+name+"</td><td>"+stat+"</td><td>"+rank+"</td>"
            stat_mod = str(self.char_hander.child_handlers['abilities'].get_mod(stat))
            misc = n.getAttribute('misc')
            mod = str(self.get_mod(name))
            if mod >= 0:
                mod1 = "+"
            else:
                mod1 = ""
            html_str = html_str + "<td>"+stat_mod+"</td><td>"+misc+'</td><td>%s%s</td></tr>' % (mod1, mod)
        html_str = html_str + "</table>"
        return html_str


class SWd20ability(SWd20_char_child):
    """ Node Handler for ability.   This handler will be
        created by SWd20char_handler.
    """
    def __init__(self, xml_dom, tree_node, parent):
        SWd20_char_child.__init__(self, xml_dom, tree_node, parent)
        self.abilities = {}
        node_list = self.master_dom.getElementsByTagName('stat')
        tree = self.tree
        icons = tree.icons
        for n in node_list:
            name = n.getAttribute('abbr')
            self.abilities[name] = n
            new_tree_node = tree.AppendItem( self.mytree_node, name, icons['gear'], icons['gear'] )
            tree.SetPyData( new_tree_node, self )

    def on_rclick( self, evt ):
        item = self.tree.GetSelection()
        name = self.tree.GetItemText( item )
        if item == self.mytree_node:
            SWd20_char_child.on_ldclick( self, evt )
        else:
            mod = self.get_mod( name )
            if mod >= 0:
                mod1 = "+"
            else:
                mod1 = ""
            chat = self.chat
            txt = '%s check: [1d20%s%s]' % ( name, mod1, mod )
            chat.ParsePost( txt, True, True )

    def get_mod(self,abbr):
        score = int(self.abilities[abbr].getAttribute('base'))
        mod = (score - 10) / 2
        return mod

    def set_score(self,abbr,score):
        if score >= 0:
            self.abilities[abbr].setAttribute("base",str(score))

    def get_design_panel(self,parent):
        wnd = outline_panel(parent,self,abil_grid,"Abilities")
        wnd.title = "Abilities (edit)"
        return wnd

    def tohtml(self):
        html_str = """<table border='1' width=100%><tr BGCOLOR=#E9E9E9 ><th width='50%'>Ability</th>
                    <th>Base</th><th>Modifier</th></tr>"""
        node_list = self.master_dom.getElementsByTagName('stat')
        for n in node_list:
            name = n.getAttribute('name')
            abbr = n.getAttribute('abbr')
            base = n.getAttribute('base')
            mod = str(self.get_mod(abbr))
            if mod >= 0:
                mod1 = "+"
            else:
                mod1 = ""
            html_str = html_str + "<tr ALIGN='center'><td>"+name+"</td><td>"+base+'</td><td>%s%s</td></tr>' % (mod1, mod)
        html_str = html_str + "</table>"
        return html_str

class SWd20saves(SWd20_char_child):
    """ Node Handler for saves.   This handler will be
        created by SWd20char_handler.
    """
    def __init__(self, xml_dom, tree_node, parent):
        SWd20_char_child.__init__(self, xml_dom, tree_node, parent)
        tree = self.tree
        icons = self.tree.icons
        node_list = self.master_dom.getElementsByTagName('save')
        self.saves={}
        for n in node_list:
            name = n.getAttribute('name')
            self.saves[name] = n
            new_tree_node = tree.AppendItem(self.mytree_node,name,icons['gear'],icons['gear'])
            tree.SetPyData(new_tree_node,self)

    def get_mod(self,name):
        save = self.saves[name]
        stat = save.getAttribute('stat')
        stat_mod = self.char_hander.child_handlers['abilities'].get_mod(stat)
        base = int(save.getAttribute('base'))
        miscmod = int(save.getAttribute('miscmod'))
#        magmod = int(save.getAttribute('magmod'))
#        total = stat_mod + base + miscmod + magmod
        total = stat_mod + base + miscmod
        return total

    def on_rclick(self,evt):
        item = self.tree.GetSelection()
        name = self.tree.GetItemText(item)
        if item == self.mytree_node:
            SWd20_char_child.on_ldclick(self,evt)
            #wnd = save_grid(self.frame.note,self)
            #wnd.title = "Saves"
            #self.frame.add_panel(wnd)
        else:
            mod = self.get_mod(name)
            if mod >= 0:
                mod1 = "+"
            else:
                mod1 = ""
            chat = self.chat
            txt = '%s save: [1d20%s%s]' % (name, mod1, mod)
            chat.ParsePost( txt, True, True )

    def get_design_panel(self,parent):
        wnd = outline_panel(parent,self,save_grid,"Saves")
        wnd.title = "Saves"
        return wnd

    def tohtml(self):
        html_str = """<table border='1' width=100% ><tr BGCOLOR=#E9E9E9 ><th width='30%'>Save</th>
                    <th>Key</th><th>Base</th><th>Abil</th><th>Magic</th>
                    <th>Misc</th><th>Total</th></tr>"""
        node_list = self.master_dom.getElementsByTagName('save')
        for n in node_list:
            name = n.getAttribute('name')
            stat = n.getAttribute('stat')
            base = n.getAttribute('base')
            html_str = html_str + "<tr ALIGN='center'><td>"+name+"</td><td>"+stat+"</td><td>"+base+"</td>"
            stat_mod = str(self.char_hander.child_handlers['abilities'].get_mod(stat))
            mag = n.getAttribute('magmod')
            misc = n.getAttribute('miscmod')
            mod = str(self.get_mod(name))
            if mod >= 0:
                mod1 = "+"
            else:
                mod1 = ""
            html_str = html_str + "<td>"+stat_mod+"</td><td>"+mag+"</td>"
            html_str = html_str + '<td>'+misc+'</td><td>%s%s</td></tr>' % (mod1, mod)
        html_str = html_str + "</table>"
        return html_str


class SWd20general(SWd20_char_child):
    """ Node Handler for general information.   This handler will be
        created by SWd20char_handler.
    """
    def __init__(self, xml_dom, tree_node, parent):
        SWd20_char_child.__init__(self, xml_dom, tree_node, parent)

    def get_design_panel(self,parent):
        wnd = outline_panel(parent,self,gen_grid,"General Information")
        wnd.title = "General Info"
        return wnd

    def tohtml(self):
        n_list = self.master_dom._get_childNodes()
        html_str = "<table width=100% border=1 ><tr BGCOLOR=#E9E9E9 ><th>General Information</th></tr><tr><td>"
        for n in n_list:
            t_node = component.get('xml').safe_get_text_node(n)
            html_str += "<B>"+n._get_tagName().capitalize() +":</B> "
            html_str += t_node._get_nodeValue() + ", "
        html_str = html_str[:len(html_str)-2] + "</td></tr></table>"
        return html_str

    def on_name_change(self,name):
        self.char_hander.rename(name)

    def get_char_name( self ):
        node = self.master_dom.getElementsByTagName( 'name' )[0]
        t_node = component.get('xml').safe_get_text_node( node )
        return t_node._get_nodeValue()


class SWd20classes(SWd20_char_child):
    """ Node Handler for classes.  This handler will be
        created by SWd20char_handler.
    """
    def __init__(self, xml_dom, tree_node, parent):
        SWd20_char_child.__init__(self, xml_dom, tree_node, parent)

    def get_design_panel(self,parent):
        wnd = outline_panel(parent,self,class_panel,"Classes")
        wnd.title = "Classes"
        return wnd

    def tohtml(self):
        html_str = "<table width=100% border=1 ><tr BGCOLOR=#E9E9E9 ><th>Classes</th></tr><tr><td>"
        n_list = self.master_dom._get_childNodes()
        for n in n_list:
            html_str += n.getAttribute('name') + " ("+n.getAttribute('level')+"), "
        html_str = html_str[:len(html_str)-2] + "</td></tr></table>"
        return html_str

    def get_char_lvl( self, attr ):
        node_list = self.master_dom.getElementsByTagName('class')
        for n in node_list:
            lvl = n.getAttribute('level')
            type = n.getAttribute('name')
            if attr == "level":
                return lvl
            elif attr == "class":
                return type


class SWd20feats(SWd20_char_child):
    """ Node Handler for classes.  This handler will be
        created by d20char_handler.
    """
    def __init__(self, xml_dom, tree_node, parent):
        SWd20_char_child.__init__(self, xml_dom, tree_node, parent)

    def get_design_panel(self,parent):
        wnd = outline_panel(parent,self,feat_panel,"Feats")
        wnd.title = "Feats"
        return wnd

    def tohtml(self):
        html_str = "<table width=100% border=1 ><tr BGCOLOR=#E9E9E9 ><th>Feats</th></tr><tr><td>"
        n_list = self.master_dom._get_childNodes()
        for n in n_list:
            html_str += n.getAttribute('name')+ ", "
        html_str = html_str[:len(html_str)-2] + "</td></tr></table>"
        return html_str

class SWd20howto(SWd20_char_child):
    """ Node Handler for hit points.  This handler will be
        created by d20char_handler.
    """
    def __init__(self, xml_dom, tree_node, parent):
        SWd20_char_child.__init__(self, xml_dom, tree_node, parent)

    def get_design_panel(self,parent):
        wnd = outline_panel(parent,self,howto_panel,"How To")
        wnd.title = "How To"
        return wnd

class SWd20inventory(SWd20_char_child):
    """ Node Handler for general information.   This handler will be
        created by d20char_handler.
    """
    def __init__(self, xml_dom, tree_node, parent):
        SWd20_char_child.__init__(self, xml_dom, tree_node, parent)

    def get_design_panel(self,parent):
        wnd = outline_panel(parent,self,inventory_grid,"Inventory")
        wnd.title = "General Info"
        return wnd

    def tohtml(self):
        n_list = self.master_dom._get_childNodes()
        html_str = "<table width=100% border=1 ><tr BGCOLOR=#E9E9E9 ><th>General Information</th></tr><tr><td>"
        for n in n_list:
            t_node = component.get('xml').safe_get_text_node(n)
            html_str += "<B>"+n._get_tagName().capitalize() +":</B> "
            html_str += t_node._get_nodeValue() + "<br />"
        html_str = html_str[:len(html_str)-2] + "</td></tr></table>"
        return html_str

    def on_name_change(self,name):
        self.char_hander.rename(name)

    def get_char_name( self ):
        node = self.master_dom.getElementsByTagName( 'name' )[0]
        t_node = component.get('xml').safe_get_text_node( node )
        return t_node._get_nodeValue()

class SWd20hp(SWd20_char_child):
    """ Node Handler for hit points.  This handler will be
        created by d20char_handler.
    """
    def __init__(self,xml_dom,tree_node,parent):
        SWd20_char_child.__init__(self,xml_dom,tree_node,parent)

    def get_design_panel(self,parent):
        wnd = outline_panel(parent,self,hp_panel,"Wound Points")
        wnd.title = "Wound Points"
        return wnd

    def tohtml(self):
        html_str = "<table width=100% border=1 ><tr BGCOLOR=#E9E9E9 ><th colspan=4>Wound Points</th></tr>"
        html_str += "<tr><th>Max:</th><td>"+self.master_dom.getAttribute('max')+"</td>"
        html_str += "<th>Current:</th><td>"+self.master_dom.getAttribute('current')+"</td>"
        html_str += "</tr></table>"
        return html_str

    def get_max_hp( self ):
        try:
            return eval( self.master_dom.getAttribute( 'max' ) )
        except:
            return 0
    def get_current_hp( self ):
        try:
            return eval( self.master_dom.getAttribute( 'current' ) )
        except:
            return 0

class SWd20vp(SWd20_char_child):
    """ Node Handler for hit points.  This handler will be
        created by d20char_handler.
    """
    def __init__(self,xml_dom,tree_node,parent):
        SWd20_char_child.__init__(self,xml_dom,tree_node,parent)

    def get_design_panel(self,parent):
        wnd = outline_panel(parent,self,vp_panel,"Vitality Points")
        wnd.title = "Vitality Points"
        return wnd

    def tohtml(self):
        html_str = "<table width=100% border=1 ><tr BGCOLOR=#E9E9E9 ><th colspan=4>Vitality Points</th></tr>"
        html_str += "<tr><th>Max:</th><td>"+self.master_dom.getAttribute('max')+"</td>"
        html_str += "<th>Current:</th><td>"+self.master_dom.getAttribute('current')+"</td>"
        html_str += "</tr></table>"
        return html_str

    def get_max_vp( self ):
        try:
            return eval( self.master_dom.getAttribute( 'max' ) )
        except:
            return 0
    def get_current_vp( self ):
        try:
            return eval( self.master_dom.getAttribute( 'current' ) )
        except:
            return 0

class SWd20attacks(SWd20_char_child):
    """ Node Handler for attacks.  This handler will be
        created by d20char_handler.
    """
    def __init__(self,xml_dom,tree_node,parent):
        SWd20_char_child.__init__(self,xml_dom,tree_node,parent)
        node_list = self.master_dom.getElementsByTagName('melee')
        self.melee = node_list[0]
        node_list = self.master_dom.getElementsByTagName('ranged')
        self.ranged = node_list[0]
        self.refresh_weapons()

    def refresh_weapons(self):
        self.weapons = {}
        tree = self.tree
        icons = self.tree.icons
        tree.CollapseAndReset(self.mytree_node)
        node_list = self.master_dom.getElementsByTagName('weapon')
        for n in node_list:
            name = n.getAttribute('name')
            new_tree_node = tree.AppendItem(self.mytree_node,name,icons['sword'],icons['sword'])
            tree.SetPyData(new_tree_node,self)
            self.weapons[name]=n

    def get_mod(self,type='m'):
        (base, base2, base3, base4, base5, base6, stat_mod, misc) = self.get_attack_data(type)
        return base + misc + stat_mod

    def get_attack_data(self,type='m'):
        if type=='m' or type=='0':
            stat_mod = self.char_hander.child_handlers['abilities'].get_mod('Str')
            temp = self.melee
        else:
            stat_mod = self.char_hander.child_handlers['abilities'].get_mod('Dex')
            temp = self.ranged
        base = int(temp.getAttribute('base'))
        base2 = int(temp.getAttribute('second'))
        base3 = int(temp.getAttribute('third'))
        base4 = int(temp.getAttribute('forth'))
        base5 = int(temp.getAttribute('fifth'))
        base6 = int(temp.getAttribute('sixth'))
        misc = int(temp.getAttribute('misc'))
        return (base, base2, base3, base4, base5, base6, stat_mod ,misc)

    def on_rclick(self,evt):
        #removed the DnD specific code
        item = self.tree.GetSelection()
        name = self.tree.GetItemText(item)
        if item == self.mytree_node:
            SWd20_char_child.on_ldclick(self,evt)
            #self.frame.add_panel(self.get_design_panel(self.frame.note))
        else:
            mod = int(self.weapons[name].getAttribute('mod'))
            if self.weapons[name].getAttribute('range') == '0':
                mod = mod + self.get_mod('m')
                if mod >= 0:
                    mod1 = "+"
                else:
                    mod1 = ""
            else:
                mod = mod + self.get_mod('r')
                if mod >= 0:
                    mod1 = "+"
                else:
                    mod1 = ""
            chat = self.chat
            dmg = self.weapons[name].getAttribute('damage')
            lvl = self.get_char_lvl('level')
            cname = self.char_hander.get_char_name()
            txt = '%s %s Attack Roll: [1d20%s%s] ===> DMG: [%s%s%s]' % (cname, name, mod1, mod, dmg, mod1, mod)
            chat.ParsePost( txt, True, False )
            temp = self.melee
            stat_mod = self.char_hander.child_handlers['abilities'].get_mod('Str')

    def get_design_panel(self,parent):
        wnd = outline_panel(parent,self,attack_panel,"Attacks")
        wnd.title = "Attacks"
        return wnd

    def get_char_lvl( self, attr ):
        return self.char_hander.get_char_lvl(attr)

    def tohtml(self):
        melee = self.get_attack_data('m')
        ranged = self.get_attack_data('r')
        html_str = """<table width=100% border=1 ><tr BGCOLOR=#E9E9E9 ><th>Attack</th>
                    <th>Total</th><th >Base</th><th>Abil</th><th>Misc</th></tr>"""
        html_str += "<tr ALIGN='center' ><th >Melee:</th>"
        html_str += "<td>"+str(melee[0]+melee[1]+melee[2])+"</td>"
        html_str += "<td>"+str(melee[0])+"</td>"
        html_str += "<td>"+str(melee[1])+"</td>"
        html_str += "<td>"+str(melee[2])+"</td></tr>"

        html_str += "<tr ALIGN='center' ><th >Ranged:</th>"
        html_str += "<td>"+str(ranged[0]+ranged[1]+ranged[2])+"</td>"
        html_str += "<td>"+str(ranged[0])+"</td>"
        html_str += "<td>"+str(ranged[1])+"</td>"
        html_str += "<td>"+str(ranged[2])+"</td></tr></table>"

        n_list = self.master_dom.getElementsByTagName('weapon')
        for n in n_list:
            mod = n.getAttribute('mod')
            if mod >= 0:
                mod1 = "+"
            else:
                mod1 = ""
            ran = n.getAttribute('range')
            total = str(int(mod) + self.get_mod(ran))
            html_str += """<P><table width=100% border=1 ><tr BGCOLOR=#E9E9E9 ><th colspan=2>Weapon</th>
                    <th>Attack</th><th >Damage</th><th>Critical</th></tr>"""
            html_str += "<tr ALIGN='center' ><td  colspan=2>"+n.getAttribute('name')+"</td><td>"+total+"</td>"
            html_str += "<td>"+n.getAttribute('damage')+"</td><td>"+n.getAttribute('critical')+"</td></tr>"
            html_str += """<tr BGCOLOR=#E9E9E9 ><th>Range</th><th>Weight</th>
                        <th>Type</th><th>Size</th><th>Misc Mod</th></tr>"""
            html_str += "<tr ALIGN='center'><td>"+ran+"</td><td>"+n.getAttribute('weight')+"</td>"
            html_str += "<td>"+n.getAttribute('type')+"</td><td>"+n.getAttribute('size')+"</td>"
            html_str += '<td>%s%s</td></tr></table>' % (mod1, mod)
        return html_str

class SWd20armor(SWd20_char_child):
    """ Node Handler for ac.  This handler will be
        created by d20char_handler.
    """
    def __init__(self,xml_dom,tree_node,parent):
        SWd20_char_child.__init__(self,xml_dom,tree_node,parent)

    def get_total_weight(self):
        return self.get_total('weight')

    def get_check_pen(self):
        return self.get_total('checkpenalty')

    def get_armor_class(self):
        ac_total = 10
        ac_total += self.get_total('bonus')
        dex_mod = self.char_hander.child_handlers['abilities'].get_mod('Dex')
        max_dex = self.get_max_dex()
        if dex_mod < max_dex:
            ac_total += dex_mod
        else:
            ac_total += max_dex
        return ac_total

    def get_max_dex(self):
        armor_list = self.master_dom.getElementsByTagName('armor')
        dex = 10
        for a in armor_list:
            temp = int(a.getAttribute("maxdex"))
            if temp < dex:
                dex = temp
        return dex

    def get_total(self,attr):
        armor_list = self.master_dom.getElementsByTagName('armor')
        total = 0
        for a in armor_list:
            total += int(a.getAttribute(attr))
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
        n_list = self.master_dom._get_childNodes()
        for n in n_list:
            html_str += """<P><table width=100% border=1 ><tr BGCOLOR=#E9E9E9 ><th colspan=3>Armor</th>
                    <th>Type</th><th >Bonus</th></tr>"""
            html_str += "<tr ALIGN='center' ><td  colspan=3>"+n.getAttribute('name')+"</td>"
            html_str += "<td>"+n.getAttribute('type')+"</td>"
            html_str += "<td>"+n.getAttribute('bonus')+"</td></tr>"
            html_str += """<tr BGCOLOR=#E9E9E9 ><th>Check Penalty</th><th>Spell Failure</th>
                        <th>Max Dex</th><th>Speed</th><th>Weight</th></tr>"""
            html_str += "<tr ALIGN='center'><td>"+n.getAttribute('checkpenalty')+"</td>"
            html_str += "<td>"+n.getAttribute('maxdex')+"</td>"
            html_str += "<td>"+n.getAttribute('speed')+"</td>"
            html_str += "<td>"+n.getAttribute('weight')+"</td></tr></table>"
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
        pname = handler.master_dom.setAttribute("name", 'TWO')
        wx.ScrolledWindow.__init__(self, parent, -1,style=wx.VSCROLL | wx.SUNKEN_BORDER  )
        self.height = 1200
        self.SetScrollbars(10, 10,80, self.height/10)
        self.main_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.panels = {}
        keys = handler.child_handlers.keys()
        for k in keys:
            self.panels[k] = handler.child_handlers[k].get_design_panel(self, [k])
        self.sub_sizer = wx.BoxSizer(wx.VERTICAL)
        self.sub_sizer2 = wx.BoxSizer(wx.VERTICAL)
        self.sub_sizer.Add(self.panels['general'], 1, wx.EXPAND)
        self.sub_sizer.Add(self.panels['abilities'], 1, wx.EXPAND)

        self.sub_sizer.Add(self.panels['attacks'], 2, wx.EXPAND)
        self.sub_sizer.Add(self.panels['ac'], 1, wx.EXPAND)
        #self.sub_sizer.Add(self.panels['spells'], 1, wx.EXPAND)

        self.sub_sizer2.Add(self.panels['classes'], 2, wx.EXPAND)
        self.sub_sizer2.Add(self.panels['wp'], 1, wx.EXPAND)
        self.sub_sizer2.Add(self.panels['vp'], 1, wx.EXPAND)
        #self.sub_sizer2.Add(self.panels['pp'], 1, wx.EXPAND)
        self.sub_sizer2.Add(self.panels['saves'], 2, wx.EXPAND)

        self.sub_sizer2.Add(self.panels['feats'], 2, wx.EXPAND)
        #self.sub_sizer2.Add(self.panels['powers'], 2, wx.EXPAND)
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
#        self.panels['powers'].panel.refresh_data()
#        self.panels['spells'].panel.refresh_data()

HOWTO_MAX = wx.NewId()

class howto_panel(wx.Panel):
    def __init__(self, parent, handler):
        wx.Panel.__init__(self, parent, -1)
        pname = handler.master_dom.setAttribute("name", 'How To')
        self.sizer = wx.FlexGridSizer(2, 4, 2, 2)  # rows, cols, hgap, vgap
        self.master_dom = handler.master_dom
        n_list = self.master_dom._get_childNodes()
        for n in n_list:
            t_node = component.get('xml').safe_get_text_node(n)
        self.sizer.AddMany([ (wx.StaticText(self, -1, t_node._get_nodeValue()),   0, wx.ALIGN_CENTER_VERTICAL),
                 ])
        self.sizer.AddGrowableCol(1)
        self.SetSizer(self.sizer)


WP_CUR = wx.NewId()
WP_MAX = wx.NewId()

class hp_panel(wx.Panel):
    def __init__(self, parent, handler):
        wx.Panel.__init__(self, parent, -1)
        pname = handler.master_dom.setAttribute("name", 'WoundPoints')
        self.sizer = wx.FlexGridSizer(2, 4, 2, 2)  # rows, cols, hgap, vgap
        self.master_dom = handler.master_dom
        self.sizer.AddMany([ (wx.StaticText(self, -1, "WP Current:"),   0, wx.ALIGN_CENTER_VERTICAL),
                 (wx.TextCtrl(self, WP_CUR, self.master_dom.getAttribute('current')),   0, wx.EXPAND),
                 (wx.StaticText(self, -1, "WP Max:"), 0, wx.ALIGN_CENTER_VERTICAL),
                 (wx.TextCtrl(self, WP_MAX, self.master_dom.getAttribute('max')),  0, wx.EXPAND),
                 ])
        self.sizer.AddGrowableCol(1)
        self.Bind(wx.EVT_SIZE, self.on_size)
        self.Bind(wx.EVT_TEXT, self.on_text, id=WP_MAX)
        self.Bind(wx.EVT_TEXT, self.on_text, id=WP_CUR)
        self.SetSizer(self.sizer)

    def on_text(self,evt):
        id = evt.GetId()
        if id == WP_CUR:
            self.master_dom.setAttribute('current',evt.GetString())
        elif id == WP_MAX:
            self.master_dom.setAttribute('max',evt.GetString())

    def on_size(self,evt):
        s = self.GetClientSizeTuple()
        self.sizer.SetDimension(0,0,s[0],s[1])

VP_CUR = wx.NewId()
VP_MAX = wx.NewId()

class vp_panel(wx.Panel):
    def __init__(self, parent, handler):
        wx.Panel.__init__(self, parent, -1)
        pname = handler.master_dom.setAttribute("name", 'VitalityPoints')
        self.sizer = wx.FlexGridSizer(2, 4, 2, 2)  # rows, cols, hgap, vgap
        self.master_dom = handler.master_dom
        self.sizer.AddMany([ (wx.StaticText(self, -1, "VP Current:"),   0, wx.ALIGN_CENTER_VERTICAL),
                 (wx.TextCtrl(self, VP_CUR, self.master_dom.getAttribute('current')),   0, wx.EXPAND),
                 (wx.StaticText(self, -1, "VP Max:"), 0, wx.ALIGN_CENTER_VERTICAL),
                 (wx.TextCtrl(self, VP_MAX, self.master_dom.getAttribute('max')),  0, wx.EXPAND),
                 ])
        self.sizer.AddGrowableCol(1)
        self.Bind(wx.EVT_SIZE, self.on_size)
        self.Bind(wx.EVT_TEXT, self.on_text, id=VP_MAX)
        self.Bind(wx.EVT_TEXT, self.on_text, id=VP_CUR)
        self.SetSizer(self.sizer)

    def on_text(self,evt):
        id = evt.GetId()
        if id == VP_CUR:
            self.master_dom.setAttribute('current',evt.GetString())
        elif id == VP_MAX:
            self.master_dom.setAttribute('max',evt.GetString())

    def on_size(self,evt):
        s = self.GetClientSizeTuple()
        self.sizer.SetDimension(0,0,s[0],s[1])

#PP_CUR = wx.NewId()
#PP_MAX = wx.NewId()
#PP_FRE = wx.NewId()
#PP_MFRE = wx.NewId()

#class pp_panel(wx.Panel):
#    def __init__(self, parent, handler):
#        wx.Panel.__init__(self, parent, -1)
#        pname = handler.master_dom.setAttribute("name", 'PowerPoints')
#        self.sizer = wx.FlexGridSizer(2, 4, 2, 2)  # rows, cols, hgap, vgap
#        self.master_dom = handler.master_dom
#
#        self.sizer.AddMany([ (wx.StaticText(self, -1, "PP Current:"),   0, wx.ALIGN_CENTER_VERTICAL),
#                 (wx.TextCtrl(self, PP_CUR, self.master_dom.getAttribute('current1')),   0, wx.EXPAND),
#                 (wx.StaticText(self, -1, "PP Max:"), 0, wx.ALIGN_CENTER_VERTICAL),
#                 (wx.TextCtrl(self, PP_MAX, self.master_dom.getAttribute('max1')),  0, wx.EXPAND),
#                 (wx.StaticText(self, -1, "Current Free Talants per day:"), 0, wx.ALIGN_CENTER_VERTICAL),
#                 (wx.TextCtrl(self, PP_FRE, self.master_dom.getAttribute('free')),  0, wx.EXPAND),
#                 (wx.StaticText(self, -1, "Max Free Talants per day:"), 0, wx.ALIGN_CENTER_VERTICAL),
#                 (wx.TextCtrl(self, PP_MFRE, self.master_dom.getAttribute('maxfree')),  0, wx.EXPAND),
#                 ])
#        self.sizer.AddGrowableCol(1)
#        self.Bind(wx.EVT_SIZE, self.on_size)
#        self.Bind(wx.EVT_TEXT, self.on_text, id=PP_MAX)
#        self.Bind(wx.EVT_TEXT, self.on_text, id=PP_CUR)
#        self.Bind(wx.EVT_TEXT, self.on_text, id=PP_FRE)
#        self.Bind(wx.EVT_TEXT, self.on_text, id=PP_MFRE)
#
#    def on_text(self,evt):
#        id = evt.GetId()
#        if id == PP_CUR:
#            self.master_dom.setAttribute('current1',evt.GetString())
#        elif id == PP_MAX:
#            self.master_dom.setAttribute('max1',evt.GetString())
#        elif id == PP_FRE:
#            self.master_dom.setAttribute('free',evt.GetString())
#        elif id == PP_MFRE:
#            self.master_dom.setAttribute('maxfree',evt.GetString())
#
#    def on_size(self,evt):
#        s = self.GetClientSizeTuple()
#        self.sizer.SetDimension(0,0,s[0],s[1])


class gen_grid(wx.grid.Grid):
    """grid for gen info"""
    def __init__(self, parent, handler):
        pname = handler.master_dom.setAttribute("name", 'General')
        wx.grid.Grid.__init__(self, parent, -1, style=wx.SUNKEN_BORDER | wx.WANTS_CHARS)
        self.Bind(wx.EVT_SIZE, self.on_size)
        self.Bind(wx.grid.EVT_GRID_CELL_CHANGE, self.on_cell_change)
        self.handler = handler
        n_list = handler.master_dom._get_childNodes()
        self.CreateGrid(len(n_list),2)
        self.SetRowLabelSize(0)
        self.SetColLabelSize(0)
        self.n_list = n_list
        i = 0
        for i in range(len(n_list)):
            self.refresh_row(i)

    def on_cell_change(self,evt):
        row = evt.GetRow()
        col = evt.GetCol()
        value = self.GetCellValue(row,col)
        t_node = self.n_list[row]._get_firstChild()
        t_node._set_nodeValue(value)
        if row==0: self.handler.on_name_change(value)

    def refresh_row(self,rowi):
        t_node = component.get('xml').safe_get_text_node(self.n_list[rowi])
        self.SetCellValue(rowi,0,self.n_list[rowi]._get_tagName())
        self.SetReadOnly(rowi,0)
        self.SetCellValue(rowi,1,t_node._get_nodeValue())

    def on_size(self,evt):
        (w,h) = self.GetClientSizeTuple()
        cols = self.GetNumberCols()
        col_w = w/(cols)
        for i in range(0,cols):
            self.SetColSize(i,col_w)
        evt.Skip()
        self.Refresh()

class inventory_grid(wx.grid.Grid):
    """grid for gen info"""
    def __init__(self, parent, handler):
        pname = handler.master_dom.setAttribute("name", 'Money and Inventory')
        wx.grid.Grid.__init__(self, parent, -1, style=wx.SUNKEN_BORDER | wx.WANTS_CHARS)
        self.Bind(wx.EVT_SIZE, self.on_size)
        self.Bind(wx.grid.EVT_GRID_CELL_CHANGE, self.on_cell_change)
        self.handler = handler
        n_list = handler.master_dom._get_childNodes()
        self.CreateGrid(len(n_list),2)
        self.SetRowLabelSize(0)
        self.SetColLabelSize(0)
        self.n_list = n_list
        i = 0
        for i in range(len(n_list)):
            self.refresh_row(i)

    def on_cell_change(self,evt):
        row = evt.GetRow()
        col = evt.GetCol()
        value = self.GetCellValue(row,col)
        t_node = self.n_list[row]._get_firstChild()
        t_node._set_nodeValue(value)
        if row==0: self.handler.on_name_change(value)

    def refresh_row(self,rowi):
        t_node = component.get('xml').safe_get_text_node(self.n_list[rowi])
        self.SetCellValue(rowi,0,self.n_list[rowi]._get_tagName())
        self.SetReadOnly(rowi,0)
        self.SetCellValue(rowi,1,t_node._get_nodeValue())

    def on_size(self,evt):
        (w,h) = self.GetClientSizeTuple()
        cols = self.GetNumberCols()
        col_w = w/(cols)
        for i in range(0,cols):
            self.SetColSize(i,col_w)
        evt.Skip()
        self.Refresh()

class abil_grid(wx.grid.Grid):
    """grid for abilities"""
    def __init__(self, parent, handler):
        pname = handler.master_dom.setAttribute("name", 'Stats')
        wx.grid.Grid.__init__(self, parent, -1, style=wx.SUNKEN_BORDER | wx.WANTS_CHARS)
        self.Bind(wx.EVT_SIZE, self.on_size)
        self.Bind(wx.grid.EVT_GRID_CELL_CHANGE, self.on_cell_change)
        self.handler = handler
        stats = handler.master_dom.getElementsByTagName('stat')
        self.CreateGrid(len(stats),3)
        self.SetRowLabelSize(0)
        col_names = ['Ability','Score','Modifier']
        for i in range(len(col_names)):
            self.SetColLabelValue(i,col_names[i])
        self.stats = stats
        i = 0
        for i in range(len(stats)):
            self.refresh_row(i)
        self.char_wnd = None

    def on_cell_change(self,evt):
        row = evt.GetRow()
        col = evt.GetCol()
        value = self.GetCellValue(row,col)
        try:
            int(value)
            self.stats[row].setAttribute('base',value)
            self.refresh_row(row)
        except:
            self.SetCellValue(row,col,"0")
        if self.char_wnd:
            self.char_wnd.refresh_data()

    def refresh_row(self,rowi):
        s = self.stats[rowi]
        name = s.getAttribute('name')
        abbr = s.getAttribute('abbr')
        self.SetCellValue(rowi,0,name)
        self.SetReadOnly(rowi,0)
        self.SetCellValue(rowi,1,s.getAttribute('base'))
        self.SetCellValue(rowi,2,str(self.handler.get_mod(abbr)))
        self.SetReadOnly(rowi,2)

    def on_size(self,evt):
        (w,h) = self.GetClientSizeTuple()
        cols = self.GetNumberCols()
        col_w = w/(cols+2)
        self.SetColSize(0,col_w*3)
        for i in range(1,cols):
            self.SetColSize(i,col_w)
        evt.Skip()
        self.Refresh()

    def refresh_data(self):
        for r in range(self.GetNumberRows()-1):
            self.refresh_row(r)


class save_grid(wx.grid.Grid):
    """grid for saves"""
    def __init__(self, parent, handler):
        pname = handler.master_dom.setAttribute("name", 'Saves')
        wx.grid.Grid.__init__(self, parent, -1, style=wx.SUNKEN_BORDER | wx.WANTS_CHARS)
        self.Bind(wx.EVT_SIZE, self.on_size)
        self.Bind(wx.grid.EVT_GRID_CELL_CHANGE, self.on_cell_change)
        self.handler = handler
        saves = handler.master_dom.getElementsByTagName('save')
        self.stats = handler.char_hander.child_handlers['abilities']
        self.CreateGrid(len(saves),7)
        self.SetRowLabelSize(0)
        col_names = ['Save','Key','base','Abil','Magic','Misc','Total']
        for i in range(len(col_names)):
            self.SetColLabelValue(i,col_names[i])
        self.saves = saves
        i = 0
        for i in range(len(saves)):
            self.refresh_row(i)

    def on_cell_change(self,evt):
        row = evt.GetRow()
        col = evt.GetCol()
        value = self.GetCellValue(row,col)
        try:
            int(value)
            if col == 2:
                self.saves[row].setAttribute('base',value)
            elif col ==4:
                self.saves[row].setAttribute('magmod',value)
            elif col ==4:
                self.saves[row].setAttribute('miscmod',value)
            self.refresh_row(row)
        except:
            self.SetCellValue(row,col,"0")

    def refresh_row(self,rowi):
        s = self.saves[rowi]
        name = s.getAttribute('name')
        self.SetCellValue(rowi,0,name)
        self.SetReadOnly(rowi,0)
        stat = s.getAttribute('stat')
        self.SetCellValue(rowi,1,stat)
        self.SetReadOnly(rowi,1)
        self.SetCellValue(rowi,2,s.getAttribute('base'))
        self.SetCellValue(rowi,3,str(self.stats.get_mod(stat)))
        self.SetReadOnly(rowi,3)
        self.SetCellValue(rowi,4,s.getAttribute('magmod'))
        self.SetCellValue(rowi,5,s.getAttribute('miscmod'))
        mod = str(self.handler.get_mod(name))
        self.SetCellValue(rowi,6,mod)
        self.SetReadOnly(rowi,6)

    def on_size(self,evt):
        (w,h) = self.GetClientSizeTuple()
        cols = self.GetNumberCols()
        col_w = w/(cols+2)
        self.SetColSize(0,col_w*3)
        for i in range(1,cols):
            self.SetColSize(i,col_w)
        evt.Skip()
        self.Refresh()

    def refresh_data(self):
        for r in range(self.GetNumberRows()):
            self.refresh_row(r)


class skill_grid(wx.grid.Grid):
    """ panel for skills """
    def __init__(self, parent, handler):
        pname = handler.master_dom.setAttribute("name", 'Skills')
        wx.grid.Grid.__init__(self, parent, -1, style=wx.SUNKEN_BORDER | wx.WANTS_CHARS)
        self.Bind(wx.EVT_SIZE, self.on_size)
        self.Bind(wx.grid.EVT_GRID_CELL_CHANGE, self.on_cell_change)
        self.handler = handler
        skills = handler.master_dom.getElementsByTagName('skill')
        self.stats = handler.char_hander.child_handlers['abilities']
        self.CreateGrid(len(skills),7)
        self.SetRowLabelSize(0)
        col_names = ['Skill','Key','Rank','Abil','Misc','Total']
        for i in range(len(col_names)):
            self.SetColLabelValue(i,col_names[i])
        rowi = 0
        self.skills = skills
        for i in range(len(skills)):
            self.refresh_row(i)

    def on_cell_change(self,evt):
        row = evt.GetRow()
        col = evt.GetCol()
        value = self.GetCellValue(row,col)
        #print value
        try:
            int(value)
            if col == 3:
                self.skills[row].setAttribute('rank',value)
            elif col ==5:
                self.skills[row].setAttribute('misc',value)
            elif col == 1:
                self.skills[row].setAttribute('untrained',value)
            self.refresh_row(row)
        except:
            self.SetCellValue(row,col,"0")

    def refresh_row(self,rowi):
        s = self.skills[rowi]
        name = s.getAttribute('name')
        self.SetCellValue(rowi,0,name)
        self.SetReadOnly(rowi,0)
        self.SetCellValue(rowi,1,s.getAttribute('untrained'))
        stat = s.getAttribute('stat')
        self.SetCellValue(rowi,2,stat)
        self.SetReadOnly(rowi,2)
        self.SetCellValue(rowi,3,s.getAttribute('rank'))
        self.SetCellValue(rowi,4,str(self.stats.get_mod(stat)))
        self.SetReadOnly(rowi,4)
        self.SetCellValue(rowi,5,s.getAttribute('misc'))
        mod = str(self.handler.get_mod(name))
        self.SetCellValue(rowi,6,mod)
        self.SetReadOnly(rowi,6)

    def on_size(self,evt):
        (w,h) = self.GetClientSizeTuple()
        cols = self.GetNumberCols()
        col_w = w/(cols+2)
        self.SetColSize(0,col_w*3)
        for i in range(1,cols):
            self.SetColSize(i,col_w)
        evt.Skip()
        self.Refresh()

    def refresh_data(self):
        for r in range(self.GetNumberRows()):
            self.refresh_row(r)



class feat_panel(wx.Panel):
    def __init__(self, parent, handler):
        pname = handler.master_dom.setAttribute("name", 'Feats')
        wx.Panel.__init__(self, parent, -1)
        self.grid =wx.grid.Grid(self, -1, style=wx.SUNKEN_BORDER | wx.WANTS_CHARS)
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        remove_btn = wx.Button(self, wx.ID_ANY, "Remove Feat")
        add_btn = wx.Button(self, wx.ID_ANY, "Add Feat")
        sizer.Add(remove_btn, 1, wx.EXPAND)
        sizer.Add(wx.Size(10,10))
        sizer.Add(add_btn, 1, wx.EXPAND)
        self.sizer = sizer
        self.SetSizer(self.sizer)
        self.Bind(wx.EVT_SIZE, self.on_size)
        self.Bind(wx.EVT_BUTTON, self.on_remove, remove_btn)
        self.Bind(wx.EVT_BUTTON, self.on_add, add_btn)

        n_list = handler.master_dom._get_childNodes()
        self.n_list = n_list
        self.master_dom = handler.master_dom
        self.grid.CreateGrid(len(n_list),2,1)
        self.grid.SetRowLabelSize(0)
        self.grid.SetColLabelValue(0,"Feat")
        self.grid.SetColLabelValue(1,"Type")
        for i in range(len(n_list)):
            self.refresh_row(i)
        self.temp_dom = None

    def refresh_row(self,i):
        feat = self.n_list[i]
        name = feat.getAttribute('name')
        type = feat.getAttribute('type')
        self.grid.SetCellValue(i,0,name)
        self.grid.SetReadOnly(i,0)
        self.grid.SetCellValue(i,1,type)
        self.grid.SetReadOnly(i,1)

    def on_remove(self,evt):
        rows = self.grid.GetNumberRows()
        for i in range(rows):
            if self.grid.IsInSelection(i,0):
                self.grid.DeleteRows(i)
                self.master_dom.removeChild(self.n_list[i])

    def on_add(self,evt):
        if not self.temp_dom:
            tmp = open(dir_struct["SWd20"]+"d20feats.xml","r")
            xml_dom = parseXml_with_dlg(self,tmp.read())
            xml_dom = xml_dom._get_firstChild()
            tmp.close()
            self.temp_dom = xml_dom
        f_list = self.temp_dom.getElementsByTagName('feat')
        opts = []
        for f in f_list:
            opts.append(f.getAttribute('name'))
        dlg = wx.SingleChoiceDialog(self,'Choose Feat','Feats',opts)
        if dlg.ShowModal() == wx.ID_OK:
            i = dlg.GetSelection()
            new_node = self.master_dom.appendChild(f_list[i].cloneNode(False))
            self.grid.AppendRows(1)
            self.refresh_row(self.grid.GetNumberRows()-1)
        dlg.Destroy()


    def on_size(self,event):
        s = self.GetClientSizeTuple()
        self.grid.SetDimensions(0,0,s[0],s[1]-25)
        self.sizer.SetDimension(0,s[1]-25,s[0],25)
        (w,h) = self.grid.GetClientSizeTuple()
        cols = self.grid.GetNumberCols()
        col_w = w/(cols)
        for i in range(0,cols):
            self.grid.SetColSize(i,col_w)

class attack_grid(wx.grid.Grid):
    """grid for attacks"""
    def __init__(self, parent, handler):
        pname = handler.master_dom.setAttribute("name", 'Melee')
        wx.grid.Grid.__init__(self, parent, -1, style=wx.SUNKEN_BORDER | wx.WANTS_CHARS)
        self.parent = parent
        self.handler = handler
        self.rows = (self.handler.melee,self.handler.ranged)
        self.CreateGrid(2,10)
        self.SetRowLabelSize(0)
        col_names = ['Type','base','base 2','base 3','base 4','base 5','base 6','abil','misc','Total']
        for i in range(len(col_names)):
            self.SetColLabelValue(i,col_names[i])
        self.SetCellValue(0,0,"Melee")
        self.SetCellValue(1,0,"Ranged")
        self.refresh_data()
        self.Bind(wx.EVT_SIZE, self.on_size)
        self.Bind(wx.grid.EVT_GRID_CELL_CHANGE, self.on_cell_change)

    def on_cell_change(self,evt):
        row = evt.GetRow()
        col = evt.GetCol()
        value = self.GetCellValue(row,col)
        try:
            int(value)
            if col==1:
                self.rows[row].setAttribute('base',value)
            elif col==2:
                self.rows[row].setAttribute('second',value)
            elif col==3:
                self.rows[row].setAttribute('third',value)
            elif col==4:
                self.rows[row].setAttribute('forth',value)
            elif col==5:
                self.rows[row].setAttribute('fifth',value)
            elif col==6:
                self.rows[row].setAttribute('sixth',value)
            elif col==8:
                self.rows[row].setAttribute('misc',value)
            self.parent.refresh_data()
        except:
            self.SetCellValue(row,col,"0")

    def refresh_data(self):
        melee = self.handler.get_attack_data('m')
        ranged = self.handler.get_attack_data('r')
        for i in range(0,7):
            self.SetCellValue(0,i+1,str(melee[i]))
            self.SetCellValue(1,i+1,str(ranged[i]))
        self.SetCellValue(0,9,str(melee[0]+melee[6]+melee[7]))
        self.SetCellValue(1,9,str(ranged[0]+ranged[6]+ranged[7]))
        self.SetReadOnly(0,0)
        self.SetReadOnly(1,0)
        self.SetReadOnly(0,7)
        self.SetReadOnly(1,7)
        self.SetReadOnly(0,9)
        self.SetReadOnly(1,9)


    def on_size(self,evt):
        (w,h) = self.GetClientSizeTuple()
        cols = self.GetNumberCols()
        col_w = w/(cols+1)
        self.SetColSize(0,col_w*2)
        for i in range(1,cols):
            self.SetColSize(i,col_w)
        evt.Skip()
        self.Refresh()

class weapon_panel(wx.Panel):
    def __init__(self, parent, handler):
        pname = handler.master_dom.setAttribute("name", 'Weapons')
        wx.Panel.__init__(self, parent, -1)
        self.grid =wx.grid.Grid(self, -1, style=wx.SUNKEN_BORDER | wx.WANTS_CHARS)
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        remove_btn = wx.Button(self, 10, "Remove Weapon")
        add_btn = wx.Button(self, 20, "Add Weapon")
        sizer.Add(remove_btn, 1, wx.EXPAND)
        sizer.Add(wx.Size(10,10))
        sizer.Add(add_btn, 1, wx.EXPAND)
        self.sizer = sizer
        self.SetSizer(self.sizer)
        self.Bind(wx.EVT_SIZE, self.on_size)
        self.Bind(wx.EVT_BUTTON, self.on_remove, remove_btn)
        self.Bind(wx.EVT_BUTTON, self.on_add, add_btn)
        self.grid.Bind(wx.grid.EVT_GRID_CELL_CHANGE, self.on_cell_change)
        n_list = handler.master_dom.getElementsByTagName('weapon')
        self.n_list = n_list
        self.master_dom = handler.master_dom
        self.handler = handler
        self.grid.CreateGrid(len(n_list),9,1)
        self.grid.SetRowLabelSize(0)
        col_names = ['Name','damage','mod','critical','type','weight','range','size','Total']
        for i in range(len(col_names)):
            self.grid.SetColLabelValue(i,col_names[i])
        self.refresh_data()
        self.temp_dom = None

    def on_cell_change(self,evt):
        row = evt.GetRow()
        col = evt.GetCol()
        value = self.grid.GetCellValue(row,col)
        if col == 0:
            self.n_list[row].setAttribute('name',value)
        elif col == 2:
            try:
                int(value)
                self.n_list[row].setAttribute('mod',value)
                self.refresh_row(row)
            except:
                self.grid.SetCellValue(row,col,"1")
        else:
            self.n_list[row].setAttribute(self.grid.GetColLabelValue(col),value)

    def refresh_row(self,i):
        n = self.n_list[i]
        name = n.getAttribute('name')
        mod = n.getAttribute('mod')
        ran = n.getAttribute('range')
        total = str(int(mod) + self.handler.get_mod(ran))
        self.grid.SetCellValue(i,0,name)
        self.grid.SetCellValue(i,1,n.getAttribute('damage'))
        self.grid.SetCellValue(i,2,mod)
        self.grid.SetCellValue(i,3,n.getAttribute('critical'))
        self.grid.SetCellValue(i,4,n.getAttribute('type'))
        self.grid.SetCellValue(i,5,n.getAttribute('weight'))
        self.grid.SetCellValue(i,6,ran)
        self.grid.SetCellValue(i,7,n.getAttribute('size') )
        self.grid.SetCellValue(i,8,total)
        self.grid.SetReadOnly(i,8)

    def on_remove(self,evt):
        rows = self.grid.GetNumberRows()
        for i in range(rows):
            if self.grid.IsInSelection(i,0):
                self.grid.DeleteRows(i)
                self.master_dom.removeChild(self.n_list[i])
                self.n_list = self.master_dom.getElementsByTagName('weapon')
                self.handler.refresh_weapons()

    def on_add(self,evt):
        if not self.temp_dom:
            tmp = open(dir_struct["SWd20"]+"d20weapons.xml","r")
            xml_dom = parseXml_with_dlg(self,tmp.read())
            xml_dom = xml_dom._get_firstChild()
            tmp.close()
            self.temp_dom = xml_dom
        f_list = self.temp_dom.getElementsByTagName('weapon')
        opts = []
        for f in f_list:
            opts.append(f.getAttribute('name'))
        dlg = wx.SingleChoiceDialog(self,'Choose Weapon','Weapon List',opts)
        if dlg.ShowModal() == wx.ID_OK:
            i = dlg.GetSelection()
            new_node = self.master_dom.appendChild(f_list[i].cloneNode(False))
            self.grid.AppendRows(1)
            self.n_list = self.master_dom.getElementsByTagName('weapon')
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
        for i in range(1,cols):
            self.grid.SetColSize(i,col_w)

    def refresh_data(self):
        for i in range(len(self.n_list)):
            self.refresh_row(i)


class attack_panel(wx.Panel):
    def __init__(self, parent, handler):
        pname = handler.master_dom.setAttribute("name", 'Melee')
        wx.Panel.__init__(self, parent, -1)

        self.a_grid = attack_grid(self, handler)
        self.w_panel = weapon_panel(self, handler)
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.a_grid, 1, wx.EXPAND)
        self.sizer.Add(self.w_panel, 2, wx.EXPAND)
        self.SetSizer(self.sizer)
        self.Bind(wx.EVT_SIZE, self.on_size)

    def on_size(self,event):
        s = self.GetClientSizeTuple()
        self.sizer.SetDimension(0,0,s[0],s[1])

    def refresh_data(self):
        self.w_panel.refresh_data()
        self.a_grid.refresh_data()


class ac_panel(wx.Panel):
    def __init__(self, parent, handler):
        pname = handler.master_dom.setAttribute("name", 'Armor')
        wx.Panel.__init__(self, parent, -1)
        self.grid =wx.grid.Grid(self, -1, style=wx.SUNKEN_BORDER | wx.WANTS_CHARS)
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        remove_btn = wx.Button(self, 10, "Remove Armor")
        add_btn = wx.Button(self, 20, "Add Armor")
        sizer.Add(remove_btn, 1, wx.EXPAND)
        sizer.Add(wx.Size(10,10))
        sizer.Add(add_btn, 1, wx.EXPAND)
        self.sizer = sizer
        self.SetSizer(self.sizer)
        self.Bind(wx.EVT_SIZE, self.on_size)
        self.Bind(wx.EVT_BUTTON, self.on_remove, remove_btn)
        self.Bind(wx.EVT_BUTTON, self.on_add, add_btn)
        self.grid.Bind(wx.grid.EVT_GRID_CELL_CHANGE, self.on_cell_change)
        self.master_dom = handler.master_dom
        n_list = handler.master_dom._get_childNodes()
        self.n_list = n_list
        col_names = ['Armor','DR','Max Dex','Check Penalty','Weight','Speed (10)','Speed (6)','type']
        self.grid.CreateGrid(len(n_list),len(col_names),1)
        self.grid.SetRowLabelSize(0)
        for i in range(len(col_names)):
            self.grid.SetColLabelValue(i,col_names[i])
        self.atts =['name','bonus','maxdex','checkpenalty','weight','speed','speed6','type']
        for i in range(len(n_list)):
            self.refresh_row(i)
        self.temp_dom = None


    def on_cell_change(self,evt):
        row = evt.GetRow()
        col = evt.GetCol()
        value = self.grid.GetCellValue(row,col)
        if col >= 1 and col <= 5:
            try:
                int(value)
                self.n_list[row].setAttribute(self.atts[col],value)
            except:
                self.grid.SetCellValue(row,col,"0")
        else:
            self.n_list[row].setAttribute(self.atts[col],value)

    def refresh_row(self,i):
        n = self.n_list[i]
        for y in range(len(self.atts)):
            self.grid.SetCellValue(i,y,n.getAttribute(self.atts[y]))

    def on_remove(self,evt):
        rows = self.grid.GetNumberRows()
        for i in range(rows):
            if self.grid.IsInSelection(i,0):
                self.grid.DeleteRows(i)
                self.master_dom.removeChild(self.n_list[i])

    def on_add(self,evt):
        if not self.temp_dom:
            tmp = open(dir_struct["SWd20"]+"d20armor.xml","r")
            xml_dom = parseXml_with_dlg(self,tmp.read())
            xml_dom = xml_dom._get_firstChild()
            tmp.close()
            self.temp_dom = xml_dom
        f_list = self.temp_dom.getElementsByTagName('armor')
        opts = []
        for f in f_list:
            opts.append(f.getAttribute('name'))
        dlg = wx.SingleChoiceDialog(self,'Choose Armor:','Armor List',opts)
        if dlg.ShowModal() == wx.ID_OK:
            i = dlg.GetSelection()
            new_node = self.master_dom.appendChild(f_list[i].cloneNode(False))
            self.grid.AppendRows(1)
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
        for i in range(1,cols):
            self.grid.SetColSize(i,col_w)


class class_panel(wx.Panel):
    def __init__(self, parent, handler):
        pname = handler.master_dom.setAttribute("name", 'Class')
        wx.Panel.__init__(self, parent, -1)
        self.grid =wx.grid.Grid(self, -1, style=wx.SUNKEN_BORDER | wx.WANTS_CHARS)
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        remove_btn = wx.Button(self, wx.ID_ANY, "Remove Class")
        add_btn = wx.Button(self, wx.ID_ANY, "Add Class")
        sizer.Add(remove_btn, 1, wx.EXPAND)
        sizer.Add(wx.Size(10,10))
        sizer.Add(add_btn, 1, wx.EXPAND)
        self.sizer = sizer
        self.SetSizer(self.sizer)
        self.Bind(wx.EVT_SIZE, self.on_size)
        self.Bind(wx.EVT_BUTTON, self.on_remove, remove_btn)
        self.Bind(wx.EVT_BUTTON, self.on_add, add_btn)
        self.grid.Bind(wx.grid.EVT_GRID_CELL_CHANGE, self.on_cell_change)

        n_list = handler.master_dom._get_childNodes()
        self.n_list = n_list
        self.master_dom = handler.master_dom
        self.grid.CreateGrid(len(n_list),2,1)
        self.grid.SetRowLabelSize(0)
        self.grid.SetColLabelValue(0,"Class")
        self.grid.SetColLabelValue(1,"Level")
        for i in range(len(n_list)):
            self.refresh_row(i)
        self.temp_dom = None

    def on_cell_change(self,evt):
        row = evt.GetRow()
        col = evt.GetCol()
        value = self.grid.GetCellValue(row,col)
        try:
            int(value)
            self.n_list[row].setAttribute('level',value)
        except:
            self.grid.SetCellValue(row,col,"1")


    def refresh_row(self,i):
        n = self.n_list[i]
        name = n.getAttribute('name')
        level = n.getAttribute('level')
        self.grid.SetCellValue(i,0,name)
        self.grid.SetReadOnly(i,0)
        self.grid.SetCellValue(i,1,level)
        #self.grid.SetReadOnly(i,1)

    def on_remove(self,evt):
        rows = self.grid.GetNumberRows()
        for i in range(rows):
            if self.grid.IsInSelection(i,0):
                self.grid.DeleteRows(i)
                self.master_dom.removeChild(self.n_list[i])

    def on_add(self,evt):
        if not self.temp_dom:
            tmp = open(dir_struct["SWd20"]+"SWd20classes.xml","r")
            xml_dom = parseXml_with_dlg(self,tmp.read())
            xml_dom = xml_dom._get_firstChild()
            tmp.close()
            self.temp_dom = xml_dom
        f_list = self.temp_dom.getElementsByTagName('class')
        opts = []
        for f in f_list:
            opts.append(f.getAttribute('name'))
        dlg = wx.SingleChoiceDialog(self,'Choose Class','Classes',opts)
        if dlg.ShowModal() == wx.ID_OK:
            i = dlg.GetSelection()
            new_node = self.master_dom.appendChild(f_list[i].cloneNode(False))
            self.grid.AppendRows(1)
            self.refresh_row(self.grid.GetNumberRows()-1)
        dlg.Destroy()


    def on_size(self,event):
        s = self.GetClientSizeTuple()
        self.grid.SetDimensions(0,0,s[0],s[1]-25)
        self.sizer.SetDimension(0,s[1]-25,s[0],25)
        (w,h) = self.grid.GetClientSizeTuple()
        cols = self.grid.GetNumberCols()
        col_w = w/(cols)
        for i in range(0,cols):
            self.grid.SetColSize(i,col_w)
