# lcd_display_driver - base class for lcd or oled 16x2 or 20x4 displays

import abc, fonts

class lcd_display_driver:
	__metaclass__ = abc.ABCMeta

	# Need to decide whether custom fonts live in the driver or the display.
	# THinking right now, they should live in the base driver class.

	FONTS_SUPPORTED = True

	def __init__(self, rows, columns):
		self.rows = rows
		self.columns = columns
		# Write custom fonts if the display supports them
		# Fonts are currenty 5x8
#		try:
#			self.loadcustomchars(0, fonts.size5x8.player.fontpkg)
#		except RuntimeError:
#			# Custom fonts not supported
#			self.FONTS_SUPPORTED = False
#			pass



	def switchcustomchars(self, fontpkg):
		if self.FONTS_SUPPORTED:
			try:
				self.loadcustomchars(0, fontpkg)
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

		if cmd == u"CLEAR":
			self.clear()
		elif cmd == u"DISPLAYON":
			self.displayon()
		elif cmd == u"DISPLAYOFF":
			self.displayoff()
		elif cmd == u"CURSORON":
			self.cursoron()
		elif cmd == u"CURSOROFF":
			self.cursoroff()
		elif cmd == u"BLINKON":
			self.blinkon()
		elif cmd == u"BLINKOFF":
			self.blinkoff()
		else:
			raise RuntimeError(u'Command {0} not supported'.format(cmd))

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
