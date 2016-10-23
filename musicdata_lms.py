#!/usr/bin/python
# coding: UTF-8

# musicdata service to read from LMS
# Written by: Ron Ritchey

import json, threading, logging, Queue, musicdata, time, sys, urllib, pylms
from pylms import server

class musicdata_lms(musicdata.musicdata):


	def __init__(self, q, server='localhost', port=9090, user='', pwd='', player=''):
		super(musicdata_lms, self).__init__(q)
		self.server = server
		self.port = port
		self.user = user
		self.pwd = pwd
		self.player = player
		self.connection_failed = 0
		self.timeout = 20
		self.idle_state = False

		self.dataserver = None
		self.dataplayer = None
		self.rawserver = None

		# Now set up a thread to listen to the channel and update our data when
		# the channel indicates a relevant key has changed
		data_t = threading.Thread(target=self.run)
		data_t.daemon = True
		data_t.start()

		# Start the idle timer
#		idle_t = threading.Thread(target=self.idlealert)
#		idle_t.daemon = True
#		idle_t.start()

#	def idlealert(self):
#
#		while True:
#			# Generate a noidle event every timeout seconds
#			time.sleep(self.timeout)
#
#			if self.idle_state:
#				try:
#					#self.dataclient.noidle()
#					self.rawclient.write("noidle\n")
#				except (NameError, IOError, AttributeError):
#					# If not idle (or not created yet) return to sleeping
#					pass


	def connectraw(self):
		# Try up to 10 times to connect to LMS
		connection_failed = 0
		self.rawserver = None
		while True:
			if connection_failed >= 10:
				logging.debug("Could not connect raw to LMS")
				break
			try:
				# Connection to LMS
				self.rawserver = telnet.telnetlib(self.server, self.port)

				# Subscribe to notification events that should wake up the system to collect data
				self.rawserver.write("subscribe pause,play,mixer,playlist\n")
				break
			except (socket_error, IOError):
				self.rawserver = None
				connection_failed += 1
				time.sleep(1)
		if self.rawserver is None:
			raise IOError("Could not connect raw to LMS")

	def connect(self):

		# Try up to 10 times to connect to LMS
		self.connection_failed = 0
		self.dataserver = None
		while True:
			if self.connection_failed >= 10:
				logging.debug("Could not connect to LMS")
				break
			try:
				# Connection to LMS
				self.dataserver = pylms.server.Server(self.server, self.port, self.user, self.pwd)
				self.dataserver.connect()

				players = self.dataserver.get_players()
				for p in players:
					if p.get_ref() == self.player
						self.dataplayer = p
						break
				if self.dataplayer is None:
					self.dataplayer = self.lmsserver.get_players()[0]
					if self.dataplayer is None:
						raise RuntimeError("Could not find any LMS Players")
					self.player = str(self.dataplayer)

				break
			except (socket_error, AttributeError, IndexError):
				self.dataserver = None
				self.dataplayer = None
				self.connection_failed += 1
				time.sleep(1)
		if self.dataserver is None:
			raise IOError("Could not connect to LMS")


	def run(self):

		logging.debug("LMS musicdata service starting")

		while True:
			# Connect to the data service if needed
			if self.dataserver is None:
				try:
					# Try to connect
					self.connect()
					self.status()
					self.sendUpdate()
				except IOError:
					self.dataserver = None
					# On connection error, sleep 5 and then return to top and try again
					time.sleep(5)
					continue

			# Connect directly to the data service (for notifications) if needed
			if self.rawserver is None:
				try:
					# Try to connect
					self.rawconnect()
				except IOError:
					self.rawserver = None
					# On connection error, sleep 5 and then return to top and try again
					time.sleep(5)
					continue

			try:
				# Wait for notice that state has changed
				try:
					#self.idle_state = True
					msg = self.rawserver.read_until("\n", self.timeout)
					#self.idle_state = False
					self.status()
					self.sendUpdate()
				except (IOError, EOFError):
					# Error occurred while trying to read from rawserver
					# Mark rawserver None so that it is restarted on the next pass
					self.rawserver = None
					pass

				time.sleep(.01)
			except IOError:
				self.dataserver = None
				logging.debug("Could not get status from LMS")
				time.sleep(5)
				continue


	def status(self):
		# Read musicplayer status and update musicdata

		state = self.dataplayer.get_mode()

		if state != "play":
			self.musicdata['state'] = u"stop"
		else:

			self.musicdata['state'] = u"play"
			self.musicdata['artist'] = urllib.unquote(str(self.dataplayer.request("artist ?", True))).decode('utf-8')
			self.musicdata['title'] = urllib.unquote(str(self.dataplayer.request("title ?", True))).decode('utf-8')
			self.musicdata['album'] = urllib.unquote(str(self.dataplayer.request("album ?", True))).decode('utf-8')
			self.musicdata['volume'] = self.dataplayer.get_volume()
			self.musicdata['current'] = self.dataplayer.get_time_elapsed()
			self.musicdata['duration'] = self.dataplayer.get_track_duration()

			plp = self.musicdata['playlist_position'] = int(self.dataplayer.request("playlist index ?"))+1
			plc = self.musicdata['playlist_count'] = self.dataplayer.playlist_track_count()

			playlist_display = "{0}/{1}".format(plp, plc)
			# If the track count is greater than 1, we are playing from a playlist and can display track position and track count
			if self.dataplayer.playlist_track_count() > 1:
				playlist_display = "{0}/{1}".format(plp, plc)
			# if the track count is exactly 1, this is either a short playlist or it is streaming
			elif self.dataplayer.playlist_track_count() == 1:
				try:
					# if streaming
					if self.dataplayer.playlist_get_info()[0]['duration'] == 0.0:
						playlist_display = "Streaming"
					# it really is a short playlist
					else:
						playlist_display = "{0}/{1}".format(plp, plc)
				except KeyError:
					logging.debug("In LMS couldn't get valid track information")
					playlist_display = u""
			else:
				logging.debug("In LMS track length is <= 0")
				playlist_display = u""

			self.musicdata['playlist_display'] = playlist_display

			self.musicdata['actPlayer'] = "LMS"
			self.musicdata['musicdatasource'] = "LMS"

			url = self.dataplayer.get_track_path()

			# Get bitrate and tracktype if they are available.  Try blocks used to prevent array out of bounds exception if values are not found
			try:
				self.musicdata['bitrate'] = urllib.unquote(str(self.dataplayer.request("songinfo 2 1 url:"+url+" tags:r", True))).decode('utf-8').split("bitrate:", 1)[1]
			except:
				self.musicdata['bitrate'] = u""

			try:
				self.musicdata['tracktype'] = urllib.unquote(str(self.dataplayer.request("songinfo 2 1 url:"+url+" tags:o", True))).decode('utf-8').split("type:",1)[1]
			except:
				self.musicdata['tracktype'] = u""


			# if duration is not available, then suppress its display
			if int(self.musicdata['duration']) > 0:
				timepos = time.strftime("%M:%S", time.gmtime(int(self.musicdata['current']))) + "/" + time.strftime("%M:%S", time.gmtime(int(self.musicdata['duration'])))
				remaining = time.strftime("%M:%S", time.gmtime( int(self.musicdata['duration']) - int(self.musicdata['current']) ) )
			else:
				timepos = time.strftime("%M:%S", time.gmtime(int(self.musicdata['current'])))
				remaining = timepos

			self.musicdata['remaining'] = remaining
			self.musicdata['position'] = timepos


if __name__ == '__main__':

	logging.basicConfig(format='%(asctime)s:%(levelname)s:%(message)s', filename='musicdata_lms.log', level=logging.DEBUG)
	logging.getLogger().addHandler(logging.StreamHandler())

	import sys
	q = Queue.Queue()
	mdr = musicdata_lms(q)

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
