#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Built-in Imports
import unittest

# Third Party Imports

# Local Imports
from senseable_gym.sg_util.user import User


class TestUserTable(unittest.TestCase):
    def setUp(self):
        self.expected_attributes = {
                'user_name': 'username',
                'first_name': 'first',
                'last_name': 'last'
                }
        self.user = User(
                self.expected_attributes['user_name'],
                self.expected_attributes['first_name'],
                self.expected_attributes['last_name']
                )

    def test_attributes(self):
        for attr, value in self.expected_attributes.items():
            self.assertEqual(getattr(self.user, attr, None), value)

    def test_modify_attributes(self):
        self.expected_attributes['first_name'] = 'new'
        self.user.first_name = self.expected_attributes['first_name']

        for attr, value in self.expected_attributes.items():
            self.assertEqual(getattr(self.user, attr, None), value)

    def test_get_full_name(self):
        expected_fullname = self.expected_attributes['first_name'] + \
                ' ' + \
                self.expected_attributes['last_name']

        self.assertEqual(self.user.full_name, expected_fullname)
