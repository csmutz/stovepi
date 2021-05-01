#!/usr/bin/python3
'''
module to handle dallas temp sensor using 1 wire protocol

if used as script, prints all the known sensors
'''

import sys
import os
import re
import logging

DEVICE_PREFIX="/sys/bus/w1/devices/"
DEVICE_POSTFIX="/w1_slave"

sensors = { "vent":     "28-021391773b3a",
            "ceiling":  "28-02119177c3db",
            "upstairs": "28-020b917741b5",
            "stovepi":  "28-3c01d607c018",
            "downstairs":  "28-3c01d607cb52",
            "hvac": "28-3c01d6072b07"}

'''
cat /sys/bus/w1/devices/28-3c01d607c018/w1_slave
5a 01 55 05 7f a5 a5 66 c3 : crc=c3 YES
5a 01 55 05 7f a5 a5 66 c3 t=21625
'''


class dallas_temp:
    
    def __init__(self):
        pass 

    def get_temp(self, sensor):
        #return temp in F (int)
        if sensor in sensors:
            dev_path = DEVICE_PREFIX + sensors[sensor] + DEVICE_POSTFIX
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
                                logging.error("Error Reading Temperature: error parsing temperature for sensor %s" % (sensor))
                        else:
                            #log error, invalid data from sensora
                            logging.error("Error Reading Temperature: invalid data from sensor %s" % (sensor))
                    else:
                        #log error reading file, invalid number of files
                        logging.error("Error Reading Temperature: unexpected number lines in file for sensor %s" % (sensor))
            except Exception as e:
                logging.error(traceback.format_exc())
        else:
            logging.error("Invalid Sensor: sensor %s not configured" % (sensor))

def main():
    dt = dallas_temp()
    for s in sensors:
        print("%s: %i" % (s,dt.get_temp(s)))
    
    
if __name__ == "__main__":
    # execute only if run as a script
    main()
