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
# File: dnd3e.py
# Author: Chris Davis & Digitalxero
# Maintainer: leadb
# Version:
#   $Id: dnd3e.py,v 1.33 2006/11/04 21:24:21 digitalxero Exp $
#
# Description: The file contains code for the dnd3e nodehanlers
#
# qpatch by lead.b.  All modified lines denoted by # 1.500x[or] as below
# 1.5001r fix for unable to update misc modifier for saves
# 1.5002r fix for dnd_globals not scoping 1 character's data from another -or
#        causing abends or other problems due to lack of intialization from
#        char abilities.  getCharacterProp function added.
#           This includes fix for "total on saves", making "rclick" on skill
#           work to send roll to window,"total on skill rolls",
# 1.5004r getting ac mod for
#       those skill which have armour class adjustments was broken.
# 1.5005r perhaps no lines marked.  Under dnd3eattacks, the misc. value for
#       both Melee and Ranged do not get re-displayed if the panel is closed
#       and re-opened, tho the adjustment still seems to be in total... perhap
#       total just isn't getting recalculated?
# 1.5006r on rclick on a weapon, on first attack roll is generated, additional
#       crash,terminating the sequence.
# 1.5008r extended bonuses for "extra" attacks don't include all items.
# 1.5009r while 1.5008 is "resolved", not sure it is correct for special monk
#       attacks.  I'm pretty sure I fixed this.
# 1.5014r powerpoints are broken.
# 1.5017r if you bring up the entire character in edit mode (dlclick on
#       top node of character), and click
#       "Money and Inventory" tab, then change the amount of "plat" a
#       character has, the name on the tree will be updated to match
#       the "plat" entry.
# 1.5019r if str bonus was 0, forgot + for aStrengthMod.
# ---v 1.6 cut. above corrected by 1.6.
# -- items marked 1.5xxx were found prior 1.6 but not added (enhancements)
#       or corrected (bugs, default if not stated) at that cut point
# 1.5003r this is currently just a "this is busted" flag, this is an rclick on
#       on the saves node (above the fort/wil/ref saves) itself.  It throws an
#       error message into the python window, then nothing... Not even sure what
#       it is -supposed- to do. set to do nothing, which I think is fine.
# 1.5011r enhancement.  Damage for thrown weapon should get str adder.
#       Don't think this is accounted for.  Remember, JUST damage, not to-hit.
#       included into 1.6002, marking resolved to simplify list.
# 1.5012r enhancement.  str penalty to dam for bow/slings should be applied.
#       but it's not. Remember, this is just for damage, not to-hit.
# 1.5015r if you bring up the entire character in edit mode (dlclick on
#       top node of character), and click
#       "Spells and Powers" tab, then "Psionic Powers", push the "Refresh
#       Powers" button, the powers are refreshed but if you select the
#       "PowerPoints" tab, the update is not reflected there.  Must close
#       and reopen edit session for refresh. (Already corrected misspelling of
#       "Pionic" -> "Psionic")
# 1.6000r eliminate misc debug items, include things like getCharacterProp which
#       never got used.  Documenting for completeness.  Minor changes for clarity
# 1.6001r bug, melee weapons, such as dagger, which have a range are currently
#       being treated simply as ranged weapons... this mean dex bonuses
#       are being applied for to-hit Vs strength.  Melee thrown are treated
#       different than ranged.
# 1.6003r bug, if double weapon handle damage specified as 1d8/1d6 as 1d8
#       for single weapon usage.  The correct usage for double weapon will
#       for short term at least remove requirement to have to update
#       memorized list.  - med priority
# 1.6008r C:\Program Files\openrpg1\orpg\templates\nodes\dnd3e.xml minor
#       typos corrected, added comment on psionics.  Remember to replace!
# 1.6009r tohtml fails, thus send to chat fails and pretty print fails.
# 1.6010r tohtml for power points needs some clean up.
# 1.6011r if multiple weapons are chosen for deletion from character inventory,
#       at least one wrong weapons will be deleted.
# 1.6012r flurry attack negative only applied to med monk, applies to all.
# 1.6013r penalties on stats on tohtml showed +-3, instead of just -3.
# 1.6014r rclick on "Skills" node above actual skills throws an error msg to
#       python window.
# 1.6015r rclick on "Attacks" or "Abilities Score" node throws an error msg to
#       python window.
# 1.6016r enhancement add comment to rclick footnotes to get footnote details.
# 1.6018r resolve saves not updating on panel if open when ability scores change
#       change
# 1.6021r didn't roll extra monk attacks if base to it bonus was 0.
# 1.6022r monks always got d20 damage, reversed order of checks to fix.
# v1.8 cut.
# -- items marked 1.6xxx were found prior 1.8 but not added (enhancements)
#       or corrected (bugs, default if not stated) at that cut point
# 1.5007o enhancement. str bows not accounted for correctly.
#       thoughts: use new element tag to indicate strBow(3).
# 1.5010r proposed enhancement.  Adding character name to frames around stuff.
#    - marking resolved... determined to not do.
# 1.5013o enhancement. this is for all "off-hand" attacks stuff. Eg: str bonus
#       only 1/2 for "off-hand" for both to-hit and damage (unless penalty! ;-)
#       Probably other things, as I see nothing in here to account for them.
# 1.5016o enhancement. swim check does not reflect weight check.
# 1.5018o enhancement. actual psionic abilities list.
# 1.6002o enhancement.  modify code to take advanage of new footnote field for
#       indicating which weapons are Thrown, as opposed to improvised thrown
#       weapons; which are treated differently.  Allow for throwing of melee
#       weapons (with 1.6001 all melee are unthrowable) recast of 1.5011,
#       which I'm marking resolved.
# 1.6004o feature request from 541659 Ability to remove skills, at least those
#       that can't be used untrained.  This would also require ability to re-add
#       skills later.  Short term solution may be to ability to clearly mark
#       skill which can't be used yet. - low priority.
# 1.6005o feature request from 541659 Custom feats, without the need to edit
#       data/dnd3e/dnd3efeats.xml  Note, while standard feats may be affecting
#       how tool will generate rolls, etc; it is unlikely that custom feats will
#       will be able to do this; but should be able to be include from a
#       complete "character sheet" perspective. - low priority (since
#       dnd3efeats can be edited to add feats)
# 1.6006o feature request from 541659 Do sorcerer and bard spells right;
#       for short term at least remove requirement to have to update
#       memorized list.  - med priority
# 1.6007o feature request from 541659 Make tabs optional to be able to remove
#       tabs which are unused by a particular character.  Would need ability
#       to add them back in, since character might later add a class which
#       would need them. - very low priority
# 1.6017o enhancement when editing footnotes for weapons,
#       provide full table of footnotes in companion window to help.
# 1.6019o enhancement Forum request to add "flatfooted" to ac matrix
# 1.6020o enh add column to skills to allow tracking of skill points allocated.
# 1.9000r clean up of excess comments from 1.6 and earlier.
# 1.9001r if str or dex changes, Melee/Ranged combat ability does not update
#        until refreshed by a change.
# 1.9002r depending on what subwindows were open, changing stat scores could
#        crash out entire orpg environment.
#
# r- resolved
# o- open
#
import orpg.tools.orpg_settings
import orpg.minidom
from core import *
from containers import *
from string import *  #a 1.6003
from inspect import *  #a 1.9001
dnd3e_EXPORT = wx.NewId()
############Global Stuff##############

HP_CUR = wx.NewId()
HP_MAX = wx.NewId()
PP_CUR = wx.NewId()
PP_MAX = wx.NewId()
PP_FRE = wx.NewId()
PP_MFRE = wx.NewId()
HOWTO_MAX = wx.NewId()

def getRoot (node): # a 1.5002 this whole function is new.
    root = None
    target = node
    while target != None:
        root = target
        target = target.hparent
    return root
#o 1.5002 (this whole comment block)
# if a method runs getRoot for its instance and assigns the
# value returned to self.root, you can get to instances X via Y
# instance handle   via     invocation
# ---------------   ---     -----------
# classes           via     self.root.classes
# abilities         via     self.root.abilities
# pp                via     self.root.pp
# general           via     self.root.general
# saves             via     self.root.saves
# attacks           via     self.root.attacks
# ac                via     self.root.ac
# feats             via     self.root.feats
# spells            via     self.root.spells
# divine            via     self.root.divine
# powers            via     self.root.powers
# inventory         via     self.root.inventory
# hp                via     self.root.hp
# skills            via     self.root.skills
#... if other instances are needed and the instance exists uniquely,
# add to the instance you need access to in the __init__ section the following:
#       self.hparent = parent # or handler if a wx instance, also add up chain
#       self.root = getRoot(self)
#       self.root.{instance handle} = self
#       # replace {instance handle} with your designation
# then, where you need access to the instance, simply add this to the instance
# that needs to reference
#       self.hparent = getRoot(self) # in the init section, if not already there
#       self.root = getRoot(self)    # also in the init
#   then to refer to the instance where you need it:
#       self.root.{instance handle}.{whatever you need}
#       # replace {instance handle} with your designation
#       # replace {whatever you need} with the attribute/method u want.

#d 1.6000 not used.
#def getCharacterProp(forgetIt):
#    return None

#a 1.6 convinience function added safeGetAttr
def safeGetAttr(node,lable,defRetV=None):
    cna=node.attributes
    for i2 in range(len(cna)):
        if cna.item(i2).name == lable:
            return cna.item(i2).value
    #retV=node.getAttribute(lable) # getAttribute does not distingish between
    # the attribute not being present vs it having a value of ""
    # This is bad for this routine, thus not used.
    return defRetV
#a 1.6... safeGetAttr end.

########End of My global Stuff########
########Start of Main Node Handlers#######
class dnd3echar_handler(container_handler):
    """ Node handler for a dnd3e charactor
        <nodehandler name='?'  module='dnd3e' class='dnd3echar_handler2'  />
    """
    def __init__(self,xml_dom,tree_node):
        node_handler.__init__(self,xml_dom,tree_node)
        self.Version = "v1.901" #a 1.6000 general documentation, usage.

        print "dnd3echar_handler - version:",self.Version #m 1.6000

        self.hparent = None #a 1.5002 allow ability to run up tree, this is the
        #a 1.5002 top of the handler tree, this is used to flag where to stop
        #a 1.5002 on the way up.  Changing this will break getRoot(self)

        self.frame = open_rpg.get_component('frame')
        self.child_handlers = {}
        self.new_child_handler('howtouse','HowTo use this tool',dnd3ehowto,'note')
        self.new_child_handler('general','GeneralInformation',dnd3egeneral,'gear')
        self.new_child_handler('inventory','MoneyAndInventory',dnd3einventory,'money')
        self.new_child_handler('character','ClassesAndStats',dnd3eclassnstats,'knight')
        self.new_child_handler('snf','SkillsAndFeats',dnd3eskillsnfeats,'book')
        self.new_child_handler('combat','Combat',dnd3ecombat,'spears')
        self.new_child_handler('snp','SpellsAndPowers',dnd3esnp,'flask')
        #wxMenuItem(self.tree.std_menu, dnd3e_EXPORT, "Export...", "Export")
        #print "dnd3echar_handler init - "+\
        # "self.child_handlers:",self.child_handlers # a (debug) 1.5002
        self.myeditor = None


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
        html_str = "<table><tr><td colspan=2 >"
        #d block for 1.6009 start
        #html_str += self.child_handlers['general'].tohtml()+"</td></tr>"
        #html_str += "<tr><td width='50%' valign=top >
        #        "+self.child_handlers['abilities'].tohtml()
        #html_str += "<P>" + self.child_handlers['saves'].tohtml()
        #html_str += "<P>" + self.child_handlers['attacks'].tohtml()
        #html_str += "<P>" + self.child_handlers['ac'].tohtml()
        #html_str += "<P>" + self.child_handlers['feats'].tohtml()
        #html_str += "<P>" + self.child_handlers['spells'].tohtml()
        #html_str += "<P>" + self.child_handlers['divine'].tohtml()
        #html_str += "<P>" + self.child_handlers['powers'].tohtml()
        #html_str += "<P>" + self.child_handlers['inventory'].tohtml() +"</td>"
        #html_str += "<td width='50%' valign=top >
        #       "+self.child_handlers['classes'].tohtml()
        #html_str += "<P>" + self.child_handlers['hp'].tohtml()
        #html_str += "<P>" + self.child_handlers['pp'].tohtml()
        #html_str += "<P>" + self.child_handlers['skills'].tohtml() +"</td>"
        #d block for 1.6009 end
        #a block for 1.6009 start
        html_str += self.general.tohtml()+"</td></tr>"
        html_str += "<tr><td width='50%' valign=top >"+self.abilities.tohtml()
        html_str += "<P>" + self.saves.tohtml()
        html_str += "<P>" + self.attacks.tohtml()
        html_str += "<P>" + self.ac.tohtml()
        html_str += "<P>" + self.feats.tohtml()
        html_str += "<P>" + self.spells.tohtml()
        html_str += "<P>" + self.divine.tohtml()
        html_str += "<P>" + self.powers.tohtml()
        html_str += "<P>" + self.inventory.tohtml() +"</td>"
        html_str += "<td width='50%' valign=top >"+self.classes.tohtml()
        html_str += "<P>" + self.hp.tohtml()
        html_str += "<P>" + self.pp.tohtml()
        html_str += "<P>" + self.skills.tohtml() +"</td>"
        #a block for 1.6009 end

        html_str += "</tr></table>"
        return html_str

    def about(self):
        html_str = "<img src='" + orpg.dirpath.dir_struct["icon"]
        html_str += "dnd3e_logo.gif' ><br><b>dnd3e Character Tool "
        html_str += self.Version+"</b>" #m 1.6000 was hard coded.
        html_str += "<br>by Dj Gilcrease<br>digitalxero@gmail.com"
        return html_str

########Core Handlers are done now############
########Onto the Sub Nodes########
##Primary Sub Node##

class outline_panel(wx.Panel):
    def __init__(self, parent, handler, wnd, txt,):
        self.parent = parent #a 1.9001
        wx.Panel.__init__(self, parent, -1)
        self.panel = wnd(self,handler)
        self.sizer = wx.StaticBoxSizer(wx.StaticBox(self,-1,txt), wx.VERTICAL)

        self.sizer.Add(self.panel, 1, wx.EXPAND)
        self.SetSizer(self.sizer)
        self.SetAutoLayout(True)
        self.Fit()

class dnd3e_char_child(node_handler):
    """ Node Handler for skill.  This handler will be
        created by dnd3echar_handler.
    """
    def __init__(self,xml_dom,tree_node,parent):
        node_handler.__init__(self,xml_dom,tree_node)
        self.char_hander = parent
        self.drag = False
        self.frame = open_rpg.get_component('frame')
        self.myeditor = None


    def on_drop(self,evt):
        pass

    def on_rclick(self,evt):
        pass

    def on_ldclick(self,evt):
        return

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

###Child Nodes Organized the way they are in the XML for easier viewing####  #m 1.5002 corrected typo.
class dnd3ehowto(dnd3e_char_child):  #m 1.5002 corrected string below to reflect "how to"
    """ Node Handler for how to instructions.  This handler will be
        created by dnd3echar_handler.
    """
    def __init__(self,xml_dom,tree_node,parent):
        dnd3e_char_child.__init__(self,xml_dom,tree_node,parent)
        self.hparent = parent #a 1.5002 allow ability to run up tree.

    def get_design_panel(self,parent):
        wnd = howto_panel(parent, self)
        wnd.title = "How To"
        return wnd

