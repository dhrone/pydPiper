# Icons for large shuffle icon (5x8)
# Taken from https://github.com/RandyCupic/RuneAudioLCD/blob/master/display.py

# 2x2 grid to print icon
# pattern
# 0,1
# 2,3

upperleft	= [ 0b00000, 0b00000, 0b00000, 0b11100, 0b00010, 0b00010, 0b00010, 0b00001 ]
upperright	= [ 0b00000, 0b00000, 0b00010, 0b00111, 0b01010, 0b01000, 0b01000, 0b10000 ]
lowerleft	= [ 0b00001, 0b00010, 0b00010, 0b00010, 0b11100, 0b00000, 0b00000, 0b00000 ]
lowerright	= [ 0b10000, 0b01000, 0b01000, 0b01010, 0b00111, 0b00010, 0b00000, 0b00000 ]

fontpkg = [ upperleft, upperright, lowerleft, lowerright ]

ul = 0
ur = 1
ll = 2
lr = 3
