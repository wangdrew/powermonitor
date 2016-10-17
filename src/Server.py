__author__ = 'andrewwang'

import requests
import copy
import time
import json
import paho.mqtt.client as mqtt
import paho.mqtt.publish as mqtt_publish
from Queue import Queue
import thread
from PowerMetric import PowerMetric

MqttBrokerHost = "wangdrew.net"     # env var
MqttBrokerPort = 1883
KairosDbHost = "localhost"
KairosDbPort = 8083

class SensorServer:
    def __init__(self):
        self.mqttMessages = Queue()

    def startMqttSubscriber(self, mqttMessages):
        self.MqttSubThread = MqttSubscriber(mqttMessages)
        self.MqttSubThread.run()

    def run(self):
        # start mqtt subscriber
        thread.start_new_thread(self.startMqttSubscriber, (self.mqttMessages,))

        while True:
            if not self.mqttMessages.empty():
                msg = self.mqttMessages.get(False)
                print 'On queue %s' % msg

                # Give to exporters


class MqttSubscriber:
    def __init__(self, sharedqueue):
        self.mqttMessages = sharedqueue

    def on_connect(self, client, userdata, flags, rc):
        print("Connected to MQTT broker "+str(rc))
        client.subscribe("power")

    def on_message(self, client, userdata, msg):
        print(msg.topic+" "+str(msg.payload))
        self.mqttMessages.put(PowerMetric.from_json(msg.payload))

    def run(self):
        try:
            client = mqtt.Client()
            client.on_connect = self.on_connect
            client.on_message = self.on_message

            client.connect(MqttBrokerHost, MqttBrokerPort, 60)
            client.loop_forever()
        except:
            raise

            import traceback
            print traceback.format_exc()


if __name__ == "__main__":
    server = SensorServer()
    server.run()
