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
# File: orpg_windows.py
# Author: Chris Davis
# Maintainer:
# Version:
#   $Id: orpg_windows.py,v 1.42 2007/12/07 20:59:16 digitalxero Exp $
#
# Description: orpg custom windows
#

__version__ = "$Id: orpg_windows.py,v 1.42 2007/12/07 20:59:16 digitalxero Exp $"

from orpg.orpg_wx import *
from orpg.orpgCore import *
import orpg.tools.rgbhex
from orpg.dirpath import dir_struct
from orpg.tools.metamenus import MenuEx

class img_helper:
    def __init__(self):
        pass

    def load_url(self,path):
        img_type = self.get_type(path)
        try:
            data = urllib.urlretrieve(path)
            if data: img = wx.Bitmap(data[0], img_type)
            else: raise IOError, "Image refused to load!"
        except IOError, e: img = None
        return img

    def load_file(self,path):
        img_type = self.get_type(path)
        return wx.Bitmap(path, img_type)

    def get_type(self,file_name):
        pos = string.rfind(file_name,'.')
        ext = string.lower(file_name[pos+1:])
        img_type = 0
	# TaS - sirebral.  Replaces 10 lines with 6 lines.
	recycle_bin = {"gif": wx.BITMAP_TYPE_GIF, "jpg": wx.BITMAP_TYPE_JPEG, 
        "jpeg": wx.BITMAP_TYPE_JPEG, "bmp": wx.BITMAP_TYPE_BMP, "png": wx.BITMAP_TYPE_PNG}
	if recycle_bin.has_key(ext): img_type = recycle_bin[ext]
	else: img_type = None ## this was imf_type = None.  imf?
	del recycle_bin; return img_type

################################
## Tabs
################################
class orpgTabberWnd(FNB.FlatNotebook):
    def __init__(self, parent, closeable=False, size=wx.DefaultSize, style = False):
        nbstyle = FNB.FNB_HIDE_ON_SINGLE_TAB|FNB.FNB_BACKGROUND_GRADIENT
        FNB.FlatNotebook.__init__(self, parent, -1, size=size, style=nbstyle)
        rgbcovert = orpg.tools.rgbhex.RGBHex()
        self.log = component.get("log")
        self.log.log("Enter orpgTabberWnd", ORPG_DEBUG)
        self.settings = component.get("settings")
        tabtheme = self.settings.get_setting('TabTheme')
        tabtext = self.settings.get_setting('TabTextColor')
        (tred, tgreen, tblue) = rgbcovert.rgb_tuple(tabtext)
        tabbedwindows = component.get("tabbedWindows")
        tabbedwindows.append(self)
        component.add("tabbedWindows", tabbedwindows)

        theme_dict = {'slanted&aqua': FNB.FNB_VC8, 'slanted&bw': FNB.FNB_VC8, 'flat&aqua': FNB.FNB_FANCY_TABS, 
            'flat&bw': FNB.FNB_FANCY_TABS, 'customflat': FNB.FNB_FANCY_TABS, 'customslant': FNB.FNB_VC8, 
            'slanted&colorful': FNB.FNB_VC8|FNB.FNB_COLORFUL_TABS, 'slant&colorful': FNB.FNB_VC8|FNB.FNB_COLORFUL_TABS}
        nbstyle |= theme_dict[tabtheme]
        if style: nbstyle |= style
        self.SetWindowStyleFlag(nbstyle)

	#Tas - sirebral.  Planned changes to the huge statement below.  
        if tabtheme == 'slanted&aqua':
            self.SetGradientColourTo(wx.Color(0, 128, 255))
            self.SetGradientColourFrom(wx.WHITE)

        elif tabtheme == 'slanted&bw':
            self.SetGradientColourTo(wx.WHITE)
            self.SetGradientColourFrom(wx.WHITE)

        elif tabtheme == 'flat&aqua':
            self.SetGradientColourFrom(wx.Color(0, 128, 255))
            self.SetGradientColourTo(wx.WHITE)
            self.SetNonActiveTabTextColour(wx.BLACK)

        elif tabtheme == 'flat&bw':
            self.SetGradientColourTo(wx.WHITE)
            self.SetGradientColourFrom(wx.WHITE)
            self.SetNonActiveTabTextColour(wx.BLACK)

        elif tabtheme == 'customflat':
            gfrom = self.settings.get_setting('TabGradientFrom')
            (red, green, blue) = rgbcovert.rgb_tuple(gfrom)
            self.SetGradientColourFrom(wx.Color(red, green, blue))

            gto = self.settings.get_setting('TabGradientTo')
            (red, green, blue) = rgbcovert.rgb_tuple(gto)
            self.SetGradientColourTo(wx.Color(red, green, blue))
            self.SetNonActiveTabTextColour(wx.Color(tred, tgreen, tblue))

        elif tabtheme == 'customslant':
            gfrom = self.settings.get_setting('TabGradientFrom')
            (red, green, blue) = rgbcovert.rgb_tuple(gfrom)
            self.SetGradientColourFrom(wx.Color(red, green, blue))

            gto = self.settings.get_setting('TabGradientTo')
            (red, green, blue) = rgbcovert.rgb_tuple(gto)
            self.SetGradientColourTo(wx.Color(red, green, blue))
            self.SetNonActiveTabTextColour(wx.Color(tred, tgreen, tblue))

        tabbg = self.settings.get_setting('TabBackgroundGradient')
        (red, green, blue) = rgbcovert.rgb_tuple(tabbg)
        self.SetTabAreaColour(wx.Color(red, green, blue))
        self.Refresh()
        self.log.log("Exit orpgTabberWnd", ORPG_DEBUG)


