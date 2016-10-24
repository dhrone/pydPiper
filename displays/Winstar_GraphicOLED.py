#!/usr/bin/python
# coding: UTF-8

# Winstar WEG010032ALPP5N00000 Graphic OLED and WS0010 OLED driver code for
# Raspberry Pi GPIO library. Some code originally found at
# http://forums.adafruit.com/viewtopic.php?f=8&t=29207&start=15#p163445
# Based on http://www.rpiblog.com/2012/11/interfacing-16x2-lcd-with-raspberry-pi.html
# Massive respec to UHCLEM in that post for getting me on the right track.
#
# Timing & initialisation issues resolved with help of LCD Initialization guide
# http://web.alfredstate.edu/weimandn/lcd/lcd_initialization/lcd_initialization_index.html
# I also found this helpful http://www.8051projects.net/lcd-interfacing/commands.php
#
# Find the latest version of this file at https://gist.github.com/lardconcepts/4947360/
# Fork and comment but I'd REALLY appreciate getting the graphics mode working.
# I'm trying to achieve "full height" letters, 32 pixels high. Anyone?
#
# based on code from lrvick and LiquidCrystal
# lrvic - https://github.com/lrvick/raspi-hd44780/blob/master/hd44780.py
# LiquidCrystal - https://github.com/arduino/Arduino/blob/master/libraries/LiquidCrystal/LiquidCrystal.cpp
#
# For Winstar WEG1xxxxxx OLED displays, I've wired it up as follows:
#   OLED PN    | FUNCT    | GPIO    | P1 pin | Audiophonics pin
#       4        RS         25        22       26
#       5        R/W        18        12       N/A (tied to GND)
#       6        E          24        18       24
#        11      D4         23        16       22
#       12       D5         17        11       18
#       13       D6         21        13       16
#       14       D7         22        15       10
#       15       CS1         9        21       N/A
#       16       CS2         1         5       N/A
#
#   Handy Binary to Hex converter
#   0x0 = 0000    0x1 = 0001    0x2 = 0010    0x3 = 0011    0x4 = 0100    0x5 = 0101
#   0x6 = 0110    0x7 = 0111    0x8 = 1000    0x9 = 1001    0xa = 1010    0xb = 1011
#   0xc = 1100    0xd = 1101    0xe = 1110    0xf = 1111
#
#   For some reason, with the Winstar in 4-bit mode, the command needs 0x00 before
#   the real command. For example, shift whole display right is 0001,1100 = 0x01,0x0c
#   So you prefix with 0x00 and, in the next command, combine the two 4-groups into 0x1c eg:
#   lcd.write4bits(0x00)
#  lcd.write4bits(0x1c)
#
# PS - Adafruit WebIDE FTMFW! http://learn.adafruit.com/webide/


import time
import RPi.GPIO as GPIO


# Make sure to set your pin mappings to the correct wiring for your display!!

# Pin Mappings V2
#OLED_DB4=25
#OLED_DB5=24
#OLED_DB6=23
#OLED_DB7=15
#OLED_RS=7
#OLED_E=8

# Pin Mappings V3
OLED_DB4=25
OLED_DB5=24
OLED_DB6=23
OLED_DB7=27
OLED_RS=7
OLED_E=8


