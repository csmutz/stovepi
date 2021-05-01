#!/usr/bin/python3
'''
Module to handle attached arduino via firmata protocol

firmata/arduino used in various situations:
- analog reads
- 5V IO


'''

import pyfirmata

import time

class firmduino:
    
    def __init__(self):
        self._line2 = ""
        
def main():
    #board = Arduino(Arduino.AUTODETECT)
    #time.sleep(10)
    board = pyfirmata.Arduino('/dev/ttyUSB0')
    
    #required for analog inputs
    it = pyfirmata.util.Iterator(board)
    it.start()
    
    #shut off relays, power up board
    #board.digital[7].write(1)
    #board.digital[8].write(1)
    #board.digital[6].write(1)
    
    board.digital[5].mode = pyfirmata.PWM
    board.digital[5].write(.1)
    
    board.digital[3].mode = pyfirmata.PWM
    board.digital[3].write(.1)
    
    
    
    time.sleep(1)
    #read analog temp value
    board.analog[4].enable_reporting()
    print(board.analog[4].read())
    
    
    #time.sleep(10)
    #turn on relay
    #board.digital[7].write(0)
    #time.sleep(10)
    #turn off relay
    #board.digital[7].write(1)   
 
if __name__ == "__main__":
    # execute only if run as a script
    main()
