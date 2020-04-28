#!/usr/bin/python
# coding: UTF-8

# musicdata service to read from Volumio V2
# Written by: Ron Ritchey
from __future__ import unicode_literals

import json, threading, logging, Queue, time, sys
import musicdata
from socketIO_client import SocketIO


def on_GetState_response(*args):
	logging.debug(u"********* Got Response **************")

class musicdata_volumio2(musicdata.musicdata):

	def __init__(self, q, server=u'localhost', port=3000, exitapp = [ False ] ):
		super(musicdata_volumio2, self).__init__(q)
		self.server = server
		self.port = port
#		self.pwd = pwd
		self.connection_failed = 0
		self.timeout = 20
		self.idle_state = False
		self.exitapp = exitapp

		self.musicdata_lock = threading.Lock()

		# Now set up a thread to listen to the channel and update our data when
		# the channel indicates a relevant key has changed
		data_t = threading.Thread(target=self.run)
		data_t.daemon = True
		data_t.start()



	def run(self):

		logging.debug(u"Volumio 2 musicdata service starting")
		logging.debug(u"Connecting to Volumio Web Service on {0}:{1}".format(self.server, self.port))

		with SocketIO(self.server, self.port) as socketIO:
			logging.debug(u"Connected to Volumio Web Service")
			self.socketIO = socketIO
			socketIO.on(u'pushState', self.on_state_response)
			socketIO.on(u'pushMultiRoomDevices', self.on_multiroomdevices_response)
			socketIO.on(u'pushQueue', self.on_queue_response)
			socketIO.emit(u'GetState', on_GetState_response)

			# Request initial values
			socketIO.emit(u'getQueue', '')
			socketIO.emit(u'getState', '')

			while not self.exitapp[0]:
				socketIO.wait_for_callbacks(seconds=20)
				socketIO.emit(u'getQueue', '')
				socketIO.emit(u'getState', '')

	def on_multiroomdevices_response(self, *args):
		list = args[0][u'list']

		for i in range(0, len(list)):
			for item, value in list[i].iteritems():
				if item == u'isSelf':
					if value == True:
						with self.musicdata_lock:
							self.musicdata[u'my_name'] = list[i][u'name'] if u'name' in list[i] else u""
						return

	def on_queue_response(self,*args):
		list = args[0]
		with self.musicdata_lock:
			try:
				self.musicdata[u'playlist_length'] = len(list)
			except:
				self.musicdata[u'playlist_length'] = 0

			# For backwards compatibility
			self.musicdata[u'playlist_count'] = self.musicdata[u'playlist_length']

			plp = self.musicdata[u'playlist_position'] if u'playlist_position' in self.musicdata else 0
			stream = self.musicdata[u'stream'] if u'stream' in self.musicdata else u""

			# Determine what playlist_display should look like
			# playlist_position comes from status messages which are handled in on_state_response
			# So, we'll be updating playlist_display both here and there to make sure we have the latest
			# regardless of whether on_state_response or on_queue_response updates the underlying data

			if stream == u'webradio':
				self.musicdata[u'playlist_display'] = u'Radio'
			else:
				self.musicdata[u'playlist_display'] = u"{0}/{1}".format(plp, self.musicdata[u'playlist_length'] )

		self.sendUpdate()

	def on_state_response(self, *args):
		# Read musicplayer status and update musicdata

		status = args[0]

		with self.musicdata_lock:
			state = status.get(u'status').lower()
			if state in [u'stop',u'pause',u'play']:
				self.musicdata[u'state'] = state
			else:
				self.musicdata[u'state'] = u'stop'

			if state == u'play':
				# Determine if the player is changing to playing.
				if self.musicdata_prev[u'state'] != u"play":
					# Request an update of the queue data
					self.socketIO.emit(u'getQueue','')

			# Update variables based upon received data

			# String values
			self.musicdata[u'album'] = status[u'album'] if u'album' in status else u""

			# stream is a binary within Volumio2 when playing from a webradio source.
			# Otherwise it is the name of the source.  Weird.
			streamval = status[u'stream'] if u'stream' in status else False
			if isinstance(streamval, bool):
				self.musicdata[u'stream'] = u'webradio' if streamval else u'not webradio'
			else:
				self.musicdata[u'stream'] = streamval

			self.musicdata[u'artist'] = status[u'artist'] if u'artist' in status else u""
			self.musicdata[u'title'] = status[u'title'] if u'title' in status else u""
			self.musicdata[u'uri'] = status[u'uri'] if u'uri' in status else u""
			self.musicdata[u'bitdepth'] = status[u'bitdepth'] if u'bitdepth' in status else u""
			self.musicdata[u'tracktype'] = status[u'trackType'] if u'trackType' in status else u""
			self.musicdata[u'samplerate'] = status[u'samplerate'] if u'samplerate' in status else u""
			self.musicdata[u'bitrate'] = status[u'bitrate'] if u'bitrate' in status else u""

			# Numeric values
			self.musicdata[u'elapsed'] = int(self.floatn(status[u'seek'])/1000) if u'seek' in status else 0

			# For backwards compatibility
			self.musicdata[u'current'] = self.musicdata[u'elapsed']

			self.musicdata[u'volume'] = self.intn(status[u'volume']) if u'volume' in status else 0

			self.musicdata[u'length'] = self.intn(status[u'duration']) if u'duration' in status else 0
			# For backwards compatibility
			self.musicdata[u'duration'] = self.musicdata[u'length']

			try:
				playlist_position = status[u'position'] if u'position' in status else 0
				self.musicdata[u'playlist_position'] = int(status[u'position'])+1 if u'position' in status else 0
			except:
				self.musicdata[u'playlist_position'] = 0

			self.musicdata[u'channels'] = self.intn(status[u'channels']) if u'channels' in status else 0

			# Boolean values
			self.musicdata[u'repeat'] = self.booln(status[u'repeat']) if u'repeat' in status else False
			self.musicdata[u'random'] = self.booln(status[u'random']) if u'random' in status else False
			self.musicdata[u'mute'] = self.booln(status[u'mute']) if u'mute' in status else False

			# Check all other items.  If any are None then set to u''
