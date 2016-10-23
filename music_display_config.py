STARTUP_MSG = "Raspdac\nStarting"

HESITATION_TIME = 2.5 # Amount of time in seconds to hesistate before scrolling
ANIMATION_SMOOTHING = .15 # Amount of time in seconds before repainting display

COOLING_PERIOD = 15 # Default amount of time in seconds before an alert message can be redisplayed

# The Winstar display shipped with the RaspDac is capable of two lines of display
# when the 5x8 font is used.  This code assumes that is what you will be using.
# The display logic would need significant rework to support a different number
# of display lines!

DISPLAY_WIDTH = 16 # the character width of the display
DISPLAY_HEIGHT = 2 # the number of lines on the display

# This is where the log file will be written
LOGFILE='/var/log/RaspDacDisplay.log'
#LOGFILE='./log/RaspDacDisplay.log'

STATUSLOGFILE='/var/log/RaspDacDisplayStatus.log'
#STATUSLOGFILE='./log/RaspDacDisplayStatus.log'
STATUSLOGGING = False

# Adjust this setting to localize the time display to your region
TIMEZONE="US/Eastern"
TIME24HOUR=False
#TIMEZONE="Europe/Paris"

# Logging level
LOGLEVEL=logging.DEBUG
#LOGLEVEL=logging.INFO
#LOGLEVEL=logging.WARNING
#LOGLEVEL=logging.CRITICAL


#Configure which music services to monitor
# For Volumio and RuneAudio MPD and SPOP should be enabled and LMS disabled
# for Max2Play if you are using the Logitech Music Service, then LMS should be enabled
MPD_ENABLED = False
MPD_SERVER = "localhost"
MPD_PORT = 6600

SPOP_ENABLED = False
SPOP_SERVER = "localhost"
SPOP_PORT = 6602

LMS_ENABLED = False
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
RUNE_ENABLED = True
REDIS_SERVER = "localhost"
REDIS_PORT = 6379
REDIS_PASSWORD = ""
