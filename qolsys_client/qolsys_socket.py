import json
import socket
import ssl
import sys
import time
import asyncio
import threading
import logging

class qolsys:
    ################################################################################
    # Code

    def __init__(self):
        self.sock = socket.socket
        self.wrappedSocket = ssl.SSLContext.wrap_socket

    def create_socket(self, hostname, port, token, cb: callable, timeout=60):
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.settimeout(timeout)
        except socket.error:
            logging.error('Could not create a socket')
            raise

        # Wrap SSL
        logging.debug("wrapping socket")
        self.wrappedSocket = ssl.wrap_socket(self.sock, cert_reqs=ssl.CERT_NONE, ssl_version=ssl.PROTOCOL_TLSv1_2)

        # Connect to server
        try:
            #The stupid Qolsys panel requires blocking
            # wrappedSocket.setblocking(False)
            logging.debug("connecting to socket")
            self.wrappedSocket.connect((hostname, port))
            logging.debug(("Connected wrappedSocket:", self.wrappedSocket))
            
            logging.debug("Starting listener thread")
            thread = threading.Thread(target=self.listen, args=([cb]))
            thread.start()
            logging.debug("started listener")
            
            return True
        except socket.error:
            logging.error(("Error creating or connecting to socket", sys.exc_info()))
            return False

    def send_to_socket(self, message: json):

        self.wrappedSocket.send(b'\n')
        self.wrappedSocket.send((json.dumps(message)).encode())

        return True

    def listen(self, cb: callable):
        #listening = True
        logging.debug("starting listen")
        data = ""
        #err = ""
        while not (self.wrappedSocket._connected):
            logging.warning("not connected yet")
            logging.debug(self.wrappedSocket._connected)
            time.sleep(1)
        try:
            while self.wrappedSocket._connected:
                data = self.wrappedSocket.recv(4096).decode()
                if is_json(data):
                    try:
                        cb(data)
                    except:
                        logging.error(("Error calling callback:", cb, sys.exc_info()))
                    #print(data)
                else:
                    if data != 'ACK\n':
                        pass
                        #logging.warning(("non json data:", data))
        except socket.timeout:
            logging.debug("socket timeout")
        except:
            logging.error(("listen failed/stopped:", sys.exc_info()))


def is_json(myjson):
    try:
        json_object = json.loads(myjson)
        if json_object: return True
    except:
        if myjson != 'ACK\n':
            logging.debug(("not json:", myjson))
            logging.debug(("Error:", sys.exc_info()))
        return False