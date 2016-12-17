import logging


# Messages
STARTUP_MSG = u"pydPiper\nStarting"
STARTUP_LOGMSG = u"pydPiper Starting"

# Display Parameters
DISPLAY_DRIVER='lcd_display_driver_winstar_ws0010_graphics_mode'
DISPLAY_WIDTH = 100 # the  width of the display
DISPLAY_HEIGHT = 16 # the height of the display
DISPLAY_SIZE = (DISPLAY_WIDTH, DISPLAY_HEIGHT)
#DISPLAY_WIDTH = 20 # the character width of the display
#DISPLAY_HEIGHT = 4 # the number of lines on the display
DISPLAY_PIN_RS = 7
DISPLAY_PIN_E =  8
DISPLAY_PINS_DATA = [ 25, 24, 23, 27 ] # Raspdac V3
#DISPLAY_PINS_DATA = [ 25, 24, 23, 15 ] # Raspdac V2

# Page Parameters
SCROLL_BLANK_WIDTH = 10 # Number of spaces to insert into string that is scrolling
COOLING_PERIOD = 15 # Default amount of time in seconds before an alert message can be redisplayed
HESITATION_TIME = 2.5 # Amount of time in seconds to hesistate before scrolling
ANIMATION_SMOOTHING = .15 # Amount of time in seconds before repainting display

# System Parameters
# This is where the log file will be written
LOGFILE=u'/var/log/pydPiper.log'
#LOGFILE=u'./log/pydPiper.log'

STATUSLOGFILE=u'/var/log/pydPiper-status.log'
#STATUSLOGFILE=u'./log/pydPiper-Status.log'
STATUSLOGGING = False

# Logging level
LOGLEVEL=logging.DEBUG
#LOGLEVEL=logging.INFO
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
OWM_API = u'52dfe63ba1fd89b1eda781a02d456842'
# NOVA Metro area.  Replace with your location.
OWM_LAT = 38.86
OWM_LON = -77.34

# NY Metro area.  Replace with your location.
#OWM_LAT = 40.72
#OWM_LON = -74.07



# Music Source Parameters

# For Volumio and RuneAudio MPD and SPOP should be enabled and LMS disabled
# for Max2Play if you are using the Logitech Music Service, then LMS should be enabled
MPD_SERVER = u"localhost"
MPD_PORT = 6600
MPD_PASSWORD = ''

SPOP_SERVER = u"localhost"
SPOP_PORT = 6602
SPOP_PASSWORD = ''

VOLUMIO_SERVER = u'localhost'
VOLUMIO_PORT = 3000

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
#LMS_PLAYER = u"00:01:02:aa:bb:cc"


# If you are using RuneAudio you can pull the information from the REDIS database that RuneAudio maintains
RUNE_SERVER = u"localhost"
RUNE_PORT = 6379
RUNE_PASSWORD = u""