class howto_panel(wx.Panel):
    def __init__(self, parent, handler):
        wx.Panel.__init__(self, parent, -1)

        pname = handler.master_dom.setAttribute("name", 'How To')
        self.sizer = wx.StaticBoxSizer(wx.StaticBox(self, -1, 'How To'), wx.VERTICAL)
        self.master_dom = handler.master_dom
        n_list = self.master_dom._get_childNodes()
        for n in n_list:
            t_node = safe_get_text_node(n)
        self.sizer.Add(wx.StaticText(self, -1, t_node._get_nodeValue()), 1, wx.EXPAND)
        self.SetSizer(self.sizer)
        self.SetAutoLayout(True)
        self.Fit()

class dnd3egeneral(dnd3e_char_child):
    """ Node Handler for general information.   This handler will be
        created by dnd3echar_handler.
    """
    def __init__(self,xml_dom,tree_node,parent):
        dnd3e_char_child.__init__(self,xml_dom,tree_node,parent)
        self.hparent = parent #a 1.5002 allow ability to run up tree.
        self.root = getRoot(self) #a 1.5002
        self.root.general = self  #a 1.5002
        self.charName = self.get_char_name() # a 1.5002 make getting name easier.

    def get_design_panel(self,parent):
        wnd = outline_panel(parent,self,gen_grid,"General Information")
        wnd.title = "General Info"
        return wnd

    def tohtml(self):
        n_list = self.master_dom._get_childNodes()
        html_str = "<table width=100% border=1 ><tr BGCOLOR=#E9E9E9 ><th>General Information</th></tr><tr><td>"
        for n in n_list:
            t_node = safe_get_text_node(n)
            html_str += "<B>"+n._get_tagName().capitalize() +":</B> "
            html_str += t_node._get_nodeValue() + ", "
        html_str = html_str[:len(html_str)-2] + "</td></tr></table>"
        return html_str

    def on_name_change(self,name):
        self.char_hander.rename(name)
        #o 1.5002 self.char_hander = parent in this case.
        self.charName = name  #a 1.5002 make getting name easier.


    def get_char_name( self ):
        node = self.master_dom.getElementsByTagName( 'name' )[0]
        t_node = safe_get_text_node( node )
        return t_node._get_nodeValue()

class gen_grid(wx.grid.Grid):
    """grid for gen info"""
    def __init__(self, parent, handler):
        pname = handler.master_dom.setAttribute("name", 'General')
        self.hparent = handler #a 1.5002 allow ability to run up tree, needed
        # a 1.5002 parent is functional parent, not invoking parent.


        wx.grid.Grid.__init__(self, parent, -1, style=wx.SUNKEN_BORDER | wx.WANTS_CHARS)
        #self.Bind(wx.EVT_SIZE, self.on_size)
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
        if row==0:
            self.handler.on_name_change(value)
        #self.AutoSizeColumn(1)

    def refresh_row(self,rowi):
        t_node = safe_get_text_node(self.n_list[rowi])

        self.SetCellValue(rowi,0,self.n_list[rowi]._get_tagName())
        self.SetReadOnly(rowi,0)
        self.SetCellValue(rowi,1,t_node._get_nodeValue())
        self.AutoSizeColumn(1)

class dnd3einventory(dnd3e_char_child):
    """ Node Handler for general information.   This handler will be
        created by dnd3echar_handler.
    """
    def __init__(self,xml_dom,tree_node,parent):
        dnd3e_char_child.__init__(self,xml_dom,tree_node,parent)
        self.hparent = parent #a 1.5002 allow ability to run up tree.
        self.root = getRoot(self) #a 1.6009
        self.root.inventory = self #a 1.6009

    def get_design_panel(self,parent):
        wnd = inventory_pane(parent, self) #outline_panel(parent,self,inventory_grid,"Inventory")
        wnd.title = "General Info"
        return wnd

    def tohtml(self):
        n_list = self.master_dom._get_childNodes()
        html_str = "<table width=100% border=1 ><tr BGCOLOR=#E9E9E9 ><th>General Information</th></tr><tr><td>"
        for n in n_list:
            t_node = safe_get_text_node(n)
            html_str += "<B>"+n._get_tagName().capitalize() +":</B> "
            html_str += t_node._get_nodeValue() + "<br>"
        html_str = html_str[:len(html_str)-2] + "</td></tr></table>"
        return html_str

class inventory_pane(wx.Panel):
    def __init__(self, parent, handler):
        wx.Panel.__init__(self, parent, wx.ID_ANY)

        self.n_list = handler.master_dom._get_childNodes()
        self.autosize = False

        self.sizer = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, "Inventroy"), wx.VERTICAL)

        self.lang = wx.TextCtrl(self, wx.ID_ANY, "", style=wx.TE_MULTILINE | wx.TE_BESTWRAP, name="Languages")
        self.gear = wx.TextCtrl(self, wx.ID_ANY, "", style=wx.TE_MULTILINE | wx.TE_BESTWRAP, name="Gear")
        self.magic = wx.TextCtrl(self, wx.ID_ANY, "", style=wx.TE_MULTILINE | wx.TE_BESTWRAP, name="Magic")
        self.grid = wx.grid.Grid(self, wx.ID_ANY, style=wx.SUNKEN_BORDER | wx.WANTS_CHARS)

        self.grid.CreateGrid(len(self.n_list)-3,2)
        self.grid.SetRowLabelSize(0)
        self.grid.SetColLabelSize(0)

        for i in xrange(len(self.n_list)):
            self.refresh_row(i)

        sizer1 = wx.BoxSizer(wx.HORIZONTAL)
        sizer1.Add(self.grid, 1, wx.EXPAND)
        sizer1.Add(self.lang, 1, wx.EXPAND)

        self.sizer.Add(sizer1, 0, wx.EXPAND)

        sizer2 = wx.BoxSizer(wx.HORIZONTAL)
        sizer2.Add(self.gear, 1, wx.EXPAND)
        sizer2.Add(self.magic, 1, wx.EXPAND)

        self.sizer.Add(sizer2, 1, wx.EXPAND)

        self.SetSizer(self.sizer)
        self.SetAutoLayout(True)
        self.Fit()

        self.Bind(wx.EVT_TEXT, self.onTextNodeChange, self.lang)
        self.Bind(wx.EVT_TEXT, self.onTextNodeChange, self.gear)
        self.Bind(wx.EVT_TEXT, self.onTextNodeChange, self.magic)
        self.Bind(wx.grid.EVT_GRID_EDITOR_HIDDEN, self.on_cell_change, self.grid)


    def fillTextNode(self, name, value):
        if name == 'Languages':
            self.lang.SetValue(value)
        elif name == 'Gear':
            self.gear.SetValue(value)
        elif name == 'Magic':
            self.magic.SetValue(value)

    def onTextNodeChange(self, event):
        id = event.GetId()

        if id == self.gear.GetId():
            nodeName = 'Gear'
            value = self.gear.GetValue()
        elif id == self.magic.GetId():
            nodeName = 'Magic'
            value = self.magic.GetValue()
        elif id == self.lang.GetId():
            nodeName = 'Languages'
            value = self.lang.GetValue()

        for node in self.n_list:
            if node._get_tagName() == nodeName:
                t_node = safe_get_text_node(node)
                t_node._set_nodeValue(value)

    def saveMoney(self, row, col):
        value = self.grid.GetCellValue(row, col)
        t_node = safe_get_text_node(self.n_list[row])
        t_node._set_nodeValue(value)

    def on_cell_change(self, evt):
        row = evt.GetRow()
        col = evt.GetCol()
        self.grid.AutoSizeColumn(col)
        wx.CallAfter(self.saveMoney, row, col)



    def refresh_row(self, row):
        t_node = safe_get_text_node(self.n_list[row])
        tagname = self.n_list[row]._get_tagName()
        value = t_node._get_nodeValue()
        if tagname == 'Gear':
            self.fillTextNode(tagname, value)
        elif tagname == 'Magic':
            self.fillTextNode(tagname, value)
        elif tagname == 'Languages':
            self.fillTextNode(tagname, value)
        else:
            self.grid.SetCellValue(row, 0, tagname)
            self.grid.SetReadOnly(row, 0)
            self.grid.SetCellValue(row, 1, value)
            self.grid.AutoSize()


class dnd3eclassnstats(dnd3e_char_child):
    """ Node handler for a dnd3e charactor
        <nodehandler name='?'  module='dnd3e' class='dnd3echar_handler2'  />
    """
    def __init__(self,xml_dom,tree_node,parent):
        node_handler.__init__(self,xml_dom,tree_node)
        self.hparent = parent #a 1.5002 allow ability to run up tree.
        dnd3e_char_child.__init__(self,xml_dom,tree_node,parent)
        self.frame = open_rpg.get_component('frame')
        self.child_handlers = {}
        self.new_child_handler('abilities','Abilities Scores',dnd3eability,'gear')
        self.new_child_handler('classes','Classes',dnd3eclasses,'knight')
        self.new_child_handler('saves','Saves',dnd3esaves,'skull')
        self.myeditor = None


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

class class_char_child(node_handler):
    """ Node Handler for skill.  This handler will be
        created by dnd3echar_handler.
    """
    def __init__(self,xml_dom,tree_node,parent):
        node_handler.__init__(self,xml_dom,tree_node)
        self.char_hander = parent
        self.drag = False
        self.frame = open_rpg.get_component('frame')
        self.myeditor = None

    def on_drop(self,evt):
        pass

    def on_rclick(self,evt):
        pass

    def on_ldclick(self,evt):
        return

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

class dnd3eability(class_char_child):
    """ Node Handler for ability.   This handler will be
        created by dnd3echar_handler.
    """
    def __init__(self,xml_dom,tree_node,parent):
        class_char_child.__init__(self,xml_dom,tree_node,parent)
        self.hparent = parent #a 1.5002 allow ability to run up tree.
        self.root = getRoot(self)  #a 1.5002 get top of our local function tree.
        self.root.abilities = self #a 1.5002 let other classes find me.

        self.abilities = {}
        node_list = self.master_dom.getElementsByTagName('stat')
        tree = self.tree
        icons = tree.icons

        for n in node_list:
            name = n.getAttribute('abbr')
            self.abilities[name] = n
            new_tree_node = tree.AppendItem( self.mytree_node, name, icons['gear'], icons['gear'] )
            tree.SetPyData( new_tree_node, self )
        #print "dnd3eability - init self.abilities",self.abilities #a (debug) 1.5002

    def on_rclick( self, evt ):
        item = self.tree.GetSelection()
        name = self.tree.GetItemText( item )
        #if item == self.mytree_node:   #d 1.6016
        #    dnd3e_char_child.on_ldclick( self, evt ) #d 1.6016
        if not item == self.mytree_node: #a 1.6016
        #else: #d 1.6016
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
        mod = int(mod)
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
            if int(mod) >= 0: #m 1.6013 added "int(" and ")"
                mod1 = "+"
            else:
                mod1 = ""
            html_str = (html_str + "<tr ALIGN='center'><td>"+
                name+"</td><td>"+base+'</td><td>%s%s</td></tr>' % (mod1, mod))
        html_str = html_str + "</table>"
        return html_str

class abil_grid(wx.grid.Grid):
    """grid for abilities"""
    def __init__(self, parent, handler):
        pname = handler.master_dom.setAttribute("name", 'Stats')
        self.hparent = handler #a 1.5002 allow ability to run up tree.
        self.root = getRoot(self)
        #a 1.5002 in this case, we need the functional parent, not the invoking parent.

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
        #print value
        try:
            int(value)
            self.stats[row].setAttribute('base',value)
            self.refresh_row(row)
        except:
            self.SetCellValue(row,col,"0")
        if self.char_wnd:
            self.char_wnd.refresh_data()

    #mark5

    def refresh_row(self,rowi):
        s = self.stats[rowi]

        name = s.getAttribute('name')
        abbr = s.getAttribute('abbr')
        self.SetCellValue(rowi,0,name)
        self.SetReadOnly(rowi,0)
        self.SetCellValue(rowi,1,s.getAttribute('base'))
        self.SetCellValue(rowi,2,str(self.handler.get_mod(abbr)))
        self.SetReadOnly(rowi,2)
        #if self.root.saves.saveGrid: #a 1.6018 d 1.9002 whole if clause
            #print getmembers(self.root.saves.saveGrid)
            #self.root.saves.saveGrid.refresh_data() #a 1.6018
            #print "skipping saving throw update, put back in later"
        self.root.saves.refresh_data() #a 1.9002
        self.root.attacks.refreshMRdata() #a 1.9001 `

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

class dnd3eclasses(class_char_child):
    """ Node Handler for classes.  This handler will be
        created by dnd3echar_handler.
    """
    def __init__(self,xml_dom,tree_node,parent):
        class_char_child.__init__(self,xml_dom,tree_node,parent)
        self.hparent = parent #a 1.5002 allow ability to run up tree.
        self.root = getRoot(self)
        self.root.classes = self
        #a 1.5002 in this case, we need the functional parent, not the invoking parent.

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
        # print "eclasses - get_char_lvl node_list",node_list
        tot = 0  #a 1.5009 actually, slipping in a quick enhancement ;-)
        for n in node_list:
            lvl = n.getAttribute('level') #o 1.5009 not sure of the value of this
            tot += int(lvl) #a 1.5009
            type = n.getAttribute('name') #o 1.5009 not sure of the value of this
            #print type,lvl #a (debug) 1.5009
            if attr == "level":
                return lvl #o 1.5009 this returns the level of someone's first class. ???
            elif attr == "class":
                return type #o 1.5009 this returns one of the char's classes. ???
        if attr == "lvl":   #a 1.5009 this has value, adding this.
            return tot  #a 1.5009 return character's "overall" level.

    def get_class_lvl( self, classN ): #a 1.5009 need to be able to get monk lvl
        #a 1.5009 this function is new.
        node_list = self.master_dom.getElementsByTagName('class')
        #print "eclasses - get_class_lvl node_list",node_list
        for n in node_list:
            lvl = n.getAttribute('level')
            type = n.getAttribute('name')
            if classN == type:
                return lvl

class class_panel(wx.Panel):
    def __init__(self, parent, handler):
        pname = handler.master_dom.setAttribute("name", 'Class')

        wx.Panel.__init__(self, parent, -1)
        self.grid =wx.grid.Grid(self, -1, style=wx.SUNKEN_BORDER | wx.WANTS_CHARS)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.grid, 1, wx.EXPAND)

        sizer1 = wx.BoxSizer(wx.HORIZONTAL)
        sizer1.Add(wx.Button(self, 10, "Remove Class"), 0, wx.EXPAND)
        sizer1.Add(wx.Size(10,10))
        sizer1.Add(wx.Button(self, 20, "Add Class"), 0, wx.EXPAND)

        sizer.Add(sizer1, 0, wx.EXPAND)
        self.sizer = sizer
        self.SetSizer(self.sizer)
        self.SetAutoLayout(True)
        self.Fit()

        #self.Bind(wx.EVT_SIZE, self.on_size)
        self.Bind(wx.EVT_BUTTON, self.on_remove, id=10)
        self.Bind(wx.EVT_BUTTON, self.on_add, id=20)
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
            tmp = open(orpg.dirpath.dir_struct["dnd3e"]+"dnd3eclasses.xml","r")
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


