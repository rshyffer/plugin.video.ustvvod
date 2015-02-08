#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import site
site.addsitedir(os.path.abspath(os.path.join(os.path.dirname(__file__),'resources','lib')))
import common
import contextmenu
import sys
import ustvpaths
import xbmcaddon
import xbmcplugin

addon = xbmcaddon.Addon()
pluginHandle = int(sys.argv[1])

print '\n\n\n start of USTV VoD plugin'

def modes():
	if sys.argv[2] == '':
		all_description = ''
		networks = common.get_networks()
		networks.sort(key = lambda x: x.SITE.replace('the', ''))
		for network in networks:
			if addon.getSetting(network.SITE) == 'true':
				if network.NAME.endswith(', The'):
					name = 'The ' + network.NAME.replace(', The', '')
				all_description += network.NAME + ', '
		count = 0
		common.add_directory(common.smart_utf8(addon.getLocalizedString(39000)), 'Favorlist', 'NoUrl', thumb = ustvpaths.FAVICON, count = count, description = common.smart_utf8(addon.getLocalizedString(39001)) + '\n' + all_description)
		count += 1
		common.add_directory(common.smart_utf8(addon.getLocalizedString(39002)), 'Masterlist', 'NoUrl', thumb = ustvpaths.ALLICON, count = count, description = common.smart_utf8(addon.getLocalizedString(39003)) + '\n' + all_description)
		count += 1
		for network in networks:
			network_name = network.NAME
			station_icon = os.path.join(ustvpaths.IMAGEPATH, network.SITE + '.png')
			if network_name.endswith(', The'):
				network_name = 'The ' + network_name.replace(', The', '')
			if addon.getSetting(network.SITE) == 'true':
				common.add_directory(network_name, network.SITE, 'rootlist', thumb = station_icon, fanart = ustvpaths.PLUGINFANART, description = network.DESCRIPTION, count = count)
			count += 1
		xbmcplugin.addSortMethod(pluginHandle, xbmcplugin.SORT_METHOD_PLAYLIST_ORDER)
		common.set_view()
		xbmcplugin.endOfDirectory(pluginHandle)
	elif common.args.mode == 'Masterlist':
		xbmcplugin.addSortMethod(pluginHandle, xbmcplugin.SORT_METHOD_LABEL)
		common.load_showlist()
		common.set_view('tvshows')
		xbmcplugin.endOfDirectory(pluginHandle)
	elif common.args.sitemode == 'rootlist':
		xbmcplugin.addSortMethod(pluginHandle, xbmcplugin.SORT_METHOD_LABEL)
		common.root_list(common.args.mode)
		xbmcplugin.endOfDirectory(pluginHandle)
	elif common.args.mode == 'Favorlist':   
		xbmcplugin.addSortMethod(pluginHandle, xbmcplugin.SORT_METHOD_LABEL)
		common.load_showlist(favored = 1)
		common.set_view('tvshows')
		xbmcplugin.endOfDirectory(pluginHandle)
	elif common.args.mode == 'contextmenu':
		getattr(contextmenu, common.args.sitemode)()
	elif common.args.mode == 'common':
		getattr(common, common.args.sitemode)()
	else:
		network = common.get_network(common.args.mode)
		if network:
			getattr(network, common.args.sitemode)()
			if 'episodes' in  common.args.sitemode and addon.getSetting('add_episode_identifier') == 'false':
				try:
					xbmcplugin.addSortMethod(pluginHandle, xbmcplugin.SORT_METHOD_DATEADDED)
				except:
					pass
				xbmcplugin.addSortMethod(pluginHandle, xbmcplugin.SORT_METHOD_EPISODE)
				xbmcplugin.addSortMethod(pluginHandle, xbmcplugin.SORT_METHOD_UNSORTED)
			if not common.args.sitemode.startswith('play'):
				xbmcplugin.endOfDirectory(pluginHandle)

try:
	modes()
except:
	sys.modules.clear()
