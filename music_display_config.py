import logging

STARTUP_MSG = "Music Display\nStarting"
STARTUP_LOGMSG = "Music Display Starting"

HESITATION_TIME = 2.5 # Amount of time in seconds to hesistate before scrolling
ANIMATION_SMOOTHING = .35 # Amount of time in seconds before repainting display
SCROLL_BLANK_WIDTH = 10 # Number of spaces to insert into string that is scrolling

COOLING_PERIOD = 15 # Default amount of time in seconds before an alert message can be redisplayed


# This is where the log file will be written
LOGFILE='/var/log/music-display.log'
#LOGFILE='./log/RaspDacDisplay.log'

STATUSLOGFILE='/var/log/music-display-status.log'
#STATUSLOGFILE='./log/RaspDacDisplayStatus.log'
STATUSLOGGING = False

# Adjust this setting to localize the time display to your region
TIMEZONE="US/Eastern"
TIME24HOUR=False
#TIMEZONE="Europe/Paris"

# Adjust this setting to localize temperature displays
TEMPERATURE='fahrenheit'
#TEMPERATURE='celsius'

# Logging level
LOGLEVEL=logging.DEBUG
#LOGLEVEL=logging.INFO
#LOGLEVEL=logging.WARNING
#LOGLEVEL=logging.CRITICAL


#Configure which music services to monitor
# For Volumio and RuneAudio MPD and SPOP should be enabled and LMS disabled
# for Max2Play if you are using the Logitech Music Service, then LMS should be enabled
MPD_SERVER = "localhost"
MPD_PORT = 6600
MPD_PASSWORD = ''

SPOP_SERVER = "localhost"
SPOP_PORT = 6602
SPOP_PASSWORD = ''

VOLUMIO_SERVER = 'localhost'
VOLUMIO_PORT = 3000

LMS_SERVER = "localhost"
LMS_PORT = 9090
LMS_USER = ""
LMS_PASSWORD = ""

# Set this to MAC address of the Player you want to monitor.
# THis should be the MAC of the RaspDac system if using Max2Play with SqueezePlayer
# Note: if you have another Logitech Media Server running in your network, it is entirely
#       possible that your player has decided to join it, instead of the LMS on Max2Play
#       To fix this, go to the SqueezeServer interface and change move the player to the
#       correct server.
LMS_PLAYER = "00:01:02:aa:bb:cc"


# If you are using RuneAudio you can pull the information from the REDIS database that RuneAudio maintains
RUNE_SERVER = "localhost"
RUNE_PORT = 6379
RUNE_PASSWORD = ""


# DISPLAY Settings
#DISPLAY_WIDTH = 16 # the character width of the display
#DISPLAY_HEIGHT = 2 # the number of lines on the display
DISPLAY_WIDTH = 20 # the character width of the display
DISPLAY_HEIGHT = 4 # the number of lines on the display
DISPLAY_PIN_RS = 7
DISPLAY_PIN_E =  8
DISPLAY_PINS_DATA = [ 25, 24, 23, 27 ] # Raspdac V3
#DISPLAY_PINS_DATA = [ 25, 24, 23, 15 ] # Raspdac V2

# WEATHER Settings
OWM_API = '52dfe63ba1fd89b1eda781a02d456842'
OWM_LOCATION = "Fairfax, VA"
