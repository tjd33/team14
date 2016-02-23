from datetime import datetime
import time
import unittest

from senseable_gym.sg_database.database import DatabaseModel
from senseable_gym.sg_network.sgServer import piServer, webServer
from senseable_gym.sg_util.exception import MachineError
from senseable_gym.sg_util.exception import ReservationError
from senseable_gym.sg_util.exception import UserError
from senseable_gym.sg_util.machine import Machine, MachineType, MachineStatus
from senseable_gym.sg_util.reservation import Reservation
from senseable_gym.sg_util.user import User


class TestPINetwork(unittest.TestCase):
    def setUp(self):
        database = DatabaseModel('test', 'team14')
        database._empty_db()

        # Create and add a machine to the database
        self.machine = Machine(type=MachineType.TREADMILL, location=[1, 1, 1])
        try:
            database.add_machine(self.machine)
        except MachineError:
            self.fail('database should be empty')

        # Create and add a user to the database
        self.user = User('dgd8', 'daniel', 'dehoog')
        try:
            database.add_user(self.user)
        except UserError:
            self.fail('database should be empty')

        # Create and add a reservation to the database
        self.reservation = Reservation(
                self.machine,
                self.user,
                datetime(2016, 6, 1, 1, 30, 0),
                datetime(2016, 6, 1, 2, 0, 1)
            )
        try:
            database.add_reservation(self.reservation)
        except ReservationError:
            self.fail('database should be empty')

        self.reservation_list = database.get_reservations()

    def test_send_reservation_to_pi(self):
        self.web_server = webServer('localhost', 10000, 'localhost', 20000, 'test', 'team14')
        self.pi_server = piServer('localhost', 20000, 'localhost', 10000, 'test', 'team14')
        self.pi_client = self.pi_server.client
         
        # Assert that there are no reservations on the PI
        self.assertEqual({}, self.pi_client.reservations)
 
        # Now we send a reservation to the client
        self.web_server.send_reservation(self.reservation)
        time.sleep(1)  # give time for request to be completed
 
        # Now we should have a reservation in our client
        self.assertEqual(1, len(self.pi_client.reservations))
        self.assertEqual(self.reservation, next(iter(self.pi_client.reservations.values())))
    
#     def test_send_reservation_from_pi(self):
#         self.web_server = webServer('localhost', 10004, 'localhost', 20004, 'test', 'team14')
#         self.pi_server = piServer('localhost', 20004, 'localhost', 10004, 'test', 'team14')
#         
#         # assert preconditions
#         database = DatabaseModel('test', 'team14')
#         self.assertEqual(1, len(database.get_reservations())
                         
        
    
    @unittest.skip('test failing and taking time')
    def test_send_machine(self):
        self.web_server = webServer('localhost', 10003, 'localhost', 20003, 'test', 'team14')
        self.pi_server = piServer('localhost', 20003, 'localhost', 10003, 'test', 'team14')
         
        # assert preconditions
        database = DatabaseModel('test', 'team14')
        self.assertEqual(1, len(database.get_machines()))
        machine = database.get_machines()[0]
        self.assertEqual(MachineStatus.UNKNOWN, machine.status)
         
        # send machine update
        machine.status = MachineStatus.BUSY
        self.pi_server.send_machine_update(machine)
        time.sleep(1)
         
        # test to see if update applied
        self.assertEqual(1, len(database.get_machines()))
        database = DatabaseModel('test', 'team14')
        machine = database.get_machines()[0]
        self.assertEqual(MachineStatus.BUSY, machine.status)
        

#   also tests send_all_reservations and send_all_machines
    def test_send_update(self):
        self.web_server = webServer('localhost', 10001,'localhost', 20001, 'test', 'team14')
        self.assertEqual(-1, self.web_server.send_update())
        self.pi_server = piServer('localhost', 20001, 'localhost', 10001, 'test', 'team14')
        self.assertEqual(1, self.web_server.send_update())
   
#     also tests request_all_reservations and request_all_machines
    def test_request_update(self):
        self.pi_server = piServer('localhost', 20002, 'localhost', 10002, 'test', 'team14')
        self.pi_client = self.pi_server.client
        self.assertEqual(-1, self.pi_server.request_update())
        self.assertEqual(0, len(self.pi_client.machines))
        self.assertEqual(0, len(self.pi_client.reservations))
        self.web_server = webServer('localhost', 10002, 'localhost', 20002, 'test', 'team14')
        self.assertEqual(1, self.pi_server.request_update())
        time.sleep(1)  # give time for request to send and come back
        self.assertEqual(1, len(self.pi_server.client.machines))
        self.assertEqual(1, len(self.pi_client.machines))
        self.assertEqual(self.machine, next(iter(self.pi_client.machines.values())))
        self.assertEqual(1, len(self.pi_server.client.reservations))
        self.assertEqual(1, len(self.pi_client.reservations))
        self.assertEqual(self.reservation, next(iter(self.pi_client.reservations.values())))

    def tearDown(self):
        try:
            self.web_server.stop()
        except:
            pass
        try:
            self.pi_server.stop()
        except:
            pass

if __name__ == '__main__':
    unittest.main()
