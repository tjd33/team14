#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Standard Imports
from sqlalchemy import Column, Integer, Sequence, String, Boolean
# from sqlalchemy.orm import relationship

# Senseable Gym Imports
from senseable_gym.sg_util.base import Base


class User(Base):
    __tablename__ = 'user'

    def __init__(self, user_name: str,  first_name: str, last_name: str, password_hash: str = ''):
        self._user_name = user_name
        self._first_name = first_name
        self._last_name = last_name
        self._password = password_hash
        self._authenticated = False
        self._administrator = False

    user_id = Column(Integer, Sequence('user_id_seq'), primary_key=True)
    _user_name = Column(String(32))
    _first_name = Column(String(32))
    _last_name = Column(String(32))
    _password = Column(String(32))
    _authenticated = Column(Boolean(False))
    _administrator = Column(Boolean(False))

    @property
    def full_name(self) -> str:
        return self.first_name + ' ' + self.last_name

    @property
    def user_name(self) -> str:
        return self._user_name

    @user_name.setter
    def user_name(self, value):
        self._user_name = value

    @property
    def first_name(self) -> str:
        return self._first_name

    @first_name.setter
    def first_name(self, value):
        self._first_name = value

    @property
    def last_name(self) -> str:
        return self._last_name

    @last_name.setter
    def last_name(self, value):
        self._last_name = value

    def __str__(self):
        return '<User: {}, Name: {}>'.format(
                self.user_name,
                self.full_name
                )

    @property
    def password(self) -> str:
        return self._password
        
    @password.setter
    def password(self, value):
        self._password = value

    def is_active(self):
        return True

    def get_id(self):
        return self._user_name

    def is_authenticated(self):
        return self._authenticated

    @property
    def authenticated(self):
        return self._authenticated

    @authenticated.setter
    def authenticated(self, value):
        self._authenticated = value
        
    @property
    def administrator(self):
        return self._administrator
        
    @administrator.setter
    def administrator(self, value):
        self._administrator = value

    def is_anonymous(self):
        return False
