import socket
import socketserver
import sys
import struct
import os
import time
import copy
from threading import Thread
from senseable_gym.sg_network.command import Command
from senseable_gym.sg_util.machine import Machine, MachineType, MachineStatus
from senseable_gym.sg_util.reservation import Reservation
import pickle
import logging

global_logger_name = 'senseable_logger'
file_logger_name = global_logger_name + '.server'
my_logger = logging.getLogger(file_logger_name)
my_logger.setLevel(logging.DEBUG)

class PIClient:
    def __init__(self, host, hostPort):
        self.machines = dict()
        self.reservations = dict()
        self.server_address = (host, hostPort)
        my_logger.info('client connected to %s port %s' % self.server_address)

        
    def request_update(self):
        success = 1
        try: 
            self.request_all_reservations()
        except ConnectionError:
            my_logger.debug('connection refused')
            success = -1
        # time.sleep(1) #for debug purposes
        try: 
            self.request_all_machines()
        except ConnectionError:
            my_logger.debug('connection refused')
            success = -1
        return success
    
    def pickle_and_send(self, object):
        try:
            # Create a TCP/IP socket to the server
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect(self.server_address)
            data_string = pickle.dumps(object, -1)
            size = len(data_string)
            size = struct.pack("I", socket.htonl(size))
            sock.sendall(size)
            data = sock.recv(8)
            if data != b'received':
                my_logger.error("communication error")
            sock.sendall(data_string)
            data = sock.recv(8)
            if data != b'received':
                my_logger.error("communication error")

        finally:
            sock.close()
            
    def send_reservation(self, res):
        self.pickle_and_send(res)    

    def send_machine_update(self, machine):
        self.pickle_and_send(machine)    
            
    def request_all_reservations(self):
        self.pickle_and_send(Command("request reservations"))
            
    def request_all_machines(self):
        self.pickle_and_send(Command("request machines"))
        

class service(socketserver.BaseRequestHandler):
    def handle(self):
        data = 'dummy'
        my_logger.info("Client connected with " + str(self.client_address))
        data = self.request.recv(4)
        length = socket.ntohl(struct.unpack("I",data)[0])
        self.request.send(b'received')
        data = self.request.recv(length+2)
        self.request.send(b'received')
        self.request.close()
        my_logger.debug(len(data))
        loaded_object = pickle.loads(data)
        if type(loaded_object) is Reservation:
            my_logger.info('reservation received: ' + loaded_object.name)
            # add locally made reservation to local list of reservations
        elif type(loaded_object) is dict:
            if type(next (iter (loaded_object.values()))) is Machine:
                PIServer.client.machines = loaded_object
                my_logger.info('replaced machine database')
            elif type(next (iter (loaded_object.values()))) is Reservation:
                PIServer.client.reservations = loaded_object
                my_logger.info('replaced reservation database')

            else:
                my_logger.debug('unknown dictionary type')
        else:
            my_logger.debug ('unknown object type')
            my_logger.debug (type(loaded_object))

class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    pass

class PIServer:
    t = None
    client = None
    def __init__(self, host, port, client):
        PIServer.client = client
        PIServer.t = ThreadedTCPServer((host,port),service)
        PIServer.t.allow_reuse_address
        thread = Thread(target = PIServer.run_TCP_server)
        thread.start()
        
    def run_TCP_server():
        try:
            my_logger.info('starting server')
            PIServer.t.serve_forever()
        finally:
            my_logger.info('TCP server was stopped')    
            
    def stop(self):
        sys.stderr = open('trash', 'w')
        PIServer.t.shutdown()
        PIServer.t.server_close()
        
if len(sys.argv)<2:
    host = 'localhost'
else:
    host = sys.argv[1]
    
# server = PIServer(host,20000)
# client = PIClient(host,10000)
# client.request_update()

    
# os.system('pause')
# server.stop()