#!/usr/bin/python
# coding: UTF-8

# musicctrl service to manage reading from active services
# Written by: Ron Ritchey

import json, threading, logging, Queue, time, sys, getopt, moment, signal, commands, os
import musicdata_mpd, musicdata_lms, musicdata_spop, musicdata_rune
import pages
import music_display_config

from drivers import lcd_display_driver_winstar_weh001602a


class display_controller(threading.Thread):
	# Receives updates from music_controller and places them onto displays
	def __init__(self, displayqueue, lcd):
		threading.Thread.__init__(self)

		self.daemon = True

		self.displayqueue = displayqueue
		self.lcd = lcd
		self.lcd.switchcustomchars(lcd.FONT_ICONS)

	def run(self):

		lines = []
		columns = []

		for i in range (0, self.lcd.rows):
		  lines.append("")
		  columns.append(0)

		# Get first display update off of the queue
		item = self.displayqueue.get()
		self.displayqueue.task_done()

		self.lcd.clear()

		for i in range(len(item)):
		  # Convert from Unicode to UTF-8
		  #item[i] = item[i].encode("utf-8")
		  lines[i] = item[i]
		  #self.lcd.setCursor(0,i)
		  self.lcd.message( lines[i][0:self.lcd.cols], i, 0 )

		prev_time = time.time()

		while True:
			short_lines=True

			# Smooth animation
			if time.time() - prev_time < music_display_config.ANIMATION_SMOOTHING:
				time.sleep(music_display_config.ANIMATION_SMOOTHING-(time.time()-prev_time))
			try:
				# Determine if any lines have been updated and if yes display them
				for i in range(len(item)):

					# Convert from Unicode into UTF-8
					#item[i] = item[i].encode("utf-8")
					# Check if line is longer than display
					if len(item[i])>self.lcd.cols:
						short_lines = False

					# Check if line has been updated
					if lines[i] != item[i]:
						# Create a line to print that is at least as long as the existing line
						# This is to erase any extraneous characters on the display
						buf = item[i].ljust(len(lines[i]))

						# Reset cursor to beginning of changed line and then display the change
						#self.lcd.setCursor(0,i)
						self.lcd.message(buf[0:self.lcd.cols], i, 0)
						print "sending {0} at position {1}:{2}".format(buf[0:self.lcd.cols], 0, i)

						# Update the local line data and reset the column position for the line
						lines[i] = item[i]
						columns[i] = 0

				# If lines all fit on display then we can wait for new input
				if short_lines:
					item=self.displayqueue.get()
					self.displayqueue.task_done()
				else:
					# Update all long lines
					for i in range(len(lines)):
						if len(lines[i])>lcd.cols:
							buf = "%s          %s" % (lines[i], lines[i][0:self.lcd.cols-1])
							#buf = "{}		{}".format(lines[i],lines[i][0:DISPLAY_WIDTH-1])
							#buf = lines[i]+"		  "+lines[i][0:c]

							columns[i] = columns[i]+1
							if columns[i] > len(buf)-self.lcd.cols:
								columns[i]=0

							#self.lcd.setCursor(0,i)
							print "sending {0} at position {1}:{2}".format(buf[columns[i]:columns[i]+self.lcd.cols], 0, i)

							# Print the portion of the string that is currently visible
							self.lcd.message(buf[columns[i]:columns[i]+self.lcd.cols], i, 0)
					# Since we have to continue updating the display, check for a new update but don't block
					item=self.displayqueue.get_nowait()
					self.displayqueue.task_done()


				prev_time = time.time()
			except Queue.Empty:
				prev_time = time.time()
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
		'current':0,
		'remaining':u"",
		'duration':0,
		'position':u"",
		'volume':0,
		'playlist_display':u"",
		'playlist_position':0,
		'playlist_count':0,
		'bitrate':u"",
		'type':u"",
		'current_tempc':0,
		'current_tempf':0,
		'disk_avail':0,
		'disk_availp':0,
		'current_time':u"",
		'current_time_sec':u"",
		'current_time_formatted':u"",
		'current_ip':u""
	}


	def __init__(self, displayqueue, servicelist, rows, cols):
		threading.Thread.__init__(self)

		self.daemon = True

		self.displayqueue = displayqueue
		self.musicqueue = Queue.Queue()
		self.rows = rows
		self.cols = cols

		self.musicdata = self.musicdata_init.copy()
		self.musicdata_prev = self.musicdata.copy()
		self.servicelist = servicelist
		self.services = { }

		# Attempt to initialize services
		self.initservices()

		# Lock used to prevent simultaneous update of the musicdata dictionary
		self.musicdatalock = False


	def initservices(self):

		# Make sure that if rune is selected that is is the only service that is selected
		if "rune" in self.servicelist and len(self.servicelist) > 1:
			logging.critical("Rune service can only be used alone")
			raise RuntimeError("Rune service can only be used alone")

		for s in self.servicelist:
			s = s.lower()
			if s == "mpd":
				musicservice = musicdata_mpd.musicdata_mpd(self.musicqueue, music_display_config.MPD_SERVER, music_display_config.MPD_PORT, music_display_config.MPD_PASSWORD)
			elif s == "spop":
				musicservice = musicdata_spop.musicdata_spop(self.musicqueue, music_display_config.SPOP_SERVER, music_display_config.SPOP_PORT, music_display_config.SPOP_PASSWORD)
			elif s == "lms":
				musicservice = musicdata_lms.musicdata_lms(self.musicqueue, music_display_config.LMS_SERVER, music_display_config.LMS_PORT, music_display_config.LMS_USER, music_display_config.LMS_PASSWORD, music_display_config.LMS_PLAYER)
			elif s == "rune":
				musicservice = musicdata_rune.musicdata_rune(self.musicqueue, music_display_config.RUNE_SERVER, music_display_config.RUNE_PORT, music_display_config.RUNE_PASSWORD)
			else:
				logging.debug("Unsupported music service {0} requested".format(s))
				continue
			self.services[s] = musicservice



	def run(self):

		logging.debug("Music Controller Starting")

		# Start the thread that updates the system variables
		sv_t = threading.Thread(target=self.updatesystemvars)
		sv_t.daemon = True
		sv_t.start()
		timesongstarted = 0

		self.current_page_number = -1
		self.current_line_number = 0
		self.page_expires = 0
		self.hesitation_expires = 0
		self.curlines = []
		self.hesitate_expires = []
		self.alert_mode = False
		self.alert_check = False

		# Reset all of the alert message cooling values
		for pl in pages.ALERT_LIST:
			pl['cooling_expires'] = 0

		# Force the system to recognize the start state as a change
		#####  Need to determine how to force a display update on start-up #####
		self.musicdata_prev['state'] = ""

		while True:

			updates = { }
			# Attempt to get an update from the queue
			try:
				updates = self.musicqueue.get_nowait()
				self.musicqueue.task_done()
			except Queue.Empty:
				pass

			while self.musicdatalock:
				sleep(.001)
			self.musicdatalock = True
			# Update musicdata based upon received message
			for item, value in updates.iteritems():
				self.musicdata[item] = value

			# Update song timing variables
			if 'current' in updates:
				self.musicdata['current'] = updates['current']
				timesongstarted = time.time() - self.musicdata['current']
				print "Setting timesongstarted to {0}".format(timesongstarted)
				print "current = {0}".format(self.musicdata['current'])
			else:
				if timesongstarted > 0:
					self.musicdata['current'] = time.time() - timesongstarted
					print "current = :{0}:".format(self.musicdata['current'])

			# If the value of current has changed then update the other related timing variables
			if self.musicdata['current'] != self.musicdata_prev['current']:
				if self.musicdata['duration'] > 0:
					timepos = time.strftime("%M:%S", time.gmtime(self.musicdata['current'])) + "/" + time.strftime("%M:%S", time.gmtime(self.musicdata['duration']))
					remaining = time.strftime("%M:%S", time.gmtime(self.musicdata['duration'] - self.musicdata['current'] ) )

				else:
					timepos = time.strftime("%M:%S", time.gmtime(self.musicdata['current']))
					remaining = timepos
				print "In music-display current = {0}".format(self.musicdata['current'])
				self.musicdata['remaining'] = remaining
				self.musicdata['position'] = timepos
			self.musicdatalock = False

			# If anything has changed, update pages
			if self.musicdata != self.musicdata_prev:
				self.updatepages()
			else:
				# Update musicdata_prev with anything that has changed
				for item, value in updates.iteritems():
					self.musicdata_prev[item] = value
				if self.musicdata['current'] != self.musicdata_prev['current']:
					self.musicdata_prev['current'] = self.musicdata['current']
					self.musicdata_prev['remaining'] = self.musicdata['remaining']
					self.musicdata_prev['position'] = self.musicdata['position']

			# Update display data every 1/4 second
			time.sleep(.25)

	def updatepages(self):

		# Using PAGES variables, compute what to display
		state = self.musicdata.get('state')


		if state != 'play':
			current_pages = pages.PAGES_Stop
		else:
			current_pages = pages.PAGES_Play

		self.alert_check = False

		# Check to see if any alerts are triggered
		for pl in pages.ALERT_LIST:


			# Check to see if alert is in its cooling period
			if pl['cooling_expires'] < time.time():

				# Use try block to skip page if variables are missing
				try:
					# Check to see what type of monitoring to perform
					if pl['alert']['type'] == "change":
						if self.musicdata[pl['alert']['variable']] != self.musicdata_prev[pl['alert']['variable']]:
							self.musicdata_prev[pl['alert']['variable']] = self.musicdata[pl['alert']['variable']]
							# Some state changes cause variable changes like volume
							# Check to see if these dependent variable changes
							# should be suppressed
							try:
								if self.musicdata_prev['state'] == state or not pl['alert']['suppressonstatechange']:
									self.alert_check = True
							except KeyError:
								pass
					elif pl['alert']['type'] == "above":
						if self.musicdata[pl['alert']['variable']] > pl['alert']['values'][0]:
							self.alert_check = True
					elif pl['alert']['type'] == "below":
						if self.musicdata[pl['alert']['variable']] < pl['alert']['values'][0]:
							self.alert_check = True
					elif pl['alert']['type'] == "range":
						if self.musicdata[pl['alert']['variable']] > pl['alert']['values'][0] and self.musicdata[pl['alert']['variable']] < pl['alert']['values'][1]:
							self.alert_check = True

					if self.alert_check:
						self.alert_mode = True

						# Set current_pages to the alert page
						current_pages = pl
						self.current_page_number = 0
						self.current_line_number = 0
						self.page_expires = time.time() + current_pages['pages'][self.current_page_number]['duration']
						self.curlines = []
						self.hesitate_expires = []

						# Set cooling expiry time.  If not coolingperiod directive, use default
						try:
							pl['cooling_expires'] = time.time() + pl['alert']['coolingperiod']
						except KeyError:
							pl['cooling_expires'] = time.time() + music_display_config.COOLING_PERIOD

						# if an alert has been found, break out of the loop
						# this has the effect of making the order of the list the priority of the messages
						break

				except (KeyError, AttributeError, IndexError):
					pass


		# Set interruptible value.  If value not present, set to default value of True
		try:
			# interruptible is only an override until the page expires.  If page expires, allow page updates to continue.
			if self.page_expires < time.time():
				interruptible = True

				# if page just expired on an alert page then force restore to current play state
				if self.alert_mode:
					self.alert_mode = False
					self.musicdata_prev['state'] = ""
			else:
				interruptible = current_pages['interruptible']
		except KeyError:
			interruptible = True

		# check to see if we need to change the display to something new
		if (self.alert_mode or state != self.musicdata_prev['state']) and interruptible:
			self.current_page_number = -1
			self.current_line_number = 0
			self.page_expires = 0
			self.curlines = []
			self.hesitate_expires = []

			# if change caused by state change and not alert
			if self.alert_mode == False:
				self.musicdata_prev['state'] = state

				# Set to new display page
				if state != "play":
					current_pages = pages.PAGES_Stop
				# else display the PAGES_Playing pages
				else:
					current_pages = pages.PAGES_Play

		# if page has expired then move to the next page
		if self.page_expires < time.time():

			# Move to next page and check to see if it should be displayed or hidden
			for i in range(len(current_pages['pages'])):
				self.current_page_number = self.current_page_number + 1

				# if on last page, return to first page
				if self.current_page_number > len(current_pages['pages'])-1:
					self.current_page_number = 0

				self.page_expires = time.time() + current_pages['pages'][self.current_page_number]['duration']

				cp = current_pages['pages'][self.current_page_number]

				try:
					hwe = cp['hidewhenempty']
				except KeyError:
					hwe = 'False'

				try:
					hwp = cp['hidewhenpresent']
				except:
					hwp = 'False'

				# to prevent old pages format from causing problems, convert values to strings
				if type(hwe) is bool:
					hwe = str(hwe)

				if type(hwp) is bool:
					hwp = str(hwp)

				if hwe.lower() == 'all' or hwe.lower() == 'true':
					allempty = True
					try:
						hvars = cp['hidewhenemptyvars']
					except KeyError:
						hvars = [ ]

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
				elif hwe.lower() == 'any':
					anyempty = False
					try:
						hvars = cp['hidewhenemptyvars']
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

				elif hwp.lower() == 'any':
					anypresent = False
					try:
						hvars = cp['hidewhenpresentvars']
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

				elif hwp.lower() == 'all' or hwp.lower() == 'true':
					allpresent = True
					try:
						hvars = cp['hidewhenemptyvars']
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



		# Set current_page
		current_page = current_pages['pages'][self.current_page_number]

		# Now display the lines from the current page
		lines = []
		for i in range(len(current_page['lines'])):

			# make sure curlines is big enough.  curlines is used to detect when the display has changed
			# if not expanded here it will cause an IndexError later if it has not already been initialized
			while len(self.curlines) < len(current_page['lines']):
				self.curlines.append("")

			# make sure hesitate_expires is big enough as well
			while len(self.hesitate_expires) < len(current_page['lines']):
				self.hesitate_expires.append(0)

			current_line = current_page['lines'][i]
			try:
				justification = current_line['justification']
			except KeyError:
				justification = "left"

			try:
				scroll = current_line['scroll']
			except KeyError:
				scroll = False

			try:
				variables = current_line['variables']
			except KeyError:
				variables = []

			# If you have specified a strftime format on the line
			# now use it to add a formatted time to musicdata
			try:
				strftime = current_line['strftime']
			except:
				# Use 12 hour clock as default
				strftime = "%-I:%M %p"

			while self.musicdatalock:
				sleep(.001)
			self.musicdatalock = True
			self.musicdata['current_time_formatted'] = moment.utcnow().timezone(music_display_config.TIMEZONE).strftime(strftime).strip()
			self.musicdatalock = False

			format = current_line['format']

			# Get paramaters
			# ignore KeyError exceptions if variable is unavailable
			parms = []
			try:
				for j in range(len(current_line['variables'])):
					try:
						if type(self.musicdata[current_line['variables'][j]]) is unicode:
							parms.append(self.musicdata[current_line['variables'][j]].encode('utf-8'))
						else:
							parms.append(self.musicdata[current_line['variables'][j]])
					except KeyError:
						pass
			except KeyError:
				pass

			# create line to display
			line = format.format(*parms).decode('utf-8')

			# justify line
			try:
				if current_line['justification'] == "center":
					line = "{0:^{1}}".format(line, self.cols)
				elif current_line['justification'] == "right":
					line = "{0:>{1}}".format(line, self.cols)
			except KeyError:
				pass

			lines.append(line)

			# determine whether to scroll or not
			# if scroll is false, set hesitation time to large value which
			# effectively shuts off the scroll function
			if lines[i] != self.curlines[i]:
				self.curlines[i] = lines[i]
				try:
					if current_line['scroll']:
						self.hesitate_expires[i] = time.time() + music_display_config.HESITATION_TIME
					else:
						self.hesitate_expires[i] = time.time() + 86400 # Do not scroll
				except KeyError:
					self.hesitate_expires[i] = time.time() + 86400 # Do not scroll

		# Determine if the display should hesitate before scrolling
		dispval = []
		for i in range(len(lines)):
			if self.hesitate_expires[i] < time.time():
				dispval.append(lines[i])
			else:
				dispval.append(lines[i][0:self.cols])

		# Send dispval to the queue
		print lines
		self.displayqueue.put(dispval)

	def updatesystemvars(self):
		while True:
			try:
				if music_display_config.TIME24HOUR == True:
					current_time = moment.utcnow().timezone(music_display_config.TIMEZONE).strftime("%H:%M").strip()
					current_time_sec = moment.utcnow().timezone(music_display_config.TIMEZONE).strftime("%H:%M:%S").strip()
				else:
					current_time = moment.utcnow().timezone(music_display_config.TIMEZONE).strftime("%-I:%M %p").strip()
					current_time_sec = moment.utcnow().timezone(music_display_config.TIMEZONE).strftime("%-I:%M:%S %p").strip()
			except ValueError:
				# Don't know why but on exit, the moment code is occasionally throwing a ValueError
				current_time = "00:00"
				current_time_sec = "00:00:00"

			current_ip = commands.getoutput("ip -4 route get 1 | head -1 | cut -d' ' -f8 | tr -d '\n'").strip()


			try:
				file = open("/sys/class/thermal/thermal_zone0/temp")
				tempc = int(file.read())

				# Convert value to float and correct decimal place
				tempc = round(float(self.tempc) / 1000,1)

				# convert to fahrenheit
				tempf = round(self.tempc*9/5+32,1)

				file.close()
			except IOError:
				tempc = 0.0
				tempf = 0.0
			except AttributeError:
				file.close()
				tempc = 0.0
				tempf = 0.0

			try:
				# Check if running on OSX.  If yes, adjust df command
				if sys.platform == "darwin":
					p = os.popen("df /")
					line = p.readline()
					line = p.readline()
					va = line.split()
					line = "{0} {1}".format(va[3], va[4])
				else:
					# assume running on Raspberry linux
					p = os.popen("df --output='avail','pcent' /")
					line = p.readline()
					line = p.readline().strip()

				va = line.split()
				avail = va[0]
				availp = va[1]

				# remove % sign
				availp = self.availp[0:len(self.availp)-1]

				avail = int(self.avail)
				availp = int(self.availp)

				p.close()
			except IOError:
				avail = 0
				availp = 0
			except AttributeError:
				p.close()
				avail = 0
				availp = 0

			while self.musicdatalock:
				time.sleep(.001)
			self.musicdatalock = True
			self.musicdata['current_tempc'] = tempc
			self.musicdata['current_tempf'] = tempf
			self.musicdata['disk_avail'] = avail
			self.musicdata['disk_availp'] = availp
			self.musicdata['current_time'] = current_time
			self.musicdata['current_time_sec'] = current_time
			self.musicdata['current_ip'] = current_ip
			self.musicdatalock = False

		# Read environmentals every 20 seconds
		time.sleep(20)


