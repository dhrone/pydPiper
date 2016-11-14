#!/usr/bin/python.pydPiper
# coding: UTF-8

# pydPiper service to display music data to LCD and OLED character displays
# Written by: Ron Ritchey

import json, threading, logging, Queue, time, sys, getopt, moment, signal, commands, os, copy, imp, codecs
import pages
import displays
import sources
import pydPiper_config

try:
	import pyowm
except ImportError:
	pass


exitapp = [ False ]

class display_controller(threading.Thread):
	# Receives updates from music_controller and places them onto displays
	def __init__(self, displayqueue, lcd):
		threading.Thread.__init__(self)

		self.daemon = True

		self.displayqueue = displayqueue
		self.lcd = lcd

		self.current_lines = [ ]

		# Load default font
		self.lcd.switchcustomchars(displays.fonts.map.map(u'default'))


	def scrollwindow(self, segment, window, direction, resetscrollposition=False):
		# segment - The segment to compute a window for
		# width - the fixed size of the window.  The value will be truncated if smaller or padded if smaller.
		# direction - 	Which direction to scroll.  Values are left, right, or bounce.
		# 				Bounce scrolls to the left until the end of value reaches the right edge of the display width.
		#				It then reverses the scroll until the start of value reaches the left edge of the display

		if resetscrollposition:
			segment[u'scrollposition'] = 0
			segment[u'hesitate_timer'] = time.time() + pydPiper_config.HESITATION_TIME


		# Get current scroll position
		sp = segment[u'scrollposition'] if u'scrollposition' in segment else 0

		# Get hesitate time value
		try:
			hesitate_timer = segment[u'hesitate_timer']
		except KeyError:
			segment[u'hesitate_timer'] = hesitate_timer = time.time() + pydPiper_config.HESITATION_TIME

		value = segment[u'value'] if u'value' in segment else u''

		try:
			blank = pydPiper_config.SCROLL_BLANK_WIDTH
		except AttributeError:
			blank = 10


		# If value is smaller than the window then just send back a padded version of the value
#		if len(value) <= window:
#			buffer = "{0:<{1}}".format(value.encode('utf-8'), window).decode('utf-8')
#		# Else send back a scrolling version
#		elif len(value)-sp+blank >= window:
#			buffer = "{0:<{1}}".format(value[sp:].encode('utf-8'),window)[0:window].decode('utf-8')
#		else: #len(value)-sp+blank < window:
#			buffer = "{0:<{1}}{2}".format(value[sp:].encode('utf-8'),len(value)-sp+blank,value)[0:window].decode('utf-8')

		# If value is smaller than the window then just send back a padded version of the value
		if len(value) <= window:
			buffer = u"{0:<{1}}".format(value, window)
		# Else send back a scrolling version
		elif len(value)-sp+blank >= window:
			buffer = u"{0:<{1}}".format(value[sp:],window)[0:window]
		else: #len(value)-sp+blank < window:
			buffer = u"{0:<{1}}{2}".format(value[sp:],len(value)-sp+blank,value)[0:window]


		# If we need to scroll then update the scollposition
		if len(value) > window and hesitate_timer < time.time():
			if direction == u'left' or (direction == u'bounce' and cbounce == u'left'):
				if sp < len(value)+blank-1:
					sp += 1
				else:
					cbounce = u'right'
					if direction == u'left':
						sp = 0
			elif direction ==u'right' or (direction == u'bounce' and cbounce == u'right'):
				if sp > 0:
					sp -= 1
				else:
					cbounce = u'left'
					if direction == u'right':
						sp = len(value)+blank-1

			# Store current scroll position
			segment[u'scrollposition'] = sp

		# Return part of segment to display based upon scroll position
		return buffer


	def buildline(self, segments, resetscrollpositions = False):

		buffer = ''
		pos = 0

		for segment in segments:
			start = segment[u'start'] if u'start' in segment else 0
			end = segment[u'end'] if u'end' in segment else pydPiper_config.DISPLAY_WIDTH
			scroll = segment[u'scroll'] if u'scroll' in segment else False
			window = end-start
			if start > pos:
				buffer += u"{0:<{1}}".format('',start-pos)

			value = segment[u'value'] if u'value' in segment else u''
			if scroll:
				direction = segment[u'scrolldirection'] if u'scrolldirection' in segment else u'left'
				buffer += self.scrollwindow(segment, window, direction, resetscrollpositions)
			else:
				buffer += value[0:window]

			buffer = u"{0:<{1}}".format(buffer, end-start)

			pos = end
		return buffer

	def run(self):

		lines = []
		columns = []

		for i in range (0, self.lcd.rows):
		  lines.append("")
		  columns.append(0)

		while not exitapp[0]:
			# Get first display update off of the queue
			qitem = self.displayqueue.get()
			self.displayqueue.task_done()

			# if the first item is a font change request, process that and then try again
			if qitem[u'type'] == u'font':
				self.lcd.clear()
				self.lcd.switchcustomchars(displays.fonts.map.map(qitem[u'font']))
			elif qitem[u'type'] == u'display':
				lines_value_current = qitem[u'lines']
				break
			else:
				logging.debug(u"Unexpected displayqueue message {0}".format(qitem[u'type']))

		self.lcd.clear()

		lines_value_prev = copy.deepcopy(lines_value_current)
		linebuffers = [ ]

		# Zero linebuffers so that display gets appropriately initialized
		for i in range(0, self.lcd.rows):
			linebuffers.append('')

		# Zero values in segments so initial update will occur
		for line in lines_value_prev:
			for segment in line:
				segment[u'value'] = u''


		# Initialize the time display got updated
		time_prev = time.time()

		while not exitapp[0]:
			# Smooth animation
			if time.time() - time_prev < pydPiper_config.ANIMATION_SMOOTHING:
				time.sleep(pydPiper_config.ANIMATION_SMOOTHING-(time.time()-time_prev))
			try:
				time_prev = time.time()

				# Determine if any lines have been updated and if yes udpate buffer for them
				for linenr in range(0,len(lines_value_current)):

					line_changed = False

					for segnr in range(0,len(lines_value_current[linenr])):
						try:
							if lines_value_current[linenr][segnr][u'value'] != lines_value_prev[linenr][segnr][u'value']:
								line_changed = True
								break
						except (KeyError, IndexError):
							line_changed = True

					if line_changed:
						# Compute a new buffer for line
						buffer = self.buildline(lines_value_current[linenr], True)
					else:
						buffer = self.buildline(lines_value_current[linenr])

					buffer = u"{0:<{1}}".format(buffer,self.lcd.cols)

					# If actual content of line changed send update to display
					if linebuffers[linenr] != buffer:
						self.lcd.message(buffer,linenr,0)
						linebuffers[linenr] = buffer


				# Update prev values with current values
				lines_value_prev = copy.deepcopy(lines_value_current)

				# Attempt to get new value from queue
				while True:
					qitem=self.displayqueue.get_nowait()
					self.displayqueue.task_done()

					if qitem[u'type'] == u'font':
						self.lcd.clear()
						self.lcd.switchcustomchars(displays.fonts.map.map(qitem[u'font']))

						linebuffers = [ ]
						lines_value_current = [ ]
						# Font change occured which requires a display reset so, clear linebuffers
						for i in range(0,self.lcd.rows):
							linebuffers.append('')

					elif qitem[u'type'] == u'display':
