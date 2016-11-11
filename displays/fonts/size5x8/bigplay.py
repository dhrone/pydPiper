

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

bigchars = [
	{'data': [[32], [32]], 'col': 1, 'row': 2, 'char':' '}, 						#
	{'data': [[8], [6]], 'col': 1, 'row': 2, 'char':'!'}, 							# !
	{'data': [[4, 4], [32, 32]], 'col': 2, 'row': 2, 'char':'"'}, 					# "
	{'data': [[3, 8, 3, 8], [3, 0, 8, 0]], 'col': 4, 'row': 2, 'char':'#'}, 		# #
	{'data': [[7, 8, 5], [6, 8, 4]], 'col': 3, 'row': 2, 'char':'$'}, 				# $
	{'data': [[0, 32, 3, 0], [3, 0, 32, 3]], 'col': 4, 'row': 2, 'char':'%'}, 		# %
	{'data': [[7, 5, 1, 32], [2, 6, 1, 3]], 'col': 4, 'row': 2, 'char':'&'}, 		# &
	{'data': [[4], [32]], 'col': 1, 'row': 2, 'char':"'"}, 							# '
	{'data': [[7, 0], [2, 3]], 'col': 2, 'row': 2, 'char':'('}, 					# (
	{'data': [[0, 1], [3, 4]], 'col': 2, 'row': 2, 'char':')'}, 					# )
	{'data': [[0, 3, 3, 0], [3, 0, 0, 3]], 'col': 4, 'row': 2, 'char':'*'}, 		# *
	{'data': [[3, 8, 3], [0, 8, 0]], 'col': 3, 'row': 2, 'char':'+'}, 				# +
	{'data': [[32], [4]], 'col': 1, 'row': 2, 'char': ','}, 						# ,
	{'data': [[3, 3, 3], [32, 32, 32]], 'col': 3, 'row': 2, 'char': '-'}, 			# -
	{'data': [[32], [3]], 'col': 1, 'row': 2, 'char': '.'}, 						# .
	{'data': [[32, 32, 3, 0], [3, 0, 32, 32]], 'col': 4, 'row': 2, 'char': '/'},	# /
	{'data': [[7, 0, 1], [2, 3, 4]], 'col': 3, 'row': 2, 'char': '0'}, 				# 0
	{'data': [[0, 1, 32], [3, 8, 3]], 'col': 3, 'row': 2, 'char': '1'}, 			# 1
	{'data': [[5, 5, 1], [8, 6, 6]], 'col': 3, 'row': 2, 'char': '2'}, 				# 2
	{'data': [[0, 5, 1], [3, 6, 4]], 'col': 3, 'row': 2, 'char': '3'}, 				# 3
	{'data': [[2, 3, 8], [32, 32, 8]], 'col': 3, 'row': 2, 'char': '4'}, 			# 4
	{'data': [[8, 5, 5], [6, 6, 4]], 'col': 3, 'row': 2, 'char': '5'}, 				# 5
	{'data': [[7, 5, 5], [2, 6, 4]], 'col': 3, 'row': 2, 'char': '6'}, 				# 6
	{'data': [[0, 0, 1], [32, 7, 32]], 'col': 3, 'row': 2, 'char': '7'}, 			# 7
	{'data': [[7, 5, 1], [2, 6, 4]], 'col': 3, 'row': 2, 'char': '8'}, 				# 8
	{'data': [[7, 5, 1], [6, 6, 4]], 'col': 3, 'row': 2, 'char': '9'}, 				# 9
	{'data': [[9], [9]], 'col': 1, 'row': 2, 'char': ':'}, 							# :
	{'data': [[3], [4]], 'col': 1, 'row': 2, 'char': ';'}, 							# ;
	{'data': [[32, 3, 0], [0, 0, 3]], 'col': 3, 'row': 2, 'char': '<'}, 			# <
	{'data': [[3, 3, 3], [0, 0, 0]], 'col': 3, 'row': 2, 'char': '='}, 				# =
	{'data': [[0, 3, 32], [3, 0, 0]], 'col': 3, 'row': 2, 'char': '>'}, 			# >
	{'data': [[0, 5, 1], [32, 6, 32]], 'col': 3, 'row': 2, 'char': '?'}, 			# ?
	{'data': [[7, 5, 1], [2, 3, 3]], 'col': 3, 'row': 2, 'char': '@'}, 				# @
	{'data': [[7, 5, 1], [8, 32, 8]], 'col': 3, 'row': 2, 'char': 'A'}, 			# A
	{'data': [[8, 5, 4], [8, 6, 1]], 'col': 3, 'row': 2, 'char': 'B'}, 				# B
	{'data': [[7, 0, 0], [2, 3, 3]], 'col': 3, 'row': 2, 'char': 'C'}, 				# C
	{'data': [[8, 0, 1], [8, 3, 4]], 'col': 3, 'row': 2, 'char': 'D'}, 				# D
	{'data': [[8, 5, 5], [8, 6, 6]], 'col': 3, 'row': 2, 'char': 'E'}, 				# E
	{'data': [[8, 5, 5], [8, 32, 32]], 'col': 3, 'row': 2, 'char': 'F'}, 			# F
	{'data': [[7, 0, 0], [2, 3, 1]], 'col': 3, 'row': 2, 'char': 'G'}, 				# G
	{'data': [[8, 3, 8], [8, 32, 8]], 'col': 3, 'row': 2, 'char': 'H'}, 			# H
	{'data': [[0, 8, 0], [3, 8, 3]], 'col': 3, 'row': 2, 'char': 'I'}, 				# I
	{'data': [[32, 32, 8], [3, 3, 4]], 'col': 3, 'row': 2, 'char': 'J'}, 			# J
	{'data': [[8, 3, 4], [8, 32, 1]], 'col': 3, 'row': 2, 'char': 'K'}, 			# K
	{'data': [[8, 32, 32], [8, 3, 3]], 'col': 3, 'row': 2, 'char': 'L'}, 			# L
	{'data': [[7, 2, 4, 1], [8, 32, 32, 8]], 'col': 4, 'row': 2, 'char': 'M'}, 		# M
	{'data': [[8, 1, 32, 8], [8, 32, 2, 8]], 'col': 4, 'row': 2, 'char': 'N'}, 		# N
	{'data': [[7, 0, 1], [2, 3, 4]], 'col': 3, 'row': 2, 'char': 'O'}, 				# O
	{'data': [[7, 5, 1], [8, 32, 32]], 'col': 3, 'row': 2, 'char': 'P'}, 			# P
	{'data': [[7, 0, 1, 32], [2, 3, 8, 3]], 'col': 4, 'row': 2, 'char': 'Q'}, 		# Q
	{'data': [[8, 5, 1], [8, 32, 1]], 'col': 3, 'row': 2, 'char': 'R'}, 			# R
	{'data': [[7, 5, 5], [6, 6, 4]], 'col': 3, 'row': 2, 'char': 'S'}, 				# S
	{'data': [[0, 8, 0], [32, 8, 32]], 'col': 3, 'row': 2, 'char': 'T'}, 			# T
	{'data': [[8, 32, 8], [2, 3, 4]], 'col': 3, 'row': 2, 'char': 'U'}, 			# U
	{'data': [[2, 32, 32, 4], [32, 1, 7, 32]], 'col': 4, 'row': 2, 'char': 'V'}, 	# V
	{'data': [[8, 32, 32, 8], [2, 7, 1, 4]], 'col': 4, 'row': 2, 'char': 'W'}, 		# W
	{'data': [[2, 3, 4], [7, 32, 1]], 'col': 3, 'row': 2, 'char': 'X'}, 			# X
	{'data': [[2, 3, 4], [32, 8, 32]], 'col': 3, 'row': 2, 'char': 'Y'}, 			# Y
	{'data': [[0, 5, 4], [7, 6, 3]], 'col': 3, 'row': 2, 'char': 'Z'}, 				# Z
	{'data': [[8, 0], [8, 3]], 'col': 2, 'row': 2, 'char': '['}, 					# [
	{'data': [[0, 3, 32, 32], [32, 32, 0, 3]], 'col': 4, 'row': 2, 'char': '\\'}, 	# \
	{'data': [[0, 8], [3, 8]], 'col': 2, 'row': 2, 'char': ']'}, 					# ]
	{'data': [[7, 1], [32, 32]], 'col': 2, 'row': 2, 'char': '^'}, 					# ^
	{'data': [[32, 32, 32], [3, 3, 3]], 'col': 3, 'row': 2, 'char': '_'}, 			# _

	# Special characters
	{'data': [[111], [32]], 'col': 1, 'row': 2, 'char': u'\xb0'}, 			# degree symbol
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
