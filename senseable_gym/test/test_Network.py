import unittest
import logging
import time
from datetime import datetime

from senseable_gym.sg_database.database import DatabaseModel 
from senseable_gym.sg_util.machine import Machine, MachineType, MachineStatus
from senseable_gym.sg_util.reservation import Reservation
from senseable_gym.sg_util.user import User
from senseable_gym.sg_util.exception import MachineError
from senseable_gym.sg_util.exception import ReservationError
from senseable_gym.sg_network.PI import PIClient
from senseable_gym.sg_network.PI import PIServer
from senseable_gym.sg_network.server import Server
from senseable_gym.sg_network.server import ServerClient



class TestPINetwork(unittest.TestCase):
	def setUp(self):
		database = DatabaseModel('test', 'team14')
		# database.empty()
		self.machine = Machine(type=MachineType.TREADMILL, location = [1,1,1])
		try:
			database.add_machine(self.machine)
		except MachineError:
			pass
			# should raise expection until empty is implemented and uncommented
		machineList = database.get_machines()
		self.machine = machineList[0]
		user = User('dgd8', 'daniel', 'dehoog')
		database.add_user(user)
		self.reservation = Reservation(self.machine, user, datetime(2016, 6, 1, 1, 30, 0), datetime(2016, 6, 1, 2, 0, 1))
		try:
			database.add_reservation(self.reservation)
		except ReservationError:
			pass
		reservationListtt = database.get_reservations()

	# also tests sendAllReservations and sendAllMachines
	def test_sendUpdate(self): 
		self.server_client = ServerClient('localhost', 20000, 'test', 'team14')
		self.server = Server('localhost', 10000, self.server_client)
		self.assertEqual(-1, self.server_client.sendUpdate())
		self.PI_Client = PIClient('localhost', 10000)
		self.PI_Server = PIServer('localhost', 20000, self.PI_Client)
		self.assertEqual(1, self.PI_Client.requestUpdate())
	
	# also tests requestAllReservations and requestAllMachines
	def test_requestUpdate(self):
		self.PI_Client = PIClient('localhost', 10000)
		self.PI_Server = PIServer('localhost', 20000, self.PI_Client)
		self.assertEqual(-1, self.PI_Client.requestUpdate())
		self.assertEqual(0, len(self.PI_Client.machines))
		self.assertEqual(0, len(self.PI_Client.reservations))
		self.server_client = ServerClient('localhost', 20000, 'test', 'team14')
		self.server = Server('localhost', 10000, self.server_client)
		self.assertEqual(1, self.PI_Client.requestUpdate())
		time.sleep(1) # give time for request to send and come back
		self.assertEqual(1, len(PIServer.client.machines))
		self.assertEqual(1, len(self.PI_Client.machines))
		self.assertEqual(self.machine, next(iter(self.PI_Client.machines.values())))
		self.assertEqual(1, len(PIServer.client.reservations))
		self.assertEqual(1, len(self.PI_Client.reservations))
		self.assertEqual(self.reservation, next(iter(self.PI_Client.reservations.values())))
	
	def tearDown(self):
		try:
			self.server.stop()
		finally:
			pass
		try:
			self.PI_Server.stop()
		finally:
			pass
			
if __name__ == '__main__':
    unittest.main()