__all__ = [ "player", "repeat_all", "repeat_once", "shuffle", "speaker", "volume" ]


try:
	import player
except ImportError:
	pass

try:
	import repeat_all
except ImportError:
	pass

try:
	import repeat_once
except ImportError:
	pass

try:
	import shuffle
except ImportError:
	pass

try:
	import speaker
except ImportError:
	pass

try:
	import volume
except ImportError:
	pass
