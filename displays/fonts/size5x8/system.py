# Icons for large clock icon (5x8)
# Written by Dhrone

# 2x2 grid to print icon
# pattern
# 0,1
# 2,3


clock_upperleft	= [ 0b00000, 0b00000, 0b00000, 0b00011, 0b00101, 0b01001, 0b10001, 0b10001 ]
clock_upperright= [ 0b00000, 0b00000, 0b00000, 0b10000, 0b01000, 0b00100, 0b00010, 0b11110 ]
clock_lowerleft	= [ 0b10000, 0b01000, 0b00100, 0b00011, 0b00000, 0b00000, 0b00000, 0b00000 ]
clock_lowerright= [ 0b00010, 0b00100, 0b01000, 0b10000, 0b00000, 0b00000, 0b00000, 0b00000 ]

temp_left	= [ 0b00011, 0b00010, 0b00010, 0b00010, 0b00010, 0b00100, 0b00100, 0b00011 ]
temp_right	= [ 0b10110, 0b10000, 0b10110, 0b10000, 0b10110, 0b01000, 0b01000, 0b10000 ]

disk_left	= [ 0b00111, 0b00100, 0b00101, 0b00100, 0b00101, 0b00101, 0b00100, 0b00111 ]
disk_right	= [ 0b11110, 0b00010, 0b11010, 0b00010, 0b11010, 0b11010, 0b00010, 0b11110 ]

fontpkg = [ clock_upperleft, clock_upperright, clock_lowerleft, clock_lowerright, temp_left, temp_right, disk_left, disk_right ]

cul = 0
cur = 1
cll = 2
clr = 3

tl = 4
tr = 5

dl = 6
dr = 7
