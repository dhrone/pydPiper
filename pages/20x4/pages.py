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
				'hidewhenemptyvars': [ "album" ],
				'lines': [
					{
						'name':"1",
						'segments': [
							{
								'start':0,
								'end':2,
								'format':"\x00\x01"
							},
							{
								'variables': [ "artist" ],
								'start':3,
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
								'start':3,
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
								'start':3,
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
								'format':"   {0}",
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
				'hidewhenpresentvars': [ "album" ],
				'lines': [
					{
						'name':"1",
						'segments': [
							{
								'start':0,
								'end':2,
								'format':"\x00\x01",
								'scroll':False
							},
							{
								'variables': [ "artist" ],
								'start':3,
								'end':20,
								'format':"{0}",
								'justification':"left",
								'scroll':True
							}
						]
					},
					{
						'name':"2",
						'segments': [
							{
								'start':0,
								'end':2,
								'format':"\x02\x03",
								'scroll':True
							},
							{
								'start':3,
								'end':20,
								'variables': [ "title" ],
								'format':"{0}",
								'scroll':True
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
								'variables': [ "playlist_display"],
								'start':0,
								'end':12,
								'format':"  {0}",
								'justification':"left",
								'scroll':False
							},
							{
								'variables': [ "elapsed_formatted" ],
								'start':12,
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
		'name':"TIMEBIG",
		'duration':8,
		'font':'size5x8.bigchars',
		'lines': [
		  {
			'name':"1",
			'variables': [ "time_formatted|bigchars+0+1", "time_ampm" ],
			'strftime':"%I:%M",
			'format':"{0} {1}",
			'justification':"left",
			'scroll':False
		  },
		  {
			'name':"2",
			'variables': [ "time_formatted|bigchars+1+1" ],
			'strftime':"%I:%M",
			'format':"{0}",
			'justification':"left",
			'scroll':False
		  },
		  {
			'name':"3",
			'format':"",
		  },
		  {
			'name':"4",
			'variables': [ "time_formatted" ],
			'strftime':"%B %-m, %Y",
			'format':"{0}",
			'justification':"left",
			'scroll':False
		  }
		]
	  },
	  {
		'name':"TEMPBIG",
		'duration':8,
		'font':'size5x8.bigchars',
		'lines': [
		  {
			'name':"1",
			'variables': [ "outside_temp_formatted|bigchars+0+1" ],
			'format':"{0}",
			'justification':"center",
			'scroll':False
		  },
		  {
			'name':"2",
			'variables': [ "outside_temp_formatted|bigchars+1+1" ],
			'format':"{0}",
			'justification':"center",
			'scroll':False
		  },
		  {
			'name':"3",
			'format':"",
		  },
		  {
			'name':"4",
			'variables': [ "outside_temp_max_formatted", "outside_temp_min_formatted" ],
			'format':"H: {0}   L: {1}",
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
							'format':"\x00\x01    Volume {0}",
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
			'font':'size5x8.bigplay',
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
							'format':"    \x00\x01   Play",
							'justification':"left",
							'scroll':False
						}
					]
				},
				{
					'name':"3",
					'segments': [
						{
							'format':"    \x02\x03",
							'justification':"left",
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
			'font':'size5x8.bigplay',
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
							'format':"    \x04\x05   Stop",
							'justification':"left",
							'scroll':False
						}
					]
				},
				{
					'name':"3",
					'segments': [
						{
							'format':"    \x06\x07",
							'justification':"left",
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
