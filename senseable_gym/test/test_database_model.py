#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Built-in Imports
import unittest
from datetime import datetime

# Third Party Imports

# Local Imports
from senseable_gym.sg_database.database import DatabaseModel

from senseable_gym.sg_util.machine import Machine, MachineType, MachineStatus
from senseable_gym.sg_util.user import User
from senseable_gym.sg_util.reservation import Reservation
from senseable_gym.sg_util.exception import MachineError, UserError, ReservationError

class TestDatabaseModel(unittest.TestCase):
    def setUp(self):
        """
        This will run before every test begins.

        It should put the database in a blank state so that we can
            isolate each test by themselves.
        """
        self.db = DatabaseModel(None, 'team14')

        self.time_1 = datetime(2050, 1, 1, 1, 0, 0)
        self.time_2 = datetime(2050, 1, 2, 1, 0, 0)
        self.time_3 = datetime(2050, 1, 3, 1, 0, 0)
        self.time_4 = datetime(2050, 1, 4, 1, 0, 0)

    @unittest.skip('Not yet implemented')
    def test_empty_db(self):
        pass

    @unittest.skip('Not yet implemented')
    def test_get_machine(self):
        pass

    def test_get_machine_by_location(self):
        machine = Machine(type=MachineType.TREADMILL, location=[1, 1, 1])

        self.db.add_machine(machine)

        test_machine = self.db.get_machine_by_location([1, 1, 1])

        self.assertEqual(test_machine.type, MachineType.TREADMILL)

    def test_add_machine(self):
        machine = Machine(type=MachineType.TREADMILL, location=[1, 1, 1])
        self.assertEqual(machine.status, MachineStatus.UNKNOWN)

        self.db.add_machine(machine)

        test_machine_type = self.db.get_machine_type(1)

        self.assertEqual(test_machine_type, MachineType.TREADMILL)

    def test_add_machine_two(self):
        machine1 = Machine(MachineType.TREADMILL, [1, 1, 1])
        machine2 = Machine(MachineType.BICYCLE, [2, 2, 2])

        self.db.add_machine(machine1)
        self.db.add_machine(machine2)

        test_machine1 = self.db.get_machine_type(1)
        test_machine2 = self.db.get_machine_type(2)

        self.assertNotEqual(test_machine1, test_machine2)

        self.assertEqual(test_machine1, MachineType.TREADMILL)
        self.assertEqual(test_machine2, MachineType.BICYCLE)

    def test_add_machine_check_type(self):
        self.assertRaises(ValueError, self.db.add_machine, 'not machine type')
        self.assertRaises(ValueError, self.db.add_machine, 1)

    def test_add_duplicate_machine(self):
        machine1 = Machine(MachineType.TREADMILL, [1, 1, 1])

        self.db.add_machine(machine1)

        with self.assertRaises(MachineError):
            self.db.add_machine(machine1)

    def test_get_machine_status(self):
        machine = Machine(MachineType.TREADMILL, [1, 1, 1])

        self.db.add_machine(machine)

        self.assertEqual(self.db.get_machine_status(1), MachineStatus.UNKNOWN)

        self.db.set_machine_status(1, MachineStatus.BUSY)

        self.assertEqual(self.db.get_machine_status(1), MachineStatus.BUSY)

    def test_get_machines(self):
        machine1 = Machine(MachineType.BICYCLE, [1, 2, 2])
        machine2 = Machine(MachineType.TREADMILL, [1, 3, 3])

        self.db.add_machine(machine1)
        self.db.add_machine(machine2)

        machines = self.db.get_machines()

        self.assertEqual(machines, [machine1, machine2])
        self.assertNotEqual(machines, [machine1, machine1])

    def test_remove_machine(self):
        machine1 = Machine(MachineType.BICYCLE, [1, 2, 2])
        machine2 = Machine(MachineType.TREADMILL, [1, 3, 3])

        self.db.add_machine(machine1)
        self.db.add_machine(machine2)

        machines = self.db.get_machines()

        self.assertEqual(machines, [machine1, machine2])
        self.assertNotEqual(machines, [machine1, machine1])

        self.db.remove_machine(machine1.machine_id)

        machines = self.db.get_machines()

        self.assertEqual(machines, [machine2])

    def test_add_user(self):
        user = User('user', 'first', 'last')

        self.db.add_user(user)

        self.assertEqual(user.user_id, 1)

        self.assertEqual(self.db.get_user(1), user)

    def test_add_duplicate_user(self):
        user = User('user', 'first', 'last')

        self.db.add_user(user)

        with self.assertRaises(UserError):
            self.db.add_user(user)

    def test_add_reservation(self):
        machine = Machine(MachineType.BICYCLE, [1, 1, 1])
        user = User('u1', 'f1', 'l1')

        self.db.add_machine(machine)
        self.db.add_user(user)

        res = Reservation(machine, user, self.time_1, self.time_2)
        self.db.add_reservation(res)

    def test_add_overlapping_reservation_different_machine(self):
        machine_1 = Machine(MachineType.BICYCLE, [1, 1, 1])
        user_1 = User('u1', 'f1', 'l1')

        self.db.add_machine(machine_1)
        self.db.add_user(user_1)

        machine_2 = Machine(MachineType.BICYCLE, [2, 2, 2])
        user_2 = User('u2', 'f2', 'l2')

        self.db.add_machine(machine_2)
        self.db.add_user(user_2)

        res_1 = Reservation(machine_1, user_1, self.time_1, self.time_3)
        self.db.add_reservation(res_1)

        res_2 = Reservation(machine_2, user_2, self.time_2, self.time_4)
        self.db.add_reservation(res_2)

    def test_add_overlapping_reservation_same_machine(self):
        machine = Machine(MachineType.BICYCLE, [1, 1, 1])
        user_1 = User('u1', 'f1', 'l1')
        user_2 = User('u2', 'f2', 'l2')

        self.db.add_machine(machine)
        self.db.add_user(user_1)
        self.db.add_user(user_2)

        res_1 = Reservation(machine, user_1, self.time_1, self.time_3)
        self.db.add_reservation(res_1)

        with self.assertRaises(ReservationError):
            res_2 = Reservation(machine, user_2, self.time_2, self.time_4)
            self.db.add_reservation(res_2)

    def test_add_overlapping_reservation_same_user(self):
        machine_1 = Machine(MachineType.BICYCLE, [1, 1, 1])
        machine_2 = Machine(MachineType.BICYCLE, [2, 2, 2])
        user = User('u1', 'f1', 'l1')

        self.db.add_machine(machine_1)
        self.db.add_machine(machine_2)
        self.db.add_user(user)

        res_1 = Reservation(machine_1, user, self.time_1, self.time_3)
        self.db.add_reservation(res_1)

        with self.assertRaises(ReservationError):
            res_2 = Reservation(machine_2, user, self.time_2, self.time_4)
            self.db.add_reservation(res_2)

    def test_current_machine_user_relationship(self):
        user = User('user', 'first', 'last')
        machine = Machine(MachineType.BICYCLE, [1, 2, 2])

        self.db.add_user(user)
        self.db.add_machine(machine)

        self.assertEqual(machine.machine_id, 1)
        self.assertEqual(user.user_id, 1)

        self.db.set_user_machine_status(machine=machine, user=user)

        rel = self.db.get_machine_user_relationships(machine)

        self.assertEqual(rel._machine, machine)
        self.assertEqual(rel._user, user)

    def test_wrong_machine_user_relationship(self):
        user = User('user', 'first', 'last')
        bad_user = User('this', 'is', 'bad')

        machine = Machine(MachineType.BICYCLE, [1, 2, 2])

        # Make a relationship without anything in the database
        self.db.set_user_machine_status(machine, bad_user)
        # self.db.get_machine_user_relationships(machine)

        self.db.add_user(user)
        self.db.add_machine(machine)

        # Make a relationship with a user that is not in the database
        self.db.set_user_machine_status(machine, bad_user)


if __name__ == "__main__":
    unittest.main()
