#!/usr/bin/python
# coding: UTF-8

# musicdata service to read from RuneAudio
# Written by: Ron Ritchey
from __future__ import unicode_literals

import json, redis, threading, logging, Queue, time, getopt, sys, logging
import musicdata

class musicdata_rune(musicdata.musicdata):

	def __init__(self, q, server=u'localhost', port=6379, pwd=u''):
		super(musicdata_rune, self).__init__(q)
		self.server = server
		self.port = port
		self.pwd = pwd
		self.connection_failed = 0

		self.dataclient = None

		# Now set up a thread to listen to the channel and update our data when
		# the channel indicates a relevant key has changed
		data_t = threading.Thread(target=self.run)
		data_t.daemon = True
		data_t.start()


	def connect(self):

		# Try up to 10 times to connect to REDIS
		self.connection_failed = 0

		logging.debug(u"Connecting to Rune Redis service on {0}:{1}".format(self.server, self.port))

		while True:
			if self.connection_failed >= 10:
				logging.debug(u"Could not connect to Rune Redis service")
				raise RuntimeError(u"Could not connect to Rune Redis service")
			try:
				# Connection to REDIS
				client = redis.StrictRedis(self.server, self.port, self.pwd)

				# Configure REDIS to send keyspace messages for set events
				client.config_set(u'notify-keyspace-events', u'KEA')
				self.dataclient = client
				logging.debug(u"Connected to Rune Redis service")
				break
			except:
				self.dataclient = None
				self.connection_failed += 1
				time.sleep(1)


	def subscribe(self):
		# Try to subscribe.  If you fail, reconnect and try again.
		# If you fail, allow the resulting exception to be passed on.

		try:
			# Create a pubsub to receive messages
			self.pubsub = self.dataclient.pubsub(ignore_subscribe_messages=True)

			# Subscribe to act_player_info keyspace events
			self.pubsub.psubscribe(u'__key*__:act_player_info')
		except redis.ConnectionError:
			self.connect()

			# Try again to subscribe
			# Create a pubsub to receive messages
			self.pubsub = self.dataclient.pubsub(ignore_subscribe_messages=True)

			# Subscribe to act_player_info keyspace events
			self.pubsub.subscribe(u'__key*__:act_player_info')

	def run(self):

		logging.debug(u"RUNE musicdata service starting")

		while True:
			if self.dataclient is None:
				try:
					# Try to connect
					self.connect()
					self.subscribe()
					self.status()
					self.sendUpdate()
				except (redis.ConnectionError, RuntimeError):
					self.dataclient = None
					# On connection error, sleep 5 and then return to top and try again
					time.sleep(5)
					continue
			try:
				# Wait for notice that key has changed
				msg = self.pubsub.get_message()
				if msg:
					# act_player_info key event occured
					self.status()
					self.sendUpdate()
				time.sleep(.01)
			except (redis.ConnectionError, RuntimeError):
				# if we lose our connection while trying to query DB
				# sleep 5 and then return to top to try again
				self.dataclient = None
				logging.debug(u"Could not get status from Rune Redis service")
				time.sleep(5)
				continue


	def status(self):
		# Read musicplayer status and update musicdata
		try:
			msg = self.dataclient.get(u'act_player_info')
			status = json.loads(msg)
		except ValueError:
			logging.debug(u"Bad status message received.  Contents were {0}".format(msg))
			raise RuntimeError(u"Bad status message received.")
		except:
			# Caught something else.  Report it and then inform calling function that the connection is bad
			e = sys.exc_info()[0]
			logging.debug(u"Caught {0} trying to get status from Rune".format(e))
			raise RuntimeError(u"Could not get status from Rune")



		state = status.get(u'state')
		if state != u"play":
			self.musicdata[u'state'] = u"stop"
		else:
			self.musicdata[u'state'] = u"play"

		# Update remaining variables
		self.musicdata[u'artist'] = status[u'currentartist'] if u'currentartist' in status else u""
		self.musicdata[u'title'] = status[u'currentsong'] if u'currentsong' in status else u""
		self.musicdata[u'album'] = status[u'currentalbum'] if u'currentalbum' in status else u""
		self.musicdata[u'volume'] = self.intn(status[u'volume']) if u'volume' in status else 0
		self.musicdata[u'length'] = self.intn(status[u'time']) if u'time' in status else 0
		self.musicdata[u'elapsed'] = self.intn(status[u'elapsed']) if u'elapsed' in status else 0
		self.musicdata[u'actPlayer'] = status[u'actPlayer'] if u'actPlayer' in status else u""
		self.musicdata[u'single'] = bool(self.intn(status[u'single'])) if u'single' in status else False
		self.musicdata[u'random'] = bool(self.intn(status[u'random'])) if u'random' in status else False
		self.musicdata[u'repeat'] = bool(self.intn(status[u'repeat'])) if u'repeat' in status else False
		self.musicdata[u'musicdatasource'] = u"Rune"

		# For backwards compatibility
		self.musicdata[u'duration'] = self.musicdata[u'length']
		self.musicdata[u'current'] = self.musicdata[u'elapsed']

		# Set default values
		self.musicdata[u'samplerate'] = u""
		self.musicdata[u'bitrate'] = u""
		self.musicdata[u'channels'] = 0
		self.musicdata[u'bitdepth'] = u""
		self.musicdata[u'tracktype'] = u""
		self.musicdata[u'encoding'] = u""
		self.musicdata[u'tracktype'] = u""

		if self.musicdata[u'actPlayer'] == u'Spotify':
			self.musicdata[u'bitrate'] = u"320 kbps"
			plp = self.musicdata[u'playlist_position'] = self.intn(status[u'song'])+1 if u'song' in status else 0
			plc = self.musicdata[u'playlist_length'] = self.intn(status[u'playlistlength']) if u'playlistlength' in status else 0

			# For backwards compatibility
			self.musicdata[u'playlist_count'] = self.musicdata[u'playlist_length']

			self.musicdata[u'playlist_display'] = u"{0}/{1}".format(plp, plc)
			self.musicdata[u'actPlayer'] = u"Spotify"
			self.musicdata[u'tracktype'] = u"Spotify"
			self.musicdata[u'stream'] = u'not webradio'

		elif self.musicdata[u'actPlayer'] == u'MPD':
			plp = self.musicdata[u'playlist_position'] = self.intn(status[u'song'])+1 if u'song' in status else 0
			plc = self.musicdata[u'playlist_length'] = self.intn(status[u'playlistlength']) if u'playlistlength' in status else 0

			# For backwards compatibility
			self.musicdata[u'playlist_count'] = self.musicdata[u'playlist_length']

			self.musicdata[u'bitrate'] = u"{0} kbps".format(status[u'bitrate']) if u'bitrate' in status else u""

			# if radioname is None then this is coming from a playlist (e.g. not streaming)
			if status.get(u'radioname') == None:
				self.musicdata[u'playlist_display'] = u"{0}/{1}".format(plp, plc)
				self.musicdata[u'stream'] = u'not webradio'
			else:
				self.musicdata[u'playlist_display'] = u"Radio"
				self.musicdata[u'stream'] = u'webradio'
				# if artist is empty, place radioname in artist field
				if self.musicdata[u'artist'] == u"" or self.musicdata[u'artist'] is None:
					self.musicdata[u'artist'] = status[u'radioname'] if u'radioname' in status else u""


			audio = status[u'audio'] if u'audio' in status else None
			chnum = 0
			if audio is None:
				tracktype = u"MPD"
			else:
				audio = audio.split(u':')
				if len(audio) == 3:
					sample = round(float(audio[0])/1000,1)
				 	bits = audio[1]
					chnum = int(audio[2])
				 	if audio[2] == u'1':
						channels = u'Mono'
				 	elif audio[2] == u'2':
					 	channels = u'Stereo'
				 	elif int(audio[2]) > 2:
					 	channels = u'Multi'
				 	else:
					 	channels = u""

			 	 	if channels == u"":
					 	tracktype = u"{0} bit, {1} kHz".format(bits, sample)
				 	else:
				 		tracktype = u"{0} {1} bit {2} kHz".format(channels, bits, sample)
				else:
					# If audio information not available just send that MPD is the source
					tracktype = u"MPD"

			self.musicdata[u'tracktype'] = tracktype
			self.musicdata[u'channels'] = chnum

		elif self.musicdata[u'actPlayer'] == u'Airplay':
			self.musicdata[u'playlist_position'] = 1
			self.musicdata[u'playlist_count'] = 1
			self.musicdata[u'playlist_length'] = 1
			self.musicdata[u'tracktype'] = u"Airplay"
			self.musicdata[u'playlist_display'] = u"Aplay"
			self.musicdata[u'stream'] = u'not webradio'
		
		else:
			# Unexpected player type
			logging.debug(u"Unexpected player type {0} discovered".format(actPlayer))
			self.musicdata[u'playlist_position'] = 1
			self.musicdata[u'playlist_count'] = 1
			self.musicdata[u'playlist_length'] = 1
			self.musicdata[u'tracktype'] = actPlayer
			self.musicdata[u'playlist_display'] = u"Radio"
			self.musicdata[u'stream'] = u'webradio'

		# if duration is not available, then suppress its display
		if int(self.musicdata[u'length']) > 0:
			timepos = time.strftime(u"%-M:%S", time.gmtime(int(self.musicdata[u'elapsed']))) + "/" + time.strftime(u"%-M:%S", time.gmtime(int(self.musicdata[u'length'])))
			remaining = time.strftime(u"%-M:%S", time.gmtime( int(self.musicdata[u'length']) - int(self.musicdata[u'elapsed']) ) )
		else:
			timepos = time.strftime(u"%-M:%S", time.gmtime(int(self.musicdata[u'elapsed'])))
			remaining = timepos

		self.musicdata[u'remaining'] = remaining.decode()
		self.musicdata[u'elapsed_formatted'] = timepos.decode()

		# For backwards compatibility
		self.musicdata[u'position'] = self.musicdata[u'elapsed_formatted']

		self.validatemusicvars(self.musicdata)


