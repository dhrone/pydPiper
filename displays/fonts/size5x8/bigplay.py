

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
	  [ 0b00000, 0b00000, 0b00000, 0b01111, 0b01111, 0b01111, 0b01111, 0b01111 ], # stop 2
	  [ 0b00000, 0b00000, 0b00000, 0b11110, 0b11110, 0b11110, 0b11110, 0b11110 ]  # stop 3
]

def generate(playstop=0):
	if playstop == 0:
		return [u'\x00\x01', u'\x02\x03']
	elif playstop == 1:
		return [u'\x04\x05', u'\x06\x07']

# BIG Play Character Set
# - Play symbol printed by sending...
# '\x00\x01'
# '\x02\x03'
