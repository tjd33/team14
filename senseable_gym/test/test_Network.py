

import unittest

from senseable_gym.sg_database.database import DatabaseModel 
from senseable_gym.sg_util.machine import Machine, MachineType, MachineStatus
from senseable_gym.sg_util.reservation import Reservation
from senseable_gym.sg_util.user import User
from senseable_gym.sg_util.exception import MachineError
from senseable_gym.sg_network.PI import PIClient
from senseable_gym.sg_network.PI import PIServer
from senseable_gym.sg_network.Command import Command


global_logger_name = 'senseable_logger'
file_logger_name = global_logger_name + '.server'
my_logger = logging.getLogger(file_logger_name)
my_logger.setLevel(logging.DEBUG)

class TestPINetwork(unittest.TestCase):
	def setUp(self):
		database = DatabaseModel('test', 'team14')
		#database.empty()
		machine = Machine(type=MachineType.TREADMILL, location = [1,1,1])
		try:
			database.add_machine(machine)
		except MachineError:
			my_logger.debug('db already contains machine')
		machineListtt = database.get_machines()
		machine = machineListtt[0]
		user = User('dgd8', 'daniel', 'dehoog')
		database.add_user(user)
		reservation = Reservation(machine, user, datetime(2016, 6, 1, 1, 30, 0), datetime(2016, 6, 1, 2, 0, 1))
		database.add_reservation(reservation)
		reservationListtt = database.get_reservations()
		my_logger.debug(len(reservationListtt))
		PIServer = PIServer(localhost, 20000)
		PIClient = PIClient(localhost, 10000)
		
	def test_requestUpdate(self):
		self.assertEqual(-1, PIClient.requestUpdate())
		Server = Server(localhost, 10000)
		self.assertEqual(1, PIClient.requestUpdate())
		