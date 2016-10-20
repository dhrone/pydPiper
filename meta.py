# meta - base class for collecting meta data from music sources

import abc
import time

class meta:
    __metaclass__ = abc.ABCMeta

    metadata = {
        'state':u"stop",
        'source':u""
        'artist':u"",
        'title':u"",
        'album':u"",
        'current':0,
        'remaining':u"",
        'duration':0,
        'position':u"",
        'volume':0,
        'playlist_display':u"",
        'playlist_position':0,
        'playlist_count':0,
        'bitrate':u"",
        'type':u""
        'current_time':u'00:00'
        'current_time_sec':u'00:00:00'
        'current_ip':u'1.2.3.4'
        'current_tempc':0
        'current_timef':0
        'disk_avail':0
        'disk_availp':0
    }

    connection_data = None
    connection_cmd = None
    connection_keepalive = None
    default_timeout = 30

	@abc.abstractmethod
    def status(block=True, timeout=self.default_timeout):
        # Return current metadata from the music source
        return

    def querysystem(frequency):
        # query for system variables such as time, temp, disk
        # frequency determines in seconds how often to update
