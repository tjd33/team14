# Standard Imports
import configparser

# Senseable Gym Imports
from senseable_gym.sg_util.signal_processing import StreamProcesser

config = configparser.ConfigParser()
config.read('./senseable_gym/sg_run/machine_updater.ini')

s = StreamProcesser(config['SERIAL']['port'], config['SERIAL']['baudrate'])

print(s.read_incremental())
