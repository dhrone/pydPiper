#!/usr/bin/python
# coding: UTF-8

# musicdata service to read from LMS
# Written by: Ron Ritchey
from __future__ import unicode_literals

import json, threading, logging, Queue, time, sys, urllib, pylms, getopt, telnetlib, urlparse
from pylms import server
import musicdata

class musicdata_lms(musicdata.musicdata):


	def __init__(self, q, server=u'localhost', port=9090, user=u'', pwd=u'', player=u''):
		super(musicdata_lms, self).__init__(q)
		self.server = server
		self.port = port
		self.user = user
		self.pwd = pwd
		self.player = player
		self.connection_failed = 0
		self.timeout = 20
		self.idle_state = False

		self.dataserver = None
		self.dataplayer = None
		self.rawserver = None

		# Now set up a thread to listen to the channel and update our data when
		# the channel indicates a relevant key has changed
		data_t = threading.Thread(target=self.run)
		data_t.daemon = True
		data_t.start()

		# Start the idle timer
#		idle_t = threading.Thread(target=self.idlealert)
#		idle_t.daemon = True
#		idle_t.start()

#	def idlealert(self):
#
#		while True:
#			# Generate a noidle event every timeout seconds
#			time.sleep(self.timeout)
#
#			if self.idle_state:
#				try:
#					#self.dataclient.noidle()
#					self.rawclient.write("noidle\n")
#				except (NameError, IOError, AttributeError):
#					# If not idle (or not created yet) return to sleeping
#					pass


	def connectraw(self):
		# Try up to 10 times to connect to LMS
		connection_failed = 0
		self.rawserver = None

		logging.debug(u"Connecting to LMS raw service on {0}:{1}".format(self.server, self.port))
		while True:
			if connection_failed >= 10:
				logging.debug(u"Could not connect to raw LMS service")
				break
			try:
				# Connection to LMS
				self.rawserver = telnetlib.Telnet(self.server, self.port)

				# Subscribe to notification events that should wake up the system to collect data
				self.rawserver.write("subscribe pause,play,mixer,playlist\n".encode('ascii'))
				break
			except IOError:
				self.rawserver = None
				connection_failed += 1
				time.sleep(1)
		if self.rawserver is None:
			raise IOError(u"Could not connect raw to LMS")

	def connect(self):

		# Try up to 10 times to connect to LMS
		self.connection_failed = 0
		self.dataserver = None
		self.dataplayer = None

		logging.debug(u"Connecting to LMS service on {0}:{1}".format(self.server, self.port))

		while True:
			if self.connection_failed >= 10:
				logging.debug(u"Could not connect to LMS service")
				break
			try:
				# Connection to LMS
				self.dataserver = pylms.server.Server(self.server, self.port, self.user, self.pwd)
				self.dataserver.connect()

				players = self.dataserver.get_players()
				for p in players:
					if p.get_ref() == self.player:
						self.dataplayer = p
						break
				if self.dataplayer is None:
					if len(self.dataserver.get_players()) > 0:
						self.dataplayer = self.dataserver.get_players()[0]
					if self.dataplayer is None:
						logging.critical(u"Could not find any LMS Players")
						raise RuntimeError(u"Could not find any LMS Players")
					self.player = str(self.dataplayer)
				break
			except (IOError, AttributeError, IndexError):
				### Trying to debug services
				logging.error(u"LMS connect failure", exc_info=sys.exc_info())

				self.dataserver = None
				self.dataplayer = None
				self.connection_failed += 1
				time.sleep(1)
		if self.dataserver is None:
			### Trying to debug services
			logging.error(u"LMS dataserver is None", exc_info=sys.exc_info())
			raise IOError(u"Could not connect to LMS")
		else:
			logging.debug(u"Connected to LMS using player {0}".format(self.dataplayer.get_name()))


	def run(self):

		logging.debug(u"LMS musicdata service starting")

		while True:
			# Connect to the data service if needed
			if self.dataserver is None:
				try:
					# Try to connect
					self.connect()
					self.status()
					self.sendUpdate()
				except IOError:
					self.dataserver = None
					# On connection error, sleep 5 and then return to top and try again
					time.sleep(5)
					continue

			# Connect directly to the data service (for notifications) if needed
			if self.rawserver is None:
				try:
					# Try to connect
					self.connectraw()
				except IOError:
					self.rawserver = None
					# On connection error, sleep 5 and then return to top and try again
					time.sleep(5)
					continue

			try:
				# Wait for notice that state has changed
				try:
					#self.idle_state = True
					msg = self.rawserver.read_until("\n", self.timeout)
					#self.idle_state = False
					self.status()
					self.sendUpdate()
				except (IOError, EOFError):
					# Error occurred while trying to read from rawserver
					# Mark rawserver None so that it is restarted on the next pass
					self.rawserver = None
					pass

				time.sleep(.01)
			except IOError:
				self.dataserver = None
				logging.debug(u"Could not get status from LMS")
				time.sleep(5)
				continue


	def status(self):
		# Read musicplayer status and update musicdata

		state = self.dataplayer.get_mode()

		if state != u"play":
			self.musicdata[u'state'] = u"stop"
		else:

			self.musicdata[u'state'] = u"play"

		# Update values
		self.musicdata[u'artist'] = urllib.unquote(str(self.dataplayer.request("artist ?", True))).decode('utf-8')
		self.musicdata[u'title'] = urllib.unquote(str(self.dataplayer.request("title ?", True))).decode('utf-8')
		self.musicdata[u'album'] = urllib.unquote(str(self.dataplayer.request("album ?", True))).decode('utf-8')

		self.musicdata[u'volume'] = self.dataplayer.get_volume()

		self.musicdata[u'elapsed'] = int(self.dataplayer.get_time_elapsed())
		try:
			self.musicdata[u'length'] = int(self.dataplayer.get_track_duration())
		except:
			self.musicdata[u'length'] = 0

		# For backwards compatibility
		self.musicdata[u'current'] = self.musicdata[u'elapsed']
		self.musicdata[u'duration'] = self.musicdata[u'length']

		playlist_mode = int(self.dataplayer.request("playlist repeat ?", True))
		if playlist_mode == 0:
			self.musicdata[u'single'] = self.musicdata[u'repeat'] = False
		elif playlist_mode == 1:
			self.musicdata[u'single'] = True
			self.musicdata[u'repeat'] = False
		elif playlist_mode == 2:
			self.musicdata[u'single'] = False
			self.musicdata[u'repeat'] = True
		else:
			logging.debug(u"Unexpected value received when querying playlist mode status (e.g. single, repeat)")
			self.musicdata[u'single'] = self.musicdata[u'repeat'] = False

		shuffle_mode = int(self.dataplayer.request("playlist shuffle ?", True))
		if shuffle_mode == 0:
			self.musicdata[u'random'] = False
		elif shuffle_mode == 1 or shuffle_mode == 2:
			self.musicdata[u'random'] = True
		else:
			logging.debug(u"Unexpected value received when querying playlist shuffle status")
			self.musicdata[u'random'] =  False


		plp = self.musicdata[u'playlist_position'] = int(self.dataplayer.request("playlist index ?"))+1
		plc = self.musicdata[u'playlist_length'] = self.dataplayer.playlist_track_count()
		# For backwards compatibility
		self.musicdata[u'playlist_count'] = self.musicdata[u'playlist_length']

		playlist_display = u"{0}/{1}".format(plp, plc)
		# If the track count is greater than 1, we are playing from a playlist and can display track position and track count
		if plc > 1:
			playlist_display = u"{0}/{1}".format(plp, plc)
			self.musicdata[u'stream'] = u'not webradio'
		# if the track count is exactly 1, this is either a short playlist or it is streaming
		elif plc == 1:
			try:
				# if streaming
				if self.musicdata['length'] == 0.0:
					playlist_display = u"Radio"
					self.musicdata[u'stream'] = u'webradio'
				# it really is a short playlist
				else:
					playlist_display = u"{0}/{1}".format(plp, plc)
					self.musicdata[u'stream'] = u'not webradio'
			except KeyError:
				logging.debug(u"In LMS couldn't get valid track information")
				playlist_display = u""
				self.musicdata[u'stream'] = u'not webradio'
		else:
			logging.debug(u"In LMS track length is <= 0")
			playlist_display = u""
			self.musicdata[u'stream'] = u''

		self.musicdata[u'playlist_display'] = playlist_display

		self.musicdata[u'musicdatasource'] = u"LMS"

		url = self.dataplayer.get_track_path().decode()
		self.musicdata[u'uri'] = url

		urlp = urlparse.urlparse(url)
		if urlp.scheme.lower() == u'wimp':
			self.musicdata[u'actPlayer'] = u'tidal'
		elif urlp.scheme.lower() == u'http':
			# Extract out domain name
			try:
				self.musicdata[u'actPlayer'] = urlp.netloc.split(u'.')[len(urlp.netloc.split(u'.'))-2]
			except IndexError:
				self.musicdata[u'actPlayer'] = urlp.netloc
		else:
			self.musicdata[u'actPlayer'] = urlp.scheme


		# Get bitrate and tracktype if they are available.  Try blocks used to prevent array out of bounds exception if values are not found
		try:
			self.musicdata[u'bitrate'] = urllib.unquote(str(self.dataplayer.request("songinfo 2 1 url:"+url+" tags:r", True))).decode(u'utf-8').split(u"bitrate:", 1)[1]
		except:
			self.musicdata[u'bitrate'] = u""

		try:
			self.musicdata[u'encoding'] = urllib.unquote(str(self.dataplayer.request("songinfo 2 1 url:"+url+" tags:o", True))).decode(u'utf-8').split(u"type:",1)[1]
		except:
			self.musicdata[u'encoding'] = u""

		self.musicdata[u'tracktype'] = self.musicdata[u'encoding']

		# if duration is not available, then suppress its display
		if int(self.musicdata[u'length']) > 0:
			timepos = time.strftime(u"%-M:%S", time.gmtime(int(self.musicdata[u'elapsed']))) + "/" + time.strftime("%-M:%S", time.gmtime(int(self.musicdata[u'length'])))
			remaining = time.strftime(u"%-M:%S", time.gmtime( int(self.musicdata[u'length']) - int(self.musicdata[u'elapsed']) ) )
		else:
			timepos = time.strftime(u"%-M:%S", time.gmtime(int(self.musicdata[u'current'])))
			remaining = timepos

		self.musicdata[u'remaining'] = remaining.decode()
		self.musicdata[u'elapsed_formatted'] = timepos.decode()

		# For backwards compatibility
		self.musicdata[u'position'] = self.musicdata[u'elapsed_formatted']

		# UNSUPPORTED VARIABLES
		self.musicdata[u'bitdepth'] = u""
		self.musicdata[u'samplerate'] = u""
		self.musicdata[u'channels'] = 0

		self.validatemusicvars(self.musicdata)

