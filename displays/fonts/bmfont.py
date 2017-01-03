#!/usr/bin/python
# coding: UTF-8

# Font class that uses bmfont style font definitions
# Warning:  Really only written to support fonts for an LCD/OLED displays
#           Not tested beyond that use case
# Written by: Ron Ritchey

from PIL import Image
import logging
import os

class bmfont:

	def __init__(self,fontfile):
		self.fontpkg = { } # Holds an image of each font character
		self.imglookup = { } # Holds image key to perform a reverse lookup of an image back to the character it represents
		self.chardata = { } # Holds position and size data for each character on sprite sheet

		# Read file
		try:
			f_path = os.path.join(os.path.dirname(__file__), fontfile)
			print "Loading font from {0}".format(f_path)
			with open(f_path, 'r') as f:

				# Read info line of font file
				line = f.readline().decode('utf-8')

				# Check for expected start value
				if u'info' not in line:
					# Bad file
					logging.debug(u'Font file {0} is not readable.  Info line not found.'.format(fontfile))
					raise SyntaxWarning(u'Font file is not readable')

				# Parse info line of font file
				d = self.parsefontline(line, u'info')
				self.face = d[u'face'] if u'face' in d else u''
				self.bold = bool(int(d[u'bold'])) if u'bold' in d else False
				self.italic = bool(int(d[u'italic'])) if u'italic' in d else False

				# Read common line
				line = f.readline().decode('utf-8')

				# Check for expected start value
				if u'common' not in line:
					# Bad file
					logging.debug(u'Font file {0} is not readable. Common line not found.'.format(fontfile))
					raise SyntaxWarning(u'Font file is not readable')

				# Parse common line of font file
				d = self.parsefontline(line, u'common')
				self.lineHeight = int(d[u'lineHeight']) if u'lineHeight' in d else 0
				self.scaleW = int(d[u'scaleW']) if u'scaleW' in d else 0
				self.scaleH = int(d[u'scaleH']) if u'scaleH' in d else 0

				# Read page line
				line = f.readline().decode('utf-8')

				# Check for expected start value
				if u'page' not in line:
					# Bad file
					logging.debug(u'Font file {0} is not readable. Page line not found.'.format(fontfile))
					raise SyntaxWarning(u'Font file is not readable')

				# Parse common line of font file
				d = self.parsefontline(line, u'page')
				self.file = d[u'file'].strip() if u'file' in d else u''
				# Remove any quotation marks
				if (self.file.startswith('"') | self.file.startswith("'")) and (self.file.endswith('"') | self.file.endswith("'")):
					self.file = self.file[1:-1]

				# Read chars line
				line = f.readline().decode('utf-8')

				# Check for expected start value
				if u'chars' not in line:
					# Bad file
					logging.debug(u'Font file {0} is not readable. Chars line not found.'.format(fontfile))
					raise SyntaxWarning(u'Font file is not readable')

				# Parse common line of font file
				d = self.parsefontline(line, u'chars')
				self.count = int(d[u'count']) if u'count' in d else 0

				# set meta data about font including size

				maxw = 0 # Will store the maximum character width.  Used to create monospaced output.
				# Now read in the list of characters
				for c in range(0,self.count):

					# Read char line
					line = f.readline().decode('utf-8')

					# Check for expected start value
					if u'char' not in line:
						# Bad file
						logging.debug(u'Font file {0} is not readable. Char line not found.'.format(fontfile))
						raise SyntaxWarning(u'Font file is not readable')

					# Parse common line of font file
					d = self.parsefontline(line, u'char')
					id = int(d[u'id']) if u'id' in d else -1
					if id < 0:
						logging.debug(u'Font file {0} is not readable. Char id missing.'.format(fontfile))
						raise SyntaxWarning(u'Font file is not readable')

					x = int(d[u'x']) if u'x' in d else -1
					y = int(d[u'y']) if u'y' in d else -1
					w = int(d[u'width']) if u'width' in d else -1
					h = int(d[u'height']) if u'height' in d else -1
					xadvance = int(d[u'xadvance']) if u'xadvance' in d else -1
					if x < 0 or y < 0 or w < 0 or h < 0 or xadvance < 0:
						logging.debug(u'Font file {0} is not readable. Char {1} missing value.'.format(fontfile,id))
						raise SyntaxWarning(u'Font file is not readable')

					self.chardata[id] = (x,y,w,h,xadvance)
					if maxw < w:
						maxw = w
				self.fontpkg['size'] = (maxw,self.lineHeight)
		except IOError:
			logging.debug(u'Font file {0} was not found.'.format(fontfile))
			raise IOError

		# try:
		# Load PNG file

		f_path = os.path.join(os.path.dirname(__file__), self.file)
		with Image.open(f_path) as im:

			for k,v in self.chardata.iteritems():
				x,y,w,h,xadvance = v

				# Adjust the width of the character based upon the xadvance field
				img = im.crop( (x,y,x+w,y+h) )

				# Resize to xadvance width
				img = img.crop( (0,0,xadvance,h) )
				self.fontpkg[k] = img
				data = tuple(list(img.convert("1").getdata()))
				self.imglookup[data] = k


		# except IOError:
		# 	print u'Sprite file {0} was not found.'.format(self.file)
		# 	logging.debug(u'Sprite file {0} was not found.'.format(self.file))
		# 	raise IOError

		# Get bitmaps of each character
	def parsefontline(self,line,name):
		d = { }
		# Parse common line of font file
		kvs = line.split(name)[1].split(u' ')
		for i in kvs:
			# If value is empty skip it
			if '=' not in i:
				continue

			# Parse valid entries
			k,v = i.split('=')
			k = k.strip()
			v = v.strip()
			d[k] = v
		return d
