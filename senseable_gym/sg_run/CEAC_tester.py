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



while (True):
    result = s.read(1000, debug=True)

    processed = s.process_data(result)
    print('Processed: {0}'.format(processed))
