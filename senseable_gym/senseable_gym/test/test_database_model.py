#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Built-in Imports
import unittest

# Local Imports
from senseable_gym.sg_database.database import DatabaseModel


class TestDatabaseModel(unittest.TestCase):
    def setUp(self):
        """TODO: Docstring for setUp.


        """
        db = DatabaseModel('testdb', 'team14')

        db.add_machine('machine1')

if __name__ == "__main__":
    print('Testing...')
