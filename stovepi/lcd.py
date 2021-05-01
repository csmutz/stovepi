#!/usr/bin/python3
'''
module to handle LCD communications

if used as script, print message supplied as first 2 args to screen (easy way to send message)

'''

import time
import board
import digitalio
import adafruit_character_lcd.character_lcd as characterlcd
import sys
import os
import subprocess

lcd_rs = digitalio.DigitalInOut(board.D16)
lcd_en = digitalio.DigitalInOut(board.D12)
lcd_d7 = digitalio.DigitalInOut(board.D26)
lcd_d6 = digitalio.DigitalInOut(board.D13)
lcd_d5 = digitalio.DigitalInOut(board.D6)
lcd_d4 = digitalio.DigitalInOut(board.D5)


display_modes = ["temp", "time", "menu"]

lcd_columns = 16
lcd_rows = 2

lcd = None

class lcd:
    
    def __init__(self, char_weight=2):
        self._lcd = characterlcd.Character_LCD_Mono(lcd_rs, lcd_en, lcd_d4, lcd_d5, lcd_d6, lcd_d7, lcd_columns, lcd_rows)
        self._lcd.clear()
        self._line1 = ""
        self._line2 = ""
        if (char_weight == 2 or char_weight == 3):
            self.char_weight = char_weight
        else:
            char_weight = 2
        
    def refresh(self, status, mode):
        '''
        refresh lcd given a specific mode. Must pass in a status object
        '''
        pass
    def output(self, line1="",line2=""):
        self._line1 = str(line1)[0:16]
        self._line2 = str(line2)[0:16]
        self._refresh_lcd()

    def _refresh_lcd(self):
        self._lcd.clear()
        self._lcd.message = self._line1 + "\n" + self._line2
    
    def _define_large_chars(self):
        #2 wide
        if (self.char_weight == 2):
    
            #vertical right justified
            self._lcd.create_char(0,b'\x03\x03\x03\x03\x03\x03\x03\x03')
            #vertical left justified
            self._lcd.create_char(1,b'\x18\x18\x18\x18\x18\x18\x18\x18')
        
            #top, middle only
            self._lcd.create_char(2,b'\x00\x00\x00\x00\x00\x00\x00\x1f')
        
            #top, both
            self._lcd.create_char(3,b'\x1f\x1f\x00\x00\x00\x00\x00\x1f')
        
            #top, top only
            self._lcd.create_char(4,b'\x1f\x1f\x00\x00\x00\x00\x00\x00')
        
            #bottom, middle only
            self._lcd.create_char(5,b'\x1f\x00\x00\x00\x00\x00\x00\x00')
        
            #bottom, both
            self._lcd.create_char(6,b'\x1f\x00\x00\x00\x00\x00\x1f\x1f')
        
            #degrees
            self._lcd.create_char(7,b'\x1f\x1f\x1b\x1f\x1f\x00\x00\x00')
        
        #3 wide
        else:        
    
            #vertical right justified
            self._lcd.create_char(0,b'\x07\x07\x07\x07\x07\x07\x07\x07')
            #vertical left justified
            self._lcd.create_char(1,b'\x1c\x1c\x1c\x1c\x1c\x1c\x1c\x1c')
        
            #top, middle only
            self._lcd.create_char(2,b'\x00\x00\x00\x00\x00\x00\x1f\x1f')
        
            #top, both
            self._lcd.create_char(3,b'\x1f\x1f\x1f\x00\x00\x00\x1f\x1f')
        
            #top, top only
            self._lcd.create_char(4,b'\x1f\x1f\x1f\x00\x00\x00\x00\x00')
        
            #bottom, middle only
            self._lcd.create_char(5,b'\x1f\x00\x00\x00\x00\x00\x00\x00')
        
            #bottom, both
            self._lcd.create_char(6,b'\x1f\x00\x00\x00\x00\x1f\x1f\x1f')
        
            #degrees
            self._lcd.create_char(7,b'\x1f\x1f\x1b\x1f\x1f\x00\x00\x00')


def main():
    #lcd = characterlcd.Character_LCD_Mono(lcd_rs, lcd_en, lcd_d4, lcd_d5, lcd_d6, lcd_d7, lcd_columns, lcd_rows)
    #lcd.clear()
    d = lcd()
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "STARTUP":
            #lcd.message = "Starting StovePI\n" + subprocess.check_output("hostname -I", shell=True).decode("utf-8", "ignore")
            d.output("Starting StovePI",subprocess.check_output("hostname -I", shell=True).decode("utf-8", "ignore"))
        elif sys.argv[1] == "SHUTDOWN":
            #lcd.message = "Shutting down...\nUnplug in 1 min"
            d.output("Shutting down...", "Unplug in 1 min")
        else:
            #lcd.message = "\n".join(sys.argv[1:3])
            if len(sys.argv) > 2:
                d.output(sys.argv[1], sys.argv[2])
            else:
                d.output(sys.argv[1])
    else:
        d.output("Hello World!")
    
    
    
    
    
    #lcd.clear()    
    #482
    #lcd.message = "\x00\x02\x01\x00\x03\x01 \x03\x01\x07\x00\x03\n \x05\x01\x00\x06\x01\x00\x06  \x00\x05"
    #517
    #lcd.message = " \x00 \x00\x03  \x04\x01\x07\x00\x03\n \x00  \x06\x01 \x00  \x00\x05"
    
    
if __name__ == "__main__":
    # execute only if run as a script
    main()
