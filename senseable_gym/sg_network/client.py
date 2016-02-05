import socket
import sys
import struct
from Reservation import Reservation
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
			
if len(sys.argv)<2:
	client = PIClient('localhost', 10000)
else:
	client = PIClient (sys.argv[1], 10000)
	
res = Reservation("pgriff", 1200, 150)

client.pickleAndSend(res)
machine = Machine(type=MachineType.TREADMILL, location = [1,1,1])
client.pickleAndSend(machine)