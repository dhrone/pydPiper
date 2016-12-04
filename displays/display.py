#!/usr/bin/python
# coding: UTF-8

# Abstract Base class to provide display primitives
# Written by: Ron Ritchey
import sys, copy, math, abc, logging, math, time, copy
from PIL import Image
from PIL import ImageDraw

class widget:
	__metaclass__ = abc.ABCMeta

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


	def __init__(self, name, variabledict=None):
		# name is the reference that will be used to access the widget.  Must be unique.
		# (width,height) is the requested size of the widget
		# variabledict is the database that contains the current values of all display variables

		# width and height.  In pixels for graphics displays and characters for character displays
		self.width = 0
		self.height = 0
		self.size = (0,0)

		# type.  What type of widget this is.  Used to determine what to do on a refresh.
		self.type = None

		# image.  A render of the current contents of the widget.
		self.image = None

		# variables.  Names of variables in to-be-used order
		self.variables = []

		# currentvarcict.  A record of any variables that have been used and their last value
		self.currentvardict = { }

		# variabledict.  A pointer to the current active list of system variables
		self.variabledict = None

		self.name = name
		self.currentvardict = { }
		self.variabledict = variabledict
		self.image = None
		self.type = None

	@abc.abstractmethod
	def update(self):
		# Refresh content based upon current variables
		return

	# Widgets
	@abc.abstractmethod
	def text(self, formatstring, variables, fontpkg, varwidth = False, just=u'left'):
		# Input
		# 	msg (unicode) -- msg to display
		#	(w,h) (integer tuple) -- Bounds of the rectangle that message will be written into.  If set to 0, no restriction on size.
		#	fontpkg (font object) -- The font that the message should be rendered in.
		#	varwidth (bool) -- Whether the font should be shown monospaced or with variable pitch
		#	just (unicode) -- Determines how to justify the text horizontally.  Allowed values [ 'left','right','center' ]
		return

	# @abc.abstractmethod
	# def image(self, file,(h,w)=(0,0)):
	# 	# Input
	# 	#	file (unicode) -- filename of file to retrieve image from.  Must be located within the images directory.
	# 	#	(h,w) (integer tuple) -- Bounds of the rectangle that image will be written into.  If set to 0, no restriction on size.
	# 	return

	@abc.abstractmethod
	def progressbar(self, value, rangeval, size, style=u'square', variabledict=None):
		# Input
		#	value (numeric) -- Value of the variable showing progress.
		#	range (numeric tuple) -- Range of possible values.  Used to calculate percentage complete.
		#	size (number tuple) -- width and height to draw progress boundary
		#	style (unicode) -- Sets the style of the progress bar.  Allowed values [ 'rounded', 'square' ]
		return

	@abc.abstractmethod
	def line(self, (x,y), color=1):
		# Input
		#	(x,y) (integer  tuple) -- Draw line between origin and x,y.
		#	color (integer) -- color of the line
		return

	@abc.abstractmethod
	def rectangle(self, (x,y), color=1):
		# Input
		#	(x,y) (integer  tuple) -- Lower right of rectanble drawn from the origin
		#	color (integer) -- color of the rectangle
		return

	# @abc.abstractmethod
	# def getimage(self):
	# 	# returns a graphical or character image suitable for including in a graphical or character based canvas
	# 	return

	# Utility functions

	def transformvariable(self, val, name):
		# Implement transformation logic (e.g. |yesno, |onoff |upper |bigchars+0)
		# Format of 'name' is the name of the transform preceded by a '|' and
		# then if variables are required a series of values seperated by '+' symbols


		transforms = name.split(u'|')
		if len(transforms) == 0:
			return ''
		elif len(transforms) == 1:
			return val

		retval = val
		# Compute transforms
		for i in range(1,len(transforms)):
			transform_request = transforms[i].split(u'+')[0] # Pull request type away from variables
			if transform_request in [u'onoff',u'truefalse',u'yesno']:
				# Make sure input is a Boolean
				if type(val) is bool:

					if transform_request == u'onoff':
						retval = u'on' if val else u'off'
					elif transform_request == u'truefalse':
						retval = u'true' if val else u'false'
					elif transform_request == u'yesno':
						retval = u'yes' if val else u'no'
				else:
					logging.debug(u"Request to perform boolean transform on {0} requires boolean input").format(name)
					return val
			elif transform_request in [u'upper',u'capitalize',u'title',u'lower']:
				# These all require string input

				if type(val) is str or type(val) is unicode:
					if type(retval) is str:
						retval = retval.decode()
					if transform_request == u'upper':
						retval = retval.upper()
					elif transform_request == u'capitalize':
						retval = retval.capitalize()
					elif transform_request == u'title':
						retval = retval.title()
					elif transform_request == u'lower':
						retval = retval.lower()
				else:
					logging.debug(u"Request to perform transform on {0} requires string input").format(name)
					return val
			elif transform_request in [ u'bigchars',u'bigplay' ]:
				# requires a string input
				# bigchars requires a variable to specify which line of the msg to return


				tvalues = transforms[i].split('+')[1:]

				if len(tvalues) > 2:
					# Safe to ignore but logging
					logging.debug(u"Expected at most two but received {0} variables".format(len(values)))

				if len(tvalues) == 0:
					# Requires at least one variable to specify line so will return error in retval
					logging.debug(u"Expected one but received no variables")
					retval = u"Err"
				else:

					if transform_request == u'bigchars':
						try:
							if len(tvalues) == 2: # Request to add spaces between characters
								es = u"{0:<{1}}".format('',int(tvalues[1]))
								val = es.join(val)

							retval = displays.fonts.size5x8.bigchars.generate(val)[int(tvalues[0])]
						except (IndexError, ValueError):
							logging.debug(u"Bad value or line provided for bigchar")
							retval = u'Err'
					elif transform_request == u'bigplay':
						try:
							if len(tvalues) == 2: # Request to add spaces between characters
								es = u"{0:<{1}}".format('',int(tvalues[1]))
								val = es.join(val)

							retval = displays.fonts.size5x8.bigplay.generate(u'symbol')[int(tvalues[0])] + '  ' + displays.fonts.size5x8.bigplay.generate(u'page')[int(tvalues[0])]
						except (IndexError, ValueError):
							logging.debug(u"Bad value or line provided for bigplay")
							retval = u'Err'

		return retval

	def clear(self,image,x,y,width,height):
		draw = ImageDraw.Draw(image)
		draw.rectangle((x,y, x+width-1, y+height-1),0)

	def evaltext(self, formatstring, variables):
		# return a string that places variables according to formatstring instructions
		parms = []
		for v in variables:
			parms.append(self.variabledict[v])

		parms = []
		try:
			for k in range(len(variables)):
				varname = variables[k].split(u'|')[0]
				val = self.transformvariable(self.variabledict[varname], variables[k])
				parms.append(val)
		except KeyError:
			logging.debug( u"Variable not found in evaltext.  Values requested are {0}".format(variables) )
			# Format doesn't match available variables
			segval = u"VarErr"
			return segval

		# create segment to display
		try:
			segval = formatstring.format(*parms)
		except:
			logging.debug( u"Var Error Format {0}, Parms {1} Vars {2}".format(format, parms, vars) )
			# Format doesn't match available variables
			logging.debug(u"Var Error with parm type {0} and format type {1}".format(type(parms), type(format)))
			segval = u"VarErr"

		return segval

	def changed(self, variables):
		# variables (unicode array) -- An array containing the names of the variables being used
		# returns bool based upon whether any variables that have been used have changed since the last time a render was requested
		for v in variables:
			try:
				if self.variabledict[v] != self.currentvardict[v]:
					return True
			except KeyError:
				return True
		return False


