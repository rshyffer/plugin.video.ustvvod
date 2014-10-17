#!/usr/bin/python
# -*- coding: utf-8 -*-
import _common
import _connection
import _main_viacom
import simplejson
import sys
import re
import urllib

pluginHandle = int(sys.argv[1])

SITE = 'mtv'
NAME = 'MTV'
DESCRIPTION = "MTV is Music Television. It is the music authority where young adults turn to find out what's happening and what's next in music and popular culture. MTV reaches 412 million households worldwide, and is the #1 Media Brand in the world. Only MTV can offer the consistently fresh, honest, groundbreaking, fun and inclusive youth-oriented programming found nowhere else in the world. MTV is a network that transcends all the clutter, reaching out beyond barriers to everyone who's got eyes, ears and a television set."
BASE = 'http://www.mtv.com'
TYPES = [('fullEpisodes' , 'Full Episodes'), ('bonusClips,afterShowsClips,recapsClips,sneakPeeksClips,dailies' , 'Specials')]
SHOWS = 'http://api.mtv.com/api/vLaNWq0xlbQB/promolist/10393491.json'

def masterlist(master_url = SHOWS):
	master_db = []
	master_data = _connection.getURL(SHOWS, header = {'X-Forwarded-For' : '12.13.14.15'})
	showdata = simplejson.loads(master_data)
	for data in showdata['promoList']['promos']:
		data = data['promo']['associatedContent']['series']
		master_name = data['title']
		seriesId = data['seriesId']
		if seriesId is not None:
			master_db.append((master_name, SITE, 'seasons', seriesId))
		else: pass
	return master_db

def seasons(id = _common.args.url):
	for type in TYPES:
		url = 'http://api.mtv.com/api/vLaNWq0xlbQB/series/' + id + '/playlists.json?page=0&pageSize=500&type=' + type[0]
		data = _connection.getURL(url, header = {'X-Forwarded-For' : '12.13.14.15'})
		try:
			count = len(simplejson.loads(data)['series']['playlists'])
		except:
			count = 0
		if count > 0:
			_common.add_directory(type[1],  SITE, 'videos', url)
	_common.set_view('seasons')

def videos(episode_url = _common.args.url):
	episode_data = _connection.getURL(episode_url, header = {'X-Forwarded-For' : '12.13.14.15'})
	episodes = simplejson.loads(episode_data)
	for episode in episodes['series']['playlists']:
		show_name = episodes['series']['title']
		episode = episode['playlist']
		episode_name = episode['headline'].split('|')[-1].strip()
		episode_info = re.compile('s([0-9]).e?([0-9]{0,2}).*').findall(episode['title'])
		try:
			episode_season, episode_number = episode_info[0]
		except:
			episode_season = episode_info
			episode_number = -1
		url = episode['mgid']
		try:
			episode_plot = episode['subhead']
		except:
			episode_plot = ''
		episode_thumb = episode['image']
		episode_duration = _common.format_seconds(episode['duration']['timecode'])
		u = sys.argv[0]
		u += '?url="' + urllib.quote_plus(url) + '"'
		u += '&mode="' + SITE + '"'
		u += '&sitemode="play"'
		infoLabels = {	'title' : episode_name,
						'plot' : episode_plot,
						'durationinseconds' : episode_duration,
						'tvshowtitle' : show_name,
						'season' : episode_season,
						'episode' : episode_number}
		_common.add_video(u, episode_name, episode_thumb, infoLabels = infoLabels, quality_mode  = 'list_qualities')
	_common.set_view('episodes')

def play(video_url = _common.args.url):
	_main_viacom.play_video(BASE, video_url)

def list_qualities(video_url = _common.args.url):
	return _main_viacom.list_qualities(BASE, video_url)
