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
    """
    The Senseable Gym client. Used to send updates to the Senseable Gym host.

    Args:
        host (str): The address to find the host
        port (int): The port that the host is listening on
    """
    def __init__(self, host, port):
        self.server_address = (host, port)
        my_logger.info('client connected to %s port %s' % self.server_address)

    def _pickle_and_send(self, object_to_send):
        """
        Pickle and then send the pickled object. For use only within the function.

        Args:
            object_to_send (object): The object to send to the server

        Returns:
            None
        """
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
        """
        Send a single reservation

        Args:
            res (Reservation): The Reservation to send.

        Returns:
            None

        TODO:
            - Confirm that it has been sent
        """
        my_logger.debug("sending single reservation")
        self._pickle_and_send(res)


class webClient(sgClient):
    """
    Client to send updates from the website

    TODO:
        - Describe Args
        - Decide if these should be included in one class?
    """
    def __init__(self, host, port, dbname, dbuser):
        super().__init__(host, port)
        self.dbname = dbname
        self.dbuser = dbuser

    def send_update(self):
        """
        Send a complete update to the server.

        Sends machines, reseervations.
        """
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
        """
        Send all the reservations to the server
        """
        my_logger.debug('sending all reservations')
        database = DatabaseModel(self.dbname, self.dbuser)
        save_stderr = sys.stderr
#         sys.stderr = StringIO()
        # this database call sometimes prints thread complaints to stderr. Can't catch them and can't fix them, so I'm silencing them.
        reservation_list = database.get_reservations()
#         sys.stderr.close()
        sys.stderr = save_stderr
        my_logger.debug(len(reservation_list))
        reservation_dict = {reservation.reservation_id: reservation for reservation in reservation_list}
        self._pickle_and_send(reservation_dict)
        my_logger.debug('all reservations sent')

    def send_all_machines(self):
        """
        Send all the machines to the server
        """
        my_logger.debug('sending all machines')
        database = DatabaseModel(self.dbname, self.dbuser)
        save_stderr = sys.stderr
#         sys.stderr = StringIO()
        # this database call sometimes prints thread complaints to stderr. Can't catch them and can't fix them, so I'm silencing them.
        machine_list = database.get_machines()
#         sys.stderr.close()
        sys.stderr = save_stderr
        my_logger.debug(len(machine_list))
        machine_dict = {machine.machine_id: machine for machine in machine_list}
        self._pickle_and_send(machine_dict)
        my_logger.debug('all machines sent')


class piClient(sgClient):
    """
    A client for the PI to send and receive updates to and from the web server.

    Args:
        host (str): The address to find the host
        port (int): The port that the host is listening on
    """
    def __init__(self, host, port):
        super().__init__(host, port)
        self.machines = dict()
        self.reservations = dict()

    def request_update(self):
        """
        Request a complete update from the server.
        """
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
        """
        Send an updated machine
        """
        self._pickle_and_send(machine)

    def request_all_reservations(self):
        """
        Request all the reservations

        TODO:
            - Request only changed reservations
        """
        self._pickle_and_send(Command("request reservations"))

    def request_all_machines(self):
        """
        Request all the machines

        TODO:
            - Request only changed / new machines
        """
        self._pickle_and_send(Command("request machines"))
