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

# Load the Widgets that will be used to produce the display pages

WIDGETS = {
	'name': { 'type':'text', 'format':'{0}', 'variables':['name'], 'font':'small','varwidth':True, 'effect':('scroll','left',1,20,'onloop',2,100) },
	'description': { 'type':'text', 'format':'{0} {1}', 'variables':['description','abv'], 'font':'small','varwidth':True, 'effect':('scroll','left',1,20,'onloop',2,100)},
	'remaining': { 'type':'text', 'format':'{0}', 'variables':['remaining'], 'font':'small', 'varwidth':True, 'effect':('scroll','left',1,20,'onloop',2,100)},
	'time': { 'type':'text', 'format':'{0}', 'variables':['time_formatted'], 'font':'large', 'just':'center', 'size':(100,16) },
	'temp': { 'type':'text', 'format':'{0}', 'variables':['outside_temp_formatted'], 'font':'large', 'just':'center', 'size':(100,16) }
}

WIDGETS_old = {
	'title': { 'type':'text', 'format':'{0}', 'variables':['title'], 'font':'small','effect':('scroll','left',1,20,'onloop',2,100) },
	'artist': { 'type':'text', 'format':'{0}', 'variables':['artist'], 'font':'small','effect':('scroll','left',1,20,'onloop',2,100)},
	'album': { 'type':'text', 'format':'{0}', 'variables':['album'], 'font':'small','effect':('scroll','left',1,20,'onloop',2,100)},
	'playlist_display': { 'type':'text', 'format':'{0}', 'variables':['playlist_display'], 'font':'small', 'varwidth':True },
	'elapsed': { 'type':'text', 'format':'{0}', 'variables':['elapsed_formatted'], 'font':'small', 'just':'right', 'size':(50,8), 'varwidth':True },
	'time': { 'type':'text', 'format':'{0}', 'variables':['time_formatted'], 'font':'large', 'just':'center', 'size':(100,16) },
	'temp': { 'type':'text', 'format':'{0}', 'variables':['outside_temp_formatted'], 'font':'large', 'just':'center', 'size':(100,16) },
	'weather': { 'type':'text', 'format':'{0}', 'variables':['outside_conditions'], 'font':'small','effect':('scroll','left',1,20,'onloop',2,100)},
	'radio': { 'type':'text', 'format':"RADIO", 'font':'small' },
	'volume': { 'type':'text', 'format':'Volume {0}', 'variables':['volume'], 'font':'small', 'just':'center', 'size':(80,8)},
	'volumebar': { 'type':'progressbar', 'value':'volume', 'rangeval':(0,100), 'size':(80,6) },
	'showplay': { 'type':'text', 'format':'\0xe000 PLAY', 'font':'large' },
	'showstop': { 'type':'text', 'format':'\0xe010 STOP', 'font':'large' },
	'showrandom': { 'type':'text', 'format':'\0xe020 Random', 'font':'large' },
	'showrepeatonce': { 'type':'text', 'format':'\0xe030 Repeat Once', 'font':'large' },
	'showrepeatall': { 'type':'text', 'format':'\0xe040 Repeat All', 'font':'large' },
	'temptoohigh': { 'type':'text', 'format':'\xe100 Warning System Too Hot ({0})', 'variables':['system_temp_formatted'], 'font':'large', 'effect':('scroll','left',1,20,'onstart',2,100) }
}

# Assemble the widgets into canvases.  Note, canvases are actually widgets and you can add any widget to a canvas, including other canvases
# The only differences between placing a widget in CANVASES as opposed to WIDGETS is that the type is assumed to be 'type':'canvas'.
CANVASES = {
	'showname': { 'widgets': [ ('name',0,0), ('description',0,8) ], 'size':(100,16) },
	'showremaining': { 'widgets': [ ('name',0,0), ('description',0,8) ], 'size':(100,16) }
	'stoptimetemp_popup': { 'widgets': [ ('time',0,0), ('temp',0,16) ], 'size':(100,32), 'effect': ('popup',16,15,10 ) },
}


CANVASES_old = {
	'playartist': { 'widgets': [ ('artist',0,0), ('playlist_display',0,8), ('elapsed',50,8) ], 'size':(100,16) },
	'playartist_radio': { 'widgets': [ ('artist',0,0),  ('radio',0,0), ('elapsed',0,0) ], 'size':(100,16) },
	'playalbum': { 'widgets': [ ('album',0,0), ('playlist_display',0,8), ('elapsed',50,8) ], 'size':(100,16) },
	'playalbum_radio': { 'widgets':  [ ('album',0,0), ('radio',0,0), ('elapsed',0,0) ], 'size':(100,16) },
	'playtitle': { 'widgets':  [ ('title',0,0), ('playlist_display',0,8), ('elapsed',50,8) ], 'size':(100,16) },
	'playtitle_radio': { 'widgets':  [ ('title',0,0), ('radio',0,0), ('elapsed',0,0) ], 'size':(100,16) },
	'blank': { 'widgets': [], 'size':(100,16) },
	'stoptimetemp_popup': { 'widgets': [ ('time',0,0), ('temp',0,16) ], 'size':(100,32), 'effect': ('popup',16,15,10 ) },
	'volume_changed': { 'widgets': [ ('volume',0,0), ('volumebar',0,8) ], 'size':(80,16) },
}

