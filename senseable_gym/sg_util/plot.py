#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import matplotlib.pyplot as plt


def plot_sensor_data(matrix_data):
    gyro_data = matrix_data[0] + matrix_data[1] + matrix_data[2]
    accel_data = matrix_data[3] + matrix_data[4] + matrix_data[5]
    plt.plot(range(1, len(gyro_data)+1), gyro_data)
    plt.show()
    plt.plot(range(1, len(accel_data)+1), accel_data)
    plt.show()
    # for k in range(0, rowlength):
    #   plt.plot(range(1,len(matrix_data[0])+1), matrix_data[k])
    #   plt.xlabel('Time')
    #   plt.ylabel(fields[k])
    #   plt.show()
    return
