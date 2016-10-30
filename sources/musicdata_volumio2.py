#!/usr/bin/python
# coding: UTF-8

# musicdata service to read from Volumio V2
# Written by: Ron Ritchey

import json, mpd, threading, logging, Queue, time, sys, getopt
import musicdata
from socketIO_client import SocketIO

class musicdata_volumio2(musicdata.musicdata):



	def __init__(self, q, server='localhost', port=3000, pwd=''):
		super(musicdata_mpd, self).__init__(q)
		self.server = server
		self.port = port
		self.pwd = pwd
		self.connection_failed = 0
		self.timeout = 20
		self.idle_state = False

		# Now set up a thread to listen to the channel and update our data when
		# the channel indicates a relevant key has changed
		data_t = threading.Thread(target=self.run)
		data_t.daemon = True
		data_t.start()


	def connect(self):

		# Try up to 10 times to connect to MPD
		self.connection_failed = 0
		self.dataclient = None

		logging.debug("Connecting to Volumio Web Service on {0}:{1}".format(self.server, self.port))

#		while True:
#			if self.connection_failed >= 10:
#				logging.debug("Could not connect to Volumio Web Service")
#				break
#			try:
#				# Connection to MPD
#				client = mpd.MPDClient(use_unicode=True)
#				client.connect(self.server, self.port)
#
#				self.dataclient = client
#				break
#			except:
#				self.dataclient = None
#				self.connection_failed += 1
#				time.sleep(1)
#		if self.dataclient is None:
#			raise mpd.ConnectionError("Could not connect to MPD")
#		else:
#			logging.debug("Connected to MPD")

		# Can not figure out how to get the socketIO_client library to report a failed connection_failed
		# So this code starts service and just assumes all is well
		# If you are not getting music data, chances are your server and/or port values are wrong

		with SocketIO(self.server, self.port) as socketIO:
			self.socketIO = socketIO
			self.socketIO.on('pushState', self.on_state_response)
			self.socketIO.on('pushMultiRoomDevices', self.on_multiroomdevices_response)

		logging.debug("Connected to Volumio Web Service")


	def run(self):

		logging.debug("Volumio 2 musicdata service starting")

		while True:
#			if self.dataclient is None:
#				try:
#					# Try to connect
#					self.connect()
#					self.status()
#					self.sendUpdate()
#				except mpd.ConnectionError:
#					self.dataclient = None
#					# On connection error, sleep 5 and then return to top and try again
#					time.sleep(5)
#					continue

			self.connect()

			self.socketIO.wait_for_callbacks(seconds=5)
			socketIO.emit('getState', self.on_response)


	def on_response(self, *args):
		logging.debug("Received web service response")

	def on_multiroomdevices_response(self, *args):
		return

	def on_status_response(self, *args):
		# Read musicplayer status and update musicdata

		status = args[0]

		state = status.get('state')
		if state != "play":
			self.musicdata['state'] = u"stop"
		else:
			self.musicdata['state'] = u"play"
			self.musicdata['album'] = status['album'] if 'album' in status else u""
			self.musicdata['random'] = status['random'] if 'random' in status else False
			self.musicdata['stream'] = status['stream'] if 'stream' in status else u""
			self.musicdata['artist'] = status['artist'] if 'artist' in status else u""
			self.musicdata['mute'] = status['mute'] if 'mute' in status else False
			self.musicdata['current'] = int(float(status['seek'])/1000) if 'seek' in status else 0
			self.musicdata['title'] = status['title'] if 'title' in status else u""
			self.musicdata['uri'] = status['uri'] if 'uri' in status else u""
			self.musicdata['volume'] = int(status['volume']) if 'volume' in status else 0
			self.musicdata['repeat]'] = status['repeat'] if 'repeat' in status else False
			self.musicdata['duration'] = int(status['duration']) if 'duration' in status else 0
			self.musicdata['playlist_position'] = int(status['position'])+1 if 'position' in status else 0
			self.musicdata['bitdepth'] = status['bitdepth'] if 'bitdepth' in status else u""

			self.musicdata['channels'] = int(status['channels']) if 'channels' in status else 0
			self.musicdata['tracktype'] = status['trackType'] if 'trackType' in status else u""
			self.musicdata['samplerate'] = status['samplerate'] if 'samplerate' in status else u""

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
				
			self.musicdata['musicdatasource'] = status['service'] if 'service' in status else u""


			# Fix any potential None values
			if self.musicdata['random'] is None:
				self.musicdata['random'] = False
			if self.musicdata['mute'] is None:
				self.musicdata['mute'] = False
			if self.musicdata['repeat'] is None:
				self.musicdata['repeat'] = False

#			self.musicdata['actPlayer'] = "MPD"

			#### Need to find a way to get the playlist length ####
#			plc = self.musicdata['playlist_count'] = int(status['playlistlength']) if 'playlistlength' in status else 0


			# If playlist is length 1 and the song playing is from an http source it is streaming
#			if plc == 1:
#				if playlist_info[0]['file'][:4] == "http":
#					self.musicdata['playlist_display'] = "Streaming"
#					if self.musicdata['artist'] == u"" or self.musicdata['artist'] is None:
#						self.musicdata['artist'] = current_song['name'] if 'name' in current_song else u""
#				else:
#					self.musicdata['playlist_display'] = "{0}/{1}".format(self.musicdata['playlist_position'], self.musicdata['playlist_count'])
#			else:
#					self.musicdata['playlist_display'] = "{0}/{1}".format(self.musicdata['playlist_position'], self.musicdata['playlist_count'])

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

			# if duration is not available, then suppress its display
			if int(self.musicdata['duration']) > 0:
				timepos = time.strftime("%-M:%S", time.gmtime(int(self.musicdata['current']))) + "/" + time.strftime("%-M:%S", time.gmtime(int(self.musicdata['duration'])))
				remaining = time.strftime("%-M:%S", time.gmtime( int(self.musicdata['duration']) - int(self.musicdata['current']) ) )
			else:
				timepos = time.strftime("%-M:%S", time.gmtime(int(self.musicdata['current'])))
				remaining = timepos

			self.musicdata['remaining'] = remaining
			self.musicdata['position'] = timepos


if __name__ == '__main__':

	logging.basicConfig(format='%(asctime)s:%(levelname)s:%(message)s', filename='musicdata_mpd.log', level=logging.DEBUG)
	logging.getLogger().addHandler(logging.StreamHandler())

	# Suppress MPD libraries INFO messages
	loggingMPD = logging.getLogger("mpd")
	loggingMPD.setLevel( logging.WARN )

	try:
		opts, args = getopt.getopt(sys.argv[1:],"hs:p:w:",["server=","port=","pwd="])
	except getopt.GetoptError:
		print 'musicdata_mpd.py -s <server> -p <port> -w <password>'
		sys.exit(2)

	# Set defaults
	server = 'localhost'
	port = 6600
	pwd= ''

	for opt, arg in opts:
		if opt == '-h':
			print 'musicdata_mpd.py -s <server> -p <port> -w <password>'
			sys.exit()
		elif opt in ("-s", "--server"):
			server = arg
		elif opt in ("-p", "--port"):
			port = arg
		elif opt in ("-w", "--pwd"):
			pwd = arg

	q = Queue.Queue()
	mdr = musicdata_mpd(q, server, port, pwd)

	try:
		start = time.time()
		while True:
			if start+120 < time.time():
				break;
			try:
				item = q.get(timeout=1000)
				print "+++++++++"
				print item
				print "+++++++++"
				print
				q.task_done()
			except Queue.Empty:
				pass
	except KeyboardInterrupt:
		print ''
		pass

	print "Exiting..."
