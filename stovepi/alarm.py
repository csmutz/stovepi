#!/usr/bin/python3
'''
buzzer
'''

import RPi.GPIO as GPIO
import sys
import time

GPIO.setmode(GPIO.BCM)

PIN_PWM = 18
PWM_FREQ = 10000

BEEP_DUTY = 5
BEEP_LEN = .1
ALARM_DUTY = 100

class alarm:
    
    def __init__(self):
        GPIO.setup(PIN_PWM, GPIO.OUT)
        self.pwm = GPIO.PWM(PIN_PWM, PWM_FREQ)
        
    def alarm_start(self):
        self.pwm.start(ALARM_DUTY)
    
    def alarm_stop(self):
        self.pwm.stop()
        
    def beep(self):
        self.pwm.start(BEEP_DUTY)
        time.sleep(BEEP_LEN)
        self.pwm.stop()


def main():
    a = alarm()
    time.sleep(10)
    a.beep()
    

if __name__ == "__main__":
    # execute only if run as a script
    main()

