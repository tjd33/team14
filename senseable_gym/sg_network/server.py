import sys
import socketserver
import socket
import struct
from threading import Thread
from Reservation import Reservation
import pickle

# Local Imports
from senseable_gym.sg_database.database import DatabaseModel
from senseable_gym.sg_util.machine import Machine, MachineType, MachineStatus
from senseable_gym.sg_util.user import User

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
			pass
			# add locally made reservation to db
		elif type(loadedObject) is Machine:
			print ("update machine in database")
			# cannot access database from thread right now 
			print(loadedObject.machine_id)
			database = DatabaseModel('testdb', 'team14')
			database.add_machine(loadedObject) # add for testing purposes
			#database.set_machine_status(loadedObject, loadedObject.status)
		else:
			print(loadedObject.location)
			print ('unknown object type')

class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
	pass

if len(sys.argv) < 2:
	host = 'localhost'
else:
	host = sys.argv[1]
t = ThreadedTCPServer((host,10000), service)
t.allow_reuse_address = True
print('created server')

try:
	t.serve_forever()
except KeyboardInterrupt:
	t.server_close()
