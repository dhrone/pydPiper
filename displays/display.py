#!/usr/bin/python
# coding: UTF-8

# Abstract Base class to provide display primitives
# Written by: Ron Ritchey

from __future__ import unicode_literals

import math, abc, logging, time, imp, sys, os
import moment
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

import fonts

class widget:
	__metaclass__ = abc.ABCMeta

	def __init__(self, variabledict={ }):
		# width and height.  In pixels for graphics displays and characters for character displays
		self.width = 0						# Width of the widget
		self.height = 0						# Height of the widget
		self.size = (0,0)					# Size of the widget
		self.type = None					# What type of widget this is.  Used to determine what to do on a refresh.
		self.image = None					# A render of the current contents of the widget.
		self.variables = []					# Names of variables in to-be-used order
		self.currentvardict = { }			# A record of any variables that have been used and their last value
		self.variabledict = variabledict	# variabledict.  A pointer to the current active system variable db
		self.curMsg = None					# If widget is derived from text, record the current message this widget was derived from

	@abc.abstractmethod
	def update(self):
		# Refresh content based upon current variables
		return

	# Widgets
	@abc.abstractmethod
	def text(self, formatstring, fontpkg, variabledict={ }, variables =[], varwidth = False, size=(0,0), just=u'left'):
		# Input
		# 	msg (unicode) -- msg to display
		#	(w,h) (integer tuple) -- Bounds of the rectangle that message will be written into.  If set to 0, no restriction on size.
		#	fontpkg (font object) -- The font that the message should be rendered in.
		#	varwidth (bool) -- Whether the font should be shown monospaced or with variable pitch
		#	just (unicode) -- Determines how to justify the text horizontally.  Allowed values [ 'left','right','center' ]
		return

	@abc.abstractmethod
	def progressbar(self, value, rangeval, size, style=u'square',variabledict={ }):
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
	def rectangle(self, (x,y), fill=0, outline=1):
		# Input
		#	(x,y) (integer  tuple) -- Lower right of rectanble drawn from the origin
		#	color (integer) -- color of the rectangle
		return

	@abc.abstractmethod
	def canvas(self, (w,h)):
		# Input
		#	(w,h) (integer  tuple) -- size of canvas
		return

	@abc.abstractmethod
	def popup(self, widget, dheight, duration=15, pduration=10):
		# Input
		#	widget (widget) -- Widget to pop up
		#	dheight (integer) -- Sets the height of the window which will get displayed from the canvas
		#	duration (float) -- How long to display the top of the canvas
		#	pduration (float) -- How long to stay popped up
		return

	@abc.abstractmethod
	def scroll(self, widget, direction=u'left', distance=1, speed=1, gap=20, hesitatetype=u'onloop', hesitatetime=2, threshold=0,reset=False):
		# Input
		#	widget (widget) -- Widget to scroll
		#	direction (unicode) -- What direction to scroll ['left', 'right','up','down']
		#	hesitatetype (unicode) -- the type of hesitation to use ['none', 'onstart', 'onloop']
		#	hesitatetime (float) -- how long in seconds to hesistate
		#	threshold (integer) -- scroll only if widget larger than threshold
		#	reset (bool) -- Should the hesitation timer be reset
		return

	# Utility functions
	def updatesize(self):
		if self.image != None:
			self.width = self.image.size[0]
			self.height = self.image.size[1]
			self.size = self.image.size
		else:
			self.width = 0
			self.height = 0
			self.size = (0,0)




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
			transform_request = transforms[i].split(u'+')[0].lower() # Pull request type away from variables
			if transform_request in [u'onoff',u'truefalse',u'yesno']:
				# Make sure input is a Boolean
				if type(retval) is bool:

					if transform_request == u'onoff':
						retval = u'on' if val else u'off'
					elif transform_request == u'truefalse':
						retval = u'true' if val else u'false'
					elif transform_request == u'yesno':
						retval = u'yes' if val else u'no'
				else:
#					logging.debug(u"Request to perform boolean transform on {0} requires boolean input".format(name))
					return val
			elif transform_request in [u'int']:
				try:
					retval = int(val)
				except:
					# Value not convertible to int
					retval = 0
			elif transform_request in [u'upper',u'capitalize',u'title',u'lower']:
				# These all require string input

				if type(retval) is str or type(retval) is unicode:
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
					logging.debug(u"Request to perform transform on {0} requires string input".format(name))
					return val

# Time transforms
# --------------------------
# Input must be a moment object
# |timezone+tz - converts utc referenced moment object into an equivalant moment object in the timezone requested by the tz parameter
# |local - converts utc referenced moment object into an equivalant moment object in the local timezone (as specified in pydPiper_config.TIMEZONE variable)
# |strftime+s - converts moment object into string formated using the strftime format string provided in the s parameter

			elif transform_request in [ u'timezone', u'strftime' ]:
				# requires a moment object as input

				tvalues = transforms[i].split('+')[1:]

				if type(retval) is moment.core.Moment:

					if len(tvalues) > 1:
						# Safe to ignore but logging
						logging.debug(u"Expected one parameter but received {0}".format(len(values)))

					if len(tvalues) == 0:
						# Requires at least one variable to specify line so will return error in retval
						logging.debug(u"Expected one parameter but received none")
						retval = u"Err"
					else:

						if transform_request == u'timezone':
							try:
								retval = retval.timezone(tvalues[0])
							except ValueError:
								# Received bad timezone value
								logging.debug("Cannot convert timezone.  Requested timezone ({0}) is not valid".format(tvalues[0]))

						elif transform_request == u'strftime':
							try:
								retval = retval.strftime(tvalues[0])
							except:
								logging.debug(u"Cannot format moment.  Bad strftime value provided ({0})".format(tvalues[0]))
								retval = u'Err'
				elif transform_request in [u'strftime'] and type(retval) is int:
					retval = time.strftime(tvalues[0], time.gmtime(int(retval)))
				else:
					# Bad input provided
					logging.debug(u'Expected a moment variable but received a {0}'.format(type(retval)))

			elif transform_request in [ u'select' ]:
				# select replaces the variable with string based upon a matching pattern.
				# <variable>|select+matchstring+replacestring+matchstring+replacestring+...

				tvalues = transforms[i].split('+')[1:]
				if len(tvalues)%2 != 0 or len(tvalues)==0:
					# Must have pairs of input (match+replace)
					retval = u'Err'
				else:
					for i in range(0,len(tvalues),2):
						if retval == tvalues[i]:
							retval = tvalues[i+1]
							break
					else:
						retval = u' '

