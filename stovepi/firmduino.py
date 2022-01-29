#!/usr/bin/python3
'''
Module to handle attached arduino via firmata protocol

firmata/arduino used in various situations:
- analog reads
- 5V IO for relays/fans
- pwm for pwm controlled fans

Turning Stove relay fan on results in fan being shut off (default on)

'''
import pyfirmata
import time
import logging

FIRMATA_DEV = '/dev/ttyUSB0'

RELAY_POWER_PIN = 6
RELAY1_PIN = 7
RELAY2_PIN = 8

PWM1_PIN = 5
PWM2_PIN = 3

#house
PWM2_OFF = 0
PWM2_LOW = .1
PWM2_MED = .4
PWM2_HIGH = .6

#bedroom
PWM1_OFF = 0
PWM1_LOW = 0
PWM1_MED = .1
PWM1_HIGH = .2
#PWM2_HIGH = .24

TEMP_FANS_ON_LOW = 300
TEMP_FANS_OFF_MED = 420
#also low temp for high setting
TEMP_FANS_ON_MED = 460
TEMP_FANS_ON_HIGH = 500

STOVE_FAN_LEVEL_OFF = "off"
STOVE_FAN_LEVEL_LOW = "off"
STOVE_FAN_LEVEL_MED = "on"
STOVE_FAN_LEVEL_HIGH = "high"

ANALOG_PIN = 4

class firmduino:
    
    def __init__(self, state, dev=FIRMATA_DEV):
        self.state = state
        self.dev = dev
        self.logger = logging.getLogger('stovepi')
        
        self.board = pyfirmata.Arduino(self.dev)
        
        #required for analog inputs
        self.it = pyfirmata.util.Iterator(self.board)
        self.it.start()
        
        self.enable_relays()
        
        self.board.digital[PWM1_PIN].mode = pyfirmata.PWM
        self.board.digital[PWM1_PIN].write(PWM1_OFF)
    
        self.board.digital[PWM2_PIN].mode = pyfirmata.PWM
        self.board.digital[PWM2_PIN].write(PWM2_OFF)
                
        self.board.analog[ANALOG_PIN].enable_reporting()

    
    def disable_relays(self):
        self.set_relay1(False)
        self.set_relay2(False)
        self.board.digital[RELAY_POWER_PIN].write(0)
    
    def enable_relays(self):
        #set relays to default (off)
        self.set_relay1(False)
        self.set_relay2(False)
        time.sleep(1)
        self.board.digital[RELAY_POWER_PIN].write(1)
    '''
    bedroom
    '''
    def set_pwm1(self, level):
        self.board.digital[PWM1_PIN].write(level)
        self.state.fan_bedroom = level
    
    '''
    house
    '''
    def set_pwm2(self, level):
        self.board.digital[PWM2_PIN].write(level)
        self.state.fan_house = level
    
    '''
    controlled speed stove fan, enabling relay disables fan
    relays are low enabled
    '''
    def set_relay1(self, value):
        if value:
            self.board.digital[RELAY1_PIN].write(0)
        else:
            self.board.digital[RELAY1_PIN].write(1)
    
    '''
    full speed stove fan, enabling relay enables fan
    relays are low enabled
    '''
    def set_relay2(self, value):
        #make sure relay1 disabled?
        if value:
            self.board.digital[RELAY2_PIN].write(0)
        else:
            self.board.digital[RELAY2_PIN].write(1)
    
    def read_analog(self):
        return self.board.analog[ANALOG_PIN].read()

    def __del__(self):
        print("firmduino destructor: disabling relays")
        self.disable_relays()
    

    def set_fans_off(self):
        #stove fans off, room fans on low
        self.set_relay1(True)
        self.set_relay2(False)
        self.state.stove_fan = STOVE_FAN_LEVEL_OFF
        self.set_pwm1(PWM1_OFF)
        self.set_pwm2(PWM2_OFF)
    
    def set_fans_low(self):
        #stove fans off, room fans on low
        self.set_relay1(True)
        self.set_relay2(False)
        self.state.stove_fan = STOVE_FAN_LEVEL_LOW
        self.set_pwm1(PWM1_LOW)
        self.set_pwm2(PWM2_LOW)
        
    
    def set_fans_med(self):
        #all fans on med
        self.set_relay1(False)
        self.set_relay2(False)
        self.state.stove_fan = STOVE_FAN_LEVEL_MED
        self.set_pwm1(PWM1_MED)
        self.set_pwm2(PWM2_MED)
        
    
    def set_fans_high(self):
        #all fans on high
        self.set_relay1(True)
        self.set_relay2(True)
        self.state.stove_fan = STOVE_FAN_LEVEL_HIGH
        self.set_pwm1(PWM1_HIGH)
        self.set_pwm2(PWM2_HIGH)
    
    
    '''
    update fan control
    '''
    def update_fans(self):
        if self.state.fan_pause > 0:
            #off
            self.set_fans_off()
        elif self.state.stove > 0:
            if self.state.stove > TEMP_FANS_ON_HIGH:
                self.set_fans_high()
            
            if self.state.stove > TEMP_FANS_ON_MED and self.state.stove <= TEMP_FANS_ON_HIGH:
                if self.state.stove_fan == STOVE_FAN_LEVEL_HIGH:
                    self.set_fans_high()
                else:
                    self.set_fans_med()
            
            if self.state.stove > TEMP_FANS_OFF_MED and self.state.stove <= TEMP_FANS_ON_MED:
                if self.state.stove_fan == STOVE_FAN_LEVEL_MED:
                    self.set_fans_med()
                else:
                    self.set_fans_low()
            
            if self.state.stove > TEMP_FANS_ON_LOW and self.state.stove <= TEMP_FANS_OFF_MED:
                self.set_fans_low()

            if self.state.stove <= TEMP_FANS_ON_LOW:
                self.set_fans_off()

        else:
            self.logger.error("Stove temp of %i invalid, setting fan to high" % (self.state.stove))
            self.set_fans_high()
        
def main():
    fduino = firmduino(None)
    
    r1 = True
    r2 = True
    fduino.set_relay1(r1)
    fduino.set_relay2(r2)
    print("relay r1: %s, r2: %s" % (r1,r2))
        
    #print("settings pwm1 to %f" % (PWM1_LOW))
    #fduino.set_pwm1(PWM1_LOW)
    
    #print("settings pwm2 to %f" % (PWM2_LOW))
    #fduino.set_pwm2(PWM2_LOW)
        
    time.sleep(30)

    print("analog value: %f" % fduino.read_analog())

if __name__ == "__main__":
    # execute only if run as a script
    main()
