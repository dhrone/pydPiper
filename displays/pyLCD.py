!/usr/bin/python
# coding: UTF-8

# Driver for WS0010 OLED driver/controller
# Written by: Ron Ritchey
# Uses RPLCD by dbrgn (github/dbrgn/RPLCD)

from __future__ import unicode_literals

import time, math, logging
import fonts
import graphics as g
import display
import moment
from PIL import Image

import RPLCD.gpio.CharLCD as lcdGPIO
import RPLCD.i2c.CharLCD as lcdI2C

class interface(object):
    def __init__(self, type='base'):
        self.type = type

class interfaceGpio(interface):
    def __init__(self, numbering_mode=GPIO.BCM, pin_rs = None, pin_rw = None, pin_e = None, pins_data = None, pin_backlight = None, backlight_mode = 'active_low', backlight_enabled = True):
        self.type = 'gpio'
        self.numbering_mode = numbering_mode
        self.pin_rs = pin_rs
        self.pin_rw = pin_rw
        self.pin_e = pin_e
        self.pins_data = pins_data
        self.pin_backlight = pin_backlight
        self.backlight_mode = backlight_mode
        self.backlight_enabled = backlight_enabled

class interfaceI2c(interface):
    def __init__(self, i2c_expander = 'PCF8574', address=None, expander_params = None, port=None, backlight_enabled=True):
        self.type = 'i2c'
        self.i2c_expander = i2c_expander
        self.address = address
        self.port = port
        self.backlight_enabled = backlight_enabled


class pyLCD(object):
    def __init__(self, interface=None, cols=16, rows=2, dotsize=8, charmap='A02'):
        if interface.type='gpio':
            self.lcd = lcdGPIO(numbering_mode=interface.numbering_mode, pin_rs = interface.pin_rs, pin_rw = interface.pin_rw, pin_e = interface.pin_e, pins_data = interface.pins_data, pin_backlight = interface.pin_backlight, backlight_mode = interface.backlight_mode, backlight_enabled = interface.backlight_enabled, cols = cols, rows = rows, dotsize = dotsize, charmap = charmap, auto_linebreaks=False)
        elif interface.type = 'i2c':
            self.lcd = lcdI2C(i2c_expander = interface.i2c_expander, address = interface.address, expander_params = interface.expander_params, port = interface.port, backlight_enabled = interface.backlight_enabled, cols = cols, rows = rows, dotsize = dotsize, charmap = charmap, auto_linebreaks = False)
        else:
            raise TypeError('Interface must be either gpio or i2c')

	def processevent(self, events, starttime, prepost, db, dbp):
		for evnt in events:
			t,var,val = evnt

			if time.time() - starttime >= t:
				if prepost in ['pre']:
					db[var] = val
				elif prepost in ['post']:
					dbp[var] = val

    def demo(self):

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

    def simpleDemo(self):
        self.lcd.clear()
        self.lcd.write_string('pyLCD')
        time.sleep(5)


class ws0010(pyLCD):
    def __init__(self, interface=None, cols=16, rows=2, dotsize=8, charmap='A02'):
        super(pyLCD, self).__init__(interface, cols, rows, dotsize, charmap)
		# Initialize the default font
		font = fonts.bmfont.bmfont('latin1_5x8_fixed.fnt')
		self.fp = font.fontpkg

        self.lcd.command(0b00011111) # Place display in graphics mode

    def write_string(self, value):
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
				self.lcd.write(byte)

	def setCursor(self, row, col):

		if row >= self.rows or col >= self.cols:
			raise IndexError

		# Convert from pixels to bytes
		row = int(math.ceil(row/8.0))

		self.lcd.command(self.lcd.c.LCD_SETDDRAMADDR | col)
		self.lcd.command(self.lcd.c.LCD_SETCGRAMADDR | row)


class hd44780(pyLCD):
