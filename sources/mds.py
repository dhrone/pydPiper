# meta - base class for collecting meta data from music sources
from __future__ import unicode_literals

import json, threading, logging, Queue, time, sys
import abc,logging,urllib2,contextlib

logger = logging.getLogger(__name__)
#logger.addHandler(logging.StreamHandler())

class mds:
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


	def __init__(self, name = 'Unknown', queue=None, playerComms = None, retriesAllowed = 3, exitApp = [0]):
		logger.info('Initializing MDS {0}'.format(name))
		# Parameters
		self.queue = queue # queue shared with master
		self.playerComms = playerComms # settings needed to connect with the player being monitored
		self.retriesAllowed = retriesAllowed # Number of connection attempts before aborting
		self.exitApp = exitApp # flag used to signal mds that master is terminating
		self.name = name # Name of the mds (e.g. Volumio, Rune)

		# Class Variables
		self.playerState = {}
		self.playerStateLastUpdate = {}
		self.timers = {}
		self.stopWatches = {}
		self.lMDS = threading.Lock()
		self.tMDS = threading.Thread(target=self.run)

		# Start Thread
		self.tMDS.daemon = True
		self.tMDS.start()

	@abc.abstractmethod
	def establishConnection(self):
		# Manage connection to the metadata service
		# Uses self.playComms information to initialize connection
		# Uses self.retriesAllowed to determine how many tries to attempt before aborting
		# throws RuntimeError if unsuccessful
		# Can be called to reestablish connection if connection is lost
		pass

	@abc.abstractmethod
	def shutdownConnection(self):
		# Releases connection to MDS
		# Called on exit
		pass

	def stopWatchStart(name, offset=0):
		self.stopWatches[name] = time.time()+offset

	def stopWatchValue(name):
		return time.time() - self.stopWatches[name]

	def timerStart(name, value):
		self.timers[name] = time.time()+offset

	def timerValue(name):
		value = self.timers[name] - time.time()
		return value if value >= 0 else 0

	def sendUpdate(self):
		# Figure out what has changed and then send just those values across dataqueue
		md = { }
		for k, v in self.playerState.iteritems():
			pv = self.playerStateLastUpdate[k] if k in self.playerStateLastUpdate else None
			if pv != v:
				md[k] = v

		# Send md to queue if anything has changed
		if len(md) > 0:
			self.queue.put(md)

		# Capture current state to compare against at next sendUpdate
		self.playerStateLastUpdate = self.playerState.copy()


	@abc.abstractmethod
	def listen(self):
		# Retrieve updates from mds
		# Returns True if it has received new data
		return False

	def run(self):
		# Main loop for MDS
		# Initializes connection to MDS
		# Enters loop that listens for updates calling sendUpdate when new data is available
		logger.info(u"{0} musicdata service starting".format(self.name))
		logger.info(u"Connecting to {0} on {1}".format(self.name, self.playerComms))

		self.establishConnection()

		while not self.exitApp[0]:
			if self.listen():
				self.sendUpdate()

		self.shutdownConnection()

		logger.info(u"{0} musicdata service shutting down".format(self.name))

class playerComms():
	__metaclass__ = abc.ABCMeta

	@abc.abstractmethod
	def __init__(self):
		pass

	@abc.abstractmethod
	def __str__(self):
		pass
