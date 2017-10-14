#!/usr/bin/python.pydPiper
# coding: UTF-8

from __future__ import unicode_literals


# Page Definitions
# See Page Format.txt for instructions and examples on how to modify your display settings

# Load the fonts needed for this system
FONTS = {
	'small': { 'default':True, 'file':'latin1_5x8_fixed.fnt','size':(5,8) },
#	'large': { 'file':'BigFont_10x16_fixed.fnt', 'size':(10,16) },
	'tiny': { 'file':'upperasciiwide_3x5_fixed.fnt', 'size':(5,5) },
}

IMAGES = {
	'progbar': {'file':'progressbar_80x8.png' },
	'splash': {'file':'pydPiper_fixed_splash.png' }
}

# Load the Widgets that will be used to produce the display pages
WIDGETS = {
	'nowplaying': { 'type':'text', 'format':'{0}', 'variables':['actPlayer|upper'], 'font':'tiny', 'varwidth':True},
	'nowplayingdata': { 'type':'text', 'format':'{0} OF {1}', 'variables':['playlist_position', 'playlist_length'], 'font':'tiny', 'just':'right','size':(40,5),'varwidth':True},
	'title': { 'type':'text', 'format':'{0}', 'variables':['title'], 'font':'small','varwidth':True,'effect':('scroll','left',5,1,20,'onloop',3,80) },
	'artist': { 'type':'text', 'format':'{0}', 'variables':['artist'], 'font':'small','varwidth':True,'effect':('scroll','left',5,1,20,'onloop',3,80)},
	'album': { 'type':'text', 'format':'{0}', 'variables':['album'], 'font':'small','varwidth':True,'effect':('scroll','left',5,1,20,'onloop',3,80)},
	'time': { 'type':'text', 'format':'{0}', 'variables':['utc|timezone+US/Eastern|strftime+%-I:%M'], 'font':'small', 'just':'right', 'varwidth':True, 'size':(50,16) },
	'ampm': { 'type':'text', 'format':'{0}', 'variables':['utc|timezone+US/Eastern|strftime+%p'], 'font':'tiny', 'varwidth':True },
	'tempsmall': { 'type':'text', 'format':'{0}', 'variables':['outside_temp_formatted'], 'font':'small', 'just':'right', 'size':(20,8) },
	'temphilow': { 'type':'text', 'format':'H {0}\nL {1}', 'variables':['outside_temp_max|int', 'outside_temp_min|int'], 'font':'small', 'just':'right', 'size':(25,16) },
	'temp': { 'type':'text', 'format':'{0}', 'variables':['outside_temp_formatted'], 'font':'small', 'just':'center', 'size':(80,16) },
	'weather': { 'type':'text', 'format':'{0}', 'variables':['outside_conditions|capitalize'], 'font':'small','varwidth':True, 'size':(55,16), 'effect':('scroll','left',5,1,20,'onloop',3,80)},
	'radio': { 'type':'text', 'format':"RADIO", 'font':'tiny', 'varwidth':True, 'size':(40,5), 'just':'right' },
	'volume': { 'type':'text', 'format':'VOLUME ({0})', 'variables':['volume'], 'font':'tiny', 'varwidth':True, 'just':'left', 'size':(60,8)},
	'volumebar': { 'type':'progressimagebar', 'image':'progbar','value':'volume', 'rangeval':(0,100) },
	'songprogress': { 'type':'progressbar', 'value':'elapsed', 'rangeval':(0,'length'), 'size':(80,1) },
	'showplay': { 'type':'text', 'format':'\ue000 PLAY', 'font':'small', 'varwidth':True, 'just':'center', 'size':(80,16) },
	'showstop': { 'type':'text', 'format':'\ue001 STOP', 'font':'small', 'varwidth':True, 'just':'center', 'size':(80,16) },
	'randomsymbol': { 'type':'text', 'format':'\ue002 ', 'font':'small', 'varwidth':True, 'size':(10,16) },
	'temptoohigh': { 'type':'text', 'format':'\ue005 Warning System Too Hot ({0})', 'variables':['system_temp_formatted'], 'font':'small', 'varwidth':True, 'effect':('scroll','left',5,1,20,'onstart',3,80) }
}

# Assemble the widgets into canvases.  Only needed if you need to combine multiple widgets together so you can produce effects on them as a group.
CANVASES = {
	'playartist': { 'widgets': [ ('artist',0,7), ('nowplaying',0,0), ('nowplayingdata',40,0), ('songprogress',0,15) ], 'size':(80,16) },
	'playalbum': { 'widgets': [ ('album',0,7), ('nowplaying',0,0), ('nowplayingdata',40,0), ('songprogress',0,15) ], 'size':(80,16) },
	'playtitle': { 'widgets':  [ ('title',0,7), ('nowplaying',0,0), ('nowplayingdata',40,0), ('songprogress',0,15) ], 'size':(80,16) },
	'playartist_radio': { 'widgets': [ ('artist',0,7), ('nowplaying',0,0), ('radio',40,0), ('songprogress', 0,15) ], 'size':(80,16) },
	'playalbum_radio': { 'widgets':  [ ('album',0,7), ('nowplaying',0,0), ('radio',40,0), ('songprogress', 0,15) ], 'size':(80,16) },
	'playtitle_radio': { 'widgets':  [ ('title',0,7), ('nowplaying',0,0), ('radio',40,0), ('songprogress',0,15) ], 'size':(80,16) },
	'blank': { 'widgets': [], 'size':(100,16) },
	'stoptime': { 'widgets': [ ('time',10,2), ('ampm',60,2) ], 'size':(80,16) },
	'stoptimetemp_popup': { 'widgets': [ ('time',0,2), ('ampm',50,2), ('tempsmall',60,8), ('weather',0,17), ('temphilow',55,16) ], 'size':(80,32), 'effect': ('popup',16,15,10 ) },
	'volume_changed': { 'widgets': [ ('volume',5,0), ('volumebar',0,8) ], 'size':(80,16) },
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
			{ 'name':'playalbum', 'duration':30, 'conditional':"not db['stream']=='webradio'" },
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
		'minimum':2,
	},
	{
		'name': 'seqAnnounceStop',
		'canvases': [ { 'name':'showstop', 'duration':2 } ],
		'conditional': "db['state'] != dbp['state'] and db['state']=='stop'",
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
