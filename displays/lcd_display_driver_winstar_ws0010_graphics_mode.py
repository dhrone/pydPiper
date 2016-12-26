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

		GPIO.output(self.pin_rs, char_mode)
		if bits & 0x80:
			GPIO.output(self.pins_db[::-1][0], True)
		else:
			GPIO.output(self.pins_db[::-1][0], False)
		if bits & 0x40:
			GPIO.output(self.pins_db[::-1][1], True)
		else:
			GPIO.output(self.pins_db[::-1][1], False)
		if bits & 0x20:
			GPIO.output(self.pins_db[::-1][2], True)
		else:
			GPIO.output(self.pins_db[::-1][2], False)
		if bits & 0x10:
			GPIO.output(self.pins_db[::-1][3], True)
		else:
			GPIO.output(self.pins_db[::-1][3], False)
		self.pulseEnable()
		if bits & 0x08:
			GPIO.output(self.pins_db[::-1][0], True)
		else:
			GPIO.output(self.pins_db[::-1][0], False)
		if bits & 0x04:
			GPIO.output(self.pins_db[::-1][1], True)
		else:
			GPIO.output(self.pins_db[::-1][1], False)
		if bits & 0x02:
			GPIO.output(self.pins_db[::-1][2], True)
		else:
			GPIO.output(self.pins_db[::-1][2], False)
		if bits & 0x01:
			GPIO.output(self.pins_db[::-1][3], True)
		else:
			GPIO.output(self.pins_db[::-1][3], False)
		self.pulseEnable()


	def write4bits_old(self, bits, char_mode=False):

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

#		GPIO.output(self.pin_e, False)
#		self.delayMicroseconds(.1) # 1 microsecond pause - enable pulse must be > 450ns
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

		# width = g.msgwidth(text, self.fp, varwidth)
		# maxw = 0
		# for i in width:
		# 	if i > maxw:
		# 		maxw = i
		# height = len(width)*8
		#
		# img = Image.new("1", (maxw, height), 0)
		img = g.message(text,0,0, self.fp, varwidth)
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
		lcd.message("pydPiper\nStarting",0,0,True)
		time.sleep(10)
		lcd.clear()


		import graphics as g
		import fonts
		import display

		starttime = time.time()
		elapsed = int(time.time()-starttime)
		timepos = time.strftime(u"%-M:%S", time.gmtime(int(elapsed))) + "/" + time.strftime(u"%-M:%S", time.gmtime(int(254)))

		db_old = {
		 		'title':"15 glasses left (240 oz)",
				'artist':"Rye IPA",
				'album':'7.2 ABV',
				'playlist_display':'01/10',
				'elapsed_formatted':timepos,
				'time_formatted':'12:34p',
				'outside_temp_formatted':'72\xb0F',
	#			'outside_temp_formatted':'72F',
				'outside_conditions':'Windy',
				'volume':88,
				'system_temp_formatted':'98\xb0C',
				'streaming':False,
				'state':'play',
				'random':False,
				'single':False,
				'repeat':False,
				'system_tempc':81.0
			}

		db = {
		 		'remaining':"26 glasses left (423 oz)",
				'name':"Bruce Springsteen",
				'abv':'2:04/4:32',
				'weight': 423,
				'description':'Born to Run',
				'time_formatted':'12:34p',
				'outside_temp_formatted':'46\xb0F',
	#			'outside_temp_formatted':'72F',
				'outside_conditions':'Windy',
				'system_temp_formatted':'98\xb0C',
				'state':'play',
				'system_tempc':81.0
			}

		dbp = {
		 		'remaining':"26 glasses left (423 oz)",
				'name':"Bruce Springsteen -- Born to Run",
				'abv':'7.2 ABV',
				'weight': 423,
				'description':'Malty and bitter with an IBU of 72',
				'time_formatted':'12:34p',
				'outside_temp_formatted':'46\xb0F',
	#			'outside_temp_formatted':'72F',
				'outside_conditions':'Windy',
				'system_temp_formatted':'98\xb0C',
				'state':'play',
				'system_tempc':81.0
			}


		dbp_old = {
		 		'title':"15 glasses left (240 oz)",
				'artist':"Rye IPA",
				'album':'7.2 ABV',
				'playlist_display':'01/10',
				'elapsed_formatted':'1:32/4:03',
				'time_formatted':'12:34p',
				'outside_temp_formatted':'72\xb0F',
	#			'outside_temp_formatted':'72F',
				'outside_conditions':'Windy',
				'volume':88,
				'system_temp_formatted':'98\xb0C',
				'streaming':False,
				'state':'play',
				'random':False,
				'single':False,
				'repeat':False,
				'system_tempc':81.0
			}

		dc = display.display_controller()
		dc.load('../pages.py', dbp,dbp_old, (80,16))
		# titlew = dc.widgets['title']

		# formatstring, fontpkg, variabledict={ }, variables =[], varwidth = False, size=(0,0), just=u'left'

		# fontpkg = dc.pages.FONTS['small']['fontpkg']
		# # fontpkg = fonts.bmfont.bmfont(u'latin1_5x8.fnt').fontpkg
		# elapsedw = display.gwidgetText("{0}", fontpkg, db, [u'elapsed_formatted'], False, (60,8), 'right')
		# artistw = display.gwidgetText("{0}", fontpkg, db, [u'album'], False )
		# playlist_displayw = display.gwidgetText("{0}", fontpkg, db, [u'playlist_display'], False )
		# canvasw = display.gwidgetCanvas( (100,16) )
		# canvasw.add(artistw, (0,0) )
		# canvasw.add(playlist_displayw, (0,8))
		# canvasw.add(elapsedw, (40,8))
		#
		# frame = g.getframe( canvasw.image, 0,0,canvasw.image.width,canvasw.image.height)
		# # g.show( frame, canvasw.image.width, int(math.ceil(canvasw.image.height/8.0)) )
		#

		starttime = time.time()
		elapsed = int(time.time()-starttime)
		timepos = time.strftime(u"%-M:%S", time.gmtime(int(elapsed))) + "/" + time.strftime(u"%-M:%S", time.gmtime(int(254)))

		import moment
		# time.sleep(2)

		starttime=time.time()
		while True:
			elapsed = int(time.time()-starttime)
			timepos = time.strftime(u"%-M:%S", time.gmtime(int(elapsed))) + "/" + time.strftime(u"%-M:%S", time.gmtime(int(254)))
			current_time = moment.utcnow().timezone('US/Eastern').strftime(u"%H:%M:%S").strip().decode()
			db['elapsed_formatted'] = timepos
			db['time_formatted'] = current_time
			img = dc.next()
			img = img.crop( (0,0,100,16) )
			frame = g.getframe( img, 0,0, 100,16 )
			# g.show( frame, 100, int(math.ceil(16/8.0)))
			lcd.update(frame)
