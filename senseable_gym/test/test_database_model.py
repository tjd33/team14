#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Built-in Imports
import unittest

# Third Party Imports
from sqlalchemy.exc import IntegrityError

# Local Imports
from senseable_gym.sg_database.database import DatabaseModel

from senseable_gym.sg_util.machine import Machine
from senseable_gym.sg_util.machine import MachineType
from senseable_gym.sg_util.machine import MachineStatus


class TestDatabaseModel(unittest.TestCase):
    def setUp(self):
        """
        This will run before every test begins.

        It should put the database in a blank state so that we can
            isolate each test by themselves.
        """
        self.db = DatabaseModel('testdb', 'team14')

    @unittest.skip('Not implemented currently')
    def test_execute_sql_script(self):
        self.db.execute_sql_script('./senseable_gym/test/sql_scripts/test1.sql')

        # Get everything from test
        self.db.cursor.execute('SELECT * FROM test')

        # Actually read the information
        rows = self.db.cursor.fetchall()

        # Assert that it equals what we inserted in test1
        self.assertEqual(rows, [(1, 'helloworld')])

        # Drop the test table
        self.db.cursor.execute('DROP TABLE test')

    def test_empty_db(self):
        pass

    def test_get_machine(self):
        pass

    def test_get_machines(self):
        pass

    def test_add_machine(self):
        machine = Machine(type=MachineType.TREADMILL, location=[1, 1, 1], status=0)
        self.assertEqual(machine.get_status(), MachineStatus.UNKNOWN)

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

if __name__ == "__main__":
    unittest.main()
