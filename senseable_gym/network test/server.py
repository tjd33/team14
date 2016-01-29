import socket
import sys
from Reservation import Reservation
import pickle

# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the socket to the address given on the command line
server_name = sys.argv[1]
server_address = (server_name, 10000)
print ('starting up on %s port %s' %server_address)
sock.bind(server_address)
sock.listen(1)

nonstop = True

while True:
	if not nonstop:
		break
	print ('waiting for connection')
	connection, client_address = sock.accept()
	try:
		print ('connection from', client_address)

		# Receive the data in small chunks and retransmit it
		data_string = b''
		while True:
			data = connection.recv(16)
			if data:
				print ('received data')
				if data == b'stop':
					nonstop = False
				data_string += data
				connection.sendall(b'received')
			else:
				print ('no more data from', client_address)
				break
			
	finally:
		# Clean up the connection
		connection.close()
		if nonstop:
			res = pickle.loads(data_string)
			print('name: ', res.name)