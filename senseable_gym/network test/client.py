import socket
import sys
from Reservation import Reservation
from senseable_gym.sg_util.machine import Machine, MachineType, MachineStatus
import pickle

res = Reservation("pgriff", 1200, 150)
machine = Machine(type=MachineType.TREADMILL, location = [1,1,1])
data_string = pickle.dumps(machine, -1)
# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect the socket to the port where the server is listening
if len(sys.argv)<2:
	server_address = ('localhost', 10000)
else:
	server_address = (sys.argv[1], 10000)
print ('connecting to %s port %s' % server_address)
sock.connect(server_address)

try:
	size = len(data_string)
	print(size)
	sock.sendall(data_string)

	while size > 0:
		data = sock.recv(8)
		size -= 16

finally:
	print ('closing socket')
	sock.close()