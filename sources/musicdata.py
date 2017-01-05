# meta - base class for collecting meta data from music sources
from __future__ import unicode_literals

import abc,logging,urllib2,contextlib

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
		'stream':u"",
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

		'my_name':u"", # Volumio 2 only

		# Deprecated values
		'current':-1,
		'duration':-1,
		'position':u"",
		'playlist_count':-1,
		'type':u""
	}

	varcheck = {
		u'unicode':
		[
			# Player state
			u'state',
			u'actPlayer',
			u'musicdatasource',

			# Track information
			u'album',
			u'artist',
			u'title',
			u'uri',
			u'encoding',
			u'tracktype',
			u'bitdepth',
			u'bitrate',
			u'samplerate',
			u'elapsed_formatted',
			u'remaining',
			u'playlist_display',
			u'my_name'
		],
		u'bool':
		[
			# Player state
			u'random',
			u'single',
			u'repeat'
		],
		u'int':
		[
			# Player state
			u'volume',

			# Track information
			u'channels',
			u'length',
			u'elapsed',
			u'playlist_position',
			u'playlist_length'

		]
	}


	def __init__(self, q):
		self.musicdata = self.musicdata_init.copy()
		self.musicdata_prev = self.musicdata.copy()
		self.dataqueue = q

	def validatemusicvars(self, vars):

		for vtype, members in self.varcheck.iteritems():

			if vtype == u'unicode':
				for v in members:
					try:
						if type(vars[v]) is unicode:
							continue
						if type(vars[v]) is None:
							vars[v] = u""
						elif type(vars[v]) is str:
							logging.debug(u"Received string in {0}.  Converting to Unicode".format(v))
							vars[v] = vars[v].decode()
						else:
							# This happens so often when playing from webradio that I'm disabling logging for now.
#							logging.debug(u"Received non-string type {0} in {1}.  Converting to null".format(type(vars[v]),v))
							vars[v] = u""
					except KeyError:
						logging.debug(u"Missing required value {0}.  Adding empty version".format(v))
						vars[v] = u""
			elif vtype == u'bool':
				for v in members:
					try:
						if type(vars[v]) is bool:
							continue
						if type(vars[v]) is None:
							vars[v] = False
						elif type(vars[v]) is int:
							logging.debug(u"Received integer in {0}.  Converting to boolean".format(v))
							vars[v] = bool(vars[v])
						else:
							logging.debug(u"Received non-bool type {0} in {1}.  Converting to False".format(type(vars[v]),v))
							vars[v] = False
					except KeyError:
						logging.debug(u"Missing required value {0}.  Adding empty version".format(v))
						vars[v] = False
			elif vtype == u'int':
				for v in members:
					try:
						if type(vars[v]) is int:
							continue
						if type(vars[v]) is None:
							vars[v] = 0
						elif type(vars[v]) is bool:
							logging.debug(u"Received boolean in {0}.  Converting to integer".format(v))
							vars[v] = int(vars[v])
						else:
							logging.debug(u"Received non-integer type {0} in {1}.  Converting to 0".format(type(vars[v]),v))
							vars[v] = 0
					except KeyError:
						logging.debug(u"Missing required value {0}.  Adding empty version".format(v))
						vars[v] = 0



	def webradioname(self,url):
		# Attempt to get name of webradio station
		# Requires station to send name using the M3U protocol
		# url - url of the station

		# Only check for a radio station name if you are actively playing a track
		if self.musicdata[u'state'] != u'play':
			return u''

		retval = u''
		with contextlib.closing(urllib2.urlopen(url)) as page:
			cnt = 20
			try:
				for line in page:
					line = line.decode('utf-8')
					cnt -= 1
					if line.startswith(u'#EXTINF:'):
						try:
							retval = line.split(u'#EXTINF:')[1].split(',')[1].split(')')[1].strip()
						except IndexError:
							try:
								retval = line.split(u'#EXTINF:')[1].split(',')[0].split(')')[1].strip()
							except IndexError:
								retval = u''
						if retval != u'':
							if retval is unicode:
								logging.debug(u"Found {0}".format(retval))
								return retval
							else:
								try:
									logging.debug(u"Found {0}".format(retval))
									return retval.decode()
								except:
									logging.debug(u"Not sure what I found {0}".format(retval))
									return u''
					elif line.startswith(u'Title1='):
						try:
							retval = line.split(u'Title1=')[1].split(':')[1:2][0]
						except:
							retval = line.split(u'Title1=')[0]
						retval = retval.split(u'(')[0].strip()
						return retval.decode()

					if cnt == 0: break
			except:
				# Likely got junk data.  Skip
				pass
			logging.debug(u"Didn't find an appropriate header at {0}".format(url))


	def sendUpdate(self):
		# Figure out what has changed and then send just those values across dataqueue
		md = { }
		for k, v in self.musicdata.iteritems():
			pv = self.musicdata_prev[k] if k in self.musicdata_prev else None
			if pv != v:
				md[k] = v


		# Send md to queue if anything has changed
		if len(md) > 0:
			# elapsed is special as it needs to be sent to guarantee that the timer gets updated correctly.  Even if it hasn't changed, send it anyway
			md[u'elapsed'] = self.musicdata[u'elapsed']
			md[u'state'] = self.musicdata[u'state']
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

	def floatn(self,val):
		# A version of float that returns 0.0 if the value is not convertable
		try:
			retval = float(val)
		except:
			retval = 0.0
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
