#!/usr/bin/python3
'''
async buttons
'''

import RPi.GPIO as GPIO
import sys
import asyncio
import time

GPIO.setmode(GPIO.BCM)

PIN_BUTTON1 = 23
PIN_BUTTON2 = 24
PIN_BUTTON3 = 25

DEBOUNCE_TIME = 250

class buttons:
    
    def __init__(self):
        GPIO.setup(PIN_BUTTON1, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.add_event_detect(PIN_BUTTON1, GPIO.FALLING, callback=self.button_action, bouncetime=DEBOUNCE_TIME)
        
        GPIO.setup(PIN_BUTTON2, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.add_event_detect(PIN_BUTTON2, GPIO.FALLING, callback=self.button_action, bouncetime=DEBOUNCE_TIME)
        
        GPIO.setup(PIN_BUTTON3, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.add_event_detect(PIN_BUTTON3, GPIO.FALLING, callback=self.button_action, bouncetime=DEBOUNCE_TIME)


    def button_action(self, pin):
        
        if self._filter_false_presses(pin):
                   
            if pin == PIN_BUTTON1:
                self.button1_action()
            if pin == PIN_BUTTON2:
                self.button2_action()
            if pin == PIN_BUTTON3:
                self.button3_action()
                
    
    def button1_action(self):
        print("button press: 1")
    
    def button2_action(self):
        print("button press: 2")
        
    def button3_action(self):
        print("button press: 3")
        
    def _filter_false_presses(self, pin):
        i = 0
        positives = 0
        while (i < 10):
            i += 1
            time.sleep(.01)
            if GPIO.input(pin) == GPIO.LOW:
                positives += 1
        #debug
        #print("Pin: %i, positives: %i" % (pin, positives))

        if positives > 7:
            return True
        else:
            return False



def main():
    b = buttons()
    while True:
        time.sleep(1)
        


if __name__ == "__main__":
    # execute only if run as a script
    main()

