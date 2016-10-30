import logging,json,moment, time
from socketIO_client import SocketIO
logging.getLogger('socketIO-client').setLevel(logging.DEBUG)


def on_GetState_response(*args):
    print "\n\n********* Got Response **************\n\n"



class ReadVolumio():

	def __init__(self, host='localhost', port=3000):
		self.host = host
		self.port = port

	def on_state_response(self,*args):
		status = args[0]

		ctime = moment.utcnow().timezone("US/Eastern").strftime("%-I:%M:%S %p").strip()
		print "\n\nStatus at time {0}".format(ctime)
		for item,value in status.iteritems():
			print "    [{0}]={1} {2}".format(item,value, type(value))
		print "\n\n"

	def on_multiroomdevices_response(self, *args):
		list = args[0]['list']

		print "\n\nMultiRoomDevices"
		for i in range(0,len(list)):
			print "  Device {0}".format(i)

			for item,value in list[i].iteritems():
				print "    [{0}]={1} {2}".format(item,value, type(value))
		print "\n\n"

	def on_queue_response(self, *args):
		list = args[0]

		print "\n\nQueue Response"

		for i in range(0,len(list)):
			print "Item {0}".format(i)
			for item,value in list[i].iteritems():
				print "    [{0}]={1} {2}".format(item,value, type(value))

		print "\n\n"

	def run(self):
		with SocketIO(self.host, self.port) as socketIO:
			self.socketIO = socketIO

			socketIO.on('pushState', self.on_state_response)
			socketIO.on('pushMultiRoomDevices', self.on_multiroomdevices_response)
			socketIO.on('pushQueue', self.on_queue_response)
      			socketIO.emit('GetState', on_GetState_response)

			while True:
				self.socketIO.emit('getQueue', '')
				self.socketIO.emit('getState', '')
				self.socketIO.wait_for_callbacks(seconds=5)
		

try:
	rv = ReadVolumio()
	rv.run()

except KeyboardInterrupt:
	pass


