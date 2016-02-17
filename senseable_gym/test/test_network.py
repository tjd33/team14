import unittest
import time
from datetime import datetime

from senseable_gym.sg_database.database import DatabaseModel
from senseable_gym.sg_util.machine import Machine, MachineType
from senseable_gym.sg_util.reservation import Reservation
from senseable_gym.sg_util.user import User
from senseable_gym.sg_util.exception import MachineError
from senseable_gym.sg_util.exception import ReservationError
from senseable_gym.sg_util.exception import UserError
from senseable_gym.sg_network.PI import PIClient
from senseable_gym.sg_network.PI import PIServer
from senseable_gym.sg_network.server import Server
from senseable_gym.sg_network.server import ServerClient


class TestPINetwork(unittest.TestCase):
    def setUp(self):
        database = DatabaseModel(None, 'team14')
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

    def test_send_reservation(self):
        self.PI_client = PIClient('localhost', 10000)
        self.PI_server = PIServer('localhost', 20000, self.PI_client)

        # Assert that initially the reservation is empty
        self.assertEqual({}, self.PI_client.reservations)

        # Now we send a reservation to the client
        self.PI_server.send_reservation(self.reservation)

        # Now we should have a reservation in our client
        self.assertEqual(1, self.PI_client.reservations)
        self.assertEqual(self.reservation, next(iter(self.PI_client.reservations.values())))

    # also tests send_all_reservations and send_all_machines
    def test_send_update(self):
        self.server_client = ServerClient('localhost', 20000, 'test', 'team14')
        self.server = Server('localhost', 10000, self.server_client)
        self.assertEqual(-1, self.server_client.send_update())
        self.PI_client = PIClient('localhost', 10000)
        self.PI_server = PIServer('localhost', 20000, self.PI_client)
        self.assertEqual(1, self.PI_client.request_update())

    # also tests request_all_reservations and request_all_machines
    def test_request_update(self):
        self.PI_client = PIClient('localhost', 10000)
        self.PI_server = PIServer('localhost', 20000, self.PI_client)
        self.assertEqual(-1, self.PI_client.request_update())
        self.assertEqual(0, len(self.PI_client.machines))
        self.assertEqual(0, len(self.PI_client.reservations))
        self.server_client = ServerClient('localhost', 20000, 'test', 'team14')
        self.server = Server('localhost', 10000, self.server_client)
        self.assertEqual(1, self.PI_client.request_update())
        time.sleep(1)  # give time for request to send and come back
        self.assertEqual(1, len(PIServer.client.machines))
        self.assertEqual(1, len(self.PI_client.machines))
        self.assertEqual(self.machine, next(iter(self.PI_client.machines.values())))
        self.assertEqual(1, len(PIServer.client.reservations))
        self.assertEqual(1, len(self.PI_client.reservations))
        self.assertEqual(self.reservation, next(iter(self.PI_client.reservations.values())))

    def tearDown(self):
        try:
            self.server.stop()
        finally:
            pass
        try:
            self.PI_server.stop()
        finally:
            pass

if __name__ == '__main__':
    unittest.main()
