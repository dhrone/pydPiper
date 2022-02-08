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

import time, math,logging
import fonts
from PIL import Image

import graphics
try:
	import smbus
except:
	logging.debug("smbus not installed")


class hd44780_mcp23008():

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

	LCD_BACKLIGHT  = 0x08  # On
	#LCD_BACKLIGHT = 0x00  # Off


	character_translation = [
		  0,  1,  2,  3,  4,  5,  6,  7,255, -1, -1, -1, -1, -1, -1, -1,	#0
		 -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1,	#16
		 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47,	#32
		 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63,	#48
		 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79,	#64
		 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 97, 93, 94, 95,	#80
		 96, 97, 98, 99,100,101,102,103,104,105,106,107,108,109,110,111,	#96
		112,113,114,115,116,117,118,119,120,121,122, -1,124,125,126,127,	#112
		 -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1,	#128
		 -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1,	#144


		 32,234,236,237, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1,	#160
		223, -1, -1, -1, -1,228, -1,176, -1, -1, -1, -1, -1, -1, -1, -1,	#176
		 -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1,	#192
		 -1, 78, -1, -1, -1, -1, -1,235, -1, -1, -1, -1, -1, -1, -1,226,	#208
		 -1, -1, -1, -1,225, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1,	#224
		 -1,238, -1, -1, -1, -1,239,253, -1, -1, -1, -1,245, -1, -1, -1 ]	#240



	def __init__(self, rows=16, cols=80, i2c_addr=0x27, i2c_bus=1, enable_duration=1):
		# Default arguments are appropriate for Raspdac V3 only!!!

		self.i2c_addr = i2c_addr

		self.rows = rows
		self.cols = cols
		self.rows_char = rows/8
		self.cols_char = cols/5
		self.curposition = (0,0)

		self.enable_duration = enable_duration

		self.bus = smbus.SMBus(i2c_bus)

		# image buffer to hold current display contents.  Used to prevent unnecessary refreshes
		self.curimage = Image.new("1", (self.cols, self.rows))

		self.FONTS_SUPPORTED = True

		# Initialize the default font
		self.font = fonts.bmfont.bmfont('latin1_5x8_fixed.fnt')
		self.fp = self.font.fontpkg

		# Sets the values to offset into DDRAM for different display lines
		self.row_offsets = [ 0x00, 0x40, 0x14, 0x54 ]

		# there is a good writeup on the HD44780 at Wikipedia
		# https://en.wikipedia.org/wiki/Hitachi_HD44780_LCD_controller


		self.write4bits(0x33,False)
		self.write4bits(0x32,False)
		# Initialize display control, function, and mode registers.
		displaycontrol = self.LCD_DISPLAYON | self.LCD_CURSOROFF | self.LCD_BLINKOFF
		displayfunction = self.LCD_4BITMODE | self.LCD_1LINE | self.LCD_2LINE | self.LCD_5x8DOTS
		displaymode = self.LCD_ENTRYLEFT | self.LCD_ENTRYSHIFTDECREMENT
		# Write registers.
		self.delayMicroseconds(1000)
		self.write4bits(self.LCD_DISPLAYCONTROL | displaycontrol, False)
		self.delayMicroseconds(2000)
		self.write4bits(self.LCD_FUNCTIONSET | displayfunction, False)
		self.write4bits(self.LCD_ENTRYMODESET | displaymode, False)  # set the entry mode
		self.clear()

		# Set up parent class.
		#super(hd44780_i2c, self).__init__(rows,cols)

	def delayMicroseconds(self, microseconds):
		seconds = microseconds / 1000000.0 # divide microseconds by 1 million for seconds
		time.sleep(seconds)

	def write4bits(self, bits, mode=False):

		# High bits
		self.lcd_toggle_enable(bits>>4, mode)

		# Low bits
		self.lcd_toggle_enable(bits&0x0F, mode)


	def lcd_toggle_enable(self, bits, mode=False):
		# Pin mapping for MCP23008
        #    7  | 6  | 5  | 4  | 3  | 2 | 1  | 0
        #    BL | D7 | D6 | D5 | D4 | E | RS | -

		# Mask out the high order bits, shift data left to fit it into the data pins, set the backlight on, and set RS if writing data (vs instruction)
		v = (bits & 0x0F) << 3 | 0x80 | (0x02 if mode else 0)

		# Write data to display
		self.bus.write_byte(self.i2c_addr, v)
		self.delayMicroseconds(self.enable_duration)

		# Pulse enable
		self.bus.write_byte(self.i2c_addr, v | 0x04)
		self.delayMicroseconds(self.enable_duration)

		# End enable pulse
		self.bus.write_byte(self.i2c_addr, v)
		self.delayMicroseconds(self.enable_duration)


	def createcustom(self, image):

		if self.currentcustom == 0:
			# initialize custom font memory
			self.customfontlookup = {}

		# The image should only be 5x8 but if larger, crop it
		img = image.crop( (0,0,5,8) )

		imgdata = list(img.convert("1").getdata())

		# Check to see if a custom character has already been created for this image
		if tuple(imgdata) in self.customfontlookup:
			return self.customfontlookup[tuple(imgdata)]

		# If there is space, create a custom character using the image provided
		if self.currentcustom > 7:
			return ord('?')

		# Set pointer to position char in CGRAM
		self.write4bits(self.LCD_SETCGRAMADDR+(self.currentcustom*8))

		# Increment currentcustom to point to the next custom char position
		self.currentcustom += 1


		# For each line of data from the image
		for j in range(8):
			line = 0
			# Computer a five bit value
			for i in range(5):
				if imgdata[j*5+i]:
					line |= 1<<4-i
			# And then send it to the custom character memory region for the current customer character
			self.write4bits(line, True)

		# Save custom character in lookup table
		self.customfontlookup[tuple(imgdata)] = self.currentcustom - 1

		# Return the custom character position.  We have to subtract one as we incremented it earlier in the function
		return self.currentcustom - 1

	def compare(self, image, position):
		imgdata = tuple(list(image.getdata()))
		disdata = tuple(list(self.curimage.crop((position[0], position[1], position[0]+5, position[1]+8)).getdata()))
		if imgdata == disdata:
			return True
		return False

	def update(self, image):

		# Make image the same size as the display
		img = image.crop( (0,0,self.cols, self.rows))

		# Make image black and white
		img = img.convert("1")


		# For each character sized cell from image, try to determine what character it is
		# by comparing it against the font reverse lookup dictionary
		# If you find a matching entry, output the cooresponding unicode value
		# else output a '?' symbol
		self.currentcustom = 0
		for j in range(self.rows_char):
			for i in range(self.cols_char):
				imgtest = img.crop( (i*5, j*8, (i+1)*5, (j+1)*8) )

				# Check to see if the img is the same as was previously updated
				# If it is, skip to the next character