# Place the canvases into sequences to display when their condition is met
# More than one sequence can be active at the same time to allow for alert messages
# Also remember that canvases are actually widgets (so widgets are also canvases).
# This means you are allowed to include a widget in the sequence without placing it on a canvas

# Note about Conditionals
# Conditionals must evaluate to a True or False resulting
# To access system variables, refer to them within the db dictionary (e.g. db['title'])
# To access the most recent previous state of a variable, refer to them within the dbp dictionary (e.g. dbp['title'])

SEQUENCES = {
	'100': {
		'canvases': [
			{ 'name':'showname', 'duration':15, 'conditional':"True" },
			{ 'name':'showremaining', 'duration':15, 'conditional':"True" }
		],
		'conditional': "db['state']=='play'"
	},
	'101': {
		'canvases': [ { 'name':'stoptimetemp_popup', 'duration':9999 } ],
		'conditional': "db['state']=='stop'"
	}
}

SEQUENCES_old = {
	'100': {
		'canvases': [
			{ 'name':'playartist', 'duration':15, 'conditional':"not db['streaming']" },
			{ 'name':'playartist_radio', 'duration':15, 'conditional':"db['streaming']" },
			{ 'name':'blank', 'duration':0.5 },
			{ 'name':'playalbum', 'duration':5, 'conditional':"not db['streaming']" },
			{ 'name':'playalbum_radio', 'duration':15, 'conditional':"db['streaming']" },
			{ 'name':'blank', 'duration':0.5 },
			{ 'name':'playtitle', 'duration':5, 'conditional':"not db['streaming']" },
			{ 'name':'playtitle_radio', 'duration':15, 'conditional':"db['streaming']" },
			{ 'name':'blank', 'duration':0.5 }
		],
		'conditional': "db['state']=='play'"
	},
	'101': {
		'canvases': [ { 'name':'stoptimetemp_popup', 'duration':9999 } ],
		'conditional': "db['state']=='stop'"
	},
	'50': {
		'coordinates':(10,0),
		'canvases': [ { 'name':'volume_changed', 'duration':2 } ],
		'conditional': "db['volume'] != dbp['volume']",
		'minimum':6,
	},
	'26': {
		'canvases': [ { 'name':'showplay', 'duration':2 } ],
		'conditional': "db['state'] != dbp['state'] and db['state']=='play'",
	},
	'25': {
		'canvases': [ { 'name':'showplay', 'duration':2 } ],
		'conditional': "db['state'] != dbp['state'] and db['state']=='stop'",
	},
	'30': {
		'canvases': [ { 'name':'showplay', 'duration':2 } ],
		'conditional': "db['random'] != dbp['random'] and db['random'] ",
	},
	'31': {
		'canvases': [ { 'name':'showplay', 'duration':2 } ],
		'conditional': "db['single'] != dbp['single'] and db['single']",
	},
	'32': {
		'canvases': [ { 'name':'showplay', 'duration':2 } ],
		'conditional': "db['repeat'] != dbp['repeat'] and db['repeat']",
	},
	'10': {
		'canvases': [ { 'name':'temptoohigh', 'duration':5 } ],
		'conditional': "db['system_tempc'] > 85",
		'coolingperiod':30
	}
}


