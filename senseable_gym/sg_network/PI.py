import socket
import socketserver
import sys
import struct
import os
from threading import Thread
from Reservation import Reservation
from Command import Command
from senseable_gym.sg_util.machine import Machine, MachineType, MachineStatus
import pickle

class PIClient:
	def __init__(self, host, hostPort):
		self.server_address = (host, hostPort)
		print ('connecting to %s port %s' % self.server_address)
		
	def pickleAndSend(self, object):
		# Create a TCP/IP socket to the server
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		sock.connect(self.server_address)
		data_string = pickle.dumps(object, -1)
		try:
			size = len(data_string)
			size = struct.pack("I", socket.htonl(size))
			sock.sendall(size)
			data = sock.recv(8)
			if data != b'received':
				print("communication error")
			sock.sendall(data_string)
			data = sock.recv(8)
			if data != b'received':
				print("communication error")

		finally:
			sock.close()
			
	def sendReservation(self, res):
		try:
			self.pickleAndSend(res)
		except ConnectionRefusedError:
			print ('connection refused')	

	def sendMachineUpdate(self, machine):
		try:
			self.pickleAndSend(machine)
		except ConnectionRefusedError:
			print ('connection refused')	
			
	def requestAllReservations(self):
		try:
			client.pickleAndSend(Command("request reservations"))
		except ConnectionRefusedError:
			print ('connection refused')

class service(socketserver.BaseRequestHandler):
	def handle(self):
		data = 'dummy'
		print ("Client connected with ", self.client_address)
		data = self.request.recv(4)
		length = socket.ntohl(struct.unpack("I",data)[0])
		self.request.send(b'received')
		data = self.request.recv(length+2)
		self.request.send(b'received')
		self.request.close()
		loadedObject = pickle.loads(data)
		if type(loadedObject) is Reservation:
			print('reservation received: ' + loadedObject.name)
			# add locally made reservation to local list of reservations
		elif type(loadedObject) is list:
			print('received reservation list')
			for reservation in loadedObject:
				if type(reservation) is Reservation:
					print (reservation.name)
					# add to local list
				else:
					print('non reservation received in list')
					
		else:
			print ('unknown object type')
			print (type(loadedObject))

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
			print ('starting server')
			PIServer.t.serve_forever()
		finally:
			print('TCP server was stopped')	
			
	def stop(self):
		PIServer.t.shutdown()
		PIServer.t.server_close()
		
if len(sys.argv)<2:
	host = 'localhost'
else:
	host = sys.argv[1]
client = PIClient(host,10000)
server = PIServer(host,20000)


client.requestAllReservations()
res = Reservation("pgriff", 1200, 150)
client.sendReservation(res)
machine = Machine(type=MachineType.TREADMILL, location = [1,1,1])
machine.status = MachineStatus.BUSY
client.sendMachineUpdate(machine)

	
os.system('pause')
server.stop()