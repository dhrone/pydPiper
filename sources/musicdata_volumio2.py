#!/usr/bin/python
# coding: UTF-8

# musicdata service to read from Volumio V2
# Written by: Ron Ritchey

import json, mpd, threading, logging, Queue, time, sys, getopt
import musicdata
from socketIO_client import SocketIO


def on_GetState_response(*args):
    print "\n\n********* Got Response **************\n\n"

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



	def run(self):

		logging.debug("Volumio 2 musicdata service starting")
		logging.debug("Connecting to Volumio Web Service on {0}:{1}".format(self.server, self.port))

		with SocketIO(self.server, self.port) as socketIO:
			logging.debug("Connected to Volumio Web Service")
			self.socketIO = socketIO
			socketIO.on('pushState', self.on_status_response)
			socketIO.on('pushMultiRoomDevices', self.on_multiroomdevices_response)
			socketIO.on('pushQueue', self.on_queue_response)
			socketIO.emit('GetState', on_GetState_response)

			while True:
				self.socketIO.emit('getQueue', '')
				self.socketIO.emit('getState', '')
				self.socketIO.wait_for_callbacks(seconds=5)


	def on_multiroomdevices_response(self, *args):
		list = args[0]['list']

		for i in range(0, len(list)):
			for item, value in list[i].iteritems():
				if item == 'isSelf':
					if value == True:
						self.musicdata['actPlayer'] = list[i]['name'] if 'name' in list[i] else u""
						return

	def on_queue_response(self.*args):
		list = args[0]['list']
		self.musicdata['playlist_count'] = len(list)

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
