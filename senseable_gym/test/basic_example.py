#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This will provide a basic test of the the api provided by the senseable gym.
    This script will provide a dictionary that has structure, history
    and relationships.

It will also provide a reference for how to use the API that the senseable
    gym provides.
"""

# Standard Imports
import logging
from datetime import datetime, timedelta

# Third Party Imports
import click

# Senseable Gym Imports
from senseable_gym.sg_database.database import DatabaseModel
from senseable_gym.sg_util.machine import Machine, MachineStatus, MachineType
from senseable_gym.sg_util.user import User
from senseable_gym.sg_util.reservation import Reservation
from senseable_gym.sg_view import bcrypt
from senseable_gym.sg_util.exception import ReservationError


# Code begins here

# Set the options for the basic test
@click.command()
@click.option('--level', default='INFO', help='Logging level for the logger')
@click.option('--dbname', default='none', help='Database name')
def main_settings(level='info', dbname='none'):
    main(level, dbname)


def main(level, dbname):
    # Create your own database model
    #   You specify the name of the database and then the user accessing the database
    #   TODO: Update with more information as the __init__ becomes more complete
    
    db = DatabaseModel(dbname, 'example')
    db._empty_db()
    # Set the database logger to your own custom level
    db.logger.setLevel(getattr(logging, level.upper(), 'INFO'))

    for machine_id in range(10):
        # Just set a few differences in the objects so every one is not identical
        if machine_id % 2 == 0:
            m_type = MachineType.BICYCLE
            m_status = MachineStatus.BUSY
        else:
            m_type = MachineType.TREADMILL
            m_status = MachineStatus.OPEN

        # Create a Machine Object
        temp_machine = Machine(type=m_type, location=[machine_id, machine_id, 1])

        # Set it to have a particular status
        temp_machine.status = m_status

        # Add the machine to the database
        try:
            db.add_machine(temp_machine)
        except:
            pass
            # already contains machine

    # Use the database to retrieve all of the machines
    machine_list = db.get_machines()

    # Print the machines that we have
    print('---------- Machines ----------')
    for machine in machine_list:
        print(machine)

    # Now we add some users to our database model
    for user_id in range(4):
        temp_user = User(str(user_id), 'first' + str(user_id), 'last' + str(user_id), bcrypt.generate_password_hash('password'+ str(user_id)))
        
        if user_id == 2:
            temp_user.administrator = True
        # Add the users to the database
        try:
            db.add_user(temp_user)
        except:
            pass
            # already contains user

    user_list = db.get_users()

    # Print the users that we have
    print('---------- Users ----------')
    for user in user_list:
        print(user)

    # Create some relationships between users and machines
    #   These relationships are all for the current status of machines

    # Lets create a relationship between a user with id = 1 and
    #   a machine with location [1, 1, 1]
    user_1 = db.get_user(1)
    machine_1 = db.get_machine_by_location([1, 1, 1])

    # Indicate the a relationship has been made between these two objects
    try:
        db.get_machine_user_relationships(machine_1)
    except:
        db.set_user_machine_status(machine_1, user_1)

    # Find out what the status of the machine is (we already know it)
    rel_1 = db.get_machine_user_relationships(machine_1)

    print('---------- Relationships -----')
    print(rel_1)
    print(rel_1._machine)
    print(rel_1._user)

    # Set some reservations for in the future
    time_1 = datetime.now() + timedelta(hours=1)
    time_2 = datetime.now() + timedelta(hours=2)
    time_3 = datetime.now() + timedelta(hours=3)
    time_4 = datetime.now() + timedelta(hours=4)
    time_5 = datetime.now() + timedelta(hours=-4)
    time_6 = datetime.now() + timedelta(hours=-2)

    print('---------- Reservations -----')
    machine_2 = db.get_machine(2)
    machine_3 = db.get_machine(3)
    user_2 = db.get_user(2)
    user_3 = db.get_user(3)

    res_1 = Reservation(machine_2, user_2, time_1, time_2)
    res_2 = Reservation(machine_3, user_3, time_1, time_3)
    res_3 = Reservation(machine_2, user_2, time_3, time_4)
    res_4 = Reservation(machine_2, user_3, time_5, time_6)
    
    try:
        db.add_reservation(res_1)
        db.add_reservation(res_2)
        db.add_reservation(res_3)
        db.add_reservation(res_4)
    except ReservationError as e:
        print(e)
        
    res_list = db.get_reservations()
    [print(res) for res in res_list]

    return db

if __name__ == "__main__":
    main_settings()
