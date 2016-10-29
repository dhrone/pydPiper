# meta - base class for collecting meta data from music sources

import abc

class musicdata:
	__metaclass__ = abc.ABCMeta

	# Children of this class will own interacting with the underlying music service
	# Must monitor for changes to the players state
	# Uses a queue (received from caller) to send any updates that occur

	# Will use a thread to receive updates from service.
	# Will update musicdata on receipt of new data
	# Will send a message over the data queue whenever an update is received
	# Will only send keys that have been updated

	# May use a thread to issue keyalives to the music service if needed

	# Future state
	# Will allow command issuance to music service.


	musicdata_init = {
		'state':u"stop",
		'musicdatasource':u"",
		'actPlayer':u"",
		'artist':u"",
		'title':u"",
		'album':u"",
		'current':-1,
		'remaining':u"",
		'duration':-1,
		'position':u"",
		'volume':-1,
		'repeat':0,
		'single':0,
		'random':0,
		'playlist_display':u"",
		'playlist_position':-1,
		'playlist_count':-1,
		'bitrate':u"",
		'type':u""
	}

	def __init__(self, q):
		self.musicdata = self.musicdata_init.copy()
		self.musicdata_prev = self.musicdata.copy()
		self.dataqueue = q


	def sendUpdate(self):
		# Figure out what has changed and then send just those values across dataqueue
		md = { }
		for k, v in self.musicdata.iteritems():
			pv = self.musicdata_prev[k] if k in self.musicdata_prev else None
			if pv != v:
				md[k] = v


		# Send md to queue if anything has changed
		if len(md) > 0:
			self.dataqueue.put(md)

			# Update musicdata_prev
			self.musicdata_prev = self.musicdata.copy()


	def clear(self):
		# revert data back to init state
		self.musicdata = self.musicdata_init.copy()

	@abc.abstractmethod
	def run():
		# Start thread(s) to monitor music source
		# Threads must be run as daemons
		# Future state: start thread to issue commands to music source
		return

	#@abc.abstractmethod
	#def command(cmd):
		# Send command to music service
		# Throws NotImplementedError if music service does not support commands
	#	return
