import serial    # http://pyserial.readthedocs.org/en/latest/pyserial.htmlp
# from tkinter import *
# import numpy as np
import math

# Specify how many different kinds of data are in a data block
# A data block is a group of data, with each data point being on a new line
# Data blocks are separated by an empty line
rowlength = 6
# filename = '/Users/paul/Desktop/ZTerm/Treadmill_Front' # Name of file to open

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False


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
        acc_total = abs(data[3] + data[4] + data[5] - 1.13)

        if (gyro_total >= 2):
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

    def read(self, num_data=1, debug=True):
        # TODO: Decide on a correct format for a read to return
        # TODO: Break into an incremental read
        # TODO: Set this function into a read certain amount
        # Read file into list
        with open(self.filename, 'r') as f_stream:
            datastring = f_stream.read()
            datalist = datastring.split('\n')

            # Format list so that it begins with gyro x and ends with newline
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
            matrix_data = [[0 for x in range(collength)] for x in range(rowlength + 1)]
            row = 0
            col = 0
            line = begin + 2
            for each_item in datalist:
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


class StreamProcessor(Processor):
    def __init__(self, port, baudrate):
        self.port = port
        self.baudrate = int(baudrate)

        self.ser = serial.Serial()
        self.ser.port = self.port
        self.ser.baudrate = self.baudrate

        # Old options
        # ser.bytesize = 8
        # ser.parity = 'N'
        # ser.stopbits = 1
        # ser.timeout = None
        # ser.xonxoff = False
        # ser.rtscts = False
        # ser.dsrdtr = False

    def read_incremental(self, stream=None, debug=False):
        """
        Read one data packet from the stream

        Returns the standard packet protocol
        """
        if stream:
            # TODO: Decide if this will ever even be used
            #   with an explicit stream
            # TODO: Update this to follow the other section
            # TODO: Abstract this section
            data = []
            counter = 0
            while(1):
                num = str(stream.readline().strip())
                print(num)
                if(num != "b''"):
                    counter += 1
                    num2 = num[2:-1]
                    data.append(float(num2))
                elif(counter == 7):
                    return data
        else:
            self.ser.open()
            data = []
            counter = 0
            while(1):
                num = str(self.ser.readline().strip())
                if debug:
                    print('Reading: {0}'.format(num))
                # If we've collected enough data,
                #   then close the connection and return the data
                if(counter == 7):
                    self.ser.close()
                    return data
                # Only pay attention to non blank lines
                elif(num != "b''"):
                    # We have to start on an integer (that is the ID)
                    if (counter == 0):
                        try:
                            data.append(int(num[2:-1]))
                            counter += 1
                        except ValueError:
                            if debug:
                                print('Tried to make an int with {}'.format(num))
                    # Otherwise, we will put an number into the data
                    else:
                        num2 = num[2:-1]
                        data.append(float(num2))
                        counter += 1

    def read(self, num_data, debug=False):
        # print(stream)
        data = []
        # TODO: fix faulty input values of data, figure out when to start reading data, slow data rate down, get rid of accel data
        for i in range(num_data):
            data.append(self.read_incremental(debug=debug))

        transformed = self.transform(data)
        return transformed

if __name__ == '__main__':
    # matrix_data, _, _, _ = read_text_file_data(filename)
    # plot_sensor_data(matrix_data)
    # read_stream_data()
    # pass
