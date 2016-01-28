#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Standard Imports
from sqlalchemy import Column, Integer, Sequence, String

# Senseable Gym Imports
from senseable_gym.sg_util.base import Base


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, Sequence('user_id_seq'), primary_key=True)
    user_name = Column(String(32))
    first_name = Column(String(32))
    last_name = Column(String(32))

    def __init__(self, user_name, first_name, last_name):
        self._user_name = user_name
        self._first_name = first_name
        self._last_name = last_name

    @property
    def full_name(self):
        return self.first_name + ' ' + self.last_name

    @property
    def user_name(self):
        return self._user_name

    @user_name.setter
    def user_name(self, value):
        self._user_name = value

    @property
    def first_name(self):
        return self._first_name

    @first_name.setter
    def first_name(self, value):
        self._first_name = value

    @property
    def last_name(self):
        return self._last_name

    @last_name.setter
    def last_name(self, value):
        self._last_name = value
