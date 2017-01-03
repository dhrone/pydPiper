#!/usr/bin/python
# coding: UTF-8

# Driver for testing pydPiper display
# Uses the curses system to emulate a display
# Written by: Ron Ritchey

import time, curses
import lcd_display_driver


class lcd_curses(lcd_display_driver.lcd_display_driver):


	def __init__(self, rows=2, cols=16 ):

		self.FONTS_SUPPORTED = False

		self.rows = rows
		self.cols = cols

		self.stdscr = curses.initscr()
		self.curx = 0
		self.cury = 0

		# Set up parent class.  Note.  This must occur after display has been
		# initialized as the parent class may attempt to load custom fonts
		super(lcd_curses, self).__init__(rows,cols)


	def clear(self):
		self.stdscr.clear()
		self.stdscr.refresh()
		self.curx = 0
		self.cury = 0


	def setCursor(self, row, col):
		self.curx = col
		self.cury = row


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
