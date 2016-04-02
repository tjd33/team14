# Standard imports
import unittest

# Local imports
from senseable_gym.sg_mvc.controller import Controller
from senseable_gym.sg_util.machine import Machine, MachineType
from senseable_gym.sg_mvc.py_sensor_view import View


class TestBasicFunctions(unittest.TestCase):
    def setUp(self):
        # Create our controller
        self.controller = Controller()

        # Create our view
        self.view = View(self.controller.get_model())

        # Create an example machine
        self.machine1 = Machine(MachineType.TREADMILL, [1, 1, 1])

    def test_get_machines(self):
        # Test on an empty set
        self.assertEqual(self.controller.get_machines(), list())

        # Manually add a machine to our machine dictionary
        self.controller.model.add_machine(self.machine1)

        self.assertEqual(self.controller.get_machines()[0], self.machine1)

        # Manually add another machine
        machine2 = Machine(MachineType.TREADMILL, [2, 2, 2])
        self.controller.model.add_machine(machine2)

        self.assertEqual(self.controller.get_machines(), [self.machine1, machine2])

    def test_add_machine(self):
        # Add our example machine
        self.controller.add_machine(self.machine1)

        self.assertEqual(self.controller.get_machines()[0], self.machine1)

    def test_add_machine_duplicate_machine(self):
        # Add our first machine
        self.controller.add_machine(self.machine1)

        # Try to add the same machine, should fail
        self.assertRaises(Exception, self.controller.add_machine, self.machine1)


class TestViewFunctions(unittest.TestCase):
    def setUp(self):
        # Create our controller
        self.controller = Controller()

        # Create our view
        self.view = View(self.controller.get_model())

        # Create an example machine
        self.machine1 = Machine(MachineType.TREADMILL, [1, 1, 1])

    def test_get_machine_type(self):
        # Add our example machine
        self.controller.add_machine(self.machine1)

        # self.view.print_machine_type(1)
        self.assertEqual(self.view.get_machine_type(self.machine1.machine_id), self.machine1.type)

    def test_display_status(self):
        # Add our example machine
        self.controller.add_machine(self.machine1)

        final_string = self.view.format_line(["ID", "Machine Type"]) + \
            self.view.format_line([self.machine1.machine_id, self.machine1.type])

        self.assertEqual(self.view.display_status(), final_string)


if __name__ == '__main__':
    unittest.main()
