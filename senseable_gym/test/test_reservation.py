#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Built-In Imports
import unittest
from datetime import datetime

# Third Party Imports

# Local Imports
from senseable_gym.sg_database.database import DatabaseModel
from senseable_gym.sg_util.machine import Machine, MachineType, MachineStatus
from senseable_gym.sg_util.user import User
from senseable_gym.sg_util.reservation import Reservation
from senseable_gym.sg_util.exception import MachineError, UserError


class TestReservation(unittest.TestCase):
    def setUp(self):
        self.db = DatabaseModel(None, 'team14')

        self.m1 = Machine(MachineType.TREADMILL, location=[2, 2, 3])
        self.u1 = User('1', 'f1', 'l1')

        self.time_1 = datetime(2016, 6, 1, 1, 30, 0)
        self.time_2 = datetime(2016, 6, 1, 2, 30, 0)
        self.time_3 = datetime(2016, 6, 1, 3, 30, 0)
        self.time_4 = datetime(2016, 6, 1, 4, 30, 0)

        self.db.add_machine(self.m1)
        self.db.add_user(self.u1)

    def test_create_reservation(self):
        res = Reservation(self.m1, self.u1, self.time_1, self.time_2)

        self.assertEqual(self.m1, res.machine)
        self.assertEqual(self.u1, res.user)
        self.assertEqual(self.m1.machine_id, res.machine_id)
        self.assertEqual(self.u1.user_id, res.user_id)
        self.assertEqual(self.time_2 - self.time_1, res.reservation_length)

        # TODO: Check to make sure _time_of_reservation_creation is correct?

    def test_reservation_with_bad_inputs(self):
        bad_machine = Machine(MachineType.BICYCLE, location=[1, 2, 3])
        bad_machine.status = MachineStatus.BUSY

        with self.assertRaises(MachineError):
            Reservation(bad_machine, self.u1, self.time_1, self.time_2)

        bad_user = User('2', 'f2', 'l2')

        with self.assertRaises(UserError):
            Reservation(self.m1, bad_user, self.time_1, self.time_2)

        with self.assertRaises(ValueError):
            Reservation(self.m1, self.u1, self.time_2, self.time_1)
