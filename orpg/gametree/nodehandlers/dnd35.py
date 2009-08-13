import orpg.tools.orpg_settings
import orpg.minidom
from core import *
from containers import *
from string import *  #a 1.6003
from inspect import *  #a 1.9001
dnd35_EXPORT = wx.NewId()

############Global Stuff##############

HP_CUR = wx.NewId()
HP_MAX = wx.NewId()

def getRoot (node): # a 1.5002 this whole function is new.
    root = None
    target = node
    while target != None:
        root = target
        target = target.hparent
    return root

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
class dnd35char_handler(container_handler):
    """ Node handler for a dnd35 charactor
        <nodehandler name='?'  module='dnd35' class='dnd35char_handler2'  />
    """
    def __init__(self,xml_dom,tree_node):
        node_handler.__init__(self,xml_dom,tree_node)
        self.Version = "v1.000" #a 1.6000 general documentation, usage.

        print "dnd35char_handler - version:",self.Version #m 1.6000

        self.hparent = None #a 1.5002 allow ability to run up tree, this is the

        self.frame = open_rpg.get_component('frame')
        self.child_handlers = {}
        self.new_child_handler('general','GeneralInformation',dnd35general,'gear')
        self.new_child_handler('inventory','MoneyAndInventory',dnd35inventory,'money')
        self.new_child_handler('character','ClassesAndStats',dnd35classnstats,'knight')
        self.new_child_handler('snf','SkillsAndFeats',dnd35skillsnfeats,'book')
        self.new_child_handler('combat','Combat',dnd35combat,'spears')

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
        html_str += self.general.tohtml()+"</td></tr>"
        html_str += "<tr><td width='50%' valign=top >"+self.abilities.tohtml()
        html_str += "<P>" + self.saves.tohtml()
        html_str += "<P>" + self.attacks.tohtml()
        html_str += "<P>" + self.ac.tohtml()
        html_str += "<P>" + self.feats.tohtml()
        html_str += "<P>" + self.inventory.tohtml() +"</td>"
        html_str += "<td width='50%' valign=top >"+self.classes.tohtml()
        html_str += "<P>" + self.hp.tohtml()
        html_str += "<P>" + self.skills.tohtml() +"</td>"
        #a block for 1.6009 end

        html_str += "</tr></table>"
        return html_str

    def about(self):
        html_str = "<img src='" + orpg.dirpath.dir_struct["icon"]
        html_str += "dnd3e_logo.gif' ><br /><b>dnd35 Character Tool "
        html_str += self.Version+"</b>" #m 1.6000 was hard coded.
        html_str += "<br />by Dj Gilcrease<br />digitalxero@gmail.com"
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

