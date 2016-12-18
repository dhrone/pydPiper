#!/usr/bin/python.pydKeg
# coding: UTF-8

# pydkeg service to display curent status of Kegs
# Written by: Ron Ritchey

from __future__ import unicode_literals
import json, threading, logging, Queue, time, sys, getopt, moment, signal, commands, os, copy, imp
import displays
import sources
import pydKeg_config


try:
	import pyowm
except ImportError:
	pass


exitapp = [ False ]

class keg_controller(threading.Thread):
	# Receives updates from keg services
	# Determines what page to displays
	# Sends relevant updates to display_controller

	# kegdata variables.
	# Includes all from kegdata class plus environmentals

	kegdata_init = {
		'name':u'',
		'description':u'',
		'ABV':0.0,
		'IBU':0.0,
		'weight':0,
		'current_tempc':0,
		'current_tempf':0,
		'disk_avail':0,
		'disk_availp':0,
		'current_time':u"",
		'current_time_sec':u"",
		'current_time_formatted':u"",
		'current_ip':u"",
		'outside_conditions':'No Data',
		'outside_temp_min':0,
		'outside_temp_max':0,
		'outside_temp_formatted':'',
		'system_temp_formatted':''
	}


	def __init__(self, servicelist, display_controller, showupdates=False):
		threading.Thread.__init__(self)

		self.daemon = True
		self.kegqueue = Queue.Queue()
		self.image = None
		self.showupdates = showupdates
		self.display_controller = display_controller

		self.kegdata = copy.deepcopy(self.kegdata_init)
		self.kegdata_prev = copy.deepcopy(self.kegdata)
		self.servicelist = servicelist
		self.services = { }

		# Attempt to initialize services
		self.initservices()

		# Lock used to prevent simultaneous update of the kegdata dictionary
		self.kegdata_lock = threading.Lock()


	def initservices(self):

		kegservice = None
		kegservice = sources.kegdata.kegdata(self.kegqueue )

	def run(self):

		logging.debug(u"Keg Controller Starting")

		# Start the thread that updates the system variables
		sv_t = threading.Thread(target=self.updatesystemvars)
		sv_t.daemon = True
		sv_t.start()
		timesongstarted = 0


		# Force the system to recognize the start state as a change
		#####  Need to determine how to force a display update on start-up #####

		lastupdate = 0 # Initialize variable to be used to force updates every second regardless of the receipt of a source update
		while not exitapp[0]:

			updates = { }

			# Attempt to get an update from the queue
			try:
				updates = self.kegqueue.get_nowait()
				self.kegqueue.task_done()
			except Queue.Empty:
				pass


			with self.kegdata_lock:
				# Update kegdata based upon received message
				for item, value in updates.iteritems():
					self.kegdata[item] = value


			# If anything has changed, update pages
			if self.kegdata != self.kegdata_prev or lastupdate < time.time():

				# Set lastupdate time to 1 second in the future
				lastupdate = time.time()+1

				######  May want to eliminate updatepages ######
				self.updatepages()

				# Print the current contents of kegdata if showupdates is True
				if self.showupdates:
					ctime = moment.utcnow().timezone(u"US/Eastern").strftime("%-I:%M:%S %p").strip()
					print u"Status at time {0}".format(ctime)

					with self.kegdata_lock:
						for item,value in self.kegdata.iteritems():
							try:
								print u"    [{0}]={1} {2}".format(item,repr(value), type(value))
							except:
								print u"err"
								print u"[{0}] =".format(item)
								print type(value)
								print repr(value)
						print u"\n"

				# Update kegdta_prev
				with self.kegdata_lock:
					for item, value in self.kegdata.iteritems():
						try:
							if self.kegdata_prev[item] != value:
								self.kegdata_prev[item] = value
						except KeyError:
							self.kegdata_prev[item] = value

			# Update display data every 1/4 second
			time.sleep(.25)


	def updatepages(self):

		with self.kegdata_lock:
			self.kegdata[u'time_formatted'] = moment.utcnow().timezone(pydKeg_config.TIMEZONE).strftime('%H:%M').strip().decode()
