from orpg.orpgCore import *
from orpg.orpg_wx import *


class orpgSound(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, -1)
        self.parent = parent

        self.log = component.get("log")
        self.settings = component.get('settings')

        self.log.log("Enter orpgSound", ORPG_DEBUG)

        # Create some controls
        try:
            self.mc = wx.media.MediaCtrl(self, wx.ID_ANY, size=(1,1))
            self.OldPlayer = False
            self.Bind(wx.media.EVT_MEDIA_LOADED, self.OnMediaLoaded)
            self.log.log("wx.media Used", ORPG_DEBUG)
        except NotImplementedError:
            self.OldPlayer = True
            self.log.log("Old Player Used", ORPG_DEBUG)
        else:
            btn2 = wx.Button(self, -1, "Play")
            self.Bind(wx.EVT_BUTTON, self.OnPlay, btn2)
            self.playBtn = btn2
            self.playBtn.Disable()

            btn3 = wx.Button(self, -1, "stop")
            self.Bind(wx.EVT_BUTTON, self.OnStop, btn3)
            self.stopBtn = btn3

            self.playList = wx.Choice(self, wx.ID_ANY)
            self.playDict = {}

            self.pslider = wx.Slider(self, wx.ID_ANY, 0, 0, 100, size=wx.Size(100, -1))
            self.Bind(wx.EVT_SLIDER, self.onSeek, self.pslider)

            self.pos = wx.StaticText(self, wx.ID_ANY, "Position:")

            self.vol = wx.StaticText(self, wx.ID_ANY, "Volume:")
            self.vslider = wx.Slider(self, wx.ID_ANY, 100, 0, 100, size=wx.Size(50, -1))
            self.Bind(wx.EVT_SLIDER, self.onVol, self.vslider)

            self.log.log("Buttons Created", ORPG_DEBUG)

            self.loopSound = False
            self.seeking = False
            self.lastlen = 0

            # setup the layout
            sizer = wx.GridBagSizer(hgap=1, vgap=1)
            sizer.Add(self.mc, (0,20))
            sizer.Add(self.playList, (0,0), span=(1,2))
            sizer.Add(btn2, (0,2))
            sizer.Add(btn3, (0,3))
            sizer.Add(self.pos, (1,0), flag=wx.ALIGN_CENTER)
            sizer.Add(self.pslider, (1,1), flag=wx.EXPAND)
            sizer.Add(self.vol, (1,2), flag=wx.ALIGN_CENTER)
            sizer.Add(self.vslider, (1,3), flag=wx.EXPAND)
            sizer.AddGrowableCol(0)
            sizer.AddGrowableCol(3)
            sizer.SetEmptyCellSize((0,0))

            self.SetSizer(sizer)
            self.SetAutoLayout(True)

            self.log.log("Sizer Set", ORPG_DEBUG)

            self.Fit()

            self.Bind(wx.EVT_CHOICE, self.PlaySelected, self.playList)
            self.Bind(wx.EVT_CLOSE, self.OnClose)
            self.timer = wx.Timer(self, wx.NewId())
            self.Bind(wx.EVT_TIMER, self.OnTimer)
            self.timer.Start(100)

            self.log.log("Events Bound", ORPG_DEBUG)

        self.log.log("Exit orpgSound", ORPG_DEBUG)

    def play(self, sound_file, type="local", loop_sound=False):
        self.log.log("Enter orpgSound->play(self, sound_file, type, loop_sound)", ORPG_DEBUG)

        if self.OldPlayer:
            if wx.Platform == '__WXMSW__':
                import winsound
                self.play_windows(sound_file.replace('&amp;', '&'))
            elif wx.Platform == '__WXGTK__':
                self.play_unix(sound_file.replace('&amp;', '&'))
        else:
            self.loopSound = loop_sound
            self.LoadSound(sound_file.replace('&amp;', '&'), type)

        self.log.log("Exit orpgSound->play(self, sound_file, type, loop_sound)", ORPG_DEBUG)

    def play_windows(self,sound_file):
        self.log.log("Enter orpgSound->play_windows(self,sound_file)", ORPG_DEBUG)

        winsound.PlaySound(sound_file, winsound.SND_FILENAME)

        self.log.log("Exit orpgSound->play_windows(self,sound_file)", ORPG_DEBUG)

    def play_unix(self, sound_file):
        self.log.log("Enter orpgSound->play_unix(self, sound_file)", ORPG_DEBUG)

        unix_player = self.settings.get_setting('UnixSoundPlayer')
        if unix_player != '':
            os.system(unix_player + " " + sound_file)

        self.log.log("Exit orpgSound->play_unix(self, sound_file)", ORPG_DEBUG)

    def onSeek(self, evt):
        self.log.log("Enter orpgSound->onSeek(self, evt)", ORPG_DEBUG)

        offset = self.pslider.GetValue()
        self.mc.Seek(offset)

        self.log.log("Exit orpgSound->onSeek(self, evt)", ORPG_DEBUG)

    def PlaySelected(self, evt):
        self.log.log("Enter orpgSound->PlaySelected(self, evt)", ORPG_DEBUG)

        name = self.playList.GetStringSelection()
        info = self.playDict[name]
        sound_file = info[0]
        pos = info[1]

        self.mc.LoadURI(sound_file)

        pane = self.parent._mgr.GetPane("Sound Control Toolbar")
        pane.window.SetInitialSize()
        pane.BestSize(pane.window.GetEffectiveMinSize() + (0, 1))
        self.parent._mgr.Update()

        if pos > 0:
            self.seeking = True
            wx.CallAfter(self.mc.Pause)

        self.log.log("Exit orpgSound->PlaySelected(self, evt)", ORPG_DEBUG)

    def LoadSound(self, sound_file, type="local"):
        self.log.log("Enter orpgSound->LoadSound(self, sound_file, type)", ORPG_DEBUG)

        if self.mc.GetState() == wx.media.MEDIASTATE_PLAYING:
            pos = self.mc.Tell()
            len = self.mc.Length()
            self.mc.Stop()
            if (len-pos) <= 2000:
                pos = 0
            pname = self.playList.GetStringSelection()
            self.playDict[pname][1] = pos

        (path, name) = os.path.split(sound_file)
        if type != "local":
            self.mc.LoadURI(sound_file)
        else:
            self.mc.Load(sound_file)

        if not self.playDict.has_key(name):
            self.playList.Append(name)

        pane = self.parent._mgr.GetPane("Sound Control Toolbar")
        pane.window.SetInitialSize()
        pane.BestSize(pane.window.GetEffectiveMinSize() + (0, 1))
        self.parent._mgr.Update()

        self.playDict[name] = [sound_file, 0]
        self.playList.SetStringSelection(name)

        self.log.log("Exit orpgSound->LoadSound(self, sound_file, type)", ORPG_DEBUG)
        return

    def OnMediaLoaded(self, evt):
        self.log.log("Enter orpgSound->OnMediaLoaded(self, evt)", ORPG_DEBUG)

        self.mc.Play()
        self.playBtn.Enable()

        self.log.log("Exit orpgSound->OnMediaLoaded(self, evt)", ORPG_DEBUG)

    def OnPlay(self, evt):
        self.log.log("Enter orpgSound->OnPlay(self, evt)", ORPG_DEBUG)

        self.mc.Play()

        self.log.log("Exit orpgSound->OnPlay(self, evt)", ORPG_DEBUG)

    def OnStop(self, evt):
        self.log.log("Enter orpgSound->OnStop(self, evt)", ORPG_DEBUG)

        self.loopSound = False
        self.mc.Stop()

        self.log.log("Exit orpgSound->OnStop(self, evt)", ORPG_DEBUG)

    def OnClose(self, evt):
        self.log.log("Enter orpgSound->OnClose(self, evt)", ORPG_DEBUG)

        self.timer.Stop()
        del self.timer

        self.log.log("Exit orpgSound->OnClose(self, evt)", ORPG_DEBUG)

    def __del__(self):
        self.timer.Stop()

    def onVol(self, evt):
        self.log.log("Enter orpgSound->onVol(self, evt)", ORPG_DEBUG)

        vol = float(self.vslider.GetValue())/100
        self.mc.SetVolume(vol)

        self.log.log("Exit orpgSound->onVol(self, evt)", ORPG_DEBUG)

    def OnTimer(self, args):
        if not self.OldPlayer:
            if self.mc.GetState() == wx.media.MEDIASTATE_PLAYING and not self.stopBtn.IsEnabled():
                self.stopBtn.Enable()
            elif self.mc.GetState() != wx.media.MEDIASTATE_PLAYING and self.stopBtn.IsEnabled():
                self.stopBtn.Disable()

            if self.mc.Length() > 0 and self.lastlen != self.mc.Length():
                self.pslider.SetRange(0, self.mc.Length())
                self.lastlen = self.mc.Length()

            if not self.seeking:
                self.pslider.SetValue(self.mc.Tell())

            if self.mc.GetState() != wx.media.MEDIASTATE_PLAYING and self.loopSound:
                self.mc.Play()

            if self.seeking:
                name = self.playList.GetStringSelection()
                info = self.playDict[name]

                if self.mc.Tell() >= info[1]:
                    self.seeking = False

                else:
                    self.pslider.SetValue(info[1])
                    wx.CallAfter(self.onSeek, None)

        elif self.stopBtn.IsShown():
            self.playBtn.Hide()
            self.stopBtn.Hide()
        return

class SoundFrame(wx.Frame):
    def __init__(self, openrpg):
        wx.Frame.__init__(self, None, title="Sound Control Toolbar", style=wx.CAPTION | wx.SYSTEM_MENU | wx.STAY_ON_TOP)

        self.soundCtrl = orpgSound(self, openrpg)

        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(self.soundCtrl, 1, wx.EXPAND)
        self.SetSizer(sizer)
        self.SetSizer(sizer)
        self.SetAutoLayout(True)
        self.Fit()



class BlankApp(wx.App):
    def OnInit(self):
        self.frame = SoundFrame()
        self.frame.Show()
        self.SetTopWindow(self.frame)
        return True

    def OnChar(self, event):
        #Not sure how to determin if only Tab or Shift Tab was used to initiate
        self.tabgroup.GoNext( self.frame1.FindFocus() )

if __name__ == "__main__":
    app = BlankApp(0)
    app.MainLoop()
