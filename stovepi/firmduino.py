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
PWM2_LOW = .15
PWM2_MED = .3
PWM2_HIGH = .45

#bedroom
PWM1_OFF = 0
PWM1_LOW = 0
PWM1_MED = .08
PWM1_HIGH = .16
#PWM2_HIGH = .24

TEMP_STOVE_FAN_ON = 475
TEMP_STOVE_FAN_OFF = 375
TEMP_FANS_ON_LOW = 300
TEMP_FANS_ON_MED = 400
TEMP_FANS_ON_HIGH = 550


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
        
        #shut off relays, power up board
        self.board.digital[RELAY1_PIN].write(1)
        #disabled to save a small amount of power
        #self.board.digital[RELAY2_PIN].write(1)
        
        time.sleep(1)
        self.board.digital[RELAY_POWER_PIN].write(1)
    
    
        self.board.digital[PWM1_PIN].mode = pyfirmata.PWM
        self.board.digital[PWM1_PIN].write(PWM1_OFF)
    
        self.board.digital[PWM2_PIN].mode = pyfirmata.PWM
        self.board.digital[PWM2_PIN].write(PWM2_OFF)
        
        
        #wait to enable reads
        #time.sleep(1)
        self.board.analog[ANALOG_PIN].enable_reporting()

    
    def disable_relays(self):
        self.board.digital[RELAY_POWER_PIN].write(0)
    
    def enable_relays(self):
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
    
    def set_relay1(self, value):
        if value:
            self.board.digital[RELAY1_PIN].write(0)
        else:
            self.board.digital[RELAY1_PIN].write(1)
    
    def read_analog(self):
        return self.board.analog[ANALOG_PIN].read()

    def __del__(self):
        print("firmduino destructor: disabling relays")
        self.disable_relays()
        self.board.digital[RELAY1_PIN].write(1)
    
    '''
    update fan control
    '''
    def update_fans(self):
        if self.state.fan_pause > 0:
            self.set_relay1(True)
            self.state.stove_fan = False
        elif self.state.stove > 0:
            if self.state.stove > TEMP_STOVE_FAN_ON:
                self.set_relay1(False)
                self.state.stove_fan = True
            if self.state.stove < TEMP_STOVE_FAN_OFF:
                self.set_relay1(True)
                self.state.stove_fan = False
        else:
            self.logger.error("Stove temp of %i invalid, setting fan to on" % (log['stove']))
            self.set_relay1(False)
            self.state.stove_fan = True
        
        
        
        if self.state.fan_pause > 0:
            self.set_pwm1(PWM1_OFF)
            self.set_pwm2(PWM2_OFF)
        else:
            if self.state.stove > TEMP_FANS_ON_LOW:
                if self.state.stove > TEMP_FANS_ON_MED:
                    if self.state.stove > TEMP_FANS_ON_HIGH:
                        self.set_pwm1(PWM1_HIGH)
                        self.set_pwm2(PWM2_HIGH)
                    else:
                        self.set_pwm1(PWM1_MED)
                        self.set_pwm2(PWM2_MED)
                else:
                    self.set_pwm1(PWM1_LOW)
                    self.set_pwm2(PWM2_LOW)
            else:
                self.set_pwm1(PWM1_OFF)
                self.set_pwm2(PWM2_OFF)
        
       
        
def main():
    fduino = firmduino(None)
    
    print("settings pwm1 to %f" % (PWM1_LOW))
    fduino.set_pwm1(PWM1_LOW)
    
    print("settings pwm2 to %f" % (PWM2_LOW))
    fduino.set_pwm2(PWM2_LOW)
        
    #time.sleep(30)

    print("analog value: %f" % fduino.read_analog())

if __name__ == "__main__":
    # execute only if run as a script
    main()