#			self.kegdata[u'time_ampm'] = current_time_ampm

			# To support previous key used for this purpose
			self.kegdata[u'current_time_formatted'] = self.kegdata[u'time_formatted']

			# Update display controller
			# The primary call to this routine is in main but this call is needed to catch variable changes before kegdata_prev is updated.
			self.display_controller.next()



	def updatesystemvars(self):
		while True:
			try:
				current_time_ampm = moment.utcnow().timezone(pydKeg_config.TIMEZONE).strftime(u"%p").strip().decode()
				if pydKeg_config.TIME24HOUR == True:
					current_time = moment.utcnow().timezone(pydKeg_config.TIMEZONE).strftime(u"%H:%M").strip().decode()
					current_time_sec = moment.utcnow().timezone(pydKeg_config.TIMEZONE).strftime(u"%H:%M:%S").strip().decode()
				else:
					current_time = moment.utcnow().timezone(pydKeg_config.TIMEZONE).strftime(u"%-I:%M %p").strip().decode()
					current_time_sec = moment.utcnow().timezone(pydKeg_config.TIMEZONE).strftime(u"%-I:%M:%S %p").strip().decode()
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
			outside_conditions = u'No data'
			outside_temp_formatted = u'0'
			outside_temp_max_formatted = u'0'
			outside_temp_min_formatted = u'0'

			try:
				owm = pyowm.OWM(pydKeg_config.OWM_API)
				obs = owm.weather_at_coords(pydKeg_config.OWM_LAT, pydKeg_config.OWM_LON)
				fc = owm.daily_forecast_at_coords(pydKeg_config.OWM_LAT, pydKeg_config.OWM_LON)
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
				if pydKeg_config.TEMPERATURE.lower() == u'celsius':
					outside_temp = outside_tempc
					outside_temp_max = int(outside_temp_maxc)
					outside_temp_min = int(outside_temp_minc)
					outside_temp_formatted = u"{0}°C".format(int(outside_temp))
					outside_temp_max_formatted = u"{0}°C".format(int(outside_temp_max))
					outside_temp_min_formatted = u"{0}°C".format(int(outside_temp_min))
				else:
					outside_temp = outside_tempf
					outside_temp_max = int(outside_temp_maxf)
					outside_temp_min = int(outside_temp_minf)
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
				if pydKeg_config.TEMPERATURE.lower() == u'celsius':
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

			with self.kegdata_lock:
				self.kegdata[u'system_temp'] = system_temp
				self.kegdata[u'system_temp_formatted'] = system_temp_formatted

				self.kegdata[u'system_tempc'] = system_tempc
				self.kegdata[u'system_tempf'] = system_tempf

				# For backward compatibility
				self.kegdata[u'current_tempc'] = self.kegdata[u'system_tempc']
				self.kegdata[u'current_tempf'] = self.kegdata[u'system_tempf']

				self.kegdata[u'disk_avail'] = avail
				self.kegdata[u'disk_availp'] = availp
				self.kegdata[u'disk_used'] = used
				self.kegdata[u'disk_usedp'] = usedp

				self.kegdata[u'time'] = current_time
				self.kegdata[u'time_ampm'] = current_time_ampm
				# note: 'time_formatted' is computed during page processing as it needs the value of the strftime key contained on the line being displayed

				# For backwards compatibility
				self.kegdata[u'current_time'] = current_time
				self.kegdata[u'current_time_sec'] = current_time

				self.kegdata[u'ip'] = current_ip.decode()

				# For backwards compatibility
				self.kegdata[u'current_ip'] = current_ip.decode()

				self.kegdata[u'outside_temp'] = outside_temp
				self.kegdata[u'outside_temp_max'] = outside_temp_max
				self.kegdata[u'outside_temp_min'] = outside_temp_min
				self.kegdata[u'outside_temp_formatted'] = outside_temp_formatted
				self.kegdata[u'outside_temp_max_formatted'] = outside_temp_max_formatted
				self.kegdata[u'outside_temp_min_formatted'] = outside_temp_min_formatted
				self.kegdata[u'outside_conditions'] = outside_conditions

			# Read environmentals every 20 seconds
			time.sleep(20)

def sigterm_handler(_signo, _stack_frame):
        sys.exit(0)

if __name__ == u'__main__':
	signal.signal(signal.SIGTERM, sigterm_handler)

	# Changing the system encoding should no longer be needed
