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

from __future__ import unicode_literals

import time, math,logging
import lcd_display_driver
import fonts
import graphics as g
from PIL import Image
import logging

try:
	import RPi.GPIO as GPIO
except:
	logging.debug("RPi.GPIO not installed")

class winstar_weg(lcd_display_driver.lcd_display_driver):

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



	def __init__(self, rows=16, cols=100, rs=7, e=8, datalines=[25, 24, 23, 27], enable_duration=0.1):
		# Default arguments are appropriate for Raspdac V3 only!!!

		self.pins_db = datalines
		self.pin_rs = rs
		self.pin_e = e

		self.rows = rows
		self.cols = cols

		self.enable_duration = enable_duration

		self.fb = [[]]

		self.FONTS_SUPPORTED = True

		# Initialize the default font
		font = fonts.bmfont.bmfont('latin1_5x8_fixed.fnt')
		self.fp = font.fontpkg

		# Set GPIO pins to handle communications to display
		GPIO.setmode(GPIO.BCM)
		GPIO.setwarnings(False)

		for pin in self.pins_db:
		   GPIO.setup(pin, GPIO.OUT, initial=GPIO.LOW)

		GPIO.setup(self.pin_e, GPIO.OUT, initial=GPIO.LOW)
		GPIO.setup(self.pin_rs, GPIO.OUT, initial=GPIO.LOW)
		GPIO.output(self.pin_e, False)

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
		super(winstar_weg, self).__init__(rows,cols, self.enable_duration)


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




	def loadcustomchars(self, char, fontdata):
		# Custom characters are unnecessary on a graphical display
		return


	def message(self, text, row=0, col=0, varwidth=True):
		''' Send string to LCD. Newline wraps to second line'''

		if row >= self.rows or col >= self.cols:
			raise IndexError

		textwidget = display.gwidgetText(text, self.fp, {}, [], varwidth )
		self.update(textwidget.image)

	def update(self, image):

		# Make image the same size as the display
		img = image.crop( (0,0,self.cols, self.rows))

		# Compute frame from image
		frame = self.getframe( img, 0,0, self.cols,self.rows )
		self.updateframe(frame)

	def updateframe(self, newbuf):

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
	import getopt,sys,os
	import graphics as g
	import fonts
	import display
	import moment

	def processevent(events, starttime, prepost, db, dbp):
		for evnt in events:
			t,var,val = evnt

			if time.time() - starttime >= t:
				if prepost in ['pre']:
					db[var] = val
				elif prepost in ['post']:
					dbp[var] = val


	logging.basicConfig(format=u'%(asctime)s:%(levelname)s:%(message)s', handlers=[logging.StreamHandler()], level=logging.DEBUG)

	try:
		opts, args = getopt.getopt(sys.argv[1:],"hr:c:",["row=","col=","rs=","e=","d4=","d5=","d6=", "d7="])
	except getopt.GetoptError:
		print 'winstar_weg.py -r <rows> -c <cols> --rs <rs> --e <e> --d4 <d4> --d5 <d5> --d6 <d6> --d7 <d7> --enable <duration in microseconds>'
		sys.exit(2)

	# Set defaults
	# These are for the wiring used by a Raspdac V3
	rows = 16
	cols = 80
	rs = 7
	e = 8
	d4 = 25
	d5 = 24
	d6 = 23
	d7 = 27
	enable = 0.1

	for opt, arg in opts:
		if opt == '-h':
			print 'winstar_weg.py -r <rows> -c <cols> --rs <rs> --e <e> --d4 <d4> --d5 <d5> --d6 <d6> --d7 <d7> --enable <duration in microseconds>'
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
		elif opt in ("--enable"):
			enable = int(arg)

	db = {
			'actPlayer':'mpd',
			'playlist_position':1,
			'playlist_length':5,
	 		'title':"Nicotine & Gravy",
			'artist':"Beck",
			'album':'Midnight Vultures',
			'elapsed':0,
			'length':400,
			'volume':50,
			'stream':'Not webradio',
			'utc': 	moment.utcnow(),
			'outside_temp_formatted':'46\xb0F',
			'outside_temp_max':72,
			'outside_temp_min':48,
			'outside_conditions':'Windy',
			'system_temp_formatted':'98\xb0C',
			'state':'stop',
			'system_tempc':81.0
		}

	dbp = {
			'actPlayer':'mpd',
			'playlist_position':1,
			'playlist_length':5,
	 		'title':"Nicotine & Gravy",
			'artist':"Beck",
			'album':'Midnight Vultures',
			'elapsed':0,
			'length':400,
			'volume':50,
			'stream':'Not webradio',
			'utc': 	moment.utcnow(),
			'outside_temp_formatted':'46\xb0F',
			'outside_temp_max':72,
			'outside_temp_min':48,
			'outside_conditions':'Windy',
			'system_temp_formatted':'98\xb0C',
			'state':'stop',
			'system_tempc':81.0
		}

	events = [
		(15, 'state', 'play'),
		(20, 'title', 'Mixed Bizness'),
		(30, 'volume', 80),
		(40, 'title', 'I Never Loved a Man (The Way I Love You)'),
		(40, 'artist', 'Aretha Franklin'),
		(40, 'album', 'The Queen Of Soul'),
		(70, 'state', 'stop'),
		(90, 'state', 'play'),
		(100, 'title', 'Do Right Woman, Do Right Man'),
		(120, 'volume', 100),
		(140, 'state', 'play' )
	]

	try:
		pins = [d4, d5, d6, d7]
		print "Winstar OLED Display Test"
		print "ROWS={0}, COLS={1}, RS={2}, E={3}, Pins={4} Delay Microseconds={5}".format(rows,cols,rs,e,pins,enable)

		lcd = winstar_weg(rows,cols,rs,e,[d4, d5, d6, d7],enable)
		lcd.clear()
		lcd.message("pydPiper\nStarting",0,0,True)
		time.sleep(2)
		lcd.clear()

		starttime = time.time()
		elapsed = int(time.time()-starttime)
		timepos = time.strftime(u"%-M:%S", time.gmtime(int(elapsed))) + "/" + time.strftime(u"%-M:%S", time.gmtime(int(254)))

		dc = display.display_controller((80,16))
		f_path = os.path.join(os.path.dirname(__file__), 'pages_test.py')
		dc.load(f_path, db,dbp )

		starttime=time.time()
		while True:
			elapsed = int(time.time()-starttime)
			db['elapsed']=elapsed
			db['utc'] = moment.utcnow()
			processevent(events, starttime, 'pre', db, dbp)
			img = dc.next()
			processevent(events, starttime, 'post', db, dbp)
			lcd.update(img)
			time.sleep(.1)


	except KeyboardInterrupt:
		pass

	finally:
		lcd.clear()
		lcd.message("Goodbye!", 0, 0, True)
		time.sleep(2)
		lcd.clear()
		GPIO.cleanup()
		print "Winstar OLED Display Test Complete"
