import sys
import time
import json
import logging
from paho.mqtt.client import MQTTMessage
import qolsys_socket, mqtt_client
from mqtt_subscriber import MQTTSubscriber

################################################################################
# Code
#args = {}

def qolsys_data_received(data:dict):
    ''' This is where any json data coming from the qolsys panel will be sent.
    In this case I have the data being published to a mqtt topic, but you can do what you want.
    
        Parameters:
            data: json object containing the output from the qolsys panel'''

    args = get_command_line_args()
    if "mqtt-broker" in args:
        mqtt_broker = args["mqtt-broker"]
        mqtt_port = args["mqtt-port"] if "mqtt-port" in args else 1883
        topic = "qolsys/"
        jdata = json.loads(data)
        event_type = jdata["event"]
        if event_type == "INFO":
            topic += "info"
        if event_type == "ZONE_EVENT":
            topic += "zone_event"
        if event_type == "ZONE_UDPATE":
            topic += "zone_update"

        logging.debug(("publishing " + event_type + " event to: " + topic))
        mq = mqtt_client.mqtt(mqtt_broker, mqtt_port)
        mq.publish(topic, data)
    else:
        print(data)
    
def main():
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s: %(levelname)s: %(module)s: %(funcName)s: %(lineno)d: %(message)s')
    logging.debug(("Command line arguments:", sys.argv[1:]))
    args = get_command_line_args()

    #Deal with some arguments that stop execution
    if "help" in args:
        help()
    if not "token" in args:
        print("Qolsys IQ 2 Panel token required")
        help()#sys.exit()
    if not "host" in args:
        print("Qolsys IQ 2 Panel IP address or hostname required")
        help()#sys.exit()

    token, host = args["token"], args["host"]
    port = int(args["port"]) if "port" in args else 12345
    timeout = int(args["timeout"]) if "timeout" in args else 86400
    mqtt_broker = args["mqtt-broker"] if "mqtt-broker" in args else None
    mqtt_port = args["mqtt-port"] if "mqtt-port" in args else 1883
    topics = [] #args["topics"] if "topics" in args else ["qolsys/requests"]
    if args["topics"]:
        topic_data = str(args["topics"])
        logging.debug(("topics arg:", topic_data))
        if topic_data.find(",") > 0:
            topic_array = args["topics"].split(",")
            logging.debug(("topic_array:", topic_array))
            for t in topic_array:
                logging.debug(("t:", t))
                topics.append(t)
        else:
            topics.append(topic_data)
    else:
        raise("No topics")

    
    logging.debug("Creating qolsys_socket")
    qolsys = qolsys_socket.qolsys()

    qolsys.create_socket(hostname=host, port=port, token=token, cb=qolsys_data_received, timeout=timeout)

    logging.debug("main: qolsys_socket created")

    #logging.debug("doing the info check on startup")
    #qolsys_status(qolsys, token)

    #qolsys_arm(qolsys,token,"stay")
    if mqtt_broker:
        mqtt_sub = MQTTSubscriber(broker=mqtt_broker, port=mqtt_port, qolsys=qolsys, topics=topics)
    else:
        logging.info("No MQTT Broker.  Only getting status events from panel")
   

def get_command_line_args() -> dict:
    args = {}
    for arg in sys.argv[1:]:
        arg_name = ""
        arg_value = ""
        arg_name = arg.split("=",1)[0]
        arg_name = arg_name.split("--",1)[1]
        try:
            arg_value = arg.split("=",1)[1]
        except:
            arg_value = ""
        logging.debug(("argument name: ", arg_name, " | ", arg_value))
        this_arg = { arg_name: arg_value }
        args.update(this_arg)
    logging.debug(("all arguments: ", args))
    return args

def help():
    help_text = """
        Parameters:
            Required:
                --host          IP address or hostname of the Qolsys IQ 2(+) Panel
                --port          Port to connect on the Qolsys panel.  Usually 12345
                --timeout       Timeout (seconds) to wait after last data sent/received from the panel before disconnecting.  Default will be one day.
                --token         Token from the Qolsys panel
                --usercode      (UNUSED) If you want to use disarm, you need to supply a usercode
            
            Optional:
                --mqtt-broker   IP address or hostname of the MQTT broker
                --mqtt-port     MQTT broker port to connect to (default is 1883)
                --topics        A list (array) of topics to subscribe to for qolsys event requests e.g. --topics=["qolsys/requests"] (Default)
            
            Usage:
                python3 main.py --host=192.168.1.123 --port=12345 --token=yourtoken --timeout=86400 --mqtt-broker=192.168.1.2 --mqtt-port=1883 --topics=["qolsys/requests"]
            

            """
    print(help_text)
    sys.exit()

if __name__ == "__main__":
    main()