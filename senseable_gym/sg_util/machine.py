#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Standard Imports
from enum import Enum

from sqlalchemy import Column, Integer, Sequence
from sqlalchemy import orm
from sqlalchemy.ext.declarative import declarative_base

# Create our base class
Base = declarative_base()


class Machine(Base):
    __tablename__ = 'machine'

    id = Column(Integer, Sequence('machine_id_seq'), primary_key=True)
    type = Column(Integer)
    location = Column(Integer)
    status = Column(Integer)

    def __init__(self, type, location, status=None, color=False):
        if isinstance(type, MachineType):
            self.type = type.value
        else:
            self.type = type

        self.location = 1

        if status is None:
            status = MachineStatus.UNKNOWN

        if isinstance(status, MachineStatus):
            self.status = status.value
        else:
            self.status = status

        # Our variable that holds whether we will print in color or not
        self.color = color

        # Base.__init__(self)

    @orm.reconstructor
    def init_on_load(self):
        if isinstance(self.type, MachineType):
            self.type = self.type.value
        else:
            self.type = self.type

        if isinstance(self.status, MachineStatus):
            self.status = self.status.value
        else:
            self.status = self.status

    # Getters
    def get_id(self):
        return self.id

    def get_status(self):
        return MachineStatus(self.status)

    def get_location(self):
        return self.location

    def get_type(self):
        return MachineType(self.type)

    # Setters
    def set_status(self, status):
        self.status = status

    def set_location(self, location):
        self.location = location

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