class dnd3esaves(class_char_child):
    """ Node Handler for saves.   This handler will be
        created by dnd3echar_handler.
    """
    def __init__(self,xml_dom,tree_node,parent):
        class_char_child.__init__(self,xml_dom,tree_node,parent)
        self.hparent = parent #a 1.5002 allow ability to run up tree.
        #self.saveGrid = None  #a 1.6018 d 1.9002
        self.saveGridFrame = []  #a 1.9002 handle list, check frame for close.

        tree = self.tree
        icons = self.tree.icons

        self.root = getRoot(self) #a 1.5002
        self.root.saves = self #a 1.6009
        node_list = self.master_dom.getElementsByTagName('save')
        self.saves={}
        for n in node_list:
            name = n.getAttribute('name')
            self.saves[name] = n
            new_tree_node = tree.AppendItem(self.mytree_node,name,icons['gear'],icons['gear'])
            tree.SetPyData(new_tree_node,self)

    #a 1.9002 this whole method
    def refresh_data(self): # refresh the data in the melee/ranged section
        # of the attack chart.
        # count backwards, maintains context despite "removes"
        for i in range(len(self.saveGridFrame)-1,-1,-1):
            x = self.saveGridFrame[i]
            if x == None:
                x.refresh_data()
            else:
                self.saveGridFrame.remove(x)

    def get_mod(self,name):
        save = self.saves[name]
        stat = save.getAttribute('stat')
        #print "dnd3esaves, get_mod: self,root",self,self.root #a (debug) 1.5002
        #print "and abilities",self.root.abilities      #a (debug) 1.5002
        stat_mod = self.root.abilities.get_mod(stat)            #a 1.5002
        base = int(save.getAttribute('base'))
        miscmod = int(save.getAttribute('miscmod'))
        magmod = int(save.getAttribute('magmod'))
        total = stat_mod + base + miscmod + magmod
        return total

    def on_rclick(self,evt):

        item = self.tree.GetSelection()
        name = self.tree.GetItemText(item)
        if item == self.mytree_node:
            pass #a 1.5003 syntatic place holder
            return #a 1.5003
            #print "failure mode!"
            #dnd3e_char_child.on_ldclick(self,evt) #d 1.5003 this busted
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
        html_str = """<table border='1' width=100% ><tr BGCOLOR=#E9E9E9 >
            <th width='30%'>Save</th>
            <th>Key</th><th>Base</th><th>Abil</th><th>Magic</th>
            <th>Misc</th><th>Total</th></tr>"""
        node_list = self.master_dom.getElementsByTagName('save')
        for n in node_list:
            name = n.getAttribute('name')
            stat = n.getAttribute('stat')
            base = n.getAttribute('base')
            html_str = html_str + "<tr ALIGN='center'><td>"+name+"</td><td>"+stat+"</td><td>"+base+"</td>"
            #stat_mod = str(dnd_globals["stats"][stat])         #d 1.5002
            stat_mod = self.root.abilities.get_mod(stat)        #a 1.5002

            mag = n.getAttribute('magmod')
            misc = n.getAttribute('miscmod')
            mod = str(self.get_mod(name))
            if mod >= 0:
                mod1 = "+"
            else:
                mod1 = ""
            #m 1.5009 next line.  added str() around stat_mod
            html_str = html_str + "<td>"+str(stat_mod)+"</td><td>"+mag+"</td>"
            html_str = html_str + '<td>'+misc+'</td><td>%s%s</td></tr>' % (mod1, mod)
        html_str = html_str + "</table>"
        return html_str

#mark6
class save_grid(wx.grid.Grid):
    """grid for saves"""
    def __init__(self, parent, handler):
        pname = handler.master_dom.setAttribute("name", 'Saves')
        self.hparent = handler #a 1.5002 allow ability to run up tree.
        #a 1.5002 in this case, we need the functional parent, not the invoking parent.
        self.root = getRoot(self)

        #self.hparent.saveGrid = self #a 1.6018 d 1.9001


        wx.grid.Grid.__init__(self, parent, -1, style=wx.SUNKEN_BORDER | wx.WANTS_CHARS)
        self.Bind(wx.EVT_SIZE, self.on_size)
        self.Bind(wx.grid.EVT_GRID_CELL_CHANGE, self.on_cell_change)
        self.handler = handler
        saves = handler.master_dom.getElementsByTagName('save')
        self.CreateGrid(len(saves),7)
        self.SetRowLabelSize(0)
        col_names = ['Save','Key','base','Abil','Magic','Misc','Total']
        for i in range(len(col_names)):
            self.SetColLabelValue(i,col_names[i])
        self.saves = saves
        i = 0
        for i in range(len(saves)):
            self.refresh_row(i)


        #a 1.9002 remainder of code in this method.
        climber = parent
        nameNode = climber.GetClassName()
        while nameNode != 'wxFrame':
            climber = climber.parent
            nameNode = climber.GetClassName()
        masterFrame=climber
        masterFrame.refresh_data=self.refresh_data
        #print getmembers(masterFrame)

        handler.saveGridFrame.append(masterFrame)

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
            elif col ==5:                                       # 1.5001
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
        self.SetCellValue(rowi,3,str(self.root.abilities.get_mod(stat)))
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

class dnd3eskillsnfeats(dnd3e_char_child):
    """ Node handler for a dnd3e charactor
        <nodehandler name='?'  module='dnd3e' class='dnd3echar_handler2'  />
    """
    def __init__(self,xml_dom,tree_node,parent):
        self.hparent = parent #a 1.5002 allow ability to run up tree.
        self.root = getRoot(self) #a 1.6009

        #print "dnd3eskillsnfeats - init, self ",self #a (debug) 1.5002
        #print "dnd3eskillsnfeats - init, parent ",self.hparent #a (debug) 1.5002
        #print "dnd3eskillsnfeats - init, parent ",parent.dnd3eclassnstats #a (debug) 1.5002

        node_handler.__init__(self,xml_dom,tree_node)
        dnd3e_char_child.__init__(self,xml_dom,tree_node,parent)
        self.frame = open_rpg.get_component('frame')
        self.child_handlers = {}
        self.new_child_handler('skills','Skills',dnd3eskill,'book')
        self.new_child_handler('feats','Feats',dnd3efeats,'book')
        #wxMenuItem(self.tree.std_menu, dnd3e_EXPORT, "Export...", "Export")
        self.myeditor = None


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

class skills_char_child(node_handler):
    """ Node Handler for skill.  This handler will be
        created by dnd3echar_handler.
    """
    def __init__(self,xml_dom,tree_node,parent):
        node_handler.__init__(self,xml_dom,tree_node)
        self.char_hander = parent
        self.drag = False
        self.frame = open_rpg.get_component('frame')
        self.myeditor = None



    def on_drop(self,evt):
        pass

    def on_rclick(self,evt):
        pass

    def on_ldclick(self,evt):
        return

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

class dnd3eskill(skills_char_child):
    """ Node Handler for skill.  This handler will be
        created by dnd3echar_handler.
    """
    def __init__(self,xml_dom,tree_node,parent):
        self.hparent = parent #a 1.5002 allow ability to run up tree.
        #a 1.5002 Need the functional parent, not the invoking parent.
        self.root = getRoot(self) #a 1.5002
        self.root.skills = self #a 1.6009

        skills_char_child.__init__(self,xml_dom,tree_node,parent)
        tree = self.tree
        icons = self.tree.icons
        node_list = self.master_dom.getElementsByTagName('skill')

        self.skills={}
        #Adding code to not display skills you can not use -mgt
        for n in node_list:
            name = n.getAttribute('name')
            self.skills[name] = n
            skill_check = self.skills[name]
            ranks = int(skill_check.getAttribute('rank'))
            trained = int(skill_check.getAttribute('untrained'))

            if ranks > 0 or trained == 1:
                new_tree_node = tree.AppendItem(self.mytree_node,name,
                                            icons['gear'],icons['gear'])
            else:
                continue

            tree.SetPyData(new_tree_node,self)



    def refresh_skills(self):
                #Adding this so when you update the grid the tree will reflect
                #The change. -mgt
        tree = self.tree
        icons = self.tree.icons
        tree.CollapseAndReset(self.mytree_node)
        node_list = self.master_dom.getElementsByTagName('skill')

        self.skills={}
        for n in node_list:
            name = n.getAttribute('name')
            self.skills[name] = n
            skill_check = self.skills[name]
            ranks = int(skill_check.getAttribute('rank'))
            trained = int(skill_check.getAttribute('untrained'))

            if ranks > 0 or trained == 1:
                new_tree_node = tree.AppendItem(self.mytree_node,name,
                                            icons['gear'],icons['gear'])
            else:
                continue

            tree.SetPyData(new_tree_node,self)

    def get_mod(self,name):
        skill = self.skills[name]
        stat = skill.getAttribute('stat')
        #stat_mod = int(dnd_globals["stats"][stat])                 #d 1.5002
        stat_mod = self.root.abilities.get_mod(stat)                #a 1.5002
        rank = int(skill.getAttribute('rank'))
        misc = int(skill.getAttribute('misc'))
        total = stat_mod + rank + misc
        return total

    def on_rclick(self,evt):
        item = self.tree.GetSelection()
        name = self.tree.GetItemText(item)
        #print "skill rc self",self                 #a 1.6004
        #print "skill rc tree",self.mytree_node     #a 1.6004
        #print "skill rc item",item                 #a 1.6004
        if item == self.mytree_node:
            return
            # following line fails,
            #dnd3e_char_child.on_ldclick(self,evt) #d 1.6014
            # it's what it used to try to do.
        ac = self.root.ac.get_check_pen() #a 1.5002 for 1.5004 verify fix.

        skill = self.skills[name]

        untr = skill.getAttribute('untrained')                         #a 1.6004
        rank = skill.getAttribute('rank')                              #a 1.6004
        if eval('%s == 0' % (untr)):                                   #a 1.6004
            if eval('%s == 0' % (rank)):                               #a 1.6004
                res = 'You fumble around, accomplishing nothing'       #a 1.6004
                txt = '%s Skill Check: %s' % (name, res)               #a 1.6004
                chat = self.chat                                       #a 1.6004
                chat.Post(txt,True,True)                               #a 1.6004
                return                                                 #a 1.6004

        armor = ''
        acCp = ''
        if ac < 0:  #acCp >= 1 #m 1.5004 this is stored as negatives.
            armorCheck = int(skill.getAttribute('armorcheck'))
            #print "ac,armorCheck",ac,armorCheck
            if armorCheck == 1:
                acCp=ac
                armor = '(includes Armor Penalty of %s)' % (acCp)
        if item == self.mytree_node:
            dnd3e_char_child.on_ldclick(self,evt)
            #wnd = skill_grid(self.frame.note,self)
            #wnd.title = "Skills"
            #self.frame.add_panel(wnd)
        else:
            mod = self.get_mod(name)
            if mod >= 0:
                mod1 = "+"
            else:
                mod1 = ""
            chat = self.chat
            txt = '%s Skill Check: [1d20%s%s%s] %s' % (
                    name, mod1, mod, acCp, armor)
            chat.ParsePost(txt,True,True)

    def get_design_panel(self,parent):
        wnd = outline_panel(parent,self,skill_grid,"Skills")
        wnd.title = "Skills (edit)"
        return wnd

    def tohtml(self):
        html_str = """<table border='1' width=100% ><tr BGCOLOR=#E9E9E9 >
                    <th width='30%'>Skill</th><th>Key</th>
                    <th>Rank</th><th>Abil</th><th>Misc</th><th>Total</th></tr>"""
        node_list = self.master_dom.getElementsByTagName('skill')

        for n in node_list:
            name = n.getAttribute('name')
            stat = n.getAttribute('stat')
            rank = n.getAttribute('rank')
            untr = n.getAttribute('untrained')                              #a 1.6004
            #Filter unsuable skills out of pretty print -mgt
            if eval('%s > 0' % (rank)) or eval('%s == 1' % (untr)):
                if eval('%s >=1' % (rank)):
                    html_str += "<tr ALIGN='center' bgcolor='#CCCCFF'><td>"     #a 1.6004
                    #html_str += "<tr ALIGN='center' bgcolor='green'><td>"      #d 1.6004
                    html_str += name+"</td><td>"+stat+"</td><td>"+rank+"</td>"
                elif eval('%s == 1' % (untr)):                                  #a 1.6004
                    html_str += "<tr ALIGN='center' bgcolor='#C0FF40'><td>"     #a 1.6004
                    html_str += name+"</td><td>"+stat+"</td><td>"+rank+"</td>"  #a 1.6004
                else:
                    html_str += "<tr ALIGN='center'><td>"+name+"</td><td>"
                    html_str += stat+"</td><td>"+rank+"</td>"
            else:
                continue
            stat_mod = self.root.abilities.get_mod(stat)        #a 1.5002
            #stat_mod = str(dnd_globals["stats"][stat])         #d 1.5002
            misc = n.getAttribute('misc')
            mod = str(self.get_mod(name))
            if mod >= 0:
                mod1 = "+"
            else:
                mod1 = ""
            html_str += "<td>"+str(stat_mod)+"</td><td>"+misc #m 1.6009 str()
            html_str += '</td><td>%s%s</td></tr>' % (mod1, mod)
        html_str = html_str + "</table>"
        return html_str


class skill_grid(wx.grid.Grid):
    """ panel for skills """
    def __init__(self, parent, handler):
        self.hparent = handler    #a 1.5002 need function parent, not invoker
        self.root = getRoot(self) #a 1.5002
        pname = handler.master_dom.setAttribute("name", 'Skills')

        wx.grid.Grid.__init__(self, parent, -1, style=wx.SUNKEN_BORDER | wx.WANTS_CHARS)
        self.Bind(wx.EVT_SIZE, self.on_size)
        self.Bind(wx.grid.EVT_GRID_CELL_CHANGE, self.on_cell_change)
        self.handler = handler
        skills = handler.master_dom.getElementsByTagName('skill')
        #xelf.stats = dnd_globals["stats"]                           #d 1.5002

        self.CreateGrid(len(skills),6)
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
            if col == 2:
                self.skills[row].setAttribute('rank',value)
            elif col ==4:
                self.skills[row].setAttribute('misc',value)
            self.refresh_row(row)
        except:
            self.SetCellValue(row,col,"0")

                #call refresh_skills
        self.handler.refresh_skills()

    def refresh_row(self,rowi):
        s = self.skills[rowi]
        name = s.getAttribute('name')
        self.SetCellValue(rowi,0,name)
        self.SetReadOnly(rowi,0)
        stat = s.getAttribute('stat')
        self.SetCellValue(rowi,1,stat)
        self.SetReadOnly(rowi,1)
        self.SetCellValue(rowi,2,s.getAttribute('rank'))
        #self.SetCellValue(rowi,3,str(dnd_globals["stats"][stat]))  #d 1.5002
        if self.root.abilities: #a 1.5002 sanity check.
            stat_mod=self.root.abilities.get_mod(stat)           #a 1.5002
        else: #a 1.5002
            stat_mod = -6 #a 1.5002 this can happen if code is changed so
            #a 1.5002 that abilities are not defined prior invokation of init.
            print "Please advise dnd3e maintainer alert 1.5002 raised"

        self.SetCellValue(rowi,3,str(stat_mod))         #a 1.5002
        self.SetReadOnly(rowi,3)
        self.SetCellValue(rowi,4,s.getAttribute('misc'))
        mod = str(self.handler.get_mod(name))
        self.SetCellValue(rowi,5,mod)
        self.SetReadOnly(rowi,5)

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




