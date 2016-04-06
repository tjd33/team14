# Standard Imports
import configparser

# Senseable Gym Imports
from senseable_gym.sg_util.signal_processing import StreamProcessor
config = configparser.ConfigParser()
config.read('./senseable_gym/sg_run/machine_updater.ini')

try:
    s = StreamProcessor(config['SERIAL']['port'], config['SERIAL']['baudrate'])
    print(s.read_incremental())
except Exception:
    print('Most likely port is not connected')
