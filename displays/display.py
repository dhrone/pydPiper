#!/usr/bin/python
# coding: UTF-8

# Abstract Base class to provide display primitives
# Written by: Ron Ritchey
import sys, copy, math, abc

class widget:
	__metaclass__ = abc.ABCMeta

	# width and height.  In pixels for graphics displays and characters for character displays
	width = 0
	height = 0

	# type.  What type of widget this is.  Used to determine what to do on a refresh.
	type = None

	# image.  A render of the current contents of the widget.
	image = None

# Widgets
# An element to place on a canvas.
# Static except when needing to be refreshed when any underlying variable gets changed.
# 	name -- Name of the widget.  Used to refer to the widget when including it in a canvas
# 	location -- (x,y) Upper left of where to place widget.  Relative to the containing object
# 	size -- (w,h) bounding size of display object
# 	justification - how to place widget on the screen (relative to itself and its bounding size). (left, right, center)
# 	type -- type of display object to render
# 		Choice from...
#
# 		Text
# 			format -- format string to structure text content
# 			variables -- array of variable names to combine with format string
# 		Image
# 			file -- name of file to retrieve
# 			crop -- (x,y,w,h) Subsection of the image to display
# 		Progress bar
# 			style -- type of progress bar to render (rounded, square)
# 			size - (w,h) how tall and wide the bar should be
# 			variable -- the variable that contains the progress value
# 			range -- (x,y) the top and bottom possible values for the variable
# 		line
# 			start -- (x,y) Where to start the line draw
# 			end -- (x,y) Where to end the line draw
# 			width -- How wide to draw the line
# 		rectangle
# 			location -- (x,y) Upper left of the rectangle
# 			size -- (w,h) size of the rectangle
# 			width -- How wide to draw the lines that make up the rectangle

	@abc.abstractmethod
	def __init__(self, (width, height), name, variabledict)):
		# name is the reference that will be used to access the widget.  Must be unique.
		# (width,height) is the requested size of the widget
		# variabledict is the database that contains the current values of all display variables

		# self.width = width
		# self.height = height
		# self.name = name
		# self.variabledict = variabledict
		return

	@abc.abstractmethod
	def update(self):
		# Refresh content based upon current variables
		return

	# Widgets
	@abc.abstractmethod
	def text(self, formatstring, variables, (h,w)=(0,0), fontpkg=Null, varwidth = False, just='left', vjust='top'):
		# Input
		# 	msg (unicode) -- msg to display
		#	(w,h) (integer tuple) -- Bounds of the rectangle that message will be written into.  If set to 0, no restriction on size.
		#	fontpkg (font object) -- The font that the message should be rendered in.
		#	varwidth (bool) -- Whether the font should be shown monospaced or with variable pitch
		#	just (unicode) -- Determines how to justify the text horizontally.  Allowed values [ 'left','right','center' ]
		#	vjust (unicode) -- Determines how to justify the text vertically.  Allowed values [ 'top', 'bottom', 'center' ]
		return

	# @abc.abstractmethod
	# def image(self, file,(h,w)=(0,0)):
	# 	# Input
	# 	#	file (unicode) -- filename of file to retrieve image from.  Must be located within the images directory.
	# 	#	(h,w) (integer tuple) -- Bounds of the rectangle that image will be written into.  If set to 0, no restriction on size.
	# 	return

	@abc.abstractmethod
	def progressbar(self, value, range, size, style):
		# Input
		#	value (numeric) -- Value of the variable showing progress.
		#	range (numeric tuple) -- Range of possible values.  Used to calculate percentage complete.
		#	size (number tuple) -- width and height to draw progress boundary
		#	style (unicode) -- Sets the style of the progress bar.  Allowed values [ 'rounded', 'square' ]
		return

	@abc.abstractmethod
	def line(self,  (x0,y0,x1,y1), color=1, width=1):
		# Input
		#	(x0,y0, x1, y1) (integer quad tuple) -- Points to draw a line between.
		#	width (integer) -- number of pixels/blocks wide the line should be drawn
		#	do (display object) -- If provided, the image will be placed within the provided display object
		return

	@abc.abstractmethod
	def rectangle(self,  (x0,y0,x1,y1), width=1):
		# Input
		#	(x0,y0, x1, y1) (integer quad tuple) -- Upper left and lower right corners of the rectangle.
		#	width (integer) -- number of pixels/blocks wide the lines of the rectangle should be drawn
		#	do (display object) -- If provided, the image will be placed within the provided display object
		return

	@abc.abstractmethod
	def getimage(self):
		# returns a graphical or character image suitable for including in a graphical or character based canvas
		return

	# Utility functions
	def evaltext(formatstring, variables):
		# return a string that places variables according to formatstring instructions
		return