class dnd35_char_child(node_handler):
    """ Node Handler for skill.  This handler will be
        created by dnd35char_handler.
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

class dnd35general(dnd35_char_child):
    """ Node Handler for general information.   This handler will be
        created by dnd35char_handler.
    """
    def __init__(self,xml_dom,tree_node,parent):
        dnd35_char_child.__init__(self,xml_dom,tree_node,parent)
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

class dnd35inventory(dnd35_char_child):
    """ Node Handler for general information.   This handler will be
        created by dnd35char_handler.
    """
    def __init__(self,xml_dom,tree_node,parent):
        dnd35_char_child.__init__(self,xml_dom,tree_node,parent)
        self.hparent = parent #a 1.5002 allow ability to run up tree.
        self.root = getRoot(self) #a 1.6009
        self.root.inventory = self #a 1.6009

    def get_design_panel(self,parent):
        wnd = inventory_pane(parent, self) #outline_panel(parent,self,inventory_grid,"Inventory")
        wnd.title = "Inventory"
        return wnd

    def tohtml(self):
        n_list = self.master_dom._get_childNodes()
        html_str = "<table width=100% border=1 ><tr BGCOLOR=#E9E9E9 ><th>Inventory</th></tr><tr><td>"
        for n in n_list:
            t_node = safe_get_text_node(n)
            html_str += "<B>"+n._get_tagName().capitalize() +":</B> "
            html_str += t_node._get_nodeValue() + "<br />"
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


class dnd35classnstats(dnd35_char_child):
    """ Node handler for a dnd35 charactor
        <nodehandler name='?'  module='dnd35' class='dnd35char_handler2'  />
    """
    def __init__(self,xml_dom,tree_node,parent):
        node_handler.__init__(self,xml_dom,tree_node)
        self.hparent = parent #a 1.5002 allow ability to run up tree.
        dnd35_char_child.__init__(self,xml_dom,tree_node,parent)
        self.frame = open_rpg.get_component('frame')
        self.child_handlers = {}
        self.new_child_handler('abilities','Abilities Scores',dnd35ability,'gear')
        self.new_child_handler('classes','Classes',dnd35classes,'knight')
        self.new_child_handler('saves','Saves',dnd35saves,'skull')
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
        created by dnd35char_handler.
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

class dnd35ability(class_char_child):
    """ Node Handler for ability.   This handler will be
        created by dnd35char_handler.
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
        #print "dnd35ability - init self.abilities",self.abilities #a (debug) 1.5002

    def on_rclick( self, evt ):
        item = self.tree.GetSelection()
        name = self.tree.GetItemText( item )
        #if item == self.mytree_node:   #d 1.6016
        #    dnd35_char_child.on_ldclick( self, evt ) #d 1.6016
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

class dnd35classes(class_char_child):
    """ Node Handler for classes.  This handler will be
        created by dnd35char_handler.
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

        self.Bind(wx.EVT_BUTTON, self.on_remove, id=10)
        self.Bind(wx.EVT_BUTTON, self.on_add, id=20)
        self.grid.Bind(wx.grid.EVT_GRID_CELL_CHANGE, self.on_cell_change)

        n_list = handler.master_dom._get_childNodes()
        self.n_list = n_list
        self.master_dom = handler.master_dom
        self.grid.CreateGrid(len(n_list),3,1)
        self.grid.SetRowLabelSize(0)
        self.grid.SetColLabelValue(0,"Class")
        self.grid.SetColLabelValue(1,"Level")
        self.grid.SetColLabelValue(2,"Refrence")
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
        book = n.getAttribute('book')
        self.grid.SetCellValue(i,0,name)
        self.grid.SetReadOnly(i,0)
        self.grid.SetCellValue(i,1,level)
        self.grid.SetCellValue(i,2,book)
        self.grid.SetReadOnly(i,0)
        self.grid.AutoSizeColumn(0)
        self.grid.AutoSizeColumn(1)
        self.grid.AutoSizeColumn(2)

    def on_remove(self,evt):
        rows = self.grid.GetNumberRows()
        for i in range(rows):
            if self.grid.IsInSelection(i,0):
                self.grid.DeleteRows(i)
                self.master_dom.removeChild(self.n_list[i])

    def on_add(self,evt):
        if not self.temp_dom:
            tmp = open(orpg.dirpath.dir_struct["dnd35"]+"dnd35classes.xml","r")
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


class dnd35saves(class_char_child):
    """ Node Handler for saves.   This handler will be
        created by dnd35char_handler.
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
        #print "dnd35saves, get_mod: self,root",self,self.root #a (debug) 1.5002
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
            #dnd35_char_child.on_ldclick(self,evt) #d 1.5003 this busted
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

