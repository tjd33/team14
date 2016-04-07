#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import matplotlib.pyplot as plt


def plot_sensor_data(matrix_data):
    gyro_data = [0 for x in range(len(matrix_data[0]))]
    accel_data = [0 for x in range(len(matrix_data[0]))]
    for col in range(0, len(matrix_data[0])):
        gyro_data[col] = matrix_data[1][col] + matrix_data[2][col] + matrix_data[3][col]
        accel_data[col] = abs(matrix_data[4][col] + matrix_data[5][col] + matrix_data[6][col] - 1.13)
    plt.plot(range(1, len(gyro_data)+1), gyro_data)
    plt.xlabel('Time')
    plt.ylabel('Gyroscope (deg/sec)')
    plt.show()
    plt.plot(range(1, len(accel_data)+1), accel_data)
    plt.xlabel('Time')
    plt.ylabel('Accelerometer (G)')
    plt.show()
    # fields = ['Gyro X (deg/sec)', 'Gyro Y (deg/sec)', 'Gyro Z (deg/sec)', 'Accel X (G)', 'Accel Y (G)', 'Accel Z (G)']
    # for k in range(0, rowlength):
    #   plt.plot(range(1,len(matrix_data[0])+1), matrix_data[k])
    #   plt.xlabel('Time')
    #   plt.ylabel(fields[k])
    #   plt.show()
    return
