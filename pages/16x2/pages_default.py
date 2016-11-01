# Page Definitions
# See Page Format.txt for instructions and examples on how to modify your display settings

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
            'variables': [ "playlist_display", "position" ],
            'format':"{0} {1}",
            'justification':"left",
            'scroll':False
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
            'variables': [ "playlist_display", "position" ],
            'format':"{0} {1}",
            'justification':"left",
            'scroll':False
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
            'variables': [ "playlist_display", "position" ],
            'format':"{0} {1}",
            'justification':"left",
            'scroll':False
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
            'variables': [ "playlist_display", "position" ],
            'format':"{0} {1}",
            'justification':"left",
            'scroll':False
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
            'variables': [ "playlist_display", "position" ],
            'format':"{0} {1}",
            'justification':"left",
            'scroll':False
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
        'duration':15,
        'lines': [
          {
            'name':"top",
            'variables': [ ],
            'format':"Ready",
            'justification':"center",
            'scroll':False
          },
          {
            'name':"bottom",
            'variables': [ "current_time_formatted" ],
            'strftime':"%a %b %-m %H:%M",
            'format':"{0}",
            'justification':"center",
            'scroll':False
          }
        ]
      },
      {
        'name':"SYSTEMVARS",
        'duration':10,
        'lines': [
          {
            'name':"top",
            'variables': [ "current_tempc", "disk_availp" ],
            'format':"Temp: {0}c / Disk {1}% full",
            'justification':"left",
            'scroll':True
          },
          {
            'name':"bottom",
            'variables': [ "current_time_formatted" ],
            'strftime':"%a %b %-m %H:%M",
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
        	'duration':2,
        	'lines': [
          		{
            		'name':"top",
            		'variables': [ ],
            		'format':"Volume",
            		'justification':"center",
            		'scroll':False
          		},
          		{
            		'name':"bottom",
            		'variables': [ "volume" ],
            		'format':"{0}",
            		'justification':"center",
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


ALERT_LIST = [ ALERT_Volume, ALERT_TempTooHigh ]
