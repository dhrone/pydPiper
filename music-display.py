import Winstar_GraphicOLED
import moment
import time
import json
import logging
import commands
import os
import sys
import getopt
from mpd import MPDClient
import pylms
from pylms import server
from pylms import player
import telnetlib
from socket import error as socket_error
import traceback

try:
	import RPi.GPIO as GPIO
	DISPLAY_INSTALLED = True
except:
	import curses
	DISPLAY_INSTALLED = False

import Queue
from threading import Thread
import signal
import sys

# import page definitions from pages.py
import pages

STARTUP_MSG = "Raspdac\nStarting"

HESITATION_TIME = 2.5 # Amount of time in seconds to hesistate before scrolling
ANIMATION_SMOOTHING = .15 # Amount of time in seconds before repainting display

COOLING_PERIOD = 15 # Default amount of time in seconds before an alert message can be redisplayed

# The Winstar display shipped with the RaspDac is capable of two lines of display
# when the 5x8 font is used.  This code assumes that is what you will be using.
# The display logic would need significant rework to support a different number
# of display lines!

DISPLAY_WIDTH = 16 # the character width of the display
DISPLAY_HEIGHT = 2 # the number of lines on the display

# This is where the log file will be written
LOGFILE='/var/log/RaspDacDisplay.log'
#LOGFILE='./log/RaspDacDisplay.log'

STATUSLOGFILE='/var/log/RaspDacDisplayStatus.log'
#STATUSLOGFILE='./log/RaspDacDisplayStatus.log'
STATUSLOGGING = False

# Adjust this setting to localize the time display to your region
TIMEZONE="US/Eastern"
TIME24HOUR=False
#TIMEZONE="Europe/Paris"

# Logging level
LOGLEVEL=logging.DEBUG
#LOGLEVEL=logging.INFO
#LOGLEVEL=logging.WARNING
#LOGLEVEL=logging.CRITICAL


#Configure which music services to monitor
# For Volumio and RuneAudio MPD and SPOP should be enabled and LMS disabled
# for Max2Play if you are using the Logitech Music Service, then LMS should be enabled
MPD_ENABLED = False
MPD_SERVER = "localhost"
MPD_PORT = 6600

SPOP_ENABLED = False
SPOP_SERVER = "localhost"
SPOP_PORT = 6602

LMS_ENABLED = False
LMS_SERVER = "localhost"
LMS_PORT = 9090
LMS_USER = ""
LMS_PASSWORD = ""

# Set this to MAC address of the Player you want to monitor.
# THis should be the MAC of the RaspDac system if using Max2Play with SqueezePlayer
# Note: if you have another Logitech Media Server running in your network, it is entirely
#       possible that your player has decided to join it, instead of the LMS on Max2Play
#       To fix this, go to the SqueezeServer interface and change move the player to the
#       correct server.
LMS_PLAYER = "00:01:02:aa:bb:cc"


# If you are using RuneAudio you can pull the information from the REDIS database that RuneAudio maintains
RUNE_ENABLED = True
REDIS_SERVER = "localhost"
REDIS_PORT = 6379
REDIS_PASSWORD = ""



