import numpy as np
import matplotlib.pyplot as plt

# Specify how many different kinds of data are in a data block
# A data block is a group of data, with each data point being on a new line
# Data blocks are separated by an empty line
rowlength = 6
filename = '/Users/paul/Desktop/ZTerm/Weight_Machine' # Name of file to open
fields = ['Gyro X (deg/sec)', 'Gyro Y (deg/sec)', 'Gyro Z (deg/sec)', 'Accel X (G)', 'Accel Y (G)', 'Accel Z (G)']

def read_text_file_data():
	# Read file into list
	file = open(filename, 'r')
	datastring = file.read()
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
	for each_item in datalist:
		if row == rowlength:
			if each_item != '':
				print('ERROR - LINE ' + str(line) + ': NO NEWLINE WHERE THERE SHOULD BE ONE')
				return
			row = 0
			col += 1
		else:
			if each_item == '':
				print('ERROR - LINE ' + str(line) + ': NEWLINE WHERE THERE SHOULD NOT BE ONE')
				row = 0
			elif is_number(each_item) == 0:
				print('ERROR - LINE ' + str(line) + ': LINE MUST CONTAIN A VALID NUMBER')
				row = 0
			else:
				matrix_data[row][col] = each_item
				row += 1
		line += 1

	# Print matrix for debugging
	# for c in range(0, rowlength):
		# print(matrix_data[c])

	# Return matrix
	return matrix_data

def plot_sensor_data(matrix_data):
	for k in range(0, rowlength):
		plt.plot(range(1,len(matrix_data[0])+1), matrix_data[k])
		plt.xlabel('Time')
		plt.ylabel(fields[k])
		plt.show()
	return

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

matrix_data = read_text_file_data()
plot_sensor_data(matrix_data)

# def read_stream_data(streamname):
# 	pass

# def process_data():
# 	pass

# process_data(read_text_file_to_numpy('example.txt'))
# process_data(read_from_stream('stdin'))