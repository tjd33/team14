#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Example test.

Made by: TJ DeVries and Ryan Siekman

This ideally will be the example we use for the presentation in 325
"""

# Local Imports
from senseable_gym.sg_mvc.controller import Controller
from senseable_gym.sg_util.machine import MachineStatus, MachineType, Machine
from senseable_gym.sg_mvc.py_sensor_view import GTKView


def main():
    """
    The main loop for the test
    :returns: None
    """
    # Begin our function by declaring a controller and a view
    controller = Controller()

    # Create our view
    # view = View(controller.get_model())
    view = GTKView(controller.get_model())

    welcome(controller, view)
    return None


def welcome(controller, view):
    """
    The welcome and setup function for the test

    :controller: The controller created in the main loop
    :view: The view created in the main loop

    :returns: TODO

    """
    # Add our first machine
    machine1 = Machine(MachineType.BICYCLE, [1, 1, 1], True)
    machine1.status = MachineStatus.OPEN
    controller.add_machine(machine1)

    # Add our second machine
    machine2 = Machine(MachineType.TREADMILL, [2, 3, 5], True)
    controller.add_machine(machine2)
    machine2.status = MachineStatus.BUSY

    # Add our third machine
    machine3 = Machine(MachineType.BICYCLE, [3, 13, 10], True)
    controller.add_machine(machine3)

    # Add our fourth machine
    machine4 = Machine(MachineType.BICYCLE, [1, 2, 3], True)
    controller.add_machine(machine4)

    # Add our fifth machine
    machine5 = Machine(MachineType.BICYCLE, [6, 6, 1], True)
    controller.add_machine(machine5)

    print("This is a text based view of the locations of the machines")
    print(view.display_locations())

    print("Now for a GUI view of the locations of the machines")
    view.start_gui()

    print("Now let's add a custom machine")
    id_num = int(input("Please input an ID number: "))
    location = []
    location.append(int(input("Please input the x location of the machine: ")))
    location.append(int(input("Please input the y location of the machine: ")))
    location.append(1)
    custom_machine = Machine(id_num, MachineType.TREADMILL, location, True)
    controller.add_machine(custom_machine)

    view2 = GTKView(controller.get_model())
    print("How we will display the new GUI")
    view2.start_gui()

if __name__ == "__main__":
    main()
