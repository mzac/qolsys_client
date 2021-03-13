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
        self._sock = socket.socket
        self._wrappedSocket = ssl.SSLContext.wrap_socket
        self._listening_thread = threading.Thread()
        self._listener_callback = callable
        self._hostname = ""
        self._port = 12345
        self._token = ""
        self._timeout = 60

    def create_socket(self, hostname, port, token, cb: callable, timeout=60):
        self._hostname = hostname
        self._port = port
        self._token = token
        self._listener_callback = cb
        self._timeout = timeout
        try:
            self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._sock.settimeout(timeout)
            #Set the listener callback at the instance level so we can restart the listener if needed
        except socket.error:
            logging.error('Could not create a socket')
            raise

        # Wrap SSL
        logging.debug("wrapping socket")
        self._wrappedSocket = ssl.wrap_socket(self._sock, cert_reqs=ssl.CERT_NONE, ssl_version=ssl.PROTOCOL_TLSv1_2)

        # Connect to server
        try:
            #The stupid Qolsys panel requires blocking
            # wrappedSocket.setblocking(False)
            logging.debug("connecting to socket")
            self._wrappedSocket.connect((hostname, port))
            logging.debug(("Connected wrappedSocket:", self._wrappedSocket))
            
            logging.debug("Starting listener thread")
            self._start_listener()
            #self.listening_thread = threading.Thread(target=self.listen, args=([cb]))
            #self.listening_thread.start()
            logging.debug("started listener")
            
            return True
        except socket.error:
            logging.error(("Error creating or connecting to socket", sys.exc_info()))
            return False
    def _start_listener(self):
        logging.debug(("Starting listener thread"))
        self._listening_thread = threading.Thread(target=self.listen, args=([self._listener_callback]))
        self._listening_thread.start()
        logging.debug(("started listener thread"))

    def _reset_socket(self):
        logging.debug(("Detatching from wrapped socket"))
        self._wrappedSocket.detach()
        logging.debug(("Closing socket"))
        self._sock.close()
        time.sleep(2)
        #self._listening_thread = threading.Thread(target=self.listen, args=([self._listener_callback]))
        logging.debug(("Creating socket"))
        self.create_socket(self._hostname, self._port, self._token, self._listener_callback, self._timeout)

    def send_to_socket(self, message: json):

        self._wrappedSocket.send(b'\n')
        self._wrappedSocket.send((json.dumps(message)).encode())

        return True

    def listen(self, cb: callable):
        #listening = True
        logging.debug("starting listen")
        data = ""
        #err = ""
        while not (self._wrappedSocket._connected):
            logging.warning("not connected yet")
            logging.debug(self._wrappedSocket._connected)
            time.sleep(1)
        try:
            while self._wrappedSocket._connected:
                data = self._wrappedSocket.recv(4096).decode()
                if len(data) > 0:
                    logging.debug(("data received from qolsys panel:", data, "len(data): ", len(data)))
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
                else:
                    logging.error(("No data received.  Bad token?  Detatching."))
                    self._wrappedSocket.detach()
                    raise NoDataError
        except socket.timeout:
            logging.debug("socket timeout")
        except NoDataError:
            self._reset_socket()
            raise NoDataError
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

class NoDataError(Exception):
    pass