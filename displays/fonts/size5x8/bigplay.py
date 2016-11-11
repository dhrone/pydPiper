

# Derived from http://woodsgood.ca/projects/2015/02/17/big-font-lcd-characters/



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
