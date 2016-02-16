#!/usr/bin/env python3

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import MetaData

# Create our base class
Meta = MetaData()
Base = declarative_base(metadata=Meta)