########################
## About HTML Dialog
########################

class AboutHTMLWindow(wx.html.HtmlWindow):
    "Window used to display the About dialog box"

    # Init using the derived from class
    def __init__( self, parent, id, position, size, style ):
        wx.html.HtmlWindow.__init__( self, parent, id, position, size, style )

    def OnLinkClicked( self, ref ):
        "Open an external browser to resolve our About box links!!!"
        href = ref.GetHref()
        webbrowser.open( href )
    """
      This class extends wxSplitterWindow to add an auto expand behavior.  The idea is that the sash
           determines the ratio of the two windows, while the mouse position determines which
           side will get the larger share of the screen real estate.  It is used instead of regular
           wxSplitterWindows if the EnableSplittersAutoExpand setting doesn't evaluate as False.
    
      Note:  To be truly functional, some way of passing EVT_MOTION events to this class, even when the
           event takes place over child windows needs to be accomplished.  Once this is accomplished,
           however, the class should work as written.
    """
class orpgFocusSplitterWindow(wx.SplitterWindow):

    def __init__(self,parent,id = -1,AutoExpand = 1,point = wx.DefaultPosition,size = wx.DefaultSize,style=wx.SP_3D,name="splitterWindow"):
        wx.SplitterWindow.__init__(self,parent,id,point,size,style,name)
        self.auto = AutoExpand
        self.Bind(wx.EVT_IDLE, self.OnIdle)  # used in workaround idea from Robin Dunn instead of EVT_MOTION

    #  Get's called during idle times.  It checks to see if the mouse is over self and calls
    #      OnMotion with the coordinates

    def EnableAutoExpand(self,value):
        self.auto = value

    def OnIdle(self,event):
        if self.auto:
            (screen_x,screen_y) = wx.GetMousePosition()
            (x,y) = self.ScreenToClientXY(screen_x,screen_y) # translate coordinates
            (w,h) = self.GetSizeTuple()
            if x >= 0 and x < w and y >= 0 and y < h: self.OnMotion(x,y)
        event.Skip()

    def OnMotion(self,mouse_X,mouse_Y):
        # Gather some info using standard wxWindows calls
        (w,h) = self.GetClientSizeTuple()
        (second_w,second_h) = self.GetWindow2().GetClientSizeTuple()
        (second_x,second_y) = self.GetWindow2().GetPositionTuple()
        splitmode = self.GetSplitMode()
        sash = self.GetSashPosition()

        if splitmode == wx.SPLIT_VERTICAL:
            pos = mouse_X #  Position of the mouse pointer
            second = second_x  #  Beginning of the second (Right) pane
            second_size = second_w  # Size of the second pane
        else:
            pos = mouse_Y #  Position of the mouse pointer
            second = second_y  #  Beginning of the second (Bottom) pane
            second_size = second_h  # Size of the second pane
        sash_size = second - sash    # Beginning of sash to beginning of second is the sash size

        if (pos > sash + sash_size and second_size < sash) or (pos < sash and second_size > sash):
            #  Equivalent to the following
            #  if
            #  (the mouse position is below/to the right of the sash, including it's thickness
            #      i.e. in the second window
            #  AND
            #  the second window is smaller than the 1st (size = the sash position))
            #
            #  OR
            #
            #  (the mouse position is above/to the left of the sash
            #      i.e. in the first window
            #  AND
            #  the second window is bigger than the 1st)


            # flip the split
            self.SetSashPosition(second_size)
            #  Both cases above set the sash to a position that corresponds to the size of the
            #  second window.  This has the effect of making the first window trade sizes with
            #  the second window.
            #      In the first part of the OR clause, the first window takes the second window's
            #      size because the user wants the currently small lower window to be big, so
            #      the first must take on the size of the small.
            #
            #      In the second case of the OR clause, the first window takes the second window's
            #      size because the user wants the currently small upper window to be big (which
            #      the second window currently is), so make the first take the size of the second.


