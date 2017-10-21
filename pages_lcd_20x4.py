#!/usr/bin/python.pydPiper
# coding: UTF-8

from __future__ import unicode_literals


# Page Definitions
# See Page Format.txt for instructions and examples on how to modify your display settings

# Load the fonts needed for this system
FONTS = {
	'small': { 'default':True, 'file':'latin1_5x8_lcd.fnt','size':(5,8) },
	'large': { 'file':'BigFont_10x16_fixed.fnt', 'size':(10,16) },
	'tiny': { 'file':'upperasciiwide_3x5_fixed.fnt', 'size':(5,5) },
}

IMAGES = {
	'progbar': {'file':'progressbar_100x8.png' },
}

# Load the Widgets that will be used to produce the display pages
WIDGETS = {
	'splash': { 'type':'text', 'format':'pydPiper\nStarting...', 'font':'small' },
	'nowplaying': { 'type':'text', 'format':'{0}', 'variables':['actPlayer|upper'], 'font':'small', 'varwidth':True},
	'nowplayingdata': { 'type':'text', 'format':'{0} OF {1}', 'variables':['playlist_position', 'playlist_length'], 'font':'small', 'just':'right','size':(40,8),'varwidth':True},
	'title': { 'type':'text', 'format':'{0}', 'variables':['title'], 'font':'small','varwidth':True,'effect':('scroll','left',5,1,20,'onloop',3,100) },
	'artist': { 'type':'text', 'format':'{0}', 'variables':['artist'], 'font':'small','varwidth':True,'effect':('scroll','left',5,1,20,'onloop',3,100)},
	'artistradio': { 'type':'text', 'format':'{0}', 'variables':['artist'], 'font':'small','varwidth':True},
	'album': { 'type':'text', 'format':'{0}', 'variables':['album'], 'font':'small','varwidth':True,'effect':('scroll','left',5,1,20,'onloop',3,100)},
	'time': { 'type':'text', 'format':'{0}', 'variables':['localtime|strftime+%-I:%M'], 'font':'large', 'just':'right', 'varwidth':True, 'size':(65,16) },
	'timesmall': { 'type':'text', 'format':'{0}', 'variables':['localtime|strftime+%-I:%M'], 'font':'small', 'just':'right', 'varwidth':True, 'size':(40,8) },
	'ampm': { 'type':'text', 'format':'{0}', 'variables':['localtime|strftime+%p'], 'font':'small', 'varwidth':True },
	'temp': { 'type':'text', 'format':'{0}', 'variables':['outside_temp_formatted'], 'font':'small', 'just':'right', 'size':(25,8) },
	'temphilow': { 'type':'text', 'format':'H {0}\nL {1}', 'variables':['outside_temp_max|int', 'outside_temp_min|int'], 'font':'small', 'just':'right', 'size':(25,16) },
	'conditions': { 'type':'text', 'format':'{0}', 'variables':['outside_conditions|capitalize'], 'font':'small','varwidth':True, 'size':(55,16), 'effect':('scroll','left',5,1,20,'onloop',3,55)},
	'conditions2': { 'type':'text', 'format':'{0}', 'variables':['outside_conditions|capitalize'], 'font':'small','varwidth':True, 'size':(75,8), 'effect':('scroll','left',5,1,20,'onloop',3,75)},
	'radio': { 'type':'text', 'format':"RADIO", 'font':'small', 'varwidth':True, 'size':(25,8), 'just':'right' },
	'volume': { 'type':'text', 'format':'VOLUME ({0})', 'variables':['volume'], 'font':'small', 'varwidth':True, 'just':'left', 'size':(95,8)},
	'volumebar': { 'type':'progressimagebar', 'image':'progbar','value':'volume', 'rangeval':(0,100) },
	'songprogresstext': { 'type':'text', 'format':'SONG', 'font':'small' },
	'songprogress': { 'type':'progressbar', 'value':'elapsed', 'rangeval':(0,'length'), 'size':(40,8) },
	'trkprogresstext': { 'type':'text', 'format':'TRK', 'font':'small' },
	'trkprogress': { 'type':'progressbar', 'value':'playlist_position', 'rangeval':(1,'playlist_length'), 'size':(25,8) },
	'elapsed': { 'type':'text', 'format':'{0}', 'variables':['elapsed_formatted'], 'font':'small' },
	'playstopsymbol': { 'type':'text', 'format':'{0}', 'variables':['state|select+play+\ue000+stop+\ue001'], 'font':'small', 'just':'left'  },
	'randomsymbol': { 'type':'text', 'format':'\ue002 ', 'font':'large', 'varwidth':True, 'size':(10,16) },
	'random': { 'type':'text', 'format':'Random\n{0}', 'variables':['random|onoff|Capitalize'], 'font':'small', 'varwidth':True, 'size':(65,16) },
	'repeatoncesymbol': { 'type':'text', 'format':'\ue003 ', 'font':'large', 'varwidth':True, 'size':(10,16) },
	'repeatonce': { 'type':'text', 'format':'Repeat Once\n{0}', 'variables':['single|onoff|Capitalize'], 'font':'small', 'varwidth':True, 'just':'center', 'size':(65,16) },
	'repeatallsymbol': { 'type':'text', 'format':'\ue004 ', 'font':'large', 'varwidth':True, 'size':(10,16) },
	'repeatall': { 'type':'text', 'format':'Repeat All\n{0}', 'variables':['repeat|onoff|Capitalize'], 'font':'small', 'varwidth':True, 'size':(65,16) },
	'temptoohigh': { 'type':'text', 'format':'\ue005 Warning System Too Hot ({0})', 'variables':['system_temp_formatted'], 'font':'large', 'varwidth':True, 'effect':('scroll','left',5,1,20,'onstart',3,80) }
}

