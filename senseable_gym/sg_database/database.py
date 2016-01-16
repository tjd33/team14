#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This file contains the database functions necessary to be used by any aspect
    of the senseable gym. It will try and abstract all the sql away from what
    we are doing and provide python interfaces for them

TJ DeVries
"""

# Built-in Imports
import logging
import re

# Third Party Imports
from sqlalchemy import create_engine
from sqlalchemy import MetaData
from sqlalchemy import inspect, select
from sqlalchemy import Table
from sqlalchemy import Column, Integer, String

# Local Imports
# from senseable_gym import logger_name

from senseable_gym.sg_util.machine import Machine
# from senseable_gym.sg_util.machine import MachineStatus
from senseable_gym.sg_util.machine import MachineType

logger_name = 'senseable_logger'    # This is temporary until I can get the logger setup


class DatabaseModel():
    def __init__(self, dbname, user, password=None):
        """TODO: Docstring for __init__.

        :dbname: TODO
        :user: TODO
        :password: TODO
        :returns: TODO

        """
        # Get the logger
        self.logger = logging.getLogger(logger_name)

        # Set up the connection to the database
        self.engine = create_engine('sqlite://')

        self.meta = MetaData(self.engine)

        self.equipment = Table('equipment', self.meta,
                               Column('equipment_id', Integer, primary_key=True),
                               Column('equipment_type', Integer),
                               Column('location', Integer)
                               )

        self.equipment.create()

    def _empty_db(self):
        """TODO: Docstring for _empty_db.
        :returns: TODO

        """
        pass

    def _print_table(self, table_name):
        """
        A function to quickly print the contents of a table.
        Currently to just be used for debugging purposes.
        """
        # Fetch the results
        if table_name not in self.meta.tables:
            raise ValueError('Table `{}` not found in database'.format(table_name))

        insp = inspect(self.engine)
        rows = insp.get_columns(table_name)

        # Print the results
        self.logger.info('Printing from table `{}`'.format(table_name))
        for row in rows:
            print(row)

    def execute_sql_script(self, filename):
        """
        This will execute a generic sql script.
            This will primarily be used to create the database from a
            script that was generated in some other way and saved
            as an SQL script.

        :filename: string containing the path to the filename
            of the sql script
        :returns: None

        """
        self.logger.info('Executing SQL script file: {}'.format(filename))

        # Initialize an empty statement
        statement = ''

        with open(filename, 'r') as f:
            for line in f:
                if re.match(r'--', line):
                    # Ignore sql comment lines
                    continue
                if not re.search(r'[^-;]+;', line):
                    # Keep appending lines that don't end
                    statement = statement + line
                else:
                    # Append the last line that we need
                    statement = statement + line

                    self.logger.debug('Executing SQL Statment: {}'.format(statement))

                    self.cursor.execute(statement)

                    # Now reset our statement
                    statement = ''

    def add_machine(self, machine):
        # Make sure that we're actually getting a machine object passed in
        if not isinstance(machine, Machine):
            raise ValueError('Machine Objects Only')

        # Now that we know we have a machine object, we can insert its information into our database

        ins1 = self.equipment.insert().values(
                    equipment_id=machine.get_id(),
                    equipment_type=machine.get_type().value,
                    location=1
                )

        with self.engine.connect() as con:
            con.execute(ins1)

    def remove_machine(self, id):
        pass

    # Getters

    def get_machines(self):
        pass

    def get_machine(self, id):
        with self.engine.connect() as con:
            query = select([self.equipment]).where(
                    self.equipment.c.equipment_id == id)

            rs = con.execute(query)

            machine_query = rs.fetchall()[0]

        return Machine(machine_query['equipment_id'],
                       MachineType(machine_query['equipment_type']),
                       machine_query['location'])

    def get_machine_status(self, id):
        pass

    def get_machine_location(self, id):
        pass

    def get_machine_type(self, id):
        current_machine = self.get_machine(id)

        return current_machine.get_type()

    # Setters

    def set_machine_status(self, id, status):
        pass

    def set_machine_location(self, id, location):
        pass