def sigterm_handler(_signo, _stack_frame):
        sys.exit(0)

if __name__ == '__main__':
	signal.signal(signal.SIGTERM, sigterm_handler)

	logging.basicConfig(format='%(asctime)s:%(levelname)s:%(message)s', filename=music_display_config.LOGFILE, level=music_display_config.LOGLEVEL)
	logging.getLogger().addHandler(logging.StreamHandler())


	# Move unhandled exception messages to log file
	def handleuncaughtexceptions(exc_type, exc_value, exc_traceback):
		if issubclass(exc_type, KeyboardInterrupt):
			sys.__excepthook__(exc_type, exc_value, exc_traceback)
			return

		logging.error("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))
		try:
			if len(mc.musicdata) > 0:
				logging.error("Player status at exception")
				logging.error(str(mc.musicdata))
		except NameError:
			# If this gets called before the music controller is instantiated, ignore it
			pass

		sys.__excepthook__(exc_type, exc_value, exc_traceback)


	sys.excepthook = handleuncaughtexceptions

	# Suppress MPD libraries INFO messages
	loggingMPD = logging.getLogger("mpd")
	loggingMPD.setLevel( logging.WARN )

	try:
		opts, args = getopt.getopt(sys.argv[1:],"",["lms","mpd","spop","rune"])
	except getopt.GetoptError:
		print 'musicdata_mpd.py --mpd --spop --lms --rune'
		sys.exit(2)

	services = [ ]

	for opt, arg in opts:
		if opt == '-h':
			print 'musicdata_mpd.py --mpd --spop --lms --rune'
			sys.exit()
		elif opt in ("--mpd"):
			services.append('mpd')
		elif opt in ("--spop"):
			services.append('spop')
		elif opt in ("--lms"):
			services.append('lms')
		elif opt in ("--rune"):
			services.append('rune')

	if len(services) == 0:
		logging.critical("Must have at least one music service to monitor")
		sys.exit()

	logging.info(music_display_config.STARTUP_LOGMSG)

	dq = Queue.Queue()


	pin_rs = music_display_config.DISPLAY_PIN_RS
	pin_e = music_display_config.DISPLAY_PIN_E
	pins_data = music_display_config.DISPLAY_PINS_DATA
	rows = music_display_config.DISPLAY_HEIGHT
	cols = music_display_config.DISPLAY_WIDTH

	# Choose display from config file
	if music_display_config.DISPLAY_DRIVER == "lcd_display_driver_winstar_weh001602a":
		lcd = lcd_display_driver_winstar_weh001602a.lcd_display_driver_winstar_weh001602a(rows, cols, pin_rs, pin_e, pins_data)
	else:
		logging.critical("No valid display found")
		sys.exit()

	lcd.clear()
	lcd.message(music_display_config.STARTUP_MSG)

	dc = display_controller(dq, lcd)
	mc = music_controller(dq, services, lcd.rows, lcd.cols)


	dc.start()
	mc.start()

	try:
		while True:
			time.sleep(1)
	except KeyboardInterrupt:
		pass

	logging.debug("Exiting...")
