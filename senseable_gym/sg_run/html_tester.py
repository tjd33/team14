# Standard Imports
import configparser

# Senseable Gym Imports
from senseable_gym.sg_util.signal_processing import HtmlProcessor
from senseable_gym.sg_run.machine_updater import send_update
config = configparser.ConfigParser(delimiters=('='))
config.read('./senseable_gym/sg_run/default.ini')
config.read('./senseable_gym/sg_run/html_updater.ini')

s = HtmlProcessor(config['6LOWPAN']['host_ip'])

# print(config['MACHINE_MAP']['http://[aaaa::212:4b00:a54:fd84]/'])


while True:
    result = s.read(3, debug=True)

    processed = s.process_data(result)
    print('Processed: {0}'.format(processed))
    
    for machine_id in processed:
        if processed[machine_id] == True:
            send_update(machine_id, 2)
        else:
            send_update(machine_id, 1)
"""
while (False):
    result = s.read(100, debug=True)

    processed = s.process_data(result)
    print('Processed: {0}'.format(processed))
    
    for machine_id in processed:
        if processed[machine_id] == True:
            send_update(machine_id, 2)
        else:
            send_update(machine_id, 1)
"""
