#!/usr/bin/python
# coding: UTF-8

# musicdata service to read from Volumio V2
# Written by: Ron Ritchey
from __future__ import unicode_literals

import mds

import json, logging, time
#Queue, time, sys
from socketIO_client import SocketIO

class mdsVolumio2Comms(mds.playerComms):
	def __init__(self, ipaddr, port):
		self.ipaddr = ipaddr
		self.port = port

	def __str__(self):
		return '{0}:{1}'.format(self.ipaddr, self.port)


class mdsVolumio2(mds.mds):

	def establishConnection(self):
		self.socketIO = None

		for i in range(self.retriesAllowed):
			try:
				with SocketIO(self.server, self.port) as socketIO:
					self.socketIO = socketIO
					socketIO.on(u'pushState', self.on_state_response)
					socketIO.on(u'pushQueue', self.on_queue_response)

					# Request initial values
					socketIO.emit(u'getQueue', '')
					socketIO.emit(u'getState', '')
					return
			except Exception as ex:
				logging.exception('Error connecting on attempt {0}'.format(i+1))
				time.sleep(0.5)
				pass
		raise RuntimeError('Unable to connect')

	def shutdownConnection(self):
		if self.socketIO:
			del(self.socketIO)

	def listen(self):
		start = time.time()
		self.socketIO.wait_for_callbacks(seconds=20)
		self.socketIO.emit(u'getQueue', '')
		self.socketIO.emit(u'getState', '')

	def on_queue_response(self,*args):
		list = args[0]
		with self.lMDS:
			self.playerState['queue'] = list
		self.sendUpdate()

	def on_state_response(self, *args):
		# Read musicplayer status and update musicdata

		status = args[0]
		with self.lMDS:
			for k, v in status.iteritems():
				self.playerState[k] = v
		self.sendUpdate()


if __name__ == u'__main__':

	import moment, getopt

	logging.basicConfig(format=u'%(asctime)s:%(levelname)s:%(message)s', filename=u'mdsVolumio2.log', level=logging.DEBUG)
	logging.getLogger().addHandler(logging.StreamHandler())
	logging.getLogger(u'socketIO-client').setLevel(logging.WARNING)

	try:
		opts, args = getopt.getopt(sys.argv[1:],u"hs:p:",[u"server=",u"port="])
	except getopt.GetoptError:
		print u'musicdata_volumio2.py -s <server> -p <port>'
		sys.exit(2)

	# Set defaults
	server = u'localhost'
	port = 3000
#	pwd= ''

	for opt, arg in opts:
		if opt == u'-h':
			print u'mdsVolumio2.py -s <server> -p <port>'
			sys.exit()
		elif opt in (u"-s", u"--server"):
			server = arg
		elif opt in (u"-p", u"--port"):
			port = arg
#		elif opt in ("-w", "--pwd"):
#			pwd = arg

	exitapp = [ False ]
	q = Queue.Queue()
	mdr = mdsVolumio2('Volumio2', q, mdsVolumio2Comms(server, port))

	try:
		while True:
			try:
				status = q.get(timeout=1000)
				q.task_done()

				ctime = moment.utcnow().timezone(u"US/Eastern").strftime(u"%-I:%M:%S %p").strip()
				print u"\n\nStatus at time {0}".format(ctime)
				for item,value in status.iteritems():
					print u"    [{0}]={1} {2}".format(item,value, type(value))
				print u"\n\n"

			except Queue.Empty:
				pass
	except KeyboardInterrupt:
		print ''
		pass
	finally:
		exitapp[0] = True

	print u"Exiting..."
