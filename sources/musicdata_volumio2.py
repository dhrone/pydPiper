#!/usr/bin/python
# coding: UTF-8

# musicdata service to read from Volumio V2
# Written by: Ron Ritchey

import json, threading, logging, Queue, time, sys
import musicdata
from socketIO_client import SocketIO


def on_GetState_response(*args):
    print "\n\n********* Got Response **************\n\n"

class musicdata_volumio2(musicdata.musicdata):



	def __init__(self, q, server='localhost', port=3000):
		super(musicdata_volumio2, self).__init__(q)
		self.server = server
		self.port = port
#		self.pwd = pwd
		self.connection_failed = 0
		self.timeout = 20
		self.idle_state = False

		self.musicdata_lock = threading.Lock()

		# Now set up a thread to listen to the channel and update our data when
		# the channel indicates a relevant key has changed
		data_t = threading.Thread(target=self.run)
		data_t.daemon = True
		data_t.start()



	def run(self):

		logging.debug("Volumio 2 musicdata service starting")
		logging.debug("Connecting to Volumio Web Service on {0}:{1}".format(self.server, self.port))

		with SocketIO(self.server, self.port) as socketIO:
			logging.debug("Connected to Volumio Web Service")
			self.socketIO = socketIO
			socketIO.on('pushState', self.on_state_response)
			socketIO.on('pushMultiRoomDevices', self.on_multiroomdevices_response)
			socketIO.on('pushQueue', self.on_queue_response)
			socketIO.emit('GetState', on_GetState_response)

			# Request initial values
			socketIO.emit('getQueue', '')
			socketIO.emit('getState', '')

			while True:
				socketIO.wait_for_callbacks(seconds=20)
				socketIO.emit('getQueue', '')
				socketIO.emit('getState', '')

	def on_multiroomdevices_response(self, *args):
		list = args[0]['list']

		# Was going to update actPlayer based upon the reported name from Volumio but
		# decided that this should be driven by the service key in status instead
