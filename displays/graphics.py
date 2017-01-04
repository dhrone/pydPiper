#!/usr/bin/python
# coding: UTF-8

# Base class to provide graphics primitives
# Written by: Ron Ritchey
import sys, copy, math
from PIL import Image
from PIL import ImageDraw


# def set(image,x,y,val):
# 	# Sets pixel at x,y to value
# 	# x is the distance in pixels from the top of the buffer (not the number of bytes)
#
# 	# Figure out what byte we are in
# 	bx = int(x/8) # Byte we are in
# 	bo = x % 8	# Offset within the byte
#
# 	# Add byte at coordinates if needed
# 	try:
# 		newval = buffer[(bx,y)]
# 	except KeyError:
# 		buffer[(bx,y)] = 0
# 		newval = 0
#
# 	newval = buffer[(bx,y)]
# 	if val:
# 		newval |= 1 << bo # Set bit
# 	else:
# 		newval = ~(1<<bo)&0xFFFF&newval # Clear bit
# 	buffer[(bx,y)] = newval

# def get(buffer,x,y):
# 	# Get current value of pixel at coordinates x,y
#
# 	bx = int(x/8)
# 	bo = x % 8
#
# 	try:
# 		vb = buffer[(bx,y)]
# 	except KeyError:
# 		return 0
#
# 	if vb & (1<<bo):
# 		return 1
# 	else:
# 		return 0

# def getbuffer(buffer,x,y,height,width):
# 	# Return buffer that is referenced from coordinates starting x,y and is the size of height,width
# 	# x,y - coordinates of the upper left portion of the display
# 	# height,width - size of the display buffer to Return
#
# 	retval = { }
#
# 	for i in range (0, width):
# 		for j in range(0, height):
# 			val = get(buffer,x+j, y+i)
# 			set(retval,j,i,val)
#
# 	return retval
def invertbits(byte):
	# Assumes 8 bit value
	if byte < 0 | byte > 255:
		raise ValueError
	retval = 0
	for i in range(0,8):
		if byte & 1:
			retval |= 1
		byte = byte >> 1
		retval = retval << 1
	retval = retval >> 1
	return retval

def getframe(image,x,y,width,height):
	# Returns an array of arrays
	# [
	#   [ ], # Array of bytes for line 0
	#   [ ]  # Array of bytes for line 1
	#				 ...
	#   [ ]  # Array of bytes for line n
	# ]

	# Select portion of image to work with
	img = image.convert("1")
	#img.crop( (x,y, width, height) )


	width, height = img.size
	bheight = int(math.ceil(height / 8.0))
	imgdata = list(img.getdata())


	retval = []	# The variable to hold the return value (an array of byte arrays)
	retline = [0]*width # Line to hold the first byte of image data
	bh = 0 # Used to determine when we've consumed a byte worth of the line

	# Perform a horizontal iteration of the image data
	for i in range(0,height):
		for j in range(0,width):
			# if the value is true then mask a bit into the byte within retline
			if imgdata[(i*width)+j]:
				try:
					retline[j] |= 1<<bh
				except IndexError as e:
					# WTF
					print "width = {0}".format(width)
					raise e
		# If we've written a full byte, start a new retline
		bh += 1
		if bh == 8: # We reached a byte boundary
			bh = 0
			retval.append(retline)
			retline = [0]*width
	if bh > 0:
		retval.append(retline)

	return retval

def scrollbuffer(image, direction=u'left', distance=1):
	direction = direction.lower()

	# Save region to be overwritten
	# Move body
	# Restore region to cleared space

	width, height = image.size

	if direction == u'left':
		region = image.crop((0,0, distance, height))
		body = image.crop((distance,0, width, height))
		image.paste(body, (0,0))
		image.paste(region, ((width-distance),0) )
	elif direction == u'right':
		region = image.crop((width-distance,0, width, height))
		body = image.crop((0,0, width-distance, height))
		image.paste(body, (distance,0) )
		image.paste(region, (0,0) )
	elif direction == u'up':
		region = image.crop((0,0, width, distance))
		body = image.crop((0,distance, width, height))
		image.paste(body, (0,0) )
		image.paste(region, (0,height-distance) )
	elif direction == u'down':
		region = image.crop((0,height-distance, width, height))
		body = image.crop((0,0, width, height-distance))
		image.paste(body, (0,distance) )
		image.paste(region, (0,0) )


def show(bytebuffer,width, height):

	sys.stdout.write('  |')
	i = 0
	for j in range(0,width):
		if j%5 == 0:
			sys.stdout.write('{0}'.format(j/5))
		else:
			if j/5 < 10:
				sys.stdout.write(' '.format(i))
		i += 1
		if i == 10:
			i = 0
	sys.stdout.write('|')
	sys.stdout.flush()
	print ''
	sys.stdout.write('  |')
	i = 0
	for j in range(0,width):
		sys.stdout.write('{0}'.format(i))
		i += 1
		if i == 10:
			i = 0
	sys.stdout.write('|')
	sys.stdout.flush()
	print ''
	sys.stdout.write('  |')
	for j in range(0,width):
		sys.stdout.write('-')
	sys.stdout.write('|')
	sys.stdout.flush()
	print ''

	for i in range(0,height):
		for k in range(0,8):
				sys.stdout.write('{:2d}|'.format(i*8+k))
				for j in range(0,width):
					mask = 1 << k
					if bytebuffer[i][j]&mask:
						sys.stdout.write('*')
						sys.stdout.flush()
					else:
						sys.stdout.write(' ')
						sys.stdout.flush()
				sys.stdout.write('|')
				sys.stdout.flush()
				print ''
	sys.stdout.write('  |')
	for j in range(0,width):
		sys.stdout.write('-')
	sys.stdout.write('|')
	sys.stdout.flush()
	print ''

