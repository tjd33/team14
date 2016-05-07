# Standard Imports
import configparser
import threading

# Senseable Gym Imports
from senseable_gym.sg_util.signal_processing import DistributedStreamProcessor
from senseable_gym.sg_run.machine_updater import send_update, send_battery
config = configparser.ConfigParser(delimiters=('='))
config.read(['./senseable_gym/sg_run/default.ini', './senseable_gym/sg_run/design_night_updater.ini'])

ip = config['SERVER']['ip']
port = config['SERVER']['port']
password = config['SERVER']['pass']
machine_map = config['MACHINE_MAP']

s = DistributedStreamProcessor(config['SERIAL']['port'], config['SERIAL']['baudrate'], machine_map)

s.ser.open()
while (True):
    try:
        result = s.read_incremental(stream=s.ser, debug=True)

        processed = s.process_data(result)
        print('Processed: {0}'.format(processed))
        
        for machine_id in processed:
            if processed[machine_id]['busy'] == True:
                threading.Thread(group=None, target=send_update, args=(ip, port, password, machine_id, 2)).start()
            else:
                threading.Thread(group=None, target=send_update, args=(ip, port, password, machine_id, 1)).start()

            threading.Thread(group=None, target=send_battery, args=(ip, port, password, machine_id, processed[machine_id]['battery'])).start()
    except KeyboardInterrupt:
        s.ser.close()
        break
