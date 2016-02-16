import sys
import socketserver
import socket
import struct
import os
import time

from threading import Thread
from sqlite3 import ProgrammingError
import pickle
import logging

# Local Imports
from senseable_gym.sg_database.database import DatabaseModel
from senseable_gym.sg_util.machine import Machine, MachineType, MachineStatus
from senseable_gym.sg_util.reservation import Reservation
from senseable_gym.sg_util.user import User
from senseable_gym.sg_util.exception import MachineError
from senseable_gym.sg_network.command import Command

global_logger_name = 'senseable_logger'
file_logger_name = global_logger_name + '.server'
my_logger = logging.getLogger(file_logger_name)
my_logger.setLevel(logging.DEBUG)

class ServerClient:
    def __init__(self, host, hostPort, dbname, dbuser):
        self.dbname = dbname
        self.dbuser = dbuser
        self.server_address = (host, hostPort)
        my_logger.info('connecting to %s port %s' % self.server_address)
        
    def send_update(self):
        success = 1
        try:
            self.send_all_machines()
        except ConnectionRefusedError:
            success = -1
        time.sleep(0.1)
        try:
            self.send_all_reservations()
        except ConnectionRefusedError:
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
            my_logger.debug('sending packet size: ' + str(len(data_string)))
            sock.sendall(data_string)
            data = sock.recv(8)
            if data != b'received':
                my_logger.error("communication error")

        finally:
            sock.close()
    
    def send_reservation(self, res):
        self.pickle_and_send(res)
            
    def send_all_reservations(self):
        my_logger.info('sending all reservations')
        database = DatabaseModel(self.dbname, self.dbuser)
        save_stderr = sys.stderr
        sys.stderr = open('trash', 'w')
        # this database call sometimes prints thread complaints to stderr. Can't catch them and can't fix them, so I'm silencing them.
        reservation_list = database.get_reservations()
        sys.stderr.close()
        sys.stderr = save_stderr
        my_logger.debug(len(reservation_list))
        reservation_dict = {reservation.reservation_id:reservation for reservation in reservation_list}
        self.pickle_and_send(reservation_dict)
        my_logger.debug('all reservations sent')
        
    def send_all_machines(self):
        my_logger.info('sending all machines')
        database = DatabaseModel(self.dbname, self.dbuser)
        save_stderr = sys.stderr
        sys.stderr = open('trash', 'w')
        # this database call sometimes prints thread complaints to stderr. Can't catch them and can't fix them, so I'm silencing them.
        machine_list = database.get_machines()
        sys.stderr.close()
        sys.stderr = save_stderr
        my_logger.debug(len(machine_list))
        machine_dict = {machine.machine_id:machine for machine in machine_list}
        self.pickle_and_send(machine_dict)
        my_logger.debug('all machines sent')

        
class service(socketserver.BaseRequestHandler):
    def handle(self):
        data = 'dummy'
        my_logger.info ("Client connected with"  + str(self.client_address))
        data = self.request.recv(4)
        length = socket.ntohl(struct.unpack("I",data)[0])
        self.request.send(b'received')
        data = self.request.recv(length+2)
        self.request.send(b'received')
        self.request.close()
        loaded_object = pickle.loads(data)
        if type(loaded_object) is Command:
            if loaded_object.commandStr == "request reservations":
                Server.client.send_all_reservations()
            elif loaded_object.commandStr == "request machines":
                Server.client.send_all_machines()
        elif type(loaded_object) is Reservation:
            my_logger.info('reservation received: ' + loaded_object.name)
            # add locally made reservation to db
        elif type(loaded_object) is Machine:
            my_logger.info("machine update received")
            # cannot access database from thread right now 
            my_logger.debug(loaded_object.machine_id)
            database = DatabaseModel(self.dbname, self.dbuser)
            database.add_machine(loaded_object) # add for testing purposes
            #database.set_machine_status(loaded_object, loaded_object.status)
        else:
            my_logger.debug(type(loaded_object))
            my_logger.debug ('unknown object type')

class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    pass

class Server:
    t = None
    client = None
    
    def __init__(self, host, port, client):
        Server.client = client
        Server.t = ThreadedTCPServer((host,port),service)
        Server.t.allow_reuse_address
        thread = Thread(target = Server.run_TCP_server)
        thread.start()
        
    def run_TCP_server():
        try:
            my_logger.info ('starting server')
            Server.t.serve_forever()
        finally:
            my_logger.info('TCP server was stopped')    
            
    def stop(self):
        sys.stderr = open('trash', 'w')
        Server.t.shutdown()
        Server.t.server_close()
    
if len(sys.argv) < 2:
    host = 'localhost'
else:
    host = sys.argv[1]




# server = Server(host, 10000)
# client = ServerClient(host, 20000, 'test', 'team14')
# client.send_update()

# os.system('pause')
# server.stop()
# save_stderr = sys.stderr
