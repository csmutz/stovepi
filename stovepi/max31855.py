#!/usr/bin/python3
'''
thermocouple interface, old version
'''

import Adafruit_MAX31855.MAX31855 as MAX31855
import time
import logging
import traceback

GPIO_THERMOCOUPLE_CS  = 22
GPIO_THERMOCOUPLE_DO  = 9
GPIO_THERMOCOUPLE_CLK = 11
THERMOCOUPLE_MIN_SANE_TEMP = -100
THERMOCOUPLE_MAX_SANE_TEMP = 1200

class thermocouple:
    
    def __init__(self):
        self.sensor = thermocouple = MAX31855.MAX31855(GPIO_THERMOCOUPLE_CLK, GPIO_THERMOCOUPLE_CS, GPIO_THERMOCOUPLE_DO)
    
    def c_to_f(self, c):
        return c * 9.0 / 5.0 + 32.0
    
    def get_temp(self):
        stove_temp = None
        try:
            stove_temp = int(self.c_to_f(self.sensor.readTempC()))
        except Exception as e:
            logging.error(traceback.format_exc())
        if (stove_temp != stove_temp):
            stove_temp = None
        if stove_temp:
            if stove_temp < THERMOCOUPLE_MIN_SANE_TEMP:
                stove_temp = None
        if stove_temp:
            if stove_temp > THERMOCOUPLE_MAX_SANE_TEMP:
                stove_temp = None
        return stove_temp
    
    def get_temp_board(self):
        board_temp = None
        try:
            board_temp = int(self.c_to_f(self.sensor.readInternalC()))
        except Exception as e:
            logging.error(traceback.format_exc())
        return board_temp

def main():
    t = thermocouple()
    while(True):
        stove_temp = t.get_temp()
        board_temp = t.get_temp_board()
        
        if (stove_temp):
            print("stove: %iF" % (stove_temp))
        else:
            print("stove: error")
        
        if (board_temp):
            print("board: %iF" % (board_temp))
        else:
            print("board: error")
        print()

        time.sleep(1)
    
if __name__ == "__main__":
    # execute only if run as a script
    main()
