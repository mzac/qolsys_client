import json
import socket
import ssl
import sys
import time

################################################################################
# Code
def qolsysStatus(hostname, port, token, timeout):
    statusString    = {
                        "nonce":        "qolsys",
                        "action":       "INFO",
                        "info_type":    "SUMMARY",
                        "version":      0,
                        "source":       "C4",
                        "token":        token,
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
        wrappedSocket.send((json.dumps(statusString)).encode())
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
