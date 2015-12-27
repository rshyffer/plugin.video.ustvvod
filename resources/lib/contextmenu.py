#!/usr/bin/python
# -*- coding: utf-8 -*-
import common
import database
import base64
import urllib
import os
import plistlib
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
	database.execute_command(command, values, commit = True)

def favor_show():
	series_title, mode, submode, url = args.url.split('<join>')
	series_title = urllib.unquote_plus(series_title)
	command = 'update shows set favor = 1 where series_title = ? and mode = ? and submode = ?;'
	values = (series_title, mode, submode)
	database.execute_command(command, values, commit = True)

def unfavor_show():
	series_title, mode, submode, url = args.url.split('<join>')
	series_title = urllib.unquote_plus(series_title)
	command = 'update shows set favor = 0 where series_title = ? and mode = ? and submode = ?;'
	values = (series_title, mode, submode)
	database.execute_command(command, values, commit = True)

def hide_show():
	series_title, mode, submode, url = args.url.split('<join>')
	series_title = urllib.unquote_plus(series_title)
	command = 'update shows set hide = 1 where tvdb_series_title = ? and mode = ? and submode = ?;'
	values = (series_title, mode, submode)
	database.execute_command(command, values, commit = True)

def unhide_show():
	series_title, mode, submode, url = args.url.split('<join>')
	series_title = urllib.unquote_plus(series_title)
	command = 'update shows set hide = 0 where tvdb_series_title = ? and mode = ? and submode = ?;'
	values = (series_title, mode, submode)
	database.execute_command(command, values, commit = True)
	common.args.name = series_title
	common.args.url = url
	refresh_menu(mode, submode, url)

def refresh_show():
	series_title, mode, submode, url = args.url.split('<join>')
	series_title = urllib.unquote_plus(series_title)
	common.get_serie(series_title, mode, submode, url, forceRefresh = True)
	common.args.name = series_title
	common.args.url = url
	refresh_menu(mode, submode, url)

def refresh_db():
	common.refresh_db()
	
def export_fav():
	print 'fav'
	dialog = xbmcgui.Dialog()
	print 'd'
	try:
		r = dialog.browse(3, 'Folder', 'files')
		print r
		path = os.path.join(r, 'favorites.txt')
		shows = common.fetch_showlist(1)
		sd = {}
		for show in shows:
			sd[show[0]] = show
		import json
		with open(path, 'w') as outfile:
			json.dump(sd, outfile)
		
	except Exception,e:
		print e
		
def import_fav():
	print 'fav'
	dialog = xbmcgui.Dialog()
	print 'd'
	try:
		r = dialog.browse(3, 'Folder', 'files')
		print r
		path = os.path.join(r, 'favorites.txt')
		shows = common.fetch_showlist(1)
		sd = {}
		for show in shows:
			sd[show[0]] = show
		import json
		print r
		json_data=open(path).read()
		#print json_data
		jd = json.loads(json_data)
		for title in jd:
			show = jd[title]
			series_title = show[0]
			mode = show[1]
			submode = show[2]
			series_title = urllib.unquote_plus(series_title)
			command = 'update shows set favor = 1 where series_title = ? and mode = ? and submode = ?;'
			values = (series_title, mode, submode)
			print values
			database.execute_command(command, values, commit = True)
		
	except Exception,e:
		print e
		
def del_fav():
	print 'del fav'
	dialog = xbmcgui.Dialog()
	try:
		r = dialog.yesno('Delete All Favorites' ,'Are you sure?')
		if r:
			print 'Deleting favorites'
			common.del_favorites()
		# path = os.path.join(r, 'favorites.txt')
		# shows = common.fetch_showlist(1)
		# sd = {}
		# for show in shows:
			# sd[show[0]] = show
		# import json
		# with open(path, 'w') as outfile:
			# json.dump(sd, outfile)
		
	except Exception,e:
		print e

def refresh_menu(mode, submode, url):
	exec 'import resources.lib.%s as sitemodule' % mode
	try:
		exec 'sitemodule.%s(\'%s\')' % (submode, url)
	except:
		exec 'sitemodule.%s()' % submode
	xbmc.executebuiltin('Container.Refresh')

def select_quality():
	show_title, season, episode, thumb, displayname, qmode, url = args.url.split('<join>')
	common.args = _Info(url.split('?')[1].replace('&', ' , '))
	network = common.get_network(common.args.mode)
	resultlist = getattr(network, qmode)()
	select = xbmcgui.Dialog()
	title = addon.getLocalizedString(39022)
	resultset = set(resultlist)
	resultlist = list(resultset)
	resultlist = sorted(resultlist)
	ret = select.select(title, [str(quality[0]) for quality in resultlist])
	bitrate = resultlist[ret][1]
	setattr(common.args, 'name', base64.b64decode(displayname))
	setattr(common.args, 'quality', bitrate)
	setattr(common.args, 'thumb', thumb)
	setattr(common.args, 'episode_number', int(episode))
	setattr(common.args, 'season_number', int(season))
	setattr(common.args, 'show_title', show_title)
	getattr(network, common.args.sitemode)()
	
def queue():
	playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
	show_title, season, episode, thumb, displayname, qmode, url = args.url.split('<join>')
	name =  base64.b64decode(displayname)
	item = xbmcgui.ListItem(name, path = url)
	try:
		item.setThumbnailImage(thumb)
	except:
		pass
	try:
		item.setInfo('Video', {	'title' : name,
						'season' : season,
						'episode' : episode,
						'TVShowTitle' : show_title})
	except:
		pass
	playlist.add(url, item)
	xbmc.executebuiltin('XBMC.Notification(%s, %s, 5000, %s)' % ("Queued", name, thumb))
	
def settings():
	addon.openSettings()
