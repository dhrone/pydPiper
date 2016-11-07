#!/usr/bin/python
# coding: UTF-8

# musicdata service to read from Volumio V2
# Written by: Ron Ritchey

import json, threading, logging, Queue, time, sys
import musicdata
from socketIO_client import SocketIO


def on_GetState_response(*args):
	logging.debug("********* Got Response **************")

class musicdata_volumio2(musicdata.musicdata):

	def __init__(self, q, server='localhost', port=3000, exitapp = [ False ] ):
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
			socketIO.on('pushState', self.on_state_response)
			socketIO.on('pushMultiRoomDevices', self.on_multiroomdevices_response)
			socketIO.on('pushQueue', self.on_queue_response)
			socketIO.emit('GetState', on_GetState_response)

			# Request initial values
			socketIO.emit('getQueue', '')
			socketIO.emit('getState', '')

			while not self.exitapp[0]:
				socketIO.wait_for_callbacks(seconds=20)
				socketIO.emit('getQueue', '')
				socketIO.emit('getState', '')

	def on_multiroomdevices_response(self, *args):
		list = args[0]['list']

		for i in range(0, len(list)):
			for item, value in list[i].iteritems():
				if item == 'isSelf':
					if value == True:
						with self.musicdata_lock:
							self.musicdata['my_name'] = list[i]['name'] if 'name' in list[i] else u""
						return

	def on_queue_response(self,*args):
		list = args[0]
		with self.musicdata_lock:
			try:
				self.musicdata['playlist_length'] = len(list)
			except:
				self.musicdata['playlist_length'] = 0

			# For backwards compatibility
			self.musicdata['playlist_count'] = self.musicdata['playlist_length']

			plp = self.musicdata['playlist_position'] if 'playlist_position' in self.musicdata else 0
			stream = self.musicdata['stream'] if 'stream' in self.musicdata else u""

			# Determine what playlist_display should look like
			# playlist_position comes from status messages which are handled in on_state_response
			# So, we'll be updating playlist_display both here and there to make sure we have the latest
			# regardless of whether on_state_response or on_queue_response updates the underlying data

			if stream == 'webradio':
				self.musicdata['playlist_display'] = u'Radio'
			else:
				self.musicdata['playlist_display'] = u"{0}/{1}".format(plp, self.musicdata['playlist_length'] )

		self.sendUpdate()

	def on_state_response(self, *args):
		# Read musicplayer status and update musicdata

		status = args[0]

		with self.musicdata_lock:
			state = status.get('status')
			if state != "play":
				self.musicdata['state'] = u"stop"
			else:
				self.musicdata['state'] = u"play"

				# Determine if the player is changing to playing.
				if self.musicdata_prev['state'] != u"play":
					# Request an update of the queue data
					self.socketIO.emit('getQueue','')

			# Update variables based upon received data

			# String values
			self.musicdata['album'] = status['album'] if 'album' in status else u""
			self.musicdata['stream'] = status['stream'] if 'stream' in status else u""
			self.musicdata['artist'] = status['artist'] if 'artist' in status else u""
			self.musicdata['title'] = status['title'] if 'title' in status else u""
			self.musicdata['uri'] = status['uri'] if 'uri' in status else u""
			self.musicdata['bitdepth'] = status['bitdepth'] if 'bitdepth' in status else u""
			self.musicdata['tracktype'] = status['trackType'] if 'trackType' in status else u""
			self.musicdata['samplerate'] = status['samplerate'] if 'samplerate' in status else u""

			# Numeric values
			self.musicdata['elapsed'] = int(self.floatn(status['seek'])/1000) if 'seek' in status else 0

			# For backwards compatibility
			self.musicdata['current'] = self.musicdata['elapsed']

			self.musicdata['volume'] = self.intn(status['volume']) if 'volume' in status else 0

			self.musicdata['length'] = self.intn(status['duration']) if 'duration' in status else 0
			# For backwards compatibility
			self.musicdata['duration'] = self.musicdata['length']

			try:
				playlist_position = status['position'] if 'position' in status else 0
				self.musicdata['playlist_position'] = int(status['position'])+1 if 'position' in status else 0
			except:
				self.musicdata['playlist_position'] = 0

			self.musicdata['channels'] = self.intn(status['channels']) if 'channels' in status else 0

			# Boolean values
			self.musicdata['repeat'] = self.booln(status['repeat']) if 'repeat' in status else False
			self.musicdata['random'] = self.booln(status['random']) if 'random' in status else False
			self.musicdata['mute'] = self.booln(status['mute']) if 'mute' in status else False

			# Check all other items.  If any are None then set to u''
