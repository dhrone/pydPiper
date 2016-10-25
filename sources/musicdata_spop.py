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

		if self.pwd:
			logging.debug("Connecting to SPOP service on {0}:{1} pwd {2}".format(self.server, self.port, self.pwd))
		else:
			logging.debug("Connecting to SPOP service on {0}:{1}".format(self.server, self.port))


		while True:
			if self.connection_failed >= 10:
				logging.debug("Could not connect to SPOP")
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
			raise IOError("Could not connect to SPOP")
		else:
			logging.debug("Connected to SPOP service")


	def run(self):

		logging.debug("SPOP musicdata service starting")

		while True:
			if self.dataclient is None:
				try:
					# Try to connect
					self.connect()
					self.status()
					self.sendUpdate()
				except IOError:
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
			except IOError:
				self.dataclient = None
				logging.debug("Could not get status from SPOP")
				time.sleep(5)
				continue


	def status(self):
		# Read musicplayer status and update musicdata

		self.dataclient.write("status\n")
		msg = self.dataclient.read_until("\n").strip()
		try:
			status = json.loads(msg)
		except ValueError:
			logging.debug("Value error with msg={0}".format(msg))

		state = status.get('status')
		if state != "playing":
			self.musicdata['state'] = u"stop"
		else:
			self.musicdata['state'] = u"play"
			self.musicdata['artist'] = status['artist'] if 'artist' in status else u""
			self.musicdata['title'] = status['title'] if 'title' in status else u""
			self.musicdata['album'] = status['album'] if 'album' in status else u""
			self.musicdata['volume'] = 0
			self.musicdata['duration'] = int(status['duration']/1000) if 'duration' in status else 0
			self.musicdata['current'] = int(status['position']) if 'position' in status else 0
			self.musicdata['playlist_position'] = int(status['current_track']) if 'current_track' in status else 0
			self.musicdata['playlist_count'] = int(status['total_tracks']) if 'total_tracks' in status else 0


			self.musicdata['actPlayer'] = "SPOP"
			self.musicdata['musicdatasource'] = "SPOP"

			self.musicdata['bitrate'] = u""
			self.musicdata['tracktype'] = u""

			plp = self.musicdata['playlist_position']
			plc = self.musicdata['playlist_count']

			if self.musicdata['duration'] > 0:
				timepos = time.strftime("%-M:%S", time.gmtime(self.musicdata['current'])) + "/" + time.strftime("%-M:%S", time.gmtime(self.musicdata['duration']))
				remaining = time.strftime("%-M:%S", time.gmtime(self.musicdata['duration'] - self.musicdata['current'] ) )

			else:
				timepos = time.strftime("%-M:%S", time.gmtime(self.musicdata['current']))
				remaining = timepos

			self.musicdata['remaining'] = remaining
			self.musicdata['position'] = timepos

			self.musicdata['playlist_display'] = "{0}/{1}".format(plp, plc)
			self.musicdata['tracktype'] = u"SPOP"


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
