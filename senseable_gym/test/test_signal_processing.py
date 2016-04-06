import unittest

# Package Imports
from senseable_gym.sg_util.signal_processing import TextProcessor

DEBUG = False


class TestSignalProcessing(unittest.TestCase):
    def setUp(self):
        # Do this every time I run a new test function
        pass

    def test_read_text_file_data(self):
        text_proc = TextProcessor('./senseable_gym/test/data_txt_files/weight_machine_sample.txt')

        print()
        output = text_proc.read(100)
        for item in output:
            print('Output: {0}'.format(item))
        print(text_proc.no_newline)
        print(text_proc.unwanted_newline)
        print(text_proc.invalid_number)

    def test_plot_sensor_data(self):
        pass

    def test_is_number(self):
        pass

    def test_is_processing_active_machine(self):
        pass
        # filename = './test/active_machine'

        # process here
        # result = True

        # self.assertEqual(result, True)

    def tearDown(self):
        # Do this after I run every test
        pass

if __name__ == '__main__':
    unittest.main()
