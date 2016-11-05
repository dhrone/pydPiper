PAGES_Play = {
	'name':"Play",
	'cols':20,
	'rows':4,
	'pages':
		[
			{
				'name':"AlbumArtistTitle",
				'font':'size5x8.playing',
				'duration':8,
				'hidewhenempty':'all',
				'hidewhenemptyvars': [ "artist", "album" ],
				'lines': [
					{
						'name':"1",
						'segments': [
							{
								'variables': [ "artist" ],
								'start':2,
								'end':20,
								'format':"{0}",
								'justification':"left",
								'scroll':True,
								'scrolldirection':'left'
							}
						]
					},
					{
						'name':"2",
						'segments': [
							{
								'start':0,
								'end':2,
								'format':"\x04\x05"
							},
							{
								'variables': [ "album" ],
								'start':2,
								'end':20,
								'format':"{0}",
								'justification':"left",
								'scroll':True,
								'scrolldirection':'left'
							}
						]
					},
					{
						'name':"3",
						'segments': [
							{
								'start':0,
								'end':2,
								'format':"\x02\x03"
							},
							{
								'variables': [ "title" ],
								'start':2,
								'end':20,
								'format':"{0}",
								'justification':"left",
								'scroll':True
							}
						]
					},
					{
						'name':"4",
						'segments': [
							{
								'variables': [ "playlist_display"],
								'start':0,
								'end':10,
								'format':"  {0}",
								'justification':"left",
								'scroll':False
							},
							{
								'variables': [ "elapsed_formatted" ],
								'start':10,
								'end':20,
								'format':"{0}",
								'justification':"right",
								'scroll':False
							}
						]
					}
				]
			},
			{
				'name':"TitleOnly",
				'font':'size5x8.playing',
				'duration':8,
				'hidewhenpresent':'any',
				'hidewhenpresentvars': [ "artist", "album" ],
				'lines': [
					{
						'name':"1",
						'segments': [
							{
								'start':0,
								'end':2,
								'format':"\x02\x03"
							},
							{
								'variables': [ "title" ],
								'start':2,
								'end':20,
								'format':"{0}",
								'justification':"left",
								'scroll':True,
								'scrolldirection':'left'
							}
						]
					},
					{
						'name':"2",
						'format':"",
					},
					{
						'name':"3",
						'format':"",
					},
					{
						'name':"4",
						'segments': [
							{
								'variables': [ "playlist_display"],
								'start':0,
								'end':10,
								'format':"  {0}",
								'justification':"left",
								'scroll':False
							},
							{
								'variables': [ "elapsed_formatted" ],
								'start':10,
								'end':20,
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
				'name':"Ready",
				'font':'size5x8.system',
				'duration':10,
				'lines': [
					{
						'name':"1",
						'segments': [
							{
								'variables': [ "current_time_formatted" ],
								'strftime':"%A %-I:%M %p",
								'format':"\x00\x01 {0}",
								'start':0,
								'end':20,
								'justification':"left",
								'scroll':False
							}
						]
					},
					{
						'name':"2",
						'segments': [
							{
								'variables': [ "current_time_formatted" ],
								'strftime':"%B %-d %Y",
								'format':"\x02\x03 {0}",
								'start':0,
								'end':20,
								'justification':"left",
								'scroll':False
							}
						]
					},
					{
						'name':"3",
						'format':"",
					},
					{
						'name':"4",
						'segments': [
							{
								'variables': [ "system_temp_formatted", "disk_availp" ],
								'format':"\x04\x05 {0}	\x06\x07 {1}%",
								'start':3,
								'end':20,
								'justification':"left",
								'scroll':False
							}
						]
					}
				]
			},
			{
				'name':"ReadyWeatherTemp",
				'font':'size5x8.system',
				'duration':4,
				'lines': [
					{
						'name':"1",
						'segments': [
							{
								'variables': [ "current_time_formatted" ],
								'strftime':"%A %-I:%M %p",
								'format':"\x00\x01 {0}",
								'start':0,
								'end':20,
								'justification':"left",
								'scroll':False
							}
						]
					},
					{
						'name':"2",
						'segments': [
							{
								'variables': [ "current_time_formatted" ],
								'strftime':"%B %-d %Y",
								'format':"\x02\x03 {0}",
								'start':0,
								'end':20,
								'justification':"left",
								'scroll':False
							}
						]
					},
					{
						'name':"3",
						'format':"",
					},
					{
						'name':"4",
						'segments': [
							{
								'variables': [ "outside_temp_formatted" ],
								'format':"Outside \x04\x05 {0}",
								'start':3,
								'end':20,
								'justification':"left",
								'scroll':False
							}
						]
					}
				]
			},
			{
				'name':"ReadyWeatherConditions",
				'font':'size5x8.system',
				'duration':4,
				'lines': [
					{
						'name':"1",
						'segments': [
							{
								'variables': [ "current_time_formatted" ],
								'strftime':"%A %-I:%M %p",
								'format':"\x00\x01 {0}",
								'start':0,
								'end':20,
								'justification':"left",
								'scroll':False
							}
						]
					},
					{
						'name':"2",
						'segments': [
							{
								'variables': [ "current_time_formatted" ],
								'strftime':"%B %-d %Y",
								'format':"\x02\x03 {0}",
								'start':0,
								'end':20,
								'justification':"left",
								'scroll':False
							}
						]
					},
					{
						'name':"3",
						'format':"",
					},
					{
						'name':"4",
						'segments': [
							{
								'variables': [ "outside_conditions|title" ],
								'format':"{0}",
								'start':3,
								'end':20,
								'justification':"left",
								'scroll':False
							}
						]
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
					'segments': [
						{
							'format':""
						}
					]
				},
				{
					'name':"2",
					'segments': [
						{
							'variables': [ "volume" ],
							'format':"\x00\x01	   Volume {0}",
							'start':0,
							'end':20,
							'justification':"left",
							'scroll':False
						}
					]
				},
				{
					'name':"3",
					'segments': [
						{
							'variables': [ "volume_bar_big" ],
							'format':"\x02\x03 {0}",
							'start':0,
							'end':20
						}
					]
				},
				{
					'name':"4",
					'segments': [
						{
							'format':""
						}
					]
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
					'segments': [
						{
							'format':""
						}
					]
				},
				{
					'name':"2",
					'segments': [
						{
							'format':"\x01 Play",
							'justification':"center",
							'scroll':False
						}
					]
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
					'segments': [
						{
							'format':""
						}
					]
				},
				{
					'name':"2",
					'segments': [
						{
							'format':"\x00 Stop",
							'justification':"center",
							'scroll':False
						}
					]
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
					'segments': [
						{
							'format':"\x00\x01 Repeat",
							'justification':"left",
							'scroll':False
						}
					]
				},
				{
					'name':"bottom",
					'segments': [
						{
							'variables': [ "single|onoff" ],
							'format':"\x02\x03 Once {0}",
							'justification':"left",
							'scroll':False
						}
					]
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
					'segments': [
						{
							'format':"\x00\x01 Repeat",
							'justification':"left",
							'scroll':False
						}
					]
				},
				{
					'name':"bottom",
					'segments': [
						{
							'variables': [ "repeat|onoff" ],
							'format':"\x02\x03 All {0}",
							'justification':"left",
							'scroll':False
						}
					]
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
					'segments': [
						{
						'format':"\x00\x01 Random",
						'justification':"left",
						'scroll':False
						}
					]
				},
				{
					'name':"bottom",
					'segments': [
						{
						'variables': [ "random|onoff" ],
						'format':"\x02\x03 Play {0}",
						'justification':"left",
						'scroll':False
						}
					]
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
					'segments': [
						{
							'format':"Temp Too High",
							'justification':"center",
							'scroll':False
						}
					]
				},
				{
					'name':"bottom",
					'segments': [
						{
							'variables': [ "system_temp_formatted" ],
							'format':"Temp: {0}",
							'justification':"center",
							'scroll':False
						}
					]
				}
			]
		}
	]
}


ALERT_LIST = [ ALERT_Volume, ALERT_Play, ALERT_Stop, ALERT_RepeatOnce, ALERT_RepeatAll, ALERT_Shuffle, ALERT_TempTooHigh ]