class gwidget(widget):

	def update(self):
		if not self.changed(self.variables):
			return False

		if self.type == 'text':
			self.text(self.formatstring, self.variables, self.fontpkg, self.varwidth, self.size, self.just)
			return True
		elif self.type == 'progressbar':
			self.progressbar(self.value, self.rangeval, self.size, self.style)
			return True
		else:
			return False

	def textsize(self, msg, fontpkg, varwidth): # returns the size needed to contain provided message
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
				cx += charimg.width
			else:
				cx += fx

		if cx > maxw:
			maxw = cx
		maxh = maxh + fy

		return ((maxw, maxh))

	# Widgets
	def text(self, formatstring, variables, fontpkg, varwidth = False, size=(0,0), just=u'left'):
		# Input
		# 	formatstring (unicode) -- format string
		#	variables (unicode array) -- list of variables used to populate formatstring.  Variable values come from variabledict.
		#	fontpkg (font object) -- The font that the message should be rendered in.
		#	varwidth (bool) -- Whether the font should be shown monospaced or with variable pitch
		#	size (integer tuple) -- Size of image if larger than text size
		#	just (unicode) -- Determines how to justify the text horizontally.  Allowed values [ 'left','right','center' ]

		# Save variables used for this text widget
		self.currentvardict = { }
		for v in variables:
			self.currentvardict[v] = self.variabledict[v]

		# size parameters for future updates
		self.type = u'text'
		self.formatstring = formatstring
		self.variables = variables
		self.fontpkg = fontpkg
		self.varwidth = varwidth
		self.just = just

		(fx,fy) = fontpkg['size']
		cx = 0
		cy = 0
		cw = 0


		msg = self.evaltext(formatstring, variables)

		# initialize image

		maxw, maxh = self.textsize(msg, fontpkg, varwidth)

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
		self.image = Image.new("1", (maxw, maxh), 0)

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
				self.image.paste(lineimage, (ax, cy))
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
				offset = (fx-charimg.width)/2
				charimg = copy.copy(charimg).crop( (-offset,0,fx-offset,fy) )

			# Paste character into frame
			lineimage.paste(charimg, (cx,0))

			# Erase space between characters
			self.clear(lineimage,cx+charimg.width,0,1,fy)

			# Move to next character position
			if varwidth:
				cx += charimg.width
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
		self.image.paste(lineimage, (ax, cy))

		self.size = self.image.size
		self.width = self.image.width
		self.height = self.image.height

		return self.image

	# def image(self, file,(h,w)=(0,0)):
	# 	# Input
	# 	#	file (unicode) -- filename of file to retrieve image from.  Must be located within the images directory.
	# 	#	(h,w) (integer tuple) -- Bounds of the rectangle that image will be written into.  If set to 0, no restriction on size.
	# 	return

	def progressbar(self, value, rangeval, size, style=u'square'):
		# Input
		#	value (numeric) -- Value of the variable showing progress.
		#	rangeval (numeric tuple) -- Range of possible values.  Used to calculate percentage complete.
		#	size (number tuple) -- width and height to draw progress bar
		#	style (unicode) -- Sets the style of the progress bar.  Allowed values [ 'rounded', 'square' ]

		if self.variabledict is None:
			self.variabledict = { }

		self.variables = []

		# Convert variable to value if needed
		if type(value) is unicode:
			v = self.variabledict[value] if value in self.variabledict else 0
			if value in self.variabledict:
				self.variables.append(value)
		elif type(value) is int or type(value) is float:
			v = value
		else:
			v = 0

		l,h = rangeval
		# Convert range low to value if needed
		if type(l) is unicode:
			rvlow = self.variabledict[l] if l in self.variabledict else 0
			if l in self.variabledict:
				self.variables.append(l)
		elif type(l) is int or type(l) is float:
			rvlow = l
		else:
			rvlow = 0

		# Convert range high to value if needed
		if type(h) is unicode:
			rvhigh = self.variabledict[h] if h in self.variabledict else 0
			if h in self.variabledict:
				self.variables.append(h)
		elif type(h) is int or type(h) is float:
			rvhigh = h
		else:
			rvhigh = 0

		width, height = size

		# correct values if needed
		if rvhigh < rvlow:
			t = rvlow
			rvlow = rvhigh
			rvhigh = t

		if v < rvlow or v > rvhigh:
			raise ValueError

		percent = (v - rvlow) / float((rvhigh - rvlow))

		# make image to place progress bar
		self.image = Image.new("1", size, 0)

		if style == u'square':
			draw = ImageDraw.Draw(self.image)
			draw.line( (0,0,0,height-1),1)
			for i in range (0,int((width-2)*percent)):
				draw.line( (i+1,0,i+1,height-1),1)
			for i in range (int((width-2)*percent), width-2):
				self.image.putpixel((i+1,0), 1)
				self.image.putpixel((i+1,height-1), 1)
			draw.line( (width-1,0,width-1,height-1),1)

		self.size = self.image.size
		self.width = self.image.width
		self.height = self.image.height

		self.value = value
		self.rangeval = rangeval
		self.style = style
		self.type = 'progressbar'

		return self.image

	def line(self, (x,y), color=1):
		# Input
		#	(x,y) (integer tuple) -- Draw a line from the origin to x,y
		#	color -- color to use for the line

		# Does image exist yet?
		if self.image == None:
			self.image = Image.new("1", (x+1, y+1), 0)
		else:
			# Is image big enough?
			if self.image.width < x or self.image.height < y:
				self.image.crop(0,0,x,y)

		draw = ImageDraw.Draw(self.image)
		draw.line( (0,0,x,y) ,color)
		self.size = self.image.size
		self.width = self.image.width
		self.height = self.image.height

		return self.image

	def rectangle(self, (x,y), fill=0, outline=1):
		# Input
		#	(x,y) (integer tuple) -- Bottom left and bottom right of rectangle drawn from origin
		#	color -- color to use for the rectangle

		# Does image exist yet?
		if self.image == None:
			self.image = Image.new("1", (x+1, y+1), 0)
		else:
			# Is image big enough?
			if self.image.width < x or self.image.height < y:
				self.image.crop(0,0,x,y)

		draw = ImageDraw.Draw(self.image)
		draw.rectangle((0,0,x,y),fill, outline)
		self.size = self.image.size
		self.width = self.image.width
		self.height = self.image.height

		return self.image

	def getimage(self):
		# returns a graphical image suitable for including in a graphical based canvas

		return self.Image

