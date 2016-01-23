#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Standard Imports
from sqlalchemy import Column, Integer, Sequence

# Senseable Gym Imports
from senseable_gym.sg_util.base import Base


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, Sequence('user_id_seq'), primary_key=True)
