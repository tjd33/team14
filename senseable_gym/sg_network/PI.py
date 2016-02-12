import socket
import socketserver
import sys
import struct
import os
import time
from threading import Thread
from Command import Command
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

		
	def requestUpdate(self):
		self.requestAllMachines()
		time.sleep(0.1) #for debug purposes
		self.requestAllReservations()
	
	def pickleAndSend(self, object):
		# Create a TCP/IP socket to the server
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		try:
			sock.connect(self.server_address)
		except ConnectionRefusedError:
			my_logger.error ('connection refused')
			return
		data_string = pickle.dumps(object, -1)
		try:
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
			
	def sendReservation(self, res):
		self.pickleAndSend(res)	

	def sendMachineUpdate(self, machine):
		self.pickleAndSend(machine)	
			
	def requestAllReservations(self):
		self.pickleAndSend(Command("request reservations"))
			
	def requestAllMachines(self):
		self.pickleAndSend(Command("request machines"))
		

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
		loadedObject = pickle.loads(data)
		if type(loadedObject) is Reservation:
			my_logger.info('reservation received: ' + loadedObject.name)
			# add locally made reservation to local list of reservations
		elif type(loadedObject) is dict:
			if type(next (iter (loadedObject.values()))) is Machine:
				client.machines = loadedObject
				my_logger.debug(next (iter (loadedObject.values())))
				my_logger.info('replaced machine database')
			elif type(next (iter (loadedObject.values()))) is Reservation:
				my_logger.debug(len(loadedObject))
				client.reservations = loadedObject
				my_logger.info('replaced reservation database')
			else:
				my_logger.debug('unknown dictionary type')
		else:
			my_logger.debug ('unknown object type')
			my_logger.debug (type(loadedObject))

class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
	pass

class PIServer:
	t = None

	def __init__(self, host, port):
		PIServer.t = ThreadedTCPServer((host,port),service)
		PIServer.t.allow_reuse_address
		thread = Thread(target = PIServer.runTCPServer)
		thread.start()
		
	def runTCPServer():
		try:
			my_logger.info('starting server')
			PIServer.t.serve_forever()
		finally:
			my_logger.info('TCP server was stopped')	
			
	def stop(self):
		PIServer.t.shutdown()
		PIServer.t.server_close()
		
if len(sys.argv)<2:
	host = 'localhost'
else:
	host = sys.argv[1]
	
server = PIServer(host,20000)
client = PIClient(host,10000)
client.requestUpdate()

	
os.system('pause')
server.stop()