class dnd3efeats(skills_char_child):
    """ Node Handler for classes.  This handler will be
        created by dnd3echar_handler.
    """
    def __init__(self,xml_dom,tree_node,parent):
        skills_char_child.__init__(self,xml_dom,tree_node,parent)
        self.hparent = parent #a 1.5002 allow ability to run up tree.
        self.root = getRoot(self) #a 1.5002
        self.root.feats = self #a 1.6009


    def get_design_panel(self,parent):
        setTitle="Feats - " + self.root.general.charName    #a 1.5010
        wnd = outline_panel(parent,self,feat_panel,setTitle) #a 1.5010
        #wnd = outline_panel(parent,self,feat_panel,"Feats") #d 1.5010
        wnd.title = "Feats" #d 1.5010
        #wnd.title = "Feats - " + self.charName
        return wnd

    def tohtml(self):
        html_str = "<table width=100% border=1 ><tr BGCOLOR=#E9E9E9 ><th>Feats</th></tr><tr><td>"
        n_list = self.master_dom._get_childNodes()
        for n in n_list:
            html_str += n.getAttribute('name')+ ", "
        html_str = html_str[:len(html_str)-2] + "</td></tr></table>"
        return html_str

class feat_panel(wx.Panel):
    def __init__(self, parent, handler):

        self.hparent = handler #a 1.5002 allow ability to run up tree.
        #a 1.5002 in this case, we need the functional parent, not the invoking parent.
        self.root = getRoot(self) #a 1.5002
        #tempTitle= 'Feats - ' + self.root.general.charName #a 1.5010
        #pname = handler.master_dom.setAttribute("name", tempTitle) #a 1.5010
        pname = handler.master_dom.setAttribute("name", 'Feats') #d 1.5010

        wx.Panel.__init__(self, parent, -1)
        self.grid =wx.grid.Grid(self, -1, style=wx.SUNKEN_BORDER | wx.WANTS_CHARS)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.grid, 1, wx.EXPAND)

        sizer1 = wx.BoxSizer(wx.HORIZONTAL)
        sizer1.Add(wx.Button(self, 10, "Remove Feat"), 0, wx.EXPAND)
        sizer1.Add(wx.Size(10,10))
        sizer1.Add(wx.Button(self, 20, "Add Feat"), 0, wx.EXPAND)

        sizer.Add(sizer1, 0, wx.EXPAND)
        self.sizer = sizer

        self.SetSizer(self.sizer)
        self.SetAutoLayout(True)
        self.Fit()

        #self.Bind(wx.EVT_SIZE, self.on_size)
        self.Bind(wx.EVT_BUTTON, self.on_remove, id=10)
        self.Bind(wx.EVT_BUTTON, self.on_add, id=20)

        n_list = handler.master_dom._get_childNodes()
        self.n_list = n_list
        self.master_dom = handler.master_dom
        self.grid.CreateGrid(len(n_list),3,1)
        self.grid.SetRowLabelSize(0)
        self.grid.SetColLabelValue(0,"Feat")
        self.grid.SetColLabelValue(1,"Type")
        self.grid.SetColLabelValue(2,"Reference") #m 1.6 typo correction.
        for i in range(len(n_list)):
            self.refresh_row(i)
        self.temp_dom = None

    def refresh_row(self,i):
        feat = self.n_list[i]

        name = feat.getAttribute('name')
        type = feat.getAttribute('type')
        desc = feat.getAttribute('desc') #m 1.6 correct typo
        self.grid.SetCellValue(i,0,name)
        self.grid.SetReadOnly(i,0)
        self.grid.SetCellValue(i,1,type)
        self.grid.SetReadOnly(i,1)
        self.grid.SetCellValue(i,2,desc) #m 1.6 correct typo
        self.grid.SetReadOnly(i,2)

    def on_remove(self,evt):
        rows = self.grid.GetNumberRows()
        for i in range(rows):
            if self.grid.IsInSelection(i,0):
                self.grid.DeleteRows(i)
                self.master_dom.removeChild(self.n_list[i])

    def on_add(self,evt):

        if not self.temp_dom:
            tmp = open(orpg.dirpath.dir_struct["dnd3e"]+"dnd3efeats.xml","r")
            xml_dom = parseXml_with_dlg(self,tmp.read())
            xml_dom = xml_dom._get_firstChild()
            tmp.close()
            self.temp_dom = xml_dom
        f_list = self.temp_dom.getElementsByTagName('feat')
        opts = []
        for f in f_list:
            opts.append(f.getAttribute('name') + "  -  [" +
                     f.getAttribute('type') + "]  -  " + f.getAttribute('desc'))
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

class dnd3ecombat(dnd3e_char_child):
    """ Node handler for a dnd3e charactor
        <nodehandler name='?'  module='dnd3e' class='dnd3echar_handler2'  />
    """
    def __init__(self,xml_dom,tree_node,parent):

        node_handler.__init__(self,xml_dom,tree_node)

        self.hparent = parent #a 1.5002 allow ability to run up tree.
        self.root = getRoot(self) #a 1.5012



        #mark3
        dnd3e_char_child.__init__(self,xml_dom,tree_node,parent)
        self.frame = open_rpg.get_component('frame')
        self.child_handlers = {}
        self.new_child_handler('hp','Hit Points',dnd3ehp,'gear')
        self.new_child_handler('attacks','Attacks',dnd3eattacks,'spears')
        self.new_child_handler('ac','Armor',dnd3earmor,'spears')
        #print "combat",self.child_handlers #a (debug) 1.5002
        #wxMenuItem(self.tree.std_menu, dnd3e_EXPORT, "Export...", "Export")
        self.myeditor = None


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


class combat_char_child(node_handler):
    """ Node Handler for combat.  This handler will be
        created by dnd3echar_handler.
    """
    def __init__(self,xml_dom,tree_node,parent):
        node_handler.__init__(self,xml_dom,tree_node)
        self.char_hander = parent
        self.drag = False
        self.frame = open_rpg.get_component('frame')
        self.myeditor = None


    def on_drop(self,evt):
        pass

    def on_rclick(self,evt):
        pass

    def on_ldclick(self,evt):
        return

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

class dnd3ehp(combat_char_child):
    """ Node Handler for hit points.  This handler will be
        created by dnd3echar_handler.
    """
    def __init__(self,xml_dom,tree_node,parent):
        combat_char_child.__init__(self,xml_dom,tree_node,parent)
        self.hparent = parent #a 1.5002 allow ability to run up tree.
        self.root = getRoot(self) #a 1.6009
        self.root.hp = self #a 1.6009

    def get_design_panel(self,parent):
        wnd = outline_panel(parent,self,hp_panel,"Hit Points")
        wnd.title = "Hit Points"
        return wnd

    def on_rclick( self, evt ):
        chp = self.master_dom.getAttribute('current')
        mhp = self.master_dom.getAttribute('max')
        txt = '((HP: %s / %s))' % ( chp, mhp )
        self.chat.ParsePost( txt, True, True )

    def tohtml(self):
        html_str = "<table width=100% border=1 >"
        html_str += "<tr BGCOLOR=#E9E9E9 ><th colspan=4>Hit Points</th></tr>"
        html_str += "<tr><th>Max:</th>"
        html_str += "<td>"+self.master_dom.getAttribute('max')+"</td>"
        html_str += "<th>Current:</th>"
        html_str += "<td>"+self.master_dom.getAttribute('current')+"</td>"
        html_str += "</tr></table>"
        return html_str

class hp_panel(wx.Panel):
    def __init__(self, parent, handler):
        wx.Panel.__init__(self, parent, -1)
        self.hparent = handler #a 1.5002 allow ability to run up tree.  In this
        #a 1.5002 case, we need the functional parent, not the invoking parent.

        pname = handler.master_dom.setAttribute("name", 'HitPoints')
        self.sizer = wx.FlexGridSizer(2, 4, 2, 2)  # rows, cols, hgap, vgap
        self.master_dom = handler.master_dom
        self.sizer.AddMany([ (wx.StaticText(self, -1, "HP Current:"),   0,
           wx.ALIGN_CENTER_VERTICAL),
          (wx.TextCtrl(self, HP_CUR,
           self.master_dom.getAttribute('current')),   0, wx.EXPAND),
          (wx.StaticText(self, -1, "HP Max:"), 0, wx.ALIGN_CENTER_VERTICAL),
          (wx.TextCtrl(self, HP_MAX, self.master_dom.getAttribute('max')),
           0, wx.EXPAND),
         ])
        self.sizer.AddGrowableCol(1)
        self.SetSizer(self.sizer)
        self.SetAutoLayout(True)
        self.Fit()

        #self.Bind(wx.EVT_SIZE, self.on_size)
        self.Bind(wx.EVT_TEXT, self.on_text, id=HP_MAX)
        self.Bind(wx.EVT_TEXT, self.on_text, id=HP_CUR)

    def on_text(self,evt):
        id = evt.GetId()
        if id == HP_CUR:
            self.master_dom.setAttribute('current',evt.GetString())
        elif id == HP_MAX:
            self.master_dom.setAttribute('max',evt.GetString())

    def on_size(self,evt):
        s = self.GetClientSizeTuple()
        self.sizer.SetDimension(0,0,s[0],s[1])

