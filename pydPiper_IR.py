#!/usr/bin/python.pydPiper
# coding: UTF-8

# pydPiper service to display music data to LCD and OLED character displays
# Written by: Ron Ritchey

from __future__ import unicode_literals
import logging, sys, getopt, signal, subprocess
import pydPiper_config
import pylms


connection_failed = 0
dataserver = None
dataplayer = None

server = pydPiper_config.LMS_SERVER
port = pydPiper_config.LMS_PORT
user = pydPiper_config.LMS_USER
pwd = pydPiper_config.LMS_PASSWORD
player = pydPiper_config.LMS_PLAYER

def connect():

	# Try up to 10 times to connect to LMS

	logging.debug(u"Connecting to LMS service on {0}:{1}".format(server, port))

	while True:
		if self.connection_failed >= 10:
			logging.debug(u"Could not connect to LMS service")
			break
		try:
			# Connection to LMS
			dataserver = pylms.server.Server(server, port, user, pwd)
			dataserver.connect()

			players = dataserver.get_players()
			for p in players:
				if p.get_ref() == player:
					dataplayer = p
					break
			if dataplayer is None:
				if len(dataserver.get_players()) > 0:
					dataplayer = dataserver.get_players()[0]
				if dataplayer is None:
					logging.critical(u"Could not find any LMS Players")
					raise RuntimeError(u"Could not find any LMS Players")
				player = str(self.dataplayer)
			break
		except (IOError, AttributeError, IndexError):
			### Trying to debug services
			logging.error(u"LMS connect failure", exc_info=sys.exc_info())

			dataserver = None
			dataplayer = None
			connection_failed += 1
			time.sleep(1)
	if dataserver is None:
		### Trying to debug services
		logging.error(u"LMS dataserver is None", exc_info=sys.exc_info())
		raise IOError(u"Could not connect to LMS")
	else:
		logging.debug(u"Connected to LMS using player {0}".format(dataplayer.get_name()))

def sigterm_handler(_signo, _stack_frame):
        sys.exit(0)

if __name__ == u'__main__':
	signal.signal(signal.SIGTERM, sigterm_handler)

	# Changing the system encoding should no longer be needed
#	if sys.stdout.encoding != u'UTF-8':
#    		sys.stdout = codecs.getwriter(u'utf-8')(sys.stdout, u'strict')

	logging.basicConfig(format=u'%(asctime)s:%(levelname)s:%(message)s', filename=pydPiper_config.LOGFILE, level=pydPiper_config.LOGLEVEL)
	logging.getLogger().addHandler(logging.StreamHandler())
	logging.getLogger(u'socketIO-client').setLevel(logging.WARNING)

	# Move unhandled exception messages to log file
	def handleuncaughtexceptions(exc_type, exc_value, exc_traceback):
		if issubclass(exc_type, KeyboardInterrupt):
			sys.__excepthook__(exc_type, exc_value, exc_traceback)
			return

		logging.error(u"Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))
		try:
			if len(mc.musicdata) > 0:
				logging.error(u"Player status at exception")
				logging.error(unicode(mc.musicdata))
		except NameError:
			# If this gets called before the music controller is instantiated, ignore it
			pass

		sys.__excepthook__(exc_type, exc_value, exc_traceback)

	sys.excepthook = handleuncaughtexceptions

	connect()
	if dataplayer is None:
		raise RuntimeError("Could not initialize LMS player")

	p = None
	p = subprocess.Popen('irw', stdout=subprocess.PIPE, stderr=None, shell=True)
	for line in iter(p.stdout.readline, ' '):
		cmd = line.split(' ')[2]
		if cmd in ['KEY_FORWARD']:
			# Send next to LMS
			dataplayer.next()
		elif cmd in ['KEY_REWIND']:
			dataplayer.prev()
		elif cmd in ['KEY_PLAY']:
			dataplayer.play()
		elif cmd in ['KEY_PAUSE']:
			dataplayer.pause()




	except KeyboardInterrupt:
		pass

	finally:
		try:
			if p not None:
				p.stdout.flush()
				p.stdout.close()
		except:
			pass
		mc.join()
		logging.info(u"Exiting...")
