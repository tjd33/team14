import unittest
from datetime import datetime

from senseable_gym.sg_database.database import DatabaseModel 
from senseable_gym.sg_util.machine import Machine, MachineType, MachineStatus
from senseable_gym.sg_util.reservation import Reservation
from senseable_gym.sg_util.user import User
from senseable_gym.sg_util.exception import MachineError
from senseable_gym.sg_network.PI import PIClient
from senseable_gym.sg_network.PI import PIServer
from senseable_gym.sg_network.server import Server
from senseable_gym.sg_network.server import ServerClient



class TestPINetwork(unittest.TestCase):
	def setUp(self):
		database = DatabaseModel('test', 'team14')
		# database.empty()
		machine = Machine(type=MachineType.TREADMILL, location = [1,1,1])
		try:
			database.add_machine(machine)
		except MachineError:
			pass
		machineListtt = database.get_machines()
		machine = machineListtt[0]
		user = User('dgd8', 'daniel', 'dehoog')
		database.add_user(user)
		reservation = Reservation(machine, user, datetime(2016, 6, 1, 1, 30, 0), datetime(2016, 6, 1, 2, 0, 1))
		database.add_reservation(reservation)
		reservationListtt = database.get_reservations()

	def test_sendUpdate(self):
		self.server_client = ServerClient('localhost', 20000, 'test', 'team14')
		self.server = Server('localhost', 10000, self.server_client)
		self.assertEqual(-1, self.server_client.sendUpdate())
		self.PI_Client = PIClient('localhost', 10000)
		self.PI_Server = PIServer('localhost', 20000, self.PI_Client)
		self.assertEqual(1, self.PI_Client.requestUpdate())
	
	def test_requestUpdate(self):
		self.PI_Client = PIClient('localhost', 10000)
		self.PI_Server = PIServer('localhost', 20000, self.PI_Client)
		self.assertEqual(-1, self.PI_Client.requestUpdate())
		self.server_client = ServerClient('localhost', 20000, 'test', 'team14')
		self.server = Server('localhost', 10000, self.server_client)
		self.assertEqual(1, self.PI_Client.requestUpdate())
	
	def tearDown(self):
		try:
			self.server.stop()
		finally:
			pass
		try:
			self.PI_Server.stop()
		finally:
			pass