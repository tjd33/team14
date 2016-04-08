# Standard Imports
import configparser

# Senseable Gym Imports
from senseable_gym.sg_util.signal_processing import StreamProcessor
config = configparser.ConfigParser()
config.read('./senseable_gym/sg_run/machine_updater.ini')

'''
try:
    s = StreamProcessor(config['SERIAL']['port'], config['SERIAL']['baudrate'])
    print(s.read_incremental())
except Exception:
    print('Most likely port is not connected')
'''

s = StreamProcessor(config['SERIAL']['port'], config['SERIAL']['baudrate'])
result = s.read_incremental(debug=True)

print('Result: {0}'.format(result))

# processed = s.process_single_data(result)
# print('Processed: {0}'.format(processed))

print('Testing read(10)')

result = s.read(10, debug=True)
print('Result: {0}'.format(result))

processed = s.process_data(result)
print('Processed: {0}'.format(processed))
