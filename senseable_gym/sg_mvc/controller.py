"""
Controller for our Python Sensor Display
Made for Engineering 325,
    but also for our senior design project.

    TJ DeVries
    Ryan Siekman
"""

from senseable_gym.sg_database.database import DatabaseModel


class Controller():
    def __init__(self):
        # Create our model
        self.model = DatabaseModel(None, 'user')

    def add_machine(self, machine):
        # Add the machine to our model
        self.model.add_machine(machine)

    def remove_machine(self, id):
        self.model.remove_machine(id)

    # Getters
    def get_machines(self):
        return self.model.get_machines()

    def get_machine_object(self, id):
        return self.model.get_machine_object(id)

    def get_machine_status(self, id):
        return self.model.get_machine_status(id)

    # Setters
    def set_machine_status(self, id, status):
        self.model.set_machine_status(id, status)

    def set_machine_location(self, id, location):
        self.model.set_machine_location(id, location)

    def get_model(self):
        return self.model
