#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Standard Imports
from datetime import datetime

from sqlalchemy import Column, Integer, Sequence, ForeignKey, DateTime
from sqlalchemy.orm import relationship

# Senseable Gym Imports
from senseable_gym.sg_util.base import Base
from senseable_gym.sg_util.machine import Machine
from senseable_gym.sg_util.user import User


class MachineCurrentUser(Base):
    __tablename__ = 'machinecurrentuser'

    relationship_id = Column(Integer, Sequence('relationship_id_seq'), primary_key=True)
    machine_id = Column(Integer, ForeignKey('machine.machine_id'))
    user_id = Column(Integer, ForeignKey('user.user_id'))
    relationship_start = Column(DateTime, nullable=False, default=datetime.now())
    machine = relationship(Machine, lazy='joined')
    # user = relationship('user')

    def __init__(self, machine: Machine, user: User, time=None):
        # self._machine_id = machine.machine_id
        # self._user_id = user.user_id
        self._machine = machine
        self._user = user
        self.machine_id = machine.machine_id
        self.user_id = user.user_id

    def init_on_load(self):
        self.machine = None

    # @property
    # def machine_id(self):
    #     # return self._machine_id
    #     return self._machine.id

    # @property
    # def user_id(self):
    #     return self._user_id

    def __repr__(self):
        return '<Machine: {}, User: {}>'.format(self.machine_id, self.user_id)
