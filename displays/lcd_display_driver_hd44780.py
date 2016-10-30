#!/usr/bin/python
# coding: UTF-8

# Driver for HD44780 LCD display on the RPi
# Written by: Ron Ritchey
# Derived from Lardconcepts
# https://gist.github.com/lardconcepts/4947360
# Which was also drived from Adafruit
# http://forums.adafruit.com/viewtopic.php?f=8&t=29207&start=15#p163445
#
# Useful references
# General overview of HD44780 style displays
# https://en.wikipedia.org/wiki/Hitachi_HD44780_LCD_controller
#
# More detail on initialization and timing
# http://web.alfredstate.edu/weimandn/lcd/lcd_initialization/lcd_initialization_index.html
#

import time
import RPi.GPIO as GPIO
import lcd_display_driver
import fonts


class lcd_display_driver_hd44780(lcd_display_driver.lcd_display_driver):

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

	character_translation = [
		  0,  1,  2,  3,  4,  5,  6,  7,  0, 32,  0,  0,  0,  0,  0,  0,	#0
		  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,	#16
		 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47,	#32
		 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63,	#48
		 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79,	#64
		 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 97, 93, 94, 95,	#80
		 96, 97, 98, 99,100,101,102,103,104,105,106,107,108,109,110,111,	#96
		112,113,114,115,116,117,118,119,120,121,122,123,124,125,126,  0,	#112
		  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,	#128
		  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,	#144
		160,234,236,237, 32, 92,124, 32, 34, 32, 32,126, 32, 32, 32, 32,	#160
		223, 32, 32, 32, 32,228, 32,176, 32, 32, 32,127, 32, 32, 32, 32,	#176
		 65, 65, 65, 65, 65, 65, 32, 67, 69, 69, 69, 69, 73, 73, 73, 73,	#192
		 32, 78, 79, 79, 79, 79, 79,235, 32, 85, 85, 85, 85, 89, 32,226,	#208
		 97, 97, 97, 97,225, 97, 32, 99,101,101,101,101,105,105,105,105,	#224
		111,238,111,111,111,111,239,253, 32,117,117,117,245,121, 32,121 ]	#240



	def __init__(self, rows=2, cols=16, rs=7, e=8, datalines=[25, 24, 23, 27]):
		# Default arguments are appropriate for Raspdac V3 only!!!

		self.pins_db = datalines
		self.pin_rs = rs
		self.pin_e = e

		self.rows = rows
		self.cols = cols

		self.FONTS_SUPPORTED = True


		# Sets the values to offset into DDRAM for different display lines
		self.row_offsets = [ 0x00, 0x40, 0x14, 0x54 ]

		# Set GPIO pins to handle communications to display
		GPIO.setmode(GPIO.BCM)
		GPIO.setwarnings(False)

		for pin in self.pins_db:
		   GPIO.setup(pin, GPIO.OUT, initial=GPIO.LOW)

		GPIO.setup(self.pin_e, GPIO.OUT, initial=GPIO.LOW)
		GPIO.setup(self.pin_rs, GPIO.OUT, initial=GPIO.LOW)

		# there is a good writeup on the HD44780 at Wikipedia
		# https://en.wikipedia.org/wiki/Hitachi_HD44780_LCD_controller

		# Now place in 8 bit mode so that we start from a known state
		self.write4bits(0x33, False)
		self.delayMicroseconds(1000)

		# Now place in 4 bit mode
		self.write4bits(0x32, False)
		self.delayMicroseconds(1000)

		self.write4bits(0x06, False) # Entry Mode set to increment and no shift
		self.write4bits(0x0c, False) # Turn on display
		self.write4bits(0x28, False) # Function set for 4 bits, 2 lines, 5x8 font
		self.write4bits(0x01, False) # Clear display and reset cursor

		# Set up parent class.  Note.  This must occur after display has been
		# initialized as the parent class may attempt to load custom fonts
		super(lcd_display_driver_hd44780, self).__init__(rows,cols)


	def clear(self):
		# Set cursor back to 0,0
		self.setCursor(0,0)

		# And then clear the screen
		self.write4bits(self.LCD_CLEARDISPLAY) # command to clear display
		self.delayMicroseconds(2000) # 2000 microsecond sleep, clearing the display takes a long time

	def setCursor(self, row, col):

		if row > self.rows or col > self.cols:
			raise IndexError

		if (row > self.rows):
			row = self.rows - 1 # we count rows starting w/0

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

		# Verify that there is room in the display
		# Only 8 special characters allowed

		if len(fontdata) + char > 8:
			logging.debug("Can not load fontset at position {0}.  Not enough room left".format(char))
			raise IndexError

		# Set pointer to position char in CGRAM
		self.write4bits(self.LCD_SETCGRAMADDR+(char*8))

		# Need a short sleep for display to stablize
		time.sleep(.01)

		# For each font in fontdata
		for font in fontdata:
			for byte in font:
				self.write4bits(byte, True)

	def message(self, text, row=0, col=0):
		''' Send string to LCD. Newline wraps to second line'''

		if row > self.rows or col > self.cols:
			raise IndexError

		self.setCursor(row, col)

		for char in text:
			if char == '\n':
				self.write4bits(0xC0) # next line

			else:
				# Translate incoming character into correct value for European charset
				# and then send it to display.  Use space if character is out of range.
				c = ord(char)
				if c > 255: c = 32
				self.write4bits(self.character_translation[c], True)

	def cleanup(self):
		GPIO.cleanup()

	def msgtest(self, text, wait=1.5):
		self.clear()
		lcd.message(text)
		time.sleep(wait)

