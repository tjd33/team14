import logging
import pickle
import socket
import struct
import sys
import time

from senseable_gym.sg_database.database import DatabaseModel
from senseable_gym.sg_network.command import Command


global_logger_name = 'senseable_logger'
file_logger_name = global_logger_name + '.server'
my_logger = logging.getLogger(file_logger_name)
my_logger.setLevel(logging.DEBUG)

class sgClient(object):
    def __init__(self, host, port):
        self.server_address = (host, port)
        my_logger.info('client connected to %s port %s' % self.server_address)
        
    def pickle_and_send(self, object_to_send):
        try:
            # Create a TCP/IP socket to the server
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect(self.server_address)
            data_string = pickle.dumps(object_to_send, -1)
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
        my_logger.debug("sending single reservation")
        self.pickle_and_send(res)

class webClient(sgClient):
    def __init__(self, host, port, dbname, dbuser):
        super().__init__(host,port)
        self.dbname = dbname
        self.dbuser = dbuser
        
    def send_update(self):
        success = 1
        try:
            self.send_all_machines()
        except ConnectionError:
            my_logger.debug('connection refused')
            success = -1
        time.sleep(0.1)
        try:
            self.send_all_reservations()
        except ConnectionError:
            my_logger.debug('connection refused')
            success = -1
        return success
    
    def send_all_reservations(self):
        my_logger.debug('sending all reservations')
        save_stderr = sys.stderr
        sys.stderr = open('trash', 'w')
        database = DatabaseModel(self.dbname, self.dbuser)
        # this database call sometimes prints thread complaints to stderr. Can't catch them and can't fix them, so I'm silencing them.
        reservation_list = database.get_reservations()
        sys.stderr.close()
        sys.stderr = save_stderr
        my_logger.debug(len(reservation_list))
        reservation_dict = {reservation.reservation_id: reservation for reservation in reservation_list}
        self.pickle_and_send(reservation_dict)
        my_logger.debug('all reservations sent')

    def send_all_machines(self):
        my_logger.debug('sending all machines')
        save_stderr = sys.stderr
        sys.stderr = open('trash', 'w')
        database = DatabaseModel(self.dbname, self.dbuser)
        # this database call sometimes prints thread complaints to stderr. Can't catch them and can't fix them, so I'm silencing them.
        machine_list = database.get_machines()
        sys.stderr.close()
        sys.stderr = save_stderr
        my_logger.debug(len(machine_list))
        machine_dict = {machine.machine_id: machine for machine in machine_list}
        self.pickle_and_send(machine_dict)
        my_logger.debug('all machines sent')
        
class piClient(sgClient):
    def __init__(self, host, port):
        super().__init__(host, port)
        self.machines = dict()
        self.reservations = dict()
        
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
    
    def send_machine_update(self, machine):
        self.pickle_and_send(machine)

    def request_all_reservations(self):
        self.pickle_and_send(Command("request reservations"))

    def request_all_machines(self):
        self.pickle_and_send(Command("request machines"))