PAGES_Play = {
  'name':"Play",
  'pages':
	[
	  {
		'name':"Artist",
		'duration':8,
		'hidewhenempty':'any',
		'hidewhenemptyvars': [ "artist" ],
		'lines': [
		  {
			'name':"top",
			'variables': [ "artist" ],
			'format':"{0}",
			'justification':"left",
			'scroll':True
		  },
		  {
			'name':"bottom",
			'segments': [
				{
					'variables': [ "playlist_display"],
					'start':0,
					'end':5,
					'format':"{0}",
					'justification':"left",
					'scroll':False
				},
				{
					'variables': [ "elapsed_formatted" ],
					'start':5,
					'end':16,
					'format':"{0}",
					'justification':"right",
					'scroll':False
				}
			]
		  }
		]
	  },
	  {
		'name':"Blank",
		'duration':0.25,
		'lines': [
		  {
			'name':"top",
			'format':"",
		  },
		  {
			'name':"bottom",
			'segments': [
				{
					'variables': [ "playlist_display"],
					'start':0,
					'end':5,
					'format':"{0}",
					'justification':"left",
					'scroll':False
				},
				{
					'variables': [ "elapsed_formatted" ],
					'start':5,
					'end':16,
					'format':"{0}",
					'justification':"right",
					'scroll':False
				}
			]
		  }
		]
	  },
	  {
		'name':"Album",
		'duration':8,
		'hidewhenempty':'any',
		'hidewhenemptyvars': [ "album" ],
		'lines': [
		  {
			'name':"top",
			'variables': [ "album" ],
			'format':"{0}",
			'justification':"left",
			'scroll':True
		  },
		  {
			'name':"bottom",
			'segments': [
				{
					'variables': [ "playlist_display"],
					'start':0,
					'end':5,
					'format':"{0}",
					'justification':"left",
					'scroll':False
				},
				{
					'variables': [ "elapsed_formatted" ],
					'start':5,
					'end':16,
					'format':"{0}",
					'justification':"right",
					'scroll':False
				}
			]
		  }
		]
	  },
	  {
		'name':"Blank",
		'duration':0.25,
		'lines': [
		  {
			'name':"top",
			'format':"",
		  },
		  {
			'name':"bottom",
			'segments': [
				{
					'variables': [ "playlist_display"],
					'start':0,
					'end':5,
					'format':"{0}",
					'justification':"left",
					'scroll':False
				},
				{
					'variables': [ "elapsed_formatted" ],
					'start':5,
					'end':16,
					'format':"{0}",
					'justification':"right",
					'scroll':False
				}
			]
		  }
		]
	  },
	  {
		'name':"Title",
		'duration':10,
		'hidewhenempty':'any',
		'hidewhenemptyvars': [ "title" ],
		'lines': [
		  {
			'name':"top",
			'variables': [ "title" ],
			'format':"{0}",
			'justification':"left",
			'scroll':True
		  },
		  {
			'name':"bottom",
			'segments': [
				{
					'variables': [ "playlist_display"],
					'start':0,
					'end':5,
					'format':"{0}",
					'justification':"left",
					'scroll':False
				},
				{
					'variables': [ "elapsed_formatted" ],
					'start':5,
					'end':16,
					'format':"{0}",
					'justification':"right",
					'scroll':False
				}
			]
		  }
		]
	  },
	  {
		'name':"Blank",
		'duration':0.25,
		'lines': [
		  {
			'name':"top",
			'format':"",
		  },
		  {
			'name':"bottom",
			'segments': [
				{
					'variables': [ "playlist_display"],
					'start':0,
					'end':5,
					'format':"{0}",
					'justification':"left",
					'scroll':False
				},
				{
					'variables': [ "elapsed_formatted" ],
					'start':5,
					'end':16,
					'format':"{0}",
					'justification':"right",
					'scroll':False
				}
			]
		  }
		]
	  }
	]
}

PAGES_Stop = {
  'name':"Stop",
  'pages':
	[
	  {
		'name':"TIME",
		'duration':8,
		'lines': [
		  {
			'name':"top",
			'variables': [ "time_formatted" ],
			'strftime':"%a %b %-d %H:%M",
			'format':"{0}",
			'justification':"left",
			'scroll':False
		  },
		  {
			'name':"bottom",
			'variables': [ "outside_temp_formatted" ],
			'format':"Temp {0}",
			'justification':"center",
			'scroll':False
		  }
		]
	  },
	  {
		'name':"WEAHLTEMP",
		'duration':8,
		'lines': [
		  {
			'name':"top",
			'variables': [ "time_formatted" ],
			'strftime':"%a %b %-d %H:%M",
			'format':"{0}",
			'justification':"left",
			'scroll':False
		  },
		  {
			'name':"bottom",
			'variables': [ "outside_temp_max_formatted", "outside_temp_min_formatted" ],
			'format':"H {0}/L {1}",
			'justification':"center",
			'scroll':False
		  }
		]
	  },
	  {
		'name':"WEACOND",
		'duration':8,
		'lines': [
		  {
			'name':"top",
			'variables': [ "time_formatted" ],
			'strftime':"%a %b %-d %H:%M",
			'format':"{0}",
			'justification':"left",
			'scroll':False
		  },
		  {
			'name':"bottom",
			'variables': [ "outside_conditions|title" ],
			'format':"{0}",
			'justification':"center",
			'scroll':False
		  }
		]
	  }
	]
}

