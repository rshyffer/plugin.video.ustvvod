#!/usr/bin/python
# -*- coding: utf-8 -*-
import resources.lib._addoncompat as _addoncompat
import resources.lib._common as _common
import resources.lib._contextmenu as _contextmenu
import operator
import os
import sys
import xbmcaddon
import xbmcplugin

pluginHandle = int(sys.argv[1])

__plugin__ = 'USTV VoD'
__authors__ = 'BlueCop'
__credits__ = 'moneymaker, slices, zero'
__version__ = '1.0.7'

print '\n\n\n start of USTV VoD plugin'

def modes():
	if sys.argv[2] == '':
		all_description = ''
		networks = _common.get_networks()
		networks.sort(key = lambda x: x.SITE.replace('the', ''))
		for network in networks:
			if _addoncompat.get_setting(network.SITE) == 'true':
				if network.NAME.endswith(', The'):
					name = 'The ' +network.NAME.replace(', The', '')
				all_description += network.NAME + ', '
		count = 0
		_common.add_directory(_common.smart_utf8(xbmcaddon.Addon(id = _common.ADDONID).getLocalizedString(39000)), 'Favorlist', 'NoUrl', thumb = _common.FAVICON, count = count, description = _common.smart_utf8(xbmcaddon.Addon(id = _common.ADDONID).getLocalizedString(39001)) + '\n' + all_description)
		count += 1
		_common.add_directory(_common.smart_utf8(xbmcaddon.Addon(id = _common.ADDONID).getLocalizedString(39002)), 'Masterlist', 'NoUrl', thumb = _common.ALLICON, count = count, description = _common.smart_utf8(xbmcaddon.Addon(id = _common.ADDONID).getLocalizedString(39003)) + '\n' + all_description)
		count += 1
		for network in networks:
			network_name = network.NAME
			station_icon = os.path.join(_common.IMAGEPATH, network.SITE + '.png')
			if network_name.endswith(', The'):
				network_name = 'The ' + network_name.replace(', The', '')
			if _addoncompat.get_setting(network.SITE) == 'true':
				_common.add_directory(network_name, network.SITE, 'rootlist', thumb = station_icon, fanart = _common.PLUGINFANART, description = network.DESCRIPTION, count = count)
			count += 1
		xbmcplugin.addSortMethod(pluginHandle, xbmcplugin.SORT_METHOD_PLAYLIST_ORDER)
		_common.set_view()
		xbmcplugin.endOfDirectory(pluginHandle)
	elif _common.args.mode == 'Masterlist':
		xbmcplugin.addSortMethod(pluginHandle, xbmcplugin.SORT_METHOD_LABEL)
		_common.load_showlist()
		_common.set_view('tvshows')
		xbmcplugin.endOfDirectory(pluginHandle)
	elif _common.args.sitemode == 'rootlist':
		xbmcplugin.addSortMethod(pluginHandle, xbmcplugin.SORT_METHOD_LABEL)
		_common.root_list(_common.args.mode)
		xbmcplugin.endOfDirectory(pluginHandle)
	elif _common.args.mode == 'Favorlist':   
		xbmcplugin.addSortMethod(pluginHandle, xbmcplugin.SORT_METHOD_LABEL)
		_common.load_showlist(favored = 1)
		_common.set_view('tvshows')
		xbmcplugin.endOfDirectory(pluginHandle)
	elif _common.args.mode == '_contextmenu':
		getattr(_contextmenu, _common.args.sitemode)()
	elif _common.args.mode == '_common':
		getattr(_common, _common.args.sitemode)()
	else:
		network = _common.get_network(_common.args.mode)
		if network:
			getattr(network, _common.args.sitemode)()
			if not _common.args.sitemode.startswith('play'):
				xbmcplugin.endOfDirectory(pluginHandle)
modes()
sys.modules.clear()
