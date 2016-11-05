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
		'uri':u"",
		'encoding':u"",
		'tracktype':u"",
		'bitdepth':u"",
		'bitrate':u"",
		'samplerate':u"",
		'elapsed_formatted':u"",
		'album':u"",
		'elapsed':-1,
		'channels':0,
		'length':0,
		'remaining':u"",
		'volume':-1,
		'repeat':False,
		'single':False,
		'random':False,
		'playlist_display':u"",
		'playlist_position':-1,
		'playlist_length':-1,

		# Deprecated values
		'current':-1,
		'duration':-1,
		'position':u"",
		'playlist_count':-1,
		'type':u""
	}

	varcheck {
		'unicode':
			[ 'state', 'actPlayer', 'musicdatasource', 'album', 'artist', 'title', 'uri', 'encoding', 'tracktype', 'bitdepth', 'bitrate', 'samplerate', 'elapsed_formatted', 'remaining', 'playlist_display' ],
		'bool':
			[ 'random', 'single', 'repeat' ],
		'int':
			[ 'channels', 'length', 'elapsed', 'playlist_position', 'playlist_length' ]
	}


	def __init__(self, q):
		self.musicdata = self.musicdata_init.copy()
		self.musicdata_prev = self.musicdata.copy()
		self.dataqueue = q

	def validatemusicvars(self, vars):

		for vtype, members in varcheck.iteritems():

			if vtype == 'unicode':
				for v in members:
					try:
						if type(vars[v]) is unicode:
							continue
						if type(vars[v]) is None:
							vars[v] = u""
						elif type(vars[v]) is str:
							logging.debug("Received string in {0}.  Converting to Unicode".format(v))
							vars[v] = vars[v].decode()
						else:
							logging.debug("Received non-string type {0} in {1}.  Converting to null".format(type(vars[v],v))
							vars[v] = u""
					except KeyError:
						logging.debug("Missing required value {0}.  Adding empty version".format(v))
						vars[v] = u""
			elif vtype == 'bool':
				for v in members:
					try:
						if type(vars[v]) is bool:
							continue
						if type(vars[v]) is None:
							vars[v] = False
						elif type(vars[v]) is int:
							logging.debug("Received integer in {0}.  Converting to boolean".format(v))
							vars[v] = bool(vars[v])
						else:
							logging.debug("Received non-bool type {0} in {1}.  Converting to False".format(type(vars[v],v))
							vars[v] = False
					except KeyError:
						logging.debug("Missing required value {0}.  Adding empty version".format(v))
						vars[v] = False
			elif vtype == 'int':
				for v in members:
					try:
						if type(vars[v]) is int:
							continue
						if type(vars[v]) is None:
							vars[v] = 0
						elif type(vars[v]) is bool:
							logging.debug("Received boolean in {0}.  Converting to integer".format(v))
							vars[v] = int(vars[v])
						else:
							logging.debug("Received non-integer type {0} in {1}.  Converting to 0".format(type(vars[v],v))
							vars[v] = 0
					except KeyError:
						logging.debug("Missing required value {0}.  Adding empty version".format(v))
						vars[v] = 0






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

	def intn(self,val):
		# A version of int that returns 0 if the value is not convertable
		try:
			retval = int(val)
		except:
			retval = 0
		return retval

	def booln(self,val):
		# A version of bool that returns False if the value is not convertable
		try:
			retval = bool(val)
		except:
			retval = False
		return retval


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
