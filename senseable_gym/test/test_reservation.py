#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Built-In Imports
import unittest
from datetime import date

# Third Party Imports

# Local Imports
from senseable_gym.sg_database.database import DatabaseModel
from senseable_gym.sg_util.machine import Machine, MachineType, MachineStatus
from senseable_gym.sg_util.user import User
from senseable_gym.sg_util.reservation import Reservation


class TestReservation(unittest.TestCase):
    def setUp(self):
        self.db = DatabaseModel(None, 'team14')

        self.m1 = Machine(MachineType.TREADMILL, location=[2, 2, 3])
        self.u1 = User('1', 'f1', 'l1')

        self.db.add_machine(self.m1)
        self.db.add_user(self.u1)

    def test_create_reservation(self):
        res = Reservation(self.m1, self.u1, date(2016, 6, 1))

        self.assertEqual(self.m1, res.machine)
        self.assertEqual(self.u1, res.user)
        self.assertEqual(self.m1.machine_id, res.machine_id)
        self.assertEqual(self.u1.user_id, res.user_id)

        # TODO: Check to make sure _time_of_reservation_creation is correct?
