#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import re
import sys
import xbmc
import xbmcplugin

try:
	import xbmcaddon
	__has_addons__ = True
except:
	__has_addons__ = False
	pass

__plugin_handle__ = int(sys.argv[1])

if __has_addons__:
	__addon__ = xbmcaddon.Addon('plugin.video.ustvvod')

def get_os():
	try: xbmc_os = os.environ.get('OS')
	except: xbmc_os = 'unknown'
	return xbmc_os

def get_revision():
	rev_re = re.compile('r(\d+)')
	try: xbmc_version = xbmc.getInfoLabel('System.BuildVersion')
	except: xbmc_version = 'unknown'
	try:
		xbmc_rev = int(rev_re.search(xbmc_version).group(1))
		print '_addoncompat :: XBMC Revision: %s' % xbmc_rev
	except:
		print '_addoncompat :: XBMC Revision not available - Version String: %s' % xbmc_version
		xbmc_rev = 0
	return xbmc_rev

def get_setting(setting):
	setting_value = ''
	if __has_addons__:
		setting_value = __addon__.getSetting(setting)
	else:
		setting_value = xbmcplugin.getSetting(setting)
	return setting_value

def open_settings():
	if __has_addons__:
		__addon__.openSettings() 
	else:
		xbmcplugin.openSettings(sys.argv[ 0 ])
        
def get_path():
	pluginpath = xbmc.translatePath(__addon__.getAddonInfo('path')).decode('utf-8') 
	return pluginpath
