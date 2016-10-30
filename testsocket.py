import logging,json,moment, time
from socketIO_client import SocketIO
logging.getLogger('socketIO-client').setLevel(logging.DEBUG)


def on_GetState_response(*args):
    print "\n\n********* Got Response **************\n\n"

def on_state_response(*args):
    status = args[0]

    ctime = moment.utcnow().timezone("US/Eastern").strftime("%-I:%M:%S %p").strip()
    print "\n\nStatus at time {0}".format(ctime)
    for item,value in status.iteritems():
      print "    [{0}]={1} {2}".format(item,value, type(value))
    print "\n\n"

def on_multiroomdevices_response(*args):
    list = args[0]['list']

    print "\n\nMultiRoomDevices"
    for i in range(0,len(list)):
      print "  Device {0}".format(i)

      for item,value in list[i].iteritems():
        print "    [{0}]={1} {2}".format(item,value, type(value))
    print "\n\n"

def on_queue_response(*args):
    list = args[0]

    print "\n\nQueue Response"

    for i in range(0,len(list)):
      print "Item {0}".format(i)
      for item,value in list[i].iteritems():
        print "    [{0}]={1} {2}".format(item,value, type(value))

    print "\n\n"

def on_getBrowseSources_response(*args):
    status = args[0]

    print "\n\nBrowseSources"
    for item,value in status.iteritems():
      if item != 'status':
        print "    [{0}]={1} {2}".format(item,value, type(value))

    print "\n\n"

try:
  with SocketIO('localhost', 3000) as socketIO:
      # Listen
      socketIO.on('pushState', on_state_response)
      socketIO.on('pushMultiRoomDevices', on_multiroomdevices_response)
      socketIO.on('getBrowseSources', on_getBrowseSources_response)
      socketIO.on('pushQueue', on_queue_response)
#     socketIO.emit('getBrowseSources', on_GetState_response)
      socketIO.emit('GetState', on_GetState_response)

      while True:
#       socketIO.emit('getState')
        socketIO.emit('getQueue', '')
        socketIO.emit('getState', '')
        socketIO.wait_for_callbacks(seconds=5)
except KeyboardInterrupt:
	pass




