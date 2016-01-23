#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Standard Imports
from enum import Enum

from sqlalchemy import Column, Integer, Sequence

from senseable_gym.sg_util.base import Base


class Machine(Base):
    __tablename__ = 'machine'

    id = Column(Integer, Sequence('machine_id_seq'), primary_key=True)
    type = Column(Integer)

    # TODO: See if this is the easiest way to store these in ANY database
    location_x = Column(Integer)
    location_y = Column(Integer)
    location_z = Column(Integer)

    status = Column(Integer)

    def __init__(self, type, location, color=False):
        self._type = type
        self._location = location
        self._status = MachineStatus.UNKNOWN

        # Our variable that holds whether we will print in color or not
        self.color = color

        # Base.__init__(self)

    @property
    def type(self):
        return MachineType(self._type)

    @type.setter
    def type(self):
        if isinstance(type, MachineType):
            self._type = type.value
        else:
            self._type = type

    @property
    def location(self):
        return self._location

    @location.setter
    def location(self, value):
        if len(value) != 3:
            raise ValueError('This is not a proper location')

        self.location_x = value[0]
        self.location_y = value[1]
        self.location_z = value[2]

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
        s = '<id: {}, type: {}, status: {}>'.format(
                str(self.id),
                self.type,
                self.status
                )

        if self.color:
            status_color = self.get_status().color_string()
            s = status_color[0] + s + status_color[1]

        return s


class MachineStatus(Enum):
    UNKNOWN = 0
    OPEN = 1
    BUSY = 2
    RESERVED = 3
    OUT_OF_ORDER = 4

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

    def __str__(self):
        return self.name.capitalize()
