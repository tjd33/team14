#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Standard Imports
from sqlalchemy import Column, Integer, Sequence, String, ForeignKey

# Senseable Gym Imports
from senseable_gym import Base

class MachineCurrentUser(Base):
    __tablename__ = 'machinecurrentuser'

    machine_id = Column(Integer, ForeignKey('machine.id'), primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'))
