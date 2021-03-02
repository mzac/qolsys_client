import paho.mqtt.client as pmqtt
import json
import time

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
        # if json.dumps(message):
        #     message = json.dumps((message).encode())
        # else:
        #     message = message.encode()
        published = self.client.publish(topic, message)
        while not published.is_published():
            time.sleep(0.5)
            print("published:", published.rc)