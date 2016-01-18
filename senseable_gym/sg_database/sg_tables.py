#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This file declares all of the tables that will be used in
    the database model.
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

class Equipment(Base):
    __tablename__ = 'equipment'

    equipment_id = Column(Integer, primary_key=True)
    equipment_type = Column(Integer)
    location = Column(Integer)