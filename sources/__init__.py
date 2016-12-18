__all__ = [ u"musicdata_lms", u"musicdata_mpd", u"musicdata_spop", u"musicdata_rune", u"musicdata_volumio2", u"keydata" ]


try:
	import musicdata_lms
except ImportError:
	pass

try:
	import musicdata_mpd
except ImportError:
	pass

try:
	import musicdata_spop
except ImportError:
	pass

try:
	import musicdata_rune
except ImportError:
	pass

try:
	import musicdata_volumio2
except ImportError:
	pass

try:
	import musicdata
except ImportError:
	pass

try:
	import kegdata
except ImportError:
	pass
