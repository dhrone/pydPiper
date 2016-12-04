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

import time, math
import RPi.GPIO as GPIO
import lcd_display_driver
import fonts
import graphics as g
from PIL import Image
import numpy as np


class lcd_display_driver_winstar_ws0010_graphics_mode(lcd_display_driver.lcd_display_driver):

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



	def __init__(self, rows=16, cols=100, rs=7, e=8, datalines=[25, 24, 23, 27]):
		# Default arguments are appropriate for Raspdac V3 only!!!

		self.pins_db = datalines
		self.pin_rs = rs
		self.pin_e = e

		self.rows = rows
		self.cols = cols

		self.fb = [[]]

		self.FONTS_SUPPORTED = True

		# Initialize the default font
		font = fonts.bmfont.bmfont('latin1_5x8.fnt')
		self.fp = font.fontpkg

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
		# send four 0000 instructions to resync the display
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
		self.write4bits(0x1F, False) # Set to char mode and turn on power
		self.write4bits(0x01, False) # Clear display and reset cursor
		self.write4bits(0x0c, False) # Turn on display

		# Set up parent class.  Note.  This must occur after display has been
		# initialized as the parent class may attempt to load custom fonts
		super(lcd_display_driver_winstar_ws0010_graphics_mode, self).__init__(rows,cols)


	def clear(self):
		# Set cursor back to 0,0
		self.setCursor(0,0) # set cursor position to zero
		self.fb = [[]]

		# And then clear the screen
		self.write4bits(self.LCD_CLEARDISPLAY) # command to clear display
		self.delayMicroseconds(2000) # 2000 microsecond sleep

	def setCursor(self, row, col):

		if row >= self.rows or col >= self.cols:
			raise IndexError

		# Convert from pixels to bytes
		row = int(math.ceil(row/8.0))

		self.write4bits(self.LCD_SETDDRAMADDR | col)
		self.write4bits(self.LCD_SETCGRAMADDR | row)


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
		# Only 8 special characters allowed with the Winstar

		if len(fontdata) + char > 8:
			logging.debug(u"Can not load fontset at position {0}.  Not enough room left".format(char))
			raise IndexError

		# Set pointer to position char in CGRAM
		self.write4bits(self.LCD_SETCGRAMADDR+(char*8))

		# Need a short sleep for display to stablize
		time.sleep(.01)

		# For each font in fontdata
		for font in fontdata:
			for byte in font:
				self.write4bits(byte, True)

	def message(self, text, row=0, col=0, varwidth=True):
		''' Send string to LCD. Newline wraps to second line'''

		if row >= self.rows or col >= self.cols:
			raise IndexError

		width = g.msgwidth(text, self.fp, varwidth)
		maxw = 0
		for i in width:
			if i > maxw:
				maxw = i
		height = len(width)*8

		img = Image.new("1", (maxw, height), 0)
		g.message(img,text,0,0, self.fp, varwidth)
		nf = g.getframe(img,0,0,self.cols,self.rows)
		self.update(nf)

# 		self.setCursor(row, col)
# 		crow = row
#
# 		for char in text:
# 			if char == '\n':
# #				self.write4bits(0xC0) # next line
# 				crow += 8
# 				if crow >= self.rows:
# 					raise IndexError
# 				self.setCursor(crow,0)
#
# 			else:
# 				# Translate incoming character into correct value for European charset
# 				# and then send it to display.  Use space if character is out of range.
# 				c = ord(char)
# 				try:
# 					cdata = fonts.size5x8.latin1.fontpkg[c]
#
# 					for byte in cdata:
# 						self.write4bits(byte, True)
# 					self.write4bits(0x00, True)
# 				except KeyError:
# 					print "Cannot find {0} in font table".format(format(c,"02x"))
# 					# Char not found
# 					pass

	def update(self, newbuf):

		rows = int(math.ceil(self.rows/8.0))
		for j in range(0, rows):
			self.setCursor(j*8,0)
			for i in range(0, self.cols):
				try:
					byte = newbuf[j][i]
				except IndexError:
					byte = 0
				self.write4bits(byte, True)

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
		print 'lcd_display_driver_winstar_weh001602a.py -r <rows> -c <cols> --rs <rs> --e <e> --d4 <d4> --d5 <d5> --d6 <d6> --d7 <d7>'
		sys.exit(2)

	# Set defaults
	# These are for the wiring used by a Raspdac V3
	rows = 16
	cols = 100
	rs = 7
	e = 8
	d4 = 25
	d5 = 24
	d6 = 23
	d7 = 27

	for opt, arg in opts:
		if opt == '-h':
			print 'lcd_display_driver_winstar_weh001602a.py -r <rows> -c <cols> --rs <rs> --e <e> --d4 <d4> --d5 <d5> --d6 <d6> --d7 <d7>'
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

