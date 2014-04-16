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
	command = 'delete from shows where tvdb_series_title = ? and mode = ? and submode = ?;'
	values = (series_title, mode, submode)
	_database.execute_command(command, values, commit = True)

def favor_show():
	series_title, mode, submode, url = args.url.split('<join>')
	command = 'update shows set favor = 1 where tvdb_series_title = ? and mode = ? and submode = ?;'
	values = (series_title, mode, submode)
	print values
	_database.execute_command(command, values, commit = True)

def unfavor_show():
	series_title, mode, submode, url = args.url.split('<join>')
	command = 'update shows set favor = 0 where tvdb_series_title = ? and mode = ? and submode = ?;'
	values = (series_title, mode, submode)
	_database.execute_command(command, values, commit = True)

def hide_show():
	series_title, mode, submode, url = args.url.split('<join>')
	command = 'update shows set hide = 1 where tvdb_series_title = ? and mode = ? and submode = ?;'
	values = (series_title, mode, submode)
	_database.execute_command(command, values, commit = True)

def unhide_show():
	series_title, mode, submode, url = args.url.split('<join>')
	command = 'update shows set hide = 0 where tvdb_series_title = ? and mode = ? and submode = ?;'
	values = (series_title, mode, submode)
	_database.execute_command(command, values, commit = True)
	_common.args.name = series_title
	_common.args.url = url
	refresh_menu(mode, submode, url)

def refresh_show():
	series_title, mode, submode, url = args.url.split('<join>')
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
	exec 'list = sitemodule.%s()' % qmode
	select = xbmcgui.Dialog()
	title = xbmcaddon.Addon(id = _common.ADDONID).getLocalizedString(39022)
	list = sorted(list)
	ret = select.select(title, [str(quality[0]) for quality in list])
	bitrate = list[ret][1]
	setattr(_common.args, 'name', base64.b64decode(displayname))
	setattr(_common.args, 'quality', bitrate)
	setattr(_common.args, 'thumb', thumb)
	setattr(_common.args, 'episode_number', int(episode))
	setattr(_common.args, 'season_number', int(season))
	setattr(_common.args, 'show_title', show_title)
	exec 'sitemodule.%s()' % _common.args.sitemode
	