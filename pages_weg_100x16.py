#!/usr/bin/python.pydPiper
# coding: UTF-8

from __future__ import unicode_literals


# Page Definitions
# See Page Format.txt for instructions and examples on how to modify your display settings

# Load the fonts needed for this system
FONTS = {
	'small': { 'file':'latin1_5x8.fnt','size':(5,8) },
	'large': { 'file':'Vintl01_10x16.fnt', 'size':(10,16) },
	'tiny': { 'file':'upperascii_3x5.fnt', 'size':(5,5) }
}

IMAGES = {
	'splash': { 'file':'pydPiper_splash.png' },
	'progbar': {'file':'progressbar_100x8.png' }
}

# Load the Widgets that will be used to produce the display pages
WIDGETS = {
	'splash': { 'type':'image', 'image':'splash' },
	'nowplaying': { 'type':'text', 'format':'NOW PLAYING', 'variables':[], 'font':'tiny', 'varwidth':True},
	'nowplayingdata': { 'type':'text', 'format':'{0} OF {1}', 'variables':['playlist_position', 'playlist_length'], 'font':'tiny', 'just':'right','size':(50,5),'varwidth':True},
	'title': { 'type':'text', 'format':'{0}', 'variables':['title'], 'font':'small','varwidth':True,'effect':('scroll','left',1,1,20,'onloop',3,100) },
	'artist': { 'type':'text', 'format':'{0}', 'variables':['artist'], 'font':'small','varwidth':True,'effect':('scroll','left',1,1,20,'onloop',3,100)},
	'album': { 'type':'text', 'format':'{0}', 'variables':['album'], 'font':'small','varwidth':True,'effect':('scroll','left',1,1,20,'onloop',3,100)},
	'playlist_display': { 'type':'text', 'format':'{0}', 'variables':['playlist_display'], 'font':'small', 'varwidth':True },
	'elapsed': { 'type':'text', 'format':'{0}', 'variables':['elapsed_formatted'], 'font':'small', 'just':'right', 'size':(50,8), 'varwidth':True },
	'time': { 'type':'text', 'format':'{0}', 'variables':['localtime|strftime+%-I:%M'], 'font':'large', 'just':'left', 'size':(50,16) },
	'ampm': { 'type':'text', 'format':'{0}', 'variables':['localtime|strftime+%p'], 'font':'tiny', 'just':'left' },
	'tempsmall': { 'type':'text', 'format':'Temp\n{0}', 'variables':['outside_temp_formatted'], 'font':'small', 'just':'right', 'size':(30,16) },
	'temphilow': { 'type':'text', 'format':'h {0}\nl {1}', 'variables':['outside_temp_max|int', 'outside_temp_min|int'], 'font':'small', 'just':'right', 'size':(30,16) },
	'temp': { 'type':'text', 'format':'{0}', 'variables':['outside_temp_formatted'], 'font':'large', 'just':'center', 'size':(100,16) },
	'weather': { 'type':'text', 'format':'{0}', 'variables':['outside_conditions|capitalize'], 'font':'large','varwidth':True, 'size':(70,16), 'effect':('scroll','left',1,1,20,'onloop',3,70)},
	'radio': { 'type':'text', 'format':"RADIO", 'font':'small', 'varwidth':True },
	'volume': { 'type':'text', 'format':'VOLUME ({0})', 'variables':['volume'], 'font':'tiny', 'varwidth':True, 'just':'left', 'size':(80,8)},
	'volumebar': { 'type':'progressimagebar', 'image':'progbar','value':'volume', 'rangeval':(0,100) },
	'songprogress': { 'type':'progressbar', 'value':'elapsed', 'rangeval':(0,'length'), 'size':(100,1) },
	'showplay': { 'type':'text', 'format':'\ue000 PLAY', 'font':'large', 'varwidth':True, 'just':'center', 'size':(100,16) },
	'showstop': { 'type':'text', 'format':'\ue001 STOP', 'font':'large', 'varwidth':True, 'just':'center', 'size':(100,16) },
	'randomsymbol': { 'type':'text', 'format':'\ue002 ', 'font':'large', 'varwidth':True, 'size':(20,16) },
	'random': { 'type':'text', 'format':'Random\n{0}', 'variables':['random|onoff|Capitalize'], 'font':'small', 'varwidth':True, 'size':(85,16) },
	'repeatoncesymbol': { 'type':'text', 'format':'\ue003 ', 'font':'large', 'varwidth':True, 'size':(20,16) },
	'repeatonce': { 'type':'text', 'format':'Repeat Once\n{0}', 'variables':['single|onoff|Capitalize'], 'font':'small', 'varwidth':True, 'just':'center', 'size':(85,16) },
	'repeatallsymbol': { 'type':'text', 'format':'\ue004 ', 'font':'large', 'varwidth':True, 'size':(20,16) },
	'repeatall': { 'type':'text', 'format':'Repeat All\n{0}', 'variables':['repeat|onoff|Capitalize'], 'font':'small', 'varwidth':True, 'size':(85,16) },
	'temptoohigh': { 'type':'text', 'format':'\xe0005 Warning System Too Hot ({0})', 'variables':['system_temp_formatted'], 'font':'large', 'varwidth':True, 'effect':('scroll','left',1,1,20,'onstart',3,100) }
}