#####################
## A text editor for openrpg related text
#####################

class html_text_edit(wx.Panel):
    """ a text ctrl with html helpers """
    def __init__(self, parent, id, text, callback,home_dir):
        wx.Panel.__init__(self, parent,-1)
        self.r_h = orpg.tools.rgbhex.RGBHex()
        self.text = wx.TextCtrl(self, id, text, wx.DefaultPosition,
                             wx.DefaultSize,
                             wx.TE_MULTILINE )
        self.Bind(wx.EVT_SIZE, self.OnSize)
        self.Bind(wx.EVT_TEXT, callback, id=id)
        self.callback = callback
        self.BOLD = wx.NewId()
        self.ITALIC = wx.NewId()
        self.UNDER = wx.NewId()
        self.COLOR = wx.NewId()
        self.DIE100 = wx.NewId()
        self.DIE20 = wx.NewId()
        self.DIE10 = wx.NewId()
        self.DIE8 = wx.NewId()
        self.DIE6 = wx.NewId()
        self.DIE4 = wx.NewId()
        self.DIE2 = wx.NewId()
        self.DIE = wx.NewId()
        self.sizer = wx.BoxSizer(wx.HORIZONTAL)
        gif = wx.Image(dir_struct["icon"]+"bold.gif", wx.BITMAP_TYPE_GIF)
        self.sizer.Add(wx.BitmapButton(self, self.BOLD, gif.ConvertToBitmap()), 0, wx.EXPAND)
        gif = wx.Image(dir_struct["icon"]+"italic.gif", wx.BITMAP_TYPE_GIF)
        self.sizer.Add(wx.BitmapButton(self, self.ITALIC, gif.ConvertToBitmap()), 0, wx.EXPAND)
        gif = wx.Image(dir_struct["icon"]+"underlined.gif", wx.BITMAP_TYPE_GIF)
        self.sizer.Add(wx.BitmapButton(self, self.UNDER, gif.ConvertToBitmap()), 0, wx.EXPAND)
        self.color_button = wx.Button(self, self.COLOR, "C",wx.Point(0,0),wx.Size(22,0))
        self.color_button.SetBackgroundColour(wx.BLACK)
        self.color_button.SetForegroundColour(wx.WHITE)
        self.sizer.Add(self.color_button, 0, wx.EXPAND)
        self.Bind(wx.EVT_BUTTON, self.on_text_format, id=self.BOLD)
        self.Bind(wx.EVT_BUTTON, self.on_text_format, id=self.ITALIC)
        self.Bind(wx.EVT_BUTTON, self.on_text_format, id=self.UNDER)
        self.Bind(wx.EVT_BUTTON, self.on_text_format, id=self.COLOR)

    def on_text_format(self,event):
        id = event.GetId()
        if wx.Platform == '__WXMSW__': txt = self.text.GetLabel()
        else: txt = self.text.GetValue()
        (beg,end) = self.text.GetSelection()
        if beg != end: sel_txt = txt[beg:end]
        else: return
        print txt
	# TaS - sirebral. Replaces 6 lines with 4 lines.
	recycle_bin = {self.BOLD: "b", self.ITALIC: "i", self.UNDER: "u"}
	if recycle_bin.has_key(id):
	    sel_txt = "<" + recycle_bin[id] + ">" + sel_txt + "</" + recycle_bin[id] + ">"
	    del recycle_bin

        elif id == self.COLOR:
            hexcolor = self.r_h.do_hex_color_dlg(self)
            if hexcolor:
                sel_txt = "<font color='"+hexcolor+"'>"+sel_txt+"</font>"
                self.color_button.SetBackgroundColour(hexcolor)

        txt = txt[:beg] + sel_txt + txt[end:]
        if wx.Platform == '__WXMSW__': txt = self.text.SetLabel(txt)
        else: txt = self.text.SetValue(txt)
        self.text.SetInsertionPoint(beg)
        self.text.SetFocus()
        self.callback(wx.Event(self.text.GetId()))

    def set_text(self,txt):
        self.text.SetValue(txt)

    def get_text(self):
        return self.text.GetValue()

    def OnSize(self,event):
        (w,h) = self.GetClientSizeTuple()
        self.text.SetDimensions(0,0,w,h-25)
        self.sizer.SetDimension(0,h-25,w,25)

