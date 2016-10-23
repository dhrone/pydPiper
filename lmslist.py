#!/usr/bin/python
# coding: UTF-8

# Get's players from LMS server
# Written by: Ron Ritchey

import logging, time, sys, pylms, getopt
from pylms import server

def connect(server, port, user, pwd):

	try:
		# Connection to LMS
		dataserver = pylms.server.Server(server, port, user, pwd)
		dataserver.connect()

		players = self.dataserver.get_players()
		for p in players:
			print "{0} is at address {1}".format(str(p), p.get_name())
	except (socket_error, AttributeError, IndexError):
		print "Error trying to get player data"


	logging.basicConfig(format='%(asctime)s:%(levelname)s:%(message)s', filename='musicdata_lms.log', level=logging.DEBUG)
	logging.getLogger().addHandler(logging.StreamHandler())


if __name__ == "__main__":
	try:
		opts, args = getopt.getopt(argv,"hs:p:u:w",["server=","port=","user","pwd"])
	except getopt.GetoptError:
		print 'lmslist.py -s <server> -p <port> -u <user> -w <password>'
		sys.exit(2)

	# Set defaults
	server = 'localhost'
	port = 9090
	user = ''
	pwd= ''

	for opt, arg in opts:
		if opt == '-h':
			print 'lmslist.py -s <server> -p <port> -u <user> -w <password>'
			sys.exit()
		elif opt in ("-s", "--server"):
			server = arg
		elif opt in ("-p", "--port"):
			port = arg
		elif opt in ("-u", "--user"):
			user = arg
		elif opt in ("-w", "--pwd"):
			pwd = arg

	connect(server,port,user,pwd)
	
