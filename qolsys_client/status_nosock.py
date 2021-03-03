import sys
import time
import qolsys_socket
import threading
import mqtt_client
import json
import logging

################################################################################
# Code

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
    # print(data)
    topic = "qolsys"
    jdata = json.loads(data)
    event_type = jdata["event"]
    if event_type == "INFO":
        topic += "/info"
    if event_type == "ZONE_EVENT":
        topic += "/zone_event"
    if event_type == "ZONE_UDPATE":
        topic += "/zone_update"

    mq = mqtt_client.mqtt("192.168.10.4")
    mq.publish(topic, data)
    
def main():
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s: %(levelname)s: %(module)s: %(funcName)s: %(lineno)d: %(message)s')
    logging.debug(("Command line arguments:", sys.argv[1:]))
    args = get_command_line_args()
    token, host = args["token"], args["host"]
    if args["port"]:
        port = args["port"]
    else:
        port = 1883
    if args["timeout"]:
        timeout = args["timeout"]
    else:
        #Setting a default of one day timeout
        timeout = 86400
    logging.debug("Creating qolsys_socket")
    qolsys = qolsys_socket.qolsys()

    qolsys.create_socket(hostname=host, port=port, token=token, cb=data_received, timeout=4)

    logging.debug("main: sock created")
    logging.debug("main: creating mqtt client")


    logging.debug("doing the info check")
    qolsys_status(qolsys, token)

def get_command_line_args() -> dict:
    args = {}
    for arg in sys.argv[1:]:
        arg_name = arg.split("=",1)[0]
        arg_name = arg_name.split("--",1)[1]
        arg_value = arg.split("=",1)[1]
        logging.debug(("argument name: ", arg_name, " | ", arg_value))
        this_arg = { arg_name: arg_value }
        args.update(this_arg)
    logging.debug(("all arguments: ", args))
    return args
if __name__ == "__main__":
    main()