###########################
## HTML related clasees
###########################

class http_html_window(wx.html.HtmlWindow):
    """ a wx.html.HTMLwindow that will load links  """
    def __init__(self, parent, id):
        wx.html.HtmlWindow.__init__(self, parent, id, wx.DefaultPosition,wx.DefaultSize, wx.SUNKEN_BORDER | wx.html.HW_SCROLLBAR_AUTO)
        self.path = ""
        self.local = 0
        #self.title = title

    def OnLinkClicked(self, linkinfo):
        address = linkinfo.GetHref()
        if address[:4] == "http":
            self.load_url(address)
            self.local = 0
        elif address[0] == "#" or self.local: self.base_OnLinkClicked(linkinfo)
        else: self.load_url(self.path+address)

    def load_url(self,path):
        print path
        dlg = wx.ProgressDialog("HTML Document","Loading...",3,self)
        dlg.Update(1)
        try:
            data = urllib.urlretrieve(path)
            file = open(data[0])
            dlg.Update(2)
            self.SetPage(file.read())
            i = string.rfind(path,"/")
            self.path = path[:i+1]
        except: wx.MessageBox("Invalid URL","Browser Error",wx.OK)
        dlg.Update(3)
        dlg.Destroy()

    def load_file(self,path):
        self.LoadPage(path)
        self.local = 1

###########################
## Some misc dialogs
###########################

class orpgMultiCheckBoxDlg(wx.Dialog):
    """ notes """
    def __init__(self, parent, opts, text, caption, selected=[], pos=wx.DefaultPosition):
        wx.Dialog.__init__(self, parent, wx.ID_ANY, caption, pos, wx.DefaultSize)
        sizers = { 'ctrls' : wx.BoxSizer(wx.VERTICAL), 'buttons' : wx.BoxSizer(wx.HORIZONTAL) }
        self.opts = opts
        self.list = wx.CheckListBox(self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize,opts)
        for s in selected: self.list.Check(s,1)
        sizers['ctrls'].Add(wx.StaticText(self, -1, text), 0, 0)
        sizers['ctrls'].Add(wx.Size(10,10))
        sizers['ctrls'].Add(self.list, 1, wx.EXPAND)
        sizers['buttons'].Add(wx.Button(self, wx.ID_OK, "OK"), 1, wx.EXPAND)
        sizers['buttons'].Add(wx.Size(10,10))
        sizers['buttons'].Add(wx.Button(self, wx.ID_CANCEL, "Cancel"), 1, wx.EXPAND)
        sizers['ctrls'].Add(sizers['buttons'], 0, wx.EXPAND)
        self.SetSizer(sizers['ctrls'])
        self.SetAutoLayout(True)
        self.Fit()
        self.Bind(wx.EVT_BUTTON, self.on_ok, id=wx.ID_OK)

    def on_ok(self,evt):
        checked = []
        for i in range(len(self.opts)):
            if self.list.IsChecked(i): checked.append(i)
        self.checked = checked
        self.EndModal(wx.ID_OK)

    def get_selections(self):
        return self.checked


