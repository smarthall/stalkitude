#!/usr/bin/env python

import wx
import threading

class MapFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, wx.ID_ANY, "Map", size=(320, 240))
        self._newFrame = False
        self._curFrame = None
        self._framelock = threading.Lock()
        self.Bind(wx.EVT_IDLE, self.updFrame)

    def updFrame(self, evt):
        self._framelock.acquire()
        if self._newFrame and self._curFrame is not None:
            wximage = wx.EmptyImage(320, 240)
            wximage.SetData(self._curFrame.convert('RGB').tostring())
            bitmap = wximage.ConvertToBitmap()
            window_list = self.GetChildren()
            for w in window_list:
                w.Destroy()
            wx.StaticBitmap(self,-1,bitmap, (0, 0))
            self._newFrame = False
        self._framelock.release()

    def newFrame(self, frame):
        self._framelock.acquire()
        self._newFrame = True
        self._curFrame = frame
        self._framelock.release()

class UIThread(threading.Thread):
    def __init__(self):
        self._started = False
        threading.Thread.__init__(self)

    def run(self):
        self._app = wx.PySimpleApp()
        self._map = MapFrame()
        self._map.Show()
        self._started = True
        self._app.MainLoop()

    def newFrame(self, frame):
        self._map.newFrame(frame)
        self._app.WakeUpIdle()