#			if db['volume'] == 40:
#				dbp['volume']= 40
#			if db['state'] == 'stop':
#				dbp['state'] = 'stop'
			if starttime + 60 < time.time():
				db['state'] = 'stop'

#			if starttime + 10 < time.time():
#				db['volume'] = 40



	#
	# 	variabledict = { u'artist':u'Prince and the Revolutions', u'title':u'Million Dollar Club', u'volume':50 }
	# 	variables = [ u'artist', u'title' ]
	#
	# 	fp_HD44780 = fonts.bmfont.bmfont(u'latin1_5x8.fnt').fontpkg
	# 	fp_Vint10x16 = fonts.bmfont.bmfont(u'Vintl01_10x16.fnt').fontpkg
	#
	# 	# artistw = gwidget(u'artist', variabledict)
	# 	# artistw.text(u"{0}",[u'artist'], fp_Vint10x16, True, (0,0), 'left')
	#
	# 	artistw = display.gwidgetText("{0}",fp_HD44780, variabledict, [u'artist'], True)
	# 	titlew = display.gwidgetText("{0}", fp_HD44780, variabledict, [u'title'], True)
	# 	linew = display.gwidgetLine( (99,0) )
	# 	rectw = display.gwidgetRectangle( (99,15) )
	# 	progw = display.gwidgetProgressBar(u'volume', (0,100), (80,6), u'square', variabledict)
	#
	# 	artistcanvas = display.gwidgetCanvas( (artistw.width,14) )
	# 	titlecanvas = display.gwidgetCanvas( (artistw.width,8) )
	#
	# 	artistcanvas = display.gwidgetScroll(artistcanvas.add( artistw, (0,0) ),u'left',1,20,u'onloop',2,100)
	# 	titlecanvas = display.gwidgetScroll(titlecanvas.add( titlew, (0,0) ),u'up',1,4,u'onloop',2,8)
	#
	# 	page = display.gwidgetCanvas( (100,32) )
	# 	page.add(artistcanvas, (0,0))
	# 	page.add(titlecanvas, (0,8), (100,8))
	# 	page.add(display.gwidgetText("Percent complete",fp_HD44780), (4,17))
	# 	page.add(linew, (0,16))
	# 	page.add(progw, (4,26))
	#
	# 	end = time.time() + 20
	# 	flag = True
	# 	i = 0
	# 	variabledict['volume'] = i
	# 	while end > time.time():
	# 		i += 1
	# 		if i > 100:
	# 			i = 0
	# 		variabledict['volume'] = i
	# 		if end < time.time()+10 and flag:
	# 			variabledict['title'] = u"Purple Rain"
	# 			flag = False
	# 		if page.update():
	# 			frame = g.getframe( page.image, 0,0, page.width, page.height)
	# 			lcd.update(frame)
	# 			time.sleep(.03)
	#
	# #-------------
	#
	# 	variabledict['title'] = "When Dove's Cry"
	# 	progw = display.gwidgetProgressBar(u'volume', (0,100), (80,4), u'square', variabledict)
	# 	page = display.gwidgetCanvas( (100,32) )
	# 	page.add( artistcanvas, (0,0) )
	# 	page.add( titlecanvas, (0,18) )
	# 	page.add( linew, (0,26) )
	# 	page.add( progw, (0,28) )
	# 	page = display.gwidgetPopup(page, 14)
	#
	# 	end = time.time() + 25
	# 	flag = True
	# 	i = 0
	# 	variabledict['volume'] = i
	# 	while end > time.time():
	# 		i += 1
	# 		if i > 100:
	# 			i = 0
	# 		variabledict['volume'] = i
	# 		if end < time.time()+15 and flag:
	# 			variabledict['title'] = u"Purple Rain"
	# 			flag = False
	# 		if page.update():
	# 			frame = g.getframe( page.image, 0,0, page.width, page.height)
	# 			lcd.update(frame)
	# 		time.sleep(.03)

	except KeyboardInterrupt:
		pass

	finally:
		lcd.clear()
		lcd.message("Goodbye!", 0, 0, True)
		time.sleep(2)
		lcd.clear()
		GPIO.cleanup()
		print "Winstar OLED Display Test Complete"
