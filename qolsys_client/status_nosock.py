import sys
import time
import qolsys_socket
#import threading
import mqtt_client
import json
import logging

################################################################################
# Code
args = {}

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
        logging.error('Could not send to socket')


def data_received(data:dict):
    ''' This is where any json data coming from the qolsys panel will be sent.  In this case I have the data being published to a mqtt topic, but you can do what you want.
    
        Parameters:
            data: json object containing the output from the qolsys panel'''

    if "mqtt-broker" in args:
        mqtt_broker = args["mqtt-broker"]
        mqtt_port = args["mqtt-port"] if "mqtt-port" in args else 1883
        topic = "qolsys"
        jdata = json.loads(data)
        event_type = jdata["event"]
        if event_type == "INFO":
            topic += "/info"
        if event_type == "ZONE_EVENT":
            topic += "/zone_event"
        if event_type == "ZONE_UDPATE":
            topic += "/zone_update"

        mq = mqtt_client.mqtt(mqtt_broker, mqtt_port)
        mq.publish(topic, data)
    else:
        print(data)
    
def main():
    logging.basicConfig(level=logging.WARNING, format='%(asctime)s: %(levelname)s: %(module)s: %(funcName)s: %(lineno)d: %(message)s')
    logging.debug(("Command line arguments:", sys.argv[1:]))
    args = get_command_line_args()

    #Deal with some arguments that stop execution
    if "help" in args:
        help()
    if not "token" in args:
        print("Qolsys IQ 2 Panel token required")
        sys.exit()
    if not "host" in args:
        print("Qolsys IQ 2 Panel IP address or hostname required")
        sys.exit()

    token, host = args["token"], args["host"]
    port = int(args["port"]) if "port" in args else 12345
    timeout = int(args["timeout"]) if "timeout" in args else 86400

    logging.debug("Creating qolsys_socket")
    qolsys = qolsys_socket.qolsys()

    qolsys.create_socket(hostname=host, port=port, token=token, cb=data_received, timeout=timeout)

    logging.debug("main: sock created")

    logging.debug("doing the info check")
    qolsys_status(qolsys, token)

def get_command_line_args() -> dict:
    #args = {}
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
            
            Optional:
                --mqtt-broker   IP address or hostname of the MQTT broker
                --mqtt-port     MQTT broker port to connect to (default is 1883)
            """
    print(help_text)
    sys.exit()

if __name__ == "__main__":
    main()