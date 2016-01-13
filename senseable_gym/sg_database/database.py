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
import psycopg2

# Local Imports
# from senseable_gym import logger_name

from senseable_gym.sg_util.machine import Machine
# from senseable_gym.sg_util.machine import MachineStatus
# from senseable_gym.sg_util.machine import MachineType

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
        if password:
            self.connection = psycopg2.connect(dbname=dbname, user=user, password=password)
        else:
            self.connection = psycopg2.connect(dbname=dbname, user=user)

        self.cursor = self.connection.cursor()

    def _empty_db(self):
        """TODO: Docstring for _empty_db.
        :returns: TODO

        """
        # self.cursor.execute('truncate table if exists equipment;')
        pass

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
        if not isinstance(machine, Machine):
            raise ValueError('Machine Objects Only')

    def remove_machine(self, id):
        pass

    # Getters

    def get_machines(self):
        pass

    def get_machine_status(self, id):
        pass

    def get_machine_location(self, id):
        pass

    def get_machine_type(self, id):
        pass

    # Setters

    def set_machine_status(self, id, status):
        pass

    def set_machine_location(self, id, location):
        pass