#			elif transform_request in [ u'local' ]:
#				# requires a moment object as input
#
#				if type(retval) is moment.core.Moment:
#					try:
#						retval = retval.timezone(pydPiper_config.TIMEZONE)
#					except ValueError:
#						# Received bad timezone value
#						logging.debug("Cannot convert timezone.  Requested timezone ({0}) is not valid".format(pydPiper_config.TIMEZONE))
#				else:
#					# Bad input provided
#					logging.debug(u'Expected a moment variable but received a {0}'.format(type(retval)))

		return retval

	def clear(self,image,x,y,width,height):
		draw = ImageDraw.Draw(image)
		draw.rectangle((x,y, x+width-1, y+height-1),0)

	def evaltext(self, formatstring, variables):
		# return a string that places variables according to formatstring instructions

		parms = []
		try:
			for k in range(len(variables)):
				varname = variables[k].split(u'|')[0]
				val = self.transformvariable(self.variabledict[varname], variables[k])
				parms.append(val)
		except KeyError:
			logging.debug( u"Variable not found in evaltext.  Values requested are {0}".format(variables) )
			print u"Variable not found in evaltext.  Values requested are {0}".format(variables)
			# Format doesn't match available variables
			segval = u"VarErr"
			return segval

		# create segment to display
		try:
			segval = formatstring.format(*parms)
		except:
			logging.debug( u"Var Error Format {0}, Parms {1} Vars {2}".format(formatstring, parms, variables) )
			print u"Var Error Format {0}, Parms {1} Vars {2}".format(formatstring, parms, variables)
			# Format doesn't match available variables
			logging.debug(u"Var Error with parm type {0} and format type {1}".format(type(parms), type(formatstring)))
			segval = u"VarErr"

		return segval

	def changed(self, variables):
		# variables (unicode array) -- An array containing the names of the variables being used
		# returns bool based upon whether any variables that have been used have changed since the last time a render was requested
		for v in variables:
			v = v.split(u'|')[0]
			try:
				if self.variabledict[v] != self.currentvardict[v]:
					return True
			except KeyError:
				return True
		return False


class gwidget(widget):

	def update(self, reset=False):

		# Moved change detection into widget
