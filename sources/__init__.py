__all__ = [ "musicdata_lms", "musicdata_mpd", "musicdata_spop", "musicdata_rune", "musicdata_volumio2" ]


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
