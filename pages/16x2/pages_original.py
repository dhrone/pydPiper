PAGES_Play = {
  'name':"Play",
  'pages':
    [
      {
        'name':"Artist",
        'duration':10,
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
            'variables': [ "position" ],
            'format':"{0}",
            'justification':"center",
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
            'variables': [ "position" ],
            'format':"{0}",
            'justification':"center",
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
        'duration':12,
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
            'variables': [ "current_time" ],
            'format':"{0}",
            'justification':"center",
            'scroll':False
          }
        ]
      },
      {
        'name':"IPADDR",
        'duration':4,
        'lines': [
          {
            'name':"top",
            'variables': [ "current_ip" ],
            'format':"{0}",
            'justification':"center",
            'scroll':False
          },
          {
            'name':"bottom",
            'variables': [ "current_time" ],
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
