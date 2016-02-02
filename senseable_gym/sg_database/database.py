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
from sqlalchemy import create_engine
from sqlalchemy import MetaData
from sqlalchemy import inspect
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
# Local Imports
# from senseable_gym import logger_name

from senseable_gym.sg_util.base import Base
from senseable_gym.sg_util.machine import Machine, MachineStatus
from senseable_gym.sg_util.user import User

# Relationships
from senseable_gym.sg_util.relationships import MachineCurrentUser


logger_name = 'senseable_logger'    # This is temporary until I can get the logger setup


class DatabaseModel():
    def __init__(self, dbname, user, password=None):
        """TODO: Docstring for __init__.
        """
        # Get the logger
        self.logger = logging.getLogger(logger_name)

        # Set up the connection to the database
        self.engine = create_engine('sqlite://')

        self.meta = MetaData(self.engine)

        self.base = Base
        self.base.metadata.bind = self.engine
        self.base.metadata.create_all()

        self.session = sessionmaker(bind=self.engine)()

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

    def add_machine(self, machine):
        # Make sure that we're actually getting a machine object passed in
        if not isinstance(machine, Machine):
            raise ValueError('Machine Objects Only')

        result = self.session.query(Machine).filter(Machine.machine_id == machine.machine_id).all()

        # TODO: This is not currently working as expected.
        if result == list():
            self.session.add(machine)
        else:
            raise IntegrityError('A machine object can only be added once')

        self.session.commit()

    def remove_machine(self, id):
        machine = self.get_machine(id)

        self.session.delete(machine)

    # Getters

    def get_machines(self):
        return self.session.query(Machine).all()

    def get_machine(self, id):
        # Query the equipment table to find the machine by its ID
        #   Then, since the ID is a primary key, there can only be one of them
        #   So, return the first one in that list.
        return self.session.query(Machine).filter(Machine.machine_id == id).one()

    def get_machine_status(self, id):
        return self.get_machine(id).status

    def get_machine_location(self, id):
        return self.get_machine(id).location

    def get_machine_type(self, id):
        return self.get_machine(id).type

    # Setters
    def set_machine_status(self, id, status):
        self.get_machine(id).status = status
        self.session.commit()

    def set_machine_location(self, id, location):
        self.get_machine(id).location = location
        self.session.commit()

    def add_user(self, user):
        # Make sure that we're actually getting a machine object passed in
        if not isinstance(user, User):
            raise ValueError('Machine Objects Only')

        result = self.session.query(User).filter(User.user_id == user.user_id).all()

        # TODO: This is not currently working as expected.
        if result == list():
            self.session.add(user)
        else:
            raise IntegrityError('A user object can only be added once')

        self.session.commit()

    def get_user(self, user_id):
        return self.session.query(User).filter(User.user_id == user_id).one()

    def set_user_machine_status(self,
                                machine: Machine,
                                user: User,
                                status: MachineStatus = MachineStatus.BUSY) -> MachineCurrentUser:
        """
        This function should update the relationship between users and machines,

        :param machine: Machine Object
        :param user: User Object
        :param status: Optional Status parameter
        """
        machine.status = status
        relationship = MachineCurrentUser(machine, user)

        self.session.add(relationship)

        return relationship

    def get_machine_user_relationships(self):
        """
        Get the current machine and user relationships
        :return: A list of MachineCurrentUser objects
        """
        rel = self.session.query(MachineCurrentUser).one()

        # TODO: I believe this is not the correct way to repopulate the relationship
        #       However, I don't really see a different way to do it now. Maybe
        #       I will see it later though.
        rel._machine = self.session.query(Machine).filter(Machine.machine_id == rel.machine_id).one()
        rel._user = self.session.query(User).filter(User.user_id == rel.user_id).one()

        return rel