class gwidgetText(gwidget):
	def __init__(self, name, formatstring, fontpkg, variabledict={ }, variables =[], varwidth = False, size=(0,0), just=u'left'):
		super(gwidgetText, self).__init__(name, variabledict)
		self.text(formatstring, variables, fontpkg, varwidth, size, just)

class gwidgetProgressBar(gwidget):
	def __init__(self, name, value, rangeval, size, style=u'square',variabledict=None):
		super(gwidgetProgressBar, self).__init__(name, variabledict)
		self.progressbar(value, rangeval, size, style)

class gwidgetLine(gwidget):
	def __init__(self, name, (x,y), color=1):
		super(gwidgetLine, self).__init__(name)
		self.line((x,y), color)

class gwidgetRectangle(gwidget):
	def __init__(self, name, (x,y), fill=0, outline=1):
		super(gwidgetRectangle, self).__init__(name)
		self.line((x,y), fill, outline)

class canvas():
	__metaclass__ = abc.ABCMeta

	@abc.abstractmethod
	def __init__(self, name):
		return

	@abc.abstractmethod
	def add(self, widget, (x,y), size): # Add a widget to the canvas
		# Input
		#	widget (widget): widget to add to canvas
		#	(x,y) (integer tuple): location to place widget on canvas
		#	size (integer tuple): size to limit widget to.  (0,0) means no restriction.
		return

	@abc.abstractmethod
	def place(self, widget, (x,y), size):
		# Input
		#	widget (widget): widget to place
		#	(x,y) (integer tuple): where to place it
		#	size (integer tuple): how big should it be
		return

	@abc.abstractmethod
	def update(self): # Update all widgets and refresh canvas
		return