if __name__ == u'__main__':

	logging.basicConfig(format='%(asctime)s:%(levelname)s:%(message)s', filename=u'musicdata_lms.log', level=logging.DEBUG)
	logging.getLogger().addHandler(logging.StreamHandler())

	try:
		opts, args = getopt.getopt(sys.argv[1:],u"hs:p:u:w:l:",[u"server=",u"port=",u"user=",u"pwd=",u"player="])
	except getopt.GetoptError:
		print u'musicdata_lms.py -s <server> -p <port> -u <user> -w <password> -l <player>'
		sys.exit(2)

	# Set defaults
	server = u'localhost'
	port = 9090
	user = ''
	pwd= u''
	player = u''

	for opt, arg in opts:
		if opt == u'-h':
			print u'musicdata_lms.py -s <server> -p <port> -u <user> -w <password> -l <player>'
			sys.exit()
		elif opt in (u"-s", u"--server"):
			server = arg
		elif opt in (u"-p", u"--port"):
			port = arg
		elif opt in (u"-u", u"--user"):
			user = arg
		elif opt in (u"-w", u"--pwd"):
			pwd = arg
		elif opt in (u"-l", u"--player"):
			player = arg


	import sys
	q = Queue.Queue()
	mdr = musicdata_lms(q, server, port, user, pwd, player)

	try:
		start = time.time()
		while True:
			if start+120 < time.time():
				break;
			try:
				item = q.get(timeout=1000)
				print u"+++++++++"
				for k,v in item.iteritems():
					print u"[{0}] '{1}' type {2}".format(k,v,type(v))
				print u"+++++++++"
				print
				q.task_done()
			except Queue.Empty:
				pass
	except KeyboardInterrupt:
		print u''
		pass

	print u"Exiting..."