class dnd3eattacks(combat_char_child):
    """ Node Handler for attacks.  This handler will be
        created by dnd3echar_handler.
    """
    def __init__(self,xml_dom,tree_node,parent):
        combat_char_child.__init__(self,xml_dom,tree_node,parent)
        self.hparent = parent #a 1.5002 allow ability to run up tree.
        self.root = getRoot(self) #a 1.5002
        self.root.attacks = self #a 1.6009 so others can find me.
        self.mrFrame = [] #a 1.9001

        #a 1.5012 start a1b

        self.updateFootNotes = False
        self.updateFootNotes = False
        self.html_str = "<html><body>"
        self.html_str += ("<br>  This character has weapons with no "+
             "footnotes.  This program will "+
             "add footnotes to the weapons which have names that still match "+
             "the orginal names.  If you have changed the weapon name, you "+
             "will see some weapons with a footnote of 'X', you will have "+
             "to either delete and re-add the weapon, or research "+
             "and add the correct footnotes for the weapon.\n"+
             "<br>  Please be aware, that only the bow/sling footnote is "+
             "being used to affect changes to rolls; implemenation of other "+
             "footnotes to automaticly adjust rolls will be completed as "+
             "soon as time allows." +
             "<br><br>Update to character:"+self.root.general.charName+
             "<br><br>"+
             """<table border='1' width=100% ><tr BGCOLOR=#E9E9E9 >
              <th width='80%'>Weapon Name</th><th>Added Footnote</th></tr>\n""")
        self.temp_dom={}
        #a 1.5012 end a1b

        node_list = self.master_dom.getElementsByTagName('melee')
        self.melee = node_list[0]
        node_list = self.master_dom.getElementsByTagName('ranged')
        self.ranged = node_list[0]
        self.refresh_weapons() # this causes self.weapons to be loaded.

        #a 1.5012 this whole if clause.
        if self.updateFootNotes == True:
            self.updateFootNotes = False
            name = self.root.general.charName
            self.html_str +=  "</table>"
            self.html_str +=  "</body> </html> "
            masterFrame = self.root.frame

            title = name+"'s weapons' update to have footnotes"
            fnFrame = wx.Frame(masterFrame, -1, title)
            fnFrame.panel = wx.html.HtmlWindow(fnFrame,-1)
            fnFrame.panel.SetPage(self.html_str)
            fnFrame.Show()

        #weaponsH = self.master_dom.getElementsByTagName('attacks')
        #mark7

    #a 1.9001 this whole method
    def refreshMRdata(self): # refresh the data in the melee/ranged section
        # of the attack chart.
        # count backwards, maintains context despite "removes"
        for i in range(len(self.mrFrame)-1,-1,-1):   #a 1.9001
            x = self.mrFrame[i]
            if x == None:
                x.refreshMRdata() #a 1.9001
            else:
                self.mrFrame.remove(x)

    def refresh_weapons(self):
        self.weapons = {}

        tree = self.tree
        icons = self.tree.icons
        tree.CollapseAndReset(self.mytree_node)
        node_list = self.master_dom.getElementsByTagName('weapon')
        for n in node_list:
            name = n.getAttribute('name')
            fn = safeGetAttr(n,'fn') #a 1.5012 can be removed when
            #a 1.5012 confident all characters in the world have footnotes.
            #if self.updateFootNotes:
            if fn == None:#a 1.5012
                self.updateFootNotes=True
                self.updateFootN(n) #a 1.5012
            new_tree_node = tree.AppendItem(
                self.mytree_node,name,icons['sword'],icons['sword'])
            tree.SetPyData(new_tree_node,self)
            self.weapons[name]=n

    def updateFootN(self,n):#a 1.5012 this whole function
        if not self.temp_dom:
            tmp = open(orpg.dirpath.dir_struct["dnd3e"]+"dnd3eweapons.xml","r")
            #tmp = open("c:\clh\codeSamples\sample1.xml","r") #a (debug) 1.5012
            self.temp_dom = xml.dom.minidom.parse(tmp)

            #self.temp_dom = parseXml_with_dlg(self,tmp.read())
            self.temp_dom = self.temp_dom._get_firstChild()
            tmp.close()
        nameF = n.getAttribute('name')
        w_list = self.temp_dom.getElementsByTagName('weapon')
        found = False
        for w in w_list:
            if nameF == w.getAttribute('name'):
                found = True
                fnN = safeGetAttr(n,'fn')
                if fnN == None or fnN == 'None':
                    fnW = w.getAttribute('fn')
                    #print "weapon",nameF,"footnotes are updated to",fnW
                    self.html_str += ("<tr ALIGN='center'><td>"+nameF+"</td>"+
                                     "<td>"+fnW+"</td></tr>\n")
                    n.setAttribute('fn',fnW)
                break
        if not found:
            self.html_str += ("<tr ALIGN='center'><td>"+nameF+" - Custom "+
              "Weapon, research "+
              "and update manually; setting footnote to indicate custom</td>"+
                                     "<td>"+'X'+"</td></tr>\n")
            n.setAttribute('fn','X')


    def get_mod(self,type='m'):
        (base, base2, base3, base4, base5, base6, stat_mod, misc) \
            = self.get_attack_data(type)
        return int(base + misc + int(stat_mod))

    def get_attack_data(self,type='m'):
        if type=='m' or type=='0':
            stat = 'Str'  #m was dnd_globals["stats"]['Str'] 1.5002
            temp = self.melee
        else:
            stat = 'Dex'  #m was dnd_globals["stats"]['Dex'] 1.5002
            temp = self.ranged
        stat_mod = -7
        stat_mod = self.root.abilities.get_mod(stat)    #a 1.5002
        #print "Big test - stat_mod",stat_mod           #a (debug) 1.6000
        base = int(temp.getAttribute('base'))
        base2 = int(temp.getAttribute('second'))
        base3 = int(temp.getAttribute('third'))
        base4 = int(temp.getAttribute('forth'))
        base5 = int(temp.getAttribute('fifth'))
        base6 = int(temp.getAttribute('sixth'))
        misc = int(temp.getAttribute('misc'))
        return (base, base2, base3, base4, base5, base6, stat_mod ,misc)

    def on_rclick(self,evt):
        item = self.tree.GetSelection()

        name = self.tree.GetItemText(item)
        if item == self.mytree_node:
            #print "bail due to FUD"
            return #a 1.6015
            #dnd3e_char_child.on_ldclick(self,evt)#d 1.6015
            #self.frame.add_panel(self.get_design_panel(self.frame.note))
        else:
            #print "entering attack phase"
            mod = int(self.weapons[name].getAttribute('mod'))
            wepMod = mod #a 1.5008
            footNotes = safeGetAttr(self.weapons[name],'fn','')
            cat = self.weapons[name].getAttribute('category') #a1.6001
            result = split(cat,"-",2) #a 1.6001
            if len(result) < 2: #a 1.6021 this if & else
                print "warning: 1.6002 unable to interpret weapon category"
                print "format 'type weapon-[Range|Melee]', probably missing"
                print "the hyphen.  Assuming Melee"
                print "weapon name: ",name
                tres="Melee"
            else:
                tres=result[1]
            #print "print FootNotes,tres",footNotes,tres
            if tres == 'Melee': #a 1.6001   #m 1.6022 use of tres here and...
            #if self.weapons[name].getAttribute('range') == '0':#d 1.6001
                rangeOrMelee = 'm' #a 1.5008 code demote for next comment block
            elif tres == 'Ranged': #m 1.6001 (was just else) #m 1.6022 here
                rangeOrMelee = 'r' #a 1.5008
            else:#a 1.6001 add this whole else clause.
                print "warning: 1.6001 unable to interpret weapon category"
                print "treating weapon as Melee, please correct xml"
                print "weapon name:",name
                rangeOrMelee ='m'
            mod = mod + self.get_mod(rangeOrMelee) #a 1.5008
            chat = self.chat
            dmg = self.weapons[name].getAttribute('damage')

            #a 1.6003 start code fix instance a
            result = split(dmg,"/",2)
            dmg = result[0]
            #print "1.6003 check:dmg",dmg,";result",result
            #o currently, only picking out dmg; rest are simply ignored.
            #o May be usefull
            #o later for two weapon attack correction.
            #a 1.6003 end code fix instance a

            monkLvl = self.root.classes.get_class_lvl('Monk') # a 1.5002
            #print "monkLvl",monkLvl #a (debug) 1.5002
            # monkLvl = dnd_globals["class"]["lvl"] #d 1.5002
            if dmg == "Monk Med":
                if monkLvl == None:     #a 1.5009
                    txt = 'Attempting to use monk attack, but has no monk '
                    txt += 'levels, please choose a different attack.'
                    chat.ParsePost( txt, True, True ) #a 1.5009
                    return #a 1.5009
                else:   #a 1.5009
                    lvl=int(monkLvl)
                    if lvl <= 3:     #m 1.6022 reversed the order of checks.
                        dmg = "1d6"
                    elif lvl <= 7:
                        dmg = "1d8"
                    elif lvl <= 11:
                        dmg = "1d10"
                    elif lvl <= 15:
                        dmg = "2d6"
                    elif lvl <= 19:
                        dmg = "2d8"
                    elif lvl <= 20:
                        dmg = "2d10"
            if dmg == "Monk Small":
                if monkLvl == None:     #a 1.5009
                    txt = 'Attempting to use monk attack, but has no monk '
                    txt += 'levels, please choose a different attack.'
                    chat.ParsePost( txt, True, True ) #a 1.5009
                    return #a 1.5009
                else:   #a 1.5009
                    lvl=int(monkLvl)
                    if lvl <= 3:     #m 1.6022 reversed the order of the checks
                        dmg = "1d4"
                    elif lvl <= 7:
                        dmg = "1d6"
                    elif lvl <= 11:
                        dmg = "1d8"
                    elif lvl <= 15:
                        dmg = "1d10"
                    elif lvl <= 20:
                        dmg = "2d6"
            flu = ''
            #print "adjusted weapon damage is:",dmg
            #o 1.5007 str bow
            #o 1.5011 start looking about here str dam bonus missed for thrown?
            #o 1.5012 start looking about here str penalty missed for bow/sling?
            #o 1.5013 off-hand attacks.? dam and all affects?
            str_mod = self.root.abilities.get_mod('Str') #a 1.5007,11,12,13
            if rangeOrMelee == 'r':                     #a 1.5008
                #if off_hand == True then stat_mod = stat_mod/2 #o 1.5013
                #c 1.5007 ranged weapons normally get no str mod
                if find(footNotes,'b') > -1:#a 1.5012 if it's a bow
                    if str_mod >= 0:        #a 1.5012 never a str bonus
                        str_mod = 0         #a 1.5012 penalty,
                else:                       #a 1.5012 if appropriate
                    str_mod = 0
                #  c 1.5007 (must adjust for str bows later and thown weapons)
                #o 1.5007 include + for str bows
                #o 1.5012 include any str penalty for bows/slings.
            mod2 = ""                                   #a 1.5007,11-13
            if str_mod >= 0: #1.6 tidy up code.
                mod2 = "+"   #1.6 tidy up code.
            aStrengthMod = mod2 + str(str_mod) #a 1.5008 applicable strength mod

            #if name == "Flurry of Blows(Monk Med)": #d 1.6012
            if find(name ,"Flurry of Blows") > -1: #a 1.6012
                flu = '-2'

            (base, base2, base3, base4, base5, base6, stat_mod, misc)\
                = self.get_attack_data(rangeOrMelee)  #a 1.5008
            self.sendRoll(base ,stat_mod,misc,wepMod,name,flu,dmg,
                aStrengthMod,'',True,rollAnyWay=True)
            if flu != '':
                self.sendRoll(base ,stat_mod,misc,wepMod,name,flu,dmg,
                    aStrengthMod) #a 1.6021

            self.sendRoll(base2,stat_mod,misc,wepMod,name,flu,dmg,aStrengthMod)
            self.sendRoll(base3,stat_mod,misc,wepMod,name,flu,dmg,aStrengthMod)
            self.sendRoll(base4,stat_mod,misc,wepMod,name,flu,dmg,aStrengthMod)
            self.sendRoll(base5,stat_mod,misc,wepMod,name,flu,dmg,aStrengthMod)
            self.sendRoll(base6,stat_mod,misc,wepMod,name,flu,dmg,aStrengthMod)


    def sendRoll(self,base,stat_mod,misc,wepMod,name,flu,dmg,aStrengthMod,
        spacer="",pname=False,rollAnyWay=False):
        if base != 0 or rollAnyWay:
            base = base + int(stat_mod) + misc + wepMod #m 1.5008
            if base >= 0:
                mod1 = "+"
            else:
                mod1 = ""
            txt = '%s ' % (spacer)
            txt += '%s Attack Roll: <b>[1d20%s%s%s]</b>' % (name, mod1, base, flu)
            txt += ' ===> Damage: <b>[%s%s]</b>' % (dmg, aStrengthMod)
            self.chat.ParsePost( txt, True, True )

    def get_design_panel(self,parent):
        wnd = outline_panel(parent,self,attack_panel,"Attacks")
        wnd.title = "Attacks"
        return wnd

    def tohtml(self):
        melee = self.get_attack_data('m')
        ranged = self.get_attack_data('r')
        html_str = ("""<table width=100% border=1 ><tr BGCOLOR=#E9E9E9 >"""+
          "<th>Attack</th><th>Total</th><th >Base</th>"+
          "<th>Abil</th><th>Misc</th></tr>")
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
            html_str += """<P><table width=100% border=1 ><tr BGCOLOR=#E9E9E9 >
                    <th colspan=2>Weapon</th>
                    <th>Attack</th><th >Damage</th><th>Critical</th></tr>"""
            html_str += "<tr ALIGN='center' ><td  colspan=2>"
            html_str += n.getAttribute('name')+"</td><td>"+total+"</td>"
            html_str += "<td>"+n.getAttribute('damage')+"</td><td>"
            html_str += n.getAttribute('critical')+"</td></tr>"
            html_str += """<tr BGCOLOR=#E9E9E9 ><th>Range</th><th>Weight</th>
                        <th>Type</th><th>Size</th><th>Misc Mod</th></tr>"""
            html_str += "<tr ALIGN='center'><td>"+ran+"</td><td>"
            html_str += n.getAttribute('weight')+"</td>"
            html_str += "<td>"+n.getAttribute('type')+"</td><td>"
            html_str += n.getAttribute('size')+"</td>"
            html_str += '<td>%s%s</td></tr>'  % (mod1, mod)
            #a 1.5012 add next two lines to pretty print footnotes.
            html_str += """<tr><th BGCOLOR=#E9E9E9 colspan=2>Footnotes:</th>"""
            html_str += "<th colspan=3>"+safeGetAttr(n,'fn','')+"</th></tr>"
            html_str += '</table>'
        return html_str

class attack_grid(wx.grid.Grid):
    """grid for attacks"""
    def __init__(self, parent, handler):
        pname = handler.master_dom.setAttribute("name", 'Melee')
        self.hparent = handler #a 1.5002 allow ability to run up tree.
        #a 1.5002 we need the functional parent, not the invoking parent.

        wx.grid.Grid.__init__(self, parent, -1, style=wx.SUNKEN_BORDER | wx.WANTS_CHARS)

        self.root = getRoot(self) #a 1.9001
        self.parent = parent
        self.handler = handler
        self.rows = (self.handler.melee,self.handler.ranged)
        self.CreateGrid(2,10)
        self.SetRowLabelSize(0)
        col_names = ['Type','base','base 2','base 3','base 4','base 5',
            'base 6','abil','misc','Total']
        for i in range(len(col_names)):
            self.SetColLabelValue(i,col_names[i])
        self.SetCellValue(0,0,"Melee")
        self.SetCellValue(1,0,"Ranged")
        self.refresh_data()
        self.Bind(wx.EVT_SIZE, self.on_size)
        self.Bind(wx.grid.EVT_GRID_CELL_CHANGE, self.on_cell_change)
        #print "looking for containing frame"

        #a 1.9001 remainder of code in this method.
        climber = parent
        nameNode = climber.GetClassName()
        while nameNode != 'wxFrame':
            climber = climber.parent
            nameNode = climber.GetClassName()
        masterFrame=climber
        masterFrame.refreshMRdata=self.refresh_data
        #print getmembers(masterFrame)

        handler.mrFrame.append(masterFrame)

        #print "masterFrame=",masterFrame
        #print "mr.Show=",masterFrame.Show()
        #print "mf.GetName",masterFrame.GetName()
        #print "mf.GetClassName",masterFrame.GetClassName()
        #print "mf.GetId",masterFrame.GetId()
        #print "mf.GetLabel",masterFrame.GetLabel()
        #print "mf.GetHandle",masterFrame.GetHandle()
        #print "mf.GetParent",masterFrame.GetParent()
        # here, GetParent consistent returns the master frame of the app.
        #print "mf.GetGParent",masterFrame.GetGrandParent() #here, always None
        #print "mf.GetTitle",masterFrame.GetTitle()
        #print "mf.IsEnabled",masterFrame.IsEnabled()
        #print "mf.IsShown",masterFrame.IsShown()
        #print "mf.IsTopLevel",masterFrame.IsTopLevel()
        #print "self.frame=",self.frame


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
                #print "row:",row,"value",value,self.rows[row]
            self.parent.refresh_data()
        except:
            self.SetCellValue(row,col,"0")

    def refresh_data(self):

        melee = self.handler.get_attack_data('m')
        ranged = self.handler.get_attack_data('r')
        tmelee = int(melee[0]) + int(melee[6]) + int(melee[7])
        tranged = int(ranged[0]) + int(ranged[6]) + int(ranged[7])
        # for i in range(0,7):  #d 1.5005
        for i in range(0,8):    #a 1.5005
            self.SetCellValue(0,i+1,str(melee[i]))
            self.SetCellValue(1,i+1,str(ranged[i]))
        self.SetCellValue(0,9,str(tmelee))
        self.SetCellValue(1,9,str(tranged))
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
        self.hparent = handler                          #a 1.5012
        self.root = getRoot(self)

        pname = handler.master_dom.setAttribute("name", 'Weapons')

        wx.Panel.__init__(self, parent, -1)
        self.grid =wx.grid.Grid(self, -1, style=wx.SUNKEN_BORDER | wx.WANTS_CHARS)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.grid, 1, wx.EXPAND)

        sizer2 = wx.BoxSizer(wx.HORIZONTAL)
        sizer2.Add(wx.Button(self, 10, "Remove Weapon"), 0, wx.EXPAND)
        sizer2.Add(wx.Size(10,10))
        sizer2.Add(wx.Button(self, 20, "Add Weapon"), 0, wx.EXPAND)

        sizer.Add(sizer2, 0, wx.EXPAND)
        sizer.Add(wx.StaticText(self, -1, "Right click a weapon's footnote to see what the footnotes mean."),0, wx.EXPAND)#a 1.5012
        self.sizer = sizer
        self.SetSizer(self.sizer)
        self.SetAutoLayout(True)
        self.Fit()

        self.sizer2 = sizer2
        #self.Bind(wx.EVT_SIZE, self.on_size)
        self.Bind(wx.EVT_BUTTON, self.on_remove, id=10)
        self.Bind(wx.EVT_BUTTON, self.on_add, id=20)
        self.grid.Bind(wx.grid.EVT_GRID_CELL_CHANGE, self.on_cell_change)
        self.grid.Bind(wx.grid.EVT_GRID_CELL_RIGHT_CLICK, self.on_gridRclick)#a 1.5012

        n_list = handler.master_dom.getElementsByTagName('weapon')
        self.n_list = n_list
        self.master_dom = handler.master_dom
        self.handler = handler
        #trash=input("weapon panel init colnames")
        self.colAttr = ['name','damage','mod','critical','type','weight',
                    'range','size','Total','fn',    'comment'] #a 1.5012
        col_names = ['Name','Damage','To hit\nmod','Critical','Type','Weight',
                    'Range','Size','Total','Foot\nnotes','Comment'] #a 1.5012
        gridColCount=len(col_names)#a 1.5012
        self.grid.CreateGrid(len(n_list),gridColCount,1) #a 1.5012
        #self.grid.CreateGrid(len(n_list),9,1) #d 1.5012
        self.grid.SetRowLabelSize(0)
        #col_names = ['Name','damage','mod','critical','type','weight','range',             'size','Total'] #d 1.5012
        #for i in range(len(col_names)):   #d 1.5012
        for i in range(gridColCount): #a 1.5012
            self.grid.SetColLabelValue(i,col_names[i])
        self.refresh_data()
        self.temp_dom = None


    #mark4
    #a 1.5012 add entire method.
    def on_gridRclick(self,evt):
        #print "weapon_panel, on_rclick: self,evt",self,evt
        row = evt.GetRow()
        col = evt.GetCol()
        value = self.grid.GetCellValue(row,col)
        #print "wp, on rclick,grid row,col,value",row,col,value
        if col == 9 and value != 'None':
            n = self.n_list[row]
            name = n.getAttribute('name')
            #print "we want a panel!"
            handler = self.hparent
            #print "handler:",handler
            # A handler is a node, and nodes have a reference to
            # the master frame
            masterFrame = handler.frame
            #print "masterFrame:",masterFrame
            title = name+"'s Special Weapon Characteristics"
            fnFrame = wx.Frame(masterFrame, -1, title)
            fnFrame.panel = wx.html.HtmlWindow(fnFrame,-1)
            if not self.temp_dom:
                tmp = open(orpg.dirpath.dir_struct["dnd3e"]+
                            "dnd3eweapons.xml","r")
                #tmp = open("c:\clh\codeSamples\sample1.xml","r")
                xml_dom = parseXml_with_dlg(self,tmp.read())
                xml_dom = xml_dom._get_firstChild()
                tmp.close()
                self.temp_dom = xml_dom
            f_list = self.temp_dom.getElementsByTagName('f') # the footnotes
            #print "weapon_panel - on_rclick f_list",f_list#a 1.6
            n = self.n_list[row]
            name = n.getAttribute('name')
            footnotes = n.getAttribute('fn')
            html_str = "<html><body>"
            html_str += """<table border='1' width=100% ><tr BGCOLOR=#E9E9E9 >
                        <th width='10%'>Note</th><th>Description</th></tr>\n"""
            #print "rclick,name,fn",name,footnotes
            if footnotes == "":
                html_str += "<tr ALIGN='center'><td></td>"
                html_str += "  <td>This weapon has no footnotes</td></tr>"
            for i in range(len(footnotes)):
                aNote=footnotes[i]
                found=False
                for f in f_list:
                    if f.getAttribute('mark') == aNote:
                        found=True
                        text=f.getAttribute('txt')
                        html_str += ("<tr ALIGN='center'><td>"+aNote+"</td>"+
                                     "<td>"+text+"</td></tr>\n")
                if not found:
                    html_str += ("<tr ALIGN='center'><td>"+aNote+"</td>"+
                       "<td>is not a recognized footnote</td></tr>\n")

            html_str +=  "</table>"
            html_str +=  "</body> </html> "

            #print html_str
            fnFrame.panel.SetPage(html_str)
            fnFrame.Show()
            return
        pass



    def on_cell_change(self,evt):
        row = evt.GetRow()
        col = evt.GetCol()
        value = self.grid.GetCellValue(row,col)
        if col == 2 and not int(value): # special case for mod, demoted
            value = "0" #a 5.012 demoted
            self.n_list[row].setAttribute('mod',value) # a 5.012 demoted
        if not (col == 9 and value == "None" and
                self.n_list[row].getAttribute('fn') == "None"
                ): #a 5.012 special case for footnotes
            self.n_list[row].setAttribute(self.colAttr[col],value)#a 5.012
        #print "cell change",row,col,value
        #if col == 0:#d 5.012 use of colAttr removed need for this.
        #    self.n_list[row].setAttribute('name',value) #d 5.012
        #elif col == 2: #d 5.012
        #    try:#d 5.012 simplifying... remove this block.
        #        int(value)
        #        self.n_list[row].setAttribute('mod',value)
        #        #self.refresh_row(row) #d 5.012 did nothing.
        #    except:
        #       value = "0"
        #       self.n_list[row].setAttribute('mod',value)
        #else: #d 5.012 demoted self.n set.
        #   self.n_list[row].setAttribute(self.grid.GetColLabelValue(col),value)


    def refresh_row(self,i):
        n = self.n_list[i]
        fn = n.getAttribute('fn')
        #print "fn=",fn
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
        self.grid.SetCellValue(i,9,safeGetAttr(n,'fn','None')) #a 1.5012
        self.grid.SetCellValue(i,10,safeGetAttr(n,'comment','')) #a 1.5012
        #fn=safeGetAttr(n,'fn','None') #a (debug) 1.5012
        #print "fn ",fn,"<" #a (debug) 1.5012
        #o 1.5012 original damage vs what someone has changed it to.

        self.grid.SetReadOnly(i,8)

    def on_remove(self,evt): #o 1.6011 correcting wrongful deletion
        rows = self.grid.GetNumberRows()
        #for i in range(rows):          #d 1.6011 do it backwards,
        for i in range(rows-1,-1,-1):   #a 1.6011 or you lose context
            if self.grid.IsInSelection(i,0):
                self.grid.DeleteRows(i)
                self.master_dom.removeChild(self.n_list[i])
                self.n_list = self.master_dom.getElementsByTagName('weapon')
                self.handler.refresh_weapons()

    def on_add(self,evt):
        if not self.temp_dom:
            tmp = open(orpg.dirpath.dir_struct["dnd3e"]+"dnd3eweapons.xml","r")
            #tmp = open("c:\clh\codeSamples\sample1.xml","r") #a (debug) 1.5012
            xml_dom = parseXml_with_dlg(self,tmp.read())
            xml_dom = xml_dom._get_firstChild()
            tmp.close()
            self.temp_dom = xml_dom
        f_list = self.temp_dom.getElementsByTagName('weapon')
        opts = []
        #print "weapon_panel - on_add f_list",f_list#a 1.6
        for f in f_list:
            opts.append(f.getAttribute('name'))
        dlg = wx.SingleChoiceDialog(self,'Choose Weapon','Weapon List',opts)
        if dlg.ShowModal() == wx.ID_OK:
            i = dlg.GetSelection()
            #print f_list[i] # DOM Element: weapon.
            new_node = self.master_dom.appendChild(f_list[i].cloneNode(False))
            #print self.grid.AppendRows # a bound method of wxGrid
            self.grid.AppendRows(1)
            self.n_list = self.master_dom.getElementsByTagName('weapon')
            #print "self.n_list",self.n_list # list of DOM weapons
            self.refresh_row(self.grid.GetNumberRows()-1)
            self.handler.refresh_weapons()
        dlg.Destroy()

    def on_size(self,event):
        s = self.GetClientSizeTuple()
        self.grid.SetDimensions(0,0,s[0],s[1]-40)
        self.sizer.SetDimension(0,s[1]-40,s[0],25)
        self.sizer2.SetDimension(0,s[1]-15,s[0],15)
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
        self.parent = parent #a 1.9001

        wx.Panel.__init__(self, parent, -1)

        self.a_grid = attack_grid(self, handler)
        self.w_panel = weapon_panel(self, handler)
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.a_grid, 1, wx.EXPAND)
        self.sizer.Add(self.w_panel, 2, wx.EXPAND)
        self.Bind(wx.EVT_SIZE, self.on_size)


    def on_size(self,event):
        s = self.GetClientSizeTuple()
        self.sizer.SetDimension(0,0,s[0],s[1])

    def refresh_data(self):

        self.w_panel.refresh_data()
        self.a_grid.refresh_data()


