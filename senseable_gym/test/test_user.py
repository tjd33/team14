#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Built-in Imports
import unittest

# Third Party Imports

# Local Imports
from senseable_gym.sg_util.user import User


class TestUserTable(unittest.TestCase):
    def setUp(self):
        self.user = User('username', 'first', 'last')