ALERT_Volume = {
 	'name':"Volume",
	'alert': {
  		'variable': "volume",
		'type': "change",
		'suppressonstatechange':True,
		'coolingperiod': 0
	},
	'interruptible':False,
	'pages': [
		{
		'name':"Volume",
		'font':'size5x8.speaker',
			'duration':2,
			'lines': [
		  		{
					'name':"top",
					'variables': ["volume" ],
					'format':"\x00\x01   Volume {0}",
					'justification':"left",
					'scroll':False
		  		},
		  		{
					'name':"bottom",
					'variables': [ "volume_bar_big" ],
					'format':"\x02\x03 {0}",
					'justification':"left",
					'scroll':False
		  		}
			]
	  	}
	]
}

ALERT_Play = {
 	'name':"Play",
	'alert': {
  		'variable': "state",
		'type': "change",
		'values': [ 'play' ],
		'suppressonstatechange':False,
		'coolingperiod': 0
	},
	'interruptible':False,
	'pages': [
		{
		'name':"Play",
		'font':'size5x8.player',
			'duration':1.5,
			'lines': [
		  		{
					'name':"top",
					'format':"\x01 Play",
					'justification':"left",
					'scroll':False
		  		},
		  		{
					'name':"bottom",
			'format':'',
					'justification':"left",
					'scroll':False
		  		}
			]
	  	}
	]
}

ALERT_Stop = {
 	'name':"Stop",
	'alert': {
  		'variable': "state",
		'type': "change",
		'values': [ 'stop' ],
		'suppressonstatechange':False,
		'coolingperiod': 0
	},
	'interruptible':False,
	'pages': [
		{
		'name':"Stop",
		'font':'size5x8.player',
			'duration':1.5,
			'lines': [
		  		{
					'name':"top",
					'format':"\x00 Stop",
					'justification':"left",
					'scroll':False
		  		},
		  		{
					'name':"bottom",
			'format':'',
					'justification':"left",
					'scroll':False
		  		}
			]
	  	}
	]
}

ALERT_RepeatOnce = {
 	'name':"RepeatOnce",
	'alert': {
  		'variable': "single",
		'type': "change",
		'suppressonstatechange':False,
		'coolingperiod': 0
	},
	'interruptible':False,
	'pages': [
		{
		'name':"Stop",
		'font':'size5x8.repeat_once',
			'duration':1.5,
			'lines': [
		  		{
					'name':"top",
					'format':"\x00\x01 Repeat",
					'justification':"left",
					'scroll':False
		  		},
		  		{
					'name':"bottom",
					'variables': [ "single|onoff" ],
					'format':"\x02\x03 Once {0}",
					'justification':"left",
					'scroll':False
		  		}
			]
	  	}
	]
}

ALERT_RepeatAll = {
 	'name':"RepeatAll",
	'alert': {
  		'variable': "repeat",
		'type': "change",
		'suppressonstatechange':False,
		'coolingperiod': 0
	},
	'interruptible':False,
	'pages': [
		{
		'name':"Stop",
		'font':'size5x8.repeat_all',
			'duration':1.5,
			'lines': [
		  		{
					'name':"top",
					'format':"\x00\x01 Repeat",
					'justification':"left",
					'scroll':False
		  		},
		  		{
					'name':"bottom",
					'variables': [ "repeat|onoff" ],
					'format':"\x02\x03 All {0}",
					'justification':"left",
					'scroll':False
		  		}
			]
	  	}
	]
}

ALERT_Shuffle = {
 	'name':"Shuffle",
	'alert': {
  		'variable': "random",
		'type': "change",
		'suppressonstatechange':False,
		'coolingperiod': 0
	},
	'interruptible':False,
	'pages': [
		{
		'name':"Stop",
		'font':'size5x8.shuffle',
			'duration':1.5,
			'lines': [
		  		{
					'name':"top",
					'format':"\x00\x01 Random",
					'justification':"left",
					'scroll':False
		  		},
		  		{
					'name':"bottom",
					'variables': [ "random|onoff" ],
					'format':"\x02\x03 Play {0}",
					'justification':"left",
					'scroll':False
		  		}
			]
	  	}
	]
}

ALERT_TempTooHigh = {
 	'name':"TempTooHigh",
	'alert': {
  		'variable': "system_tempc",
		'type': "above",
		'values': [ 85 ],
		'suppressonstatechange':False,
		'coolingperiod': 30
	},
	'interruptible':False,
	'pages': [
		{
			'name':"TempTooHigh",
			'duration':8,
			'lines': [
		  		{
					'name':"top",
					'variables': [ ],
					'format':"Temp Too High",
					'justification':"center",
					'scroll':False
		  		},
		  		{
					'name':"bottom",
					'variables': [ "system_tempc" ],
					'format':"Temp: {0}c",
					'justification':"center",
					'scroll':False
		  		}
			]
	  	}
	]
}


ALERT_LIST = [ ALERT_Volume, ALERT_Play, ALERT_Stop, ALERT_RepeatOnce, ALERT_RepeatAll, ALERT_Shuffle, ALERT_TempTooHigh ]
