#!/usr/bin/env python

import mosquitto
import json
from motionless import LatLonMarker, DecoratedMap

class LocationListener(mosquitto.Mosquitto):
    def __init__(self):
        self._markers = {}
        mosquitto.Mosquitto.__init__(self, "stalkitude")
        self.on_connect = self._ll_on_connect
        self.on_message = self._ll_on_message
        self.on_update = None

    def _ll_on_connect(self, mosq, obj, rc):
        self.subscribe("mqttitude/+/+", 0)

    def _ll_on_message(self, mosq, obj, msg):
        data = json.loads(msg.payload)
        self._markers[msg.topic] = LatLonMarker(data['lat'], data['lon'])
        dmap = DecoratedMap(size_x=320, size_y=240)
        for m in self._markers.keys():
            dmap.add_marker(self._markers[m])
        if self.on_update is not None:
            self.on_update(dmap.generate_url())