#		if self.type in ['text', 'ttext']:
#			if not self.changed(self.variables):
#				return False

		if self.type == 'text':
			return self.text(self.formatstring, self.variables, self.fontpkg, self.varwidth, self.specifiedsize, self.just)
		if self.type == 'ttext':
			return self.ttext(self.formatstring, self.variables, self.fontpkg, self.varwidth, self.specifiedsize, self.just)
		elif self.type == 'progressbar':
			return self.progressbar(self.value, self.rangeval, self.size, self.style)
		elif self.type == 'progressimagebar':
			return self.progressimagebar(self.maskimage, self.value, self.rangeval, self.direction)
		elif self.type == 'canvas':
			retval = True if reset else False
			for e in self.widgets:
				widget,x,y,w,h = e
				if widget.update(reset):
					retval = True
			# If a widget has changed
			if retval:
				# Replace all of the widgets
				self.clear()
				for e in self.widgets:
					widget,x,y,w,h = e
					self.place(widget, (x,y), (w,h))
			return retval
		elif self.type == u'scroll':
			return self.scroll(self.widget, self.direction, self.distance, self.speed, self.gap, self.hesitatetype, self.hesitatetime,self.threshold, reset)
		elif self.type == u'popup':
			return self.popup(self.widget, self.dheight, self.duration, self.pduration)
		else:
			# Static content like images, lines, rectangles do not need to be refreshed
			return False

	# WIDGETS

	# CANVAS widget functions
	def canvas(self, (w,h)):
		self.type = u'canvas'
		self.image = Image.new("1", (w,h) )
		self.updatesize()
		self.widgets = []

	def add(self, widget, (x,y), (w,h)=(0,0)): # Add a widget to the canvas

		if self.type != u'canvas':
			logging.warning("Trying to add a widget to something that is not a canvas")
			return

		self.widgets.append( (widget,x,y,w,h) )
		self.place(widget, (x,y), (w,h) )
		return self

	def clear(self): # Erase canvas
		if self.type != u'canvas':
			logging.warning('Trying to clear a widget that is not a canvas')
			return
		self.image = Image.new("1", (self.image.size[0], self.size[1]))

	def place(self, widget, (x,y), size=(0,0)): # Place a widget's image on the canvas
		# Input
		#	widget (widget): widget to place
		#	(x,y) (integer tuple): where to place it
		#	size (integer tuple): how big should it be
		if self.type != u'canvas':
			logging.warning(u"Trying to place a widget on something that is not a canvas")
			return

		w,h = size
		if w > 0 or h > 0:
			img = widget.image.crop( (0,0,0+w,0+h) )
		else:
			img = widget.image

		self.image.paste(img, (x,y))

	# TEXT widget functions
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
				cx += charimg.size[0]
			else:
				cx += fx

		if cx > maxw:
			maxw = cx
		maxh = maxh + fy

		return ((maxw, maxh))

	def text(self, formatstring, variables, fontpkg, varwidth = True, specifiedsize=(0,0), just=u'left'):
		# Input
		# 	formatstring (unicode) -- format string
		#	variables (unicode array) -- list of variables used to populate formatstring.  Variable values come from variabledict.
		#	fontpkg (font object) -- The font that the message should be rendered in.
		#	varwidth (bool) -- Whether the font should be shown monospaced or with variable pitch
		#	specifiedsize (integer tuple) -- Size to make image if larger than what is requird for the message size
		#	just (unicode) -- Determines how to justify the text horizontally.  Allowed values [ 'left','right','center','centerchar' ]

		# Save variables used for this text widget
		self.currentvardict = { }
		for v in variables:
			try:
				jv = v.split(u'|')[0]
				self.currentvardict[jv] = self.variabledict[jv]
			except KeyError:
				logging.debug('Trying to save state of {0} but it was not found within database'.format(jv))
				pass

		# save parameters for future updates
		self.type = u'text'
		self.formatstring = formatstring
		self.variables = variables
		self.fontpkg = fontpkg
		self.varwidth = varwidth
		self.just = just
		self.specifiedsize = specifiedsize

		(fx,fy) = fontpkg['size']
		cx = 0
		cy = 0
		cw = 0

		msg = self.evaltext(formatstring, variables)
		# initialize image

		# If the evaluated text has not changed, skip processing
		if msg == self.curMsg:
			return False
		else:
			self.curMsg = msg

		if msg == '':
			msg = ' '

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
		width, height = specifiedsize
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

				# if this is a character mode display then we need to be careful not to split a character across the character boundary
				elif just == u'centerchar':
					# If the number of chars is even, then we should be ok
					if cx % 2 == 0:
						ax = (maxw-cx)/2
					else:
					# If it's odd though we'll get split so add another character worth of space to the calculation
						ax = (maxw-cx-fx)/2
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

		# if this is a character mode display then we need to be careful not to split a character across the character boundary
		elif just == u'centerchar':
			# If the number of chars is even, then we should be ok
			if cx % 2 == 0:
				ax = (maxw-cx)/2
			else:
			# If it's odd though we'll get split so add another character worth of space to the calculation
				ax = (maxw-cx-fx)/2
		elif just == u'right':
			ax = (maxw-cx)
		self.image.paste(lineimage, (ax, cy))

		self.updatesize()

		return True

	def ttext(self, formatstring, variables, fontpkg, varwidth = True, specifiedsize=8, just=u'left'):
		# Input
		# 	formatstring (unicode) -- format string
		#	variables (unicode array) -- list of variables used to populate formatstring.  Variable values come from variabledict.
		#	fontpkg (font object) -- The font that the message should be rendered in.
		#	varwidth (bool) -- Whether the font should be shown monospaced or with variable pitch
		#	specifiedsize (integer tuple) -- Size to make image if larger than what is requird for the message size
		#	just (unicode) -- Determines how to justify the text horizontally.  Allowed values [ 'left','right','center','centerchar' ]

		# Save variables used for this text widget
		self.currentvardict = { }
		for v in variables:
			try:
				jv = v.split(u'|')[0]
				self.currentvardict[jv] = self.variabledict[jv]
			except KeyError:
				logging.debug('Trying to save state of {0} but it was not found within database'.format(jv))
				pass

		# save parameters for future updates
		self.type = u'ttext'
		self.formatstring = formatstring
		self.variables = variables
		self.fontpkg = fontpkg
		self.varwidth = varwidth
		self.just = just
		self.specifiedsize = specifiedsize

		msg = self.evaltext(formatstring, variables)
		# initialize image

		# If the evaluated text has not changed, skip processing
		if msg == self.curMsg:
			return False
		else:
			self.curMsg = msg

		if msg == '':
			msg = ' '

		maxw, maxh = self.fontpkg.getsize(msg)
		cx = maxw
		textimage = Image.new("1", (maxw, maxh), 0)

		# msglines = msg.split('\n')
		# maxw = 0
		# for line in msglines:
		# 	if maxw < len(line):
		# 		maxw = len(line)
		# maxw = maxw * fx
		# maxh = len(msglines) * fy

		# If a size was provided that is larger than what is required to display the text
		# expand the image size as appropriate
		width, height = specifiedsize
		maxw = maxw if maxw > width else width
		maxh = maxh if maxh > height else height
		self.image = Image.new("1", (maxw, maxh), 0)

		draw = ImageDraw.Draw(textimage)
		draw.text( (0,0), msg, font=self.fontpkg, fill='white')
		del draw
		# # resize to exact requirement of message
		# self.image.crop((0,0,cx-1, cy+fy))

		# Place last line into image
		if just == u'left':
			ax = 0
		elif just == u'center':
			ax = (maxw-cx)/2

		# if this is a character mode display then we need to be careful not to split a character across the character boundary
		elif just == u'centerchar':
			# If the number of chars is even, then we should be ok
			if cx % 2 == 0:
				ax = (maxw-cx)/2
			else:
			# If it's odd though we'll get split so add another character worth of space to the calculation
				ax = (maxw-cx-fx)/2
		elif just == u'right':
			ax = (maxw-cx)
		self.image.paste(textimage, (ax, 0))

		self.updatesize()

		return True


	# Image widget function
	def imagewidget(self, image, size=(0,0)):
		# Input
		#	image (Image object)-- image to place within widget
		#	size (integer tuple) -- size of widget.  If not provided then size will be the same as the provided image

		self.image = image.copy()
		self.type = 'image'

		width, height = size

		# If either dimension is empty, take the dimension from the actual image
		if not width:
			width = self.image.size[0]
		if not height:
			height = self.image.size[1]

		# Resize image
		self.image = self.image.crop( (0,0,width,height))

		self.updatesize()

		return True

	# PROGRESSBAR widget function
	def progressbar(self, value, rangeval, size, style=u'square'):
		# Input
		#	value (numeric) -- Value of the variable showing progress.
		#	rangeval (numeric tuple) -- Range of possible values.  Used to calculate percentage complete.
		#	size (number tuple) -- width and height to draw progress bar
		#	style (unicode) -- Sets the style of the progress bar.  Allowed values [ 'rounded', 'square' ]

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

		# Save variables used for this progressbar widget
		self.currentvardict = { }
		for sv in self.variables:
			self.currentvardict[sv] = self.variabledict[sv]

		width, height = size

		# correct values if needed
		if rvhigh < rvlow:
			t = rvlow
			rvlow = rvhigh
			rvhigh = t

		if v < rvlow :
			logging.debug("v out of range with value {0}.  Should have been between {1} and {2}".format(v,rvlow,rvhigh))
			v = rvlow
		if v > rvhigh :
			logging.debug("v out of range with value {0}.  Should have been between {1} and {2}".format(v,rvlow,rvhigh))
			v = rvhigh

		try:
			percent = (v - rvlow) / float((rvhigh - rvlow))
		except ZeroDivisionError:
			percent = 0

		# If the evaluated value has not changed, skip processing
		if percent == self.curMsg:
			return False
		else:
			self.curMsg = percent

		# make image to place progress bar
		self.image = Image.new("1", size, 0)

		if style == u'square':
			draw = ImageDraw.Draw(self.image)
			if height > 2:
				draw.line( (0,0,0,height-1),1)
				for i in range (0,int((width-2)*percent)):
					draw.line( (i+1,0,i+1,height-1),1)
				for i in range (int((width-2)*percent), width-2):
					self.image.putpixel((i+1,0), 1)
					self.image.putpixel((i+1,height-1), 1)
				draw.line( (width-1,0,width-1,height-1),1)
			else:
				for i in range (0,int((width)*percent)):
					draw.line( (i,0,i,height-1),1)


		self.updatesize()

		# Save parameters for update
		self.value = value
		self.rangeval = rangeval
		self.style = style
		self.type = 'progressbar'

		return True

	# PROGRESSBAR widget function
	def progressimagebar(self, maskimage, value, rangeval, direction='right'):
		# Input
		#	image (Image) -- The image to fill for the progress bar.  Must have a transparent region to fill!
		#	value (numeric) -- Value of the variable showing progress.
		#	rangeval (numeric tuple) -- Range of possible values.  Used to calculate percentage complete.
		#	direction (unicode) -- The direction to fill towards.  Allowed values ['right', 'left', 'up', 'down']
		#	style (unicode) -- Sets the style of the progress bar.  Allowed values [ 'rounded', 'square' ]

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

		# Save variables used for this progressbar widget
		self.currentvardict = { }
		for sv in self.variables:
			self.currentvardict[sv] = self.variabledict[sv]


		# correct values if needed
		if rvhigh < rvlow:
			t = rvlow
			rvlow = rvhigh
			rvhigh = t

		if v < rvlow :
			logging.debug("v out of range with value {0}.  Should have been between {1} and {2}".format(v,rvlow,rvhigh))
			v = rvlow
		if v > rvhigh :
			logging.debug("v out of range with value {0}.  Should have been between {1} and {2}".format(v,rvlow,rvhigh))
			v = rvhigh

		percent = (v - rvlow) / float((rvhigh - rvlow))

		# If the evaluated value has not changed, skip processing
		if percent == self.curMsg:
			return False
		else:
			self.curMsg = percent

		# make a copy of the image to make the progress bar
		self.image = maskimage.copy()
		width, height = self.image.size

		if direction in ['left','right']:
			bheight = self.image.size[1]
			bwidth = int(width*percent)
		elif direction in ['up','down']:
			bheight = int(height*percent)
			bwidth = self.image.size[0]
		else:
			logging.warning('Direction value invalid.  Defaulting to left')
			bwidth = self.image.size[0]*percent
			bheight = self.image.size[1]

		background = Image.new("1", (width, height),0)

		if bwidth > 0 and bheight > 0:
			if direction in ['right']:
				background.paste(Image.new("1", (bwidth, bheight), 1), (self.image.size[0]-bwidth,0))
			elif direction in ['up']:
				background.paste(Image.new("1", (bwidth, bheight), 1), (0,self.image.size[1]-bheight))
			else: # ['left', 'down'] or default if bad direction provided
				background.paste(Image.new("1", (bwidth, bheight), 1), (0,0))

		# Combine background with image
		background.paste(self.image, (0,0), self.image)
		self.image = background

		self.updatesize()

		# Save parameters for update
		self.value = value
		self.rangeval = rangeval
		self.direction = direction
		self.maskimage = maskimage
		self.type = 'progressimagebar'

		return True


	# LINE widget function
	def line(self, (x,y), color=1):
		# Input
		#	(x,y) (integer tuple) -- Draw a line from the origin to x,y
		#	color -- color to use for the line

		# Does image exist yet?
		if self.image == None:
			self.image = Image.new("1", (x+1, y+1), 0)
		else:
			# Is image big enough?
			if self.image.size[0] < x or self.image.size[1] < y:
				self.image.crop(0,0,x,y)

		draw = ImageDraw.Draw(self.image)
		draw.line( (0,0,x,y) ,color)

		self.updatesize()

		# save parameters
		self.xy = (x,y)
		self.color = color

		return True

	# RECTANGLE widget function
	def rectangle(self, (x,y), fill=0, outline=1):
		# Input
		#	(x,y) (integer tuple) -- Bottom left and bottom right of rectangle drawn from origin
		#	color -- color to use for the rectangle

		# Does image exist yet?
		if self.image == None:
			self.image = Image.new("1", (x+1, y+1), 0)
		else:
			# Is image big enough?
			if self.image.size[0] < x or self.image.size[1] < y:
				self.image.crop(0,0,x,y)

		draw = ImageDraw.Draw(self.image)
		draw.rectangle((0,0,x,y),fill, outline)

		self.updatesize()

		# save parameters
		self.xy = (x,y)
		self.fill = fill
		self.outline = outline

		return True

	# POPUP widget function
	def popup(self, widget, dheight, duration=15, pduration=10): # Set up for pop-up display
		# Input
		#	widget (widget) -- Widget to pop up
		#	dheight (integer) -- Sets the height of the window which will get displayed from the canvas
		#	duration (float) -- How long to display the top of the canvas
		#	pduration (float) -- How long to stay popped up

		# If this is the first pass, initialize state variables
		try:
			self.popped
		except:
			self.type = u'popup'
			self.popped = False
			self.end = time.time() + duration
			self.image = widget.image
			self.updatesize()
			self.index = 0

			# Save parameters
			self.widget = widget
			self.dheight = dheight
			self.duration = duration
			self.pduration = pduration

		# Update the widget if needed
		self.widget.update()

		# If we are waiting for a transition
		if self.end > time.time():
			self.image = self.widget.image.crop( (0, self.index, self.widget.size[0], self.index+self.dheight) )
			self.updatesize()
			return True

		if self.popped:
			# Move back into non-popped mode
			if self.index > 0:
				self.index -= 1
			else:
				self.popped = False
				self.end = time.time()+self.duration
		else:
			# Move into popped mode
			if self.index < self.widget.size[1] - self.dheight:
				self.index += 1
			else:
				self.popped = True
				self.end = time.time() + self.pduration

		self.image = self.widget.image.crop( (0, self.index, self.widget.size[0], self.index+self.dheight) )
		self.updatesize()

		return True

	# SCROLL widget function
	def scroll(self, widget, direction=u'left', distance=1, speed=1, gap=20, hesitatetype=u'onloop', hesitatetime=2, threshold=0, reset=False): # Set up for scrolling
		# Input
		#	widget (widget) -- Widget to scroll
		#	direction (unicode) -- What direction to scroll ['left', 'right','up','down']
		#	hesitatetype (unicode) -- the type of hesitation to use ['none', 'onstart', 'onloop']
		#	hesitatetime (float) -- how long in seconds to hesistate
		#	threshold (integer) -- scroll only if widget larger than threshold

		retval = False
		if reset:
			self.start = time.time()
			if hesitatetype not in ['onstart', 'onloop']:
				self.end = 0
			else:
				self.end = self.start + hesitatetime

		# If this is the first pass, initialize state variables
		try:
			self.type
			self.end
		except:
			retval = True
			self.type= u'scroll'
			self.start = time.time()
			if hesitatetype not in ['onstart', 'onloop']:
				self.end = 0
			else:
				self.end = self.start + hesitatetime
			self.hindex = 0 # Horizontal index
			self.vindex = 0 # Vertical index
			self.updatesize()

			self.shouldscroll = False

			# Save parameters
			self.widget = widget
			direction = direction.lower()
			self.direction = direction
			self.distance = distance
			self.speed = speed # Used to slow scroll.  Speed is an integer that tells how many calls to scroll before an update is made
			self.speedcount = speed
			self.gap = gap
			hesitatetype = hesitatetype.lower()
			self.hesitatetype = hesitatetype
			self.hesitatetime = hesitatetime
			self.threshold = threshold

			# Make sure direction is valid.  Set to 'left' if not.
			if self.direction not in [u'left',u'right',u'up',u'down']:
				self.direction = u'left'

			# Set height and width for expanded image
			self.eheight = self.widget.size[1] if self.direction in [u'left',u'right'] else self.widget.size[1]+gap
			self.ewidth = self.widget.size[0]+gap if self.direction in [u'left',u'right'] else self.widget.size[0]

			# Update image using current index values
			self.expanded_image = self.widget.image.copy().crop( (0,0,self.ewidth,self.eheight) )
			self.image = self.expanded_image.copy()
			self.image.paste( self.widget.image, (0,0) )

			# Check to see if scrolling is needed
			if self.direction in ['left','right']:
				if self.widget.size[0] > self.threshold:
					self.shouldscroll = True
				else:
					self.shouldscroll = False
			elif self.direction in ['up','down']:
				if self.widget.height > self.threshold:
					self.shouldscroll = True
				else:
					self.shouldscroll = False
			return True

			# # Expand canvas
			# if self.shouldscroll:
			# 	if direction in ['left','right']:
			# 		self.image = Image.new("1", (self.widget.size[0]+gap, self.widget.size[1]))
			# 		self.image.paste(self.widget.image, (0,0))
			# 		self.updatesize()
			# 	elif direction in ['up','down']:
			# 		self.image = Image.new("1", (self.widget.size[0], self.widget.size[1]+gap))
			# 		self.image.paste(self.widget.image, (0,0))
			# 		self.updatesize()


		# If the widget has changed or a reset was commanded then reset the scroll to the starting position
		if self.widget.update(reset) or reset:
			# something has changed
			retval = True
			self.start = time.time()
			if hesitatetype not in ['onstart', 'onloop']:
				self.end = 0
			else:
				self.end = self.start + hesitatetime
			self.image = self.widget.image.copy()
			self.hindex = 0
			self.vindex = 0
			self.updatesize()

			# Reset speed count
			self.speedcount = self.speed

			# Set height and width for expanded image
			self.eheight = self.widget.size[1] if self.direction in [u'left',u'right'] else self.widget.size[1]+gap
			self.ewidth = self.widget.size[0]+gap if self.direction in [u'left',u'right'] else self.widget.size[0]

			# Update image using current index values
			self.expanded_image = self.widget.image.copy().crop( (0,0,self.ewidth,self.eheight) )
			self.image = self.expanded_image.copy()
			self.image.paste( self.widget.image, (0,0) )

			# Check to see if scrolling is needed
			if self.direction in ['left','right']:
				if self.widget.size[0] > self.threshold:
					self.shouldscroll = True
				else:
					self.shouldscroll = False
			elif self.direction in ['up','down']:
				if self.widget.height > self.threshold:
					self.shouldscroll = True
				else:
					self.shouldscroll = False
			return True

		# Decrement the speed counter and test to see if this update should be skipped
		self.speedcount -= 1
		speeddelay = True
		if not self.speedcount:
			speeddelay = False
			self.speedcount = self.speed

		# If Hesitate is needed or scrolling is not needed, return
		if self.end > time.time() or not self.shouldscroll or speeddelay:
			return retval

		if direction == u'left':
			self.hindex += distance
			if self.hindex >= self.ewidth:
				self.hindex = 0
		elif direction == u'right':
			self.hindex -= distance
			if self.hindex < 0:
				self.hindex = self.ewidth
		elif direction == u'up':
			self.vindex += distance
			if self.vindex >= self.eheight:
				self.vindex = 0
		elif direction == u'down':
			self.vindex -= distance
			if self.vindex < 0:
				self.vindex = self.eheight

		# Reset expanded_image
		self.expanded_image = self.widget.image.copy().crop( (0,0,self.ewidth,self.eheight) )

		# Update image using current index values
		if direction in [u'left',u'right']:
			hregion = self.expanded_image.crop( (0,0,self.hindex,self.eheight) )
			hbody = self.expanded_image.crop( (self.hindex,0,self.ewidth,self.eheight) )
			self.image.paste( hbody, (0,0) )
			self.image.paste( hregion, (self.ewidth - self.hindex, 0) )
		elif direction in [u'up',u'down']:
			vregion = expanded_image.crop( (0,0,self.ewidth,self.vindex) )
			vbody = expanded_image.crop( (0,self.vindex,self.ewidth,self.eheight) )
			self.image.paste( vbody, (0,0) )
			self.image.paste( vregion, (0, self.eheight - self.vindex) )

		if hesitatetype == u'onloop' and ( (self.hindex == 0 and self.direction in [u'left',u'right']) or (self.vindex == 0 and self.direction in [u'up',u'down'])):
			self.start = time.time()
			self.end = self.start + hesitatetime

		return True

