#!/usr/bin/python
# coding: UTF-8

# musicdata service to read from RuneAudio
# Written by: Ron Ritchey

import json, redis, threading, logging, Queue

class musicdata_rune(musicdata.musicdata):


	def __init__(self, q, server='localhost', port=6379, pwd=''):
		super(musicdata_rune, self).__init__(self.q)
		self.server = server
		self.port = port
		self.pwd = pwd
		self.connection_failed = 0

		self.dataclient = self.connect()

		# Now that we have a good connection, subscribe to the channels we need
		self.subscribe()

		# Now set up a thread to listen to the channel and update our data when
		# the channel indicates a relevant key has changed
		data_t = Thread(target=self.run)
		data_t = setDaemon(True)
		data_t.start()


	def connect(self):

		# Try up to 10 times to connect to REDIS
		self.connection_failed = 0
		while True:
			if self.connection_failed >= 10:
				raise RuntimeError("Could not connect to REDIS")
			try:
				# Connection to REDIS
				client = redis.StrictRedis(self.server, self.port, self.pwd)

				# Configure REDIS to send keyspace messages for set events
				client.config_set('notify-keyspace-events', 'KEA')
				return client
			except:
				self.connection_failed += 1
				sleep(1)


	def subscribe(self):
		# Try to subscribe.  If you fail, reconnect and try again.
		# If you fail, allow the resulting exception to be passed on.

		try:
			# Create a pubsub to receive messages
			self.pubsub = self.dataclient.pubsub(ignore_subscribe_messages=True)

			# Subscribe to act_player_info keyspace events
			self.pubsub.psubscribe('__key*__:act_player_info')
		except redis.ConnectionError:
			self.dataclient = self.connect()

			# Try again to subscribe
			# Create a pubsub to receive messages
			self.pubsub = self.dataclient.pubsub(ignore_subscribe_messages=True)

			# Subscribe to act_player_info keyspace events
			self.pubsub.subscribe('__key*__:act_player_info')

	def run(self):

		while True:

			try:
				item = None
				# Wait for notice that key has changed
				for item in self.pubsub.listen():
					# act_player_info key event occured
					self.status()
					self.sendUpdate()
				# Hmmm.  We have executed the for loop.  This means that the connection has failed
				raise redis.ConnectionError
			except RuntimeError, redis.ConnectionError:
				logging.debug("Could not get status from REDIS")
				sleep(10)
				try:
					self.connect()
					self.subscribe()
				except RuntimeError, redis.ConnectionError:
					logging.debug("Failed reconnect to REDIS")
					sleep(30)


	def status(self):
		# Read musicplayer status and update musicdata

		status = json.loads(self.dataclient.get('act_player_info'))

		state = status.get('state')
		if state == "play":
			self.musicdata['artist'] = status['currentartist'] if 'currentartist' in status else u""
			self.musicdata['title'] = status['currentsong'] if 'currentsong' in status else u""
			self.musicdata['album'] = status['currentalbum'] if 'currentalbum' in status else u""
			self.musicdata['volume'] = int(status['volume']) if 'volume' in status else 0
			self.musicdata['actPlayer'] = status['actPlayer'] if 'actPlayer' in status else u""
			self.musicdata['duration'] = int(status['time']) if 'time' in status else 0
			self.musicdata['current'] = int(status['elapsed']) if 'elapsed' in status else 0

			if self.musicdata['actPlayer'] == 'Spotify':
				self.musicdata['bitrate'] = "320 kbps"
				plp = self.musicdata['playlist_position'] = int(status['song'])+1 if 'song' in status else 0
				plc = self.musicdata['playlist_count'] = int(status['playlistlength']) if 'playlistlength' in status else 0
				self.musicdata['playlist_display'] = "{0}/{1}".format(plp, plc)
				self.musicdata['actPlayer'] = "Spotify"

			elif self.musicdata['actPlayer'] == 'MPD':
				plp = self.musicdata['playlist_position'] = int(status['song'])+1 if 'song' in status else 0
				plc = self.musicdata['playlist_count'] = int(status['playlistlength']) if 'playlistlength' in status else 0
				self.musicdata['bitrate'] = "{0} kbps".format(status['bitrate']) if 'bitrate' in status else u""

				# if radioname is None then this is coming from a playlist (e.g. not streaming)
				if status.get('radioname') == None:
					self.musicdata['playlist_display'] = "{0}/{1}".format(playlist_position, playlist_count)
				else:
					self.musicdata['playlist_display'] = "Streaming"
					# if artist is empty, place radioname in artist field
					if self.musicdata['artist'] == u"" or self.musicdata['artist'] is None:
						self.musicdata['artist'] = status['radioname'] if 'radioname' in status else u""

				audio = status['audio'] if 'audio' in status else None
				if audio is None:
					tracktype = u"MPD"
				else:
					audio = audio.split(':')
					if len(audio) == 3:
						sample = round(float(audio[0])/1000,1)
					 	bits = audio[1]
					 	if audio[2] == '1':
							channels = 'Mono'
					 	elif audio[2] == '2':
						 	channels = 'Stereo'
					 	elif int(audio[2]) > 2:
						 	channels = 'Multi'
					 	else:
						 	channels = u""

				 	 	if channels == u"":
						 	tracktype = "{0} bit, {1} kHz".format(bits, sample)
					 	else:
					 		tracktype = "{0}, {1} bit, {2} kHz".format(channels, bits, sample)
					else:
						# If audio information not available just send that MPD is the source
						tracktype = u"MPD"

				self.musicdata['tracktype'] = tracktype

			elif self.musicdata['actPlayer'] == 'Airplay':
				self.musicdata['playlist_position'] = 1
				self.musicdata['playlist_count'] = 1
				self.musicdata['bitrate'] = ""
				self.musicdata['tracktype'] = u"Airplay"
				self.musicdata['playlist_display'] = "Airplay"

			else:
				# Unexpected player type
				logging.debug("Unexpected player type {0} discovered".format(actPlayer))
				self.musicdata['playlist_position'] = 1
				self.musicdata['playlist_count'] = 1
				self.musicdata['bitrate'] = ""
				self.musicdata['tracktype'] = actPlayer
				self.musicdata['playlist_display'] = "Streaming"

			# if duration is not available, then suppress its display
			if int(self.musicdata['duration']) > 0:
				timepos = time.strftime("%M:%S", time.gmtime(int(current))) + "/" + time.strftime("%M:%S", time.gmtime(int(duration)))
				remaining = time.strftime("%M:%S", time.gmtime( int(duration) - int(current) ) )
			else:
				timepos = time.strftime("%M:%S", time.gmtime(int(current)))
				remaining = timepos

			self.musicdata['remaining'] = remaining
			self.musicdata['position'] = timepos

if __name__ == '__main__':

	q = Queue.Queue()
	mdr = musicdata_rune(q)

	start = time.time()
	while True:
		if start+20 < time.time():
			sys.exit(0)

		item = q.get()
		q.task_done()

		print q