class RaspDac_Display:


	def __init__(self):
		logging.debug("RaspDac_Display Initializing")

		self.tempreadexpired = 0
		self.diskreadexpired = 0
		self.ratereadexpired = 0

		# used with Redis to try to figure out how long the song has been playing
		self.timesongstarted = 0
		self.currentsong = ""
		self.currentelapsed = 0

		self.tempc = 0.0
		self.tempf = 0.0
		self.avail = 0
		self.availp = 0
		self.rate = 0

		# Initilize the connections to the music Daemons.  Currently supporting
		# MPD and SPOP (for Spotify)

		ATTEMPTS=3
		# Will try to connect multiple times

		global RUNE_ENABLED
		if RUNE_ENABLED:
			# This tries to pull in the redis module which is only used right now for RuneAudio.
			# If it is not present, REDIS will be disabled
			try:
				import redis
				for i in range (1,ATTEMPTS):
					try:
						# Try to connect to REDIS service
						self.redisclient = redis.Redis(REDIS_SERVER, REDIS_PORT, REDIS_PASSWORD)
						break
					except:
						time.sleep(2)
				else:
					# After the alloted number of attempts did not succeed in connecting
					logging.warning("Unable to connect to REDIS service on startup")

			except ImportError:
				logging.warning("Redis requested but module not found.")
				RUNE_ENABLED = False


		if MPD_ENABLED:
			for i in range (1,ATTEMPTS):
				self.client = MPDClient(use_unicode=True)

				try:
					# Connect to the MPD daemon
					self.client.connect(MPD_SERVER, MPD_PORT)
					break
				except:
					time.sleep(2)
			else:
				# After the alloted number of attempts did not succeed in connecting
				logging.warning("Unable to connect to MPD service on startup")

		if SPOP_ENABLED:
			# Now attempting to connect to the Spotify daemon
			# This may fail if Spotify is not configured.  That's ok!
			for i in range (1,ATTEMPTS):
				try:
					self.spotclient = telnetlib.Telnet(SPOP_SERVER,SPOP_PORT)
					self.spotclient.read_until("\n")
					break
				except:
					time.sleep(2)
			else:
				# After the alloted number of attempts did not succeed in connecting
				logging.warning("Unable to connect to Spotify service on startup")

		if LMS_ENABLED:
			for i in range (1,ATTEMPTS):
				try:
					# Connect to the LMS daemon
					self.lmsserver = pylms.server.Server(LMS_SERVER, LMS_PORT, LMS_USER, LMS_PASSWORD)
					self.lmsserver.connect()

					# Find correct player
					players = self.lmsserver.get_players()
					for p in players:
						### Need to find out how to get the MAC address from player
						if p.get_ref() == LMS_PLAYER:
							self.lmsplayer = p
							break
					if self.lmsplayer is None:
						self.lmsplayer = self.lmsserver.get_players()[0]
						if self.lmsplayer is None:
							raise Exception('Could not find any LMS player')
					break
				except (socket_error, AttributeError, IndexError):
					logging.debug("Connect attempt {0} to LMS server failed".format(i))
					time.sleep(2)
			else:
				# After the alloted number of attempts did not succeed in connecting
				logging.warning("Unable to connect to LMS service on startup")

		global STATUSLOGGING
		if STATUSLOGGING:
			try:
				self.statusfile = open(STATUSLOGFILE, 'a')
			except:
				logging.warning("Status data logging requested but could not open {0}".format(STATUSLOGFILE))
				STATUSLOGGING = False


	def status_redis(self):
		# Try to get status from MPD daemon

		try:
			r_status = json.loads(self.redisclient.get('act_player_info'))
		except:
			# Attempt to reestablish connection to daemon
			try:
				self.redisclient = redis.Redis(REDIS_SERVER, REDIS_PORT, REDIS_PASSWORD)
				r_status = json.loads(self.redisclient.get('act_player_info'))
			except:
				logging.debug("Could not get status from REDIS daemon")
				return { 'state':u"stop", 'artist':u"", 'title':u"", 'album':u"", 'current':0, 'remaining':u"", 'duration':0, 'position':u"", 'volume':0, 'playlist_display':u"", 'playlist_position':0, 'playlist_count':0, 'bitrate':u"", 'type':u"" }

		state = r_status.get('state')
		if state == "play":
			artist = r_status.get('currentartist')
			title = r_status.get('currentsong')
			album = r_status.get('currentalbum')
			volume = int(r_status.get('volume'))
			actPlayer = r_status.get('actPlayer')
			duration = int(r_status.get('time'))

			# if transitioning state from stopped to playing
			if self.timesongstarted == 0:
				self.currentelapsed = int(r_status['elapsed'])
				current = self.currentelapsed
				self.timesongstarted = time.time() - current
				self.currentsong = title
			else:
				# Are we still playing the same title?
				if self.currentsong == title:

					# Did elapsed change?  This can happen if someone fast forwards the song, etc.
					if self.currentelapsed != int(r_status['elapsed']):
						self.currentelapsed = int(r_status['elapsed'])
						current = self.currentelapsed
						self.timesongstarted = time.time() - current
					else:
						# if not continue to estimate
						current = int(time.time() - self.timesongstarted)
				else:
					self.currentelapsed = int(r_status['elapsed'])
					current = self.currentelapsed
					self.timesongstarted = time.time() - current
					self.currentsong = title

			if actPlayer == 'Spotify':
				bitrate = "320 kbps"
				playlist_position = int(r_status.get('song'))+1
				playlist_count = int(r_status.get('playlistlength'))
				playlist_display = "{0}/{1}".format(playlist_position, playlist_count)
				tracktype = "Spotify"

			elif actPlayer == 'MPD':
				playlist_position = int(r_status.get('song'))+1
				playlist_count = int(r_status.get('playlistlength'))
				bitrate = "{0} kbps".format(r_status.get('bitrate'))

				# if radioname is None then this is coming from a playlist (e.g. not streaming)
				if r_status['radioname'] == None:
					playlist_display = "{0}/{1}".format(playlist_position, playlist_count)
				else:
					playlist_display = "Streaming"
					# if artist is empty, place radioname in artist field
					if artist is None:
						artist = r_status['radioname']

				try:
					audio = r_status['audio'].split(':')
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
				except KeyError:
					tracktype = u"MPD"


			elif actPlayer == 'Airplay':
				playlist_position = 1
				playlist_count = 1
				bitrate = ""
				tracktype = u"Airplay"
				playlist_display = "Airplay"

			else:
				# Unexpected player type
				logging.debug("Unexpected player type {0} discovered".format(actPlayer))
				playlist_position = 1
				playlist_count = 1
				bitrate = ""
				tracktype = actPlayer
				playlist_display = "Streaming"

			# since we are returning the info as a JSON formatted return, convert
			# any None's into reasonable values
			if artist is None: artist = u""
			if title is None: title = u""
			if album is None: album = u""
			if current is None: current = 0
			if volume is None: volume = 0
			if bitrate is None: bitrate = u""
			if tracktype is None: tracktype = u""
			if duration is None: duration = 0

			# if duration is not available, then suppress its display
			if int(duration) > 0:
				timepos = time.strftime("%M:%S", time.gmtime(int(current))) + "/" + time.strftime("%M:%S", time.gmtime(int(duration)))
				remaining = time.strftime("%M:%S", time.gmtime( int(duration) - int(current) ) )
			else:
				timepos = time.strftime("%M:%S", time.gmtime(int(current)))
				remaining = timepos

			return { 'state':u"play", 'artist':artist, 'title':title, 'album':album, 'remaining':remaining, 'current':current, 'duration':duration, 'position':timepos, 'volume':volume, 'playlist_display':playlist_display, 'playlist_position':playlist_position, 'playlist_count':playlist_count, 'bitrate':bitrate, 'type':tracktype }
	  	else:
			self.timesongstarted = 0
			return { 'state':u"stop", 'artist':u"", 'title':u"", 'album':u"", 'remaining':u"", 'current':0, 'duration':0, 'position':u"", 'volume':0, 'playlist_display':u"", 'playlist_position':u"", 'playlist_count':0, 'bitrate':u"", 'type':u""}


	def status_mpd(self):
		# Try to get status from MPD daemon

		try:
			m_status = self.client.status()
			m_currentsong = self.client.currentsong()
			playlist_info = self.client.playlistinfo()
		except:
			# Attempt to reestablish connection to daemon
			try:
				self.client.connect(MPD_SERVER, MPD_PORT)
				m_status=self.client.status()
				m_currentsong = self.client.currentsong()
				playlist_info = self.client.playlistinfo()
			except:
				logging.debug("Could not get status from MPD daemon")
				return { 'state':u"stop", 'artist':u"", 'title':u"", 'album':u"", 'current':0, 'remaining':u"", 'duration':0, 'position':u"", 'volume':0, 'playlist_display':u"", 'playlist_position':0, 'playlist_count':0, 'bitrate':u"", 'type':u"" }

		state = m_status.get('state')
		if state == "play":
			artist = m_currentsong.get('artist')
			name = m_currentsong.get('name')

			# Trying to have something to display.  If artist is empty, try the
			# name field instead.
			if artist is None:
				artist = name

			title = m_currentsong.get('title')
			album = m_currentsong.get('album')
			playlist_position = int(m_status.get('song'))+1
			playlist_count = int(m_status.get('playlistlength'))
			volume = int(m_status.get('volume'))

			# MPDs rate data changes continuously.
			# To prevent the screen from unnecessarily refreshing limit updates to every 20 seconds
			if self.ratereadexpired < time.time():
				self.ratereadexpired = time.time() + 20
				self.bitrate = "{0} kbps".format(m_status.get('bitrate'))

			try:
				audio = m_status['audio'].split(':')
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
			except KeyError:
				tracktype = u""

			(current, duration) = (m_status.get('time').split(":"))

			# since we are returning the info as a JSON formatted return, convert
			# any None's into reasonable values
			if artist is None: artist = u""
			if title is None: title = u""
			if album is None: album = u""
			if current is None: current = 0
			if volume is None: volume = 0
			if self.bitrate is None: self.bitrate = u""
			if tracktype is None: tracktype = u""
			if duration is None: duration = 0

			# if duration is not available, then suppress its display
			if int(duration) > 0:
				timepos = time.strftime("%M:%S", time.gmtime(int(current))) + "/" + time.strftime("%M:%S", time.gmtime(int(duration)))
				remaining = time.strftime("%M:%S", time.gmtime( int(duration) - int(current) ) )
			else:
				timepos = time.strftime("%M:%S", time.gmtime(int(current)))
				remaining = timepos

			# If playlist is length 1 and the song playing is from an http source it is streaming
			if playlist_count == 1:
				if playlist_info[0]['file'][:4] == "http":
					playlist_display = "Streaming"
				else:
					playlist_display = "{0}/{1}".format(playlist_position, playlist_count)
			else:
					playlist_display = "{0}/{1}".format(playlist_position, playlist_count)


			return { 'state':u"play", 'artist':artist, 'title':title, 'album':album, 'remaining':remaining, 'current':current, 'duration':duration, 'position':timepos, 'volume':volume, 'playlist_display':playlist_display, 'playlist_position':playlist_position, 'playlist_count':playlist_count, 'bitrate':self.bitrate, 'type':tracktype }
	  	else:
			return { 'state':u"stop", 'artist':u"", 'title':u"", 'album':u"", 'remaining':u"", 'current':0, 'duration':0, 'position':u"", 'volume':0, 'playlist_display':u"", 'playlist_position':u"", 'playlist_count':0, 'bitrate':u"", 'type':u""}

	def status_spop(self):
		# Try to get status from SPOP daemon

		try:
			self.spotclient.write("status\n")
			spot_status_string = self.spotclient.read_until("\n").strip()
		except:
			# Try to reestablish connection to daemon
			try:
				self.spotclient = telnetlib.Telnet(SPOP_SERVER,SPOP_PORT)
				self.spotclient.read_until("\n")
				self.spotclient.write("status\n")
				spot_status_string = self.spotclient.read_until("\n").strip()
			except:
				logging.debug("Could not get status from SPOP daemon")
				return { 'state':u"stop", 'artist':u"", 'title':u"", 'album':u"", 'current':0, 'remaining':u"", 'duration':0, 'position':u"", 'volume':0, 'playlist_display':u"", 'playlist_position':0, 'playlist_count':0, 'bitrate':u"", 'type':u""}

		spot_status = json.loads(spot_status_string)

	  	if spot_status.get('status') == "playing":
			artist = spot_status.get('artist')
			title = spot_status.get('title')
			album = spot_status.get('album')
			current = spot_status.get('position')
			duration = spot_status.get('duration')
			playlist_position = spot_status.get('current_track')
			playlist_count = spot_status.get('total_tracks')

			# SPOP doesn't seem to have bitrate, track type, or volume available
			bitrate = u""
			tracktype = u""
			volume = 0

		  	# since we are returning the info as a JSON formatted return, convert
		  	# any None's into reasonable values

			if artist is None: artist = u""
			if title is None: title = u""
			if album is None: album = u""
			if current is None: current = 0
			if volume is None: volume = 0
			if bitrate is None: bitrate = u""
			if tracktype is None: tracktype = u""
			if duration is None:
				duration = 0
			else:
				# The spotify client returns time in 1000's of a second
				# Need to adjust to seconds to be consistent with MPD
				duration = duration / 1000

			# if duration is not available, then suppress its display
			if int(duration) > 0:
				timepos = time.strftime("%M:%S", time.gmtime(int(current))) + "/" + time.strftime("%M:%S", time.gmtime(int(duration)))
				remaining = time.strftime("%M:%S", time.gmtime(int(duration) - int(current) ) )

			else:
				timepos = time.strftime("%M:%S", time.gmtime(int(current)))
				remaining = timepos

			playlist_display = "{0}/{1}".format(playlist_position, playlist_count)

			return { 'state':u"play", 'artist':artist, 'title':title, 'album':album, 'remaining':remaining, 'current':current, 'duration':duration, 'position':timepos, 'volume':volume, 'playlist_display':playlist_display, 'playlist_position':playlist_position, 'playlist_count':playlist_count, 'bitrate':bitrate, 'type':tracktype }
	  	else:
			return { 'state':u"stop", 'artist':u"", 'title':u"", 'album':u"", 'remaining':u"", 'current':0, 'duration':0, 'position':u"", 'volume':0, 'playlist_display':u"", 'playlist_position':0, 'playlist_count':0, 'bitrate':u"", 'type':u""}


	def status_lms(self):
		# Try to get status from LMS daemon

		try:
			lms_status = self.lmsplayer.get_mode()
		except:
			# Try to reestablish connection to daemon
			try:
				self.lmsserver = pylms.server.Server(LMS_SERVER, LMS_PORT, LMS_USER, LMS_PASSWORD)
				self.lmsserver.connect()

				# Find correct player
				players = self.lmsserver.get_players()
				for p in players:
					### Need to find out how to get the MAC address from player
					if p.get_ref() == LMS_PLAYER:
						self.lmsplayer = p
						break
				if self.lmsplayer is None:
					self.lmsplayer = self.lmsserver.get_players()[0]
					if self.lmsplayer is None:
						raise Exception('Could not find any LMS player')

				lms_status = self.lmsplayer.get_mode()
			except (socket_error, AttributeError, IndexError):
				logging.debug("Could not get status from LMS daemon")
				return { 'state':u"stop", 'artist':u"", 'title':u"", 'album':u"", 'remaining':u"", 'current':0, 'duration':0, 'position':u"", 'volume':0, 'playlist_display':u"", 'playlist_position':0, 'playlist_count':0, 'bitrate':u"", 'type':u"", 'current_time':u""}


	  	if lms_status == "play":
			import urllib

			artist = urllib.unquote(str(self.lmsplayer.request("artist ?", True))).decode('utf-8')
			title = urllib.unquote(str(self.lmsplayer.request("title ?", True))).decode('utf-8')
			album = urllib.unquote(str(self.lmsplayer.request("album ?", True))).decode('utf-8')
			playlist_position = int(self.lmsplayer.request("playlist index ?"))+1
			playlist_count = self.lmsplayer.playlist_track_count()
			volume = self.lmsplayer.get_volume()
			current = self.lmsplayer.get_time_elapsed()
			duration = self.lmsplayer.get_track_duration()
			url = self.lmsplayer.get_track_path()

			# Get bitrate and tracktype if they are available.  Try blocks used to prevent array out of bounds exception if values are not found
			try:
				bitrate = urllib.unquote(str(self.lmsplayer.request("songinfo 2 1 url:"+url+" tags:r", True))).decode('utf-8').split("bitrate:", 1)[1]
			except:
				bitrate = u""

			try:
				tracktype = urllib.unquote(str(self.lmsplayer.request("songinfo 2 1 url:"+url+" tags:o", True))).decode('utf-8').split("type:",1)[1]
			except:
				tracktype = u""

			playlist_display = "{0}/{1}".format(playlist_position, playlist_count)
			# If the track count is greater than 1, we are playing from a playlist and can display track position and track count
			if self.lmsplayer.playlist_track_count() > 1:
				playlist_display = "{0}/{1}".format(playlist_position, playlist_count)
			# if the track count is exactly 1, this is either a short playlist or it is streaming
			elif self.lmsplayer.playlist_track_count() == 1:
				try:
					# if streaming
					if self.lmsplayer.playlist_get_info()[0]['duration'] == 0.0:
						playlist_display = "Streaming"
					# it really is a short playlist
					else:
						playlist_display = "{0}/{1}".format(playlist_position, playlist_count)
				except KeyError:
					logging.debug("In LMS couldn't get valid track information")
					playlist_display = u""
			else:
				logging.debug("In LMS track length is <= 0")
				playlist_display = u""

		  	# since we are returning the info as a JSON formatted return, convert
		  	# any None's into reasonable values

			if artist is None: artist = u""
			if title is None: title = u""
			if album is None: album = u""
			if current is None: current = 0
			if volume is None: volume = 0
			if bitrate is None: bitrate = u""
			if tracktype is None: tracktype = u""
			if duration is None: duration = 0

			# if duration is not available, then suppress its display
			if int(duration) > 0:
				timepos = time.strftime("%M:%S", time.gmtime(int(current))) + "/" + time.strftime("%M:%S", time.gmtime(int(duration)))
				remaining = time.strftime("%M:%S", time.gmtime(int(duration) - int(current) ) )

			else:
				timepos = time.strftime("%M:%S", time.gmtime(int(current)))
				remaining = timepos

			return { 'state':u"play", 'artist':artist, 'title':title, 'album':album, 'remaining':remaining, 'current':current, 'duration':duration, 'position':timepos, 'volume':volume, 'playlist_display':playlist_display,'playlist_position':playlist_position, 'playlist_count':playlist_count, 'bitrate':bitrate, 'type':tracktype }
	  	else:
			return { 'state':u"stop", 'artist':u"", 'title':u"", 'album':u"", 'remaining':u"", 'current':0, 'duration':0, 'position':u"", 'volume':0, 'playlist_display':u"", 'playlist_position':0, 'playlist_count':0, 'bitrate':u"", 'type':u""}


	def status(self):

		# If you are using Rune
		if RUNE_ENABLED:
			status = self.status_redis()
		elif MPD_ENABLED or SPOP_ENABLED or LMS_ENABLED:

			if MPD_ENABLED:
				# Try MPD daemon
				status = self.status_mpd()
			else:
				status = { 'state':u"stop", 'artist':u"", 'title':u"", 'album':u"", 'remaining':u"", 'current':0, 'duration':0, 'position':u"", 'volume':0, 'playlist_display':u"", 'playlist_position':0, 'playlist_count':0, 'bitrate':u"", 'type':u"" }

			# If MPD is stopped
			if status.get('state') != "play":

				# Try SPOP
				if SPOP_ENABLED:
					status = self.status_spop()
				else:
					status = { 'state':u"stop", 'artist':u"", 'title':u"", 'album':u"", 'remaining':u"", 'current':0, 'duration':0, 'position':u"", 'volume':0, 'playlist_display':u"", 'playlist_position':0, 'playlist_count':0, 'bitrate':u"", 'type':u""}

				# If SPOP is stopped
				if status.get('state') != "play":

					# Try LMS
					if LMS_ENABLED:
						status = self.status_lms()
					else:
						status = { 'state':u"stop", 'artist':u"", 'title':u"", 'album':u"", 'remaining':u"", 'current':0, 'duration':0, 'position':u"", 'volume':0, 'playlist_display':u"", 'playlist_position':0, 'playlist_count':0, 'bitrate':u"", 'type':u""}
		else:
			status = { 'state':u"stop", 'artist':u"", 'title':u"", 'album':u"", 'remaining':u"", 'current':0, 'duration':0, 'position':u"", 'volume':0, 'playlist_display':u"", 'playlist_position':0, 'playlist_count':0, 'bitrate':u"", 'type':u""}


		# Add system variables

		try:
			if TIME24HOUR == True:
				current_time = moment.utcnow().timezone(TIMEZONE).strftime("%H:%M").strip()
				current_time_sec = moment.utcnow().timezone(TIMEZONE).strftime("%H:%M:%S").strip()
			else:
				current_time = moment.utcnow().timezone(TIMEZONE).strftime("%-I:%M %p").strip()
				current_time_sec = moment.utcnow().timezone(TIMEZONE).strftime("%-I:%M:%S %p").strip()
		except ValueError:
			# Don't know why but on exit, the moment code is occasionally throwing a ValueError
			current_time = "00:00"
			current_time_sec = "00:00:00"

		current_ip = commands.getoutput("ip -4 route get 1 | head -1 | cut -d' ' -f8 | tr -d '\n'").strip()


		# Read Temperature from Pi's on-board temperature sensor once every 20 seconds
		if self.tempreadexpired < time.time():
			self.tempreadexpired = time.time()+20
			try:
				file = open("/sys/class/thermal/thermal_zone0/temp")
				self.tempc = int(file.read())

				# Convert value to float and correct decimal place
				self.tempc = round(float(self.tempc) / 1000,1)

				# convert to fahrenheit
				self.tempf = round(self.tempc*9/5+32,1)

				file.close()
			except IOError:
				self.tempc = 0.0
				self.tempf = 0.0
			except AttributeError:
				file.close()
				self.tempc = 0.0
				self.tempf = 0.0

		# Read available disk space remaining every 20 seconds
		if self.diskreadexpired < time.time():
			self.diskreadexpired = time.time() + 20
			try:
				# Check if running on OSX.  If yes, adjust df command
				if sys.platform == "darwin":
					p = os.popen("df /")
					line = p.readline()
					line = p.readline()
					va = line.split()
					line = "{0} {1}".format(va[3], va[4])
				else:
					# assume running on Raspberry linux
					p = os.popen("df --output='avail','pcent' /")
					line = p.readline()
					line = p.readline().strip()

				va = line.split()
				self.avail = va[0]
				self.availp = va[1]

				# remove % sign
				self.availp = self.availp[0:len(self.availp)-1]

				self.avail = int(self.avail)
				self.availp = int(self.availp)

				p.close()
			except IOError:
				self.avail = 0
				self.availp = 0
			except AttributeError:
				p.close()
				self.avail = 0
				self.availp = 0


		status['current_tempc'] = self.tempc
		status['current_tempf'] = self.tempf
		status['disk_avail'] = self.avail
		status['disk_availp'] = self.availp
		status['current_time'] = current_time
		status['current_time_sec'] = current_time
		status['current_ip'] = current_ip

		# if logging of the status data has been requested record the current status
		if STATUSLOGGING:
			self.statusfile.write(str(status)+'\n')
			self.statusfile.flush()

		return status


