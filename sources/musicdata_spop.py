#!/usr/bin/python
# coding: UTF-8

# musicdata service to read from SPOP
# Written by: Ron Ritchey
from __future__ import unicode_literals

import threading, logging, Queue, time, sys, telnetlib, json, getopt
import musicdata

class musicdata_spop(musicdata.musicdata):


	def __init__(self, q, server=u'localhost', port=6602, pwd=u''):
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
					self.dataclient.write(u"notify\n")
					self.dataclient.read_until(u"\n")
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
			self.dataclient.write(u"status\n")
			msg = self.dataclient.read_until("\n").strip()
			status = json.loads(msg)
		except (IOError, ValueError):
			logging.debug(u"Bad status message received.  Contents were {0}".format(msg))
			raise RuntimeError(u"Bad status message received.")
		except:
			# Caught something else.  Report it and then inform calling function that the connection is bad
			e = sys.exc_info()[0]
			logging.debug(u"Caught {0} trying to get status from SPOP".format(e))
			raise RuntimeError(u"Could not get status from SPOP")

		state = status.get(u'status')
		if state != u"playing":
			self.musicdata[u'state'] = u"stop"
		else:
			self.musicdata[u'state'] = u"play"

		# Update remaining variables
		self.musicdata[u'artist'] = status[u'artist'] if u'artist' in status else u""
		self.musicdata[u'title'] = status[u'title'] if u'title' in status else u""
		self.musicdata[u'album'] = status[u'album'] if u'album' in status else u""
		self.musicdata[u'volume'] = 0
		self.musicdata[u'length'] = self.intn(status[u'duration']/1000) if u'duration' in status else 0
		self.musicdata[u'elapsed'] = self.intn(status[u'position']) if u'position' in status else 0
		self.musicdata[u'playlist_position'] = self.intn(status[u'current_track']) if u'current_track' in status else 0
		self.musicdata[u'playlist_length'] = self.musicdata[u'playlist_count'] = self.intn(status[u'total_tracks']) if u'total_tracks' in status else 0
		self.musicdata[u'uri'] = status[u'uri'] if u'uri' in status else u""
		self.musicdata[u'repeat'] = status[u'repeat'] if u'repeat' in status else False
		self.musicdata[u'random'] = status[u'shuffle'] if u'shuffle' in status else False

		self.musicdata[u'single'] = False # Not support in SPOP

		self.musicdata[u'current'] = self.musicdata[u'elapsed']
		self.musicdata[u'duration'] = self.musicdata[u'length']

		self.musicdata[u'actPlayer'] = u"Spotify"
		self.musicdata[u'musicdatasource'] = u"SPOP"

		self.musicdata[u'bitrate'] = u""
		self.musicdata[u'tracktype'] = u""

		plp = self.musicdata[u'playlist_position']
		plc = self.musicdata[u'playlist_length']

		if self.musicdata[u'length'] > 0:
			timepos = time.strftime(u"%-M:%S", time.gmtime(self.musicdata[u'elapsed'])) + "/" + time.strftime(u"%-M:%S", time.gmtime(self.musicdata[u'length']))
			remaining = time.strftime(u"%-M:%S", time.gmtime(self.musicdata[u'length'] - self.musicdata[u'duration'] ) )

		else:
			timepos = time.strftime(u"%-M:%S", time.gmtime(self.musicdata[u'elapsed']))
			remaining = timepos

		self.musicdata[u'remaining'] = remaining.decode()
		self.musicdata[u'elapsed_formatted'] = self.musicdata[u'position'] = timepos.decode()

		self.musicdata[u'playlist_display'] = u"{0}/{1}".format(plp, plc)
		self.musicdata[u'tracktype'] = u"SPOP"

		self.validatemusicvars(self.musicdata)


if __name__ == u'__main__':

	logging.basicConfig(format='%(asctime)s:%(levelname)s:%(message)s', filename=u'musicdata_spop.log', level=logging.DEBUG)
	logging.getLogger().addHandler(logging.StreamHandler())

	try:
		opts, args = getopt.getopt(sys.argv[1:],u"hs:p:w:",[u"server=",u"port=",u"pwd="])
	except getopt.GetoptError:
		print u'musicdata_spop.py -s <server> -p <port> -w <password>'
		sys.exit(2)

	# Set defaults
	server = u'localhost'
	port = 6602
	pwd= u''

	for opt, arg in opts:
		if opt == u'-h':
			print u'musicdata_spop.py -s <server> -p <port> -w <password>'
			sys.exit()
		elif opt in (u"-s", u"--server"):
			server = arg
		elif opt in (u"-p", u"--port"):
			port = arg
		elif opt in (u"-w", u"--pwd"):
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
				print u"+++++++++"
				for k,v in item.iteritems():
					print u"[{0}] '{1}' type {2}".format(k,v,type(v))
				print u"+++++++++"
				print
				q.task_done()
			except Queue.Empty:
				pass
	except KeyboardInterrupt:
		print u''
		pass

	print u"Exiting..."
