import paho.mqtt.client as pmqtt
import paho.mqtt.subscribe as smqtt
import json
import time
import logging

class mqtt:

    def __init__(self, broker: str, port=1883):
        self.client = ""
        self.broker = broker
        self.port = port
        self.connect()

    def connect(self):
        self.client = pmqtt.Client()
        self.client.connect(host=self.broker, port=self.port)
    
    def publish(self, topic:str, message:str):
        if topic == "" or message == "":
            raise Exception("Topic and Message required")
        published = self.client.publish(topic, message)
        while not published.is_published():
            time.sleep(0.5)
            print("published:", published.rc)
    
    def subscribe(self, topics:[], cb:callable):
        if topics == []:
            raise Exception("Need a topic to listen to")
        logging.debug("Starting the MQTT subscriber")
        smqtt.callback(cb, topics, hostname=self.broker)
        #subscribed.callback(cb,)
        #self.client.subscribe(topic)
        #self.client.on