class dnd3earmor(combat_char_child):
    """ Node Handler for ac.  This handler will be
        created by dnd3echar_handler.
    """
    def __init__(self,xml_dom,tree_node,parent):
        combat_char_child.__init__(self,xml_dom,tree_node,parent)
        self.hparent = parent #a 1.5002 allow ability to run up tree.
        self.root = getRoot(self) #a 1.5002
        self.root.ac = self #a 1.6009

    def get_spell_failure(self):
        return self.get_total('spellfailure')

    def get_total_weight(self):
        return self.get_total('weight')

    def get_check_pen(self):
        return self.get_total('checkpenalty')

    def get_armor_class(self):
        ac_total = 10

        ac_total += self.get_total('bonus')
        #m 1.5009 change to hardcode dex, was incorrect gv "stat"
        dex_mod = self.root.abilities.get_mod('Dex')#m 1.5009 hardcode dex
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

    def on_rclick( self, evt ):
        ac = self.get_armor_class()
        fac = (int(ac)-(self.root.abilities.get_mod('Dex')))

        txt = '((AC: %s Normal, %s Flatfoot))' % ( ac, fac ) #a 1.5002
        self.chat.ParsePost( txt, True, True )

    def tohtml(self):
        html_str = """<table width=100% border=1 ><tr BGCOLOR=#E9E9E9 >
            <th>AC</th><th>Check Penalty</th><th >Spell Failure</th>
            <th>Max Dex</th><th>Total Weight</th></tr>"""
        html_str += "<tr ALIGN='center' >"
        html_str += "<td>"+str(self.get_armor_class())+"</td>"
        html_str += "<td>"+str(self.get_check_pen())+"</td>"
        html_str += "<td>"+str(self.get_spell_failure())+"</td>"
        html_str += "<td>"+str(self.get_max_dex())+"</td>"
        html_str += "<td>"+str(self.get_total_weight())+"</td></tr></table>"
        n_list = self.master_dom._get_childNodes()
        for n in n_list:
            html_str += """<P><table width=100% border=1 ><tr BGCOLOR=#E9E9E9 >
                <th colspan=3>Armor</th><th>Type</th><th >Bonus</th></tr>"""
            html_str += "<tr ALIGN='center' >"
            html_str += "<td  colspan=3>"+n.getAttribute('name')+"</td>"
            html_str += "<td>"+n.getAttribute('type')+"</td>"
            html_str += "<td>"+n.getAttribute('bonus')+"</td></tr>"
            html_str += """<tr BGCOLOR=#E9E9E9 >"""
            html_str += "<th>Check Penalty</th><th>Spell Failure</th>"
            html_str += "<th>Max Dex</th><th>Speed</th><th>Weight</th></tr>"
            html_str += "<tr ALIGN='center'>"
            html_str += "<td>"+n.getAttribute('checkpenalty')+"</td>"
            html_str += "<td>"+n.getAttribute('spellfailure')+"</td>"
            html_str += "<td>"+n.getAttribute('maxdex')+"</td>"
            html_str += "<td>"+n.getAttribute('speed')+"</td>"
            html_str += "<td>"+n.getAttribute('weight')+"</td></tr></table>"
        return html_str


class ac_panel(wx.Panel):
    def __init__(self, parent, handler):
        pname = handler.master_dom.setAttribute("name", 'Armor')
        self.hparent = handler #a 1.5002 allow ability to run up tree.
        #a 1.5002 we need the functional parent, not the invoking parent.

        wx.Panel.__init__(self, parent, -1)
        self.grid =wx.grid.Grid(self, -1, style=wx.SUNKEN_BORDER | wx.WANTS_CHARS)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.grid, 1, wx.EXPAND)

        sizer1 = wx.BoxSizer(wx.HORIZONTAL)
        sizer1.Add(wx.Button(self, 10, "Remove Armor"), 1, wx.EXPAND)
        sizer1.Add(wx.Size(10,10))
        sizer1.Add(wx.Button(self, 20, "Add Armor"), 1, wx.EXPAND)

        sizer.Add(sizer1, 0, wx.EXPAND)

        self.sizer = sizer
        self.SetSizer(self.sizer)
        self.SetAutoLayout(True)
        self.Fit()

        #self.Bind(wx.EVT_SIZE, self.on_size)
        self.Bind(wx.EVT_BUTTON, self.on_remove, id=10)
        self.Bind(wx.EVT_BUTTON, self.on_add, id=20)
        self.grid.Bind(wx.grid.EVT_GRID_CELL_CHANGE, self.on_cell_change)
        self.master_dom = handler.master_dom
        n_list = handler.master_dom._get_childNodes()
        self.n_list = n_list
        col_names = ['Armor','bonus','maxdex','cp','sf','weight','speed','type']
        self.grid.CreateGrid(len(n_list),len(col_names),1)
        self.grid.SetRowLabelSize(0)
        for i in range(len(col_names)):
            self.grid.SetColLabelValue(i,col_names[i])
        self.atts =['name','bonus','maxdex','checkpenalty',
            'spellfailure','weight','speed','type']
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
            tmp = open(orpg.dirpath.dir_struct["dnd3e"]+"dnd3earmor.xml","r")
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


class dnd3esnp(dnd3e_char_child):
    """ Node Handler for power points.  This handler will be
        created by dnd3echar_handler.
    """
    def __init__(self,xml_dom,tree_node,parent):
        node_handler.__init__(self,xml_dom,tree_node)
        dnd3e_char_child.__init__(self,xml_dom,tree_node,parent)
        self.hparent = parent #a 1.5002 allow ability to run up tree.


        self.frame = open_rpg.get_component('frame')
        self.child_handlers = {}
        self.new_child_handler('spells','Spells',dnd3espells,'book')
        self.new_child_handler('divine','Divine Spells',dnd3edivine,'book')
        self.new_child_handler('powers','Powers',dnd3epowers,'book')
        self.new_child_handler('pp','Power Points',dnd3epp,'gear')
        self.myeditor = None

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

#    def set_char_pp(self,attr,evl):     #d 1.5002 doesn't seem to be used, but
#        dnd_globals["pp"][attr] = evl  #d 1.5002 uses dnd_globals, so tossing.


#    def get_char_pp( self, attr ):     #d 1.5002 doesn't seem to be used, but
#        return dnd_globals["pp"][attr]     #d 1.5002 doesn't seem to be used, but

class snp_char_child(node_handler):
    """ Node Handler for skill.  This handler will be
        created by dnd3echar_handler.
    """
    def __init__(self,xml_dom,tree_node,parent):
        node_handler.__init__(self,xml_dom,tree_node)
        self.char_hander = parent
        self.drag = False
        self.frame = open_rpg.get_component('frame')
        self.myeditor = None



    def on_drop(self,evt):
        pass

    def on_rclick(self,evt):
        pass

    def on_ldclick(self,evt):
        return

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


class dnd3espells(snp_char_child):
    """ Node Handler for classes.  This handler will be
        created by dnd3echar_handler.
    """
    def __init__(self,xml_dom,tree_node,parent):
        snp_char_child.__init__(self,xml_dom,tree_node,parent)
        self.hparent = parent #a 1.5002 allow ability to run up tree.
        self.root = getRoot(self) #a 1.5002
        self.root.spells = self #a 1.6009


        node_list = self.master_dom.getElementsByTagName( 'spell' )
        self.spells = {}
        tree = self.tree
        icons = self.tree.icons
        for n in node_list:
            name = n.getAttribute('name')
            self.spells[ name ] = n
            new_tree_node = tree.AppendItem( self.mytree_node, name, icons['gear'], icons['gear'] )
            tree.SetPyData( new_tree_node, self )

    def on_rclick( self, evt ):
        item = self.tree.GetSelection()
        name = self.tree.GetItemText( item )
        if item == self.mytree_node:
            dnd3e_char_child.on_ldclick( self, evt )
        else:
            level = self.spells[ name ].getAttribute( 'level' )
            descr = self.spells[ name ].getAttribute( 'desc' )
            use = self.spells[ name ].getAttribute( 'used' )
            memrz = self.spells[ name ].getAttribute( 'memrz' )
            use += '+1'
            charNameL=self.root.general.charName #a  1.5002
            left = eval( '%s - ( %s )' % ( memrz, use ) )
            if left < 0:
                txt = '%s Tried to cast %s but has used all of them for today,'
                #txt +='"Please rest so I can cast more."' % ( dnd_globals["gen"]["Name"], name )##d 1.5002
                txt +='"Please rest so I can cast more."' % ( charNameL, name ) #a 1.5002
                self.chat.ParsePost( txt, True, False )
            else:
                #txt = '%s casts %s ( level %s, "%s" )' % ( dnd_globals["gen"]["Name"], name, level, descr )#d 1.5002
                txt = '%s casts %s ( level %s, "%s" )' % ( charNameL, name, level, descr )#a f 1.5002
                self.chat.ParsePost( txt, True, False )
                s = ''
                if left != 1:
                    s = 's'
                #txt = '%s can cast %s %d more time%s' % ( dnd_globals["gen"]["Name"], name, left, s )#d 1.5002
                txt = '%s can cast %s %d more time%s' % ( charNameL, name, left, s ) #a 1.5002
                self.chat.ParsePost( txt, False, False )
                self.spells[ name ].setAttribute( 'used', `eval( use )` )

    def refresh_spells(self):
        self.spells = {}
        tree = self.tree
        icons = self.tree.icons
        tree.CollapseAndReset(self.mytree_node)
        node_list = self.master_dom.getElementsByTagName('spell')
        for n in node_list:
            name = n.getAttribute('name')
            new_tree_node = tree.AppendItem(self.mytree_node,name,icons['gear'],icons['gear'])
            tree.SetPyData(new_tree_node,self)
            self.spells[name]=n

    def get_design_panel(self,parent):
        wnd = outline_panel(parent,self,spells_panel,"Spells")
        wnd.title = "Spells"
        return wnd

    def tohtml(self):
        html_str = "<table width=100% border=1 ><tr BGCOLOR=#E9E9E9 ><th>Arcane Spells</th></tr><tr><td><br>"
        n_list = self.master_dom._get_childNodes()
        for n in n_list:
            html_str += "(" + n.getAttribute('level') + ") " + n.getAttribute('name')+ ", "
        html_str = html_str[:len(html_str)-2] + "</td></tr></table>"
        return html_str

    def get_char_lvl( self, attr ):
        return self.char_hander.get_char_lvl(attr)