class gwidgetText(gwidget):
	def __init__(self, formatstring, fontpkg, variabledict={ }, variables =[], varwidth = True, size=(0,0), just=u'left'):
		super(gwidgetText, self).__init__(variabledict)
		self.text(formatstring, variables, fontpkg, varwidth, size, just)

class gwidgetTText(gwidget):
	def __init__(self, formatstring, fontpkg, variabledict={ }, variables =[], varwidth = True, size=8, just=u'left'):
		super(gwidgetTText, self).__init__(variabledict)
		self.ttext(formatstring, variables, fontpkg, varwidth, size, just)

class gwidgetProgressBar(gwidget):
	def __init__(self, value, rangeval, size, style=u'square',variabledict={ }):
		super(gwidgetProgressBar, self).__init__(variabledict)
		self.progressbar(value, rangeval, size, style)

class gwidgetProgressImageBar(gwidget):
	def __init__(self, maskimage, value, rangeval, direction=u'left',variabledict={ }):
		super(gwidgetProgressImageBar, self).__init__(variabledict)
		self.progressimagebar(maskimage, value, rangeval, direction)

class gwidgetImage(gwidget):
	def __init__(self, image, size=(0,0)):
		super(gwidgetImage, self).__init__()
		self.imagewidget(image, size)

class gwidgetLine(gwidget):
	def __init__(self, (x,y), color=1):
		super(gwidgetLine, self).__init__()
		self.line((x,y), color)

