import socket
import sys

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
		while True:
			data = connection.recv(16)
			print ('received "%s"' %data)
			if data:
				print ('sending data back to the client')
				if data == b'stop':
					nonstop = False
				connection.sendall(data)
			else:
				print ('no more data from', client_address)
				break
			
	finally:
		# Clean up the connection
		connection.close()