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

FIRMATA_DEV = '/dev/ttyUSB0'

RELAY_POWER_PIN = 6
RELAY1_PIN = 7
RELAY2_PIN = 8

PWM1_PIN = 5
PWM2_PIN = 3

PWM1_DEFAULT = .1
PWM2_DEFAULT = .1

ANALOG_PIN = 4

class firmduino:
    
    def __init__(self, dev=FIRMATA_DEV):
        self.dev = dev
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
        self.board.digital[PWM1_PIN].write(PWM1_DEFAULT)
    
        self.board.digital[PWM2_PIN].mode = pyfirmata.PWM
        self.board.digital[PWM2_PIN].write(PWM2_DEFAULT)
        
        #wait to enable reads
        #time.sleep(1)
        self.board.analog[ANALOG_PIN].enable_reporting()

    
    def disable_relays(self):
        self.board.digital[RELAY_POWER_PIN].write(0)
    
    def enable_relays(self):
        self.board.digital[RELAY_POWER_PIN].write(1)
    
    def set_pwm1(self, level):
        self.board.digital[PWM1_PIN].write(level)
    
    def set_pwm2(self, level):
        self.board.digital[PWM2_PIN].write(level)
    
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
        

        
def main():
    fduino = firmduino()
    
    print("turning on relay")
    fduino.set_relay1(True)
    time.sleep(3)
    
    print("turning off relay")
    fduino.set_relay1(False)
        
    fduino.disable_relays()

    print("analog value: %f" % fduino.read_analog())

if __name__ == "__main__":
    # execute only if run as a script
    main()
