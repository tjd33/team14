#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Standard Imports
from enum import Enum

from sqlalchemy import Column, Integer, Sequence, Boolean
# from sqlalchemy.orm import relationship

from senseable_gym.sg_util.base import Base


class Machine(Base):
    __tablename__ = 'machine'

    machine_id = Column(Integer, Sequence('machine_id_seq'), primary_key=True)
    _type = Column(Integer)
    _status = Column(Integer)
    color = Column(Boolean)

    # TODO: See if this is the easiest way to store these in ANY database
    _location_x = Column(Integer)
    _location_y = Column(Integer)
    _location_z = Column(Integer)

    # current_user = relationship('MachineCurrentUser', cascade="all, delete-orphan", backref='machine')

    # current_user = relationship('MachineCurrentUser', cascade="all, delete-orphan", backref='machine')

    def __init__(self, type, location, color=False):
        self._type = type.value
        self._location_x = location[0]
        self._location_y = location[1]
        self._location_z = location[2]
        self._status = MachineStatus.UNKNOWN.value

        # Our variable that holds whether we will print in color or not
        self.color = color

        # Base.__init__(self)

    @property
    def type(self):
        return MachineType(self._type)

    @property
    def type_value(self):
        return self._type
        
    @type.setter
    def type(self, type):
        if isinstance(type, MachineType):
            self._type = type.value
        else:
            self._type = type
            

    @property
    def location(self):
        return [self._location_x, self._location_y, self._location_z]

    @location.setter
    def location(self, value):
        if len(value) != 3:
            raise ValueError('This is not a proper location')

        self._location_x = value[0]
        self._location_y = value[1]
        self._location_z = value[2]

        self._location = value

    @property
    def status(self):
        return MachineStatus(self._status)

    @status.setter
    def status(self, value):
        if isinstance(value, MachineStatus):
            self._status = value.value
        else:
            self._status = value

    # String representation
    def __str__(self):
        s = '<id: {0:2}, type: {1:10}, status: {2:7}, location: {3}>'.format(
                str(self.machine_id),
                self.type,
                self.status,
                self.location
                )

        if self.color:
            status_color = self.status.color_string()
            s = status_color[0] + s + status_color[1]

        return s

    def __eq__(self, other):
        return self.machine_id == other.machine_id and \
                self._type == other._type and \
                self._status == other._status and \
                self.color == other.color and \
                self._location_x == other._location_x and \
                self._location_y == other._location_y and \
                self._location_z == other._location_z


class MachineStatus(Enum):
    UNKNOWN = 0
    OPEN = 1
    BUSY = 2
    RESERVED = 3
    RESERVED_AND_BUSY = 4
    OUT_OF_ORDER = 5

    def __str__(self):
        return self.name.capitalize()

    def color_string(self):
        """
        Returns the correct color start and finish sequence

        :returns: A list where the first entry is the start of a color sequence,
            and the second entry is the ending of the color sequence
        """
        color_start = '\033[00m'

        if self.name == "OPEN":
            color_start = '\033[32m'
        elif self.name == "BUSY":
            color_start = '\033[31m'

        return [color_start, '\033[00m']


class MachineType(Enum):
    TREADMILL = 1
    BICYCLE = 2
    ELLIPTICAL = 3
    WEIGHT_MACHINE = 4
    ROWING_MACHINE = 5

    def __str__(self):
        return self.name.capitalize()
