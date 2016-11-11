

# Derived from http://woodsgood.ca/projects/2015/02/17/big-font-lcd-characters/


#ful	= [ 0b00111, 0b01111, 0b11111, 0b11111, 0b11111, 0b11111, 0b11111, 0b11111 ] # Block with upper left rounded
#fll	= [ 0b11111, 0b11111, 0b11111, 0b11111, 0b11111, 0b11111, 0b01111, 0b00111 ] # Block with lower left rounded
#fur	= [ 0b11100, 0b11110, 0b11111, 0b11111, 0b11111, 0b11111, 0b11111, 0b11111 ] # Block with upper right rounded
#flr	= [ 0b11111, 0b11111, 0b11111, 0b11111, 0b11111, 0b11111, 0b11110, 0b11100 ] # Block with lower right rounded
#fub	= [ 0b11111, 0b11111, 0b00000, 0b00000, 0b00000, 0b00000, 0b00000, 0b00000 ] # Upper bar
#flb	= [ 0b00000, 0b00000, 0b00000, 0b00000, 0b00000, 0b00000, 0b11111, 0b11111 ] # Lower bar
#fuln= [ 0b11111, 0b00000, 0b00000, 0b00000, 0b00000, 0b00000, 0b11111, 0b11111 ] # Upper lower thin
#fulk =[ 0b11111, 0b11111, 0b00000, 0b00000, 0b00000, 0b00000, 0b11111, 0b11111 ] # Upper lower thick

fontpkg = [						# Custom character definitions
	  [ 0b01000, 0b01100, 0b01110, 0b01111, 0b01111, 0b01111, 0b01111, 0b01111 ], # play 0
	  [ 0b00000, 0b00000, 0b00000, 0b00000, 0b10000, 0b11000, 0b11100, 0b11110 ], # play 1
	  [ 0b01111, 0b01111, 0b01111, 0b01111, 0b01111, 0b01110, 0b01100, 0b01000 ], # play 2
	  [ 0b11110, 0b11100, 0b11000, 0b10000, 0b00000, 0b00000, 0b00000, 0b00000 ], # play 3
	  [ 0b00000, 0b00000, 0b00000, 0b01111, 0b01111, 0b01111, 0b01111, 0b01111 ], # stop 0
	  [ 0b00000, 0b00000, 0b00000, 0b11110, 0b11110, 0b11110, 0b11110, 0b11110 ], # stop 1
	  [ 0b01111, 0b01111, 0b01111, 0b01111, 0b01111, 0b00000, 0b00000, 0b00000 ], # stop 2
	  [ 0b11110, 0b11110, 0b11110, 0b11110, 0b11110, 0b00000, 0b00000, 0b00000 ]  # stop 3
]

fontpkg = [						# Custom character definitions
	  [ 0b00000, 0b00000, 0b00000, 0b10000, 0b11000, 0b11100, 0b11110, 0b11111 ], # Upper Play
	  [ 0x18, 0x1C, 0x1E, 0x1F, 0x1F, 0x1F, 0x1F, 0x1F ], # char 1
	  [ 0x1F, 0x1F, 0x1F, 0x1F, 0x1F, 0x0F, 0x07, 0x03 ], # char 2
	  [ 0x00, 0x00, 0x00, 0x00, 0x00, 0x1F, 0x1F, 0x1F ], # char 3
	  [ 0x1F, 0x1F, 0x1F, 0x1F, 0x1F, 0x1E, 0x1C, 0x18 ], # char 4
	  [ 0x1F, 0x1F, 0x1F, 0x00, 0x00, 0x00, 0x1F, 0x1F ], # char 5
	  [ 0b11111, 0b11110, 0b11100, 0b11000, 0b10000, 0b00000, 0b00000, 0b00000 ], # Lower Play
	  [ 0x03, 0x07, 0x0F, 0x1F, 0x1F, 0x1F, 0x1F, 0x1F ]  # char 7
]


def generate(choice='symbol'):
	# Input msg - the message to return. Raises IndexError if any chars in msg are not supported
	# Return - An array of unicode strings; on string per line

	if choice == 'symbol':
		return [u'\x00', u'\x06']


	msg = u'PLAY'
	retval = [ u'',u'' ] # This font has a height of two characters so initialize return value to return two lines

	# Check if every character is in the allowable
	for c in msg.upper():

		# Make sure we have a printable character
		if ord(c) < ord(' ') or ord(c) > ord('_'):
			# Check for special characters
			i = None
			for i in range( ord('_') - ord(' ')+1, len(bigchars)):
				if bigchars[i]['char'] == c:
					d = i
					break
			if i is None:
				raise IndexError
		else:
			# Character is normal.  Compute location in data bigchars array
			d = ord(c)-ord(' ')

		# Verify that correct character has been selected
		if bigchars[d]['char'] != c:
			logging.debug("bigplay expected {0} but found {1}".format(bigchars[d]['char'], c))
			raise ValueError

		rows = len(bigchars[d]['data'])
		cols = len(bigchars[d]['data'][0])

		for i in range(0, rows):
			for j in range(0, cols):
				retval[i] += unichr(bigchars[d]['data'][i][j])

	return retval


# BIG Play Character Set
# - Play symbol printed by sending...
# '\x00\x01'
# '\x02\x03'
