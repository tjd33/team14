import unittest

# Package Imports
from senseable_gym.sg_util.signal_processing import TextProcessor, HtmlProcessor

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


class TestHtmlSignalProcessing(unittest.TestCase):
    def setUp(self):
        pass

    def test_read_incremental(self):
        html_proc = HtmlProcessor('[bbbb::100]')
        with open('./senseable_gym/test/data_html_files/Index.html', 'r') as f:
            read_data = f.read()

        res = html_proc.read_incremental(read_data)

        self.assertEqual(res, ['http://[aaaa::212:4b00:a54:fd84]/', -0.71, -4.97, -5.65, 0.03, 0.08, 1.1])

        with open('./senseable_gym/test/data_html_files/Index2.html', 'r') as f:
            read_data = f.read()

        res = html_proc.read_incremental(read_data)
        self.assertEqual(res, ['http://[aaaa::212:4b00:7c9:4484]/', 4.79, 4.31, 1.59, 0.00, 0.01, 0.94])

    def test_update_sensor_list(self):
        html_proc = HtmlProcessor('[bbbb::100]')
        with open('./senseable_gym/test/data_html_files/Sensors - 6LBR.html', 'r') as f:
            read_data = f.read()

        new_sensor_list = html_proc.update_sensor_list(read_data)
        self.assertEqual(new_sensor_list, ['http://[aaaa::212:4b00:a54:fd84]/', 'http://[aaaa::212:4b00:7c9:4484]/'])


if __name__ == '__main__':
    unittest.main()
