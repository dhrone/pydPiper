import logging

import size5x8


def map(fontpkgname):
	if fontpkgname == 'size5x8.player':
		return size5x8.player.fontpkg
	elif fontpkgname == 'size5x8.playing':
		return size5x8.playing.fontpkg
	elif fontpkgname == 'size5x8.repeat_all':
		return size5x8.repeat_all.fontpkg
	elif fontpkgname == 'size5x8.repeat_once':
		return size5x8.repeat_once.fontpkg
	elif fontpkgname == 'size5x8.shuffle':
		return size5x8.shuffle.fontpkg
	elif fontpkgname == 'size5x8.speaker':
		return size5x8.speaker.fontpkg
	elif fontpkgname == 'size5x8.volume':
		return size5x8.volume.fontpkg
	elif fontpkgname == 'size5x8.system':
		return size5x8.system.fontpkg
	elif fontpkgname == 'size5x8.bigclock':
		return size5x8.bigclock.fontpkg
	elif fontpkgname == 'size5x8.bigchars':
		return size5x8.bigchars.fontpkg
	elif fontpkgname == 'size5x8.bigplay':
		return size5x8.bigplay.fontpkg
	elif fontpkgname == 'default':
		return size5x8.player.fontpkg
	else:
		logging.debug("Font change requeste to unknown font {0}".format(fontpkgname))
		return [ ]
