#!/usr/bin/python
# coding: UTF-8

# Driver for SSD1306 OLED display on the RPi using I2C interface
# Written by: Ron Ritchey
#
# Enabled by Richard Hull's excellent luma.oled project (https://github.com/rm-hull/luma.oled)
#


from __future__ import unicode_literals

import time, math,logging
import lcd_display_driver
import fonts
import graphics as g
from PIL import Image
import logging

from luma.core.interface.serial import i2c
from luma.core.render import canvas
from luma.oled.device import sh1106
from luma.oled.device import ssd1306
from luma.oled.device import ssd1322
from luma.oled.device import ssd1325
from luma.oled.device import ssd1331
from luma.core.error import DeviceNotFoundError


try:
	import RPi.GPIO as GPIO
except:
	logging.debug("RPi.GPIO not installed")

class luma_i2c():

	def __init__(self, rows=64, cols=128, i2c_address=0x3d, i2c_port=1, devicetype=u'ssd1306'):

		self.i2c_address = i2c_address
		self.i2c_port = i2c_port

		self.rows = rows
		self.cols = cols

		self.fb = [[]]

		# Initialize the default font
		font = fonts.bmfont.bmfont('latin1_5x8_fixed.fnt')
		self.fp = font.fontpkg

		serial = i2c(port=i2c_port, address=i2c_address)

		if devicetype.lower() == u'ssd1306':
			self.device = ssd1306(serial)
		elif devicetype.lower() == u'sh1106':
			self.device = sh1106(serial)
		elif devicetype.lower() == u'ssd1322':
			self.device = ssd1322(serial)
		elif devicetype.lower() == u'ssd1325':
			self.device = ssd1325(serial)
		elif devicetype.lower() == u'ssd1331':
			self.device = ssd1331(serial)
		else:
			raise ValueError('{0} not a recognized luma device type'.format(devicetype))

	def clear(self):
		with canvas(self.device) as draw:
			draw.rectangle(self.device.bounding_box, outline="black", fill="black")

	def message(self, text, row=0, col=0, varwidth=True):
		''' Send string to LCD. Newline wraps to second line'''

		if row >= self.rows or col >= self.cols:
			raise IndexError

		textwidget = display.gwidgetText(text, self.fp, {}, [], varwidth )
		self.update(textwidget.image)

	def update(self, image):
		retry = 5

		# Make image the same size as the display
		img = image.crop( (0,0,self.cols, self.rows))

		while retry:
			# send to display
			try:
				self.device.display(img)
				break
			except IOError:
				retry -= 1


	def msgtest(self, text, wait=1.5):
		self.clear()
		self.message(text)
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
		opts, args = getopt.getopt(sys.argv[1:],"hr:c:",["row=","col=","i2c_address=","i2c_port=","devicetype="])
	except getopt.GetoptError:
		print 'luma_i2c.py -r <rows> -c <cols> --devicetype <devicetype> --i2c_address <addr> --i2c_port <port>'
		sys.exit(2)

	# Set defaults
	rows = 64
	cols = 128
	i2c_address = 0x3d
	i2c_port = 1
	devicetype = u'ssd1306'

	for opt, arg in opts:
		if opt == '-h':
			print 'luma_i2c.py -r <rows> -c <cols> --devicetype <devicetype> --i2c_address <addr> --i2c_port <port>\nDevice types can be sh1106, ssd1306, ssd1322, ssd1325, and ssd1331'
			sys.exit()
		elif opt in ("-r", "--rows"):
			rows = int(arg)
		elif opt in ("-c", "--cols"):
			cols = int(arg)
		elif opt in ("--devicetype"):
			devicetype  = arg
		elif opt in ("--i2c_address"):
			i2c_address  = int(arg)
		elif opt in ("--i2c_port"):
			i2c_port  = int(arg)

	db = {
			'actPlayer':'mpd',
			'playlist_position':1,
			'playlist_length':5,
	 		'title':"Nicotine & Gravy",
			'artist':"Beck",
			'album':'Midnight Vultures',
			'tracktype':'MP3 Stereo 24 bit 44.1 Khz',
			'bitdepth':'16 bits',
			'samplerate':'44.1 kHz',
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
			'tracktype':'MP3 Stereo 24 bit 44.1 Khz',
			'bitdepth':'16 bits',
			'samplerate':'44.1 kHz',
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

	DISPLAY_OK = False
	try:
		print "LUMA OLED Display Test"
		print "ROWS={0}, COLS={1}, DEVICETYPE={4}, I2C_ADDRESS={2}, I2C_PORT={3}".format(rows,cols,i2c_address,i2c_port,devicetype)

		lcd = luma_i2c(rows,cols,i2c_address,i2c_port,devicetype)

		DISPLAY_OK = True

		lcd.clear()
		lcd.message("OLED Display\nStarting",0,0,True)
		time.sleep(2)
		lcd.clear()

		starttime = time.time()
		elapsed = int(time.time()-starttime)
		timepos = time.strftime(u"%-M:%S", time.gmtime(int(elapsed))) + "/" + time.strftime(u"%-M:%S", time.gmtime(int(254)))

		dc = display.display_controller((cols,rows))
		f_path = os.path.join(os.path.dirname(__file__), '../pages_ssd1306.py')
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
			time.sleep(.001)


	except KeyboardInterrupt:
		pass

	finally:
		if DISPLAY_OK:
			lcd.clear()
			lcd.message("Goodbye!", 0, 0, True)
			time.sleep(2)
			lcd.clear()
		print "Luma OLED Display Test Complete"