#	if sys.stdout.encoding != u'UTF-8':
#    		sys.stdout = codecs.getwriter(u'utf-8')(sys.stdout, u'strict')

	logging.basicConfig(format=u'%(asctime)s:%(levelname)s:%(message)s', filename=pydKeg_config.LOGFILE, level=pydKeg_config.LOGLEVEL)
	logging.getLogger().addHandler(logging.StreamHandler())
	logging.getLogger(u'socketIO-client').setLevel(logging.WARNING)

	# Move unhandled exception messages to log file
	def handleuncaughtexceptions(exc_type, exc_value, exc_traceback):
		if issubclass(exc_type, KeyboardInterrupt):
			sys.__excepthook__(exc_type, exc_value, exc_traceback)
			return

		logging.error(u"Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))
		try:
			if len(mc.kegdata) > 0:
				logging.error(u"Player status at exception")
				logging.error(unicode(mc.kegdata))
		except NameError:
			# If this gets called before the keg controller is instantiated, ignore it
			pass

		sys.__excepthook__(exc_type, exc_value, exc_traceback)


	sys.excepthook = handleuncaughtexceptions

	# Suppress libraries INFO messages
	loggingPIL = logging.getLogger(u'PIL')
	loggingPIL.setLevel( logging.WARN )

	# try:
	# 	opts, args = getopt.getopt(sys.argv[1:],u"d:",[u"driver=", u"lms",u"mpd",u"spop",u"rune",u"volumio",u"pages=", u"showupdates"])
	# except getopt.GetoptError:
	# 	print u'pydKeg.py -d <driver> --mpd --spop --lms --rune --volumio --pages --showupdates'
	# 	sys.exit(2)

	services_list = [ ]
	driver = ''
	showupdates = False
	pagefile = 'pages_beer.py'

	# for opt, arg in opts:
	# 	if opt == u'-h':
	# 		print u'pydKeg.py -d <driver> --mpd --spop --lms --rune --volumio --pages --showupdates'
	# 		sys.exit()
	# 	elif opt in (u"-d", u"--driver"):
	# 		driver = arg
	# 	elif opt in (u"--mpd"):
	# 		services_list.append(u'mpd')
	# 	elif opt in (u"--spop"):
	# 		services_list.append(u'spop')
	# 	elif opt in (u"--lms"):
	# 		services_list.append(u'lms')
	# 	elif opt in (u"--rune"):
	# 		services_list.append(u'rune')
	# 	elif opt in (u"--volumio"):
	# 		services_list.append(u'volumio')
	# 	elif opt in (u"--pages"):
	# 		pagefile = arg
	# 		# print u"Loading {0} as page file".format(arg)
	# 		# If page file provided, try to load provided file on top of default pages file
	# 		# try:
	# 		# 	newpages = imp.load_source(u'pages', arg)
	# 		# 	if validpages(newpages):
	# 		# 		pages = newpages
	# 		# 	else:
	# 		# 		print u"Invalid page file provided.  Using default pages."
	# 		# except IOError:
	# 		# 	# Page file not found
	# 		# 	print u"Page file {0} not found.  Using default pages".format(arg)
	#
	# 	elif opt in (u"--showupdates"):
	# 		showupdates = True
	#
	#
	# if len(services_list) == 0:
	# 	logging.critical(u"Must have at least one keg service to monitor")
	# 	sys.exit()

	logging.info(pydKeg_config.STARTUP_LOGMSG)

	dq = Queue.Queue()

	pin_rs = pydKeg_config.DISPLAY_PIN_RS
	pin_e = pydKeg_config.DISPLAY_PIN_E
	pins_data = pydKeg_config.DISPLAY_PINS_DATA
	rows = pydKeg_config.DISPLAY_HEIGHT
	cols = pydKeg_config.DISPLAY_WIDTH

	# Choose display

	if not driver:
		driver = pydKeg_config.DISPLAY_DRIVER


	if driver == u"lcd_display_driver_winstar_weh001602a":
		lcd = displays.lcd_display_driver_winstar_weh001602a.lcd_display_driver_winstar_weh001602a(rows, cols, pin_rs, pin_e, pins_data)
	elif driver == u"lcd_display_driver_winstar_ws0010_graphics_mode":
		lcd = displays.lcd_display_driver_winstar_ws0010_graphics_mode.lcd_display_driver_winstar_ws0010_graphics_mode(rows, cols, pin_rs, pin_e, pins_data)
	elif driver == u"lcd_display_driver_hd44780":
		lcd = displays.lcd_display_driver_hd44780.lcd_display_driver_hd44780(rows, cols, pin_rs, pin_e, pins_data)
	elif driver == u"lcd_display_driver_curses":
		lcd = displays.lcd_display_driver_curses.lcd_display_driver_curses(rows, cols)
	else:
		logging.critical(u"No valid display found")
		sys.exit()

	lcd.clear()
	lcd.message(pydKeg_config.STARTUP_MSG)


	dc = displays.display.display_controller()
	mc = keg_controller(services_list, dc, showupdates)
	time.sleep(2)
	mc.start()
	dc.load(pagefile, mc.kegdata,mc.kegdata_prev, pydKeg_config.DISPLAY_SIZE)

	try:
		while True:
			# Get next image and send it to the display every .1 seconds
			with mc.kegdata_lock:
				img = dc.next()
			frame = displays.display.getframe(img, 0, 0, pydKeg_config.DISPLAY_WIDTH, pydKeg_config.DISPLAY_HEIGHT)
			lcd.update(frame)
			time.sleep(.02)


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
		mc.join()
		logging.info(u"Exiting...")
