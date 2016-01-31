#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Built-in Imports
import unittest

# Third Party Imports
from sqlalchemy.exc import IntegrityError

# Local Imports
from senseable_gym.sg_database.database import DatabaseModel

from senseable_gym.sg_util.machine import Machine, MachineType, MachineStatus
from senseable_gym.sg_util.user import User


class TestDatabaseModel(unittest.TestCase):
    def setUp(self):
        """
        This will run before every test begins.

        It should put the database in a blank state so that we can
            isolate each test by themselves.
        """
        self.db = DatabaseModel('testdb', 'team14')

    def test_empty_db(self):
        pass

    def test_get_machine(self):
        pass

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

    @unittest.skip('Not implemented')
    def test_add_duplicate_machine(self):
        machine1 = Machine(MachineType.TREADMILL, [1, 1, 1])

        self.db.add_machine(machine1)

        self.assertRaises(IntegrityError, self.db.add_machine, machine1)

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

    @unittest.skip('Not yet implemented')
    def test_add_duplicate_user(self):
        user = User('user', 'first', 'last')

        self.db.add_user(user)
        self.db.add_user(user)

    def test_current_machine_user_relationship(self):
        user = User('user', 'first', 'last')
        machine = Machine(MachineType.BICYCLE, [1, 2, 2])

        self.db.add_user(user)
        self.db.add_machine(machine)

        self.assertEqual(machine.machine_id, 1)
        self.assertEqual(user.user_id, 1)

        self.db.set_user_machine_status(machine=machine, user=user)

        rel = self.db.get_machine_user_relationships()

        self.assertEqual(rel._machine, machine)
        self.assertEqual(rel._user, user)


if __name__ == "__main__":
    unittest.main()
