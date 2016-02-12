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
from senseable_gym.sg_util.exception import MachineError, UserError


class Reservation(Base):
    __tablename__ = 'reservation'

    reservation_id = Column(Integer, Sequence('reservation_id_seq'), primary_key=True)
    machine_id = Column(Integer, ForeignKey('machine.machine_id'))
    user_id = Column(Integer, ForeignKey('user.user_id'))
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    _time_of_reservation_creation = Column(DateTime, default=datetime.now())

    def __init__(self, machine: Machine, user: User, start_time: datetime, end_time: datetime) -> None:
        if machine.machine_id is None:
            raise MachineError('Machine must already be in the database')

        if user.user_id is None:
            raise UserError('User must already be in the database')

        if start_time > end_time:
            raise ValueError('end_time must be greater than start_time')

        self._machine = machine
        self._user = user
        self.start_time = start_time
        self.end_time = end_time

        self.machine_id = self._machine.machine_id
        self.user_id = self._user.user_id

    @property
    def machine(self):
        return self._machine

    @property
    def user(self):
        return self._user

    @property
    def reservation_length(self):
        return self.end_time - self.start_time

    def is_overlapping_reservation(self, res) -> bool:
        "Returns true if res overlaps this reservation"
        if self.start_time >= res.start_time and self.start_time <= res.end_time:
            return True

        if self.end_time >= res.start_time and self.end_time <= res.end_time:
            return True

    def __repr__(self):
        return '<M: {}, U: {}, Start: {}, End: {}>'.format(
                self.machine_id, self.user_id, self.start_time, self.end_time)