def update(image):
	frame = getframe(image,0,0,image.size[0], image.size[1])
	show(frame,image.size[0], int(math.ceil(image.size[1] / 8.0)))

def clear(image,x,y,width,height):
	draw = ImageDraw.Draw(image)
	draw.rectangle((x,y, x+width-1, y+height-1),0)

def msgwidth(msg, fontpkg, varwidth=False):
 	(fx, fy) = fontpkg['size']
 	retval = [ ]
 	clp = 0 # Current line pixel used count

	for c in msg:
		if c == u'\n':
			if clp == 0:
				retval.append(0)
			else:
				retval.append(clp-1)
			clp = 0
			continue

		if varwidth:
			try:
				clp += fontpkg[ord(c)].size[0]+1
			except:
				clp += fontpkg[ord('?')].size[0]+1
		else:
			clp += fx+1
	retval.append(clp-1)
	return retval

 # 	for c in msg:
 # 		if c == u'\n':
 # 			retval.append(clp-1)
 # 			clp = 0
 # 			continue
	#
 # 		bytearray = copy.copy(fontpkg[ord(c)])
 # 		if varwidth and ord(c) != 0x20: # if variable width requested and char is not a space
 # 			try:
 # 				# Trim left
 # 				while bytearray[0] == 0:
 # 					del bytearray[0]
 # 				# Trim right
 # 				for i in range(len(bytearray)-1,0,-1):
 # 					if bytearray[i] == 0:
 # 						del bytearray[i]
 # 			except IndexError:
 # 				# bytearray for this character was empty
 # 				pass
	#
 # 		for val in bytearray:
 # 			clp += 1
 # 		# Add pixel wide gap between characters
 # 		clp += 1
 # 	retval.append(clp-1)
	#
 # 	return retval

def line(image,x0, y0, x1, y1, color=1):
	draw = ImageDraw.Draw(image)
	draw.line((x0,y0,x1,y1),color)

def textsize(msg, fontpkg, varwidth): # returns the size needed to contain provided message
	# Input
	#	msg (unicode): string that contains the message for the calculation
	#	fontpkg (fontpkg): the font to use for the calculation
	#	varwidth (bool): Should the font be fixed or variable width

	maxw = 0
	maxh = 0
	cx = 0
	(fx,fy) = fontpkg['size']

	for c in msg:

		if c == u'\n':
			maxh = maxh + fy
			if cx > maxw:
				maxw = cx
			cx = 0
			continue

		try:
			charimg = fontpkg[ord(c)]
		except KeyError:
			# Requested character does not exist in font.  Replace with '?'
			charimg = fontpkg[ord('?')]

		if varwidth:
			cx += charimg.size[0]
		else:
			cx += fx

	if cx > maxw:
		maxw = cx
	maxh = maxh + fy

	return ((maxw, maxh))

def message(msg, fontpkg,varwidth = False, just='left', size=(0,0)):
	(fx,fy) = fontpkg['size']
	cx = 0
	cy = 0
	cw = 0

	# initialize image

	if msg == '':
		msg = ' '

	maxw, maxh = textsize(msg, fontpkg, varwidth)

	# msglines = msg.split('\n')
	# maxw = 0
	# for line in msglines:
	# 	if maxw < len(line):
	# 		maxw = len(line)
	# maxw = maxw * fx
	# maxh = len(msglines) * fy

	# If a size was provided that is larger than what is required to display the text
	# expand the image size as appropriate
	width, height = size
	maxw = maxw if maxw > width else width
	maxh = maxh if maxh > height else height
	image = Image.new("1", (maxw, maxh), 0)

	lineimage = Image.new("1", (maxw, fy), 0)
	for c in msg:

		# If newline, move y to next line (based upon font height) and return x to beginning of line
		if c == u'\n':
			# Place line into image
			if just == u'left':
				ax = 0
			elif just == u'center':
				ax = (maxw-cx)/2
			elif just == u'right':
				ax = (maxw-cx)
			image.paste(lineimage, (ax, cy))
			lineimage = Image.new("1", (maxw, fy), 0)
			cy = cy + fy
			cx = 0
			continue

		try:
			charimg = fontpkg[ord(c)]
		except KeyError:
			# Requested character does not exist in font.  Replace with '?'
			charimg = fontpkg[ord('?')]


		# Adjust charimg if varwidth is False
		if not varwidth:
			offset = (fx-charimg.size[0])/2
			charimg = charimg.crop( (-offset,0,fx-offset,fy) )
			charimg.load()

		# Paste character into frame
		lineimage.paste(charimg, (cx,0))

		# Erase space between characters
		draw = ImageDraw.Draw(lineimage)
		draw.rectangle((cx+charimg.size[0],0, cx+charimg.size[0], fy-1),0)

		# Move to next character position
		if varwidth:
			cx += charimg.size[0]
		else:
			cx += fx

	# # resize to exact requirement of message
	# self.image.crop((0,0,cx-1, cy+fy))

	# Place last line into image
	if just == u'left':
		ax = 0
	elif just == u'center':
		ax = (maxw-cx)/2
	elif just == u'right':
		ax = (maxw-cx)
	image.paste(lineimage, (ax, cy))

	return image