# Assemble the widgets into canvases.  Only needed if you need to combine multiple widgets together so you can produce effects on them as a group.
CANVASES = {
	'playartist': { 'widgets': [ ('artist',0,8), ('nowplaying',0,0), ('nowplayingdata',60,0), ('playstopsymbol', 50,16), ('songprogresstext',0,24), ('songprogress',20,24), ('trkprogresstext',60,24), ('trkprogress',75,24) ], 'size':(100,32) },
	'playalbum': { 'widgets': [ ('album',0,8), ('nowplaying',0,0), ('nowplayingdata',60,0), ('playstopsymbol', 50,16), ('songprogresstext',0,24), ('songprogress',20,24), ('trkprogresstext',60,24), ('trkprogress',75,24) ], 'size':(100,32) },
	'playtitle': { 'widgets':  [ ('title',0,8), ('nowplaying',0,0), ('nowplayingdata',60,0), ('playstopsymbol', 50,16), ('songprogresstext',0,24), ('songprogress',20,24), ('trkprogresstext',60,24), ('trkprogress',75,24) ], 'size':(100,32) },
	'play_radio': { 'widgets': [ ('artistradio',0,0), ('title',0,8), ('radio',75,0), ('playstopsymbol', 50,16), ('elapsed',0,24), ('timesmall',60,24)  ], 'size':(100,32) },
	'showrandom': { 'widgets': [ ('randomsymbol',0,0), ('random', 15,0) ], 'size':(80,16) },
	'showrepeatonce': { 'widgets': [ ('repeatoncesymbol',0,0), ('repeatonce', 15,0) ], 'size':(100,16) },
	'showrepeatall': { 'widgets': [ ('repeatallsymbol',0,0), ('repeatall', 15,0) ], 'size':(100,16) },
	'blank': { 'widgets': [], 'size':(80,16) },
	'stoptime':        { 'widgets': [ ('time',10,8), ('ampm',75,8) ], 'size':(100,32) },
	'stoptimeweather': { 'widgets': [ ('time',0,0), ('ampm',65,0), ('temphilow',75,0), ('conditions2',0,24), ('temp',75,24) ], 'size':(100,32) },
	'weather': { 'widgets': [ ('temp',0,0), ('conditions',0,8), ('temphilow', 55,0) ], 'size':(100,16) },
	'volume_changed': { 'widgets': [ ('volume',5,0), ('volumebar',0,8) ], 'size':(100,16) },
}

# Place the canvases into sequences to display when their condition is met
# More than one sequence can be active at the same time to allow for alert messages
# You are allowed to include a widget in the sequence without placing it on a canvas

# Note about Conditionals
# Conditionals must evaluate to a True or False resulting
# To access system variables, refer to them within the db dictionary (e.g. db['title'])
# To access the most recent previous state of a variable, refer to them within the dbp dictionary (e.g. dbp['title'])
SEQUENCES = [
	{	'name': 'seqSplash', 'canvases': [ { 'name':'splash', 'duration':4 } ], 'conditional':"db['state']=='starting'"   },
	{
		'name': 'seqPlay',
		'canvases': [
			{ 'name':'playartist', 'duration':8, 'conditional':"not db['actPlayer']=='webradio'" },
			{ 'name':'playalbum', 'duration':8, 'conditional':"not db['stream']=='webradio'" },
			{ 'name':'playtitle', 'duration':8, 'conditional':"not db['stream']=='webradio'" },
			{ 'name':'play_radio', 'duration':9999, 'conditional':"db['stream']=='webradio'" },
		],
		'conditional': "db['state']=='play'"
	},
	{
		'name': 'seqStop',
		'canvases': [
			{ 'name':'stoptime', 'duration':9999, 'conditional':"db['outside_conditions']=='No data'" },
			{ 'name':'stoptimeweather', 'duration':9999, 'conditional':"not db['outside_conditions']=='No data'" }
		],
		'conditional': "db['state']=='stop'"
	},
	{
		'name':'seqVolume',
		'coordinates':(0,16),
		'canvases': [ { 'name':'volume_changed', 'duration':2 } ],
		'conditional': "db['volume'] != dbp['volume'] and db['state']=='play'",
		'minimum':2,
	},
	{
		'name':'seqAnnounceRandom',
		'canvases': [ { 'name':'showrandom', 'duration':2 } ],
		'conditional': "db['random'] != dbp['random']",
		'minimum':2,
	},
	{
		'name':'seqAnnounceSingle',
		'canvases': [ { 'name':'showrepeatonce', 'duration':2 } ],
		'conditional': "db['single'] != dbp['single']",
		'minimum':2,
	},
	{
		'name':'seqAnnounceRepeat',
		'canvases': [ { 'name':'showrepeatall', 'duration':2 } ],
		'conditional': "db['repeat'] != dbp['repeat']",
		'minimum':2,
	},
	{
		'name':'seqAnnounceTooHot',
		'canvases': [ { 'name':'temptoohigh', 'duration':5 } ],
		'conditional': "db['system_tempc'] > 85",
		'minimum':5,
		'coolingperiod':30
	}
]
