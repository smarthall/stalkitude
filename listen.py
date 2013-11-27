#!/usr/bin/env python

import argparse
import Image
from StringIO import StringIO
import wx
import threading
import urllib2
from motionless import LatLonMarker, DecoratedMap
import locationlistener

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

def on_update(url):
    img_file = urllib2.urlopen(url)
    imgdata = img_file.read()
    img = Image.open(StringIO(imgdata))
    gui.newFrame(img)

parser = argparse.ArgumentParser(description='Displays MQTTitude on a map')
parser.add_argument('-u', '--username', help='Username for the MQTT server')
parser.add_argument('-P', '--password', help='Password for the MQTT server')
parser.add_argument('-c', '--cafile', help='The CA certificate for the MQTT server')
parser.add_argument('-H', '--host', default='127.0.0.1', help='The hostname of the MQTT server')
parser.add_argument('-p', '--port', default=1883, type=int, help='The port of the MQTT server')
args = vars(parser.parse_args())

gui = UIThread()
gui.start()

client = locationlistener.LocationListener()

if args['cafile'] is not None:
    client.tls_set(args['cafile'])

if args['username'] is not None:
    client.username_pw_set(args['username'], args['password'])
client.connect(args['host'], port=args['port'])

client.on_update = on_update

while not gui._started:
    pass

client.subscribe("mqttitude/+/+", 0)

while gui._app.IsMainLoopRunning():
  client.loop()