class gcanvas(canvas):

	def __init__(self, name, (w,h)): # Initialize class
		self.name = name
		self.widgets = []
		self.image = Image.new("1", (w,h) )
		self.width = w
		self.height = h

	def add(self, widget, (x,y), (w,h)=(0,0)): # Add a widget to the canvas
		self.widgets.append( (widget,x,y,w,h) )
		a,b,c,d,e = self.widgets[-1]

		self.place(widget, (x,y), (w,h) )

	def clear(self): # Erase canvas
		self.image = Image.new("1", (self.image.width, self.image.height))

	def place(self, widget, (x,y), size=(0,0)): # Place a widget's image on the canvas
		# Input
		#	widget (widget): widget to place
		#	(x,y) (integer tuple): where to place it
		#	size (integer tuple): how big should it be
		w,h = size
		if w > 0 or h > 0:
			img = widget.image.crop(0,0,0+w-1,0+h-1)
		else:
			img = widget.image

		self.image.paste(img, (x,y))

	def update(self): # Update all widgets and refresh canvas

		retval = False
		for e in self.widgets:
			widget,x,y,w,h = e
			if widget.update():
				retval = True

		# If a widget has changed
		if retval:
			# Clear canvas
			self.clear()

			# Replace all of the widgets
			for e in self.widgets:
				widget,x,y,w,h = e
				self.place(widget, (x,y), (w,h))

		return retval