if __name__ == '__main__':
	def volume_bar(vol_per, chars, fe='_', fh='/', ff='*', vle='_', vre='_', vrh='/'):
		# Algorithm for computing the volume lines
		# inputs (vol_per, characters, fontempyt, fonthalf, fontfull, fontleftempty, fontrightempty, fontrighthalf)
		ppb = percentperblock = 100.0 / chars

		buffer = ''
		i = 0
		if vol_per <= (i+.25)*ppb:
			buffer += chr(vle)
		elif (i+.25)*ppb < vol_per and vol_per <= (i+.75)*ppb:
			buffer += chr(fh)
		elif (i+.75)*ppb < vol_per:
			buffer += chr(ff)
		else:
			# Shouldnt be here
			logging.debug("Bad value in volume_bar")
			buffer += 'Y'

		for i in range(1, chars-1):
			if vol_per <= (i+.25)*ppb:
				buffer += chr(fe)
			elif (i+.25)*ppb < vol_per and vol_per <= (i+.75)*ppb:
				buffer += chr(fh)
			elif (i+.75)*ppb < vol_per:
				buffer += chr(ff)
			else:
				# Shouldnt be here
				logging.debug("Bad value in volume_bar")
				buffer += 'Y'

		i = chars - 1
		if vol_per <= (i+.25)*ppb:
			buffer += chr(vre)
		elif (i+.25)*ppb < vol_per and vol_per <= (i+.75)*ppb:
			buffer += chr(vrh)
		elif (i+.75)*ppb < vol_per:
			buffer += chr(ff)
		else:
			# Shouldnt be here
			logging.debug("Bad value in volume_bar")
			buffer += 'Y'


		return buffer

	import getopt,sys
	try:
		opts, args = getopt.getopt(sys.argv[1:],"hr:c:",["row=","col=","rs=","e=","d4=","d5=","d6=", "d7="])
	except getopt.GetoptError:
		print 'lcd_display_driver_hd44780.py -r <rows> -c <cols> --rs <rs> --e <e> --d4 <d4> --d5 <d5> --d6 <d6> --d7 <d7>'
		sys.exit(2)

	# Set defaults
	# These are for the wiring used by a Raspdac V3
	rows = 2
	cols = 16
	rs = 7
	e = 8
	d4 = 25
	d5 = 24
	d6 = 23
	d7 = 27

	for opt, arg in opts:
		if opt == '-h':
			print 'lcd_display_driver_hd44780.py -r <rows> -c <cols> --rs <rs> --e <e> --d4 <d4> --d5 <d5> --d6 <d6> --d7 <d7>'
			sys.exit()
		elif opt in ("-r", "--rows"):
			rows = int(arg)
		elif opt in ("-c", "--cols"):
			cols = int(arg)
		elif opt in ("--rs"):
			rs  = int(arg)
		elif opt in ("--e"):
			e  = int(arg)
		elif opt in ("--d4"):
			d4  = int(arg)
		elif opt in ("--d5"):
			d5  = int(arg)
		elif opt in ("--d6"):
			d6  = int(arg)
		elif opt in ("--d7"):
			d7  = int(arg)

	try:

		pins = [d4, d5, d6, d7]
		print "HD44780 LCD Display Test"
		print "ROWS={0}, COLS={1}, RS={2}, E={3}, Pins={4}".format(rows,cols,rs,e,pins) 

		lcd = lcd_display_driver_hd44780(rows,cols,rs,e,[d4, d5, d6, d7])
		lcd.clear()
		lcd.switchcustomchars(fonts.size5x8.player.fontpkg)

		lcd.message("HD44780 LCD\nPi Powered")
		time.sleep(4)

		lcd.clear()

		accent_min = u"àáâãäçèéëêìíî \nïòóôöøùúûüþÿ"
		#for char in accent_min: print char, ord(char)
		lcd.message(accent_min)
		time.sleep(2)

		lcd.clear()

		accent_maj = u"ÀÁÂÆÇÈÉÊËÌÍÎÐ \nÑÒÓÔÕÙÚÛÜÝÞß"
		lcd.message(accent_maj)

		time.sleep(2)
		lcd.clear()

		lcd.msgtest("\x00 Stop")
		lcd.msgtest("\x01 Play")
		lcd.msgtest("\x02 Pause")
		lcd.msgtest("\x03 Ethernet")
		lcd.msgtest("\x04 Wireless")
		lcd.msgtest("\x05 Music")
		lcd.msgtest("\x06 Power")
		lcd.clear()

		lcd.switchcustomchars(fonts.size5x8.speaker.fontpkg)
		lcd.msgtest("\x00\x01 SPEAKER\n\x02\x03")
		lcd.switchcustomchars(fonts.size5x8.shuffle.fontpkg)
		lcd.msgtest("\x00\x01 SHUFFLE\n\x02\x03")
		lcd.switchcustomchars(fonts.size5x8.repeat_all.fontpkg)
		lcd.msgtest("\x00\x01 REPEAT\n\x02\x03 ALL")
		lcd.switchcustomchars(fonts.size5x8.repeat_once.fontpkg)
		lcd.msgtest("\x00\x01 REPEAT\n\x02\x03 SINGLE")
		lcd.switchcustomchars(fonts.size5x8.volume.fontpkg)

		for i in range (0,101,5):
			volbar = volume_bar(i,
				14,
				fonts.size5x8.volume.e,
				fonts.size5x8.volume.h,
				fonts.size5x8.volume.f,
				fonts.size5x8.volume.el,
				fonts.size5x8.volume.er,
				fonts.size5x8.volume.hr )
			lcd.clear()
			lcd.message("Volume {0}".format(i),0,0)
			lcd.message("\x06 {0}".format(volbar),1,0)
			time.sleep(.25)

		time.sleep(2)


	except KeyboardInterrupt:
		pass

	finally:
		lcd.clear()
		lcd.message("Goodbye!")
		time.sleep(2)
		lcd.clear()
		time.sleep(.5)
		GPIO.cleanup()
		print "LCD Display Test Complete"
