import sys
import socketserver
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
		data_string = b''
		while len(data):
			data = self.request.recv(16)
			data_string += data
			self.request.send(b'received')

		print ("Client exited")
		self.request.close()
		obj = pickle.loads(data_string)
		if type(obj) is Reservation:
			print('name: ', obj.name)
			# add locally made reservation to db
		elif type(obj) is Machine:
			print ("add machine to database")
			# database.set_machine_status(obj.machine_id,obj.status)
		else:
			print ('unknown object type')

class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
	pass

if len(sys.argv) < 2:
	host = 'localhost'
else:
	host = sys.argv[1]
t = ThreadedTCPServer((host,10000), service)
print('created server')
database = DatabaseModel('testdb', 'team14')
database.add_machine(Machine(type=MachineType.TREADMILL, location=[1, 1, 1]))
try:
	t.serve_forever()
except KeyboardInterrupt:
	pass
t.server_close()