class renderer(object):

	def __init__(self, name, canvas):
		# Input
		#	name (unicode) -- the name of the render object
		#	canvas (canvas) -- the canvas to render
		self.name = name
		self.canvas = canvas
		self.type = None

class grenderer(renderer):

	def __init__(self, name, canvas):
		super(grenderer, self).__init__(name, canvas)
		self.image = copy.deepcopy(canvas.image)

	def static(self, appears='instant'): # Set up for static display
		self.type = u'static'
		return

	def popup(self, frequency=15, duration=5): # Set up for pop-up display
		# Input
		#	frequency (float) -- How long to display the top of the canvas
		#	duration (float) -- How long to stay popped up
		self.type = u'popup'
		return

	def scroll(self, direction=u'left', distance=1, gap=20, hesitatetype=u'onloop', hesitatetime=2): # Set up for scrolling
		# Input
		#	direction (unicode) -- What direction to scroll ['left', 'right','up','down']
		#	hesitatetype (unicode) -- the type of hesitation to use ['none', 'onstart', 'onloop']
		#	hesitatetime (float) -- how long in seconds to hesistate

		# If this is the first pass, initialize state variables
		try:
			self.start
			self.end
			self.image
			self.index
			self.width
			self.height
			self.type
			self.direction
			self.distance
			self.gap
			self.hesitatetype
			self.hesitatetime
			self.index
		except:
			self.start = time.time()
			if hesitatetype not in ['onstart', 'onloop']:
				self.end = 0
			else:
				self.end = self.start + hesitatetime
			self.image = copy.deepcopy(self.canvas.image)
			self.index = 0
			self.width = self.image.width
			self.height = self.image.height
			self.index = 0

			# Save parameters
			self.type= u'scroll'
			direction = direction.lower()
			self.direction = direction
			self.distance = distance
			self.gap = gap
			hesitatetype = hesitatetype.lower()
			self.hesitatetype = hesitatetype
			self.hesitatetime = hesitatetime

			# Expand canvas
			if direction in ['left','right']:
				self.image = Image.new("1", (self.canvas.width+gap, self.canvas.height))
				self.image.paste(self.canvas.image, (0,0))
				self.width = self.image.width
				self.height = self.image.height
				self.size = self.image.size
			elif direction in ['up','down']:
				self.image = Image.new("1", (self.canvas.width, self.canvas.height+gap))
				self.image.paste(self.canvas.image, (0,0))
				self.width = self.image.width
				self.height = self.image.height
				self.size = self.image.size


		if self.canvas.update():
			# something has changed
			self.start = time.time()
			if hesitatetype not in ['onstart', 'onloop']:
				self.end = 0
			else:
				self.end = self.start + hesitatetime
			self.image = copy.copy(self.canvas.image)
			self.index = 0
			self.width = self.image.width
			self.height = self.image.height
			self.index = 0

			# Expand canvas
			if direction in ['left','right']:
				self.image = Image.new("1", (self.canvas.width+gap, self.canvas.height))
				self.image.paste(self.canvas.image, (0,0))
				self.width = self.image.width
				self.height = self.image.height
				self.size = self.image.size

			elif direction in ['up','down']:
				self.image = Image.new("1", (self.canvas.width, self.canvas.height+gap))
				self.image.paste(self.canvas.image, (0,0))
				self.width = self.image.width
				self.height = self.image.height
				self.size = self.image.size

		# Hesitate if needed
		if self.end > time.time():
			return False

		# Save region to be overwritten
		# Move body
		# Restore region to cleared space

		image = self.image
		width = self.width
		height = self.height

		if direction == u'left':
			region = image.crop((0,0, distance, height))
			body = image.crop((distance,0, width, height))
			image.paste(body, (0,0))
			image.paste(region, ((width-distance),0) )
			if hesitatetype == u'onloop':
				self.index += distance
				if self.index >= width:
					self.index = 0
					self.start = time.time()
					self.end = self.start + hesitatetime
		elif direction == u'right':
			region = image.crop((width-distance,0, width, height))
			body = image.crop((0,0, width-distance, height))
			image.paste(body, (distance,0) )
			image.paste(region, (0,0) )
			if hesitatetype == u'onloop':
				self.index += distance
				if self.index >= width:
					self.index = 0
					self.start = time.time()
					self.end = self.start + hesitatetime
		elif direction == u'up':
			region = image.crop((0,0, width, distance))
			body = image.crop((0,distance, width, height))
			image.paste(body, (0,0) )
			image.paste(region, (0,height-distance) )
			if hesitatetype == u'onloop':
				self.index += distance
				if self.index >= height:
					self.index = 0
					self.start = time.time()
					self.end = self.start + hesitatetime
		elif direction == u'down':
			region = image.crop((0,height-distance, width, height))
			body = image.crop((0,0, width, height-distance))
			image.paste(body, (0,distance) )
			image.paste(region, (0,0) )
			if hesitatetype == u'onloop':
				self.index += distance
				if self.index >= height:
					self.index = 0
					self.start = time.time()
					self.end = self.start + hesitatetime

		return True

	def update(self): # Do the next step of any animation that is required

		if self.type == u'scroll':
			return self.scroll(self.direction, self.distance, self.gap, self.hesitatetype, self.hesitatetime)

		return False