class gwidgetRectangle(gwidget):
	def __init__(self, (x,y), fill=0, outline=1):
		super(gwidgetRectangle, self).__init__()
		self.rectangle((x,y), fill, outline)

class gwidgetCanvas(gwidget):
	def __init__(self, (w,h)):
		super(gwidgetCanvas, self).__init__()
		self.canvas((w,h))

class gwidgetPopup(gwidget):
	def __init__(self, widget, dheight, duration=15, pduration=10):
		super(gwidgetPopup, self).__init__()
		self.popup(widget, dheight, duration, pduration)

class gwidgetScroll(gwidget):
	def __init__(self, widget, direction=u'left', distance=1, speed=1, gap=20, hesitatetype=u'onloop', hesitatetime=2, threshold=0, reset=False):
		super(gwidgetScroll, self).__init__()
		self.scroll(widget, direction, distance, speed, gap, hesitatetype, hesitatetime,threshold,reset)


class sequence(object): # Holds a sequence of widgets to display on the screen in turn
	def __init__(self, name, conditional, db, dbprevious, coolingperiod, minimum, coordinates): # initialize class
		# Input
		#	conditional (unicode) -- a string containing an evaluable boolean logic statement which determines whether the sequence is active
		#	db (dict) -- A dictionary that points to system variable db
		#	dbp (dict) -- A dictionary that points to the previous state of the system variable db
		#	coolingperiod (float) -- Amount of time to wait before a sequence can be displayed again

		self.widgets = []					# Array to hold widget list
		self.name = name			# Name of sequence
		self.conditional = conditional		# Sequence conditional.  Must be true for sequence to be displayed
		self.coordinates = coordinates		# Offset from origin to place any canvas in this sequence
		self.db = db						# System variable db
		self.dbp = dbprevious				# System variable db for previous values (to allow system to detect changes)
		self.coolingperiod = coolingperiod	# Wait for coolingperiod seconds before allowing this sequence to be displayed again
		self.coolingexpires = 0				# Variable to mark the time that the sequence exits its coolingperiod
		self.end = 0						# Variable to mark the time that the current widget expires
		self.currentwidget = 0				# Marks the index of the current widget
		self.minimum = minimum				# When this sequence activates, keep in active for a least minimum seconds
		self.expires = 0					# Time that this sequence can be allowed to go inactive

		return

	def add(self, widget, duration, conditional): # Add a widget to the display sequence
		# Input
		#	widget (widget) -- The widget to add to the display seqeunce
		#	duration (float) -- How long in seconds to display this widget
		#	conditional (unicode) -- A string containing an evaluable boolean logic statement which determines whether the widget should be included in the sequence

		# If this is the first widget then set the duration it should be displayed
		if len(self.widgets) == 0:
			self.end = time.time() + duration

		# Add widget to sequence
		self.widgets.append( (widget, duration, conditional) )

	def evalconditional(self, conditional): # Evaluate the conditional statement
		# Input
		#	conditional (unicode) -- A string containing an evaluable boolean logic statement

		# This is NOT a safe routine.  Make sure that any input sent to this function is from a trusted source

		db = self.db
		dbp = self.dbp

		try:
			return eval(conditional)
		except:
			# Could not evaluate conditional so returning False
			return False

 	def get(self, restart=False): # Return current widget (or None) if none are active
		# Input
		#	restart (bool) -- If True resets the sequence to the first widget on the list

		# Evaluate sequence conditional and check for cooling period.
		if self.expires < time.time() and (not self.evalconditional(self.conditional) or self.coolingexpires > time.time()):
			return None

		# If the condition is true and the sequence has already passed it's minimum time reset the timer
		if self.expires < time.time() and self.minimum > 0:
			self.expires = time.time() + self.minimum

		widget, duration, conditional = self.widgets[self.currentwidget]

		# Check and respond to restart
		if restart:
			self.currentwidget = 0
			self.coolingexpires = 0
			widget, duration, conditional = self.widgets[self.currentwidget]
			self.end = duration + time.time()

		# See if current widget has expired (or has gone inactive).
		if self.end < time.time() or not self.evalconditional(conditional):
			# If it has, iterate through list to find the next active widget
			self.currentwidget += 1
			if self.currentwidget >= len(self.widgets):
				self.currentwidget = 0

			for i in range(len(self.widgets)):
				widget, duration, conditional = self.widgets[self.currentwidget]
				if self.evalconditional(conditional):
					self.end = duration + time.time()
					widget.update(True)
					return widget
				else:
					self.currentwidget += 1
					if self.currentwidget >= len(self.widgets):
						self.currentwidget = 0

			# If you go through the whole list without finding an active widget then return None
			return None
		else:
			# If current widget is active and has not expired, then return it
			widget.update()
			return widget

