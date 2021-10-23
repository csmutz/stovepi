#!/usr/bin/python3
'''
module to max31850k with 1wire interface

Call get_data then call get_temp_sensor or get_temp_board
'''

import sys
import os
import re
import logging
import traceback
import glob
import time

DEVICE_PREFIX="/sys/bus/w1/devices/"
DEVICE_POSTFIX="/w1_slave"

TEMP_SANITY_CHECK_MIN = 0
TEMP_SANITY_CHECK_MAX = 1200

NUM_RETRIES = 30
RETRY_WAIT = 1

#Number of decimal digits to round to, set to 0 to round to nearest integeter temp
#also forced to int because resolution of thermocouple is above 1 degree F
TEMP_RESOLUTION = 0


'''
cat /sys/bus/w1/devices/3b-0d800cc77eec/w1_slave
48 01 00 1a f0 ff ff ff 88 : crc=88 YES
48 01 00 1a f0 ff ff ff 88 t=20500
'''

def CtoF(degreesC):
    return int(round(degreesC * 9 / 5 + 32, TEMP_RESOLUTION))
       
DEVICE_TYPE_MAX31850 = "3b-"
DEVICE_TYPE_DS18B20 = "28-"

def list_devices(device_type=DEVICE_TYPE_MAX31850):
    devs = []
    for path in glob.glob(DEVICE_PREFIX + device_type + "*"):
        devs.append(os.path.basename(path))
    return devs


class max_31850_w1:
    
    def __init__(self, device):
        self.device_id = device
        self.device_path = DEVICE_PREFIX + self.device_id + DEVICE_POSTFIX
        
    def _reset_data(self):
        self.board_temp = -1
        self.sensor_temp = -1
    
    def _temp_sanity_check(self):
        if (self.sensor_temp < TEMP_SANITY_CHECK_MIN) or (self.sensor_temp > TEMP_SANITY_CHECK_MAX):
            self._reset_data()
            logging.error("Error Reading Thermocouple: temperature %i out of range (%i,%i)" % (temp, TEMP_SANITY_CHECK_MIN, TEMP_SANITY_CHECK_MAX))
    
    def get_temp_sensor(self):
        return self.sensor_temp
        
    def get_temp_board(self):
        return self.board_temp
        
    '''
    get data from board, returns flags which should be 0
    '''
    def get_data(self):
        self._reset_data()
        
        tries = 0
        
        while (tries < NUM_RETRIES):    
            try:    
                with open(self.device_path) as f:
                    lines = f.readlines()
                    if len(lines) == 2:
                        match =  re.search(r'''YES\s?$''', lines[0])
                        if match:
                            match = re.search(r'''^([a-f0-9])([a-f0-9]) ([a-f0-9]{2}) ([a-f0-9])([a-f0-9]) ([a-f0-9]{2}) ''', lines[1])
                            if match:
                                sensor_temp_low = match.group(1)
                                sensor_temp_flags = match.group(2)
                                sensor_temp_high = match.group(3)
                                board_temp_decimal = match.group(4)
                                flags_hex = match.group(5)
                                board_temp = match.group(6)
                                
                                self.sensor_temp = CtoF(int("0x" + sensor_temp_high + sensor_temp_low, 16))
                                self.board_temp = CtoF(int("0x" + board_temp, 16))
                                                            
                                flags = int("0x"+flags_hex, 16)
                                flags = flags & 7
                                
                                if flags > 0:
                                    self._reset_data()
                                    if (flags & 1) == 1:
                                        logging.error("Error Reading Thermocouple: Open Circuit for thermocouple %s" % (self.device_id))
                                    if (flags & 2) == 2:
                                        logging.error("Error Reading Thermocouple: Short to GND for thermocouple %s" % (self.device_id))
                                    if (flags & 4) == 4:
                                        logging.error("Error Reading Thermocouple: Short to VDD for thermocouple %s" % (self.device_id))
                            else:
                                #error reading temp
                                logging.error("Error Reading Thermocouple: error parsing temperature for thermocouple %s" % (self.device_id))
                                self._reset_data()
                        else:
                            #log error, invalid data from sensora
                            logging.error("Error Reading Thermocouple: invalid data from thermocouple %s" % (self.device_id))
                            self._reset_data()
                    else:
                        #log error reading file, invalid number of files
                        logging.error("Error Reading Thermocouple: unexpected number lines in file for thermocouple %s" % (self.device_id))
                        self._reset_data()
            except Exception as e:
                logging.error(traceback.format_exc())
                self._reset_data()

            if (self.sensor_temp != -1):
                self._temp_sanity_check()
            #print("board temp: %i, tries : %i" % (self.sensor_temp))
            if (self.sensor_temp != -1):
                break;
            tries = tries + 1
            time.sleep(RETRY_WAIT)
        
        
        

def main():
    for dev in list_devices():
        print("Thermocouple ID: %s" % (dev)) 
        thermocouple = max_31850_w1(device=dev)
        thermocouple.get_data()
        print("Thermocouple temp: %i" % (thermocouple.get_temp_sensor()))
        print("Board temp: %i" % (thermocouple.get_temp_board()))
        print()
        
    
if __name__ == "__main__":
    # execute only if run as a script
    main()