class page():
	__metaclass__ = abc.ABCMeta

	@abc.abstractmethod
	def __init__(self, name):
		return

	@abc.abstractmethod
	def add(self, widget, (x,y), size): # Add a canvas to the page
		# Input
		#	widget (widget): widget to add to canvas
		#	(x,y) (integer tuple): location to place widget on canvas
		#	size (integer tuple): size to limit widget to.  (0,0) means no restriction.
		return

	@abc.abstractmethod
	def place(self, canvas, (x,y), size):
		# Input
		#	canvas (canvas): canvas to place
		#	(x,y) (integer tuple): where to place it
		#	size (integer tuple): how big should it be
		return

	@abc.abstractmethod
	def update(self): # Update all canvases and refresh page
		return

class gpage(page):

	def __init__(self, name, (w,h)): # Initialize class
		self.name = name
		self.canvases = []
		self.image = Image.new("1", (w,h) )
		self.width = w
		self.height = h

	def add(self, canvas, (x,y), (w,h)=(0,0)): # Add a canvas to the page
		self.canvases.append( (canvas,x,y,w,h) )
		self.place(canvas, (x,y), (w,h) )

	def clear(self): # Erase canvas
		self.image = Image.new("1", (self.image.width, self.image.height))

	def place(self, canvas, (x,y), size=(0,0)): # Place a canvas's image on the page
		# Input
		#	widget (widget): widget to place
		#	(x,y) (integer tuple): where to place it
		#	size (integer tuple): how big should it be
		w,h = size
		if w > 0 or h > 0:
			img = canvas.image.crop( (0,0,0+w,0+h) )
		else:
			img = canvas.image

		self.image.paste(img, (x,y))

	def update(self): # Update all canvases and refresh page

		retval = False
		for e in self.canvases:
			canvas,x,y,w,h = e
			if canvas.update():
				retval = True

		# If a widget has changed
		if retval:
			# Clear canvas
			self.clear()

			# Replace all of the widgets
			for e in self.canvases:
				canvas,x,y,w,h = e
				self.place(canvas, (x,y), (w,h))

		return retval

