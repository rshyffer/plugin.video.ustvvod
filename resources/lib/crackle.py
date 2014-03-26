#!/usr/bin/python
# -*- coding: utf-8 -*-
import _addoncompat
import _common
import _connection
import simplejson
import sys
import re
import urllib
import xbmc
import xbmcgui
import xbmcplugin
from bs4 import BeautifulSoup, SoupStrainer

pluginHandle = int(sys.argv[1])

SITE = 'crackle'
NAME = 'Crackle'
DESCRIPTION = "Crackle, Inc. is a multi-platform video entertainment network and studio that distributes full length, uncut, movies, TV shows and original programming in our users favorite genres ï¿½ like comedy, action, crime, horror, Sci-Fi, and thriller. Crackles channels and shows reach a global audience across the Internet, in the living room, and on devices including a broad range of Sony electronics."
SHOWS = 'http://api.crackle.com/Service.svc/browse/shows/all/all/alpha/us?format=json'
MOVIES = 'http://api.crackle.com/Service.svc/browse/movies/all/all/alpha/us?format=json'
BASE  = 'http://media-us-am.crackle.com/'
FULLEPISODES = 'http://api.crackle.com/Service.svc/channel/%s/folders/us?format=json'
EPISODE = 'http://www.crackle.com/app/vidwallcache.aspx?flags=-1&o=12&fpl=%s&fm=%s&partner=20'
QUALITIES = [(360, '360p.mp4'), (480, '480p_1mbps.mp4')]

def masterlist():
	master_db = []
	master_dict = {}
	master_url = SHOWS
	master_data = _connection.getURL(master_url)
	master_menu = simplejson.loads(master_data)['Entries']
	for master_item in master_menu:
		master_name = master_item['Title']
		season_url = FULLEPISODES % master_item['ID']
		master_dict[master_name] = season_url
		master_db.append((master_name, SITE, 'seasons', season_url))
	master_db.append(('Crackle Movies', SITE, 'movielist', MOVIES))
	return master_db

def rootlist():	
	root_dict = {}
	root_url = SHOWS
	root_data = _connection.getURL(root_url)
	root_menu = simplejson.loads(root_data)['Entries']
	for root_item in root_menu:
		root_name = root_item['Title']
		season_url = FULLEPISODES % root_item['ID']
		_common.add_show(root_name, SITE, 'seasons', season_url)
	_common.add_show('Crackle Movies', SITE, 'movielist', MOVIES)
	_common.set_view('tvshows')

def movielist(url = _common.args.url):	
	root_dict = {}
	root_url = url
	root_data = _connection.getURL(root_url)
	root_menu = simplejson.loads(root_data)['Entries']
	for root_item in root_menu:
		root_name = root_item['Title']
		season_url = FULLEPISODES % root_item['ID']
		_common.add_show(root_name, SITE, 'episodes', season_url)
	_common.set_view('tvshows')
	
def seasons(season_url = _common.args.url):
	seasons = []
	season_data = _connection.getURL(season_url)
	media_list = simplejson.loads(season_data)['FolderList'][0]['PlaylistList'][0]['MediaList']
	for media in media_list:
		season_number = media['Season']
		if season_number not in seasons:
			season_title = 'Season %s' % season_number
			seasons.append(season_number)
			_common.add_directory(season_title,  SITE, 'episodes', season_url + '#' + season_number)
	_common.set_view('seasons')

