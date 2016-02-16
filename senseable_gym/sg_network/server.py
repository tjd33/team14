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
		
	def sendUpdate(self):
		success = 1
		try:
			self.sendAllMachines()
		except ConnectionRefusedError:
			success = -1
		time.sleep(0.1)
		try:
			self.sendAllReservations()
		except ConnectionRefusedError:
			success = -1
		return success
		
	def pickleAndSend(self, object):
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
	
	def sendReservation(self, res):
		self.pickleAndSend(res)
			
	def sendAllReservations(self):
		my_logger.info('sending all reservations')
		database = DatabaseModel(self.dbname, self.dbuser)
		save_stderr = sys.stderr
		sys.stderr = open('trash', 'w')
		# this database call sometimes prints thread complaints to stderr. Can't catch them and can't fix them, so I'm silencing them.
		reservationList = database.get_reservations()
		sys.stderr = save_stderr
		my_logger.debug(len(reservationList))
		reservationDict = {reservation.reservation_id:reservation for reservation in reservationList}
		self.pickleAndSend(reservationDict)
		my_logger.debug('all reservations sent')
		
	def sendAllMachines(self):
		my_logger.info('sending all machines')
		save_stderr = sys.stderr
		sys.stderr = open('trash', 'w')
		# this database call sometimes prints thread complaints to stderr. Can't catch them and can't fix them, so I'm silencing them.
		database = DatabaseModel(self.dbname, self.dbuser)
		sys.stderr = save_stderr
		machineList = database.get_machines()
		my_logger.debug(len(machineList))
		machineDict = {machine.machine_id:machine for machine in machineList}
		self.pickleAndSend(machineDict)
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
		loadedObject = pickle.loads(data)
		if type(loadedObject) is Command:
			if loadedObject.commandStr == "request reservations":
				Server.client.sendAllReservations()
			elif loadedObject.commandStr == "request machines":
				Server.client.sendAllMachines()
		elif type(loadedObject) is Reservation:
			my_logger.info('reservation received: ' + loadedObject.name)
			# add locally made reservation to db
		elif type(loadedObject) is Machine:
			my_logger.info("machine update received")
			# cannot access database from thread right now 
			my_logger.debug(loadedObject.machine_id)
			database = DatabaseModel(self.dbname, self.dbuser)
			database.add_machine(loadedObject) # add for testing purposes
			#database.set_machine_status(loadedObject, loadedObject.status)
		else:
			my_logger.debug(type(loadedObject))
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
		thread = Thread(target = Server.runTCPServer)
		thread.start()
		
	def runTCPServer():
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
# client.sendUpdate()

# os.system('pause')
# server.stop()
# save_stderr = sys.stderr
