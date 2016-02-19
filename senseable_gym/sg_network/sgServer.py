import logging
import pickle
import socket
import socketserver
import struct
import sys
from threading import Thread

from senseable_gym.sg_database.database import DatabaseModel
from senseable_gym.sg_network.command import Command
from senseable_gym.sg_network.sgClient import webClient, piClient
from senseable_gym.sg_util.machine import Machine
from senseable_gym.sg_util.reservation import Reservation


global_logger_name = 'senseable_logger'
file_logger_name = global_logger_name + '.server'
my_logger = logging.getLogger(file_logger_name)
my_logger.setLevel(logging.DEBUG)

class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    pass

def run_tcp_server(tcp_server):
    try:
        my_logger.info('starting server')
        tcp_server.serve_forever()
    finally:
        my_logger.info('TCP server was stopped')

class sgServer(object):
    def __init__(self, host, port, service):
        self.tcp_server = ThreadedTCPServer((host, port), service)
        self.tcp_server.allow_reuse_address
        thread = Thread(target=run_tcp_server, args = (self.tcp_server, ))
        thread.start()
        
    def stop(self):
#         sys.stderr = open('trash', 'w')
#         sys.stderr.close()
        self.tcp_server.shutdown()
        self.tcp_server.server_close()
        
    def pickle_and_send(self, object_to_send):
        self.client.pickle_and_send(object_to_send)
        
    def send_reservation(self, reservation):
        self.client.send_reservation(reservation)
        
class webService(socketserver.BaseRequestHandler):
    def handle(self):
        my_logger.info("Client connected with" + str(self.client_address))
        data = self.request.recv(4)
        length = socket.ntohl(struct.unpack("I", data)[0])
        self.request.send(b'received')
        data = self.request.recv(length + 2)
        self.request.send(b'received')
        self.request.close()
        loaded_object = pickle.loads(data)
        if type(loaded_object) is Command:
            if loaded_object.commandStr == "request reservations":
                self.server.client.send_all_reservations()
            elif loaded_object.commandStr == "request machines":
                self.server.client.send_all_machines()
        elif type(loaded_object) is Reservation:
            my_logger.info('reservation received: ' + loaded_object.name)
            # add locally made reservation to db
        elif type(loaded_object) is Machine:
            my_logger.info("machine update received")
            # cannot access database from thread right now
            my_logger.debug(loaded_object.machine_id)
            database = DatabaseModel(self.dbname, self.dbuser)
            database.add_machine(loaded_object)  # add for testing purposes
            # database.set_machine_status(loaded_object, loaded_object.status)
        else:
            my_logger.debug(type(loaded_object))
            my_logger.debug('unknown object type')
            
class webServer(sgServer):
    def __init__(self, server_host, server_port, client_host, client_port, db_name, db_user):
        super().__init__(server_host, server_port, webService)
        self.client = webClient(client_host, client_port, db_name, db_user)
        self.tcp_server.client = self.client # accessible by webService

    def send_update(self):
        return self.client.send_update()
        
    def send_all_reservations(self):
        self.client.send_all_reservations()
        
    def send_all_machines(self):
        self.client.send_all_machines()

class piService(socketserver.BaseRequestHandler):
    def handle(self):
        my_logger.info("Client connected with " + str(self.client_address))
        data = self.request.recv(4)
        length = socket.ntohl(struct.unpack("I", data)[0])
        self.request.send(b'received')
        data = self.request.recv(length + 2)
        self.request.send(b'received')
        self.request.close()
        my_logger.debug(len(data))
        loaded_object = pickle.loads(data)
        if type(loaded_object) is Reservation:
            my_logger.info('reservation received: ' + loaded_object.name)
            # add locally made reservation to local list of reservations
        elif type(loaded_object) is dict:
            if type(next(iter(loaded_object.values()))) is Machine:
                self.server.client.machines = loaded_object
                my_logger.info('replaced machine database')
            elif type(next(iter(loaded_object.values()))) is Reservation:
                self.server.client.reservations = loaded_object
                my_logger.info('replaced reservation database')

            else:
                my_logger.debug('unknown dictionary type')
        else:
            my_logger.debug('unknown object type')
            my_logger.debug(type(loaded_object))
    
class piServer(sgServer):
    def __init__(self, server_host, server_port, client_host, client_port):
        super().__init__(server_host, server_port, piService)
        self.client = piClient(client_host, client_port)
        self.tcp_server.client = self.client
        
    def request_update(self):
        return self.client.request_update()
        
    def request_all_reservations(self):
        self.client.request_all_reservations()
    
    def request_all_machines(self):
        self.client.request_all_machines()
        
    def send_machine_update(self, machine):
        self.client.send_machine_update(machine)
    