#				if self.compare(imgtest, (i*5, j*5)):
#					continue
				imgdata = tuple(list(imgtest.getdata()))
				char = self.font.imglookup[imgdata] if imgdata in self.font.imglookup else self.createcustom(imgtest)
				#print "Using char {0}".format(char)
				#frame = graphics.getframe(imgtest,0,0,5,8)
				#graphics.show(frame,5,1)

				# Check to see if there is a character in the font table that matches.  If not, try to create a custom character for it.
				char = self.character_translation[char] if self.character_translation[char] >= 0 else self.createcustom(imgtest)

				# Write the resulting character value to the display
				self.setCursor(i,j)
				self.write4bits(char, True)

		# Save the current image to curimage
		self.curimage.paste(image.crop((0,0,self.cols,self.rows)),(0,0))
		self.setCursor(0,0)

		displaycontrol = self.LCD_DISPLAYON | self.LCD_CURSOROFF | self.LCD_BLINKOFF
		self.write4bits(self.LCD_DISPLAYCONTROL | displaycontrol, False)


	def clear(self):

		# Set cursor back to 0,0
		self.setCursor(0,0)
		self.curposition = (0,0)

		self.curimage = Image.new("1",(self.cols,self.rows))

		# And then clear the screen
		self.write4bits(self.LCD_CLEARDISPLAY) # command to clear display
		self.delayMicroseconds(2000) # 2000 microsecond sleep, clearing the display takes a long time

	def setCursor(self, col_char, row_char):

		if row_char > self.rows_char or col_char > self.cols_char:
			raise IndexError

		if (row_char > self.rows_char):
			row = self.rows_char - 1 # we count rows starting w/0

		self.write4bits(self.LCD_SETDDRAMADDR | (col_char + self.row_offsets[row_char]))

		self.curposition = (col_char, row_char)


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

	def message(self, text, row_char=0, col_char=0):
		''' Send string to LCD. Newline wraps to second line'''

		if row_char > self.rows_char or col_char > self.cols_char:
			raise IndexError

		self.setCursor(col_char, row_char)

		for char in text:
			if char == '\n':
				row_char = self.curposition[1]+1 if row_char < self.rows_char else self.curposition[1]
				self.setCursor(0, row_char)
			else:
				# Translate incoming character into correct value for European charset
				# and then send it to display.  Use space if character is out of range.
				c = ord(char)
				if c > 255: c = 32
				ct = self.character_translation[c]
				if ct > 0:
					self.write4bits(self.character_translation[c], True)


	def msgtest(self, text, wait=1.5):
		self.clear()
		lcd.message(text)
		time.sleep(wait)

