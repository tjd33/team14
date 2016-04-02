import numpy as np
import matplotlib.pyplot as plt
import serial    # http://pyserial.readthedocs.org/en/latest/pyserial.htmlp
from tkinter import *

# Specify how many different kinds of data are in a data block
# A data block is a group of data, with each data point being on a new line
# Data blocks are separated by an empty line
rowlength = 6
filename = '/Users/paul/Desktop/ZTerm/Treadmill_Front' # Name of file to open
fields = ['Gyro X (deg/sec)', 'Gyro Y (deg/sec)', 'Gyro Z (deg/sec)', 'Accel X (G)', 'Accel Y (G)', 'Accel Z (G)']

def read_text_file_data(filename):
    # Read file into list
    with open(filename, 'r') as f:
        datastring = f.read()
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
        matrix_data = [[0 for x in range(collength)] for x in range(rowlength)]
        row = 0
        col = 0
        index = 0
        line = begin + 2
        no_newline = []
        unwanted_newline = []
        invalid_number = []
        for each_item in datalist:
            if row == rowlength:
                if each_item != '':
                    # print('ERROR - LINE ' + str(line) + ': NO NEWLINE WHERE THERE SHOULD BE ONE')
                    no_newline.append(line)
                    return
                row = 0
                col += 1
            else:
                if each_item == '':
                    # print('ERROR - LINE ' + str(line) + ': NEWLINE WHERE THERE SHOULD NOT BE ONE')
                    unwanted_newline.append(line)
                    row = 0
                elif is_number(each_item) == 0:
                    # print('ERROR - LINE ' + str(line) + ': LINE MUST CONTAIN A VALID NUMBER')
                    invalid_number.append(line)
                    row = 0
                else:
                    matrix_data[row][col] = abs(float(each_item))
                    row += 1
            line += 1

        # Print matrix for debugging
        # for c in range(0, rowlength):
            # print(matrix_data[c])

        # Return matrix
        return matrix_data, no_newline, unwanted_newline, invalid_number

def plot_sensor_data(matrix_data):
    gyro_data = matrix_data[0] + matrix_data[1] + matrix_data[2]
    accel_data = matrix_data[3] + matrix_data[4] + matrix_data[5]
    plt.plot(range(1,len(gyro_data)+1), gyro_data)
    plt.show()
    plt.plot(range(1,len(accel_data)+1), accel_data)
    plt.show()
    # for k in range(0, rowlength):
    #   plt.plot(range(1,len(matrix_data[0])+1), matrix_data[k])
    #   plt.xlabel('Time')
    #   plt.ylabel(fields[k])
    #   plt.show()
    return

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

def read_stream_data():
    ser = serial.Serial()
    ser.port = '/dev/serial/by-id/usb-Texas_Instruments_XDS110__02.02.05.01__with_CMSIS-DAP_L3000408-if00'
    ser.baudrate = 115200
    # ser.bytesize = 8
    # ser.parity = 'N'
    # ser.stopbits = 1
    # ser.timeout = None
    # ser.xonxoff = False
    # ser.rtscts = False
    # ser.dsrdtr = False
    ser.open()
    # print(ser)
    data = []
    # TODO: fix faulty input values of data, figure out when to start reading data, slow data rate down, get rid of accel data
    while(1):
        num = str(ser.readline().strip())
        if(num != "b''"):
            num2 = num[2:-1]
            data.append(float(num2))
        else:
            gyro = data[0] + data[1] + data[2]
            # print(gyro)
            if(gyro >= 2):
                print('In Use')
            else:
                print('Not in Use')
            data = []

# def process_data():
#   pass

if __name__ == '__main__':
    # matrix_data, _, _, _ = read_text_file_data(filename)
    # plot_sensor_data(matrix_data)
    read_stream_data()
