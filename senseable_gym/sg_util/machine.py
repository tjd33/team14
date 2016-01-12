#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Standard Imports
from enum import Enum


class Machine():
    def __init__(self, id, type, location, color=False):
        self.id = id
        self.type = type
        self.location = location
        self.status = MachineStatus.UNKNOWN

        # Our variable that holds whether we will print in color or not
        self.color = color

    # Getters
    def get_id(self):
        return self.id

    def get_status(self):
        return self.status

    def get_location(self):
        return self.location

    def get_type(self):
        return self.type

    # Setters
    def set_status(self, status):
        self.status = status

    def set_location(self, location):
        self.location = location

    # String representation
    def __str__(self):
        s = str(self.id)

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