# Assemble the widgets into canvases.  Only needed if you need to combine multiple widgets together so you can produce effects on them as a group.
CANVASES = {
	'playartist': { 'widgets': [ ('artist',0,6), ('nowplaying',0,0), ('nowplayingdata',50,0), ('songprogress',0,15) ], 'size':(100,16) },
	'playartist_radio': { 'widgets': [ ('artist',0,0),  ('radio',0,8), ('elapsed',50,8) ], 'size':(100,16) },
	'playalbum': { 'widgets': [ ('album',0,6), ('nowplaying',0,0), ('nowplayingdata',50,0), ('songprogress',0,15) ], 'size':(100,16) },
	'playalbum_radio': { 'widgets':  [ ('album',0,0), ('radio',0,8), ('elapsed',50,8) ], 'size':(100,16) },
	'playtitle': { 'widgets':  [ ('title',0,6), ('nowplaying',0,0), ('nowplayingdata',50,0), ('songprogress',0,15) ], 'size':(100,16) },
	'playtitle_radio': { 'widgets':  [ ('title',0,0), ('radio',0,8), ('elapsed',50,8) ], 'size':(100,16) },
	'showrandom': { 'widgets': [ ('randomsymbol',0,0), ('random', 15,0) ], 'size':(100,16) },
	'showrepeatonce': { 'widgets': [ ('repeatoncesymbol',0,0), ('repeatonce', 15,0) ], 'size':(100,16) },
	'showrepeatall': { 'widgets': [ ('repeatallsymbol',0,0), ('repeatall', 15,0) ], 'size':(100,16) },
	'blank': { 'widgets': [], 'size':(100,16) },
	'stoptime': { 'widgets': [ ('time',15,1), ('ampm',70,2) ], 'size':(100,16) },
	'stoptimetemp_popup': { 'widgets': [ ('time',6,1), ('apmp',60,1), ('tempsmall',70,0), ('weather',0,17), ('temphilow',70,16) ], 'size':(100,32), 'effect': ('popup',16,15,10 ) },
	'volume_changed': { 'widgets': [ ('volume',3,0), ('volumebar',0,8) ], 'size':(100,16) },
}

# Place the canvases into sequences to display when their condition is met
# More than one sequence can be active at the same time to allow for alert messages
# You are allowed to include a widget in the sequence without placing it on a canvas

# Note about Conditionals
# Conditionals must evaluate to a True or False resulting
# To access system variables, refer to them within the db dictionary (e.g. db['title'])
# To access the most recent previous state of a variable, refer to them within the dbp dictionary (e.g. dbp['title'])
SEQUENCES = [
	{
		'name': 'seqPlay',
		'canvases': [
			{ 'name':'playartist', 'duration':15, 'conditional':"not db['stream']=='webradio'" },
			{ 'name':'playartist_radio', 'duration':15, 'conditional':"db['stream']=='webradio'" },
			{ 'name':'playalbum', 'duration':15, 'conditional':"not db['stream']=='webradio'" },
			{ 'name':'playalbum_radio', 'duration':15, 'conditional':"db['stream']=='webradio' and db['album']" },
			{ 'name':'playtitle', 'duration':30, 'conditional':"not db['stream']=='webradio'" },
			{ 'name':'playtitle_radio', 'duration':15, 'conditional':"db['stream']=='webradio'" },
		],
		'conditional': "db['state']=='play'"
	},
	{
		'name': 'seqStop',
		'canvases': [
			{ 'name':'stoptimetemp_popup', 'duration':9999, 'conditional':"not db['outside_conditions']=='No data'" },
			{ 'name':'stoptime', 'duration':9999, 'conditional':"db['outside_conditions']=='No data'" }
		],
		'conditional': "db['state']=='stop'"
	},
	{
		'name':'seqVolume',
		'coordinates':(10,0),
		'canvases': [ { 'name':'volume_changed', 'duration':2 } ],
		'conditional': "db['volume'] != dbp['volume']",
		'minimum':2,
	},
	{
		'name': 'seqAnnouncePlay',
		'canvases': [ { 'name':'showplay', 'duration':2 } ],
		'conditional': "db['state'] != dbp['state'] and db['state']=='play'",
	},
	{
		'name': 'seqAnnounceStop',
		'canvases': [ { 'name':'showstop', 'duration':2 } ],
		'conditional': "db['state'] != dbp['state'] and db['state']=='stop'",
	},
	{
		'name':'seqAnnounceRandom',
		'canvases': [ { 'name':'showrandom', 'duration':2 } ],
		'conditional': "db['random'] != dbp['random']",
	},
	{
		'name':'seqAnnounceSingle',
		'canvases': [ { 'name':'showrepeatonce', 'duration':2 } ],
		'conditional': "db['single'] != dbp['single']",
	},
	{
		'name':'seqAnnounceRepeat',
		'canvases': [ { 'name':'showrepeatall', 'duration':2 } ],
		'conditional': "db['repeat'] != dbp['repeat']",
	},
	{
		'name':'seqAnnounceTooHot',
		'canvases': [ { 'name':'temptoohigh', 'duration':5 } ],
		'conditional': "db['system_tempc'] > 85",
		'coolingperiod':30
	}
]
