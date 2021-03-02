import sys
import time
import qolsys_socket
import asyncio
import threading
import mqtt_client
import json

################################################################################
# Code

token = "shw9s8"

def qolsys_status(qolsys, token):
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
        print('Could not send to socket')

def data_received(data):
    # print(data)
    topic = ""
    jdata = json.loads(data)
    event_type = jdata["event"]
    if event_type == "INFO":
        topic = "qolsys/info"
    if event_type == "ZONE_EVENT" or event_type == "ZONE_UDPATE":
        topic = "qolsys/zone_event"
    mq = mqtt_client.mqtt("192.168.10.4")
    mq.publish(topic, data)
    print(mq)

def main():

    qolsys = qolsys_socket.qolsys()
    qolsys.create_socket(hostname="192.168.10.34", port=12345, token=token, cb=data_received, timeout=4)

    print("main: sock created")
    print("main: creating mqtt client")


    print("doing the info check")
    qolsys_status(qolsys, token)
    time.sleep(2)
    qolsys_status(qolsys, token)
    time.sleep(2.9)
    qolsys_status(qolsys, token)
    
if __name__ == "__main__":
    main()