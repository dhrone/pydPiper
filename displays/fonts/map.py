import logging

import size5x8


def map(fontpkgname):
	if fontpkgname == 'size5x8.player':
		return size5x8.player.fontpkg
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
	elif fontpkgname == 'default':
		return size5x8.player.fontpkg
	else:
		logging.debug("Font change requeste to unknown font {0}".fontpkgname)
		return [ ]