class spells_panel(wx.Panel):
    def __init__(self, parent, handler):
        pname = handler.master_dom.setAttribute("name", 'Arcane Spells')
        self.hparent = handler #a 1.5002 allow ability to run up tree.
        #a 1.5002 in this case, we need the functional parent, not the invoking parent.

        wx.Panel.__init__(self, parent, -1)
        self.grid =wx.grid.Grid(self, -1, style=wx.SUNKEN_BORDER | wx.WANTS_CHARS)
        self.handler = handler
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.grid, 1, wx.EXPAND)

        sizer1 = wx.BoxSizer(wx.HORIZONTAL)
        sizer1.Add(wx.Button(self, 10, "Remove Spell"), 1, wx.EXPAND)
        sizer1.Add(wx.Size(10,10))
        sizer1.Add(wx.Button(self, 20, "Add Spell"), 1, wx.EXPAND)
        sizer1.Add(wx.Size(10,10))
        sizer1.Add(wx.Button(self, 30, "Refresh Spells"), 1, wx.EXPAND)

        sizer.Add(sizer1, 0, wx.EXPAND)
        self.sizer = sizer
        self.SetSizer(self.sizer)
        self.SetAutoLayout(True)
        self.Fit()

        #self.Bind(wx.EVT_SIZE, self.on_size)
        self.Bind(wx.EVT_BUTTON, self.on_remove, id=10)
        self.Bind(wx.EVT_BUTTON, self.on_add, id=20)
        self.Bind(wx.EVT_BUTTON, self.on_refresh_spells, id=30)
        self.grid.Bind(wx.grid.EVT_GRID_CELL_CHANGE, self.on_cell_change)
        n_list = handler.master_dom._get_childNodes()
        self.n_list = n_list
        self.master_dom = handler.master_dom
        self.grid.CreateGrid(len(n_list),4,1)
        self.grid.SetRowLabelSize(0)
        self.grid.SetColLabelValue(0,"No.")
        self.grid.SetColLabelValue(1,"Lvl")
        self.grid.SetColLabelValue(2,"Spell")
        self.grid.SetColLabelValue(3,"Desc")
        for i in range(len(n_list)):
            self.refresh_row(i)
        self.temp_dom = None

    def on_cell_change(self,evt):
        row = evt.GetRow()
        col = evt.GetCol()
        value = self.grid.GetCellValue(row,col)
        if col == 0:
            self.n_list[row].setAttribute('memrz',value)


    def refresh_row(self,i):
        spell = self.n_list[i]

        memrz = spell.getAttribute('memrz')
        name = spell.getAttribute('name')
        type = spell.getAttribute('desc')
        level = spell.getAttribute('level')
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
                self.master_dom.removeChild(self.n_list[i])

    def on_add(self,evt):

        if not self.temp_dom:
            tmp = open(orpg.dirpath.dir_struct["dnd3e"]+"dnd3espells.xml","r")
            xml_dom = parseXml_with_dlg(self,tmp.read())
            xml_dom = xml_dom._get_firstChild()
            tmp.close()
            self.temp_dom = xml_dom
        f_list = self.temp_dom.getElementsByTagName('spell')
        opts = []
        #lvl = int(dnd3e_char_child.get_char_lvl('level'))
        #castlvl = eval('%s/2' % (lvl))
        for f in f_list:
            spelllvl = f.getAttribute('level')
            #if spelllvl <= "1":
            #    opts.append("(" + f.getAttribute('level') + ")" + f.getAttribute('name'))
            #else:
            #    if eval('%d >= %s' %(castlvl, spelllvl)):
            opts.append("(" + f.getAttribute('level') + ")" + f.getAttribute('name'))
        dlg = wx.SingleChoiceDialog(self,'Choose Spell','Spells',opts)
        if dlg.ShowModal() == wx.ID_OK:
            i = dlg.GetSelection()
            new_node = self.master_dom.appendChild(f_list[i].cloneNode(False))
            self.grid.AppendRows(1)
            self.n_list = self.master_dom.getElementsByTagName('spell')
            self.refresh_row(self.grid.GetNumberRows()-1)
            self.handler.refresh_spells()
        dlg.Destroy()

    def on_refresh_spells( self, evt ):
        f_list = self.master_dom.getElementsByTagName('spell')

        for spell in f_list:
            spell.setAttribute( 'used', '0' )

    def on_size(self,event):
        s = self.GetClientSizeTuple()
        self.grid.SetDimensions(0,0,s[0],s[1]-25)
        self.sizer.SetDimension(0,s[1]-25,s[0],25)
        (w,h) = self.grid.GetClientSizeTuple()
        cols = self.grid.GetNumberCols()
        col_w = w/(cols)
        for i in range(0,cols):
            self.grid.SetColSize(i,col_w)
        self.grid.SetColSize(0,w * 0.10)
        self.grid.SetColSize(1,w * 0.10)
        self.grid.SetColSize(2,w * 0.30)
        self.grid.SetColSize(3,w * 0.50)

    def refresh_data(self):
        for i in range(len(self.n_list)):
            self.refresh_row(i)

class dnd3edivine(snp_char_child):
    """ Node Handler for classes.  This handler will be
        created by dnd3echar_handler.
    """
    def __init__(self,xml_dom,tree_node,parent):
        snp_char_child.__init__(self,xml_dom,tree_node,parent)
        self.hparent = parent #a 1.5002 allow ability to run up tree.
        self.root = getRoot(self) #a 1.5002
        self.root.divine = self #a 1.6009


        node_list = self.master_dom.getElementsByTagName( 'gift' )
        self.spells = {}
        tree = self.tree
        icons = self.tree.icons
        for n in node_list:
            name = n.getAttribute('name')
            self.spells[ name ] = n
            new_tree_node = tree.AppendItem( self.mytree_node, name, icons['flask'], icons['flask'] )
            tree.SetPyData( new_tree_node, self )

    def on_rclick( self, evt ):
        charNameL=self.root.general.charName #a f 1.5002
        item = self.tree.GetSelection()
        name = self.tree.GetItemText( item )
        if item == self.mytree_node:
            dnd3e_char_child.on_ldclick( self, evt )
        else:
            level = self.spells[ name ].getAttribute( 'level' )
            descr = self.spells[ name ].getAttribute( 'desc' )
            use = self.spells[ name ].getAttribute( 'used' )
            memrz = self.spells[ name ].getAttribute( 'memrz' )
            use += '+1'
            left = eval( '%s - ( %s )' % ( memrz, use ) )
            if left < 0:
                txt = '%s Tried to cast %s but has used all of them for today,' #m 1.5002 break in 2.
                txt += "Please rest so I can cast more."' % ( charNameL, name )' #a 1.5002
                #txt += "Please rest so I can cast more."' % ( dnd_globals["gen"]["Name"], name ) #d 1.5002
                self.chat.ParsePost( txt, True, False )
            else:
                #txt = '%s casts %s ( level %s, "%s" )' % ( dnd_globals["gen"]["Name"], name, level, descr ) #d 1.5002
                txt = '%s casts %s ( level %s, "%s" )' % ( charNameL, name, level, descr ) #a 5002
                self.chat.ParsePost( txt, True, False )
                s = ''
                if left != 1:
                    s = 's'
                #txt = '%s can cast %s %d more time%s' % ( dnd_globals["gen"]["Name"], name, left, s ) #d 1.5002
                txt = '%s can cast %s %d more time%s' % ( charNameL, name, left, s ) #a 1.5002
                self.chat.ParsePost( txt, False, False )
                self.spells[ name ].setAttribute( 'used', `eval( use )` )

    def refresh_spells(self):
        self.spells = {}
        tree = self.tree
        icons = self.tree.icons
        tree.CollapseAndReset(self.mytree_node)

        node_list = self.master_dom.getElementsByTagName('gift')
        for n in node_list:
            name = n.getAttribute('name')
            new_tree_node = tree.AppendItem(self.mytree_node,name,icons['flask'],icons['flask'])
            tree.SetPyData(new_tree_node,self)
            self.spells[name]=n

    def get_design_panel(self,parent):
        wnd = outline_panel(parent,self,divine_panel,"Spells")
        wnd.title = "Spells"
        return wnd

    def tohtml(self):
        html_str = "<table width=100% border=1 ><tr BGCOLOR=#E9E9E9 ><th>Divine Spells</th></tr><tr><td><br>"
        n_list = self.master_dom._get_childNodes()
        for n in n_list:
            html_str += "(" + n.getAttribute('level') + ") " + n.getAttribute('name')+ ", "
        html_str = html_str[:len(html_str)-2] + "</td></tr></table>"
        return html_str

    def get_char_lvl( self, attr ):
        return self.char_hander.get_char_lvl(attr)

class divine_panel(wx.Panel):
    def __init__(self, parent, handler):
        pname = handler.master_dom.setAttribute("name", 'Divine Spells')
        self.hparent = handler #a 1.5002 allow ability to run up tree.
        #a 1.5002 in this case, we need the functional parent, not the invoking parent.

        wx.Panel.__init__(self, parent, -1)
        self.grid =wx.grid.Grid(self, -1, style=wx.SUNKEN_BORDER | wx.WANTS_CHARS)
        self.handler = handler
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.grid, 1, wx.EXPAND)

        sizer1 = wx.BoxSizer(wx.HORIZONTAL)
        sizer1.Add(wx.Button(self, 10, "Remove Spell"), 1, wx.EXPAND)
        sizer1.Add(wx.Size(10,10))
        sizer1.Add(wx.Button(self, 20, "Add Spell"), 1, wx.EXPAND)
        sizer1.Add(wx.Size(10,10))
        sizer1.Add(wx.Button(self, 30, "Refresh Spells"), 1, wx.EXPAND)

        sizer.Add(sizer1, 0, wx.EXPAND)
        self.sizer = sizer
        self.SetSizer(self.sizer)
        self.SetAutoLayout(True)
        self.Fit()

        #self.Bind(wx.EVT_SIZE, self.on_size)
        self.Bind(wx.EVT_BUTTON, self.on_remove, id=10)
        self.Bind(wx.EVT_BUTTON, self.on_add, id=20)
        self.Bind(wx.EVT_BUTTON, self.on_refresh_spells, id=30)
        self.grid.Bind(wx.grid.EVT_GRID_CELL_CHANGE, self.on_cell_change)

        n_list = handler.master_dom._get_childNodes()
        self.n_list = n_list
        self.master_dom = handler.master_dom
        self.grid.CreateGrid(len(n_list),4,1)
        self.grid.SetRowLabelSize(0)
        self.grid.SetColLabelValue(0,"No.")
        self.grid.SetColLabelValue(1,"Lvl")
        self.grid.SetColLabelValue(2,"Spell")
        self.grid.SetColLabelValue(3,"Desc")
        for i in range(len(n_list)):
            self.refresh_row(i)
        self.temp_dom = None

    def on_cell_change(self,evt):
        row = evt.GetRow()

        col = evt.GetCol()
        value = self.grid.GetCellValue(row,col)
        if col == 0:
            self.n_list[row].setAttribute('memrz',value)


    def refresh_row(self,i):
        spell = self.n_list[i]

        memrz = spell.getAttribute('memrz')
        name = spell.getAttribute('name')
        type = spell.getAttribute('desc')
        level = spell.getAttribute('level')
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
                self.master_dom.removeChild(self.n_list[i])

    def on_add(self,evt):
        if not self.temp_dom:
            tmp = open(orpg.dirpath.dir_struct["dnd3e"]+"dnd3edivine.xml","r")

            xml_dom = parseXml_with_dlg(self,tmp.read())
            xml_dom = xml_dom._get_firstChild()
            tmp.close()
            self.temp_dom = xml_dom
        f_list = self.temp_dom.getElementsByTagName('gift')
        opts = []
        #lvl = int(dnd3e_char_child.get_char_lvl('level'))
        #castlvl = lvl / 2
        for f in f_list:
            spelllvl = f.getAttribute('level')
            #if spelllvl <= "1":
            #    opts.append("(" + f.getAttribute('level') + ")" + f.getAttribute('name'))
            #else:
            #    if eval('%d >= %s' %(castlvl, spelllvl)):
            opts.append("(" + f.getAttribute('level') + ")" + f.getAttribute('name'))
        dlg = wx.SingleChoiceDialog(self,'Choose Spell','Spells',opts)
        if dlg.ShowModal() == wx.ID_OK:
            i = dlg.GetSelection()
            new_node = self.master_dom.appendChild(f_list[i].cloneNode(False))
            self.grid.AppendRows(1)
            self.n_list = self.master_dom.getElementsByTagName('gift')
            self.refresh_row(self.grid.GetNumberRows()-1)
            self.handler.refresh_spells()
        dlg.Destroy()

    def on_refresh_spells( self, evt ):
        f_list = self.master_dom.getElementsByTagName('gift')
        for spell in f_list:
            spell.setAttribute( 'used', '0' )

    def on_size(self,event):
        s = self.GetClientSizeTuple()
        self.grid.SetDimensions(0,0,s[0],s[1]-25)
        self.sizer.SetDimension(0,s[1]-25,s[0],25)
        (w,h) = self.grid.GetClientSizeTuple()
        cols = self.grid.GetNumberCols()
        col_w = w/(cols)
        for i in range(0,cols):
            self.grid.SetColSize(i,col_w)
        self.grid.SetColSize(0,w * 0.10)
        self.grid.SetColSize(1,w * 0.10)
        self.grid.SetColSize(2,w * 0.30)
        self.grid.SetColSize(3,w * 0.50)

    def refresh_data(self):

        for i in range(len(self.n_list)):
            self.refresh_row(i)


