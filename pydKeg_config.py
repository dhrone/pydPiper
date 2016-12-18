import logging

# Messages
STARTUP_MSG = u"pydKeg\nStarting"
STARTUP_LOGMSG = u"pydKeg Starting"

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
LOGFILE=u'/var/log/pydKeg.log'
#LOGFILE=u'./log/pydKeg.log'

STATUSLOGFILE=u'/var/log/pydKeg-status.log'
#STATUSLOGFILE=u'./log/pydKeg-Status.log'
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
