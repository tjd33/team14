# Sqlalchemy Imports
from sqlalchemy import MetaData
from sqlalchemy import Table
from sqlalchemy import Column, Integer

meta = MetaData()

equipment = Table('equipment', meta,
                  Column('equipment_id', Integer, primary_key=True),
                  Column('equipment_type', Integer),
                  Column('location', Integer)
                  )
