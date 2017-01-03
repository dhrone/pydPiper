#!/usr/bin/python
# coding: UTF-8

# Get's players from LMS server
# Written by: Ron Ritchey

import time, sys, pylms, getopt
from pylms import server

def connect(server, port, user, pwd):

	try:
		# Connection to LMS
		dataserver = pylms.server.Server(server, port, user, pwd)
		dataserver.connect()

		players = dataserver.get_players()
		for p in players:
			print "{0} is at address {1}".format(p.get_name(), str(p)[8:])
	except (IOError, AttributeError, IndexError):
		print "Error trying to get player data"



if __name__ == "__main__":
	try:
		opts, args = getopt.getopt(sys.argv[1:],"hs:p:u:w:",["server=","port=","user","pwd"])
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