#						lines_value_current = qitem['lines']
						new_lines = qitem[u'lines']

						# Need to make sure not to overwrite lines_value_current unless new_lines is coming from a new page
						# If this is just a value update, then determine what has changed and update just that
						try:
							if len(new_lines) != len(lines_value_current):
								# Structured between page updates is different so assume page change.  Throwing exception to drop to reset logic
								raise IndexError
							for i in range(0,len(new_lines)):
								for j in range(0, len( new_lines[i])):
									ns = new_lines[i][j]
									ps = lines_value_current[i][j]
									for k, v in ns.iteritems():
										if k in ps:
											# If any key has changed, update lines_value_current and set scroll position to 0
											if ps[k] != v:
												ps[k] = v
												ps[u'scrollposition'] = 0
										else:
											# If they key is not there, add it to lines_value_current and set scroll position to 0
											ps[k] = v
											ps[u'scrollposition'] = 0
						except:
							# Structure of new_lines and lines_value_current is different
							# Need to reset lines_value_current to new values
							lcd.clear()
							lines_value_current = copy.deepcopy(new_lines)
							linebuffers = [ ]
							for i in range(0,self.lcd.rows):
								linebuffers.append('')


						break
					else:
						logging.debug(u"Unexpected displayqueue message {0}".format(qitem[u'type']))

			# if no item available then...
			except Queue.Empty:
				pass

class music_controller(threading.Thread):
	# Receives updates from music services
	# Determines what page to displays
	# Sends relevant updates to display_controller

	# musicdata variables.
	# Includes all from musicdata class plus environmentals
	musicdata_init = {
		'state':u"stop",
		'musicdatasource':u"",
		'actPlayer':u"",
		'artist':u"",
		'title':u"",
		'album':u"",
		'uri':u"",
		'current':-1,
		'elapsed':-1,
		'remaining':u"",
		'duration':-1,
		'length':-1,
		'position':u"",
		'elapsed_formatted':u"",
		'volume':-1,
		'repeat': 0,
		'single': 0,
		'random': 0,
		'channels':0,
		'bitdepth':u"",
		'bitrate':u"",
		'samplerate':u"",
		'type':u"",
		'tracktype':u"",
		'repeat_onoff': u"Off",
		'single_onoff': u"Off",
		'random_onoff': u"Off",
		'playlist_display':u"",
		'playlist_position':-1,
		'playlist_count':-1,
		'playlist_length':-1,
		'current_tempc':0,
		'current_tempf':0,
		'disk_avail':0,
		'disk_availp':0,
		'current_time':u"",
		'current_time_sec':u"",
		'current_time_formatted':u"",
		'current_ip':u""
	}


	def __init__(self, displayqueue, servicelist, rows, cols, showupdates=False):
		threading.Thread.__init__(self)

		self.daemon = True

		self.displayqueue = displayqueue
		self.musicqueue = Queue.Queue()
		self.rows = rows
		self.cols = cols
		self.current_font = ''

		self.showupdates = showupdates

		self.musicdata = copy.deepcopy(self.musicdata_init)
		self.musicdata_prev = copy.deepcopy(self.musicdata)
		self.servicelist = servicelist
		self.services = { }

		# Attempt to initialize services
		self.initservices()

		# Lock used to prevent simultaneous update of the musicdata dictionary
		self.musicdata_lock = threading.Lock()


	def initservices(self):

		# Make sure that if rune is selected that is is the only service that is selected
		if u"rune" in self.servicelist and len(self.servicelist) > 1:
			logging.critical(u"Rune service can only be used alone")
			raise RuntimeError(u"Rune service can only be used alone")
		if u"volumio" in self.servicelist and len(self.servicelist) > 1:
			logging.critical(u"Volumio service can only be used alone")
			raise RuntimeError(u"Volumio service can only be used alone")

		musicservice = None
		for s in self.servicelist:
			s = s.lower()
			try:
				if s == u"mpd":
					musicservice = sources.musicdata_mpd.musicdata_mpd(self.musicqueue, pydPiper_config.MPD_SERVER, pydPiper_config.MPD_PORT, pydPiper_config.MPD_PASSWORD)
				elif s == u"spop":
					musicservice = sources.musicdata_spop.musicdata_spop(self.musicqueue, pydPiper_config.SPOP_SERVER, pydPiper_config.SPOP_PORT, pydPiper_config.SPOP_PASSWORD)
				elif s == u"lms":
					musicservice = sources.musicdata_lms.musicdata_lms(self.musicqueue, pydPiper_config.LMS_SERVER, pydPiper_config.LMS_PORT, pydPiper_config.LMS_USER, pydPiper_config.LMS_PASSWORD, pydPiper_config.LMS_PLAYER)
				elif s == u"rune":
					musicservice = sources.musicdata_rune.musicdata_rune(self.musicqueue, pydPiper_config.RUNE_SERVER, pydPiper_config.RUNE_PORT, pydPiper_config.RUNE_PASSWORD)
				elif s == u"volumio":
					musicservice = sources.musicdata_volumio2.musicdata_volumio2(self.musicqueue, pydPiper_config.VOLUMIO_SERVER, pydPiper_config.VOLUMIO_PORT, exitapp )
				else:
					logging.debug(u"Unsupported music service {0} requested".format(s))
					continue
			except NameError:
				# Missing dependency for requested servicelist
				logging.warning(u"Request for {0} failed due to missing dependencies".format(s))
				pass
			if musicservice != None:
				self.services[s] = musicservice

		if len(self.services) == 0:
			logging.critical(u"No music services succeeded in initializing")
			raise RuntimeError(u"No music services succeeded in initializing")

	def bigclock(self, time):
		#Converts time into string array that can be printed to produce a large clock display
		# time must be formatted as ##:## or #:##
		# can be 24 or 12 hour

		retval = [ u'Bad Symbol', u' Received ' ]
		# Make sure that time doesn't contain invalid charcters
		AllowableSymbols = [ u'0', u'1',u'2',u'3',u'4',u'5',u'6',u'7',u'8',u'9',u':' ]
		for c in time:
			if c not in AllowableSymbols:
				logging.debug(u"Received invalid symbol into bigclock converter")
				retval = [ u'Bad Symbol', u' Received ' ]
				return retval

		retval = [ u'Bad Size', u'Received' ]
		# Make sure that display is appropriate size (e.g. 4-5 characters)
		if len(time) < 4 or len(time) > 5:
			logging.debug(u"Received time value that was the wrong size")
			return retval

		numbers = displays.fonts.size5x8.bigclock.numbers
		retval = [ u'', u'' ]
		for tc in time:
			for l in range(0,2):
				if tc in u'0123456789':
					for c in range(0,3):
						retval[l] += unichr(numbers[int(tc)][l][c])
				elif tc in u':':
					retval[l] += u'o'
