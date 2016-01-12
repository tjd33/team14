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

# Third Party Imports
import psycopg2

# Local Imports


class Database():
    def __init__(self, dbname, user, password=None, filename=None):
        """TODO: Docstring for __init__.

        :dbname: TODO
        :user: TODO
        :password: TODO
        :filename: TODO
        :returns: TODO

        """

        # Get the logger
        self.logger = logging.getLogger(logger_name)
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
        pass
