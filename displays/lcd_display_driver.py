# lcd_display_driver - base class for lcd or oled 16x2 or 20x4 displays

import abc

class lcd_display_driver:
	__metaclass__ = abc.ABCMeta

	# Need to decide whether custom fonts live in the driver or the display.
	# THinking right now, they should live in the base driver class.

	# Taken from https://github.com/RandyCupic/RuneAudioLCD/blob/master/display.py

	# 1x1 characters.  Can be displayed directly
	# Icons for display (5x8)
	display_icons = [
			[ 0b00000, 0b11111, 0b11111, 0b11111, 0b11111, 0b11111, 0b11111, 0b00000 ], # Stop
			[ 0b00000, 0b01000, 0b01100, 0b01110, 0b01110, 0b01100, 0b01000, 0b00000 ], # Play
			[ 0b00000, 0b01010, 0b01010, 0b01010, 0b01010, 0b01010, 0b01010, 0b00000 ], # Pause
			[ 0b00000, 0b11111, 0b11011, 0b10001, 0b10001, 0b10001, 0b11111, 0b00000 ], # Ethernet
			[ 0b00000, 0b00000, 0b00001, 0b00001, 0b00101, 0b00101, 0b10101, 0b00000 ], # Wireless
			[ 0b00000, 0b01111, 0b01001, 0b01001, 0b01001, 0b11011, 0b11011, 0b00000 ], # Music note
			[ 0b00000, 0b00100, 0b00100, 0b10101, 0b10101, 0b10001, 0b01110, 0b00000 ]  # Power
	]

	# 2x2 characters.  Must be displayed in the following pattern
	# "01"
	# "23"
	speaker_icon = [
			[ 0b00000, 0b00000, 0b00000, 0b00000, 0b11111, 0b10001, 0b10001, 0b10001 ],
			[ 0b00001, 0b00011, 0b00101, 0b01001, 0b10001, 0b00001, 0b00001, 0b00001 ],
			[ 0b10001, 0b10001, 0b10001, 0b11111, 0b00000, 0b00000, 0b00000, 0b00000 ],
			[ 0b00001, 0b00001, 0b00001, 0b10001, 0b01001, 0b00101, 0b00011, 0b00001 ]
	]

	shuffle_icon = [
			[ 0b00000, 0b00000, 0b00000, 0b11100, 0b00010, 0b00010, 0b00010, 0b00001 ],
			[ 0b00000, 0b00000, 0b00010, 0b00111, 0b01010, 0b01000, 0b01000, 0b10000 ],
			[ 0b00001, 0b00010, 0b00010, 0b00010, 0b11100, 0b00000, 0b00000, 0b00000 ],
			[ 0b10000, 0b01000, 0b01000, 0b01010, 0b00111, 0b00010, 0b00000, 0b00000 ]
	]

	repeat_all_icon = [
			[ 0b00000, 0b00000, 0b00000, 0b00011, 0b00100, 0b01000, 0b10000, 0b10000 ],
			[ 0b00000, 0b00000, 0b00000, 0b11000, 0b00101, 0b00011, 0b00111, 0b00000 ],
			[ 0b10000, 0b10000, 0b01000, 0b00100, 0b00011, 0b00000, 0b00000, 0b00000 ],
			[ 0b00000, 0b00000, 0b00010, 0b00100, 0b11000, 0b00000, 0b00000, 0b00000 ]
	]

	repeat_single_icon = [
			[ 0b00000, 0b00000, 0b00000, 0b00011, 0b00100, 0b01000, 0b00000, 0b00000 ],
			[ 0b00000, 0b00000, 0b00000, 0b11000, 0b00101, 0b00011, 0b00111, 0b00000 ],
			[ 0b00000, 0b11100, 0b11000, 0b10100, 0b00011, 0b00000, 0b00000, 0b00000 ],
			[ 0b00000, 0b00000, 0b00010, 0b00100, 0b11000, 0b00000, 0b00000, 0b00000 ]
	]

	FONT_ICONS = 0
	FONT_SPEAKER = 1
	FONT_SHUFFLE = 2
	FONT_REPEATALL = 3
	FONT_REPEATSINGLE = 4
	FONTSETS = [ display_icons, speaker_icon, shuffle_icon, repeat_all_icon, repeat_single_icon ]

	FONTS_SUPPORTED = True

	def __init__(self, rows, columns):
		self.rows = rows
		self.columns = columns
		# Write custom fonts if the display supports them
		# Fonts are currenty 5x8
		try:
			self.loadcustomchars(0, self.display_icons)
		except RuntimeError:
			# Custom fonts not supported
			self.FONTS_SUPPORTED = False
			pass



	def switchcustomchars(self, index):
		if self.FONTS_SUPPORTED:
			try:
				self.loadcustomchars(0, self.FONTSETS[index])
			except RuntimeError:
				self.FONTS_SUPPORTED = False
				pass

	@abc.abstractmethod
	def message(self, message, row, col):
		# Sends a message for the dispay to show on row at col
		# Messages must be UTF-8 encoded
		# Must throw IndexError if row or col is out of range for the display
		return

	@abc.abstractmethod
	def clear(self):
		# clears the display
		return

	@abc.abstractmethod
	def displayon(self):
		# turns the display on
		return

	@abc.abstractmethod
	def displayoff(self):
		# turns the display off
		return

	@abc.abstractmethod
	def cursoron(self):
		# turns the cursor on
		return

	@abc.abstractmethod
	def cursoroff(self):
		# turns the cursor off
		return

	@abc.abstractmethod
	def blinkon(self):
		# turns blnking on
		return

	@abc.abstractmethod
	def blinkoff(self):
		# turns blinking off
		return

	def command(self, cmd):
		# Sends a command to the display
		# Must support the following commands...
			# CLEAR - Clears the display
			# DISPLAYON - Turns display on
			# DISPLAYOFF - Turns display off
			# CURSORON - Turns the underine cursor on
			# CURSOROFF - Turns the underline cursor off
			# BLINKON - Turns blinking on
			# BLINKOFF - Turns blinking off

		if cmd == "CLEAR":
			self.clear()
		elif cmd == "DISPLAYON":
			self.displayon()
		elif cmd == "DISPLAYOFF":
			self.displayoff()
		elif cmd == "CURSORON":
			self.cursoron()
		elif cmd == "CURSOROFF":
			self.cursoroff()
		elif cmd == "BLINKON":
			self.blinkon()
		elif cmd == "BLINKOFF":
			self.blinkoff()
		else:
			raise RuntimeError('Command {0} not supported'.format(cmd))

	@abc.abstractmethod
	def cleanup(self):
		# If there are any steps needed to restore system state on exit, this is the place to do it.
		return

	@abc.abstractmethod
	def loadcustomchars(self, char, fontdata):
		# Write an array of custom characters starting at position char within
		# the CGRAM region.
		# Char should be an integer between 0 and 255
		# fontdata should be an array of fonts which is are arrays of font data
		# Must throw RuntimeError('Command loadcustomchars not supported')
		# if display doesn't allow custom characters
		return
