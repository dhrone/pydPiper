import logging

# Messages
STARTUP_LOGMSG = 'pydPiper starting'
STARTUP_MSG_DURATION = 5  # Sets how long that system state 'starting' will be True

# Display Parameters
#DISPLAY_DRIVER='ssd1306_i2c'
DISPLAY_DRIVER='winstar_weg'
#DISPLAY_DRIVER='hd44780'

DISPLAY_WIDTH = 80 # the  width of the display in pixels
DISPLAY_HEIGHT = 16 # the height of the display in pixels
DISPLAY_SIZE = (DISPLAY_WIDTH, DISPLAY_HEIGHT)
DISPLAY_PIN_RS = 7
DISPLAY_PIN_E =  8
DISPLAY_PINS_DATA = [ 25, 24, 23, 27 ] # Raspdac V3
#DISPLAY_PINS_DATA = [ 25, 24, 23, 15 ] # Raspdac V2
#DISPLAY_I2C_ADDRESS = 0x3d
DISPLAY_I2C_ADDRESS = 0x27
DISPLAY_I2C_PORT = 1

# Page Parameters
ANIMATION_SMOOTHING = .015 # Amount of time in seconds to wait before repainting display

# System Parameters
# This is where the log file will be written
LOGFILE=u'/var/log/pydPiper.log'
#LOGFILE=u'./log/pydPiper.log'

# Logging level
#LOGLEVEL=logging.DEBUG
LOGLEVEL=logging.INFO
#LOGLEVEL=logging.WARNING
#LOGLEVEL=logging.CRITICAL

# Localization Parameters
# Adjust this setting to localize the time display to your region
TIMEZONE=u"US/Eastern"
TIME24HOUR=False
#TIMEZONE=u"Europe/Paris"
# Adjust this setting to localize temperature displays
TEMPERATURE=u'fahrenheit'
#TEMPERATURE=u'celsius'

# WEATHER Parameters
# You must get your own API key from http://openweathermap.org/appid
OWM_API = u''
# NOVA Metro area.  Replace with your location.
#OWM_LAT = 38.86
#OWM_LON = -77.34
# NY Metro area.  Replace with your location.
#OWM_LAT = 40.72
#OWM_LON = -74.07
# Paris Metro area.  Replace with your location.
OWM_LAT = 48.865
OWM_LON = 2.352

WUNDER_API = ''
WUNDER_LOCATION = '07302'


# Music Source Parameters

# Used by Volumio V1 and Moode
MPD_SERVER = u"localhost"
MPD_PORT = 6600
MPD_PASSWORD = ''

# Used by Volumio v1 and Moode
SPOP_SERVER = u"localhost"
SPOP_PORT = 6602
SPOP_PASSWORD = ''

# Used by Volumio v2
VOLUMIO_SERVER = u'localhost'
VOLUMIO_PORT = 3000

# Used by RuneAudio
RUNE_SERVER = u"localhost"
RUNE_PORT = 6379
RUNE_PASSWORD = u""

# Used by Max2Play and piCorePlayer
LMS_SERVER = u"localhost"
LMS_PORT = 9090
LMS_USER = u""
LMS_PASSWORD = u""

# Set this to MAC address of the Player you want to monitor.
# THis should be the MAC of the RaspDac system if using Max2Play with SqueezePlayer
# Note: if you have another Logitech Media Server running in your network, it is entirely
#       possible that your player has decided to join it, instead of the LMS on Max2Play
#       To fix this, go to the SqueezeServer interface and change move the player to the
#       correct server.
LMS_PLAYER = u"00:01:02:aa:bb:cc"
