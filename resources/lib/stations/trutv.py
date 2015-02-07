#!/usr/bin/python
# -*- coding: utf-8 -*-
import simplejson
import sys
import urllib
import xbmcgui
import xbmcplugin
from .. import _connection
from .. import _common
from .. import _main_turner

pluginHandle = int(sys.argv[1])

SITE = 'trutv'
NAME = "truTV"
DESCRIPTION = "TruTV (stylized as truTV and, formerly Court TV), is an American cable and satellite television channel that is owned by the Turner Broadcasting System division of Time Warner. TruTV's programming originally consists of reality programming, legal-based news shows, and 'caught on video' reality programs (which TruTV refers to as 'actuality' television)."
SHOWS = 'http://feed.theplatform.com/f/ilYX/9A4duhdMkbgp?form=json&count=true'
CLIPS = 'http://feed.theplatform.com/f/ilYX/hjRdcrJ7AAi5?form=json&count=true'
FULLEPISODES = 'http://www.trutv.com/tveverywhere/services/getCollectionByContentId.json?sortBy=originalPremiereDate&id=%s'
EPISODE = 'http://www.trutv.com/tveverywhere/services/cvpXML.do?titleId=%s'
HLSPATH ='trutv'

def masterlist():
	master_db = []
	master_data = _connection.getURL(SHOWS)
	master_menu = simplejson.loads(master_data)['entries']
	for master_item in master_menu:
		master_name = master_item['title']
		try:
			collection_id = master_item['pl1$collectionID']
		except:
			collection_id = '0'
		season_url = master_item['link'] + '?form=json&count=true' + '#' + collection_id
		master_db.append((master_name, SITE, 'seasons', season_url))
	return master_db

def seasons(season_url = _common.args.url):
	clip_url = season_url.split('#')[0]
	episode_id = season_url.split('#')[1]
	clip_data = _connection.getURL(season_url)
	episode_data = _connection.getURL(FULLEPISODES % episode_id)
	try:
		season_menu = int(simplejson.loads(episode_data)['episodes']['totalItems'])
	except:
		season_menu = 0
	if season_menu > 0:
		_common.add_directory('Episodes',  SITE, 'episodes', FULLEPISODES % episode_id)
	try:
		season_menu = int(simplejson.loads(clip_data)['totalResults'])
	except:
		season_menu = 0
	if season_menu > 0:
		_common.add_directory('Clips',  SITE, 'episodes', clip_url)
	_common.set_view('seasons')

def episodes(episode_url = _common.args.url):
	episode_data = _connection.getURL(episode_url)
	if 'clips' in _common.args.name.lower():
		episode_menu = simplejson.loads(episode_data)['entries']
		for i, episode_item in enumerate(episode_menu):
			default_mediacontent = None
			for mediacontent in episode_item['media$content']:
				if (mediacontent['plfile$isDefault'] == True) and (mediacontent['plfile$format'] == 'MPEG4'):
					default_mediacontent = mediacontent
				elif (mediacontent['plfile$format'] == 'MPEG4'):
					mpeg4_mediacontent = mediacontent
			if default_mediacontent is None:
				default_mediacontent=mpeg4_mediacontent
			url = default_mediacontent['plfile$url']
			episode_duration = int(episode_item['media$content'][0]['plfile$duration'])
			episode_plot = episode_item['description']
			episode_airdate = _common.format_date(epoch = episode_item['pubDate']/1000)
			episode_name = episode_item['title']
			try:
				season_number = int(episode_item['pl' + str(i + 1) + '$season'][0])
			except:
				season_number = -1
			try:
				episode_number = int(episode_item['pl' + str(i + 1) + '$episode'][0])
			except:
				episode_number = -1
			try:
				episode_thumb = episode_item['plmedia$defaultThumbnailUrl']
			except:
				episode_thumb = None
			u = sys.argv[0]
			u += '?url="' + urllib.quote_plus(url) + '"'
			u += '&mode="' + SITE + '"'
			u += '&sitemode="play_video"'
			infoLabels={	'title' : episode_name,
							'durationinseconds' : episode_duration,
							'season' : season_number,
							'episode' : episode_number,
							'plot' : episode_plot,
							'premiered' : episode_airdate }
			_common.add_video(u, episode_name, episode_thumb, infoLabels = infoLabels)
	else:
		episode_menu = simplejson.loads(episode_data)['episodes']
		for episode_item in episode_menu['episode']:
			url = str(episode_item['id'])
			episode_duration = _common.format_seconds(episode_item['duration'])
			episode_plot = episode_item['description']
			episode_airdate = _common.format_date(episode_item['publishDate'].replace(' EDT', '').replace(' EST', ''), '%a %b %d %H:%M:%S %Y')
			episode_name = episode_item['title']
			try:
				season_number = int(episode_item['seasonNumber'])
			except:
				season_number = -1
			try:
				episode_number = int(episode_item['episodeNumber'][:1])
			except:
				episode_number = -1
			try:
				episode_thumb = episode_item['Thumbs']['Thumb'][-1]['content']
			except:
				episode_thumb = None
			u = sys.argv[0]
			u += '?url="' + urllib.quote_plus(url) + '"'
			u += '&mode="' + SITE + '"'
			u += '&sitemode="play_video"'
			infoLabels={	'title' : episode_name,
							'durationinseconds' : episode_duration,
							'season' : season_number,
							'episode' : episode_number,
							'plot' : episode_plot,
							'premiered' : episode_airdate }
			_common.add_video(u, episode_name, episode_thumb, infoLabels = infoLabels, quality_mode  = 'list_qualities')
	_common.set_view('episodes')

def play_video(video_url = _common.args.url):
	if 'mp4' in video_url:
		finalurl = video_url
		item = xbmcgui.ListItem(path = finalurl)
		xbmcplugin.setResolvedUrl(pluginHandle, True, item)
	else:
		_main_turner.play_video(SITE, EPISODE, HLSPATH)

def list_qualities():
	return _main_turner.list_qualities(SITE, EPISODE)