#				retval[l] += ' '

		return retval


	def volume_bar(self,vol_per, chars, fe=u'_', fh=u'/', ff=u'*', vle=u'_', vre=u'_', vrh=u'/'):
		# Algorithm for computing the volume lines
		# inputs (vol_per, characters, fontempyt, fonthalf, fontfull, fontleftempty, fontrightempty, fontrighthalf)
		ppb = percentperblock = 100.0 / chars

		buffer = u''
		i = 0
		if vol_per <= (i+.25)*ppb:
			buffer += chr(vle)
		elif (i+.25)*ppb < vol_per and vol_per <= (i+.75)*ppb:
			buffer += chr(fh)
		elif (i+.75)*ppb < vol_per:
			buffer += chr(ff)
		else:
			# Shouldnt be here
			logging.debug(u"Bad value in volume_bar")
			buffer += u'Y'

		for i in range(1, chars-1):
			if vol_per <= (i+.25)*ppb:
				buffer += chr(fe)
			elif (i+.25)*ppb < vol_per and vol_per <= (i+.75)*ppb:
				buffer += chr(fh)
			elif (i+.75)*ppb < vol_per:
				buffer += chr(ff)
			else:
				# Shouldnt be here
				logging.debug(u"Bad value in volume_bar")
				buffer += u'Y'

		i = chars - 1
		if vol_per <= (i+.25)*ppb:
			buffer += chr(vre)
		elif (i+.25)*ppb < vol_per and vol_per <= (i+.75)*ppb:
			buffer += chr(vrh)
		elif (i+.75)*ppb < vol_per:
			buffer += chr(ff)
		else:
			# Shouldnt be here
			logging.debug(u"Bad value in volume_bar")
			buffer += u'Y'


		return buffer

	def run(self):

		logging.debug(u"Music Controller Starting")

		# Start the thread that updates the system variables
		sv_t = threading.Thread(target=self.updatesystemvars)
		sv_t.daemon = True
		sv_t.start()
		timesongstarted = 0

		self.current_page_number = -1
		self.current_line_number = 0
		self.current_pages = pages.PAGES_Stop
		self.page_expires = 0
		self.hesitation_expires = 0
		self.curlines = []
		self.hesitate_expires = []
		self.alert_mode = False
		self.alert_check = False

		# Reset all of the alert message cooling values
		for pl in pages.ALERT_LIST:
			pl[u'cooling_expires'] = 0

		# Force the system to recognize the start state as a change
		#####  Need to determine how to force a display update on start-up #####
		self.musicdata_prev[u'state'] = ""

		lastupdate = 0 # Initialize variable to be used to force updates every second regardless of the receipt of a source update
		while not exitapp[0]:

			updates = { }

			# Attempt to get an update from the queue
			try:
				updates = self.musicqueue.get_nowait()
				self.musicqueue.task_done()
			except Queue.Empty:
				pass


			with self.musicdata_lock:
				# Update musicdata based upon received message
				for item, value in updates.iteritems():
					self.musicdata[item] = value

				# Update song timing variables
				if u'elapsed' in updates:
					self.musicdata[u'elapsed'] = self.musicdata[u'current'] = updates[u'elapsed']
					timesongstarted = time.time() - self.musicdata[u'elapsed']

				if self.musicdata[u'state'] == u'play':
					if u'elapsed' not in updates:
						if timesongstarted > 0:
							self.musicdata[u'elapsed'] = int(time.time() - timesongstarted)
						else:
							# We got here without timesongstarted being set which is a problem...
							logging.debug(u"Trying to update current song position with an uninitialized start time")

				# If the value of current has changed then update the other related timing variables
				if self.musicdata[u'elapsed'] != self.musicdata_prev[u'elapsed']:
					if self.musicdata[u'length'] > 0:
						timepos = time.strftime("%-M:%S", time.gmtime(self.musicdata[u'elapsed'])) + "/" + time.strftime("%-M:%S", time.gmtime(self.musicdata[u'length']))
						remaining = time.strftime("%-M:%S", time.gmtime(self.musicdata[u'length'] - self.musicdata[u'elapsed'] ) )

					else:
						timepos = time.strftime("%-M:%S", time.gmtime(self.musicdata[u'elapsed']))
						remaining = timepos

					self.musicdata[u'remaining'] = remaining.decode()
					self.musicdata[u'elapsed_formatted'] = self.musicdata[u'position'] = timepos.decode()

				# Update onoff variables (random, single, repeat)
				self.musicdata[u'random_onoff'] = u"On" if self.musicdata[u'random'] else u"Off"
				self.musicdata[u'single_onoff'] = u"On" if self.musicdata[u'single'] else u"Off"
				self.musicdata[u'repeat_onoff'] = u"On" if self.musicdata[u'repeat'] else u"Off"

				# if volume has changed, update volume_bar_fancy
				if u'volume' in updates:
					self.musicdata[u'volume_bar_fancy'] = self.volume_bar(self.musicdata[u'volume'],
					self.cols-2,
					displays.fonts.size5x8.volume.e,
					displays.fonts.size5x8.volume.h,
					displays.fonts.size5x8.volume.f,
					displays.fonts.size5x8.volume.el,
					displays.fonts.size5x8.volume.er,
					displays.fonts.size5x8.volume.hr )

					self.musicdata[u'volume_bar_big'] = self.volume_bar(self.musicdata[u'volume'],
					self.cols-3,
					displays.fonts.size5x8.speaker.e,
					displays.fonts.size5x8.speaker.h,
					displays.fonts.size5x8.speaker.f,
					displays.fonts.size5x8.speaker.el,
					displays.fonts.size5x8.speaker.er,
					displays.fonts.size5x8.speaker.hr )

			# If anything has changed, update pages
			if self.musicdata != self.musicdata_prev or lastupdate < time.time():
				lastupdate = time.time()+1
				self.updatepages()

				if self.showupdates:
					ctime = moment.utcnow().timezone(u"US/Eastern").strftime("%-I:%M:%S %p").strip()
					print u"Status at time {0}".format(ctime)

					with self.musicdata_lock:
						for item,value in self.musicdata.iteritems():
							try:
								print u"    [{0}]={1} {2}".format(item,repr(value), type(value))
							except:
								print u"err"
								print u"[{0}] =".format(item)
								print type(value)
								print repr(value)
						print u"\n"

				# Update musicdata_prev with anything that has changed