class dnd35skillsnfeats(dnd35_char_child):
    """ Node handler for a dnd35 charactor
        <nodehandler name='?'  module='dnd35' class='dnd35char_handler2'  />
    """
    def __init__(self,xml_dom,tree_node,parent):
        self.hparent = parent #a 1.5002 allow ability to run up tree.
        self.root = getRoot(self) #a 1.6009

        node_handler.__init__(self,xml_dom,tree_node)
        dnd35_char_child.__init__(self,xml_dom,tree_node,parent)
        self.frame = open_rpg.get_component('frame')
        self.child_handlers = {}
        self.new_child_handler('skills','Skills',dnd35skill,'book')
        self.new_child_handler('feats','Feats',dnd35feats,'book')
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
        created by dnd35char_handler.
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

class dnd35skill(skills_char_child):
    """ Node Handler for skill.  This handler will be
        created by dnd35char_handler.
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
            #dnd35_char_child.on_ldclick(self,evt) #d 1.6014
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
            dnd35_char_child.on_ldclick(self,evt)
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
            print "Please advise dnd35 maintainer alert 1.5002 raised"

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




class dnd35feats(skills_char_child):
    """ Node Handler for classes.  This handler will be
        created by dnd35char_handler.
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
        self.grid = wx.grid.Grid(self, -1, style=wx.SUNKEN_BORDER | wx.WANTS_CHARS)
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
        self.grid.SetColLabelValue(1,"Reference")
        self.grid.SetColLabelValue(2,"Description") #m 1.6 typo correction.
        wrap = wx.grid.GridCellAutoWrapStringRenderer()
        attr = wx.grid.GridCellAttr()
        attr.SetRenderer(wrap)
        self.grid.SetColAttr(2, attr)
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
        self.grid.AutoSizeColumn(0)
        self.grid.AutoSizeColumn(1)
        self.grid.AutoSizeColumn(2, False)
        self.grid.AutoSizeRow(i)

    def on_remove(self,evt):
        rows = self.grid.GetNumberRows()
        for i in range(rows):
            if self.grid.IsInSelection(i,0):
                self.grid.DeleteRows(i)
                self.master_dom.removeChild(self.n_list[i])

    def on_add(self,evt):

        if not self.temp_dom:
            tmp = open(orpg.dirpath.dir_struct["dnd35"]+"dnd35feats.xml","r")
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

class dnd35combat(dnd35_char_child):
    """ Node handler for a dnd35 charactor
        <nodehandler name='?'  module='dnd35' class='dnd35char_handler2'  />
    """
    def __init__(self,xml_dom,tree_node,parent):

        node_handler.__init__(self,xml_dom,tree_node)

        self.hparent = parent #a 1.5002 allow ability to run up tree.
        self.root = getRoot(self) #a 1.5012



        #mark3
        dnd35_char_child.__init__(self,xml_dom,tree_node,parent)
        self.frame = open_rpg.get_component('frame')
        self.child_handlers = {}
        self.new_child_handler('hp','Hit Points',dnd35hp,'gear')
        self.new_child_handler('attacks','Attacks',dnd35attacks,'spears')
        self.new_child_handler('ac','Armor',dnd35armor,'spears')
        #print "combat",self.child_handlers #a (debug) 1.5002
        #wxMenuItem(self.tree.std_menu, dnd35_EXPORT, "Export...", "Export")
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
        created by dnd35char_handler.
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