#			for k, v in self.musicdata.iteritems():
#				if v is None:
#					self.musicdata[k] = u''

			if self.musicdata[u'channels'] == 1:
				self.musicdata[u'tracktype'] = u"{0} {1}".format(self.musicdata[u'tracktype'], u'Mono').strip()
			elif self.musicdata[u'channels'] == 2:
				self.musicdata[u'tracktype'] = u"{0} {1}".format(self.musicdata[u'tracktype'], u'Stereo').strip()
			elif self.musicdata[u'channels'] > 2:
				self.musicdata[u'tracktype'] = u"{0} {1}".format(self.musicdata[u'tracktype'], u'Multi').strip()
			if self.musicdata[u'bitdepth']:
				self.musicdata[u'tracktype'] = u"{0} {1}".format(self.musicdata[u'tracktype'], self.musicdata[u'bitdepth']).strip()
			if self.musicdata[u'samplerate']:
				self.musicdata[u'tracktype'] = u"{0} {1}".format(self.musicdata[u'tracktype'], self.musicdata[u'samplerate']).strip()

			self.musicdata[u'musicdatasource'] = u"Volumio"
			self.musicdata[u'actPlayer'] = status[u'service'] if u'service' in status else u""


			# Determine what playlist_display should look like
			# playlist_count comes from queue messages which are handled in on_queue_response
			# So, we'll be updating playlist_display both here and there to make sure we have the latest
			# regardless of whether on_state_response or on_queue_response updates the underlying data
			plc = self.musicdata[u'playlist_length'] if u'playlist_length' in self.musicdata else 0

			if self.musicdata[u'stream'].lower() == u'webradio':
				self.musicdata[u'playlist_display'] = u'Radio'
				if self.musicdata[u'artist'] is None or self.musicdata[u'artist'] == u'':
					# Try to get web station name
					self.musicdata[u'artist'] = self.webradioname(self.musicdata[u'uri'])
			else:
				self.musicdata[u'playlist_display'] = u"{0}/{1}".format(self.musicdata[u'playlist_position'], plc)


			# if duration is not available, then suppress its display
			if int(self.musicdata[u'length']) > 0:
				timepos = time.strftime(u"%-M:%S", time.gmtime(int(self.musicdata[u'elapsed']))) + u"/" + time.strftime(u"%-M:%S", time.gmtime(int(self.musicdata[u'length'])))
				remaining = time.strftime(u"%-M:%S", time.gmtime( int(self.musicdata[u'length']) - int(self.musicdata[u'elapsed']) ) )
			else:
				timepos = time.strftime(u"%-M:%S", time.gmtime(int(self.musicdata[u'elapsed'])))
				remaining = timepos

			self.musicdata[u'remaining'] = remaining.decode()
			self.musicdata[u'elapsed_formatted'] = timepos.decode()

			# For backwards compatibility
			self.musicdata[u'position'] = self.musicdata[u'elapsed_formatted']

			self.validatemusicvars(self.musicdata)

		self.sendUpdate()


if __name__ == u'__main__':

	import moment, getopt

	logging.basicConfig(format=u'%(asctime)s:%(levelname)s:%(message)s', filename=u'musicdata_volumio2.log', level=logging.DEBUG)
	logging.getLogger().addHandler(logging.StreamHandler())
	logging.getLogger(u'socketIO-client').setLevel(logging.WARNING)

	try:
		opts, args = getopt.getopt(sys.argv[1:],u"hs:p:",[u"server=",u"port="])
	except getopt.GetoptError:
		print u'musicdata_volumio2.py -s <server> -p <port>'
		sys.exit(2)

	# Set defaults
	server = u'localhost'
	port = 3000
#	pwd= ''

	for opt, arg in opts:
		if opt == u'-h':
			print u'musicdata_volumio2.py -s <server> -p <port>'
			sys.exit()
		elif opt in (u"-s", u"--server"):
			server = arg
		elif opt in (u"-p", u"--port"):
			port = arg
#		elif opt in ("-w", "--pwd"):
#			pwd = arg

	exitapp = [ False ]
	q = Queue.Queue()
	mdr = musicdata_volumio2(q, server, port, exitapp)

	try:
		while True:
			try:
				status = q.get(timeout=1000)
				q.task_done()

				ctime = moment.utcnow().timezone(u"US/Eastern").strftime(u"%-I:%M:%S %p").strip()
				print u"\n\nStatus at time {0}".format(ctime)
				for item,value in status.iteritems():
					print u"    [{0}]={1} {2}".format(item,value, type(value))
				print u"\n\n"

			except Queue.Empty:
				pass
	except KeyboardInterrupt:
		print ''
		pass
	finally:
		exitapp[0] = True

	print u"Exiting..."
