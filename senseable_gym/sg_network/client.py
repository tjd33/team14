import socket
import sys
from Reservation import Reservation
from senseable_gym.sg_util.machine import Machine, MachineType, MachineStatus
import pickle


	
class PIClient:
	def __init__(self, host, hostPort):
		# Create a TCP/IP socket to the server
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.server_address = (host, hostPort)
		print ('connecting to %s port %s' % self.server_address)
		self.sock.connect(self.server_address)
	
	def pickleAndSend(self, object):
		data_string = pickle.dumps(object, -1)
		try:
			size = len(data_string)
			print(size)
			self.sock.sendall(data_string)

			while size > 0:
				data = self.sock.recv(8)
				size -= 16
		finally:
			pass
	
	def close(self):
		print ('closing socket')
		self.sock.close()
			
if len(sys.argv)<2:
	client = PIClient('localhost', 10000)
else:
	client = PIClient (sys.argv[1], 10000)
	
res = Reservation("pgriff", 1200, 150)
machine = Machine(type=MachineType.TREADMILL, location = [1,1,1])

client.pickleAndSend(res)
client.pickleAndSend(Machine)
client.close()