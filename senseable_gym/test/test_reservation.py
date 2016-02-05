#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Built-In Imports
import unittest
from datetime import datetime

# Third Party Imports

# Local Imports
from senseable_gym.sg_database.database import DatabaseModel
from senseable_gym.sg_util.machine import Machine, MachineType, MachineStatus
from senseable_gym.sg_util.User import User
from senseable_gym.sg_util.Reservation import Reservation

class TestReservation(unittest.TestClass):
    def setUp(self):
        self.db = DatabaseModel('testdb', 'team14')

        self.m1 = Machine(MachineType.TREADMILL, location=[2, 2, 3])
        self.u1 = User('1', 'f1', 'l1')

        self.res = Reservation(self.m1, self.u1, datetime.date())