if __name__ == '__main__':

	import graphics as g
	import fonts

	variabledict = { u'artist':u'Prince and the Revolutions', u'title':u'Million Dollar Club', u'volume':50 }
	variables = [ u'artist', u'title' ]

	f_HD44780 = fonts.bmfont.bmfont(u'latin1_5x8.fnt')
	fp_HD44780 = f_HD44780.fontpkg

	fp_Vint10x16 = fonts.bmfont.bmfont(u'Vintl01_10x16.fnt').fontpkg

	# artistw = gwidget(u'artist', variabledict)
	# artistw.text(u"{0}",[u'artist'], fp_Vint10x16, True, (0,0), 'left')

	artistw = gwidgetText(u'artist',"{0}",fp_Vint10x16, variabledict, [u'artist'], True)

	titlew = gwidget(u'title', variabledict)
	titlew.text(u"{0}",[u'title'], fp_HD44780, True)

	linew = gwidget(u'line1')
	linew.line( (99,0) )

	rectw = gwidget('rect1')
	rectw.rectangle( (99,15) )

	# progw = gwidget('prog1')
	# progw.progressbar( 50, (0,100), (80,6) )

	progw = gwidgetProgressBar(u'progbar1',u'volume', (0,100), (80,6), u'square', variabledict)

	gc1 = gcanvas('can1', (artistw.width,14) )
	gc2 = gcanvas('can2', (artistw.width,8) )

	gc1.add( artistw, (0,0) )
	gc2.add( titlew, (0,0) )
	# gc.add( linew, (0,22) )
	# gc.add( progw, (10,24) )

	gr1 = grenderer('testgr2',gc1)
	gr1.scroll('left')
	gr2 = grenderer('testgr2',gc2)
	gr2.scroll('up')

	firstpage = gpage('first', (100,32))
	firstpage.add(gr1, (0,0))
	firstpage.add(gr2, (0,14), (100,8))
	firstpage.add(linew, (0,22))
	firstpage.add(progw, (0,24))

	end = time.time() + 25
	flag = True
	i = 0
	variabledict['volume'] = i
	while end > time.time():
		i += 1
		if i > 100:
			i = 0
		variabledict['volume'] = i
		if end < time.time()+15 and flag:
			variabledict['title'] = u"Purple Rain"
			flag = False
		if firstpage.update():
			frame = g.getframe( firstpage.image, 0,0, firstpage.width, firstpage.height)
			g.show( frame, firstpage.width, int(math.ceil(firstpage.height/8.0)))
			time.sleep(.03)
