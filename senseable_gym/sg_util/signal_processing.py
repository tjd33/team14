import serial    # http://pyserial.readthedocs.org/en/latest/pyserial.html
import math
import urllib
import logging
from html.parser import HTMLParser
# from threading import BoundedSemaphore
# from senseable_gym.sg_util.plot import plot_sensor_data

# Senseable Gym Imports
from senseable_gym import global_logger_name

# Specify how many different kinds of data are in a data block
# A data block is a group of data, with each data point being on a new line
# Data blocks are separated by an empty line
rowlength = 7

logger = logging.getLogger(global_logger_name + '.database')


def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False


def is_int(s):
    try:
        int(s)
        return True
    except ValueError:
        return False


class MyHTMLParser(HTMLParser):
    def __init__(self):
        self.inside_tbody = False
        self.correct_data = False
        self.current_attr = None
        self.ip_addrs = []
        super().__init__()

    def handle_starttag(self, tag, attrs):
        self.current_attr = attrs

        if tag == 'tbody':
            self.inside_tbody = True

        # if self.inside_tbody and tag == 'a':
        #     print("Start tag:", tag)

    def handle_endtag(self, tag):
        if tag == 'tbody':
            self.inside_tbody = False

        # if self.inside_tbody and tag == 'a':
        #     print("End tag  :", tag)

    def handle_data(self, data):
        if self.inside_tbody and data == 'web':
            # print("Data     :", data)
            # print('Appending:', self.current_attr[0][1])
            self.ip_addrs.append(self.current_attr[0][1])


class Processor():
    def __init__(self):
        self.data_packets_read = 0

    def read(self):
        pass

    def process_single_data(self, data) -> bool:
        """
        Takes a list of data, of the form:
        [gyro_x, gyro_y, gyro_z, acc_x, acc_y, acc_z]
        and determines if the machine is busy.

        :returns: True if busy, else False
        """
        gyro_total = abs(data[0]) + abs(data[1]) + abs(data[2])
        # acc_total = abs(data[3] + data[4] + data[5] - 1.13)

        if(gyro_total >= 100):  # or (acc_total >= 0.11)):
            return True
        else:
            return False

    def process_data(self, data_dict: dict) -> dict:
        """
        Takes a dictionary of data, of the form:
        {
            machine_id_1: [
                single_data_1,
                single_data_2,
                single_data_3,
            ]
            machine_id_2: [
                single_data_1,
                single_data_2,
                single_data_3,
            ]
            ...
        }
        and determines if the machine is busy.

        :returns: {machine_id_1: True, machine_id_2: False}
        """
        processed = {}
        for machine_id in data_dict.keys():
            num_busy = 0
            for l in data_dict[machine_id]:
                num_busy += self.process_single_data(l)

            if num_busy / len(data_dict[machine_id]) > 0.5:
                processed[machine_id] = True
            else:
                processed[machine_id] = False

        return processed

    def transform(self, data: list) -> dict:
        """
        Takes a list of lists, of the form:
        [
            [ID, gyro_x, ... ]
            [ID, gyro_x, ... ]
            [ID, gyro_x, ... ]
        ]

        and turns it into the form:
        {
            machine_id_1: [
                single_data_1,
                single_data_2,
                single_data_3,
            ]
            machine_id_2: [
                single_data_1,
                single_data_2,
                single_data_3,
            ]
            ...
        }
        """
        transformed = {}
        for l in data:
            if l[0] not in transformed.keys():
                transformed[l[0]] = []

            transformed[l[0]].append(l[1:])

        return transformed


class HtmlProcessor(Processor):
    def __init__(self, host_ip):
        self.host_ip = host_ip
        self.sensor_list = None

    def get_page(self, url):
        filehandle = urllib.urlopen(url)
        return filehandle.read()

    # TODO(tjdevries): Pass in the ID, so that it can place it at the front of the list?
    #   This way it would do the same type of transofmration in read. Currently I'm not really
    #   returning the correct thing as specified by our API.
    def read_incremental(self, html):
        lines = html.split('\n')

        important_lines = False
        result_gyro = []
        result_acc = []
        id_num = None
        for line in lines:
            if 'aaaa::' in line and not id_num:
                id_num =  line[line.index('aaaa::') - 8:line.index('index.html')]
            elif 'Acc X' in line:
                important_lines = True

            if important_lines:
                if 'Gyro Z' in line:
                    split_line = line.split('<')[0]
                    result_gyro.append(float(split_line.split('=')[1][0:-12]))
                elif 'Gyro' in line:
                    result_gyro.append(float(line.split('=')[1][0:-12]))
                elif 'Acc' in line:
                    result_acc.append(float(line.split('=')[1][0:-2]))

        return [id_num] + result_gyro + result_acc

    def read(self, iterations, debug=False):
        processed = []

        # TODO(tjdevries): Make sure this is the correct sensor html
        logger.info('GET: {0}'.format(self.host_ip + '/sensors.html'))
        self.sensor_list = self.update_sensor_list(self.host_ip + '/sensors.html')

        # TODO(tjdevries): Make this threaded
        for data_point in range(len(iterations)):
            for sensor in self.sensor_list:
                logger.debug('Data point: {0}, Sensor: {1} -- Start'.format(data_point, sensor))

                # TODO(tjdevries): Is this the correct address?
                html = self.get_page(sensor)

                processed.append(self.read_incremental(html))
                logger.debug('Data point: {0}, Sensor: {1} -- Finish'.format(data_point, sensor))

        transformed = self.transform(processed)
        return transformed

    def update_sensor_list(self, sensor_info):
        # TODO(tjdevries): Check if we have done this recently
        parser = MyHTMLParser()
        parser.feed(sensor_info)

        return parser.ip_addrs