def Display(q, l, c, d):
  # q - Queue to receive updates from
  # l - number of lines in display
  # c - number of columns in display
  # d - driver for the display

  lines = []
  columns = []

  lcd = d
  lcd.oledReset()
  lcd.home()
  lcd.clear()

  lcd.message(STARTUP_MSG)
  time.sleep(2)

  for i in range (0, l):
	lines.append("")
	columns.append(0)

  # Get first display update off of the queue
  item = q.get()
  q.task_done()

  lcd.home()
  lcd.clear()

  for i in range(len(item)):
	# Convert from Unicode to UTF-8
	#item[i] = item[i].encode("utf-8")
	lines[i] = item[i]
	lcd.setCursor(0,i)
	lcd.message( lines[i][0:c] )

  prev_time = time.time()

  while True:
	  short_lines=True

	  # Smooth animation
	  if time.time() - prev_time < ANIMATION_SMOOTHING:
		  time.sleep(ANIMATION_SMOOTHING-(time.time()-prev_time))
	  try:
		  # Determine if any lines have been updated and if yes display them
		  for i in range(len(item)):

			  # Convert from Unicode into UTF-8
			  #item[i] = item[i].encode("utf-8")
			  # Check if line is longer than display
			  if len(item[i])>c:
				  short_lines = False

			  # Check if line has been updated
			  if lines[i] != item[i]:
				  # Create a line to print that is at least as long as the existing line
				  # This is to erase any extraneous characters on the display
				  buf = item[i].ljust(len(lines[i]))

				  # Reset cursor to beginning of changed line and then display the change
				  lcd.setCursor(0,i)
				  lcd.message(buf[0:c])

				  # Update the local line data and reset the column position for the line
				  lines[i] = item[i]
				  columns[i] = 0

		  # If lines all fit on display then we can wait for new input
		  if short_lines:
			  item=q.get()
			  q.task_done()
		  else:
			  # Update all long lines
			  for i in range(len(lines)):
				  if len(lines[i])>c:
					  buf = "%s          %s" % (lines[i], lines[i][0:DISPLAY_WIDTH-1])
				  	  #buf = "{}		{}".format(lines[i],lines[i][0:DISPLAY_WIDTH-1])
					  #buf = lines[i]+"		  "+lines[i][0:c]

					  columns[i] = columns[i]+1
					  if columns[i] > len(buf)-c:
						  columns[i]=0

					  lcd.setCursor(0,i)

					  # Print the portion of the string that is currently visible
					  lcd.message(buf[columns[i]:columns[i]+c])
			  # Since we have to continue updating the display, check for a new update but don't block
			  item=q.get_nowait()
			  q.task_done()


		  prev_time = time.time()
	  except Queue.Empty:
		  prev_time = time.time()
		  pass