#			for k, v in self.musicdata.iteritems():
#				if v is None:
#					self.musicdata[k] = u''

			if self.musicdata['channels'] == 1:
				self.musicdata['tracktype'] = u"{0} {1}".format(self.musicdata['tracktype'], 'Mono').strip()
			elif self.musicdata['channels'] == 2:
				self.musicdata['tracktype'] = u"{0} {1}".format(self.musicdata['tracktype'], 'Stereo').strip()
			elif self.musicdata['channels'] > 2:
				self.musicdata['tracktype'] = u"{0} {1}".format(self.musicdata['tracktype'], 'Multi').strip()
			if self.musicdata['bitdepth']:
				self.musicdata['tracktype'] = u"{0} {1}".format(self.musicdata['tracktype'], self.musicdata['bitdepth']).strip()
			if self.musicdata['samplerate']:
				self.musicdata['tracktype'] = u"{0} {1}".format(self.musicdata['tracktype'], self.musicdata['samplerate']).strip()

			self.musicdata['musicdatasource'] = u"Volumio"
			self.musicdata['actPlayer'] = status['service'] if 'service' in status else u""


			# Determine what playlist_display should look like
			# playlist_count comes from queue messages which are handled in on_queue_response
			# So, we'll be updating playlist_display both here and there to make sure we have the latest
			# regardless of whether on_state_response or on_queue_response updates the underlying data
			plc = self.musicdata['playlist_length'] if 'playlist_length' in self.musicdata else 0

			if self.musicdata['stream'].lower() == u'webradio':
				self.musicdata['playlist_display'] = u'Radio'
			else:
				self.musicdata['playlist_display'] = u"{0}/{1}".format(self.musicdata['playlist_position'], plc)


			# if duration is not available, then suppress its display
			if int(self.musicdata['length']) > 0:
				timepos = time.strftime("%-M:%S", time.gmtime(int(self.musicdata['elapsed']))) + "/" + time.strftime("%-M:%S", time.gmtime(int(self.musicdata['length'])))
				remaining = time.strftime("%-M:%S", time.gmtime( int(self.musicdata['length']) - int(self.musicdata['elapsed']) ) )
			else:
				timepos = time.strftime("%-M:%S", time.gmtime(int(self.musicdata['elapsed'])))
				remaining = timepos

			self.musicdata['remaining'] = remaining.decode()
			self.musicdata['elapsed_formatted'] = timepos.decode()

			# For backwards compatibility
			self.musicdata['position'] = self.musicdata['elapsed_formatted']

			self.validatemusicvars(self.musicdata)

		self.sendUpdate()


if __name__ == '__main__':

	import moment, getopt

	logging.basicConfig(format='%(asctime)s:%(levelname)s:%(message)s', filename='musicdata_volumio2.log', level=logging.DEBUG)
	logging.getLogger().addHandler(logging.StreamHandler())
	logging.getLogger('socketIO-client').setLevel(logging.WARNING)

	try:
		opts, args = getopt.getopt(sys.argv[1:],"hs:p:",["server=","port="])
	except getopt.GetoptError:
		print 'musicdata_volumio2.py -s <server> -p <port>'
		sys.exit(2)

	# Set defaults
	server = 'localhost'
	port = 3000
#	pwd= ''

	for opt, arg in opts:
		if opt == '-h':
			print 'musicdata_volumio2.py -s <server> -p <port>'
			sys.exit()
		elif opt in ("-s", "--server"):
			server = arg
		elif opt in ("-p", "--port"):
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

				ctime = moment.utcnow().timezone("US/Eastern").strftime("%-I:%M:%S %p").strip()
				print "\n\nStatus at time {0}".format(ctime)
				for item,value in status.iteritems():
					print "    [{0}]={1} {2}".format(item,value, type(value))
				print "\n\n"

			except Queue.Empty:
				pass
	except KeyboardInterrupt:
		print ''
		pass
	finally:
		exitapp[0] = True

	print "Exiting..."