class display_controller(object):
	def __init__(self, size):
		self.sequences = []
		self.size = size

	def load(self, file, db, dbp,): # Load config file and initialize sequences
		# Input
		#	file (unicode) -- file that contains a valid display configuration

		self.file = file
		self.db = db
		self.dbp = dbp

		self.pages = None
		self.widgets = { }
		self.sequences = []
		self.errwidgets = { }
		self.defaultfontpkg = None

		logging.debug("Loading {0} as page file".format(file))
		# If page file provided, try to load provided file on top of default pages file
		try:
			newpages = imp.load_source('pages', file)
				# Need to have the following structures to be valid
			self.pages = newpages
		except:
			logging.critical('Page file {0} was unable to be loaded'.format(file))
			self.pages = None
			raise

		# Load fonts
		try:
			for k,v in self.pages.FONTS.iteritems():
				fontfile = v['file'] if 'file' in v else ''
				isdefault = v['default'] if 'default' in v else False
				if fontfile:
	#				try:
#					logging.debug('Loading font {0}'.format(k))
					v['fontpkg'] = fonts.bmfont.bmfont(fontfile).fontpkg
					if isdefault:
						self.defaultfontpkg = v['fontpkg']
	#				except:
						# Font load failed
	#					logging.critical('Attempt to load font {0} failed'.format(fontfile))
				else:
					logging.critical('Expected a font file for {0} but none provided'.format(k))
		except AttributeError:
			# No fonts specified
			pass

		# Load truetype fonts
		try:
			for k,v in self.pages.TRUETYPE_FONTS.iteritems():
				fontfile = v['file'] if 'file' in v else ''
				fontsize = v['size'] if 'size' in v else 8
				if fontfile:
#					logging.debug('Loading font {0}'.format(k))
					try:
						v['fontpkg'] = ImageFont.truetype(font=fontfile, size=fontsize)
					except IOError:
						logging.critical('Font {0} not found'.format(fontfile))
				else:
					logging.critical('Expected a font file for {0} but none provided'.format(k))
		except AttributeError:
			# No fonts specified
			pass


		if self.defaultfontpkg is None:
			logging.critical('Must specify a default font.  Exiting...')
			raise RuntimeError('Must specify a default font.  Exiting...')

		self.defaultwidget = gwidgetText('No active widgets', self.defaultfontpkg, {},[], True)

		try:
			# Load images
			for k,v in self.pages.IMAGES.iteritems():
				imagefile = v['file'] if 'file' in v else ''
				if imagefile:
					logging.debug('Loading image {0}'.format(k))
					try:
						i_path = os.path.join(os.path.dirname(__file__), 'images', imagefile)
						v['image'] = Image.open(i_path)
					except IOError:
						logging.critical('Failed to open file {0} for image {1}'.format(i_path, k))
				else:
					logging.critical('Expected that a filename for image {0} would be provided'.format(k))
		except AttributeError:
			# No Images specified
			pass

		# Add type field to CANVAS widgets
		for k,v in self.pages.CANVASES.iteritems():
			v['type'] = 'canvas'

		self.loadwidgets(self.pages.WIDGETS)
		self.loadwidgets(self.pages.CANVASES)
		self.loadsequences(self.pages.SEQUENCES)



	def loadwidgets(self, pageWidgets): # Load widgets. Return any widgets that could not be loaded because a widget contained within it was not found

		# Load widgets
		for k,v in pageWidgets.iteritems():
			typeval = v['type'].lower() if 'type' in v else ''