class orpgMultiTextEntry(wx.Dialog):
    """ a dialog that takes two lists (labels and values) and creates a
        'label: value' style text edit control for each node in the dic"""
    def __init__(self,parent,tlist,vlist,caption,pos=wx.DefaultPosition):
        wx.Dialog.__init__(self,parent,-1,caption,pos,wx.DefaultSize)
        num = len(tlist)
        sizers = { 'ctrls' : wx.FlexGridSizer(num,2,5,0),
                    'buttons' : wx.BoxSizer(wx.HORIZONTAL) }
        #keys = mlist.keys()
        self.tlist = tlist
        self.vlist = vlist
        add_list = []
        ctrls = []
        for i in range(len(tlist)):
            add_list.append((wx.StaticText(self, -1, tlist[i]+": "),0,wx.ALIGN_CENTER_VERTICAL ))
            ctrls.append(wx.TextCtrl(self, 10, vlist[i]))
            add_list.append((ctrls[i],1,wx.EXPAND))
        self.ctrls = ctrls
        sizers['ctrls'].AddMany(add_list)
        sizers['ctrls'].AddGrowableCol(1)
        sizers['buttons'].Add(wx.Button(self, wx.ID_OK, "OK"), 1, wx.EXPAND)
        sizers['buttons'].Add(wx.Size(10,10))
        sizers['buttons'].Add(wx.Button(self, wx.ID_CANCEL, "Cancel"), 1, wx.EXPAND)
        width = 300
        (w,h) = ctrls[0].GetSizeTuple()
        h = h + 5
        height = ((num)*h)+35
        self.SetClientSizeWH(width,height)
        sizers['ctrls'].SetDimension(10,5,width-20,num*30)
        sizers['buttons'].SetDimension(10,(num*h)+5,width-20,25)
        self.Bind(wx.EVT_BUTTON, self.on_ok, id=wx.ID_OK)

    def on_ok(self,evt):
        for i in range(len(self.ctrls)): self.vlist[i] = self.ctrls[i].GetValue()
        self.EndModal(wx.ID_OK)

    def get_values(self):
        return self.vlist