def sigterm_handler(_signo, _stack_frame):
        sys.exit(0)

if __name__ == '__main__':
	signal.signal(signal.SIGTERM, sigterm_handler)
	try:
		logging.basicConfig(format='%(asctime)s:%(levelname)s:%(message)s', filename=LOGFILE, level=LOGLEVEL)
	except IOError:
		logging.basicConfig(format='%(asctime)s:%(levelname)s:%(message)s', filename="RaspDacDisplay.log", level=LOGLEVEL)

	try:
		opts, args = getopt.getopt(sys.argv[1:], "hs")
	except get.opt.GetoptError:
		print "{0} -h -s".format(sys.argv[0])
		sys.exit(2)

	simulated = False
	for opt, arg in opts:
		if opt == '-h':
			print "{0} -h -s".format(sys.argv[0])
			sys.exit()
		elif opt == '-s':
			simulated = True

	# As cstatus will get referenced inside of handlecaughtexceptions, make sure it has a valid value
	cstatus = { }

	# Move unhandled exception messages to log file
	def handleuncaughtexceptions(exc_type, exc_value, exc_traceback):
		if issubclass(exc_type, KeyboardInterrupt):
			sys.__excepthook__(exc_type, exc_value, exc_traceback)
			return

		logging.error("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))
		if len(cstatus) > 0:
			logging.error("Player status at exception")
			logging.error(str(cstatus))

		sys.__excepthook__(exc_type, exc_value, exc_traceback)


	sys.excepthook = handleuncaughtexceptions

	logging.info("Raspdac display starting...")

	# Suppress MPD libraries INFO messages
	loggingMPD = logging.getLogger("mpd")
	loggingMPD.setLevel( logging.WARN )

	display_driver = Winstar_GraphicOLED.Winstar_GraphicOLED([25, 24, 23, 27], 7, 8, simulated)

	try:
		dq = Queue.Queue()  # Create display Queue
		dm = Thread(target=Display, args=(dq,DISPLAY_HEIGHT,DISPLAY_WIDTH))
		dm.setDaemon(True)
		dm.start()

		rd = RaspDac_Display()
	except:
		#e = sys.exc_info()[0]
		#logging.critical("Received exception: %s" % e)
#		e = sys.exc_info()[0]
		logging.critical("Unable to initialize RaspDac Display.  Exiting...")
		logging.critical("Exception", exc_info = (sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2]))

		if DISPLAY_INSTALLED:
			GPIO.cleanup()
		else:
			curses.endwin()

		sys.exit(0)

	try:
		current_page_number = -1
		current_line_number = 0
		page_expires = 0
		hesitation_expires = 0
		curlines = []
		hesitate_expires = []
		alert_mode = False

		# Reset all of the alert message cooling values
		for pl in pages.ALERT_LIST:
			pl['cooling_expires'] = 0

		# Initialize previous state
		prev_state = rd.status()

		# Force the system to recognize the start state as a change
		prev_state['state'] = ""

		while True:
			# Get current state of the player
			cstatus = rd.status()
			state = cstatus.get('state')

			alert_check = False
			# Check to see if any alerts are triggered
			for pl in pages.ALERT_LIST:


				# Check to see if alert is in its cooling period
				if pl['cooling_expires'] < time.time():

					# Use try block to skip page if variables are missing
					try:
						# Check to see what type of monitoring to perform
						if pl['alert']['type'] == "change":
							if cstatus[pl['alert']['variable']] != prev_state[pl['alert']['variable']]:
								prev_state[pl['alert']['variable']] = cstatus[pl['alert']['variable']]
								# Some state changes cause variable changes like volume
								# Check to see if these dependent variable changes
								# should be suppressed
								try:
									if prev_state['state'] == state or not pl['alert']['suppressonstatechange']:
										alert_check = True
								except KeyError:
									pass
						elif pl['alert']['type'] == "above":
							if cstatus[pl['alert']['variable']] > pl['alert']['values'][0]:
								alert_check = True
						elif pl['alert']['type'] == "below":
							if cstatus[pl['alert']['variable']] < pl['alert']['values'][0]:
								alert_check = True
						elif pl['alert']['type'] == "range":
							if cstatus[pl['alert']['variable']] > pl['alert']['values'][0] and cstatus[pl['alert']['variable']] < pl['alert']['values'][1]:
								alert_check = True

						if alert_check:
							alert_mode = True

							# Set current_pages to the alert page
							current_pages = pl
							current_page_number = 0
							current_line_number = 0
							page_expires = time.time() + current_pages['pages'][current_page_number]['duration']
							curlines = []
							hesitate_expires = []

							# Set cooling expiry time.  If not coolingperiod directive, use default
							try:
								pl['cooling_expires'] = time.time() + pl['alert']['coolingperiod']
							except KeyError:
								pl['cooling_expires'] = time.time() + COOLING_PERIOD

							# if an alert has been found, break out of the loop
							# this has the effect of making the order of the list the priority of the messages
							break

					except (KeyError, AttributeError, IndexError):
						pass


			# Set interruptible value.  If value not present, set to default value of True
			try:
				# interruptible is only an override until the page expires.  If page expires, allow page updates to continue.
				if page_expires < time.time():
					interruptible = True

					# if page just expired on an alert page then force restore to current play state
					if alert_mode:
						alert_mode = False
						prev_state['state'] = ""
				else:
					interruptible = current_pages['interruptible']
			except KeyError:
				interruptible = True

			# check to see if we need to change the display to something new
			if (alert_mode or state != prev_state['state']) and interruptible:
				current_page_number = -1
				current_line_number = 0
				page_expires = 0
				curlines = []
				hesitate_expires = []

				# if change caused by state change and not alert
				if alert_mode == False:
					prev_state['state'] = state

					# Set to new display page
					if state != "play":
						current_pages = pages.PAGES_Stop
					# else display the PAGES_Playing pages
					else:
						current_pages = pages.PAGES_Play

			# if page has expired then move to the next page
			if page_expires < time.time():

				# Move to next page and check to see if it should be displayed or hidden
				for i in range(len(current_pages['pages'])):
					current_page_number = current_page_number + 1

					# if on last page, return to first page
					if current_page_number > len(current_pages['pages'])-1:
						current_page_number = 0

					page_expires = time.time() + current_pages['pages'][current_page_number]['duration']

					cp = current_pages['pages'][current_page_number]

					try:
						hwe = cp['hidewhenempty']
					except KeyError:
						hwe = 'False'

					try:
						hwp = cp['hidewhenpresent']
					except:
						hwp = 'False'

					# to prevent old pages format from causing problems, convert values to strings
					if type(hwe) is bool:
						hwe = str(hwe)

					if type(hwp) is bool:
						hwp = str(hwp)

					if hwe.lower() == 'all' or hwe.lower() == 'true':
						allempty = True
						try:
							hvars = cp['hidewhenemptyvars']
						except KeyError:
							hvars = [ ]

						for v in hvars:
							try:
								# if the variable is a string
								if type(cstatus[v]) is unicode:
									# and it is not empty, then set allempty False and exit loop
									if len(cstatus[v]) > 0:
										allempty = False
										break
								elif type(cstatus[v]) is int:
									if not cstatus[v] == 0:
										allempty = False
										break
								else:
									# All other variable types are considered not empty
									allempty = False
									break
							except KeyError:
								# if the variable is not in cstatus consider it empty
								pass
						if not allempty:
							break
					elif hwe.lower() == 'any':
						anyempty = False
						try:
							hvars = cp['hidewhenemptyvars']
						except KeyError:
							hvars = [ ]

						for v in hvars:
							try:
								# if the variable is a string
								if type(cstatus[v]) is unicode:
									# and it is empty, then set anyempty True and exit loop
									if len(cstatus[v]) == 0:
										anyempty = True
										break

								# if the value is 0 consider it empty
								elif type(cstatus[v]) is int:
									if cstatus[v] == 0:
										anyempty = True
										break
							except KeyError:
								# if the variable is not in cstatus consider it empty
								anyempty = True
								break
						if not anyempty:
							break

					elif hwp.lower() == 'any':
						anypresent = False
						try:
							hvars = cp['hidewhenpresentvars']
						except KeyError:
							hvars = [ ]

						for v in hvars:
							try:
								# if the variable is a string
								if type(cstatus[v]) is unicode:
									# and it is present, then set anypresent True and exit loop
									if len(cstatus[v]) > 0:
										anypresent = True
										break
								elif type(cstatus[v]) is int:
									if not cstatus[v] == 0:
										anypresent = True
										break

								# if it is not a string, and not zero consider it present
								else:
									anypresent = True
									break
							except KeyError:
								# if the variable is not in cstatus consider it empty
								break
						if not anypresent:
							break

					elif hwp.lower() == 'all' or hwp.lower() == 'true':
						allpresent = True
						try:
							hvars = cp['hidewhenemptyvars']
						except KeyError:
							hvars = [ ]

						for v in hvars:
							try:
								# if the variable is a string
								if type(cstatus[v]) is unicode:
									# and it is not present, then set allpresent False and exit loop
									if len(cstatus[v]) == 0:
										allpresent = False
										break
								elif type(cstatus[v]) is int:
									if cstatus[v] == 0:
										allpresent = False
										break
							except KeyError:
								# if the variable is not in cstatus consider it empty
								allpresent = False
								break
						if not allpresent:
							break

					else:
						# If not hidewhenempty or hidewhenpresent then exit loop
						break



			# Set current_page
			current_page = current_pages['pages'][current_page_number]

			# Now display the lines from the current page
			lines = []
			for i in range(len(current_page['lines'])):

				# make sure curlines is big enough.  curlines is used to detect when the display has changed
				# if not expanded here it will cause an IndexError later if it has not already been initialized
				while len(curlines) < len(current_page['lines']):
					curlines.append("")

				# make sure hesitate_expires is big enough as well
				while len(hesitate_expires) < len(current_page['lines']):
					hesitate_expires.append(0)

				current_line = current_page['lines'][i]
				try:
					justification = current_line['justification']
				except KeyError:
					justification = "left"

				try:
					scroll = current_line['scroll']
				except KeyError:
					scroll = False

				try:
					variables = current_line['variables']
				except KeyError:
					variables = []

				# If you have specified a strftime format on the line
				# now use it to add a formatted time to cstatus
				try:
					strftime = current_line['strftime']
				except:
					# Use 12 hour clock as default
					strftime = "%-I:%M %p"

				cstatus['current_time_formatted'] = moment.utcnow().timezone(TIMEZONE).strftime(strftime).strip()

				format = current_line['format']

				# Get paramaters
				# ignore KeyError exceptions if variable is unavailable
				parms = []
				try:
					for j in range(len(current_line['variables'])):
						try:
							if type(cstatus[current_line['variables'][j]]) is unicode:
								parms.append(cstatus[current_line['variables'][j]].encode('utf-8'))
							else:
								parms.append(cstatus[current_line['variables'][j]])
						except KeyError:
							pass
				except KeyError:
					pass

				# create line to display
				line = format.format(*parms).decode('utf-8')

				# justify line
				try:
					if current_line['justification'] == "center":
						line = "{0:^{1}}".format(line, DISPLAY_WIDTH)
					elif current_line['justification'] == "right":
						line = "{0:>{1}}".format(line, DISPLAY_WIDTH)
				except KeyError:
					pass

				lines.append(line)

				# determine whether to scroll or not
				# if scroll is false, set hesitation time to large value which
				# effectively shuts off the scroll function
				if lines[i] != curlines[i]:
					curlines[i] = lines[i]
					try:
						if current_line['scroll']:
							hesitate_expires[i] = time.time() + HESITATION_TIME
						else:
							hesitate_expires[i] = time.time() + 86400 # Do not scroll
					except KeyError:
						hesitate_expires[i] = time.time() + 86400 # Do not scroll

			# Determine if the display should hesitate before scrolling
			dispval = []
			for i in range(len(lines)):
				if hesitate_expires[i] < time.time():
					dispval.append(lines[i])
				else:
					dispval.append(lines[i][0:DISPLAY_WIDTH])

			# Send dispval to the queue
			dq.put(dispval)

			# sleep before next update
			time.sleep(.25)


	except KeyboardInterrupt:
		pass

	finally:
		dq.put(["Goodbye!",""])
		logging.info("Raspdac display shutting down")
		try:
			rd.client.disconnect()
		except:
			pass
		try:
			rd.spotclient.write("bye\n")
			rd.spotclient.close()
		except:
			pass

		if STATUSLOGGING:
			rd.statusfile.close()

		time.sleep(2)
		dq.put(["",""])
		time.sleep(1)
		if DISPLAY_INSTALLED:
			GPIO.cleanup()
		else:
			curses.endwin()