#		for i in range(0, len(list)):
#			for item, value in list[i].iteritems():
#				if item == 'isSelf':
#					if value == True:
#						with self.musicdata_lock:
#							self.musicdata['actPlayer'] = list[i]['name'] if 'name' in list[i] else u""
#						return

	def on_queue_response(self,*args):
		list = args[0]
		with self.musicdata_lock:
			try:
				self.musicdata['playlist_count'] = len(list)
			except:
				self.musidata['playlist_count'] = 0

			plp = self.musicdata['playlist_position'] if 'playlist_position' in self.musicdata else 0
			stream = self.musicdata['stream'] if 'stream' in self.musicdata else u""

			# Determine what playlist_display should look like
			# playlist_position comes from status messages which are handled in on_state_response
			# So, we'll be updating playlist_display both here and there to make sure we have the latest
			# regardless of whether on_state_response or on_queue_response updates the underlying data

			if stream == 'webradio':
				self.musicdata['playlist_display'] = 'Streaming'
			else:
				self.musicdata['playlist_display'] = "{0}/{1}".format(plp, self.musicdata['playlist_count'], )

		self.sendUpdate()

	def on_state_response(self, *args):
		# Read musicplayer status and update musicdata

		status = args[0]

		with self.musicdata_lock:
			state = status.get('status')
			if state != "play":
				self.musicdata['state'] = u"stop"
			else:

				# Determine if the player is changing to playing.
				if self.musicdata_prev['state'] != u"play":

					# Request an update of the queue data
					self.socketIO.emit('getQueue','')

				# Update variables based upon received data
				self.musicdata['state'] = u"play"
				self.musicdata['album'] = status['album'] if 'album' in status else u""
				self.musicdata['random'] = status['random'] if 'random' in status else False
				self.musicdata['stream'] = status['stream'] if 'stream' in status else u""
				self.musicdata['artist'] = status['artist'] if 'artist' in status else u""
				self.musicdata['mute'] = status['mute'] if 'mute' in status else False
				seek = status['seek'] if 'seek' in status else 0
				self.musicdata['current'] = int(float(seek)/1000) if seek !=  None else 0
				self.musicdata['title'] = status['title'] if 'title' in status else u""
				self.musicdata['uri'] = status['uri'] if 'uri' in status else u""
				volume = status['volume'] if 'volume' in status else 0
				self.musicdata['volume'] = int(volume) if volume != None else 0
				self.musicdata['repeat]'] = status['repeat'] if 'repeat' in status else False
				duration = status['duration'] if 'duration' in status else 0
				self.musicdata['duration'] = int(duration) if duration !=  None else 0
				playlist_position = status['position'] if 'position' in status else 0
				self.musicdata['playlist_position'] = int(playlist_position)+1 if playlist_position != None else 0
				self.musicdata['bitdepth'] = status['bitdepth'] if 'bitdepth' in status else u""
				channels = status['channels'] if 'channels' in status else 0
				self.musicdata['channels'] = int(channels) if channels != None else 0
				self.musicdata['tracktype'] = status['trackType'] if 'trackType' in status else u""
				self.musicdata['samplerate'] = status['samplerate'] if 'samplerate' in status else u""

				# Fix any potential None values for Numeric or Boolean values
				if self.musicdata['random'] is None:
					self.musicdata['random'] = False
				if self.musicdata['mute'] is None:
					self.musicdata['mute'] = False
				if self.musicdata['repeat'] is None:
					self.musicdata['repeat'] = False


				# Convert Boolean to ints (to be consistent with other services
				self.musicdata['random'] = int(self.musicdata['random'])
				self.musicdata['mute'] = int(self.musicdata['mute'])
				self.musicdata['repeat'] = int(self.musicdata['repeat'])

				# Check all other items.  If any are None then set to u''
				for k, v in self.musicdata.iteritems():
					if v is None:
						self.musicdata[k] = u''

				if self.musicdata['channels'] == 1:
					self.musicdata['tracktype'] = "{0} {1}".format(self.musicdata['tracktype'], 'Mono').strip()
				elif self.musicdata['channels'] == 2:
					self.musicdata['tracktype'] = "{0} {1}".format(self.musicdata['tracktype'], 'Stereo').strip()
				elif self.musicdata['channels'] > 2:
					self.musicdata['tracktype'] = "{0} {1}".format(self.musicdata['tracktype'], 'Multi').strip()
				if self.musicdata['bitdepth']:
					self.musicdata['tracktype'] = "{0} {1}".format(self.musicdata['tracktype'], self.musicdata['bitdepth']).strip()
				if self.musicdata['samplerate']:
					self.musicdata['tracktype'] = "{0} {1}".format(self.musicdata['tracktype'], self.musicdata['samplerate']).strip()

				self.musicdata['musicdatasource'] = "Volumio"
				self.musicdata['actPlayer'] = status['service'] if 'service' in status else u""


				# Determine what playlist_display should look like
				# playlist_count comes from queue messages which are handled in on_queue_response
				# So, we'll be updating playlist_display both here and there to make sure we have the latest
				# regardless of whether on_state_response or on_queue_response updates the underlying data
				plc = self.musicdata['playlist_count'] if 'playlist_count' in self.musicdata else 0

				if self.musicdata['stream'].lower() == 'webradio':
					self.musicdata['playlist_display'] = 'Streaming'
				else:
					self.musicdata['playlist_display'] = "{0}/{1}".format(self.musicdata['playlist_position'], plc)


				# if duration is not available, then suppress its display
				if int(self.musicdata['duration']) > 0:
					timepos = time.strftime("%-M:%S", time.gmtime(int(self.musicdata['current']))) + "/" + time.strftime("%-M:%S", time.gmtime(int(self.musicdata['duration'])))
					remaining = time.strftime("%-M:%S", time.gmtime( int(self.musicdata['duration']) - int(self.musicdata['current']) ) )
				else:
					timepos = time.strftime("%-M:%S", time.gmtime(int(self.musicdata['current'])))
					remaining = timepos

				self.musicdata['remaining'] = remaining
				self.musicdata['position'] = timepos

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

	q = Queue.Queue()
	mdr = musicdata_volumio2(q, server, port)

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

	print "Exiting..."