#				if self.musicdata['current'] != self.musicdata_prev['current']:
#					self.musicdata_prev['current'] = self.musicdata['current']
#					self.musicdata_prev['remaining'] = self.musicdata['remaining']
#					self.musicdata_prev['position'] = self.musicdata['position']
				with self.musicdata_lock:
					for item, value in self.musicdata.iteritems():
						try:
							if self.musicdata_prev[item] != value:
								self.musicdata_prev[item] = value
						except KeyError:
							self.musicdata_prev[item] = value

			# Update display data every 1/4 second
			time.sleep(.25)

	def checkalert(self, pl, state):
		# Determines whether a alert show be displayed

		# Use try block to skip page if variables are missing
		try:
			# Check to see what type of monitoring to perform
			if pl[u'alert'][u'type'] == u"change":
				if self.musicdata[pl[u'alert'][u'variable']] != self.musicdata_prev[pl[u'alert'][u'variable']]:
					# Some state changes cause variable changes like volume
					# Check to see if these dependent variable changes
					# should be suppressed
					try:
						if self.musicdata_prev[u'state'] == state or not pl[u'alert'][u'suppressonstatechange']:
							if u'values' in pl[u'alert']:
								if len(pl[u'alert'][u'values']) > 0:
									for v in pl[u'alert'][u'values']:
										if v == self.musicdata[pl[u'alert'][u'variable']]:
											return True
								else:
									return True
							else:
								return True
					except KeyError:
						return False
			elif pl[u'alert'][u'type'] == u"above":
				if self.musicdata[pl[u'alert'][u'variable']] > pl[u'alert'][u'values'][0]:
					return True
			elif pl[u'alert'][u'type'] == u"below":
				if self.musicdata[pl[u'alert'][u'variable']] < pl[u'alert'][u'values'][0]:
					return True
			elif pl[u'alert'][u'type'] == u"range":
				if self.musicdata[pl[u'alert'][u'variable']] > pl[u'alert'][u'values'][0] and self.musicdata[pl[u'alert'][u'variable']] < pl[u'alert'][u'values'][1]:
					return True
		except (KeyError, AttributeError, IndexError):
			return False
		return False

	def resetalertpage(self, pl):
		# Set current_pages to the alert page
		self.current_pages = pl
		self.current_page_number = 0
		self.current_line_number = 0
		self.page_expires = time.time() + self.current_pages[u'pages'][self.current_page_number][u'length']
		self.curlines = []
		self.hesitate_expires = []

		# Set cooling expiry time.  If not coolingperiod directive, use default
		try:
			pl[u'cooling_expires'] = time.time() + pl[u'alert'][u'coolingperiod']
		except KeyError:
			try:
				pl[u'cooling_expires'] = time.time() + pydPiper_config.COOLING_PERIOD
			except AttributeError:
				logging.debug(u"COOLING_PERIOD missing from pydPiper_config.py")
				pl[u'cooling_expires'] = time.time() + 15


	def movetonextpage(self):

		# Move to next page and check to see if it should be displayed or hidden
		for i in range(len(self.current_pages[u'pages'])):
			self.current_page_number = self.current_page_number + 1

			# if on last page, return to first page
			if self.current_page_number > len(self.current_pages[u'pages'])-1:
				self.current_page_number = 0

			self.page_expires = time.time() + self.current_pages[u'pages'][self.current_page_number][u'duration']

			cp = self.current_pages[u'pages'][self.current_page_number]

			hwe = cp[u'hidewhenempty'] if u'hidewhenempty' in cp else False
			hwp = cp[u'hidewhenpresent'] if u'hidewhenpresent' in cp else False

			# to prevent old pages format from causing problems, convert values to strings
			if type(hwe) is bool:
				hwe = unicode(hwe)

			if type(hwp) is bool:
				hwp = unicode(hwp)

			if hwe.lower() == u'all' or hwe.lower() == u'true':
				allempty = True
				hvars = cp[u'hidewhenemptyvars'] if u'hidewhenemptyvars' in cp else [ ]

				for v in hvars:
					try:
						# if the variable is a string
						if type(self.musicdata[v]) is unicode:
							# and it is not empty, then set allempty False and exit loop
							if len(self.musicdata[v]) > 0:
								allempty = False
								break
						elif type(self.musicdata[v]) is int:
							if not self.musicdata[v] == 0:
								allempty = False
								break
						else:
							# All other variable types are considered not empty
							allempty = False
							break
					except KeyError:
						# if the variable is not in musicdata consider it empty
						pass
				if not allempty:
					break
			elif hwe.lower() == u'any':
				anyempty = False
				try:
					hvars = cp[u'hidewhenemptyvars']
				except KeyError:
					hvars = [ ]

				for v in hvars:
					try:
						# if the variable is a string
						if type(self.musicdata[v]) is unicode:
							# and it is empty, then set anyempty True and exit loop
							if len(self.musicdata[v]) == 0:
								anyempty = True
								break

						# if the value is 0 consider it empty
						elif type(self.musicdata[v]) is int:
							if self.musicdata[v] == 0:
								anyempty = True
								break
					except KeyError:
						# if the variable is not in musicdata consider it empty
						anyempty = True
						break
				if not anyempty:
					break

			elif hwp.lower() == u'any':
				anypresent = False
				try:
					hvars = cp[u'hidewhenpresentvars']
				except KeyError:
					hvars = [ ]

				for v in hvars:
					try:
						# if the variable is a string
						if type(self.musicdata[v]) is unicode:
							# and it is present, then set anypresent True and exit loop
							if len(self.musicdata[v]) > 0:
								anypresent = True
								break
						elif type(self.musicdata[v]) is int:
							if not self.musicdata[v] == 0:
								anypresent = True
								break

						# if it is not a string, and not zero consider it present
						else:
							anypresent = True
							break
					except KeyError:
						# if the variable is not in musicdata consider it empty
						break
				if not anypresent:
					break

			elif hwp.lower() == u'all' or hwp.lower() == u'true':
				allpresent = True
				try:
					hvars = cp[u'hidewhenemptyvars']
				except KeyError:
					hvars = [ ]

				for v in hvars:
					try:
						# if the variable is a string
						if type(self.musicdata[v]) is unicode:
							# and it is not present, then set allpresent False and exit loop
							if len(self.musicdata[v]) == 0:
								allpresent = False
								break
						elif type(self.musicdata[v]) is int:
							if self.musicdata[v] == 0:
								allpresent = False
								break
					except KeyError:
						# if the variable is not in musicdata consider it empty
						allpresent = False
						break
				if not allpresent:
					break

			else:
				# If not hidewhenempty or hidewhenpresent then exit loop
				break



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

	def getsegmentvalue(self, vars, format, just, start, end):

		# Get paramaters
		# ignore KeyError exceptions if variable is unavailable
		parms = []
		try:
			for k in range(len(vars)):
				try:
					varname = vars[k].split(u'|')[0]
					val = self.transformvariable(self.musicdata[varname], vars[k])
