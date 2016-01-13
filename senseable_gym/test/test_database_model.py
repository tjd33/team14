#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Built-in Imports
import unittest

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

        self.db.execute_sql_script('./senseable_gym/sg_database/sg_schema.sql')
        self.db._empty_db()

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
        machine = Machine(1, MachineType.TREADMILL, [1, 1, 1])
        self.assertEqual(machine.get_status(), MachineStatus.UNKNOWN)

        self.db.add_machine(machine)

        test_machine_type = self.db.get_machine_type(1)

        self.assertEqual(test_machine_type, MachineType.TREADMILL)

    def test_add_machine_check_type(self):
        self.assertRaises(ValueError, self.db.add_machine, 'not machine type')
        self.assertRaises(ValueError, self.db.add_machine, 1)

    def test_add_duplicate_machine(self):
        pass

if __name__ == "__main__":
    unittest.main()