class dnd35hp(combat_char_child):
    """ Node Handler for hit points.  This handler will be
        created by dnd35char_handler.
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

class dnd35attacks(combat_char_child):
    """ Node Handler for attacks.  This handler will be
        created by dnd35char_handler.
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
        self.html_str += ("<br />  This character has weapons with no "+
             "footnotes.  This program will "+
             "add footnotes to the weapons which have names that still match "+
             "the orginal names.  If you have changed the weapon name, you "+
             "will see some weapons with a footnote of 'X', you will have "+
             "to either delete and re-add the weapon, or research "+
             "and add the correct footnotes for the weapon.\n"+
             "<br />  Please be aware, that only the bow/sling footnote is "+
             "being used to affect changes to rolls; implemenation of other "+
             "footnotes to automaticly adjust rolls will be completed as "+
             "soon as time allows." +
             "<br /><br />Update to character:"+self.root.general.charName+
             "<br /><br />"+
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
            tmp = open(orpg.dirpath.dir_struct["dnd35"]+"dnd35weapons.xml","r")
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
            #dnd35_char_child.on_ldclick(self,evt)#d 1.6015
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
            if find(dmg, "Monk Med") > -1:
                if monkLvl == None:     #a 1.5009
                    txt = 'Attempting to use monk attack, but has no monk '
                    txt += 'levels, please choose a different attack.'
                    chat.ParsePost( txt, True, True ) #a 1.5009
                    return #a 1.5009
                else:   #a 1.5009
                    lvl=int(monkLvl)
                    if lvl <= 3:     #m 1.6022 reversed the order of checks.
                        dmg = dmg.replace("Monk Med", "1d6")
                    elif lvl <= 7:
                        dmg = dmg.replace("Monk Med", "1d8")
                    elif lvl <= 11:
                        dmg = dmg.replace("Monk Med", "1d10")
                    elif lvl <= 15:
                        dmg = dmg.replace("Monk Med", "2d6")
                    elif lvl <= 19:
                        dmg = dmg.replace("Monk Med", "2d8")
                    elif lvl <= 20:
                        dmg = dmg.replace("Monk Med", "2d10")
            if find(dmg, "Monk Small") > -1:
                if monkLvl == None:     #a 1.5009
                    txt = 'Attempting to use monk attack, but has no monk '
                    txt += 'levels, please choose a different attack.'
                    chat.ParsePost( txt, True, True ) #a 1.5009
                    return #a 1.5009
                else:   #a 1.5009
                    lvl=int(monkLvl)
                    if lvl <= 3:     #m 1.6022 reversed the order of the checks
                        dmg = dmg.replace("Monk Small", "1d4")
                    elif lvl <= 7:
                        dmg = dmg.replace("Monk Small", "1d6")
                    elif lvl <= 11:
                        dmg = dmg.replace("Monk Small", "1d8")
                    elif lvl <= 15:
                        dmg = dmg.replace("Monk Small", "1d10")
                    elif lvl <= 19:
                        dmg = dmg.replace("Monk Small", "2d6")
                    elif lvl <= 20:
                        dmg = dmg.replace("Monk Small", "2d8")
            if find(dmg, "Monk Large") > -1:
                if monkLvl == None:     #a 1.5009
                    txt = 'Attempting to use monk attack, but has no monk '
                    txt += 'levels, please choose a different attack.'
                    chat.ParsePost( txt, True, True ) #a 1.5009
                    return #a 1.5009
                else:   #a 1.5009
                    lvl=int(monkLvl)
                    if lvl <= 3:     #m 1.6022 reversed the order of the checks
                        dmg = dmg.replace("Monk Large", "1d8")
                    elif lvl <= 7:
                        dmg = dmg.replace("Monk Large", "2d6")
                    elif lvl <= 11:
                        dmg = dmg.replace("Monk Large", "2d8")
                    elif lvl <= 15:
                        dmg = dmg.replace("Monk Large", "3d6")
                    elif lvl <= 19:
                        dmg = dmg.replace("Monk Large", "3d8")
                    elif lvl <= 20:
                        dmg = dmg.replace("Monk Large", "4d8")
            flurry = False
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
                flurry = True

            (base, base2, base3, base4, base5, base6, stat_mod, misc) = self.get_attack_data(rangeOrMelee)  #a 1.5008
            name = name.replace('(Monk Med)', '')
            name = name.replace('(Monk Small)', '')
            if not flurry:
                if name == 'Shuriken':
                    for n in xrange(3):
                        self.sendRoll(base, stat_mod, misc, wepMod, name, '', dmg, aStrengthMod, rollAnyWay=True)
                        self.sendRoll(base2, stat_mod, misc, wepMod, name, '', dmg, aStrengthMod)
                        self.sendRoll(base3, stat_mod, misc, wepMod, name, '', dmg, aStrengthMod)
                        self.sendRoll(base4, stat_mod, misc, wepMod, name, '', dmg, aStrengthMod)
                        self.sendRoll(base5, stat_mod, misc, wepMod, name, '', dmg, aStrengthMod)
                        self.sendRoll(base6, stat_mod, misc, wepMod, name, '', dmg, aStrengthMod)
                else:
                    self.sendRoll(base, stat_mod, misc, wepMod, name, '', dmg, aStrengthMod, rollAnyWay=True)
                    self.sendRoll(base2, stat_mod, misc, wepMod, name, '', dmg, aStrengthMod)
                    self.sendRoll(base3, stat_mod, misc, wepMod, name, '', dmg, aStrengthMod)
                    self.sendRoll(base4, stat_mod, misc, wepMod, name, '', dmg, aStrengthMod)
                    self.sendRoll(base5, stat_mod, misc, wepMod, name, '', dmg, aStrengthMod)
                    self.sendRoll(base6, stat_mod, misc, wepMod, name, '', dmg, aStrengthMod)
            else:
                if monkLvl == None:
                    txt = 'Attempting to use monk attack, but has no monk '
                    txt += 'levels, please choose a different attack.'
                    chat.ParsePost( txt, True, True ) #a 1.5009
                    return
                else:
                    lvl = int(monkLvl)
                    if lvl <= 4:
                        flu = '-2'
                        atks = False
                    elif lvl <= 8:
                        flu = '-1'
                        atks = False
                    elif lvl <= 10:
                        flu = ''
                        atks = False
                    elif lvl <= 20:
                        flu = ''
                        atks = True

                    self.sendRoll(base, stat_mod, misc, wepMod, name, flu, dmg, aStrengthMod, rollAnyWay=True)
                    self.sendRoll(base, stat_mod, misc, wepMod, name, flu, dmg, aStrengthMod, rollAnyWay=True)
                    if atks:
                        self.sendRoll(base, stat_mod, misc, wepMod, name, flu, dmg, aStrengthMod, rollAnyWay=True)
                    self.sendRoll(base2, stat_mod, misc, wepMod, name, flu, dmg, aStrengthMod)
                    self.sendRoll(base3, stat_mod, misc, wepMod, name, flu, dmg, aStrengthMod)
                    self.sendRoll(base4, stat_mod, misc, wepMod, name, flu, dmg, aStrengthMod)
                    self.sendRoll(base5, stat_mod, misc, wepMod, name, flu, dmg, aStrengthMod)
                    self.sendRoll(base6, stat_mod, misc, wepMod, name, flu, dmg, aStrengthMod)



    def sendRoll(self, base, stat_mod, misc, wepMod, name, flu, dmg, aStrengthMod, rollAnyWay=False):
        if base != 0 or rollAnyWay:
            base = base + int(stat_mod) + misc + wepMod #m 1.5008
            if base >= 0:
                mod1 = "+"
            else:
                mod1 = ""
            txt = ' %s Attack Roll: <b>[1d20%s%s%s]</b>' % (name, mod1, base, flu)
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

        handler.mrFrame.append(masterFrame)


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
        tmelee = int(melee[0]) + int(melee[6]) + int(melee[7])
        tranged = int(ranged[0]) + int(ranged[6]) + int(ranged[7])
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
                tmp = open(orpg.dirpath.dir_struct["dnd35"]+
                            "dnd35weapons.xml","r")
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
            tmp = open(orpg.dirpath.dir_struct["dnd35"]+"dnd35weapons.xml","r")
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


class dnd35armor(combat_char_child):
    """ Node Handler for ac.  This handler will be
        created by dnd35char_handler.
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
            tmp = open(orpg.dirpath.dir_struct["dnd35"]+"dnd35armor.xml","r")
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