class gwidget(widget):

		def __init__(self, (width, height), name, variabledict)):
			# name is the reference that will be used to access the widget.  Must be unique.
			# (width,height) is the requested size of the widget
			# variabledict is the database that contains the current values of all display variables

			self.width = width
			self.height = height
			self.name = name
			self.variabledict = variabledict
			self.image = None
			self.type = None

		def update(self):
			return

		# Widgets
		def text(self, formatstring, variables, size=(0,0), fontpkg=Null, varwidth = False, just='left', vjust='top'):
			# Input
			# 	msg (unicode) -- msg to display
			#	(w,h) (integer tuple) -- Bounds of the rectangle that message will be written into.  If set to 0, no restriction on size.
			#	fontpkg (font object) -- The font that the message should be rendered in.
			#	varwidth (bool) -- Whether the font should be shown monospaced or with variable pitch
			#	just (unicode) -- Determines how to justify the text horizontally.  Allowed values [ 'left','right','center' ]
			#	vjust (unicode) -- Determines how to justify the text vertically.  Allowed values [ 'top', 'bottom', 'center' ]

			self.type = u'text'

			(fx,fy) = fontpkg['size']
			w,h = size
			cx = 0
			cy = 0
			cw = 0

			msg = self.evaltext(formatstring, variables)

			# initialize image if needed
			if self.image is None:
				# initialize image
				msglines = msg.split('\n')
				maxw = 0
				for line in msglines:
					if maxw < len(line):
						max = len(line):
				maxw = maxw * fx
				maxh = len(msglines) * fy
				self.image = Image.new("1", (maxw, maxh), 0)


			for c in msg:

				# If newline, move y to next line (based upon font height) and return x to beginning of line
				if c == u'\n':
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
					offset = (fx-charimg.width)/2
					charimg = copy.copy(charimg).crop( (-offset,0,fx-offset,fy) )

				# Paste character into frame
				self.image.paste(charimg, (cx,cy))

				# Erase space between characters
				clear(image,cx+charimg.width,cy,1,fy)

				# Move to next character position
				if varwidth:
					cx += charimg.width+1
				else:
					cx += fx+1

			# Resize image
			if size == (0,0):
				# resize to exact requirement of message
				self.image.crop(0,0,cx-1, cy+fy)
			else:
				self.image.crop(0,0,w,h)
			self.size = (self.width, self.height)

			return self.image

		# def image(self, file,(h,w)=(0,0)):
		# 	# Input
		# 	#	file (unicode) -- filename of file to retrieve image from.  Must be located within the images directory.
		# 	#	(h,w) (integer tuple) -- Bounds of the rectangle that image will be written into.  If set to 0, no restriction on size.
		# 	return

		def progressbar(self, value, range, size, style):
			# Input
			#	value (numeric) -- Value of the variable showing progress.
			#	range (numeric tuple) -- Range of possible values.  Used to calculate percentage complete.
			#	size (number tuple) -- width and height to draw progress boundary
			#	style (unicode) -- Sets the style of the progress bar.  Allowed values [ 'rounded', 'square' ]
			return

		@abc.abstractmethod
		def line(self, (x0,y0,x1,y1), color=1, width=1):
			# Input
			#	(x0,y0, x1, y1) (integer quad tuple) -- Points to draw a line between.
			#	width (integer) -- number of pixels/blocks wide the line should be drawn
			#	do (display object) -- If provided, the image will be placed within the provided display object

			draw = ImageDraw.Draw(self.image)
			draw.line( (x0,y0,x1,y1) ,color)
			self.size = self.image.size

			return

		def rectangle(self,  (x0,y0,x1,y1), color=1, width=1):
			# Input
			#	(x0,y0, x1, y1) (integer quad tuple) -- Upper left and lower right corners of the rectangle.
			#	width (integer) -- number of pixels/blocks wide the lines of the rectangle should be drawn
			#	do (display object) -- If provided, the image will be placed within the provided display object

			draw = ImageDraw.Draw(self.image)
			draw.rectangle((x0,y0,x1,y1),color)
			self.size = self.image.size
			return


		@abc.abstractmethod
		def getimage(self):
			# returns a graphical image suitable for including in a graphical based canvas
			return