class orpgScrolledMessageFrameEditor(wx.Frame):
    "class to implement wxScrolledMessageFrame with Find feature for the text of chatbuffer in a popup"
    def __init__(self, parent, msg, caption, pos = None, size = None):
        ID_ORPGTEXTCTRL = wx.NewId()
        ID_MATCHINSTRUCTION = wx.NewId()
        ID_MATCHINPUT = wx.NewId()
        ID_MATCHBUTTON = wx.NewId()
        ID_MATCHCASEINSTRUCTION = wx.NewId()
        ID_MATCHCASECHECKBOX = wx.NewId()
        ID_DEHTML = wx.NewId()
        wx.Frame.__init__(self, parent, -1, caption, pos=wx.DefaultPosition, size=(640,480))
        self.SetBackgroundColour(wx.WHITE)
        self.text = wx.TextCtrl(self, ID_ORPGTEXTCTRL, msg, wx.DefaultPosition, wx.DefaultSize, wx.TE_MULTILINE )
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.text, 1, wx.EXPAND)
        sizer1 = wx.BoxSizer(wx.HORIZONTAL)
        self.matchInstruction = wx.StaticText(self, ID_MATCHINSTRUCTION, "Text to search for: ")
        self.sizer.Add(self.matchInstruction, 0, wx.ALIGN_CENTER_VERTICAL)
        self.matchCaseInstruction = wx.StaticText(self, ID_MATCHCASEINSTRUCTION, "Match case:")
        sizer1.Add(self.matchCaseInstruction, 0, wx.ALIGN_CENTER_VERTICAL)
        self.matchCaseCheckBox = wx.CheckBox(self, ID_MATCHCASECHECKBOX, "")
        sizer1.Add(self.matchCaseCheckBox, 0, wx.ALIGN_CENTER_VERTICAL)
        self.matchInput = wx.TextCtrl(self, ID_MATCHINPUT, "")
        sizer1.Add(self.matchInput, 1, wx.EXPAND)
        self.sizer.Add(sizer1, 0, wx.EXPAND)
        sizer2 = wx.BoxSizer(wx.HORIZONTAL)
        self.matchButton = wx.Button(self, ID_MATCHBUTTON, "Find")
        self.Bind(wx.EVT_BUTTON, self.OnMatchMe, id=ID_MATCHBUTTON)
        sizer2.Add(self.matchButton, 1, wx.EXPAND)
        self.dehtmlButton = wx.Button(self, ID_DEHTML, "Remove HTML")
        self.Bind(wx.EVT_BUTTON, self.OnDeHTML, id=ID_DEHTML)
        sizer2.Add(self.dehtmlButton, 1, wx.EXPAND)
        self.cancel = wx.Button(self, wx.ID_CANCEL, "Cancel")
        self.Bind(wx.EVT_BUTTON, self.OnCloseMe, id=wx.ID_CANCEL)
        sizer2.Add(self.cancel, 1, wx.EXPAND)
        self.sizer.Add(sizer2, 0, wx.EXPAND)
        self.SetSizer(self.sizer)
        self.SetAutoLayout(True)
        self.Fit()
        #self.Bind(wx.EVT_SIZE, self.OnSize)

        # current position
        self.matchPosition = 0
        # former position
        self.matchPositionOld = 0

    def OnDeHTML(self, event):
        text = re.sub( "\<[^<]*?\>", "", self.text.GetValue() )
        self.text.SetValue(text)

    def OnMatchMe(self, event):
        # match case sensitive
        if self.matchCaseCheckBox.GetValue() == 1:
            textValue = self.text.GetValue()
            matchValue = self.matchInput.GetValue()
        # match case insensitive
        else:
            textValue = string.upper(self.text.GetValue())
            matchValue = string.upper(self.matchInput.GetValue())

        # continue search from insertion point instead of top
        self.matchPosition = self.matchPositionOld = self.text.GetInsertionPoint()

        # find search string in chatbuffer
        self.matchPosition = string.find(textValue[self.matchPositionOld:], matchValue)
        # cumulate position for substring matching in continuing search
        self.matchPositionOld = self.matchPositionOld + self.matchPosition

        # if match was found
        if self.matchPosition >= 0:
            # highlight(select) match
            self.text.SetSelection(self.matchPositionOld, self.matchPositionOld + len(matchValue))
            # continue search from end of match
            self.text.SetInsertionPoint(self.matchPositionOld + len(matchValue))
        # if match was not found, but match exists somewhere in buffer, start from top
        elif string.find(textValue, matchValue) >= 0:
            self.text.SetInsertionPoint(0)
            self.OnMatchMe(self)

    def OnCloseMe(self, event):
        self.Close(True)

    def OnCloseWindow(self, event):
        self.Destroy()

class orpgProgressDlg(wx.Dialog):
    def __init__(self, parent,  title="", text="", range=10 ):
        wx.Dialog.__init__(self, parent, -1, title, size= wx.Size(200,75))
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.text = wx.StaticText( self, -1, text)
        self.gauge = wx.Gauge(self,-1,range)
        self.sizer.Add(self.text,1,wx.ALIGN_CENTER | wx.EXPAND)
        self.sizer.Add(self.gauge,1,wx.ALIGN_CENTER | wx.EXPAND)
        (w,h) = self.GetClientSizeTuple()
        self.sizer.SetDimension(10,10,w-20,h-20)

    def Update(self,pos,text=None):
        self.gauge.SetValue(pos)
        if text: self.text.SetLabel(text)

