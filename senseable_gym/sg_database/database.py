#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# {{{ Docstring
"""
This file contains the database functions necessary to be used by any aspect
    of the senseable gym. It will try and abstract all the sql away from what
    we are doing and provide python interfaces for them

TJ DeVries
"""
# }}}
# {{{ Imports
# Built-in Imports
import logging
from typing import List

# Third Party Imports
from sqlalchemy import create_engine, and_
from sqlalchemy import MetaData
from sqlalchemy import inspect
from sqlalchemy.orm import sessionmaker, scoped_session

# Local Imports
from senseable_gym import EXTRA_DEBUG, global_logger_name
from senseable_gym.sg_util.base import Base
from senseable_gym.sg_util.machine import Machine, MachineStatus
from senseable_gym.sg_util.user import User

# Relationships
from senseable_gym.sg_util.relationships import MachineCurrentUser
from senseable_gym.sg_util.reservation import Reservation
from senseable_gym.sg_util.exception import MachineError, UserError, ReservationError

# }}}


class DatabaseModel():
    # {{{ Initialization
    def __init__(self, dbname, user, password=None):
        """TODO: Docstring for __init__.
        """
        # Get the logger
        self.logger = logging.getLogger(global_logger_name + '.database')

        # Set up the connection to the database
        if dbname:
            self.engine = create_engine('sqlite:///{}.db'.format(dbname))
        else:
            self.engine = create_engine('sqlite://')

        self.meta = MetaData(self.engine)

        self.base = Base
        self.base.metadata.bind = self.engine
        self.base.metadata.create_all()

        self.session_factory = sessionmaker(bind=self.engine)
        self.session = scoped_session(self.session_factory)()

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

    # }}}
    # {{{ Adders
    def add_machine(self, machine):
        # Make sure that we're actually getting a machine object passed in
        if not isinstance(machine, Machine):
            raise ValueError('Machine Objects Only')

        # Check to make sure machine is valid
        result_loc = self.session.query(Machine).filter(and_(
            Machine._location_x == machine._location_x,
            Machine._location_y == machine._location_y,
            Machine._location_z == machine._location_z)
            ).all()

        # TODO: This is not currently working as expected.
        if not result_loc:
            # This means the machine has not been added with the same location
            self.logger.debug('Adding machine at location {}'.format(
                machine.location))
            self.session.add(machine)
        else:
            # We have entered a duplicate machine, and that needs to be handled
            if result_loc[0].type == machine.type:
                raise MachineError('This machine object has already been added before.\n\tOriginal Machine ID: {}'.format(
                    result_loc[0].machine_id))
            else:
                raise MachineError('A machine object has already been added in this location.\n\tOriginal Machine ID: {}'.format(
                    result_loc[0].machine_id))

        self.session.commit()

    def add_user(self, user):
        # Make sure that we're actually getting a machine object passed in
        if not isinstance(user, User):
            raise ValueError('User Objects Only')

        result = self.session.query(User).filter(User.user_id == user.user_id).all()

        # TODO: This is not currently working as expected.
        if not result:
            self.session.add(user)
        else:
            raise UserError('A user object can only be added once')

        self.session.commit()

    def add_reservation(self, res: Reservation) -> None:
        """
        Adds a reservation to the database.
        Also checks for overlapping pertinent reservations.
        """
        machine_reservations = self.session.query(Reservation).filter(
                Reservation.machine_id == res.machine_id).all()
        self.logger.log(EXTRA_DEBUG, 'Machine {} Reservations: {}'.format(
                            res.machine_id, machine_reservations)
                        )

        for m_r in machine_reservations:
            if res.is_overlapping_reservation(m_r):
                raise ReservationError('Overlapping Reservations with Machine {}'.format(
                    res.machine_id))

        user_reservations = self.session.query(Reservation).filter(
                Reservation.user_id == res.user_id).all()
        self.logger.debug('User {} Reservations: {}'.format(
            res.user_id, user_reservations))

        for u_r in user_reservations:
            if res.is_overlapping_reservation(u_r):
                raise ReservationError('Overlapping Reservations with User {}'.format(
                    res.user_id))

        self.session.add(res)

        self.session.commit()

    # }}}
    # {{{ Removers
    def remove_machine(self, id):
        machine = self.get_machine(id)

        self.session.delete(machine)

    # }}}
    # {{{ Getters
    def get_machines(self) -> List[Machine]:
        return self.session.query(Machine).all()

    def get_machine(self, id) -> Machine:
        # Query the equipment table to find the machine by its ID
        #   Then, since the ID is a primary key, there can only be one of them
        #   So, return the first one in that list.
        return self.session.query(Machine).filter(Machine.machine_id == id).one()

    def get_machine_by_location(self, location) -> Machine:
        # This is used to get a machine by a specific location.
        #   This is useful because locations need to be unique
        return self.session.query(Machine).filter(and_(
            Machine._location_x == location[0],
            Machine._location_y == location[1],
            Machine._location_z == location[2])
            ).one()

    def get_machine_status(self, id):
        return self.get_machine(id).status

    def get_machine_location(self, id):
        return self.get_machine(id).location

    def get_machine_type(self, id):
        return self.get_machine(id).type

    def get_users(self):
        return self.session.query(User).all()

    def get_user(self, user_id):
        return self.session.query(User).filter(User.user_id == user_id).one()

    def get_machine_user_relationships(self, machine):
        """
        Get the current machine and user relationships
        :return: A list of MachineCurrentUser objects
        """
        rel = self.session.query(MachineCurrentUser).filter(MachineCurrentUser.machine_id == machine.machine_id).one()

        # TODO: I believe this is not the correct way to repopulate the relationship
        #       However, I don't really see a different way to do it now. Maybe
        #       I will see it later though.
        rel._machine = self.session.query(Machine).filter(Machine.machine_id == rel.machine_id).one()
        rel._user = self.session.query(User).filter(User.user_id == rel.user_id).one()

        return rel

    def get_reservations(self):
        return self.session.query(Reservation).all()

    def get_reservations_by_machine(self, machine):
        return self.session.query(Reservation).filter(
                Reservation.machine_id == machine.machine_id).all()

    def get_reservations_by_machine_id(self, machine_id):
        return self.session.query(Reservation).filter(
                Reservation.machine_id == machine_id).all()

    # }}}
    # {{{ Setters
    def set_machine_status(self, id, status):
        self.get_machine(id).status = status
        self.session.commit()

    def set_machine_location(self, id, location):
        self.get_machine(id).location = location
        self.session.commit()

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

    # }}}
