#!/usr/bin/python
# coding: UTF-8

# Base class to provide graphics primitives
# Written by: Ron Ritchey
import sys, copy, math


def set(buffer,x,y,val):
	# Sets pixel at x,y to value
	# x is the distance in pixels from the top of the buffer (not the number of bytes)

	# Figure out what byte we are in
	bx = int(x/8) # Byte we are in
	bo = x % 8	# Offset within the byte

	# Add byte at coordinates if needed
	try:
		newval = buffer[(bx,y)]
	except KeyError:
		buffer[(bx,y)] = 0
		newval = 0

	newval = buffer[(bx,y)]
	if val:
		newval |= 1 << bo # Set bit
	else:
		newval = ~(1<<bo)&0xFFFF&newval # Clear bit
	buffer[(bx,y)] = newval

def get(buffer,x,y):
	# Get current value of pixel at coordinates x,y

	bx = int(x/8)
	bo = x % 8

	try:
		vb = buffer[(bx,y)]
	except KeyError:
		return 0

	if vb & (1<<bo):
		return 1
	else:
		return 0

def getbuffer(buffer,x,y,height,width):
	# Return buffer that is referenced from coordinates starting x,y and is the size of height,width
	# x,y - coordinates of the upper left portion of the display
	# height,width - size of the display buffer to Return

	retval = { }

	for i in range (0, width):
		for j in range(0, height):
			val = get(buffer,x+j, y+i)
			set(retval,j,i,val)

	return retval

def getframe(buffer,x,y,height,width):
	# Returns an array of arrays
	# [
	#   [ ], # Array of bytes for line 0
	#   [ ]  # Array of bytes for line 1
	#				 ...
	#   [ ]  # Array of bytes for line n
	# ]

	buf = getbuffer(buffer,x,y,height,width)
	retval = []
	for i in range(0, int(math.ceil(height/8.0))):
		retline = []
		for j in range(0,width):
			try:
				retline.append(buf[(i,j)])
			except KeyError:
				# If key is not found, those pixels are off
				retline.append(0)
		retval.append(retline)

	return retval


def combinebuffer(buffer, addbuf, x, y, height, width):

	for i in range (0, width):
		for j in range (0, height):
			val = get(addbuf,j,i)
			set(buffer,j+x,i+y,val)

def scrollbuffer(buffer, height, width, direction=u'left', distance=1):
	direction = direction.lower()

	# Save region to be overwritten
	# Move body
	# Restore region to cleared space

	if direction == u'left':
		region = getbuffer(buffer,0,0,height, distance)
		body = getbuffer(buffer,0,distance, height, width-distance)
		combinebuffer(buffer, body,0,0,height,width-distance)
		combinebuffer(buffer, region, 0,width-distance, height, distance)
	elif direction == u'right':
		region = getbuffer(buffer,0,width-distance,height, distance)
		body = getbuffer(buffer,0,0, height, width-distance)
		combinebuffer(buffer, body,0,distance,height,width-distance)
		combinebuffer(buffer, region, 0,0, height, distance)
	elif direction == u'up':
		region = getbuffer(buffer,0,0,distance, width)
		body = getbuffer(buffer,distance,0, height-distance, width)
		combinebuffer(buffer, body,0,0,height-distance,width)
		combinebuffer(buffer, region, height-distance, 0, distance, width)
	elif direction == u'down':
		region = getbuffer(buffer,height-distance,0,distance, width)
		body = getbuffer(buffer,0,0, height-distance, width)
		combinebuffer(buffer, body,distance,0,height-distance,width)
		combinebuffer(buffer, region, 0, 0, distance, width)


def show(buffer,x,y,height,width):
		buf = getbuffer(buffer,x,y,height,width)

		for i in range(0,height):
			for j in range(0,width):
				if get(buf,i,j):
					sys.stdout.write('*')
					sys.stdout.flush()
				else:
					sys.stdout.write(' ')
					sys.stdout.flush()
			print ''

def clear(x,y,height,width,buffer):
		for i in range(0,height):
			for j in range(0,width):
				set(buffer,i+x,j+y,0)

def msgwidth(msg, fontpkg, varwidth=False):
	(fx, fy) = fontpkg['size']
	retval = [ ]
	clp = 0 # Current line pixel used count

	for c in msg:
		if c == u'\n':
			retval.append(clp-1)
			clp = 0
			continue

		bytearray = copy.copy(fontpkg[ord(c)])
		if varwidth and ord(c) != 0x20: # if variable width requested and char is not a space
			try:
				# Trim left
				while bytearray[0] == 0:
					del bytearray[0]
				# Trim right
				for i in range(len(bytearray)-1,0,-1):
					if bytearray[i] == 0:
						del bytearray[i]
			except IndexError:
				# bytearray for this character was empty
				pass

		for val in bytearray:
			clp += 1
		# Add pixel wide gap between characters
		clp += 1
	retval.append(clp-1)

	return retval

# From https://en.wikipedia.org/wiki/Bresenham's_line_algorithm
def line(buf,x0, y0, x1, y1):
	deltax = x1 - x0
	deltay = y1 - y0
	error = -1.0
	try:
		deltaerr = abs(float(deltay) / float(deltax))	# Assume deltax != 0 (line is not vertical),
		# note that this division needs to be done in a way that preserves the fractional part
	except:
		deltaerr = 0

	if deltax:
		y = y0
		for x in range(x0,x1):
			set(buf,y,x,1)
			error = error + deltaerr
			if error >= 0.0:
				y = y + 1
				error = error - 1.0
	else:
		# line is vertical
		for y in range(y0,y1):
			set(buf,y,x0,1)

def message(buffer,msg,x,y,fontpkg,varwidth = False, just='left', height=0, width=0):

	(fx,fy) = fontpkg['size']
	cy = y

	for c in msg:

		# If newline, move x to next line (based upon font height) and return y to beginning of line
		if c == u'\n':
			x = x + fx
			cy = y
			continue

		try:
			bytearray = copy.copy(fontpkg[ord(c)])
		except KeyError:
			# Requested character does not exist in font.  Replace with '?'
			bytearray = copy.copy(fontpkg[ord('?')])

		if varwidth and ord(c) != 0x20: # if variable width requested and char is not a space
			try:
				# Trim left
				while bytearray[0] == 0:
					del bytearray[0]
				# Trim right
				for i in range(len(bytearray)-1,0,-1):
					if bytearray[i] == 0:
						del bytearray[i]
			except IndexError:
				# bytearray for this character was empty
				pass

		# Place character bitmap into frame buffer
		for val in bytearray:
			cx = x
			for i in range(0,fx):
				# Test bit
				tb = 1
				if val & (1<<i):
					tv = 1
				else:
					tv = 0
				set(buffer,cx,cy,tv)
				cx += 1
			cy += 1

		# Add pixel wide gap between characters
		cx = x
		for i in range(0,fx):
			set(buffer,cx,cy,0)
			cx += 1
		cy += 1
