import sys
import socketserver
from threading import Thread
from Reservation import Reservation
import pickle

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
		res = pickle.loads(data_string)
		print('name: ', res.name)


class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
	pass

t = ThreadedTCPServer((sys.argv[1],10000), service)
print('created server')
try:
	t.serve_forever()
except KeyboardInterrupt:
	pass
t.server_close()