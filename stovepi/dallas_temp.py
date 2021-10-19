#!/usr/bin/python3
'''
module to handle dallas temp (DS18B20) sensors using 1 wire protocol

if used as script, prints all the dallas sensors

#TODO: implement retries on temp reads

'''

import sys
import os
import re
import logging
import glob
import traceback

DEVICE_PREFIX="/sys/bus/w1/devices/"
DEVICE_POSTFIX="/w1_slave"

sensors = { "vent":     "28-021391773b3a",
            "ceiling":  "28-02119177c3db",
            "upstairs": "28-020b917741b5",
            "stovepi":  "28-3c01d607c018",
            "downstairs":  "28-3c01d607cb52",
            "hvac": "28-3c01d6072b07",
            }

'''
cat /sys/bus/w1/devices/28-3c01d607c018/w1_slave
5a 01 55 05 7f a5 a5 66 c3 : crc=c3 YES
5a 01 55 05 7f a5 a5 66 c3 t=21625
'''

DEVICE_TYPE_DS18B20 = "28-"

def list_devices(device_type=DEVICE_TYPE_DS18B20):
    devs = []
    for path in glob.glob(DEVICE_PREFIX + device_type + "*"):
        devs.append(os.path.basename(path))
    return devs


class dallas_temp:
    
    def __init__(self):
        pass 

    def get_temp(self, sensor):
        if sensor in sensors:
            return self.get_temp_by_id(sensors[sensor],sensor)

    def get_temp_by_id(self, sensor_id, sensor_name=""):
        dev_path = DEVICE_PREFIX + sensor_id + DEVICE_POSTFIX
        try:    
            with open(dev_path) as f:
                lines = f.readlines()
                if len(lines) == 2:
                    match =  re.search(r'''YES\s?$''', lines[0])
                    if match:
                        match = re.search(r'''t=([0-9]+)\s?$''', lines[1])
                        if match:
                            return int(int(match.group(1)) * 9 / 5 / 1000 + 32)
                        else:
                            #error reading temp
                            logging.error("Error Reading Dallas Temperature: error parsing temperature for sensor %s:%s" % (sensor_name, sensor_id))
                    else:
                        #log error, invalid data from sensora
                        logging.error("Error Reading Dallas Temperature: invalid data from sensor %s:%s" % (sensor_name, sensor_id))
                else:
                    #log error reading file, invalid number of files
                    logging.error("Error Reading Dallas Temperature: unexpected number lines in file for sensor %s:%s" % (sensor_name, sensor_id))
        except Exception as e:
            logging.error(traceback.format_exc())

def main():
    dt = dallas_temp()
    known_sensors = []
    print("Known Sensors:")
    for s in sensors:
        known_sensors.append(sensors[s])
        print("%s: %i" % (s,dt.get_temp(s)))
    
    print()
    print("Other Sensors:")
    for s in list_devices():
        if s not in known_sensors:
            print("%s: %i" % (s,dt.get_temp_by_id(s)))
        
    
    
if __name__ == "__main__":
    # execute only if run as a script
    main()
