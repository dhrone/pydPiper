#!/usr/bin/python
# coding: UTF-8

# Driver for testing pydPiper display
# Uses the curses system to emulate a display
# Written by: Ron Ritchey

import time, math, logging, curses, locale
import lcd_display_driver
from PIL import Image

class lcd_curses(lcd_display_driver.lcd_display_driver):


	def __init__(self, rows=16, cols=100 ):

		self.FONTS_SUPPORTED = False

		self.rows = rows
		self.cols = cols

		self.stdscr = curses.initscr()
		self.curx = 0
		self.cury = 0

		if (curses.LINES < rows+1) or (curses.COLS < cols+1):
			raise RuntimeError(u"Screen too small.  Increase size to at least ({0}, {1})".format(rows+1, cols+1))

		# Set up parent class.  Note.  This must occur after display has been
		# initialized as the parent class may attempt to load custom fonts
		super(lcd_curses, self).__init__(rows,cols,1)

		locale.setlocale(locale.LC_ALL, '')

	def clear(self):
		self.stdscr.clear()
		self.stdscr.refresh()
		self.curx = 0
		self.cury = 0


	def setCursor(self, row, col):
		self.curx = col
		self.cury = row

	def write4bits(self, bits, char_mode=False):

		self.stdscr.addch(self.cury, self.curx, curses.ACS_BLOCK if bits & 0x01 else ' ')
		self.setCursor(self.cury+1, self.curx)
		self.stdscr.addch(self.cury, self.curx, curses.ACS_BLOCK if bits & 0x02 else ' ')
		self.setCursor(self.cury+1, self.curx)
		self.stdscr.addch(self.cury, self.curx, curses.ACS_BLOCK if bits & 0x04 else ' ')
		self.setCursor(self.cury+1, self.curx)
		self.stdscr.addch(self.cury, self.curx, curses.ACS_BLOCK if bits & 0x08 else ' ')
		self.setCursor(self.cury+1, self.curx)
		self.stdscr.addch(self.cury, self.curx, curses.ACS_BLOCK if bits & 0x10 else ' ')
		self.setCursor(self.cury+1, self.curx)
		self.stdscr.addch(self.cury, self.curx, curses.ACS_BLOCK if bits & 0x20 else ' ')
		self.setCursor(self.cury+1, self.curx)
		self.stdscr.addch(self.cury, self.curx, curses.ACS_BLOCK if bits & 0x40 else ' ')
		self.setCursor(self.cury+1, self.curx)
		self.stdscr.addch(self.cury, self.curx, curses.ACS_BLOCK if bits & 0x80 else ' ')
		self.setCursor(self.cury+1, self.curx)

	def loadcustomchars(self, char, fontdata):
		# Load custom characters
		RuntimeError('Command loadcustomchars not supported')

	def cleanup(self):
		curses.endwin()

	def message(self, text, row=0, col=0):
		''' Send string to LCD. Newline wraps to second line'''

		self.setCursor(row, col)
		self.stdscr.addstr(self.cury, self.curx, text.encode('utf-8'))
		self.stdscr.refresh()

	def update(self, image):

		# Make image the same size as the display
		img = image.crop( (0,0,self.cols, self.rows))

		# Compute frame from image
		frame = self.getframe( img, 0,0, self.cols,self.rows )
		self.updateframe(frame)

	def updateframe(self, newbuf):

		self.stdscr.clear()
		rows = int(math.ceil(self.rows/8.0))
		for j in range(0, rows):
#			self.setCursor(j*8,0)
			for i in range(0, self.cols):
				self.setCursor(j*8,i)
				try:
					byte = newbuf[j][i]
				except IndexError:
					byte = 0
				self.write4bits(byte, True)

		self.stdscr.refresh()

	def msgtest(self, text, wait=1.5):
		self.clear()
		lcd.message(text)
		time.sleep(wait)

if __name__ == '__main__':

  try:

	print "Curses Display Test"

	lcd = lcd_curses(2,16)
	lcd.msgtest("Curses\nPi Powered",2)
	lcd.msgtest("This is a driver\nused for testing",2)

	accent_min = u"àáâãäçèéëêìíî \nïòóôöøùúûüþÿ"
	#for char in accent_min: print char, ord(char)
	lcd.msgtest(accent_min,2)
	lcd.clear()

  except KeyboardInterrupt:
	pass

  finally:

	lcd.clear()
	lcd.message("Goodbye!")
	time.sleep(2)
	lcd.clear()
	curses.endwin()
	print "Curses Display Test Complete"
