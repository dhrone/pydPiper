import sys
if sys.version_info[0] < 3:
    import ConfigParser
else:
    import configparser




if __name__ == u'__main__':

    import re

    CONFIG = [
        {
            'section_name': 'STARTUP',
            'section_title': 'Startup Configuration',
            'questions': [
                {
                    'variable': 'STARTUP_MSG_DURATION',
                    'prompt': 'Startup mode duration (in seconds)?',
                    'help': 'Sets how long in seconds the startup mode will last',
                    'default': '5'
                }
            ]
        },
        {
            'section_name': 'DISPLAY',
            'section_title': 'Display Configuration',
            'questions': [
                {
                    'prompt': 'Display type?',
                    'variable': 'DISPLAY_DRIVER',
                    'allowed': [ 'winstar_weg', 'hd44780', 'hd44780_i2c', 'hd44780_mcp23008', 'luma_i2c' ],
                    'help': 'Configures pydPiper for the display type you have installed',
                    'followup_questions': {
                        '^winstar_weg$|^hd44780$':
                            [
                                { 'prompt': 'Register select pin?', 'variable': 'DISPLAY_PIN_RS', 'default': '7', 'help': 'What GPIO pin is the display\'s register select line connected to' },
                                { 'prompt': 'Enable pin?', 'variable': 'DISPLAY_PIN_E', 'default': '8', 'help': 'What GPIO pin is the display\'s enable line connected to' },
                                { 'prompt': 'Data 4 pin?', 'variable': 'DISPLAY_PIN_D4', 'default': '25', 'help': 'What GPIO pin is the display\'s data 4 line connected to'  },
                                { 'prompt': 'Data 5 pin?', 'variable': 'DISPLAY_PIN_D5', 'default': '24', 'help': 'What GPIO pin is the display\'s data 5 line connected to'  },
                                { 'prompt': 'Data 6 pin?', 'variable': 'DISPLAY_PIN_D6', 'default': '23', 'help': 'What GPIO pin is the display\'s data 6 line connected to'  },
                                { 'prompt': 'Data 7 pin?', 'variable': 'DISPLAY_PIN_D7', 'default': '27', 'help': 'What GPIO pin is the display\'s data 7 line connected to'  }
                            ],
                        '^hd44780_i2c$|^hd44780_mcp23008$|^luma_i2c$':
                            [
                                { 'prompt': 'I2C Port?', 'variable': 'DISPLAY_I2C_PORT', 'default': '1', 'help': 'What I2C bus is the display connected to' },
                                { 'prompt': 'I2C Address?', 'variable': 'DISPLAY_I2C_ADDRESS', 'default': '0x3d', 'help': 'What is the display\'s I2C address' }
                            ],
                        '^luma_i2c$':
                            [
                                { 'prompt': 'Type of Display?', 'variable': 'DISPLAY_DEVICETYPE', 'allowed': ['ssd1306', 'sh1106', 'ssd1322', 'ssd1325', 'ssd1331'], 'default': 'ssd1306', 'help': 'What is the display device type' },
                                { 'prompt': 'Width of display (in pixels)?', 'variable': 'DISPLAY_WIDTH', 'default': '128', 'help': 'What is the horizontal resolution of the display in pixels' },
                                { 'prompt': 'Height of display (in pixels)?', 'variable': 'DISPLAY_HEIGHT', 'default': '64', 'help': 'What is the vertical resolution of the display in pixels' },
                            ],
                        '^winstar_weg$':
                            [
                                { 'prompt': 'Width of display (in pixels)?', 'variable': 'DISPLAY_WIDTH', 'default': '80', 'help': 'What is the horizontal resolution of the display in pixels.  Note: even if using the character version of the winstar, the value you enter should be in pixels.  For reference, a 16x2 character display has a horizontal resolution of 80' },
                                { 'prompt': 'Height of display (in pixels)?', 'variable': 'DISPLAY_HEIGHT', 'default': '16', 'help': 'What is the vertical resolution of the display in pixels.  Note: even if using the character version of the winstar, the value you enter should be in pixels.  For reference, a 16x2 character display has a vertical resolution of 16' },
                                {
                                    'prompt': 'Enable pulse duration (in microseconds)?',
                                    'variable': 'DISPLAY_ENABLE_DURATION',
                                    'default': '0.1',
                                    'help': 'Determines how long in microseconds the enable pulse should last.  This should be set as low as possible but setting it too low may cause display instability.  Recommended value is 1 ms for LCDs and 0.1 ms for OLEDs'
                                },                            ],
                        '^hd44780$|^hd44780_i2c$|^hd44780_mcp23008$':
                            [
                                { 'prompt': 'Width of display (in pixels)?', 'variable': 'DISPLAY_WIDTH', 'default': '80', 'help': 'What is the horizontal resolution of the display in pixels.  Note: even though the hd44780 is a character device, the value you enter should be in pixels.  For reference, a 16x2 character display has a horizontal resolution of 80' },
                                { 'prompt': 'Height of display (in pixels)?', 'variable': 'DISPLAY_HEIGHT', 'default': '16', 'help': 'What is the vertical resolution of the display in pixels.  Note: even though the hd44780 is a character device, the value you enter should be in pixels.  For reference, a 16x2 character display has a vertical resolution of 16' },
                                {
                                    'prompt': 'Enable pulse duration (in microseconds)?',
                                    'variable': 'DISPLAY_ENABLE_DURATION',
                                    'default': '1',
                                    'help': 'Determines how long in microseconds the enable pulse should last.  This should be set as low as possible but setting it too low may cause display instability.  Recommended value is 1 ms for LCDs and 0.1 ms for OLEDs'
                                },
                            ],
                    }
                },
                {
                    'prompt': 'Location of the pagefile?',
                    'variable': 'PAGEFILE',
                    'help': 'Sets which page file should be used to determine what and when to display content',
                    'default': 'pages_lcd_16x2.py'
                },
                {
                    'prompt': 'Animation Smoothing (in seconds)?',
                    'variable': 'ANIMATION_SMOOTHING',
                    'default': '0.15',
                    'help': 'Determines how often the display will attempt to update.  This is used to smooth the animation effects'
                }
            ]
        },
        {
            'section_name': 'SYSTEM',
            'section_title': 'System configuration',
            'questions': [
                {
                    'prompt': 'Location of log file?',
                    'variable': 'LOGFILE',
                    'default': '/var/log/pydPiper.log',
                    'help': 'Where should the log file be written to?'
                },
                {
                    'prompt': 'Logging Level?',
                    'variable': 'LOGLEVEL',
                    'allowed': ['debug', 'info', 'warning', 'error', 'critical'],
                    'casesensitive': False,
                    'default': 'info',
                    'help': 'Set logging level.  Normal logging for the system is info.  Setting to debug will provide much more information about how the system is operating which is useful for debugging'
                },
                {
                    'prompt': 'Time Zone?',
                    'variable': 'TIMEZONE',
                    'default': 'US/Eastern',
                    'help': 'Sets the time zone for the system.  Use ISO 3166 compliant values.  See https://en.wikipedia.org/wiki/List_of_tz_database_time_zones'
                },
                {
                    'prompt': '24-hour clock?',
                    'variable': 'TIME24HOUR',
                    'default': 'FALSE',
                    'casesensitive': False,
                    'allowed': ['true', 'false'],
                    'help': 'Determines whether the (deprecated) variable "current_time" is formatted as a 24 hour or 12 hour clock'
                },
                {
                    'prompt': 'Temperature Scale?',
                    'variable': 'TEMPERATURE',
                    'default': 'fahrenheit',
                    'casesensitive': False,
                    'allowed': ['fahrenheit', 'celsius'],
                    'help': 'Determines whether the temperature values will be shown in Fahrenheit or Celsius'
                },
                {
                    'prompt': 'Enable weather?',
                    'allowed': ['y','n','yes','no'],
                    'default': 'n',
                    'help': 'Do you want to enable the weather system?  Requires an API key from a supported weather provider.',
                    'casesensitive': False,
                    'followup_questions': {
                        '^y$|^yes$':
                            [
                                {
                                    'prompt': 'Weather service?',
                                    'variable': 'WEATHER_SERVICE',
                                    'default': 'accuweather',
                                    'allowed': ['accuweather', 'wunderground'],
                                    'casesensitive': False,
                                    'followup_questions': {
                                        '^accuweather$|^wunderground$':[
                                            {
                                                'prompt': 'API key?',
                                                'variable': 'WEATHER_API',
                                                'help': 'If using accuweather, an API can be requested from http://developer.accuweather.com.  Note: Weather Underground no longer supports free API keys.'
                                            },
                                            {
                                                'prompt': 'Location?',
                                                'variable': 'WEATHER_LOCATION',
                                                'help': 'You much provide a valid location.  If using Accuweather, these can be searched for using the API calls shown on https://developer.accuweather.com/accuweather-locations-api/apis'
                                            }
                                        ]
                                    }
                                },
                            ]
                    }
                }
            ]
        },
        {
            'section_name': 'SOURCE',
            'section_title': 'Music distribution',
            'questions': [
                {
                    'prompt': 'Name of distribution?',
                    'variable': 'SOURCE_TYPE',
                    'allowed': ['volumio', 'moode', 'rune', 'lms', 'mpd', 'spop'],
                    'casesensitive': False,
                    'mandatory': True,
                    'followup_questions': {
                        '^volumio$':
                            [
                                {
                                    'prompt': 'Server address?',
                                    'variable': 'VOLUMIO_SERVER',
                                    'default': 'localhost'
                                },
                                {
                                    'prompt': 'Port?',
                                    'variable': 'VOLUMIO_PORT',
                                    'default': '3000'
                                }
                            ],
                        '^rune$':
                            [
                                {
                                    'prompt': 'Server address?',
                                    'variable': 'RUNE_SERVER',
                                    'default': 'localhost'
                                },
                                {
                                    'prompt': 'Port?',
                                    'variable': 'RUNE_PORT',
                                    'default': '6379'
                                }
                            ],
                        '^lms$':
                            [
                                {
                                    'prompt': 'Server address?',
                                    'variable': 'LMS_SERVER',
                                    'default': 'localhost'
                                },
                                {
                                    'prompt': 'Port?',
                                    'variable': 'LMS_PORT',
                                    'default': '9090'
                                },
                                {
                                    'prompt': 'Username?',
                                    'variable': 'LMS_USER',
                                },
                                {
                                    'prompt': 'Password?',
                                    'variable': 'LMS_PASSWORD',
                                },
                                {
                                    'prompt': 'LMS Player MAC address?',
                                    'variable': 'LMS_PLAYER',
                                }
                            ],
                        '^mpd$|^moode$':
                            [
                                {
                                    'prompt': 'Server address?',
                                    'variable': 'MPD_SERVER',
                                    'default': 'localhost'
                                },
                                {
                                    'prompt': 'Port?',
                                    'variable': 'MPD_PORT',
                                    'default': '6600'
                                },
                                {
                                    'prompt': 'Password?',
                                    'variable': 'MPD_Password',
                                }
                            ],
                        '^spop$':
                            [
                                {
                                    'prompt': 'Server address?',
                                    'variable': 'SPOP_SERVER',
                                    'default': 'localhost'
                                },
                                {
                                    'prompt': 'Port?',
                                    'variable': 'SPOP_PORT',
                                    'default': '6602'
                                },
                                {
                                    'prompt': 'Password?',
                                    'variable': 'SPOP_Password',
                                }
                            ]
                    }
                }
            ]
        }
    ]


    def process_section(section, config):

        # if section does not exist, add it
        try:
            config.add_section(section['section_name'])
        except:
            pass
        print ('\n'+section['section_title'].upper()+'\n')

        process_questions(section['section_name'],section['questions'],config)

    def process_questions(section_name, questions, config):
        for question in questions:

            # If an previous value is available in the config file make it the default answer
            try:
                question['default'] = config.get(section_name, question['variable'])
            except:
                pass

            value = ask_question(question)
            if value and 'variable' in question:
                config.set(section_name, question['variable'], value)
            if 'followup_questions' in question:
                if sys.version_info[0] < 3:
                    for match, followup_questions in question['followup_questions'].iteritems():
                        if re.match(match,value):
                            process_questions(section_name, followup_questions, config)
                else:
                    for match, followup_questions in question['followup_questions'].items():
                        if re.match(match,value):
                            process_questions(section_name, followup_questions, config)

    def ask_question(question):

        prompt = question['prompt'] + ' [' + question['default'] + ']: ' if 'default' in question else question['prompt'] + ': '
        while True:
            if sys.version_info[0] < 3:
                value = raw_input(prompt)
            else:
                value = input(prompt)

            if value == '':
                value = question.get('default','')

            if 'casesensitive' in question and not question['casesensitive']:
                value = value.lower()
                if 'allowed' in question:
                    question['allowed'] = [allowed_value.lower() for allowed_value in question['allowed']]

            if value == '?' or value.lower() == 'help':
                if 'help' in question:
                    print (question['help'])
                if 'allowed' in question:
                    line = 'Possible values are: '
                    for possible in question['allowed']:
                        line += possible + ', '
                    line = line[:-2]
                    print (line)
                continue
            if 'allowed' in question:
                if value not in question['allowed'] and value:
                    print ('{0} is not a valid value'.format(value))
                    continue

            if 'mandatory' in question and question['mandatory'] is True and not value:
                print ('This value can not be blank.  Please enter a valid value')
                continue

            return value

    print ('\nCreating configuration file for pydPiper')
    print ('----------------------------------------')
    if sys.version_info[0] < 3:
        config = ConfigParser.RawConfigParser()
        serviceconfig = ConfigParser.RawConfigParser()
    else:
        config = configparser.RawConfigParser()
        serviceconfig = configparser.RawConfigParser()

    serviceconfig.optionxform = str

    config.read('pydPiper.cfg')

    for section in CONFIG:
        process_section(section,config)

    print ('\nUPDATING pydPiper.cfg')
    with open('pydPiper.cfg', 'w') as fp:
        config.write(fp)

    serviceconfig.add_section('Unit')
    serviceconfig.add_section('Service')
    serviceconfig.add_section('Install')
    serviceconfig.set('Unit', 'Description', 'pydPiper')

    serviceconfig.set('Service', 'Restart', 'always')
    serviceconfig.set('Install', 'WantedBy', 'multi-user.target')

    if config.get('SOURCE', 'source_type') == 'volumio':
        serviceconfig.set('Unit', 'Requires', 'docker.service')
        serviceconfig.set('Unit', 'After', 'volumio.service')
        serviceconfig.set('Service', 'ExecStart', '/usr/bin/docker run --network=host --privileged -v /var/log:/var/log:rw -v /home/volumio/pydPiper:/app:rw dhrone/pydpiper:v0.31-alpha python /app/pydPiper.py')
    elif config.get('SOURCE', 'source_type') == 'moode':
        serviceconfig.set('Unit', 'Requires', 'docker.service')
        serviceconfig.set('Unit', 'After', 'mpd.service docker.service')
        serviceconfig.set('Service', 'ExecStart', '/usr/bin/docker run --network=host --privileged -v /var/log:/var/log:rw -v /home/pi/pydPiper:/app:rw dhrone/pydpiper:v0.31-alpha python /app/pydPiper.py')
    elif config.get('SOURCE', 'source_type') == 'rune':
        serviceconfig.set('Unit', 'After', 'network.target redis.target')
        serviceconfig.set('Service', 'WorkingDirectory', '/root/pydPiper')
        serviceconfig.set('Service', 'ExecStart', '/root/.local/bin/pipenv run python2 pydPiper.py')

    if config.get('SOURCE', 'source_type') in ['volumio', 'moode', 'rune']:
        print ('Creating pydpiper.service file\n')
        with open('pydpiper.service', 'w') as fp:
            serviceconfig.write(fp)
