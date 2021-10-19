#!/usr/bin/python3
'''
main monitor script


TODO: 
-general retry, exception catching 
-logging to file
-button to temporarily stop fans
-pwm control of fans
-long term logging, system syslog
-alarm on thresholds for temp, air_quality
-buttons, menu system, modes

'''

import time
import datetime
import sys
import os
import json
from collections import deque
import csv


import dallas_temp
import max31850_w1
import firmduino
import lcd


POLL_INTERVAL = 60
THERMOCOUPLE_DEV = "3b-0d800cc77eec"

LOGFILE_CURRENT = "/dev/shm/stovepi_current.json"
LOGFILE_HISTORY = "/dev/shm/stovepi_history.json"
LOGFILE_HISTORY_CSV = "/dev/shm/stovepi_history.csv"
LOGFILE_ERRORS = "/dev/shm/stovepi_errors.json"

LOG_HISTORY_DAYS = .5

TEMP_FAN_ON = 450
TEMP_FAN_OFF = 350
STOVE_FAN_ON = True


log_history = deque(maxlen=int(60*60*24*LOG_HISTORY_DAYS/POLL_INTERVAL))


def write_log(log):
    log_json = json.dumps(log)
    
    with open(LOGFILE_CURRENT,"w") as f:
        f.write(log_json)    
    
    log_history.append(log)
        
    with open(LOGFILE_HISTORY,"w") as f:
        for r in log_history:
            f.write(log_json)
            f.write("\n")

    with open(LOGFILE_HISTORY_CSV,"w") as outfile:
        fieldnames = ['date','stove_temp']
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)

        writer.writeheader()
        for r in log_history:
            out = {}
            out['date'] = r['date']
            out['stove_temp'] = r['stove']
            #out['board_temp'] = r['board_temp']
            writer.writerow(out)


'''
Turning the relay on turns off the stove fan

'''
def control_fans(log, fduino):
    global STOVE_FAN_ON
    if log['stove'] > 0:
        if log['stove'] > TEMP_FAN_ON:
            fduino.set_relay1(False)
            STOVE_FAN_ON = True
        if log['stove'] < TEMP_FAN_OFF:
            fduino.set_relay1(True)
            STOVE_FAN_ON = False
    else:
        logging.error("Stove temp of %i invalid, setting fan to on" % (log['stove']))
        fduino.set_relay1(False)
        STOVE_FAN_ON = True
        
    log['stove_fan'] = STOVE_FAN_ON
    

def main():
    last_poll = int(time.time())
    
    
    #initialize objects
    dt = dallas_temp.dallas_temp()
    thermocouple = max31850_w1.max_31850_w1(device=THERMOCOUPLE_DEV)
    fduino = firmduino.firmduino()
    display = lcd.lcd()
    
        
    while True:
        
        log = {}
                
        for s in dallas_temp.sensors:
            log[s] = dt.get_temp(s)
        
        log['air_quality'] = fduino.read_analog()
        
        
        thermocouple.get_data()
        log['stove'] = thermocouple.get_temp_sensor()
        log['board'] = thermocouple.get_temp_board()
        
        control_fans(log, fduino)
        
        log['date'] = datetime.datetime.now().isoformat()
        
        display.output_temp(log)
        write_log(log)
        
        time.sleep(last_poll + POLL_INTERVAL - time.time())
        last_poll = last_poll + POLL_INTERVAL

    
    
if __name__ == "__main__":
    main()
