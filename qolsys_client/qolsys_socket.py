import json
import socket
import ssl
import sys
import time
import asyncio
import threading

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
            print('Could not create a socket')
            raise

        # Wrap SSL
        print("wrapping socket")
        self.wrappedSocket = ssl.wrap_socket(self.sock, cert_reqs=ssl.CERT_NONE, ssl_version=ssl.PROTOCOL_TLSv1_2)
        # print("wrappedSocket: ", self.wrappedSocket)
        # Connect to server
        try:
            #The stupid Qolsys panel requires blocking
            # wrappedSocket.setblocking(False)
            print("connecting to socket")
            self.wrappedSocket.connect((hostname, port))
            print("Connected wrappedSocket:", self.wrappedSocket)
            print("Starting listener thread")
            #print("timeout:", self.sock.gettimeout())
            
            thread = threading.Thread(target=self.listen, args=([cb]))
            thread.start()
            
            print("started listener")
            return True
        except socket.error:
            print(sys.exc_info()[0]) 
            return False

    def send_to_socket(self, message: json):

        self.wrappedSocket.send(b'\n')
        self.wrappedSocket.send((json.dumps(message)).encode())

        return True

    def listen(self, cb: callable):
        listening = True
        print("starting listen")
        data = ""
        err = ""
        while not (self.wrappedSocket._connected):
            print("not connected yet")
            print(self.wrappedSocket._connected)
            time.sleep(1)
        try:
            while self.wrappedSocket._connected:
                data = self.wrappedSocket.recv(4096).decode()
                if is_json(data):
                    try:
                        cb(data)
                    except:
                        print("Error calling callback:", cb, sys.exc_info())
                    #print(data)
                else:
                    print("non json data:", data)
        except socket.timeout:
            print ("socket timeout")
        except:
            print("listen failed/stopped:", sys.exc_info())


def is_json(myjson):
    try:
        json_object = json.loads(myjson)
        if json_object: return True
    except ValueError as e:
        #print("not json:", myjson)
        return False