#					if val is unicode:
#						parms.append(val.encode('utf-8'))
#					else:
					parms.append(val)
#							if type(self.musicdata[vars[k]]) is unicode:
#								parms.append(self.transformvariable(self.musicdata[vars[k]],vars[k]).encode('utf-8'))
#							else:
#								parms.append(self.transformvariable(self.musicdata[vars[k]],vars[k]))
				except KeyError:
					pass
		except KeyError:
			pass

		# create segment to display
		try:
			segval = format.format(*parms)
		except:
			logging.debug( u"Var Error Format {0}, Parms {1} Vars {2}".format(format, parms, vars) )
			# Format doesn't match available variables
			logging.debug(u"Var Error with parm type {0} and format type {1}".format(type(parms), type(format)))
			segval = u"VarErr"

		# justify segment
		try:
			if just.lower() == u"center":
				segval = u"{0:^{1}}".format(segval, end-start)
			elif just.lower() == u"right":
				segval = u"{0:>{1}}".format(segval, end-start)
		except KeyError:
			pass

		# Place actual value to display within segment into the segment data structure
		return segval


	def updatepages(self):

		# Using PAGES variables, compute what to display
		state = self.musicdata.get(u'state')

		self.alert_check = False

		# Check to see if any alerts are triggered
		for pl in pages.ALERT_LIST:
			# Check to see if alert is in its cooling period
			if pl[u'cooling_expires'] < time.time():
				# Use try block to skip page if variables are missing
				try:
					self.alert_check = self.checkalert(pl, state)

					if self.alert_check:
						self.alert_mode = True

						# Set current_pages to the alert page
						self.resetalertpage(pl)

						# if an alert has been found, break out of the loop
						# this has the effect of making the order of the list the priority of the messages
						break

				except (KeyError, AttributeError, IndexError):
					pass


		# Set interruptible value.  If value not present, set to default value of True
		try:
			# interruptible is only an override until the page expires.  If page expires, allow page updates to continue.
			interruptible = self.current_pages[u'interruptible']
			if self.page_expires < time.time():
				interruptible = True

				# if page just expired on an alert page then force restore to current play state
				if self.alert_mode:
					self.alert_mode = False
					self.musicdata_prev[u'state'] = u""
			else:
				interruptible = self.current_pages[u'interruptible']
		except KeyError:
			interruptible = True

		# check to see if we need to change the display to something new
		if (self.alert_mode or state != self.musicdata_prev[u'state']) and interruptible:
			self.current_page_number = -1
			self.current_line_number = 0
			self.page_expires = 0
			self.curlines = []
			self.hesitate_expires = []

			# if change caused by state change and not alert
			if self.alert_mode == False:
				self.musicdata_prev[u'state'] = state

				# Set to new display page
				if state != u"play":
					self.current_pages = pages.PAGES_Stop
				# else display the PAGES_Playing pages
				else:
					self.current_pages = pages.PAGES_Play

		# if page has expired then move to the next page
		if self.page_expires < time.time():
			self.movetonextpage()

		# Set current_page
		current_page = self.current_pages[u'pages'][self.current_page_number]

		# Change the font if requested
		if u'font' in current_page:
			if self.current_font != current_page[u'font']:
				self.current_font = current_page[u'font']

				dispval = { u'type': u'font', u'font': current_page[u'font'] }

				# Send font update to the queue
				self.displayqueue.put(dispval)

		# Now build the display

		# The data structure for the display is an array of lines with each line made up of an array of segments
		# Each segment is a dict that defines what goes into the segment and where to display it on the line
		# E.g.
		#  lines = [
		#	[ 	{ 'start':0, 'end':7, 'value':"Artist:" },
		#		{ 'start':8, 'end':20, 'value':"Prince and the Revolutions", 'scroll':True, 'justification':'left' }
		#	],
		#	[ 	{ 'start':0, 'end':7, 'value':"Title:" },
		#		{ 'start':8, 'end':20, 'value':"Purple Rain", 'scroll':True, 'justification':'left' }
		#	],
		#]

		lines = []
		for i in range(len(current_page[u'lines'])):
			pagename = current_page[u'name'] if u'name' in current_page else u"unknown"
			current_line = current_page[u'lines'][i]
			linename = current_line[u'name'] if u'name' in current_line else u"unknown"

			segments = []

			# If no segments in line, create line with one segment based upon the line level variables then add it to lines and go to next loop iteration
			if u'segments' not in current_line:
				segment = { }

				segment[u'start'] = 0
				segment[u'end'] = self.cols
				segment[u'variables'] = vars = current_line[u'variables'] if u'variables' in current_line else [ ]
				segment[u'format'] = current_line[u'format'] if u'format' in current_line else u""
				segment[u'justification'] = justification = current_line[u'justification'] if u'justification' in current_line else u"left"
				segment[u'scroll'] = scroll = current_line[u'scroll'] if u'scroll' in current_line else False
				segment[u'scrolldirection'] = scrolldirection = current_line[u'scrolldirection'] if u'scrolldirection' in current_line else u"left"

				# Make sure format is a unicode value
				if type(segment[u'format']) is not unicode:
					try:
						segment[u'format'] = segment[u'format'].decode()
					except:
						logging.debug(u"On page {0}, line {1}, there is a segment with a bad format key".format(pagename, linename))
						segment[u'format'] = u'FmtErr'

				format = segment[u'format']

				strftime = current_line[u'strftime'] if u'strftime' in current_line else u"%-I:%M %p"

				if pydPiper_config.TIME24HOUR:
					bigclockformat = u"%H:%M"
				else:
					bigclockformat = u"%I:%M"

				bigclockinput = moment.utcnow().timezone(pydPiper_config.TIMEZONE).strftime(bigclockformat).strip().decode()
				bigclockoutput = self.bigclock(bigclockinput)

				current_time_ampm = moment.utcnow().timezone(pydPiper_config.TIMEZONE).strftime("%p").strip().decode()

				with self.musicdata_lock:
					self.musicdata[u'time_formatted'] = moment.utcnow().timezone(pydPiper_config.TIMEZONE).strftime(strftime).strip().decode()
					self.musicdata[u'time_big_1'] = bigclockoutput[0]
					self.musicdata[u'time_big_2'] = bigclockoutput[1]
					self.musicdata[u'time_ampm'] = current_time_ampm

					# To support previous key used for this purpose
					self.musicdata[u'current_time_formatted'] = self.musicdata[u'time_formatted']

				segment[u'value'] = self.getsegmentvalue(vars, format, justification, segment[u'start'], segment[u'end'])

				segments.append(segment)
				lines.append(segments)
				continue


			segment_start = 0

			for j in range(0, len(current_line[u'segments'])):
				current_segment = current_line[u'segments'][j]
				segname = current_segment[u'name'] if u'name' in current_segment else u"unknown"

				segment = { }

				# Need to make sure start and end are available
				segment[u'start'] = current_segment[u'start'] if u'start' in current_segment else 0
				segment[u'end'] = current_segment[u'end'] if u'end' in current_segment else self.cols


				segment[u'variables'] = variables = current_segment[u'variables'] if u'variables' in current_segment else [ ]
				segment[u'format'] = current_segment[u'format'] if u'format' in current_segment else u""
				segment[u'justification'] = justification = current_segment[u'justification'] if u'justification' in current_segment else u"left"
				segment[u'scroll'] = scroll = current_segment[u'scroll'] if u'scroll' in current_segment else False
				segment[u'scrolldirection'] = scrolldirection = current_segment[u'scrolldirection'] if u'scrolldirection' in current_segment else u"left"

				# Make sure format is a unicode value
				if type(segment[u'format']) is not unicode:
					try:
						segment[u'format'] = segment[u'format'].decode()
					except:
						logging.debug(u"On page {0}, line {1}, there is a segment with a bad format key".format(pagename, linename))
						segment[u'format'] = u'FmtErr'

				format = segment[u'format']

				# Check placement on line
				if segment[u'start'] < segment_start:
					# This segment starts before the end of the previous segment
					# Skip it
					logging.debug(u"Found a segment that starts before the end of a previous segment on page {0}, segment {1}".format(pagename,segname))
					continue

				# Crop line if end past the current display width
				if segment[u'end'] <= self.cols:
					current_segment[u'end'] = segment[u'end']
				else:
					current_segment[u'end'] = self.cols
					logging.debug(u"Cropping segment from page {0}, segment {1} to display width".format(pagename, segname))

				# Update the current start position so we can detect if the next segment starts after this one
				segment_start = current_segment[u'end']

				# If you have specified a strftime format on the segment
				# use it to add a formatted time to musicdata
				# else use 12 hour clock as default

				if pydPiper_config.TIME24HOUR:
					bigclockformat = u"%H:%M"
				else:
					bigclockformat = u"%I:%M"

				bigclockinput = moment.utcnow().timezone(pydPiper_config.TIMEZONE).strftime(bigclockformat).strip().decode()
				bigclockoutput = self.bigclock(bigclockinput)

				strftime = current_segment[u'strftime'] if u'strftime' in current_segment else u"%-I:%M %p"

				with self.musicdata_lock:
					self.musicdata[u'time_formatted'] = moment.utcnow().timezone(pydPiper_config.TIMEZONE).strftime(strftime).strip().decode()
					self.musicdata[u'time_big_1'] = bigclockoutput[0]
					self.musicdata[u'time_big_2'] = bigclockoutput[1]

					# To support previous key used for this purpose
					self.musicdata[u'current_time_formatted'] = self.musicdata[u'time_formatted']


				segment[u'value'] = self.getsegmentvalue(variables, format, justification, segment[u'start'], segment[u'end'])

				# Add segment to array of segments
				segments.append(segment)

			# Add array of segments to line array
			lines.append(segments)


			####### This logic moving to display controller ###########
			# determine whether to scroll or not
			# if scroll is false, set hesitation time to large value which
			# effectively shuts off the scroll function
