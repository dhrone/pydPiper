#!/usr/bin/python.pydPiper
# coding: UTF-8

from __future__ import unicode_literals


# Page Definitions
# See Page Format.txt for instructions and examples on how to modify your display settings

# Load the fonts needed for this system
FONTS = {
	'small': {
		'file':'latin1_5x8.fnt',
		'size':(5,8)
	},
	'large': {
		'file':'Vintl01_10x16.fnt',
		'size':(10,16)
	}
}

IMAGES = {
	'keg': { 'file':'keg.png' },
	'progbar': {'file':'progressbar_100x8.png' }
}

# Load the Widgets that will be used to produce the display pages

WIDGETS = {
	'name': { 'type':'text', 'format':'{0}', 'variables':['name'], 'font':'small','varwidth':True, 'effect':('scroll','left',1,20,'onloop',2,70) },
	'description': { 'type':'text', 'format':'{0}', 'variables':['description'], 'font':'small','varwidth':True, 'effect':('scroll','left',1,20,'onloop',2,100)},
	'remaining': { 'type':'text', 'format':'{0} ozs\nremaining', 'variables':['weight'], 'font':'small', 'varwidth':True, 'size':(80,16), 'just':'left' },
	'remainingbar': { 'type':'progressimagebar', 'image':'keg', 'value':'weight', 'rangeval':(0,640), 'direction':'down' },
	'abv': { 'type':'text', 'format':'{0}', 'variables':['ABV'], 'font':'small', 'varwidth':True, 'just':'right', 'size':(30,8) },
	'empty': { 'type':'text', 'format':'{0} Almost Empty!!!', 'variables':['name'], 'font':'large', 'varwidth':True, 'effect': ('scroll','left',1,20,'onloop',2,60) },
	'time': { 'type':'text', 'format':'{0}', 'variables':['time_formatted'], 'font':'large', 'just':'center', 'size':(100,16) },
	'temp': { 'type':'text', 'format':'{0}', 'variables':['outside_temp_formatted'], 'font':'large', 'just':'center', 'size':(100,16) }
}

# Assemble the widgets into canvases.  Only needed if you need to combine multiple widgets together so you can produce effects on them as a group.
CANVASES = {
	'showname': { 'widgets': [ ('name',0,0), ('abv',70,0), ('description',0,8) ], 'size':(100,16) },
	'showremaining': { 'widgets': [ ('remaining',0,0), ('remainingbar',80,0) ], 'size':(100,16) },
	'stoptimetemp_popup': { 'widgets': [ ('time',0,0), ('temp',0,16) ], 'size':(100,32), 'effect': ('popup',16,15,10 ) },
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
		'name':'seqBeer',
		'canvases': [
			{ 'name':'showname', 'duration':15, 'conditional':"True" },
			{ 'name':'showremaining', 'duration':15, 'conditional':"True" }
		],
		'conditional': "True"
	},
	{
		'name':'seqAlmostEmpty',
		'canvases': [ { 'name':'empty', 'duration':15 } ],
		'conditional': "db['weight'] < 51",
		'minimum':15,
		'coolingperiod':45
	}
]
