import sys
import time
import qolsys_socket, mqtt_client
#import threading
import json
import logging
from paho.mqtt.client import MQTTMessage

class MQTTSubscriber:
    def __init__(self, broker="", qolsys:qolsys_socket.qolsys=None, port=1883, topics=[]):
        self.broker = broker
        self.qolsys = qolsys
        self.port = port
        self.topics = topics
        self._arming_types = ["away", "stay", "disarm"]


        logging.debug(("MQTT Subscriber: ", self.broker, ":", self.port, ":", self.topics))
        mqtt_sub = mqtt_client.mqtt(self.broker, self.port)
        mqtt_sub.subscribe(topics=self.topics, cb=self.mqtt_request_received)

    def mqtt_request_received(self, client, userdata, message:MQTTMessage):
        '''Runs when a MQTT event is received on the request topic
        
            Parameters:
                data: json object containing the request to send to the qolsys panel
            
            Expected JSON Message:
                Required:
                    event                   INFO, ARM, DISARM
                    token                   Qolsys IQ Panel token

                Optional
                    usercode                Required if disarming
                    partition_id            Required if arming or disarming.  0 is a good value if you don't know what to use
                    arm_type                Required if arming.  Options are "away" or "stay"
                '''

        logging.debug(("client:", client))
        logging.debug(("userdata:", userdata))
        logging.debug(("message:", message))
        payload = message.payload
        logging.debug(("payload:", payload))
        payload_json = {}
        event_type = ""

        try:
            if json.loads(payload):
                payload_json = json.loads(payload)
                logging.debug(("payload_json:", payload_json))
        except:
            logging.debug(("Error converting to JSON:", sys.exc_info()))
            logging.debug(("Not JSON:", payload))
        
        try:
            event_type = payload_json["event"]
            logging.debug(("event:", event_type))
        except:
            logging.error(('Unable to find "event"', payload_json))
            #raise("Unable to receive MQTT requests")

        if event_type != "":
            token = payload_json["token"] if "token" in payload_json else None
            usercode = payload_json["usercode"] if "usercode" in payload_json else None
            partition_id = payload_json["partition_id"] if "partition_id" in payload_json else None
            arm_type = payload_json["arm_type"] if "arm_type" in payload_json else None
            logging.debug(("event:", event_type,"usercode:", usercode, "partition_id", partition_id, "arm_type", arm_type))
            if token == None:
                #raise("Token required for anything you want to do")
                logging.error("No token provided.  Token is required for anything you want to do with the Qolsys panel")
            else:
                if event_type == "INFO":
                    self.qolsys_status(self.qolsys, token)
                
                if event_type == "ARM":
                    if partition_id is None or arm_type is None:
                        logging.error(("arm_type and partition_id are required"))
                    else:                    
                        self.qolsys_arm(self.qolsys, token, arm_type, partition_id)

                if event_type == "DISARM":
                    arm_type = "disarm"
                    if partition_id is None or arm_type is None or usercode is None:
                        logging.error(("arm_type, partition_id, and usercode are required"))
                    else:                    
                        self.qolsys_arm(self.qolsys, token, "disarm", partition_id, usercode)

    def qolsys_arm(self, qolsys, token:str, arming_type:str, partition_id:int, usercode=""):
        if not arming_type in self._arming_types:
            raise("Invalid arm command")

        arm_type = ""

        if arming_type.lower() == 'away':
            arm_type = "ARM_AWAY"
        elif arming_type.lower() == 'stay':
            arm_type = "ARM_STAY"
        elif arming_type.lower() == 'disarm':
            arm_type = "DISARM"
        else:
            raise("Invalid arm command")

        armString    = {
                            "partition_id": partition_id,
                            "action":       "ARMING",
                            "arming_type":  arm_type,
                            "version":      0,
                            "nonce":        "qolsys",
                            "source":       "C4",
                            "version_key":  1,
                            "source_key":   "C4",
                            "token":        token
                        }

        #Disarm requires a usercode
        if arming_type.lower() == "disarm":
            armString.update({"usercode":usercode})

        try:
            logging.debug(("armString:", armString))
            qolsys.send_to_socket(armString)
        except socket.error:
            logging.error("Could not send arm command to qolsys socket")

    def qolsys_status(self, qolsys, token):
        statusString    = {
                            "nonce":        "qolsys",
                            "action":       "INFO",
                            "info_type":    "SUMMARY",
                            "version":      0,
                            "source":       "C4",
                            "token":        token,
                        }

        try:
            qolsys.send_to_socket(statusString)
        except:
            logging.error('Could not send status request to qolsys socket')