#########################
#status frame window
#########################
class status_bar(wx.StatusBar):
    def __init__(self, parent):
        wx.StatusBar.__init__(self, parent, -1)
        GENERAL_MENU = 1
        URL_MENU = 2
        self.parent = parent
        self.connect_status = "Not Connected"
        self.urlis = ""
        self.window = 1
        self.menu = wx.Menu("Switch layout to...")
        item = wx.MenuItem(self.menu, wx.ID_ANY, "General", "General", wx.ITEM_CHECK)
        self.Bind(wx.EVT_MENU, self.OnM_SwitchlayouttoGeneral, item)
        self.menu.AppendItem(item)
        item = wx.MenuItem(self.menu, wx.ID_ANY, "Url Display", "Url Display", wx.ITEM_CHECK)
        self.Bind(wx.EVT_MENU, self.OnM_SwitchlayouttoUrlDisplay, item)
        self.menu.AppendItem(item)

        #menu = [["Switch layout to..."],
        #     ["  General"],
        #     ["  Url Display"]]
        #self.menu = MenuEx(self, menu)

        self.Bind(wx.EVT_RIGHT_DOWN, self.onPopup)
        self.widths = [-1,200]
        (msgwidth,msgheight) = self.GetTextExtent(`self.connect_status`)
        #parent.SetClientSize(wx.Size(450,msgheight+8))
        #self.SetClientSize(wx.Size(450,msgheight+7))
        self.SetFieldsCount(2)
        self.timer = wx.Timer(self, wx.NewId())
        self.Bind(wx.EVT_TIMER, self.Notify)
        self.timer.Start(3000)

    def onPopup(self, evt):
        self.PopupMenu(self.menu)

    def OnM_SwitchlayouttoUrlDisplay(self, evt):
        self.window = 2
        self.bar1()

    def OnM_SwitchlayouttoGeneral(self, evt):
        self.window = 1
        self.bar0()

    def set_connect_status(self,connect):
        self.connect_status = connect

    def Notify(self, event):
        if self.window == 1: self.bar0()
        elif self.window == 2: self.bar1()
        pass

    def bar1(self):
        self.SetFieldsCount(1)
        self.widths = [-1]
        self.SetStatusWidths(self.widths)
        self.SetStatusText("URL: " + self.urlis, 0)

    def bar0(self):
        self.SetFieldsCount(2)
        self.widths = [-1,200]
        t = time.gmtime(time.time())
        st = time.strftime("GMT: %d-%b-%Y  %I:%M:%S", t)
        #(x,y) = self.GetTextExtent(self.connect_status)
        #self.widths[0] = x+10
        (x,y) = self.GetTextExtent(st)
        self.widths[1] =  x+10
        self.SetStatusWidths(self.widths)
        self.SetStatusText(self.connect_status, 0)
        self.SetStatusText(st, 1)

    def set_url(self, url):
        self.urlis = url

    def __del__(self):
        self.timer.Stop()
        del self.timer

#####################
## Some misc utilties for the GUI
#####################

def do_progress_dlg(parent,title,text,range):
    " Returns a new progress dialog"
    if wx.Platform == '__WXMSW__':
        dlg = orpgProgressDlg(parent,title,text,range)
        dlg.Centre()
        dlg.Show(1)
        dlg.Raise()
    else: dlg = wx.ProgressDialog(title,text,range,parent)
    return dlg

def parseXml_with_dlg(parent,s,ownerDocument=None):
    "Parse xml with progress dialog"
    dlg = do_progress_dlg(parent,"XML Parser","Reading Configuration Files...",2)
    #dlg.Update(1)
    doc = component.get('xml').parseXml(s)
    dlg.Update(1,"Done.")
    dlg.Destroy()
    return doc

def createMaskedButton( parent, image, tooltip, id, mask_color=wx.WHITE, image_type=wx.BITMAP_TYPE_GIF ):
    gif = wx.Image( image, image_type, ).ConvertToBitmap()
    mask = wx.Mask( gif, mask_color )
    gif.SetMask( mask )
    btn = wx.BitmapButton( parent, id, gif )
    btn.SetToolTip( wx.ToolTip( tooltip ) )
    return btn
