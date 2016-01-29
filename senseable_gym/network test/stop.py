import socket
import sys

# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect the socket to the port where the server is listening
server_address = (sys.argv[1], 10000)
print ('connecting to %s port %s' %server_address)
sock.connect(server_address)

try:
	
	# Send data
	message = 'stop'
	print ('sending "%s"' % message)
	sock.sendall(message)

	# Look for the response
	print (sock.recv(16))

 

finally:
	print ('closing socket')
	sock.close()