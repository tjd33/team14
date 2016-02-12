

import unittest

from senseable_gym.sg_database.database import DatabaseModel 
from senseable_gym.sg_util.machine import Machine, MachineType, MachineStatus
from senseable_gym.sg_util.reservation import Reservation
from senseable_gym.sg_util.user import User
from senseable_gym.sg_util.exception import MachineError
from senseable_gym.sg_network.PI import PIClient
from senseable_gym.sg_network.PI import PIServer

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
		
	def test_createClient(self):
		client = PIClient(localhost, 100000)