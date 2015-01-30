#!/usr/bin/python
# -*- coding: utf-8 -*-
import _common
import _database
import base64
import urllib
import sys
import xbmc
import xbmcgui
import xbmcaddon

addon = xbmcaddon.Addon()

class _Info:
	def __init__(self, s):
		args = urllib.unquote_plus(s).split(' , ')
		for x in args:
			try:
				(k, v) = x.split('=', 1)
				setattr(self, k, v.strip('"\''))
			except:
				pass

args = _Info(sys.argv[2][1:].replace('&', ' , '))

def delete_show():
	series_title, mode, submode, url = args.url.split('<join>')
	series_title = urllib.unquote_plus(series_title)
	command = 'delete from shows where tvdb_series_title = ? and mode = ? and submode = ?;'
	values = (series_title, mode, submode)
	_database.execute_command(command, values, commit = True)

def favor_show():
	series_title, mode, submode, url = args.url.split('<join>')
	series_title = urllib.unquote_plus(series_title)
	command = 'update shows set favor = 1 where series_title = ? and mode = ? and submode = ?;'
	values = (series_title, mode, submode)
	_database.execute_command(command, values, commit = True)

def unfavor_show():
	series_title, mode, submode, url = args.url.split('<join>')
	series_title = urllib.unquote_plus(series_title)
	command = 'update shows set favor = 0 where series_title = ? and mode = ? and submode = ?;'
	values = (series_title, mode, submode)
	_database.execute_command(command, values, commit = True)

def hide_show():
	series_title, mode, submode, url = args.url.split('<join>')
	series_title = urllib.unquote_plus(series_title)
	command = 'update shows set hide = 1 where tvdb_series_title = ? and mode = ? and submode = ?;'
	values = (series_title, mode, submode)
	_database.execute_command(command, values, commit = True)

def unhide_show():
	series_title, mode, submode, url = args.url.split('<join>')
	series_title = urllib.unquote_plus(series_title)
	command = 'update shows set hide = 0 where tvdb_series_title = ? and mode = ? and submode = ?;'
	values = (series_title, mode, submode)
	_database.execute_command(command, values, commit = True)
	_common.args.name = series_title
	_common.args.url = url
	refresh_menu(mode, submode, url)

def refresh_show():
	series_title, mode, submode, url = args.url.split('<join>')
	series_title = urllib.unquote_plus(series_title)
	_common.get_serie(series_title, mode, submode, url, forceRefresh = True)
	_common.args.name = series_title
	_common.args.url = url
	refresh_menu(mode, submode, url)

def refresh_db():
	_common.refresh_db()

def refresh_menu(mode, submode, url):
	exec 'import resources.lib.%s as sitemodule' % mode
	try:
		exec 'sitemodule.%s(\'%s\')' % (submode, url)
	except:
		exec 'sitemodule.%s()' % submode
	xbmc.executebuiltin('Container.Refresh')

def select_quality():
	show_title, season, episode, thumb, displayname, qmode, url = args.url.split('<join>')
	_common.args = _Info(url.split('?')[1].replace('&', ' , '))
	exec 'import resources.lib.%s as sitemodule' % _common.args.mode 
	exec 'resultlist = sitemodule.%s()' % qmode
	select = xbmcgui.Dialog()
	title = addon.getLocalizedString(39022)
	resultset = set(resultlist)
	resultlist = list(resultset)
	resultlist = sorted(resultlist)
	ret = select.select(title, [str(quality[0]) for quality in resultlist])
	bitrate = resultlist[ret][1]
	setattr(_common.args, 'name', base64.b64decode(displayname))
	setattr(_common.args, 'quality', bitrate)
	setattr(_common.args, 'thumb', thumb)
	setattr(_common.args, 'episode_number', int(episode))
	setattr(_common.args, 'season_number', int(season))
	setattr(_common.args, 'show_title', show_title)
	exec 'sitemodule.%s()' % _common.args.sitemode