#			if lines[i] != self.curlines[i]:
#				self.curlines[i] = lines[i]
#				try:
#					if current_line['scroll']:
#						self.hesitate_expires[i] = time.time() + pydPiper_config.HESITATION_TIME
#					else:
#						self.hesitate_expires[i] = time.time() + 86400 # Do not scroll
#				except KeyError:
#					self.hesitate_expires[i] = time.time() + 86400 # Do not scroll

		# Determine if the display should hesitate before scrolling
#		dispval = { 'type': 'display', 'lines': [] }
#		for i in range(len(lines)):
#			if self.hesitate_expires[i] < time.time():
#				dispval['lines'].append(lines[i])
#			else:
#				dispval['lines'].append(lines[i][0:self.cols])

		# Send dispval to the queue
		dispval = { u'type': u'display', u'lines': lines }
		self.displayqueue.put(dispval)

	def updatesystemvars(self):
		while True:
			try:
				current_time_ampm = moment.utcnow().timezone(pydPiper_config.TIMEZONE).strftime(u"%p").strip().decode()
				if pydPiper_config.TIME24HOUR == True:
					current_time = moment.utcnow().timezone(pydPiper_config.TIMEZONE).strftime(u"%H:%M").strip().decode()
					current_time_sec = moment.utcnow().timezone(pydPiper_config.TIMEZONE).strftime(u"%H:%M:%S").strip().decode()
				else:
					current_time = moment.utcnow().timezone(pydPiper_config.TIMEZONE).strftime(u"%-I:%M %p").strip().decode()
					current_time_sec = moment.utcnow().timezone(pydPiper_config.TIMEZONE).strftime(u"%-I:%M:%S %p").strip().decode()
			except ValueError:
				# Don't know why but on exit, the moment code is occasionally throwing a ValueError
				current_time = u"00:00"
				current_time_sec = u"00:00:00"
				current_time_ampm = u''

			current_ip = commands.getoutput(u"ip -4 route get 1 | head -1 | cut -d' ' -f8 | tr -d '\n'").strip()

			outside_tempf = 0.0
			outside_tempc = 0.0
			outside_temp = 0.0
			outside_temp_max = 0.0
			outside_temp_min = 0.0
			outside_conditions = u''
			outside_temp_formatted = u''
			outside_temp_max_formatted = u''
			outside_temp_min_formatted = u''

			try:
				owm = pyowm.OWM(pydPiper_config.OWM_API)
				obs = owm.weather_at_place(pydPiper_config.OWM_LOCATION)
				fc = owm.daily_forecast(pydPiper_config.OWM_LOCATION)
				f = fc.get_forecast()
				dailyfc = f.get_weathers()
				wea = obs.get_weather()

				outside_tempf = wea.get_temperature(u'fahrenheit')[u'temp']
				outside_temp_maxf = dailyfc[0].get_temperature(u'fahrenheit')[u'max']
				outside_temp_minf = dailyfc[0].get_temperature(u'fahrenheit')[u'min']

				outside_tempc = wea.get_temperature(u'celsius')[u'temp']
				outside_temp_maxc = dailyfc[0].get_temperature(u'celsius')[u'max']
				outside_temp_minc = dailyfc[0].get_temperature(u'celsius')[u'min']

				# Localize temperature value
				if pydPiper_config.TEMPERATURE.lower() == u'celsius':
					outside_temp = outside_tempc
					outside_temp_max = outside_temp_maxc
					outside_temp_min = outside_temp_minc
					outside_temp_formatted = u"{0}°C".format(int(outside_temp))
					outside_temp_max_formatted = u"{0}°C".format(int(outside_temp_max))
					outside_temp_min_formatted = u"{0}°C".format(int(outside_temp_min))
				else:
					outside_temp = outside_tempf
					outside_temp_max = outside_temp_maxf
					outside_temp_min = outside_temp_minf
					outside_temp_formatted = u"{0}°F".format(int(outside_temp))
					outside_temp_max_formatted = u"{0}°F".format(int(outside_temp_max))
					outside_temp_min_formatted = u"{0}°F".format(int(outside_temp_min))

				outside_conditions = wea.get_detailed_status()
			except:
				logging.debug(u"Failed to get weather data.  Check OWM_API key.")
				pass


			try:
				with open(u"/sys/class/thermal/thermal_zone0/temp") as file:
					system_tempc = int(file.read())

				# Convert value to float and correct decimal place
				system_tempc = round(float(system_tempc) / 1000,1)

				# convert to fahrenheit
				system_tempf = round(system_tempc*9/5+32,1)

			except AttributeError:
				system_tempc = 0.0
				system_tempf = 0.0

			try:
				if pydPiper_config.TEMPERATURE.lower() == u'celsius':
					system_temp = system_tempc
					system_temp_formatted = u"{0}°c".format(int(system_temp))
				else:
					system_temp = system_tempf
					system_temp_formatted = u"{0}°f".format(int(system_temp))
			except:
				system_temp = system_tempf
				system_temp_formatted = u"{0}°f".format(int(system_temp))

			try:
				# Check if running on OSX.  If yes, adjust df command
				if sys.platform == u"darwin":
					with os.popen(u"df /") as p:
						p = os.popen(u"df /")
						line = p.readline()
						line = p.readline()

					va = line.split()
					line = "{0} {1}".format(va[3], va[4])
				else:
					# assume running on Raspberry linux
					with os.popen(u"df --output='avail','pcent','used' /") as p:
						line = p.readline()
						line = p.readline().strip()

				va = line.split()
				avail = int(va[0])
				usedp = int(va[1][:-1]) # Remove trailing % and convert to int
				used = int(va[2])
				availp = 100-usedp

			except AttributeError:
				avail = 0
				availp = 0
				usedp = 0
				used = 0

			with self.musicdata_lock:
				self.musicdata[u'system_temp'] = system_temp
				self.musicdata[u'system_temp_formatted'] = system_temp_formatted

				self.musicdata[u'system_tempc'] = system_tempc
				self.musicdata[u'system_tempf'] = system_tempf

				# For backward compatibility
				self.musicdata[u'current_tempc'] = self.musicdata[u'system_tempc']
				self.musicdata[u'current_tempf'] = self.musicdata[u'system_tempf']

				self.musicdata[u'disk_avail'] = avail
				self.musicdata[u'disk_availp'] = availp
				self.musicdata[u'disk_used'] = used
				self.musicdata[u'disk_usedp'] = usedp

				self.musicdata[u'time'] = current_time
				self.musicdata[u'time_ampm'] = current_time_ampm
				# note: 'time_formatted' is computed during page processing as it needs the value of the strftime key contained on the line being displayed

				# For backwards compatibility
				self.musicdata[u'current_time'] = current_time
				self.musicdata[u'current_time_sec'] = current_time

				self.musicdata[u'ip'] = current_ip.decode()

				# For backwards compatibility
				self.musicdata[u'current_ip'] = current_ip.decode()

				self.musicdata[u'outside_temp'] = outside_temp
				self.musicdata[u'outside_temp_max'] = outside_temp_max
				self.musicdata[u'outside_temp_min'] = outside_temp_min
				self.musicdata[u'outside_temp_formatted'] = outside_temp_formatted
				self.musicdata[u'outside_temp_max_formatted'] = outside_temp_max_formatted
				self.musicdata[u'outside_temp_min_formatted'] = outside_temp_min_formatted
				self.musicdata[u'outside_conditions'] = outside_conditions

			# Read environmentals every 20 seconds
			time.sleep(20)

