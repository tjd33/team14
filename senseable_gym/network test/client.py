import socket
import sys
from Reservation import Reservation
import pickle

res = Reservation("pgriff", 1200, 150)
data_string = pickle.dumps(res, -1)
# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect the socket to the port where the server is listening
server_address = (sys.argv[1], 10000)
print ('connecting to %s port %s' % server_address)
sock.connect(server_address)

try:
	size = len(data_string)
	print(size)
	sock.sendall(data_string)

	while size > 0:
		data = sock.recv(8)
		print ('sent 16')
		size -= 16

finally:
	print ('closing socket')
	sock.close()