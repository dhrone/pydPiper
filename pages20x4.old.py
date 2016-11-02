# Page Definitions
# See Page Format.txt for instructions and examples on how to modify your display settings

PAGES_Play = {
  'name':"Play",
  'pages':
    [
      {
        'name':"AlbumArtistTitle",
        'duration':8,
		'hidewhenempty':'any',
        'hidewhenemptyvars': [ "title" ],
        'lines': [
          {
            'name':"1",
            'variables': [ "album" ],
            'format':"{0}",
            'justification':"left",
            'scroll':True
          },
          {
            'name':"2",
            'variables': [ "artist" ],
            'format':"{0}",
            'justification':"left",
            'scroll':True
          },
          {
            'name':"3",
            'variables': [ "title" ],
            'format':"{0}",
            'justification':"left",
            'scroll':True
          },
          {
            'name':"4",
            'variables': [ "playlist_display", "position" ],
            'format':"{0} {1}",
            'justification':"left",
            'scroll':False
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
        'name':"Ready",
	'font':'size5x8.system',
        'duration':15,
        'lines': [
          {
            'name':"1",
            'variables': [ "current_time_formatted" ],
            'strftime':"%A %-I:%M %p",
            'format':"\x00\x01 {0}",
            'justification':"left",
            'scroll':False
          },
          {
            'name':"2",
            'variables': [ "current_time_formatted" ],
            'strftime':"%B %-d %Y",
            'format':"\x02\x03 {0}",
            'justification':"left",
            'scroll':False
          },
          {
            'name':"3",
            'format':"",
          },
          {
            'name':"4",
            'variables': [ "current_tempf", "disk_availp" ],
            'format':"\x04\x05 {0}  \x06\x07 {1}%",
            'justification':"left",
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
            		'name':"1",
            		'format':"",
          		},
          		{
            		'name':"2",
            		'variables': ["volume" ],
            		'format':"\x00\x01   Volume {0}",
            		'justification':"left",
            		'scroll':False
          		},
          		{
            		'name':"3",
            		'variables': [ "volume_bar_big" ],
            		'format':"\x02\x03 {0}",
            		'justification':"left",
            		'scroll':False
          		},
          		{
            		'name':"4",
            		'format':"",
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
            		'name':"1",
            		'format':"",
          		},
          		{
            		'name':"2",
            		'format':"\x01 Play",
            		'justification':"center",
            		'scroll':False
          		},
          		{
            		'name':"3",
			'format':'',
          		},
          		{
            		'name':"4",
			'format':'',
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
            		'name':"1",
			'format':'',
          		},
          		{
            		'name':"2",
            		'format':"\x00 Stop",
            		'justification':"center",
            		'scroll':False
          		},
          		{
            		'name':"3",
			'format':'',
            		'justification':"left",
            		'scroll':False
          		},
          		{
            		'name':"4",
			'format':'',
          		},
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
            		'variables': [ "single_onoff" ],
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
            		'variables': [ "repeat_onoff" ],
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
            		'variables': [ "random_onoff" ],
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
  		'variable': "current_tempc",
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
            		'variables': [ "current_tempc" ],
            		'format':"Temp: {0}c",
            		'justification':"center",
            		'scroll':False
          		}
        	]
      	}
    ]
}


ALERT_LIST = [ ALERT_Volume, ALERT_Play, ALERT_Stop, ALERT_RepeatOnce, ALERT_RepeatAll, ALERT_Shuffle, ALERT_TempTooHigh ]
