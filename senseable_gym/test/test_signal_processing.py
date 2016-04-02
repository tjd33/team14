import unittest

# Package Imports
from senseable_gym.sg_util.signal_processing import read_text_file_data

class TestSignalProcessing(unittest.TestCase):
    def setUp(self):
        # Do this every time I run a new test function
        pass

    def test_read_text_file_data(self):
        filename = './senseable_gym/test/data_txt_files/Weight_Machine'
        _, no_newline, unwanted_newline, invalid_number = read_text_file_data(filename)
        print('Filename: ' + filename)
        print('NO NEWLINE WHERE THERE SHOULD BE ONE:')
        for line in no_newline:
            print('- Line ' + str(line))
        print('NEWLINE WHERE THERE SHOULD NOT BE ONE:')
        for line in unwanted_newline:
            print('- Line ' + str(line))
        print('LINE MUST CONTAIN A VALID NUMBER:')
        for line in invalid_number:
            print('- Line ' + str(line))

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
