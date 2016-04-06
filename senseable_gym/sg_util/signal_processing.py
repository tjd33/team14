import serial    # http://pyserial.readthedocs.org/en/latest/pyserial.htmlp
# from tkinter import *
# import numpy as np

# Specify how many different kinds of data are in a data block
# A data block is a group of data, with each data point being on a new line
# Data blocks are separated by an empty line
rowlength = 6
# filename = '/Users/paul/Desktop/ZTerm/Treadmill_Front' # Name of file to open
fields = ['Gyro X (deg/sec)', 'Gyro Y (deg/sec)', 'Gyro Z (deg/sec)', 'Accel X (G)', 'Accel Y (G)', 'Accel Z (G)']


def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False


class Processer():
    def __init__(self):
        self.data_packets_read = 0

    def read(self):
        pass

    def process_single_data(self, data) -> bool:
        """
        Takes a list of data, of the form:
        [ID, gyro_x, gyro_y, gyro_z, acc_x, acc_y, acc_z]
        and determines if the machine is busy.

        :returns: True if busy, else False
        """
        gyro_total = abs(data[1]) + abs(data[2]) + abs(data[3])

        if (gyro_total >= 2):
            return True
        else:
            return False

    def process_data(self, data_dict: dict, num_data: int) -> bool:
        """
        Takes a dictionary of data, of the form:
        {
            time_stamp_1: single_data_1,
            time_stamp_2: single_data_2,
            ...
        }
        and determines if the machine is busy.

        :returns: True if busy, else False
        """
        time_stamps = sorted(data_dict.keys())

        is_busy = False
        for i in range(num_data):
            if self.process_data(time_stamps[i]):
                is_busy = True

        self.data_packets_read += num_data

        return is_busy


class TextProcessor(Processer):
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
            collength = len(datalist)//(rowlength + 1)
            matrix_data = [[0 for x in range(collength)] for x in range(rowlength + 1)]

            row = 0
            col = 0
            line = begin + 2
            for each_item in datalist:
                print('Row: {0}, item: {1}'.format(row, each_item))
                if row == rowlength:
                    if each_item != '':
                        # print('ERROR - LINE ' + str(line) + ': NO NEWLINE WHERE THERE SHOULD BE ONE')
                        self.no_newline.append(line)
                    row = 0
                    col += 1
                else:
                    if each_item == '':
                        # print('ERROR - LINE ' + str(line) + ': NEWLINE WHERE THERE SHOULD NOT BE ONE')
                        self.unwanted_newline.append(line)
                        row = 0
                    elif is_number(each_item) == 0:
                        # print('ERROR - LINE ' + str(line) + ': LINE MUST CONTAIN A VALID NUMBER')
                        self.invalid_number.append(line)
                        row = 0
                    else:
                        matrix_data[row][col] = abs(float(each_item))
                        row += 1
                line += 1

            # Print matrix for debugging
            # for c in range(0, rowlength):
                # print(matrix_data[c])

            # Return matrix
            return matrix_data


class StreamProcessor(Processer):
    def __init__(self, port, baudrate):
        self.port = port
        self.baudrate = baudrate

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

    def read_incremental(self, stream=None):
        """
        Read one data packet from the stream

        Returns the standard packet protocol
        """
        if stream:
            data = []
            counter = 0
            while(1):
                num = str(stream.readline().strip())
                if(num != "b''"):
                    counter += 1
                    num2 = num[2:-1]
                    data.append(float(num2))
                elif(counter == 7):
                    return data
        else:
            with self.ser.open() as stream:
                data = []
                counter = 0
                while(1):
                    num = str(stream.readline().strip())
                    if(num != "b''"):
                        counter += 1
                        num2 = num[2:-1]
                        data.append(float(num2))
                    elif(counter == 7):
                        return data

    def read(self, num_data):
        with self.ser.open() as stream:
            # print(stream)
            data = []
            # TODO: fix faulty input values of data, figure out when to start reading data, slow data rate down, get rid of accel data
            for i in range(num_data):
                data.append(self.read_incremental(stream))

        return data

# def process_data():
#   pass

if __name__ == '__main__':
    # matrix_data, _, _, _ = read_text_file_data(filename)
    # plot_sensor_data(matrix_data)
    # read_stream_data()
    pass