#			logging.debug('Loading widget {0}'.format(k))

			if typeval not in ['canvas', 'text', 'ttext', 'progressbar', 'progressimagebar', 'line', 'rectangle', 'image' ]:
				if typeval:
					logging.warning('Attempted to add widget {0} with an unsupported widget type {1}.  Skipping...'.format(k,typeval))
				else:
					logging.warning('Attempted to add widget {0} without a type specified.  Skipping...'.format(k))
				continue

			# type if valid
			if typeval == 'text':
				format = v['format'] if 'format' in v else ''
				variables = v['variables'] if 'variables' in v else []
				font = v['font'] if 'font' in v else ''
				just = v['just'] if 'just' in v else 'left'
				size = v['size'] if 'size' in v else (0,0)
				varwidth = v['varwidth'] if 'varwidth' in v else True
				fontentry = self.pages.FONTS[font] if font in self.pages.FONTS else { }
				fontpkg = fontentry['fontpkg'] if 'fontpkg' in fontentry else None
				if not format or not fontpkg:
					logging.warning('Attempted to add text widget {0} without a format or font specified.  Skipping...'.format(k))
					continue
				widget = gwidgetText(format, fontpkg, self.db, variables, varwidth, size, just)
			elif typeval == 'ttext':
				format = v['format'] if 'format' in v else ''
				variables = v['variables'] if 'variables' in v else []
				font = v['font'] if 'font' in v else ''
				just = v['just'] if 'just' in v else 'left'
				size = v['size'] if 'size' in v else (0,0)
				varwidth = v['varwidth'] if 'varwidth' in v else True
				fontentry = self.pages.TRUETYPE_FONTS[font] if font in self.pages.TRUETYPE_FONTS else { }
				fontpkg = fontentry['fontpkg'] if 'fontpkg' in fontentry else None
				if not format or not fontpkg:
					logging.warning('Attempted to add text widget {0} without a format or font specified.  Skipping...'.format(k))
					continue
				widget = gwidgetTText(format, fontpkg, self.db, variables, varwidth, size, just)
			elif typeval == 'progressbar':
				value = v['value'] if 'value' in v else None
				rangeval = v['rangeval'] if 'rangeval' in v else (0,100)
				size = v['size'] if 'size' in v else None
				style = v['style'] if 'style' in v else 'square'
				if not value or not size:
					logging.warning('Attempted to add progressbar widget {0} without a value or size.  Skipping...'.format(k))
					continue
				widget = gwidgetProgressBar(value, rangeval, size, style, self.db)
			elif typeval == 'progressimagebar':
				imagename = v['image'] if 'image' in v else ''
				maskentry = self.pages.IMAGES[imagename] if imagename in self.pages.IMAGES else { }
				maskimage = maskentry['image'] if 'image' in maskentry else None
				value = v['value'] if 'value' in v else None
				rangeval = v['rangeval'] if 'rangeval' in v else (0,100)
				direction = v['direction'] if 'direction' in v else 'left'
				if not value or not maskimage:
					logging.warning('Attempted to add progressimagebar widget {0} without a value or maskimage.  Skipping...'.format(k))
					continue
				widget = gwidgetProgressImageBar(maskimage, value, rangeval, direction, self.db)
			elif typeval == 'image':
				imagename = v['image'] if 'image' in v else ''
				entry = self.pages.IMAGES[imagename] if imagename in self.pages.IMAGES else { }
				image = entry['image'] if 'image' in entry else None
				size = v['size'] if 'size' in v else (0,0)
				if not image:
					logging.warning('Attempted to add image widget {0} without an image.  Skipping...'.format(k))
					continue
				widget = gwidgetImage(image, size)
			elif typeval == 'line':
				point = v['point'] if 'point' in v else None
				color = v['color'] if 'color' in v else 1
				if not point:
					logging.warning('Attempted to add line widget {0} without a point.  Skipping...'.format(k))
					continue
				widget = gwidgetLine(point, color)
				size = widget.size
			elif typeval == 'rectangle':
				point = v['point'] if 'point' in v else None
				fill = v['fill'] if 'fill' in v else 0
				outline = v['outline'] if 'outline' in v else 1
				if not point:
					logging.warning('Attempted to add rectangle widget {0} without a point.  Skipping...'.format(k))
					continue
				widget = gwidgetRectangle(point, fill, outline)
				size = widget.size
			elif typeval == 'canvas':
				widgetentries = v['widgets'] if 'widgets' in v else []
				size = v['size'] if 'size' in v else None

				if not size:
					logging.warning('Attempted to add create canvas {0} without a size.  Skipping...'.format(k))
					continue

				widget = gwidgetCanvas(size)
				for wtuple in widgetentries:
					try:
						 wname, x, y = wtuple
					except ValueError:
						logging.warning('Canvas {0} included widget that does not have the appropriate number of parameters. Skipping widget...'.format(k))
						continue
					if type(x) is not int or type(y) is not int:
						logging.warning('Canvas {0} included a widget with an invalid point to place the widget. Skipping widget...'.format(k))
						continue

					widtoadd = self.widgets[wname] if wname in self.widgets else None
					if not widtoadd:
						logging.warning('Canvas {0} attempted to add widget {1} but it was not found in the widget list'.format(k, wname))
						continue

					widget.add(widtoadd, (x,y))

			# Add effect if requested
			effect = v['effect'] if 'effect' in v else None
			if effect != None:

				try:
					etype = effect[0]
#					logging.debug('Adding effect {0} to {1} which is currently size {2}'.format(etype,k,widget.size))
				except IndexError:
					logging.debug('Tried to add effect {0} but effect type not specified'.format(k))
					etype = ''
				if etype in ['scroll', 'popup']:
					if etype == 'scroll':
						widget = gwidgetScroll(widget, *effect[1:])
