#!/usr/bin/env python

import argparse
import urllib2
import Image
from cStringIO import StringIO

import locationlistener
import ui

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

gui = ui.UIThread()
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

