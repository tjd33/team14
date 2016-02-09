#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Standard Imports
from datetime import datetime

# Third Party Imports
from sqlalchemy import Column, Integer, Sequence, ForeignKey, DateTime

# Local Imports
from senseable_gym.sg_util.base import Base
from senseable_gym.sg_util.machine import Machine
from senseable_gym.sg_util.user import User


class Reservation(Base):
    __tablename__ = 'reservation'

    reservation_id = Column(Integer, Sequence('reservation_id_seq'), primary_key=True)
    machine_id = Column(Integer, ForeignKey('machine.machine_id'))
    user_id = Column(Integer, ForeignKey('user.user_id'))
    reservation_time = Column(DateTime, nullable=False)
    _time_of_reservation_creation = Column(DateTime, default=datetime.now())

    def __init__(self, machine: Machine, user: User, time: datetime) -> None:
        self._machine = machine
        self._user = user
        self.reservation_time = time

        self.machine_id = self._machine.machine_id
        self.user_id = self._user.user_id

    @property
    def machine(self):
        return self._machine

    @property
    def user(self):
        return self._user
