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
			print(size)
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

class service(socketserver.BaseRequestHandler):
	def handle(self):
		data = 'dummy'
		print ("Client connected with ", self.client_address)
		data = self.request.recv(4)
		length = socket.ntohl(struct.unpack("I",data)[0])
		self.request.send(b'received')
		data = self.request.recv(length+2)
		self.request.send(b'received')
		print ("Client exited")
		self.request.close()
		loadedObject = pickle.loads(data)
		if type(loadedObject) is Reservation:
			print('reservation received: ' + loadedObject.name)
			# add locally made reservation to local list of reservations

		else:
			print(loadedObject.location)
			print ('unknown object type')

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

try:
	client.pickleAndSend(Command("request reservations"))
except ConnectionRefusedError:
	print ('connection refused')

	
res = Reservation("pgriff", 1200, 150)	
try:
	client.pickleAndSend(res)
	print('sent reservation')
except ConnectionRefusedError:
	print ('connection refused')


machine = Machine(type=MachineType.TREADMILL, location = [1,1,1])
machine.status = MachineStatus.BUSY
try:
	client.pickleAndSend(machine)
except ConnectionRefusedError:
	print ('connection refused')

	
os.system('pause')
server.stop()