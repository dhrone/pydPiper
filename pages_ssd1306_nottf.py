#!/usr/bin/python.pydPiper
# coding: UTF-8

from __future__ import unicode_literals


# Page Definitions
# See Page Format.txt for instructions and examples on how to modify your display settings

# Load the fonts needed for this system
FONTS = {
	'small': { 'default':True, 'file':'latin1_5x8.fnt','size':(5,8) },
#	'large': { 'file':'BigFont_10x16.fnt', 'size':(10,16) },
	'large': { 'file':'Vintl01_10x16.fnt', 'size':(10,16) },
	'tiny': { 'file':'upperasciiwide_3x5_fixed.fnt', 'size':(5,5) },
}

IMAGES = {
	'progbar': {'file':'progressbar_80x8.png' },
	'splash': {'file':'pydPiper_fixed_splash.png' }
}

# Load the Widgets that will be used to produce the display pages
WIDGETS = {
	'xofy': { 'type':'text', 'format':'{0}/{1}', 'variables':['playlist_position', 'playlist_length'], 'font':'small', 'size':(58,16), 'varwidth':True },
	'volume': { 'type':'text', 'format':'Volume: {0}', 'variables':['volume'], 'font':'small', 'just':'right', 'size':(60,16), 'varwidth':True },
	'volumelarge': { 'type':'text', 'format':'Volume: {0}', 'variables':['volume'], 'font':'large', 'just':'left', 'varwidth':True },
	'volumebar': { 'type':'progressbar', 'value':'volume', 'rangeval':(0,100), 'size':(115,8) },
	'artist': { 'type':'text', 'format':'{0}', 'variables':['artist'], 'font':'large','varwidth':True,'effect':('scroll','left',1,1,20,'onloop',3,125)},
	'title': { 'type':'text', 'format':'{0}', 'variables':['title'], 'font':'small','varwidth':True,'effect':('scroll','left',1,1,20,'onloop',3,125)},
	'samplerate': { 'type':'text', 'format':'{0}', 'variables':['samplerate'], 'font':'small', 'just':'center','varwidth':True},
	'bitdepth': { 'type':'text', 'format':'{0}', 'variables':['bitdepth'], 'font':'small', 'just':'center','varwidth':True},
	'elapsed': { 'type':'text', 'format':'{0}', 'variables':['elapsed|strftime+%-M:%S'], 'font':'small','size':(30,8), 'varwidth':True},
	'length': { 'type':'text', 'format':'{0}', 'variables':['length|strftime+%-M:%S'], 'font':'small','size':(30,8),'just':'right','varwidth':True},
	'songprogress': { 'type':'progressbar', 'value':'elapsed', 'rangeval':(0,'length'), 'size':(62,8) },
	'time': { 'type':'text', 'format':'{0}', 'variables':['utc|timezone+US/Eastern|strftime+%-I:%M'], 'font':'large', 'just':'right', 'varwidth':True, 'size':(45,16) },
	'ttime': { 'type':'ttext', 'format':'{0}', 'variables':['utc|timezone+US/Eastern|strftime+%-I:%M'], 'font':'large', 'just':'right', 'varwidth':True },
	'ampm': { 'type':'text', 'format':'{0}', 'variables':['utc|timezone+US/Eastern|strftime+%p'], 'font':'tiny', 'varwidth':True },
	'tempsmall': { 'type':'text', 'format':'{0}', 'variables':['outside_temp_formatted'], 'font':'small', 'just':'right', 'size':(24,16) },
	'temphilow': { 'type':'text', 'format':'H {0}\nL {1}', 'variables':['outside_temp_max|int', 'outside_temp_min|int'], 'font':'small', 'just':'right', 'size':(25,16) },
	'temp': { 'type':'text', 'format':'{0}', 'variables':['outside_temp_formatted'], 'font':'large', 'just':'center', 'size':(80,16) },
	'weather': { 'type':'text', 'format':'{0}', 'variables':['outside_conditions|capitalize'], 'font':'large','varwidth':True, 'effect':('scroll','left',1,1,20,'onloop',3,100)}
}

# Assemble the widgets into canvases.  Only needed if you need to combine multiple widgets together so you can produce effects on them as a group.
CANVASES = {
	'playing': { 'widgets': [ ('xofy',3,0), ('volume',68,0), ('artist',3,10), ('title',3,26), ('bitdepth',22,45), ('samplerate',78,45), ('elapsed',3,56), ('length',98,56), ('songprogress',33,56) ], 'size':(128,64) },
	'stoptime': { 'widgets': [ ('ttime',10,2) ], 'size':(128,64) },
	'stoptimetemp_popup': { 'widgets': [ ('ttime',3,0), ('tempsmall',100,0), ('weather',8,47), ('temphilow',100,48) ], 'size':(128,64) },
	'volume_changed': { 'widgets': [ ('volumelarge',8,0), ('volumebar',8,18) ], 'size':(128,64) }
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
			{ 'name':'playing', 'duration':999, 'conditional':'True' }
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
		'coordinates':(0,0),
		'canvases': [ { 'name':'volume_changed', 'duration':2 } ],
		'conditional': "db['volume'] != dbp['volume']",
		'minimum':2,
	}
]
