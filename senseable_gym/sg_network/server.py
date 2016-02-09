import sys
import socketserver
import socket
import struct
import os
from threading import Thread
from Reservation import Reservation
from Command import Command
import pickle

# Local Imports
from senseable_gym.sg_database.database import DatabaseModel
from senseable_gym.sg_util.machine import Machine, MachineType, MachineStatus
from senseable_gym.sg_util.reservation import Reservation
from senseable_gym.sg_util.user import User

class ServerClient:
	def __init__(self, host, hostPort):
		self.server_address = (host, hostPort)
		print ('connecting to %s port %s' % self.server_address)
		
	def pickleAndSend(self, object):
		# Create a TCP/IP socket to the server
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		try:
			sock.connect(self.server_address)
		except ConnectionRefusedError:
			print ('connection refused')
			return
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
		self.pickleAndSend(res)
			
	def sendAllReservations(self):
		print('sending all reservations')
		database = DatabaseModel('testdb', 'team14')
		#database.getAllReservations()
		res1 = Reservation(Machine(type=MachineType.TREADMILL, location = [1,1,1]), 1, 1)
		res2 = Reservation(Machine(type=MachineType.TREADMILL, location = [1,1,1]), 1, 1)
		reservationList = []
		reservationList.append(res1)
		reservationList.append(res2)
		reservationDict = {reservation.reservation_id:reservation for reservation in reservationList}
		self.pickleAndSend(reservationDict)
		
	def sendAllMachines(self):
		print('sending all machines')
		database = DatabaseModel('testdb', 'team14')
		machineList = database.get_machines()
		machineDict = {machine.machine_id:machine for machine in machineList}
		self.pickleAndSend(machineDict)
		
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
		if type(loadedObject) is Command:
			if loadedObject.commandStr == "request reservations":
				client.sendAllReservations()
			elif loadedObject.commandStr == "request machines":
				client.sendAllMachines()
		elif type(loadedObject) is Reservation:
			print('reservation received: ' + loadedObject.name)
			# add locally made reservation to db
		elif type(loadedObject) is Machine:
			print ("update machine in database")
			# cannot access database from thread right now 
			print(loadedObject.machine_id)
			database = DatabaseModel('testdb', 'team14')
			database.add_machine(loadedObject) # add for testing purposes
			#database.set_machine_status(loadedObject, loadedObject.status)
		else:
			print(type(loadedObject))
			print ('unknown object type')

class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
	pass

class Server:
	t = None
	def __init__(self, host, port):
		Server.t = ThreadedTCPServer((host,port),service)
		Server.t.allow_reuse_address
		thread = Thread(target = Server.runTCPServer)
		thread.start()
		
	def runTCPServer():
		try:
			print ('starting server')
			Server.t.serve_forever()
		finally:
			print('TCP server was stopped')	
			
	def stop(self):
		Server.t.shutdown()
		Server.t.server_close()
	
if len(sys.argv) < 2:
	host = 'localhost'
else:
	host = sys.argv[1]
client = ServerClient(host, 20000)
server = Server(host, 10000)


client.sendAllReservations()
database = DatabaseModel('testdb', 'team14')
database.add_machine(Machine(type=MachineType.TREADMILL, location = [1,1,1]))

os.system('pause')
server.stop()