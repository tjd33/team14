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
import time
from typing import List
from datetime import datetime
# from queue import Queue
from threading import Lock

# Third Party Imports
from sqlalchemy import create_engine, and_
from sqlalchemy import inspect
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.pool import StaticPool

# Local Imports
from senseable_gym import EXTRA_DEBUG, global_logger_name
from senseable_gym.sg_util.base import Base, Meta
from senseable_gym.sg_util.machine import Machine, MachineStatus, MachineType
from senseable_gym.sg_util.user import User

# Relationships
from senseable_gym.sg_util.relationships import MachineCurrentUser
from senseable_gym.sg_util.reservation import Reservation
from senseable_gym.sg_util.exception import MachineError, UserError, ReservationError

# }}}

l = Lock()


def enqueue_action(func):
    l.acquire()

    def func_wrapper(*args, **kwargs):
        return func(*args, **kwargs)

    l.release()
    return func


class DatabaseModel():
    # {{{ Initialization
    def __init__(self, dbname, user, password=None):
        """TODO: Docstring for __init__.
        """
        # Get the logger
        self.logger = logging.getLogger(global_logger_name + '.database')

        # Set up the connection to the database
        if dbname:
            self.engine = create_engine('sqlite:///{}.db'.format(dbname),
                                        connect_args={'check_same_thread': False},
                                        poolclass=StaticPool,
                                        )
            # self.engine = create_engine('postgresql://tj_chromebook@localhost:5432/sg',
            #                             poolclass=StaticPool,
            #                             )

        else:
            self.engine = create_engine('sqlite://')

        self.meta = Meta
        self.base = Base
        self.base.metadata.bind = self.engine
        self.base.metadata.create_all()

        self.session_factory = sessionmaker(bind=self.engine, autoflush=True)
        self.session_maker = scoped_session(self.session_factory)
        self.session = self.session_maker()

        # Spawn a thread, and store in self
        # Create a queue for that thread
        # Create

    @enqueue_action
    def _empty_db(self):
        """
        Empties the database of any current records.
            Use with caution :D
        :returns: None
        """
        time.sleep(.5)
        self.meta.drop_all()
        self.meta.create_all()
        self.session.commit()

        # TODO: Delete this if it turns out the two lines above thie
        #           work perfectly fine. Otherwise, we may have to go back to this
        # machines = self.session.query(Machine).delete()
        # users = self.session.query(User).delete()
        # reservations = self.session.query(Reservation).delete()

        # self.logger.debug('Deleted: M={}, U={}, R={}'.format(
        #     machines, users, reservations)
        #     )
        # new_meta = self.meta
        # print(new_meta)
        # with closing(self.engine.connect()) as con:
        #     trans = con.begin()
        #     self.logger.info('Emptying the database')
        #     for table in reversed(new_meta.sorted_tables):
        #         self.logger.debug('Table clearing: {}'.format(table))
        #         con.execute(table.delete())
        #     trans.commit()
        #     self.logger.info('Done emptying the database')

    def _str_table(self, table_name):
        """
        A function to quickly print the contents of a table.
        Currently to just be used for debugging purposes.
        """
        table_str = '| '

        # Fetch the results
        if table_name not in self.meta.tables:
            raise ValueError('Table `{}` not found in database'.format(table_name))

        insp = inspect(self.engine)
        cols = insp.get_columns(table_name)

        # Print the results
        self.logger.debug('Getting Info from table `{}`'.format(table_name))
        for col in cols:
            table_str += str(col['name']) + ' | '

        return table_str

    # }}}
    # {{{ Adders
    @enqueue_action
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

    @enqueue_action
    def add_user(self, user):
        # Make sure that we're actually getting a machine object passed in
        if not isinstance(user, User):
            raise ValueError('User Objects Only')

        result = self.session.query(User).filter(User._user_name == user._user_name).all()

        # TODO: This is not currently working as expected.
        if not result:
            self.session.add(user)
        else:
            raise UserError('A user object can only be added once')

        self.session.commit()

    @enqueue_action
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
        self.session.commit()

    def remove_user(self, id):
        user = self.get_user(id)
        self.session.delete(user)

    # }}}
    # {{{ Getters
    def get_machines(self) -> List[Machine]:
        return self.session.query(Machine).all()

    def get_machine(self, machine_id: int) -> Machine:
        # Query the equipment table to find the machine by its ID
        #   Then, since the ID is a primary key, there can only be one of them
        #   So, return the first one in that list.
        return self.session.query(Machine).filter(Machine.machine_id == machine_id).one()

    def get_machine_by_location(self, location: List[int]) -> Machine:
        # This is used to get a machine by a specific location.
        #   This is useful because locations need to be unique
        return self.session.query(Machine).filter(and_(
            Machine._location_x == location[0],
            Machine._location_y == location[1],
            Machine._location_z == location[2])
            ).one()

    def get_machine_status(self, id) -> MachineStatus:
        return self.get_machine(id).status

    def get_machine_location(self, id) -> List[int]:
        return self.get_machine(id).location

    def get_machine_type(self, id) -> MachineType:
        return self.get_machine(id).type

    def get_users(self) -> List[User]:
        return self.session.query(User).all()

    def get_user(self, user_id) -> User:
        return self.session.query(User).filter(User.user_id == user_id).one()

    def get_user_from_user_name(self, user_name) -> User:
        return self.session.query(User).filter(User._user_name == user_name).one()

    def get_machine_user_relationships(self, machine) -> MachineCurrentUser:
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

    def get_reservations(self) -> List[Reservation]:
        return self.session.query(Reservation).all()

    def get_reservations_by_machine(self, machine: Machine) -> List[Reservation]:
        return self.session.query(Reservation).filter(
                Reservation.machine_id == machine.machine_id).all()

    def get_reservations_by_machine_id(self, machine_id: int) -> List[Reservation]:
        return self.session.query(Reservation).filter(
                Reservation.machine_id == machine_id).all()

    def get_applicable_reservations_by_machine(self, machine: Machine, cut_off_time: datetime) -> List[Reservation]:
        return self.session.query(Reservation).filter(
                and_(Reservation.machine_id == machine.machine_id,
                     # TODO: Not sure about the start time and end time ideas here
                     Reservation.start_time >= datetime.now(),
                     Reservation.end_time <= cut_off_time)
                )

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
        self.session.commit()

        return relationship

    # }}}
