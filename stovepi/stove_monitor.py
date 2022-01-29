#!/usr/bin/python3
'''
main monitor script


TODO: 
  -general retry, exception catching 
  -error logging to file
  -alarm on thresholds air_quality
  -button to display more temps?
  -long term logging, system syslog
  -startup, restart scripts

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
import buttons
import alarm

import logging
import logging.handlers

#main loop interval, in min
POLL_INTERVAL = 1
#time to wait for refresh following relay change in sec
RELAY_CHANGE_WAIT_INTERVAL = 3
THERMOCOUPLE_DEV = "3b-0d800cc77eec"

LOGFILE_CURRENT = "/dev/shm/stovepi_current.json"
LOGFILE_HISTORY = "/dev/shm/stovepi_history.json"
LOGFILE_HISTORY_CSV = "/dev/shm/stovepi_history.csv"
LOGFILE_ERRORS = "/dev/shm/stovepi_errors.json"

LOG_HISTORY_DAYS = .5


log_history = deque(maxlen=int(60*24*LOG_HISTORY_DAYS/POLL_INTERVAL))


def format_log(state):
    log = {}
    
    log['fan_pause'] = state.fan_pause
    log['air_quality'] = state.air_quality
    log['stove'] = state.stove
    log['board'] = state.board

    log['ceiling'] = state.ceiling
    log['vent'] = state.vent
    log['stovepi'] = state.stovepi
    log['upstairs'] = state.upstairs
    log['downstairs'] = state.downstairs
    log['hvac'] = state.hvac
    
    log['stove_fan'] = state.stove_fan
    log['fan_pause'] = state.fan_pause
    log['date'] = state.date

    log['alarm'] = state.alarm

    log['fan_house'] = state.fan_house
    log['fan_bedroom'] = state.fan_bedroom

    log_history.append(log)
    
    return json.dumps(log)
    


def write_log(state):
    log_json = format_log(state)
    
    with open(LOGFILE_CURRENT,"w") as f:
        f.write(log_json)    
    
    with open(LOGFILE_HISTORY,"a") as f:
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
global state
'''
class global_state:
    def __init__(self):
        #minutes to disable fans
        self.fan_pause = 0
        self.air_quality = None
        self.stove = None
        self.board = None
        
        self.ceiling = None
        self.vent = None
        self.stovepi = None
        self.upstairs = None
        self.downstairs = None
        self.hvac = None
        
        self.stove_fan = firmduino.STOVE_FAN_LEVEL_MED
        self.fan_pause = 0
        
        self.alarm_pause = 0
        self.alarm = False
        
        self.fan_house = "off"
        self.fan_bedroom = "off"
        
        self.date = None
   
       

def main():
    logger = logging.getLogger('stovepi')
    logger.setLevel(logging.WARNING)
    handler = logging.handlers.SysLogHandler(address = '/dev/log')
    formatter = logging.Formatter('%(name)s: %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
        
    logger.warning("Starting StovePI")
    
    
    
    last_poll = int(time.time())
    
    
    #initialize objects
    state = global_state()
    dt = dallas_temp.dallas_temp()
    thermocouple = max31850_w1.max_31850_w1(device=THERMOCOUPLE_DEV)
    fduino = firmduino.firmduino(state)
    display = lcd.lcd(state)
    al = alarm.alarm(state)
    bt = buttons.buttons(state, display, al, fduino)
        
    while True:
        
        #move this to dt object?
        state.ceiling = dt.get_temp("ceiling")
        state.upstairs = dt.get_temp("upstairs")
        state.stovepi = dt.get_temp("stovepi")
        state.downstairs = dt.get_temp("downstairs")
        state.hvac = dt.get_temp("hvac")
        state.vent = dt.get_temp("vent")
                
        state.air_quality = fduino.read_analog()
                        
        thermocouple.get_data()
        state.stove = thermocouple.get_temp_sensor()
        state.board = thermocouple.get_temp_board()
                
        #date is date of last thermocouple update
        state.date = datetime.datetime.now().isoformat()
                
        last_stove_fan_state = state.stove_fan
        fduino.update_fans()
        
        if state.stove_fan != last_stove_fan_state:
            #wait for interference from relay changes before refreshing screen
            time.sleep(3)
                        
        display.output_temp()
        write_log(state)
        
        if state.fan_pause > 0:
            state.fan_pause -= POLL_INTERVAL
        if state.fan_pause < 0:
            state.fan_pause = 0
        
        if state.alarm_pause > 0:
            state.alarm_pause -= POLL_INTERVAL
        if state.alarm_pause < 0:
            state.alarm_pause = 0
        
        time.sleep(last_poll + POLL_INTERVAL * 60 - time.time())
        last_poll = last_poll + POLL_INTERVAL * 60

    
    
if __name__ == "__main__":
    main()