#	import codecs
#	if sys.stdout.encoding != 'UTF-8':
#    		sys.stdout = codecs.getwriter('utf-8')(sys.stdout, 'strict')

	import display

	try:
		pins = [d4, d5, d6, d7]
		print "Winstar OLED Display Test"
		print "ROWS={0}, COLS={1}, RS={2}, E={3}, Pins={4}".format(rows,cols,rs,e,pins)

		lcd = lcd_display_driver_winstar_ws0010_graphics_mode(rows,cols,rs,e,[d4, d5, d6, d7])

		lcd.clear()

		lcd.message("Winstar OLED\nPi Powered")
		time.sleep(3)

		lcd.clear()
		# fontV = fonts.bmfont.bmfont('Vintl01_10x16.fnt')
		# fpV = fontV.fontpkg
		#
		# width = g.msgwidth("12:35 pm", fpV, True)
		# maxw = 0
		# for i in width:
		# 	if i > maxw:
		# 		maxw = i
		# height = len(width)*16
		#
		# img = Image.new("1", (maxw+20, height+4), 0)
		# g.message(img,"12:35 pm",0,0, fpV, True)
		# nf = g.getframe(img,0,0,cols,rows)
		# lcd.update(nf)
		# time.sleep(10)
		#
		# font = fonts.bmfont.bmfont('latin1_5x8.fnt')
		# fp = font.fontpkg
		#
		# width = g.msgwidth("Prince and the Revolutions\nPurple Rain", fp, True)
		# maxw = 0
		# for i in width:
		# 	if i > maxw:
		# 		maxw = i
		# height = len(width)*8
		#
		# img = Image.new("1", (maxw+20, height+4), 0)
		# g.message(img,"Prince and the Revolutions\nPurple Rain",0,0, fp, True)
		# nf = g.getframe(img,0,0,cols,rows)
		# lcd.update(nf)
		# time.sleep(2)
		#
		# for i in range(0,(maxw+20)):
		# 	g.scrollbuffer(img,u'left')
		# 	nf = g.getframe(img,0,0,cols,rows)
		# 	lcd.update(nf)
		# time.sleep(2)
		#
		# for i in range(0,(height+4)*4):
		# 	g.scrollbuffer(img,u'up')
		# 	nf = g.getframe(img,0,0,cols,rows)
		# 	lcd.update(nf)
		# time.sleep(2)
		#
		# for i in range(0,(maxw+20)):
		# 	g.scrollbuffer(img,u'right')
		# 	nf = g.getframe(img,0,0,cols,rows)
		# 	lcd.update(nf)
		# time.sleep(2)
		#
		# for i in range(0,(height+4)*4):
		# 	g.scrollbuffer(img,u'down')
		# 	nf = g.getframe(img,0,0,cols,rows)
		# 	lcd.update(nf)
		# time.sleep(2)
		#
		# g.line(img,0,0,cols,rows,1)
		# fb = g.getframe(img,0,0,cols,rows)
		# lcd.update(fb)
		# j=0
		# for i in range(0,99):
		# 	j = i+1
		# 	g.line(img,i,0,cols-i,rows,0)
		# 	g.line(img,j,0,cols-j,rows,1)
		# 	fb = g.getframe(img,0,0,cols,rows)
		# 	lcd.update(fb)
		# g.line(img,j,0,cols-j,rows,0)
		# fb = g.getframe(img,0,0,cols,rows)
		# lcd.update(fb)
		#
		# g.line(img,cols,0,0,rows,1)
		# fb = g.getframe(img,0,0,cols,rows)
		# lcd.update(fb)
		# for i in range(0,16):
		# 	j = i+1
		# 	g.line(img,cols,i,0,rows-i,0)
		# 	g.line(img,cols,j,0,rows-j,1)
		# 	fb = g.getframe(img,0,0,cols,rows)
		# 	lcd.update(fb)
		# g.line(img,0,0,cols,rows,0)
		# fb = g.getframe(img,0,0,cols,rows)
		# lcd.update(fb)
		#
		# time.sleep(2)
		#
		# g.line(img,0,0,0,8) # vertical left line
		# g.line(img,0,0,100,0) # horizontal top line
		# g.line(img,99,0,99,8) # vertical right line
		# g.line(img,0,8,100,8) # horizontal bottom line
		# nf = g.getframe(img,0,0,cols,rows)
		# lcd.update(nf)
		# time.sleep(5)
		#
		# lcd.clear()
		# accent_min = u"àáâãäçèéëêìíî \nïòóôöøùúûüþÿ"
		# #for char in accent_min: print char, ord(char)
		# lcd.message(accent_min)
		# time.sleep(2)
		#
		# lcd.clear()
		#
		# accent_maj = u"ÀÁÂÆÇÈÉÊËÌÍÎÐ \nÑÒÓÔÕÙÚÛÜÝÞß"
		# #for char in accent_maj: print char, ord(char)
		# lcd.message(accent_maj)
		#
		# time.sleep(2)
		# lcd.clear()
		#
		# fontV = fonts.bmfont.bmfont('Vintl01_10x16.fnt')
		# fpV = fontV.fontpkg
		#
		# width = g.msgwidth("12:35 pm", fpV, True)
		# maxw = 0
		# for i in width:
		# 	if i > maxw:
		# 		maxw = i
		# height = len(width)*16
		#
		# img = Image.new("1", (maxw+20, height+4), 0)
		# g.message(img,"12:35 pm",0,0, fpV, True)
		# nf = g.getframe(img,0,0,cols,rows)
		# lcd.update(nf)
		# time.sleep(4)


		variabledict = { u'artist':u'Prince and the Revolutions', u'title':u'Million Dollar Club', u'volume':50 }
		variables = [ u'artist', u'title' ]

		f_HD44780 = fonts.bmfont.bmfont(u'latin1_5x8.fnt')
		fp_HD44780 = f_HD44780.fontpkg

		fp_Vint10x16 = fonts.bmfont.bmfont(u'Vintl01_10x16.fnt').fontpkg

		# artistw = gwidget(u'artist', variabledict)
		# artistw.text(u"{0}",[u'artist'], fp_Vint10x16, True, (0,0), 'left')

		artistw = display.gwidgetText(u'artist',"{0}",fp_HD44780, variabledict, [u'artist'], True)

		titlew = display.gwidget(u'title', variabledict)
		titlew.text(u"{0}",[u'title'], fp_HD44780, True)

		linew = display.gwidget(u'line1')
		linew.line( (99,0) )

		rectw = display.gwidget('rect1')
		rectw.rectangle( (99,15) )

		# progw = gwidget('prog1')
		# progw.progressbar( 50, (0,100), (80,6) )

		progw = display.gwidgetProgressBar(u'progbar1',u'volume', (0,100), (80,6), u'square', variabledict)

		gc1 = display.gcanvas('can1', (artistw.width,8) )
		gc2 = display.gcanvas('can2', (artistw.width,8) )

		gc1.add( artistw, (0,0) )
		gc2.add( titlew, (0,0) )
		# gc.add( linew, (0,22) )
		# gc.add( progw, (10,24) )

		gr1 = display.grenderer('testgr2',gc1)
		gr1.scroll('left')
		gr2 = display.grenderer('testgr2',gc2)
		gr2.scroll('up')

		firstpage = display.gpage('first', (100,32))
		firstpage.add(gr1, (0,0))
		firstpage.add(gr2, (0,8), (100,8))
		firstpage.add(linew, (0,22))
		firstpage.add(progw, (0,24))

		end = time.time() + 25
		flag = True
		i = 0
		variabledict['volume'] = i
		while end > time.time():
			i += 1
			if i > 100:
				i = 0
			variabledict['volume'] = i
			if end < time.time()+15 and flag:
				variabledict['title'] = u"Purple Rain"
				flag = False
			if firstpage.update():
				frame = g.getframe( firstpage.image, 0,0, firstpage.width, firstpage.height)
				lcd.update(frame)
				time.sleep(.03)

		secondpage = display.gpage('second', (100,32))
		secondpage.add(gr1, (0,0))
		secondpage.add(progw, (10,10))
		end = time.time() + 10
		while end > time.time():
			i += 1
			if i > 100:
				i = 0
			variabledict['volume'] = i
			if secondpage.update():
				frame = g.getframe( secondpage.image, 0,0, secondpage.width, secondpage.height)
				lcd.update(frame)
				time.sleep(.03)
		


		#
		# lcd.msgtest("\x00 Stop")
		# lcd.msgtest("\x01 Play")
		# lcd.msgtest("\x02 Pause")
		# lcd.msgtest("\x03 Ethernet")
		# lcd.msgtest("\x04 Wireless")
		# lcd.msgtest("\x05 Music")
		# lcd.msgtest("\x06 Power")
		# lcd.clear()
		#
		# lcd.switchcustomchars(fonts.size5x8.speaker.fontpkg)
		# lcd.msgtest("\x00\x01 SPEAKER\n\x02\x03")
		# lcd.switchcustomchars(fonts.size5x8.shuffle.fontpkg)
		# lcd.msgtest("\x00\x01 SHUFFLE\n\x02\x03")
		# lcd.switchcustomchars(fonts.size5x8.repeat_all.fontpkg)
		# lcd.msgtest("\x00\x01 REPEAT\n\x02\x03 ALL")
		# lcd.switchcustomchars(fonts.size5x8.repeat_once.fontpkg)
		# lcd.msgtest("\x00\x01 REPEAT\n\x02\x03 SINGLE")
		#
		# lcd.switchcustomchars(fonts.size5x8.bigchars.fontpkg)
		# numbers = fonts.size5x8.bigclock.numbers
		# bigchars = fonts.size5x8.bigchars.bigchars
		#
		# # Print large letters
		# for c in bigchars:
		# 	s = [ '', '' ]
		# 	for row in range(0,c['row']):
		# 		for col in range(0,c['col']):
		# 			s[row] += unichr(c['data'][row][col])
		# 	lcd.message(u"{0}  {1}\n{2}".format(s[0],c['char'],s[1]))
		# 	time.sleep(2)
		# 	lcd.clear()
		#
		#
		#
		# lcd.switchcustomchars(fonts.size5x8.volume.fontpkg)
		# for i in range (0,101):
		# 	volbar = volume_bar(i,
		# 		14,
		# 		fonts.size5x8.volume.e,
		# 		fonts.size5x8.volume.h,
		# 		fonts.size5x8.volume.f,
		# 		fonts.size5x8.volume.el,
		# 		fonts.size5x8.volume.er,
		# 		fonts.size5x8.volume.hr )
		# 	lcd.clear()
		# 	lcd.message("Volume {0}".format(i),0,0)
		# 	lcd.message("\x06 {0}".format(volbar),1,0)
		# 	time.sleep(.05)
		#
		# time.sleep(2)


	except KeyboardInterrupt:
		pass

	finally:
		lcd.clear()
		lcd.message("Goodbye!")
		time.sleep(2)
		lcd.clear()
		GPIO.cleanup()
		print "Winstar OLED Display Test Complete"