class TextProcessor(Processor):
    def __init__(self, filename):
        self.filename = filename
        self.no_newline = []
        self.unwanted_newline = []
        self.invalid_number = []

    def read_incremental(self, f_stream=None):
        if f_stream:
            # Read from it here
            pass
        else:
            # Open and read from it
            #   Play nice and close it.
            pass

    def read(self, num_data=1, debug=False):
        # TODO: Decide on a correct format for a read to return
        # TODO: Break into an incremental read
        # TODO: Set this function into a read certain amount
        # Read file into list
        with open(self.filename, 'r') as f_stream:
            datastring = f_stream.read()
            datalist = datastring.split('\n')

            # TODO: fix end of list so that it ends nicer and update collength variable accordingly
            # Format list so that it begins with machine ID and ends with newline
            begin = rowlength
            for n in range(0, begin - 1):
                if datalist[n] == '':
                    begin = n
                    break
            if begin != rowlength:
                del datalist[0:(begin + 1)]
            end = -1
            for k in range(end - 1, end - rowlength, -1):
                if datalist[k] == '':
                    end = k
                    break
            if end != -1:
                del datalist[(end + 1):]

            # Initialize and store data into matrix format
            collength = math.ceil(len(datalist)/(rowlength + 1))
            matrix_data = [[0 for x in range(collength)] for x in range(rowlength)]
            row = 0
            col = 0
            line = begin + 2
            for each_item in datalist:
                if debug:
                    print('Row: {0}, item: {1}'.format(row, each_item))
                if row == rowlength:
                    if each_item != '':
                        self.no_newline.append(line)
                    row = 0
                    col += 1
                else:
                    if each_item == '':
                        self.unwanted_newline.append(line)
                        row = 0
                    elif is_number(each_item) == 0:
                        self.invalid_number.append(line)
                        row = 0
                    else:
                        matrix_data[row][col] = abs(float(each_item))
                        row += 1
                line += 1

            # Return matrix
            return matrix_data

    # def create_test_files(self):
    #     tempfile = open(self.filename, 'r')
    #     tempdatastring = tempfile.read()
    #     tempdatalist = tempdatastring.split('\n')
    #     numb = 8*17000
    #     numb2 = 8*22000
    #     newdatalist = tempdatalist[numb:numb2]
    #     f = open('../test/data_txt_files/Off', 'w')
    #     for itemm in newdatalist:
    #         if itemm == '':
    #             f.write('\r\n')
    #         else:
    #             f.write(itemm)
    #             f.write('\r\n')


class StreamProcessor(Processor):
    def __init__(self, port, baudrate):
        self.port = port
        self.baudrate = int(baudrate)

        self.ser = serial.Serial()
        self.ser.port = self.port
        self.ser.baudrate = self.baudrate

        # Old options
        # self.ser.bytesize = 8
        # self.ser.parity = 'N'
        # self.ser.stopbits = 1
        # self.ser.timeout = None
        # self.ser.xonxoff = False
        # self.ser.rtscts = False
        # self.ser.dsrdtr = False

    def read_incremental(self, stream=None, debug=False):
        """
        Read one data packet from the stream

        Returns the standard packet protocol
        """
        # TODO: Abstract this section
        data = []
        counter = 0

        if not stream:
            self.ser.open()

        while(1):
            num = str(self.ser.readline().strip())
            if debug:
                print('Reading: {0}'.format(num))
            # For non blank lines, put a number into the data
            if((num != "b''") and (counter < rowlength)):
                num2 = num[2:-1]
                if((counter != 0) and (is_number(num2))):
                    data.append(float(num2))
                    counter += 1
                elif((counter == 0) and (is_int(num2))):
                    data.append(int(num2))
                    counter += 1
            # If we've collected enough data, return the data
            elif(counter == rowlength):
                if not stream:
                    self.ser.close()
                return data
            # If we read a packet that was too small or too large, try again
            else:
                data = []
                counter = 0

        if not stream:
            self.ser.close()

    def read(self, num_data, debug=False):
        data = []
        self.ser.open()
        for i in range(num_data):
            data.append(self.read_incremental(stream=self.ser, debug=debug))
        self.ser.close()
        transformed = self.transform(data)
        return transformed

if __name__ == '__main__':
    # tp = TextProcessor('../test/data_txt_files/Treadmill_Side')
    # mdata = tp.read()
    # plot_sensor_data(mdata)
    # sp = StreamProcessor('/dev/serial/by-id/usb-Texas_Instruments_XDS110__02.02.05.01__with_CMSIS-DAP_L3000408-if00', 115200)
    # print(sp.read(10))
    pass