class dnd3epowers(snp_char_child):
    """ Node Handler for classes.  This handler will be
        created by dnd3echar_handler.
    """
    def __init__(self,xml_dom,tree_node,parent):
        snp_char_child.__init__(self,xml_dom,tree_node,parent)
        self.hparent = parent #a 1.5002 allow ability to run up tree.
        self.root = getRoot(self) #a 1.5002
        self.root.powers = self #a 1.6009

        node_list = self.master_dom.getElementsByTagName( 'power' )
        self.powers = {}
        tree = self.tree
        icons = self.tree.icons
        for n in node_list:
            name = n.getAttribute('name')
            self.powers[ name ] = n
            new_tree_node = tree.AppendItem( self.mytree_node, name,
                                             icons['gear'], icons['gear'] )
            tree.SetPyData( new_tree_node, self )

    def on_rclick( self, evt ):
        charNameL = self.root.general.charName                  #a f 1.5002

        item = self.tree.GetSelection()
        name = self.tree.GetItemText( item )
        charNameL = self.root.general.charName                  #a 1.5002
        if item == self.mytree_node:
            dnd3e_char_child.on_ldclick( self, evt )
        else:
            level = int(self.powers[ name ].getAttribute( 'level' ))
            descr = self.powers[ name ].getAttribute( 'desc' )
            #use can be removed -mgt
            #use = self.powers[ name ].getAttribute( 'used' )
            points = self.powers[ name ].getAttribute( 'point' )
            #cpp and fre are strings without the eval -mgt
            cpp = eval(self.root.pp.get_char_pp('current1'))          #a 1.5002
            fre = eval(self.root.pp.get_char_pp('free'))              #a 1.5002
            if level == 0 and fre > 0:
                left = eval('%s - ( %s )' % ( fre, points ))
                numcast = eval('%s / %s' % (left, points))
                if left < 0:
                    #In theory you should never see this -mgt
                    txt = ('%s doesnt have enough PowerPoints to use %s'
                        % ( charNameL, name )) #a 1.5002
                    self.chat.ParsePost( txt, True, False )
                else:
                    txt = ('%s uses %s as a Free Talent ( level %s, "%s" )'
                        % ( charNameL, name, level, descr )) #a 1.5002
                    self.chat.ParsePost( txt, True, False )
                    s = ''
                    if left != 1:
                        s = 's'
                    txt = '%s has %d Free Talent%s left' % ( charNameL, numcast, s ) #a 1.5002
                    self.chat.ParsePost( txt, False, False )
                    self.root.pp.set_char_pp('free',left)       #a 1.5002
            else:
                left = eval('%s - ( %s )' % ( cpp, points ))
                #numcast = eval('%s / %s' % (left, points))
                if left < 0:
                    txt = '%s doesnt have enough PowerPoints to use %s' % ( charNameL, name ) #m 1.5002
                    self.chat.ParsePost( txt, True, False )
                else:
                    txt = '%s uses %s ( level %s, "%s" )' % ( charNameL, name, level, descr ) #m 1.5002
                    self.chat.ParsePost( txt, True, False )
                    s = ''
                    if left != 1:
                        s = 's'
                    #numcast is meaningless here -mgt
                    #txt = '%s can use %s %d more time%s' % ( charNameL, name, numcast, s ) #m 1.5002
                    #txt += ' - And has %d more PowerpointsP left' % (left)
                    txt = '%s has %d more Powerpoint%s' % ( charNameL, left, s ) #m 1.5002
                    self.chat.ParsePost( txt, False, False )
                    self.root.pp.set_char_pp('current1',left)   #a 1.5002

    def refresh_powers(self):
        self.powers = {}

        tree = self.tree
        icons = self.tree.icons
        tree.CollapseAndReset(self.mytree_node)
        node_list = self.master_dom.getElementsByTagName('power')
        for n in node_list:
            name = n.getAttribute('name')
            new_tree_node = tree.AppendItem(self.mytree_node,name,icons['gear'],icons['gear'])
            tree.SetPyData(new_tree_node,self)
            self.powers[name]=n

    def get_design_panel(self,parent):
        wnd = outline_panel(parent,self,power_panel,"Powers")
        wnd.title = "Powers"
        return wnd

    def tohtml(self):
        html_str = "<table width=100% border=1 ><tr BGCOLOR=#E9E9E9 ><th>Powers</th></tr><tr><td><br>"
        n_list = self.master_dom._get_childNodes()
        for n in n_list:
            html_str += "(" + n.getAttribute('level') + ") " + n.getAttribute('name')+ ", "
        html_str = html_str[:len(html_str)-2] + "</td></tr></table>"
        return html_str


class power_panel(wx.Panel):
    def __init__(self, parent, handler):
        #m 1.5015 corrected typo, was Pionic.
        pname = handler.master_dom.setAttribute("name", 'Psionic Powers')
        self.hparent = handler #a 1.5002 allow ability to run up tree. In this
        #a 1.5002 case, we need the functional parent, not the invoking parent.
        self.root = getRoot(self)               #a (debug) 1.5002,1.5014

        wx.Panel.__init__(self, parent, -1)
        self.grid = wx.grid.Grid(self, -1, style=wx.SUNKEN_BORDER | wx.WANTS_CHARS)
        self.handler = handler
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.grid, 1, wx.EXPAND)

        sizer1 = wx.BoxSizer(wx.HORIZONTAL)
        sizer1.Add(wx.Button(self, 10, "Remove Power"), 1, wx.EXPAND)
        sizer1.Add(wx.Size(10,10))
        sizer1.Add(wx.Button(self, 20, "Add Power"), 1, wx.EXPAND)
        sizer1.Add(wx.Size(10,10))
        sizer1.Add(wx.Button(self, 30, "Refresh Power"), 1, wx.EXPAND)

        sizer.Add(sizer1, 0, wx.EXPAND)
        self.sizer = sizer
        self.SetSizer(self.sizer)
        self.SetAutoLayout(True)
        self.Fit()
        #self.Bind(wx.EVT_SIZE, self.on_size)

        self.Bind(wx.EVT_BUTTON, self.on_remove, id=10)
        self.Bind(wx.EVT_BUTTON, self.on_add, id=20)
        self.Bind(wx.EVT_BUTTON, self.on_refresh_powers, id=30)
        self.grid.Bind(wx.grid.EVT_GRID_CELL_CHANGE, self.on_cell_change)
        n_list = handler.master_dom._get_childNodes()
        self.n_list = n_list
        self.master_dom = handler.master_dom
        self.grid.CreateGrid(len(n_list),5,1)
        self.grid.SetRowLabelSize(0)
        self.grid.SetColLabelValue(0,"PP")
        self.grid.SetColLabelValue(1,"Lvl")
        self.grid.SetColLabelValue(2,"Power")
        self.grid.SetColLabelValue(3,"Desc")
        self.grid.SetColLabelValue(4,"Type")
        for i in range(len(n_list)):
            self.refresh_row(i)
        self.refresh_data()
        self.temp_dom = None

    def on_cell_change(self,evt):
        row = evt.GetRow()
        col = evt.GetCol()
        value = self.grid.GetCellValue(row,col)
        """if col == 0:
            self.n_list[row].setAttribute('memrz',value)"""


    def refresh_row(self,i):
        power = self.n_list[i]

        point = power.getAttribute('point')
        name = power.getAttribute('name')
        type = power.getAttribute('desc')
        test = power.getAttribute('test')
        level = power.getAttribute('level')
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
                self.master_dom.removeChild(self.n_list[i])

    def on_add(self,evt):
        if not self.temp_dom:
            tmp = open(orpg.dirpath.dir_struct["dnd3e"]+"dnd3epowers.xml","r")

            xml_dom = parseXml_with_dlg(self,tmp.read())
            xml_dom = xml_dom._get_firstChild()
            tmp.close()
            self.temp_dom = xml_dom
        f_list = self.temp_dom.getElementsByTagName('power')
        opts = []
        #lvl = int(dnd3e_char_child.get_char_lvl('level'))
        #castlvl = lvl / 2
        for f in f_list:
            spelllvl = f.getAttribute('level')
            #if spelllvl <= "1":
            #    opts.append("(" + f.getAttribute('level') + ") - " + f.getAttribute('name') + " - " + f.getAttribute('test'))
            #else:
            #    if eval('%d >= %s' %(castlvl, spelllvl)):
            opts.append("(" + f.getAttribute('level') + ") - " +
                        f.getAttribute('name') + " - " + f.getAttribute('test'))
        dlg = wx.SingleChoiceDialog(self,'Choose Power','Powers',opts)
        if dlg.ShowModal() == wx.ID_OK:
            i = dlg.GetSelection()
            new_node = self.master_dom.appendChild(f_list[i].cloneNode(False))
            self.grid.AppendRows(1)
            self.n_list = self.master_dom.getElementsByTagName('power')
            self.refresh_row(self.grid.GetNumberRows()-1)
            self.handler.refresh_powers()
        dlg.Destroy()

    def on_remove(self,evt):
        rows = self.grid.GetNumberRows()
        for i in range(rows):
            if self.grid.IsInSelection(i,0):
                self.grid.DeleteRows(i)
                self.master_dom.removeChild(self.n_list[i])
                self.n_list = self.master_dom.getElementsByTagName('weapon')
                self.handler.refresh_powers()

    def on_refresh_powers( self, evt ):
        #a 1.5002,1.5014 s
        self.root.pp.set_char_pp('current1',self.root.pp.get_char_pp('max1'))
        self.root.pp.set_char_pp('free',self.root.pp.get_char_pp('maxfree'))
        #a 1.5002,1.5014 e



    def on_size(self,event):
        s = self.GetClientSizeTuple()
        self.grid.SetDimensions(0,0,s[0],s[1]-25)
        self.sizer.SetDimension(0,s[1]-25,s[0],25)
        (w,h) = self.grid.GetClientSizeTuple()
        cols = self.grid.GetNumberCols()
        col_w = w/(cols)
        for i in range(0,cols):
            self.grid.SetColSize(i,col_w)
        self.grid.SetColSize(0,w * 0.05)
        self.grid.SetColSize(1,w * 0.05)
        self.grid.SetColSize(2,w * 0.30)
        self.grid.SetColSize(3,w * 0.30)
        self.grid.SetColSize(4,w * 0.30)

    def refresh_data(self):

        for i in range(len(self.n_list)):
            self.refresh_row(i)

class dnd3epp(snp_char_child):
    """ Node Handler for power points.  This handler will be
        created by dnd3echar_handler.
    """
    def __init__(self,xml_dom,tree_node,parent):
        snp_char_child.__init__(self,xml_dom,tree_node,parent)
        self.hparent = parent #a 1.5002 allow ability to run up tree.
        self.root = getRoot(self)
        self.root.pp = self
        self.ppPanel=None


    def get_design_panel(self,parent):
        wnd = outline_panel(parent,self,pp_panel,"Power Points")
        wnd.title = "Power Points"
        return wnd


    def tohtml(self):
        html_str = "<table width=100% border=1 ><tr BGCOLOR=#E9E9E9 >"
        #html_str += "<th colspan=8>Power Points</th></tr>" #d 1.6010
        html_str += "<th colspan=7>Power Points</th>" #a 1.6010
        #m 1.6010 rearanged everything below to "return html_str"
        html_str += "</tr><tr>"
        html_str += "<th colspan=2>Max:</th>"
        html_str += "<td>"+self.master_dom.getAttribute('max1')+"</td>"
        html_str += "<th colspan=3>Max Talents/day:</th>"
        html_str += "<td>"+self.master_dom.getAttribute('maxfree')+"</td>"
        html_str += "</tr><tr>"
        html_str += "<th colspan=2>Current:</th>"
        html_str += "<td>"+self.master_dom.getAttribute('current1')+"</td>"
        html_str += "<th colspan=3>Current Talents/day:</th>"
        html_str += "<td>"+self.master_dom.getAttribute('free')+"</td>"
        html_str += "</tr></table>"
        return html_str

    def get_char_pp( self, attr ):
        pp = self.master_dom.getAttribute(attr)
        #print "dnd3epp -get_char_pp: attr,pp",attr,pp
        return pp

    def set_char_pp( self, attr, evl ):
        qSub = str(evl) #a 1.5014 must force it to be a string for next call.
        self.master_dom.setAttribute(attr, qSub)
        #This function needs to be looked at the idea is to refresh the power panel
        #But it causes a seg fault when you refresh from powers -mgt
        #if self.ppPanel:                #a 1.5015
        #    self.ppPanel.on_refresh(attr,qSub)   #a 1.5015


class pp_panel(wx.Panel):
    def __init__(self, parent, handler):
        wx.Panel.__init__(self, parent, -1)
        self.hparent = handler #a 1.5002 allow ability to run up tree.
        #a 1.5002 we need the functional parent, not the invoking parent.
        self.hparent.ppPanel=self #a 1.5xx

        pname = handler.master_dom.setAttribute("name", 'PowerPoints')
        self.sizer = wx.FlexGridSizer(2, 4, 2, 2)  # rows, cols, hgap, vgap
        self.master_dom = handler.master_dom

        self.static1= wx.StaticText(self, -1, "PP Current:")  #a 1.5015
        self.dyn1= wx.TextCtrl(self, PP_CUR,
                self.master_dom.getAttribute('current1'))   #a 1.5015
        self.dyn3= wx.TextCtrl(self, PP_FRE,
                self.master_dom.getAttribute('free'))       #a 1.5015
#        self.sizer.AddMany([ (wx.StaticText(self, -1, "PP Current:"),  #d 1.5015
#                                           0, wx.ALIGN_CENTER_VERTICAL),
#            (wx.TextCtrl(self, PP_CUR,                                 #d 1.5015
#                self.master_dom.getAttribute('current1')),   0, wx.EXPAND),
        self.sizer.AddMany([ (self.static1, 0, wx.ALIGN_CENTER_VERTICAL),
            (self.dyn1,   0, wx.EXPAND),
            (wx.StaticText(self, -1, "PP Max:"), 0, wx.ALIGN_CENTER_VERTICAL),
            (wx.TextCtrl(self, PP_MAX,
                self.master_dom.getAttribute('max1')),  0, wx.EXPAND),
            (wx.StaticText(self, -1, "Current Free Talants per day:"),
                          0, wx.ALIGN_CENTER_VERTICAL),
            (self.dyn3,  0, wx.EXPAND),                          #a 1.5015
#            (wx.TextCtrl(self, PP_FRE,
#                self.master_dom.getAttribute('free')),  0, wx.EXPAND),#d 1.5015
            (wx.StaticText(self, -1, "Max Free Talants per day:"),
                            0, wx.ALIGN_CENTER_VERTICAL),
            (wx.TextCtrl(self, PP_MFRE,
                self.master_dom.getAttribute('maxfree')),  0, wx.EXPAND),
            ])

        self.sizer.AddGrowableCol(1)
        self.SetSizer(self.sizer)
        self.SetAutoLayout(True)
        self.Fit()

        #self.Bind(wx.EVT_SIZE, self.on_size)
        self.Bind(wx.EVT_TEXT, self.on_text, id=PP_MAX)
        self.Bind(wx.EVT_TEXT, self.on_text, id=PP_CUR)
        self.Bind(wx.EVT_TEXT, self.on_text, id=PP_FRE)
        self.Bind(wx.EVT_TEXT, self.on_text, id=PP_MFRE)

    def on_text(self,evt):
        id = evt.GetId()
        if id == PP_CUR:
            self.master_dom.setAttribute('current1',evt.GetString())
        elif id == PP_MAX:
            self.master_dom.setAttribute('max1',evt.GetString())
        elif id == PP_FRE:
            self.master_dom.setAttribute('free',evt.GetString())
        elif id == PP_MFRE:
            self.master_dom.setAttribute('maxfree',evt.GetString())

    def on_size(self,evt):
        s = self.GetClientSizeTuple()
        self.sizer.SetDimension(0,0,s[0],s[1])

    #a 5.015 this whole function.
    def on_refresh(self,attr,value):
        if attr == 'current1':
            self.dyn1.SetValue(value)
        else:
            self.dyn3.SetValue(value)