def validpages(pagesmodule):
	# Need to have the following structures to be valid

	# PAGES_Play
	try:
		p = pagesmodule.PAGES_Play
	except:
		return False

	# PAGES_Stop
	try:
		p = pagesmodule.PAGES_Stop
	except:
		return False

	# ALERT_LIST
	try:
		al = pagesmodule.ALERT_LIST
	except:
		return False

	return True

def sigterm_handler(_signo, _stack_frame):
        sys.exit(0)

if __name__ == u'__main__':
	signal.signal(signal.SIGTERM, sigterm_handler)

	# Changing the system encoding should no longer be needed
#	if sys.stdout.encoding != u'UTF-8':
#    		sys.stdout = codecs.getwriter(u'utf-8')(sys.stdout, u'strict')

	logging.basicConfig(format=u'%(asctime)s:%(levelname)s:%(message)s', filename=pydPiper_config.LOGFILE, level=pydPiper_config.LOGLEVEL)
	logging.getLogger().addHandler(logging.StreamHandler())
	logging.getLogger(u'socketIO-client').setLevel(logging.WARNING)

	# Move unhandled exception messages to log file
	def handleuncaughtexceptions(exc_type, exc_value, exc_traceback):
		if issubclass(exc_type, KeyboardInterrupt):
			sys.__excepthook__(exc_type, exc_value, exc_traceback)
			return

		logging.error(u"Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))
		try:
			if len(mc.musicdata) > 0:
				logging.error(u"Player status at exception")
				logging.error(unicode(mc.musicdata))
		except NameError:
			# If this gets called before the music controller is instantiated, ignore it
			pass

		sys.__excepthook__(exc_type, exc_value, exc_traceback)


	sys.excepthook = handleuncaughtexceptions

	# Suppress MPD libraries INFO messages
	loggingMPD = logging.getLogger(u"mpd")
	loggingMPD.setLevel( logging.WARN )

	try:
		opts, args = getopt.getopt(sys.argv[1:],u"d:",[u"driver=", u"lms",u"mpd",u"spop",u"rune",u"volumio",u"pages=", u"showupdates"])
	except getopt.GetoptError:
		print u'pydPiper.py -d <driver> --mpd --spop --lms --rune --volumio --pages --showupdates'
		sys.exit(2)

	services_list = [ ]
	driver = ''
	showupdates = False

	for opt, arg in opts:
		if opt == u'-h':
			print u'pydPiper.py -d <driver> --mpd --spop --lms --rune --volumio --pages --showupdates'
			sys.exit()
		elif opt in (u"-d", u"--driver"):
			driver = arg
		elif opt in (u"--mpd"):
			services_list.append(u'mpd')
		elif opt in (u"--spop"):
			services_list.append(u'spop')
		elif opt in (u"--lms"):
			services_list.append(u'lms')
		elif opt in (u"--rune"):
			services_list.append(u'rune')
		elif opt in (u"--volumio"):
			services_list.append(u'volumio')
		elif opt in (u"--pages"):
			print u"Loading {0} as page file".format(arg)
			# If page file provided, try to load provided file on top of default pages file
			try:
				newpages = imp.load_source(u'pages', arg)
				if validpages(newpages):
					pages = newpages
				else:
					print u"Invalid page file provided.  Using default pages."
			except IOError:
				# Page file not found
				print u"Page file {0} not found.  Using default pages".format(arg)

		elif opt in (u"--showupdates"):
			showupdates = True


	if len(services_list) == 0:
		logging.critical(u"Must have at least one music service to monitor")
		sys.exit()

	logging.info(pydPiper_config.STARTUP_LOGMSG)

	dq = Queue.Queue()

	pin_rs = pydPiper_config.DISPLAY_PIN_RS
	pin_e = pydPiper_config.DISPLAY_PIN_E
	pins_data = pydPiper_config.DISPLAY_PINS_DATA
	rows = pydPiper_config.DISPLAY_HEIGHT
	cols = pydPiper_config.DISPLAY_WIDTH

	# Choose display

	if not driver:
		driver = pydPiper_config.DISPLAY_DRIVER


	if driver == u"lcd_display_driver_winstar_weh001602a":
		lcd = displays.lcd_display_driver_winstar_weh001602a.lcd_display_driver_winstar_weh001602a(rows, cols, pin_rs, pin_e, pins_data)
	elif driver == u"lcd_display_driver_hd44780":
		lcd = displays.lcd_display_driver_hd44780.lcd_display_driver_hd44780(rows, cols, pin_rs, pin_e, pins_data)
	elif driver == u"lcd_display_driver_curses":
		lcd = displays.lcd_display_driver_curses.lcd_display_driver_curses(rows, cols)
	else:
		logging.critical(u"No valid display found")
		sys.exit()

	lcd.clear()
	lcd.message(pydPiper_config.STARTUP_MSG)

	mc = music_controller(dq, services_list, lcd.rows, lcd.cols, showupdates)
	time.sleep(2)
	dc = display_controller(dq, lcd)

	dc.start()
	mc.start()

	try:
		while True:
			time.sleep(1)
	except KeyboardInterrupt:
		pass

	finally:
		print u"Shutting down threads"
		exitapp[0] = True
		try:
			lcd.clear()
			lcd.message(u"Exiting...")
			time.sleep(1)
			lcd.clear()
			lcd.cleanup()
		except:
			pass
		dc.join()
		mc.join()
		logging.info(u"Exiting...")
