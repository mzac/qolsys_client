import json
import socket
import ssl
import sys
import time

################################################################################
# Code
def qolsysArm(hostname, port, token, timeout, partition, arm_type):
    if arm_type.lower() == 'away':
        arming_type = "ARM_AWAY"
    elif arm_type.lower() == 'stay':
        arming_type = "ARM_STAY"
    elif arm.type.lower() == 'disarm':
        arming_type = "DISARM"

    armString    = {
                        "partition_id": partition,
                        "action":       "ARMING",
                        "arming_type":  arming_type,
                        "version":      0,
                        "nonce":        "qolsys",
                        "source":       "C4",
                        "version_key":  1,
                        "source_key":   "C4",
                        "token":        token
                    }

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
    except socket.error:
        print('Could not create a socket')
        sys.exit()

    # Wrap SSL
    wrappedSocket = ssl.wrap_socket(sock, cert_reqs=ssl.CERT_NONE, ssl_version=ssl.PROTOCOL_TLSv1_2)

    # Connect to server
    try:
        wrappedSocket.connect((hostname, port))
    except socket.error:
        print('Could not connect to server')
        sys.exit()

    # Send message and print reply
    online = True
    while online:
        wrappedSocket.send(b'\n')
        wrappedSocket.send((json.dumps(armString)).encode())
        while True:
            response = wrappedSocket.recv(4096).decode()
            if is_json(response):
                online = False
                return(response)
                break  # stop receiving
        time.sleep(timeout / 4)

def is_json(myjson):
    try:
        json_object = json.loads(myjson)
    except ValueError as e:
        return False
    return True