if __name__ == u'__main__':

	logging.basicConfig(format='%(asctime)s:%(levelname)s:%(message)s', filename=u'musicdata_rune.log', level=logging.DEBUG)
	logging.getLogger().addHandler(logging.StreamHandler())

	try:
		opts, args = getopt.getopt(sys.argv[1:],u"hs:p:w:",[u"server=",u"port=",u"pwd="])
	except getopt.GetoptError:
		print u'musicdata_rune.py -s <server> -p <port> -w <password>'
		sys.exit(2)

	# Set defaults
	server = u'localhost'
	port = 6379
	pwd= u''

	for opt, arg in opts:
		if opt == u'-h':
			print u'musicdata_rune.py -s <server> -p <port> -w <password>'
			sys.exit()
		elif opt in (u"-s", u"--server"):
			server = arg
		elif opt in (u"-p", u"--port"):
			port = arg
		elif opt in (u"-w", u"--pwd"):
			pwd = arg


	import sys
	q = Queue.Queue()
	mdr = musicdata_rune(q, server, port, pwd)

	try:
		start = time.time()
		while True:
			if start+120 < time.time():
				break;
			try:
				item = q.get(timeout=1000)
				print u"++++++++++"
				for k,v in item.iteritems():
					print u"[{0}] '{1}' type {2}".format(k,v,type(v))
				print u"++++++++++"
				print
				q.task_done()
			except Queue.Empty:
				pass
	except KeyboardInterrupt:
		print u''
		pass

	print u"Exiting..."