def episodes(episode_url = _common.args.url):
	try:
		season_number = episode_url.split('#')[1]
	except:
		season_number = -1
	episode_url = episode_url.split('#')[0]
	episode_data = _connection.getURL(episode_url)
	episode_menu = simplejson.loads(episode_data)['FolderList'][0]['PlaylistList'][0]
	for episode_item in episode_menu['MediaList']:
		if episode_item['Season'] == season_number or season_number == -1:
			''' THX to foreverguest '''
			path_pattern = re.compile('http:\\/\\/.+?\/(.+?)_[a-zA-Z0-9]+')
			pattern_url = episode_item['Thumbnail_Wide']
			path = path_pattern.findall(pattern_url)
			if not path and episode_item['ClosedCaptionFiles']:
				path = path_pattern.findall(episode_item['ClosedCaptionFiles'][0]['Path'])
			if not path:
				continue
			video_url = BASE + path[0] + '_'
			episode_duration = int(episode_item['DurationInSeconds'])
			episode_name = episode_item['Title']
			episode_plot = episode_item['Description']
			try:
				episode_airdate = _common.format_date(episode_item['ReleaseDate'], '%m/%d/%Y')
			except:
				episode_airdate = None
			try:
				episode_number = int(episode_item['Episode'])
			except:
				episode_number = -1
			try:
				episode_thumb = episode_item['Thumbnail_854x480']
			except:
				episode_thumb = None
			try:
				episode_caption = episode_item['ClosedCaptionFiles'][0]['Path']
			except:
				episode_caption = ''
			episode_MPAA = episode_item['Rating']
			episode_genre = episode_item['Genre']
			episode_showtitle = episode_item['ParentChannelName']
			video_url = video_url + '#' + episode_caption
			u = sys.argv[0]
			u += '?url="' + urllib.quote_plus(video_url) + '"'
			u += '&mode="' + SITE + '"'
			u += '&sitemode="play_video"'
			infoLabels={	'title' : episode_name,
							'durationinseconds' : episode_duration,
							'season' : season_number,
							'episode' : episode_number,
							'plot' : episode_plot,
							'premiered' : episode_airdate,
							'MPAA' : episode_MPAA,
							'Genre' : episode_genre,
							'TVShowTitle' : episode_showtitle}
			_common.add_video(u, episode_name, episode_thumb, infoLabels = infoLabels, quality_mode = 'list_qualities')
	_common.set_view('episodes')

def list_qualities(video_url = _common.args.url):
	return QUALITIES
		
def play_video(video_url = _common.args.url):
	try:
		qbitrate = _common.args.quality
	except:
		qbitrate = None
	hbitrate = -1
	hpath = None
	sbitrate = int(_addoncompat.get_setting('quality'))
	closedcaption = video_url.split('#')[1]
	video_url = video_url.split('#')[0]
	if qbitrate is None:
		lbitrate = -1
		for quality_index in QUALITIES:
			bitrate = int(quality_index[0])
			if bitrate < lbitrate or lbitrate == -1:
				lbitrate = bitrate
				lpath = quality_index[1]	
			if bitrate > hbitrate and bitrate <= sbitrate:
				hbitrate = bitrate
				hpath = quality_index[1]	
		if hpath is None:
			hpath = lpath
	else:
		hpath = qbitrate	
	if (_addoncompat.get_setting('enablesubtitles') == 'true') and (closedcaption != ''):
			convert_subtitles(closedcaption)
	finalurl = video_url + hpath
	item = xbmcgui.ListItem(path = finalurl)
	if qbitrate is not None:
		item.setThumbnailImage(_common.args.thumb)
		item.setInfo('Video', {	'title' : _common.args.name,
								'season' : _common.args.season_number,
								'episode' : _common.args.episode_number,
								'TVShowTitle' : _common.args.show_title })
	xbmcplugin.setResolvedUrl(pluginHandle, True, item)
	if (_addoncompat.get_setting('enablesubtitles') == 'true') and (closedcaption != ''):
		while not xbmc.Player().isPlaying():
			xbmc.sleep(100)
		xbmc.Player().setSubtitles(_common.SUBTITLE)

def clean_subs(data):
	br = re.compile(r'<br.*?>')
	tag = re.compile(r'<.*?>')
	space = re.compile(r'\s\s\s+')
	apos = re.compile(r'&amp;apos;')
	sub = br.sub('\n', data)
	sub = tag.sub(' ', sub)
	sub = space.sub(' ', sub)
	sub = apos.sub('\'', sub)
	return sub

def convert_subtitles(closedcaption):
	str_output = ''
	subtitle_data = _connection.getURL(closedcaption, connectiontype = 0)
	subtitle_data = BeautifulSoup(subtitle_data, 'html.parser', parse_only = SoupStrainer('div'))
	srt_output = ''
	lines = subtitle_data.find_all('p')
	for i, line in enumerate(lines):
		if line is not None:
			sub = clean_subs(_common.smart_utf8(line))
			start_time = _common.smart_utf8(line['begin'].replace('.', ','))
			end_time = _common.smart_utf8(line['end'].replace('.', ','))
			str_output += str(i + 1) + '\n' + start_time + ' --> ' + end_time + '\n' + sub + '\n\n'
	file = open(_common.SUBTITLE, 'w')
	file.write(str_output)
	file.close()