#						logging.debug("Scroll added with widget size {0}".format(widget.image.size))

						# if the actual size of the widget is greater than the requested size then place the scroll object in a canvas to limit its display size
						tw, th = size

						# If size is (0,0) then there was no specified size and this step should be skipped
						if not (tw == 0 and th == 0):
							if widget.size[0] > tw or widget.size[1] > th:
								cwidget = gwidgetCanvas(size)
								cwidget.add(widget, (0,0))
								widget = cwidget

					elif etype == 'popup':
						widget = gwidgetPopup(widget, *effect[1:])
				else:
					if etype:
						logging.warning('Attempted to add an unrecognized effect ({0}) to widget {1}.  Ignoring...'.format(etype,k))
					else:
						logging.warning('Attempted to an effect to widget {0} without specifying the details.  Ignoring...'.format(k))
			else:
				# if the actual size of the widget is greater than the requested size and no effect has been requested, resize the widget to fit
				tw, th = size

				# If size is (0,0) then there was no specified size and this step should be skipped
				if not (tw == 0 and th == 0):
					if widget.size[0] > tw or widget.size[1] > th:
						widget.image = widget.image.crop( (0,0,tw,th) )
						widget.updatesize()

			# Add widget to widget list
			self.widgets[k] = widget

	def next(self): # Compute and return the next image to display
		active = []
		img = None

		for s in self.sequences:
			w = s.get()
			if w != None:
				active.append((w,s.coordinates))
				# If sequence does not have an active coolingperiod timer set then set one
				if s.coolingexpires < time.time():
					s.coolingexpires = s.coolingperiod + time.time()
		img = None
		for wid in active:
			if not img:
				img = Image.new("1", self.size)

			# If more than one sequence is active, paste together.
			w = wid[0].image.size[0]+wid[1][0] if wid[0].image.size[0]+wid[1][0] > img.size[0] else img.size[0]
			h = wid[0].image.size[1]+wid[1][1] if wid[0].image.size[1]+wid[1][1] > img.size[1] else img.size[1]
			if w > img.size[0] or h > img.size[1]:
				img = img.crop((0,0,w,h))

			img.paste(wid[0].image,wid[1])

		if img is None:
			try:
				img = self.defaultwidget.image.copy()
			except AttributeError:
				# This should only happen if next is called before load
				img = Image.new("1", self.size)

		if img is not None:
			# Limit returned image to the display controllers size
			x,y = self.size
			img = img.crop( (0,0,x,y))

		# Return next valid image
		return img

	def loadsequences(self, sequences):

		for value in sequences:

			conditional = value['conditional'] if 'conditional' in value else 'True'
			coolingperiod = value['coolingperiod'] if 'coolingperiod' in value else 0
			minimum = value['minimum'] if 'minimum' in value else 0
			name = value['name'] if 'name' in value else 'name not provided'
			coordinates = value['coordinates'] if 'coordinates' in value else (0,0)

#			logging.debug('Loading sequence {0}'.format(name))

			newseq = sequence(name,conditional,self.db,self.dbp, coolingperiod, minimum, coordinates)
			self.sequences.append(newseq)
			canvases = value['canvases'] if 'canvases' in value else []
			if canvases:
				for c in canvases:
					cname = c['name'] if 'name' in c else ''
					duration = c['duration'] if 'duration' in c else 0
					cconditional = c['conditional'] if 'conditional' in c else 'True'
					if cname and duration and cconditional:
						widget = self.widgets[cname] if cname in self.widgets else None
						if widget:
							newseq.add(widget,duration, cconditional)
						else:
							logging.warning('Trying to add widget {0} to sequence {1} but widget was not found'.format(cname, name))

			# If no canvases were added to the sequence, remove it
			if len(newseq.widgets) == 0:
				logging.warning('Unable to create sequence {0}.  No widgets'.format(name))
				del self.sequences[-1]


def printsequences(seq):
	for s in seq:
		print "SEQUENCE"
		print '  Canvases      : {0}'.format(len(s.widgets))
		print '  Conditional   : {0}'.format(s.conditional)
		print '  Cooling Period: {0}'.format(s.coolingperiod)

def processevent(events, starttime, prepost, db, dbp):
	for evnt in events:
		t,var,val = evnt

		if time.time() - starttime >= t:
			if prepost in ['pre']:
				db[var] = val
			elif prepost in ['post']:
				dbp[var] = val

if __name__ == '__main__':

	import graphics as g
	import moment

	starttime = time.time()
	elapsed = int(time.time()-starttime)
	timepos = time.strftime(u"%-M:%S", time.gmtime(int(elapsed))) + "/" + time.strftime(u"%-M:%S", time.gmtime(int(254)))

	logging.basicConfig(format=u'%(asctime)s:%(levelname)s:%(message)s', level=logging.DEBUG)

	db = {
			'actPlayer':'mpd',
			'playlist_position':1,
			'playlist_length':5,
	 		'title':"Nicotine & Gravy",
			'artist':"Beck",
			'album':'Midnight Vultures',
			'elapsed':0,
			'length':400,
			'volume':50,
			'stream':'Not webradio',
			'utc': 	moment.utcnow(),
			'outside_temp_formatted':'46\xb0F',
			'outside_temp_max':72,
			'outside_temp_min':48,
			'outside_conditions':'Windy',
			'system_temp_formatted':'98\xb0C',
			'state':'play',
			'system_tempc':81.0
		}

	dbp = {
			'actPlayer':'mpd',
			'playlist_position':1,
			'playlist_length':5,
	 		'title':"Nicotine & Gravy",
			'artist':"Beck",
			'album':'Midnight Vultures',
			'elapsed':0,
			'length':400,
			'volume':50,
			'stream':'Not webradio',
			'utc': 	moment.utcnow(),
			'outside_temp_formatted':'46\xb0F',
			'outside_temp_max':72,
			'outside_temp_min':48,
			'outside_conditions':'Windy',
			'system_temp_formatted':'98\xb0C',
			'state':'play',
			'system_tempc':81.0
		}

	events = [
		(10, 'title', 'Mixed Bizness'),
		(20, 'volume', 80),
		(30, 'title', 'I Never Loved a Man (The Way I Love You)'),
		(30, 'artist', 'Aretha Franklin'),
		(30, 'album', 'The Queen Of Soul'),
		(60, 'state', 'stop'),
		(80, 'state', 'play'),
		(90, 'title', 'Do Right Woman, Do Right Man'),
		(110, 'volume', 100),
		(130, 'state', 'play' )
	]

	f_path = os.path.join(os.path.dirname(__file__), 'pages_test.py')
	dc = display_controller((80, 16))
	dc.load(f_path, db,dbp )

	starttime = time.time()
	elapsed = int(time.time()-starttime)
	timepos = time.strftime(u"%-M:%S", time.gmtime(int(elapsed))) + "/" + time.strftime(u"%-M:%S", time.gmtime(int(254)))

	starttime=time.time()
	while True:
		db['elapsed'] = int(time.time()-starttime)
		# timepos = time.strftime(u"%-M:%S", time.gmtime(int(elapsed))) + "/" + time.strftime(u"%-M:%S", time.gmtime(int(254)))
		# current_time = moment.utcnow().timezone('US/Eastern').strftime(u"%H:%M:%S").strip().decode()
		# db['elapsed_formatted'] = timepos
		# db['time_formatted'] = current_time

		processevent(events, starttime, 'pre', db, dbp)
		img = dc.next()
		processevent(events, starttime, 'post', db, dbp)
		frame = g.getframe( img, 0,0, 80,16 )
		g.show( frame, 80, int(math.ceil(16/8.0)))
		time.sleep(.1)
