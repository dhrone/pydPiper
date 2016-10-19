#!/usr/bin/python
# coding: UTF-8

# Driver for Winstar WEH001602A 16x2 OLED display on the RPi
# Written by: Ron Ritchey
# Derived from Lardconcepts
# https://gist.github.com/lardconcepts/4947360
# Which was also drived from Adafruit
# http://forums.adafruit.com/viewtopic.php?f=8&t=29207&start=15#p163445
#
# Ultimately this is a minor variation of the HD44780 controller
#
# Useful references
# General overview of HD44780 style displays
# https://en.wikipedia.org/wiki/Hitachi_HD44780_LCD_controller
#
# More detail on initialization and timing
# http://web.alfredstate.edu/weimandn/lcd/lcd_initialization/lcd_initialization_index.html
#
# Documenation for the similar Winstar WS0010 board currently available at
# http://www.picaxe.com/docs/oled.pdf

import time
import RPi.GPIO as GPIO
import lcd_display_driver


class lcd_display_driver_winstar_weh001602a(lcd_display_driver.lcd_display_driver):

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



    def __init__(self, rows=2, cols=16, rs=7, e=8, datalines=[25, 24, 23, 27]):
        # Default arguments are appropriate for Raspdac V3 only!!!

        self.pins_db = datalines
        self.pin_rs = rs
        self.pin_e = e

        self.rows = rows
        self.cols = cols

        # Sets the values to offset into DDRAM for different display lines
        self.row_offsets = [ 0x00, 0x40 ]

        # Set GPIO pins to handle communications to display
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)

        for pin in self.pins_db:
           GPIO.setup(pin, GPIO.OUT, initial=GPIO.LOW)

        GPIO.setup(self.pin_e, GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup(self.pin_rs, GPIO.OUT, initial=GPIO.LOW)

        # initialization sequence taken from audiophonics.fr site
        # there is a good writeup on the HD44780 at Wikipedia
        # https://en.wikipedia.org/wiki/Hitachi_HD44780_LCD_controller

        # Assuming that the display may already be in 4 bit mode
        # send five 0000 instructions to resync the display
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

        # Set up parent class.  Note.  This must occur after display has been
        # initialized as the parent class may attempt to load custom fonts
        super(lcd_display_driver_winstar_weh001602a, self).__init__(rows,cols)


    def clear(self):
        # Set cursor back to 0,0
        self.write4bits(self.LCD_RETURNHOME) # set cursor position to zero
        self.delayMicroseconds(2000) # this command takes a long time!

        # And then clear the screen
        self.write4bits(self.LCD_CLEARDISPLAY) # command to clear display
        self.delayMicroseconds(2000) # 2000 microsecond sleep, clearing the display takes a long time

    def setCursor(self, col, row):

        if row > self.rows or col > self.cols:
            raise IndexError

        if (row > self.numlines):
            row = self.numlines - 1 # we count rows starting w/0

        self.write4bits(self.LCD_SETDDRAMADDR | (col + self.row_offsets[row]))


    def displayoff(self):
        ''' Turn the display off (quickly) '''

        self.displaycontrol &= ~self.LCD_DISPLAYON
        self.write4bits(self.LCD_DISPLAYCONTROL | self.displaycontrol)


    def displayon(self):
        ''' Turn the display on (quickly) '''

        if not self.simulate:
            self.displaycontrol |= self.LCD_DISPLAYON
            self.write4bits(self.LCD_DISPLAYCONTROL | self.displaycontrol)


    def cursoroff(self):
        ''' Turns the underline cursor on/off '''

        self.displaycontrol &= ~self.LCD_CURSORON
        self.write4bits(self.LCD_DISPLAYCONTROL | self.displaycontrol)


    def cursoron(self):
        ''' Cursor On '''

        self.displaycontrol |= self.LCD_CURSORON
        self.write4bits(self.LCD_DISPLAYCONTROL | self.displaycontrol)


    def blinkoff(self):
        ''' Turn off the blinking cursor '''

        self.displaycontrol &= ~self.LCD_BLINKON
        self.write4bits(self.LCD_DISPLAYCONTROL | self.displaycontrol)

    def blinkon(self):
        ''' Turn on the blinking cursor '''

        self.displaycontrol |= self.LCD_BLINKON
        self.write4bits(self.LCD_DISPLAYCONTROL | self.displaycontrol)

    def write4bits(self, bits, char_mode=False):

        ''' Send command to LCD '''
        #self.delayMicroseconds(1000) # 1000 microsecond sleep

        # take the value, convert to a binary string and then zero fill
        # Note that the beginning of a bits return is 0b so [2:] used to strip that out
        bits = bin(bits)[2:].zfill(8)

        # Set as appropriate for character vs command mode
        GPIO.output(self.pin_rs, char_mode)

        # Zero the data pins
        for pin in self.pins_db:
            GPIO.output(pin, False)

        # From left to right, if the bit value is 1, set the corresponding GPIO pin
        for i in range(4):
            if bits[i] == "1":
                GPIO.output(self.pins_db[::-1][i], True)

        self.pulseEnable()

        for pin in self.pins_db:
            GPIO.output(pin, False)

        # Now set the low order bits
        for i in range(4, 8):
            if bits[i] == "1":
                GPIO.output(self.pins_db[::-1][i - 4], True)

        self.pulseEnable()

    def writeonly4bits(self, bits, char_mode=False):

            # Version of write that only sends a 4 bit value
            if bits > 15: return

            bits = bin(bits)[2:].zfill(4)

            GPIO.output(self.pin_rs, char_mode)

            for pin in self.pins_db:
                GPIO.output(pin, False)

            for i in range(4):
                if bits[i] == "1":
                    GPIO.output(self.pins_db[::-1][i], True)
            self.pulseEnable()


    def delayMicroseconds(self, microseconds):
        seconds = microseconds / 1000000.0 # divide microseconds by 1 million for seconds
        time.sleep(seconds)


    def pulseEnable(self):
        # the pulse timing in the 16x2_oled_volumio 2.py file is 1000/500
        # the pulse timing in the original version of this file is 10/10
        # with a 100 post time for setting

        GPIO.output(self.pin_e, False)
        self.delayMicroseconds(.1) # 1 microsecond pause - enable pulse must be > 450ns
        GPIO.output(self.pin_e, True)
        self.delayMicroseconds(.1) # 1 microsecond pause - enable pulse must be > 450ns
        GPIO.output(self.pin_e, False)


    def loadcustomchars(self, char, fontdata):
        # Load custom characters

        # Set pointer to position char in CGRAM
        self.write4bits(LCD_SETCGRAMADDR)

        # For each font in fontdata
        for font in fontdata:
			for data in font:
				self.write4bits(data)


    def message(self, text, row=0, col=0):
        ''' Send string to LCD. Newline wraps to second line'''

        if row > self.rows or col > self.cols:
            raise IndexError

        self.setCursor(row,col)

        for char in text:
            if char == '\n':
                self.write4bits(0xC0) # next line

            else:
                # Translate incoming character into correct value for European charset
                # and then send it to display.  Use space if character is out of range.
                c = ord(char)
                if c > 255: c = 32
                self.write4bits(self.character_translation[c], True)


if __name__ == '__main__':

  try:

    print "Winstar OLED Display Test"
    lcd = lcd_display_driver_winstar_weh001602a()
    lcd.clear()

    lcd.message("Winstar OLED\nPi Powered")
    time.sleep(4)

    lcd.clear()

    accent_min = u"àáâãäçèéëêìíî \nïòóôöøùúûüþÿ"
    #for char in accent_min: print char, ord(char)
    lcd.message(accent_min)
    time.sleep(5)

    lcd.clear()

    accent_maj = u"ÀÁÂÆÇÈÉÊËÌÍÎÐ \nÑÒÓÔÕÙÚÛÜÝÞß"
    #for char in accent_maj: print char, ord(char)
    lcd.message(accent_maj)

    time.sleep(5)
    lcd.clear()


  except KeyboardInterrupt:
    pass

  finally:
    lcd.clear()
    lcd.message("Goodbye!")
    time.sleep(2)
    lcd.clear()
    GPIO.cleanup()
    print "Winstar OLED Display Test Complete"
