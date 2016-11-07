#!/usr/bin/python
# coding: UTF-8

# musicdata service to read from SPOP
# Written by: Ron Ritchey

import threading, logging, Queue, time, sys, telnetlib, json, getopt
import musicdata

class musicdata_spop(musicdata.musicdata):


	def __init__(self, q, server='localhost', port=6602, pwd=''):
		super(musicdata_spop, self).__init__(q)
		self.server = server
		self.port = port
		self.pwd = pwd
		self.connection_failed = 0
		self.timeout = 20
		self.idle_state = False

		self.dataclient = None

		# Now set up a thread to listen to the channel and update our data when
		# the channel indicates a relevant key has changed
		data_t = threading.Thread(target=self.run)
		data_t.daemon = True
		data_t.start()

		# Start the idle timer
		idle_t = threading.Thread(target=self.idlealert)
		idle_t.daemon = True
		idle_t.start()

	def idlealert(self):

		while True:
			# Generate a noidle event every timeout seconds
			time.sleep(self.timeout)

			# If blocked waiting for a response then allow idleaert to issue notify to unblock the service
			if self.idle_state:
				try:
					#self.dataclient.noidle()
					self.dataclient.write("notify\n")
					self.dataclient.read_until("\n")
				except (IOError, AttributeError):
					# If not idle (or not created yet) return to sleeping
					pass

	def connect(self):

		# Try up to 10 times to connect to REDIS
		self.connection_failed = 0
		self.dataclient = None

		logging.debug(u"Connecting to SPOP service on {0}:{1}".format(self.server, self.port))


		while True:
			if self.connection_failed >= 10:
				logging.debug(u"Could not connect to SPOP")
				break
			try:
				# Connection to MPD
				client = telnetlib.Telnet(self.server, self.port)
				client.read_until("\n")

				self.dataclient = client
				break
			except:
				self.dataclient = None
				self.connection_failed += 1
				time.sleep(1)
		if self.dataclient is None:
			raise IOError(u"Could not connect to SPOP")
		else:
			logging.debug(u"Connected to SPOP service")


	def run(self):

		logging.debug(u"SPOP musicdata service starting")

		while True:
			if self.dataclient is None:
				try:
					# Try to connect
					self.connect()
					self.status()
					self.sendUpdate()
				except (IOError, RuntimeError):
					self.dataclient = None
					# On connection error, sleep 5 and then return to top and try again
					time.sleep(5)
					continue

			try:
				# Wait for notice that state has changed
				self.idle_state = True
				self.dataclient.write("idle\n")
				msg = self.dataclient.read_until("\n")
				self.idle_state = False
				self.status()
				self.sendUpdate()
				time.sleep(.01)
			except (IOError, RuntimeError):
				self.dataclient = None
				logging.debug(u"Could not get status from SPOP")
				time.sleep(5)
				continue


	def status(self):
		# Read musicplayer status and update musicdata

		try:
			self.dataclient.write("status\n")
			msg = self.dataclient.read_until("\n").strip()
			status = json.loads(msg)
		except (IOError, ValueError):
			logging.debug(u"Bad status message received.  Contents were {0}".format(msg))
			raise RuntimeError("Bad status message received.")
		except:
			# Caught something else.  Report it and then inform calling function that the connection is bad
			e = sys.exc_info()[0]
			logging.debug(u"Caught {0} trying to get status from SPOP".format(e))
			raise RuntimeError("Could not get status from SPOP")

		state = status.get('status')
		if state != "playing":
			self.musicdata['state'] = u"stop"
		else:
			self.musicdata['state'] = u"play"

		# Update remaining variables
		self.musicdata['artist'] = status['artist'] if 'artist' in status else u""
		self.musicdata['title'] = status['title'] if 'title' in status else u""
		self.musicdata['album'] = status['album'] if 'album' in status else u""
		self.musicdata['volume'] = 0
		self.musicdata['length'] = self.intn(status['duration']/1000) if 'duration' in status else 0
		self.musicdata['elapsed'] = self.intn(status['position']) if 'position' in status else 0
		self.musicdata['playlist_position'] = self.intn(status['current_track']) if 'current_track' in status else 0
		self.musicdata['playlist_length'] = self.musicdata['playlist_count'] = self.intn(status['total_tracks']) if 'total_tracks' in status else 0
		self.musicdata['uri'] = status['uri'] if 'uri' in status else u""
		self.musicdata['repeat'] = status['repeat'] if 'repeat' in status else False
		self.musicdata['random'] = status['shuffle'] if 'shuffle' in status else False

		self.musicdata['single'] = False # Not support in SPOP

		self.musicdata['current'] = self.musicdata['elapsed']
		self.musicdata['duration'] = self.musicdata['length']

		self.musicdata['actPlayer'] = u"SPOP"
		self.musicdata['musicdatasource'] = u"SPOP"

		self.musicdata['bitrate'] = u""
		self.musicdata['tracktype'] = u""

		plp = self.musicdata['playlist_position']
		plc = self.musicdata['playlist_length']

		if self.musicdata['length'] > 0:
			timepos = time.strftime("%-M:%S", time.gmtime(self.musicdata['elapsed'])) + "/" + time.strftime("%-M:%S", time.gmtime(self.musicdata['length']))
			remaining = time.strftime("%-M:%S", time.gmtime(self.musicdata['length'] - self.musicdata['duration'] ) )

		else:
			timepos = time.strftime("%-M:%S", time.gmtime(self.musicdata['elapsed']))
			remaining = timepos

		self.musicdata['remaining'] = remaining.decode()
		self.musicdata['elapsed_formatted'] = self.musicdata['position'] = timepos.decode()

		self.musicdata['playlist_display'] = u"{0}/{1}".format(plp, plc)
		self.musicdata['tracktype'] = u"SPOP"

		self.validatemusicvars(self.musicdata)


if __name__ == '__main__':

	logging.basicConfig(format='%(asctime)s:%(levelname)s:%(message)s', filename='musicdata_spop.log', level=logging.DEBUG)
	logging.getLogger().addHandler(logging.StreamHandler())

	try:
		opts, args = getopt.getopt(sys.argv[1:],"hs:p:w:",["server=","port=","pwd="])
	except getopt.GetoptError:
		print 'musicdata_spop.py -s <server> -p <port> -w <password>'
		sys.exit(2)

	# Set defaults
	server = 'localhost'
	port = 6602
	pwd= ''

	for opt, arg in opts:
		if opt == '-h':
			print 'musicdata_spop.py -s <server> -p <port> -w <password>'
			sys.exit()
		elif opt in ("-s", "--server"):
			server = arg
		elif opt in ("-p", "--port"):
			port = arg
		elif opt in ("-w", "--pwd"):
			pwd = arg


	import sys
	q = Queue.Queue()
	mds = musicdata_spop(q, server, port, pwd)

	try:
		start = time.time()
		while True:
			if start+120 < time.time():
				break;
			try:
				item = q.get(timeout=1000)
				print "+++++++++"
				for k,v in item.iteritems():
					print u"[{0}] '{1}' type {2}".format(k,v,type(v))
				print "+++++++++"
				print
				q.task_done()
			except Queue.Empty:
				pass
	except KeyboardInterrupt:
		print ''
		pass

	print "Exiting..."
