#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Standard Imports
import unittest

# Senseable Gym Imports
from senseable_gym.sg_database.database import DatabaseModel
from senseable_gym.sg_database.database_updater import update_all_machine_statuses
from senseable_gym.sg_util.machine import Machine, MachineStatus, MachineType


class TestDatabaseUpdater(unittest.TestCase):
    def setUp(self):
        self.db = DatabaseModel(None, 'user', 'password')

    def test_basic_reservation_update(self):
        m = Machine(MachineType.TREADMILL, [1, 1, 1])
        m.status = MachineStatus.BUSY

        self.db.add_machine(m)

        # update_all_machine_statuses(self.db)

if __name__ == "__main__":
    unittest.main()