class Winstar_GraphicOLED:

    # commands
    LCD_CLEARDISPLAY = 0x01
    LCD_RETURNHOME = 0x02
    LCD_ENTRYMODESET = 0x04
    LCD_DISPLAYCONTROL = 0x08
    LCD_CURSORSHIFT = 0x10
    LCD_FUNCTIONSET = 0x20
    LCD_SETCGRAMADDR = 0x40
    LCD_SETDDRAMADDR = 0x80

    # flags for display entry mode
    LCD_ENTRYRIGHT = 0x00
    LCD_ENTRYLEFT = 0x02
    LCD_ENTRYSHIFTINCREMENT = 0x01
    LCD_ENTRYSHIFTDECREMENT = 0x00

    # flags for display on/off control
    LCD_DISPLAYON = 0x04
    LCD_DISPLAYOFF = 0x00
    LCD_CURSORON = 0x02
    LCD_CURSOROFF = 0x00
    LCD_BLINKON = 0x01
    LCD_BLINKOFF = 0x00

    # flags for display/cursor shift
    LCD_DISPLAYMOVE = 0x08
    LCD_CURSORMOVE = 0x00

    # flags for display/cursor shift
    LCD_DISPLAYMOVE = 0x08
    LCD_CURSORMOVE = 0x00
    LCD_MOVERIGHT = 0x04
    LCD_MOVELEFT = 0x00

    # flags for function set
    LCD_8BITMODE = 0x10
    LCD_4BITMODE = 0x00
    LCD_2LINE = 0x08
    LCD_1LINE = 0x00
    LCD_5x10s = 0x04
    LCD_5x8DOTS = 0x00

    character_translation = [   0,0,0,0,0,0,0,0,0,32,                        #0
                                0,0,0,0,0,0,0,0,0,0,                        #10
                                0,0,0,0,0,0,0,0,0,0,                        #20
                                0,0,32,33,34,35,36,37,38,39,                #30
                                40,41,42,43,44,45,46,47,48,49,              #40
                                50,51,52,53,54,55,56,57,58,59,              #50
                                60,61,62,63,64,65,66,67,68,69,              #60
                                70,71,72,73,74,75,76,77,78,79,              #70
                                80,81,82,83,84,85,86,87,88,89,              #80
                                90,91,92,93,94,95,96,97,98,99,              #90
                                100,101,102,103,104,105,106,107,108,109,    #100
                                110,111,112,113,114,115,116,117,118,119,    #110
                                120,121,122,123,124,125,126,0,0,0,          #120
                                0,0,0,0,0,0,0,0,0,0,                        #130
                                0,0,0,0,0,0,0,0,0,0,                        #140
                                0,0,0,0,0,0,0,0,0,0,                        #150
                                32,33,204,179,198,32,32,176,209,221,        #160
                                32,215,32,32,220,32,210,177,32,32,          #170
                                211,200,188,32,32,32,210,216,227,226,       #180
                                229,143,152,152,65,203,153,65,175,196,       #190
                                145,146,144,147,73,73,73,73,194,166,        #200
                                136,137,135,206,79,88,201,129,130,128,      #210
                                131,89,254,195,156,157,155,205,158,97,      #220
                                32,196,149,150,148,151,162,163,161,164,     #230
                                111,167,140,141,139,207,142,214,192,133,    #240
                                134,132,117,121,250,202 ]                   #250

    def __init__(self, datalines=[25, 24, 23, 27], rs=7, e=8, simulate=False):
        # Default arguments are appropriate for Raspdac V3 only!!!

        # Pin Mappings V2
        #OLED_DB4=25
        #OLED_DB5=24
        #OLED_DB6=23
        #OLED_DB7=15
        #OLED_RS=7
        #OLED_E=8

        # Pin Mappings V3
        #OLED_DB4=25
        #OLED_DB5=24
        #OLED_DB6=23
        #OLED_DB7=27
        #OLED_RS=7
        #OLED_E=8

        self.pins_db = datalines
        self.pin_rs = rs
        self.pin_e = e

        self.numlines=2

        self.simulate = simulate

        # To make testing easier, displays support a simulated mode
        if simulate == True:
            import curses
            self.stdscr = curses.initscr()
            self.curx = 0
            self.cury = 0
        else:
            import RPi.GPIO as GPIO



    def oledReset(self):
        if not self.simulate:
            GPIO.setmode(GPIO.BCM)
            GPIO.setwarnings(False)

            # Initialize GPIO pins
            for pin in self.pins_db:
               GPIO.setup(pin, GPIO.OUT, initial=GPIO.LOW)

            GPIO.setup(OLED_E, GPIO.OUT, initial=GPIO.LOW)
            GPIO.setup(OLED_RS, GPIO.OUT, initial=GPIO.LOW)

            # initialization sequence taken from audiophonics.fr site
            # there is a good writeup on the HD44780 at Wikipedia
            # https://en.wikipedia.org/wiki/Hitachi_HD44780_LCD_controller

            # Assuming that the display may already be in 4 bit mode
            # send five 0000 instructions to resync the display
            # NOTE:  There is a resync function that is included later but is
            #        not being used here due to the need to place the display in
            #        8 bit mode temporarily
            for i in range(1,5):
                self.writeonly4bits(0x00, False)

            self.delayMicroseconds(1000)

            # Now place in 8 bit mode so that we start from a known state
            # issuing function set twice in case we are in 4 bit mode
            self.writeonly4bits(0x03, False)
            self.writeonly4bits(0x03, False)

            self.delayMicroseconds(1000)

            # placing display in 4 bit mode
            self.writeonly4bits(0x02, False)
            self.delayMicroseconds(1000)

            # From this point forward, we need to use write4bits function which
            # implements the two stage write that 4 bit mode requires

            self.write4bits(0x08, False) # Turn display off
            self.write4bits(0x29, False) # Function set for 4 bits, 2 lines, 5x8 font, Western European font table
            self.write4bits(0x06, False) # Entry Mode set to increment and no shift
            self.write4bits(0x17, False) # Set to char mode and turn on power
            self.write4bits(0x01, False) # Clear display and reset cursor
            self.write4bits(0x0c, False) # Turn on display
        else:
            self.stdscr.clear()
            self.curx = 0
            self.cury = 0


    def home(self):
        if not self.simulate:
            self.write4bits(self.LCD_RETURNHOME) # set cursor position to zero
            self.delayMicroseconds(2000) # this command takes a long time!
        else:
            self.curx = 0
            self.cury = 0

    def clear(self):
        if not self.simulate:
            self.write4bits(self.LCD_CLEARDISPLAY) # command to clear display
            self.delayMicroseconds(2000) # 2000 microsecond sleep, clearing the display takes a long time
        else:
            self.stdscr.clear()
            self.stdscr.refresh()
            self.curx = 0
            self.cury = 0

    def setCursor(self, col, row):

        if not self.simulate:
            self.row_offsets = [ 0x00, 0x40, 0x14, 0x54 ]

            if (row > self.numlines):
                row = self.numlines - 1 # we count rows starting w/0

            self.write4bits(self.LCD_SETDDRAMADDR | (col + self.row_offsets[row]))
        else:
            self.curx = col
            self.cury = row


    def noDisplay(self):
        ''' Turn the display off (quickly) '''

        if not self.simulate:
            self.displaycontrol &= ~self.LCD_DISPLAYON
            self.write4bits(self.LCD_DISPLAYCONTROL | self.displaycontrol)


    def display(self):
        ''' Turn the display on (quickly) '''

        if not self.simulate:
            self.displaycontrol |= self.LCD_DISPLAYON
            self.write4bits(self.LCD_DISPLAYCONTROL | self.displaycontrol)


    def noCursor(self):
        ''' Turns the underline cursor on/off '''

        if not self.simulate:
            self.displaycontrol &= ~self.LCD_CURSORON
            self.write4bits(self.LCD_DISPLAYCONTROL | self.displaycontrol)


    def cursor(self):
        ''' Cursor On '''

        if DISPLAY_INSTALLED:
            self.displaycontrol |= self.LCD_CURSORON
            self.write4bits(self.LCD_DISPLAYCONTROL | self.displaycontrol)


    def noBlink(self):
        ''' Turn on and off the blinking cursor '''

        if not self.simulate:
            self.displaycontrol &= ~self.LCD_BLINKON
            self.write4bits(self.LCD_DISPLAYCONTROL | self.displaycontrol)


    def DisplayLeft(self):
        ''' These commands scroll the display without changing the RAM '''

        if not self.simulate:
            self.write4bits(self.LCD_CURSORSHIFT | self.LCD_DISPLAYMOVE | self.LCD_MOVELEFT)


    def scrollDisplayRight(self):
        ''' These commands scroll the display without changing the RAM '''

        if not self.simulate:
            self.write4bits(self.LCD_CURSORSHIFT | self.LCD_DISPLAYMOVE | self.LCD_MOVERIGHT);


    def leftToRight(self):
        ''' This is for text that flows Left to Right '''

        if not self.simulate:
            self.displaymode |= self.LCD_ENTRYLEFT
            self.write4bits(self.LCD_ENTRYMODESET | self.displaymode);


    def rightToLeft(self):
        ''' This is for text that flows Right to Left '''

        if not self.simulate:
            self.displaymode &= ~self.LCD_ENTRYLEFT
            self.write4bits(self.LCD_ENTRYMODESET | self.displaymode)


    def autoscroll(self):
        ''' This will 'right justify' text from the cursor '''

        if not self.simulate:
            self.displaymode |= self.LCD_ENTRYSHIFTINCREMENT
            self.write4bits(self.LCD_ENTRYMODESET | self.displaymode)


    def noAutoscroll(self):
        ''' This will 'left justify' text from the cursor '''

        if not self.simulate:
            self.displaymode &= ~self.LCD_ENTRYSHIFTINCREMENT
            self.write4bits(self.LCD_ENTRYMODESET | self.displaymode)


    def writeonly4bits(self, bits, char_mode=False):

        if not self.simulate:
            if bits > 15: return

            #self.delayMicroseconds(1000)
            bits = bin(bits)[2:].zfill(4)

            GPIO.output(self.pin_rs, char_mode)

            for pin in self.pins_db:
                GPIO.output(pin, False)

            for i in range(4):
                if bits[i] == "1":
                    GPIO.output(self.pins_db[::-1][i], True)
            self.pulseEnable()



    def write4bits(self, bits, char_mode=False):

        if not self.simulate:

            ''' Send command to LCD '''
            #self.delayMicroseconds(1000) # 1000 microsecond sleep

            bits = bin(bits)[2:].zfill(8)

            GPIO.output(self.pin_rs, char_mode)

            for pin in self.pins_db:
                GPIO.output(pin, False)

            for i in range(4):
                if bits[i] == "1":
                    GPIO.output(self.pins_db[::-1][i], True)

            self.pulseEnable()

            for pin in self.pins_db:
                GPIO.output(pin, False)

            for i in range(4, 8):
                if bits[i] == "1":
                    GPIO.output(self.pins_db[::-1][i - 4], True)

            self.pulseEnable()
            # self.delayMicroseconds(1000)
            #self.waitForReady()
            #self.delayMicroseconds(5)


    def resyncDisplay(self):
        # Per the last page (pg 24) of OLED doc located at
        # www.picaxe.com/docs/oled.pdf
        # To resync the display send 5 0000's and then
        # two function sets for 4 bit mode 0010
        # The display should now be resynced to be ready to accept a new cmd

        if not self.simulate:
            for i in range(1,5):
                self.writeonly4bits(0x0, False)
            self.write4bits(0x02, False)



    def delayMicroseconds(self, microseconds):
        seconds = microseconds / 1000000.0 # divide microseconds by 1 million for seconds
        time.sleep(seconds)


    def pulseEnable(self):
        # the pulse timing in the 16x2_oled_volumio 2.py file is 1000/500
        # the pulse timing in the original version of this file is 10/10
        # with a 100 post time for setting

        if not self.simulate:
            GPIO.output(self.pin_e, False)
            self.delayMicroseconds(.1) # 1 microsecond pause - enable pulse must be > 450ns
            GPIO.output(self.pin_e, True)
            self.delayMicroseconds(.1) # 1 microsecond pause - enable pulse must be > 450ns
            #time.sleep(0.000000001)
            GPIO.output(self.pin_e, False)
            #self.delayMicroseconds(10) # commands need > 37us to settle


    def message(self, text):
        ''' Send string to LCD. Newline wraps to second line'''

        if not self.simulate:
            for char in text:
                if char == '\n':
                    self.write4bits(0xC0) # next line

                else:
                    #time.sleep(.000001)

                    # Translate incoming character into correct value for European charset
                    # and then send it to display.  Use space if character is out of range.
                    c = ord(char)
                    if c > 255: c = 32
                    self.write4bits(self.character_translation[c], True)
        else:
            self.stdscr.addstr(self.cury, self.curx, text.encode('utf-8'))
            self.stdscr.refresh()


if __name__ == '__main__':

  try:

    print "Winstar OLED Display Test"
    lcd = Winstar_GraphicOLED()
    lcd.oledReset()
    lcd.home()
    lcd.clear()

    lcd.message("Winstar OLED\nPi Powered")
    time.sleep(4)

    lcd.home()
    lcd.clear()

    accent_min = u"àáâãäçèéëêìíî \nïòóôöøùúûüþÿ"
    #for char in accent_min: print char, ord(char)
    lcd.message(accent_min)
    time.sleep(5)

    lcd.home()
    lcd.clear()

    accent_maj = u"ÀÁÂÆÇÈÉÊËÌÍÎÐ \nÑÒÓÔÕÙÚÛÜÝÞß"
    #for char in accent_maj: print char, ord(char)
    lcd.message(accent_maj)

    time.sleep(5)
    lcd.home()
    lcd.clear()


  except KeyboardInterrupt:
    pass

  finally:
    lcd.home()
    lcd.clear()
    lcd.message("Goodbye!")
    time.sleep(2)
    lcd.home()
    lcd.clear()
    if not lcd.simulate:
        GPIO.cleanup()
    else:
        curses.endwin()
    print "Winstar OLED Display Test Complete"
