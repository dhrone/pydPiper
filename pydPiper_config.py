import logging
import sys
if sys.version_info[0] < 3:
    import ConfigParser
    config = ConfigParser.RawConfigParser()
else:
    import configparser
    config = configparser.RawConfigParser()

config.read('pydPiper.cfg')

def safeget(config, section, option, default=None):
    return config.has_option(section, option) and config.get(section, option) or default

# Start-up mode
STARTUP_MSG_DURATION = float(safeget(config,'STARTUP', 'startup_msg_duration',0))

# Display Parameters
DISPLAY_DRIVER= safeget(config,'DISPLAY', 'display_driver')
DISPLAY_DEVICETYPE= safeget(config,'DISPLAY', 'display_devicetype')
DISPLAY_WIDTH = int(safeget(config,'DISPLAY', 'display_width',0)) # the  width of the display in pixels
DISPLAY_HEIGHT = int(safeget(config,'DISPLAY', 'display_height',0)) # the height of the display in pixels
DISPLAY_SIZE = (DISPLAY_WIDTH, DISPLAY_HEIGHT)
DISPLAY_PIN_RS = int(safeget(config,'DISPLAY', 'display_pin_rs',0))
DISPLAY_PIN_E = int(safeget(config,'DISPLAY', 'display_pin_e',0))
DISPLAY_PIN_D4 = int(safeget(config,'DISPLAY', 'display_pin_d4',0))
DISPLAY_PIN_D5 = int(safeget(config,'DISPLAY', 'display_pin_d5',0))
DISPLAY_PIN_D6 = int(safeget(config,'DISPLAY', 'display_pin_d6',0))
DISPLAY_PIN_D7 = int(safeget(config,'DISPLAY', 'display_pin_d7',0))
DISPLAY_PINS_DATA = [ DISPLAY_PIN_D4, DISPLAY_PIN_D5, DISPLAY_PIN_D6, DISPLAY_PIN_D7 ]
i2c_address = safeget(config,'DISPLAY', 'display_i2c_address','0')
DISPLAY_I2C_ADDRESS = int(i2c_address) if i2c_address and 'x' not in i2c_address else int(i2c_address,16)
DISPLAY_I2C_PORT = int(safeget(config,'DISPLAY', 'display_i2c_port',0))
DISPLAY_ENABLE_DURATION = float(safeget(config,'DISPLAY', 'display_enable_duration',0)) # in microseconds.  Decrease to increase performance.  Increase to improve display stability

# Page Parameters
PAGEFILE = safeget(config, 'DISPLAY', 'pagefile')
ANIMATION_SMOOTHING = float(safeget(config,'DISPLAY', 'animation_smoothing',0)) # Amount of time in seconds to wait before repainting display

# System Parameters
# This is where the log file will be written
LOGFILE=safeget(config,'SYSTEM','logfile')

# Logging level
LOGLEVEL={'debug': logging.DEBUG, 'info': logging.INFO, 'warning': logging.WARNING, 'critical': logging.CRITICAL }.get(safeget(config,'SYSTEM', 'loglevel'))

# Localization Parameters
# Adjust this setting to localize the time display to your region
TIMEZONE=safeget(config,'SYSTEM', 'timezone')
TIME24HOUR=bool(safeget(config, 'SYSTEM', 'time24hour',False))

# Adjust this setting to localize temperature displays
TEMPERATURE=safeget(config,'SYSTEM', 'temperature')

# Weather related variables
WEATHER_SERVICE = safeget(config,'SYSTEM', 'weather_service')
WEATHER_API = safeget(config,'SYSTEM', 'weather_api')
WEATHER_LOCATION = safeget(config,'SYSTEM', 'weather_location')


# Music Source Parameters
MUSIC_SERVICE = safeget(config, 'SOURCE', 'source_type')

# Used by Volumio V1 and Moode
MPD_SERVER = safeget(config, 'SOURCE', 'mpd_server')
MPD_PORT = safeget(config, 'SOURCE', 'mpd_port')
MPD_PASSWORD = safeget(config, 'SOURCE', 'mpd_password')

# Used by Volumio v1 and Moode
SPOP_SERVER = safeget(config, 'SOURCE', 'spop_server')
SPOP_PORT = safeget(config, 'SOURCE', 'spop_port')
SPOP_PASSWORD = safeget(config, 'SOURCE', 'spop_password')

# Used by Volumio v2
VOLUMIO_SERVER = safeget(config, 'SOURCE', 'volumio_server')
VOLUMIO_PORT = safeget(config, 'SOURCE', 'volumio_port')

# Used by RuneAudio
RUNE_SERVER = safeget(config, 'SOURCE', 'rune_server')
RUNE_PORT = safeget(config, 'SOURCE', 'rune_port')
RUNE_PASSWORD = safeget(config, 'SOURCE', 'rune_password')

# Used by Max2Play and piCorePlayer
LMS_SERVER = safeget(config, 'SOURCE', 'lms_server')
LMS_PORT = safeget(config, 'SOURCE', 'lms_port')
LMS_USER = safeget(config, 'SOURCE', 'lms_user')
LMS_PASSWORD = safeget(config, 'SOURCE', 'lms_password')
LMS_PLAYER = safeget(config, 'SOURCE', 'lms_player')

del (safeget)
