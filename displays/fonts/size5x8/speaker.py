# Icons for large speaker (5x8)
# Taken from https://github.com/RandyCupic/RuneAudioLCD/blob/master/display.py

# 2x2 grid to print speaker
# pattern
# 0,1
# 2,3

upperleft	= [ 0b00000, 0b00000, 0b00000, 0b00000, 0b11111, 0b10001, 0b10001, 0b10001 ]
upperright	= [ 0b00001, 0b00011, 0b00101, 0b01001, 0b10001, 0b00001, 0b00001, 0b00001 ]
lowerleft	= [ 0b10001, 0b10001, 0b10001, 0b11111, 0b00000, 0b00000, 0b00000, 0b00000 ]
lowerright	= [ 0b00001, 0b00001, 0b00001, 0b10001, 0b01001, 0b00101, 0b00011, 0b00001 ]
empty		= [ 0b00000, 0b11111, 0b00000, 0b00000, 0b00000, 0b00000, 0b11111, 0b00000 ] # Volume empty
half		= [ 0b00000, 0b11111, 0b11100, 0b11100, 0b11100, 0b11100, 0b11111, 0b00000 ] # Volume half
full		= [ 0b00000, 0b11111, 0b11111, 0b11111, 0b11111, 0b11111, 0b11111, 0b00000 ] # Volume full


fontpkg = [ upperleft, upperright, lowerleft, lowerright, empty, half, full ]

ul = 0
ur = 1
ll = 2
lr = 3
e = 4
h = 5
f = 6
er = 4
hr = 5
el = 4