if __name__ == '__main__':

	import getopt,sys, os
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
			'outside_temp_formatted':u'46\xb0F',
			'outside_temp_max':72,
			'outside_temp_min':48,
			'outside_conditions':'Windy',
			'system_temp_formatted':u'98\xb0C',
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
			'outside_temp_formatted':u'46\xb0F',
			'outside_temp_max':72,
			'outside_temp_min':48,
			'outside_conditions':'Windy',
			'system_temp_formatted':u'98\xb0C',
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
		(40, 'playlist_position', 2),
		(70, 'state', 'stop'),
		(90, 'state', 'play'),
		(100, 'title', 'Do Right Woman, Do Right Man'),
		(100, 'playlist_position', 3),
		(120, 'volume', 100),
		(140, 'state', 'play' )
	]




	try:
		opts, args = getopt.getopt(sys.argv[1:],"hr:c:",["row=","col=","addr=","bus="])
	except getopt.GetoptError:
		print 'hd44780_mcp23008.py -r <rows> -c <cols> --addr <i2c addr> --bus <i2c bus> --enable <duration in microseconds>'
		sys.exit(2)

	# Set defaults
	# These are for the wiring used by a Raspdac V3
	rows = 32
	cols = 100
	i2c_addr = 0x27
	i2c_bus = 1
	enable = 1

	for opt, arg in opts:
		if opt == '-h':
			print 'hd44780_mcp23008.py -r <rows> -c <cols> --addr <i2c addr> --bus <i2c bus> --enable <duration in microseconds>'
			sys.exit()
		elif opt in ("-r", "--rows"):
			rows = int(arg)
		elif opt in ("-c", "--cols"):
			cols = int(arg)
		elif opt in ("--addr"):
			i2c_addr  = int(arg)
		elif opt in ("--bus"):
			i2c_bus  = int(arg)
		elif opt in ("--enable"):
			enable = int(arg)

	try:

		print "HD44780 with MCP23008 I2C Backpack Display Test"
		print "ROWS={0}, COLS={1}, I2C Addr={2}, I2C Bus={3} enable duraction={4}".format(rows,cols,i2c_addr,i2c_bus,enable)

		lcd = hd44780_mcp23008(rows,cols,i2c_addr, i2c_bus, enable)
		lcd.clear()

		lcd.message("HD44780 MCP23008 LCD\nPi Powered")
		time.sleep(4)

		starttime = time.time()
		elapsed = int(time.time()-starttime)
		timepos = time.strftime(u"%-M:%S", time.gmtime(int(elapsed))) + "/" + time.strftime(u"%-M:%S", time.gmtime(int(254)))

		pathtotest = 'pages_test_lcd_20x4.py' if rows == 32 else 'pages_test_lcd_16x2.py'
		dc = display.display_controller((cols,rows))
		f_path = os.path.join(os.path.dirname(__file__), 'pages_test_lcd_20x4.py')
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

		lcd.clear()

		time.sleep(2)


	except KeyboardInterrupt:
		pass

	finally:
		try:
			lcd.clear()
			lcd.message("Goodbye!")
			time.sleep(2)
			lcd.clear()
		except:
			pass
		time.sleep(.5)
		print u"LCD Display Test Complete"
