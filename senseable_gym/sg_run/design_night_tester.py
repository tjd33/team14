# Standard Imports
import configparser

# Senseable Gym Imports
from senseable_gym.sg_util.signal_processing import StreamProcessor
from senseable_gym.sg_run.machine_updater import send_update
config = configparser.ConfigParser()
config.read(['./senseable_gym/sg_run/default.ini', './senseable_gym/sg_run/design_night_updater.ini')

ip = config['SERVER']['ip']
port = config['SERVER']['port']
password = config['SERVER']['pass']

s = StreamProcessor(config['SERIAL']['port'], config['SERIAL']['baudrate'])

while (True):
    result = s.read(100, debug=True)

    processed = s.process_data(result)
    print('Processed: {0}'.format(processed))
    
    for machine_id in processed:
        if processed[machine_id] == True:
            send_update(ip, port, password, machine_id, 2)
        else:
            send_update(ip, port, password, machine_id, 1)
