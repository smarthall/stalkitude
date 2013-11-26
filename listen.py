#!/usr/bin/env python

import mosquitto
import json
import Image
from StringIO import StringIO
import wx
import threading
import urllib2
from motionless import LatLonMarker, DecoratedMap

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

markers = {}

def on_message(mosq, obj, msg):
    data = json.loads(msg.payload)
    markers[msg.topic] = LatLonMarker(data['lat'], data['lon'])
    dmap = DecoratedMap(size_x=320, size_y=240)
    for m in markers.keys():
        dmap.add_marker(markers[m])
    url = dmap.generate_url()
    img_file = urllib2.urlopen(url)
    imgdata = img_file.read()
    img = Image.open(StringIO(imgdata))
    ui.newFrame(img)

ui = UIThread()
ui.start()

client = mosquitto.Mosquitto("test-client")
client.tls_set('ca.crt')
client.username_pw_set('testing', 'c1rvyiZhoDgn')
client.connect("mqtt.tildaslash.com")

client.on_message = on_message

while not ui._started:
    pass

client.subscribe("mqttitude/+/+", 0)

while ui._app.IsMainLoopRunning():
  client.loop()

