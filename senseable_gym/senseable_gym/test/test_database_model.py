#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Built-in Imports
import unittest

# Local Imports
from senseable_gym.sg_database.database import DatabaseModel


class TestDatabaseModel(unittest.TestCase):
    def setUp(self):
        """
        This will run before every test begins.

        It should put the database in a blank state so that we can
            isolate each test by themselves.
        """
        self.db = DatabaseModel('testdb', 'team14')

        self.db._empty_db()

    def test_execute_sql_script(self):
        self.db.execute_sql_script('./senseable_gym/test/sql_scripts/test1.sql')

        self.db.cursor.execute('SELECT * FROM test')

        rows = self.db.cursor.fetchall()

        self.assertEqual(rows, [(1, 'helloworld')])

    def test_empty_db(self):
        pass

    def test_get_machine(self):
        pass

    def test_get_machines(self):
        pass

    def test_add_machine(self):
        pass

    def test_add_duplicate_machine(self):
        pass

if __name__ == "__main__":
    unittest.main()
