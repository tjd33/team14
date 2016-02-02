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

# Third Party Imports

# Senseable Gym Imports
from senseable_gym.sg_database.database import DatabaseModel
from senseable_gym.sg_util.machine import Machine, MachineStatus, MachineType

# Code begins here

# Create your own database model
#   You specify the name of the database and then the user accessing the database
#   TODO: Update with more information as the __init__ becomes more complete
db = DatabaseModel('dbname', 'example')

for machine_id in range(10):
    # Just set a few differences in the objects so every one is not identical
    if machine_id % 2 == 0:
        m_type = MachineType.BICYCLE
        m_status = MachineStatus.BUSY
    else:
        m_type = MachineType.TREADMILL
        m_status = MachineStatus.UNKNOWN

    # Create a Machine Object
    temp_machine = Machine(type=m_type, location=[machine_id, machine_id, 1])

    # Set it to have a particular status
    temp_machine.status = m_status

    # Add the machine to the database
    db.add_machine(temp_machine)

# Use the database to retrieve all of the machines
machine_list = db.get_machines()

# Print the machines that we have
for machine in machine_list:
    print(machine)
