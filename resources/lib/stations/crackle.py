#!/usr/bin/python
# -*- coding: utf-8 -*-
import simplejson
import sys
import re
import urllib
import xbmc
import xbmcaddon
import xbmcgui
import xbmcplugin
from .. import common
from .. import connection
from .. import ustvpaths
from bs4 import BeautifulSoup, SoupStrainer

addon = xbmcaddon.Addon()
pluginHandle = int(sys.argv[1])

SITE = 'crackle'
NAME = 'Crackle'
ALIAS = ['Sony Entertainment Television']
DESCRIPTION = "Crackle, Inc. is a multi-platform video entertainment network and studio that distributes full length, uncut, movies, TV shows and original programming in our users favorite genres like comedy, action, crime, horror, Sci-Fi, and thriller. Crackles channels and shows reach a global audience across the Internet, in the living room, and on devices including a broad range of Sony electronics."
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
	master_data = connection.getURL(master_url)
	master_menu = simplejson.loads(master_data)['Entries']
	for master_item in master_menu:
		if addon.getSetting('hide_clip_only') == 'false' or not master_item.get('ClipsOnly', False):
			master_name = master_item['Title']
			season_url = FULLEPISODES % master_item['ID']
			master_dict[master_name] = season_url
			master_db.append((master_name, SITE, 'seasons', season_url))
	master_db.append(('--Crackle Movies', SITE, 'movielist', MOVIES))
	return master_db

def movielist(url = common.args.url):
	root_dict = {}
	root_url = url
	root_data = connection.getURL(root_url)
	root_menu = simplejson.loads(root_data)['Entries']
	for root_item in root_menu:
		if addon.getSetting('hide_clip_only') == 'false' or not root_item.get('ClipsOnly', False):
			root_name = root_item['Title']
			season_url = FULLEPISODES % root_item['ID']
			showdata = common.get_skelton_series(root_name, SITE, 'episodes', season_url)
			showdata[6] = root_item.get('ChannelArtTileWide', showdata[6])
			showdata[7] = root_item.get('ChannelArtTileLarge', showdata[7])
			showdata[8] = root_item.get('ChannelArtLandscape', showdata[8])
			showdata[9] = root_item.get('ReleaseYear', showdata[9])
			showdata[11] = root_item.get('ReleaseYear', showdata[11])
			showdata[13] = root_item.get('Genre', showdata[13])
			showdata[15] = root_item.get('Description', showdata[15])
			if root_item.get('ReleaseYear', None):
				showdata[15] = u"%s \n(%s, %s)" % (showdata[15], showdata[13], root_item.get('ReleaseYear'))
			common.add_show(root_name, SITE, 'episodes', season_url, showdata = showdata)
	common.set_view('root')

def seasons(season_url = common.args.url):
	seasons = []
	season_data = connection.getURL(season_url)
	media_list = simplejson.loads(season_data)['FolderList'][0]['PlaylistList'][0]['MediaList']
	for media in media_list:
		season_number = media['Season']
		if season_number not in seasons:
			season_title = 'Season %s' % season_number
			seasons.append(season_number)
			common.add_directory(season_title,  SITE, 'episodes', season_url + '#' + season_number)
	common.set_view('seasons')

def episodes(episode_url = common.args.url):
	try:
		season_number = episode_url.split('#')[1]
	except:
		season_number = -1
	episode_url = episode_url.split('#')[0]
	episode_data = connection.getURL(episode_url)
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
				episode_airdate = common.format_date(episode_item['ReleaseDate'], '%m/%d/%Y')
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
			common.add_video(u, episode_name, episode_thumb, infoLabels = infoLabels, quality_mode = 'list_qualities')
	common.set_view('episodes')

def list_qualities(video_url = common.args.url):
	return QUALITIES

def play_video(video_url = common.args.url):
	try:
		qbitrate = common.args.quality
	except:
		qbitrate = None
	hbitrate = -1
	hpath = None
	sbitrate = int(addon.getSetting('quality'))
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
	if (addon.getSetting('enablesubtitles') == 'true') and (closedcaption != ''):
			convert_subtitles(closedcaption)
	finalurl = video_url + hpath
	item = xbmcgui.ListItem(path = finalurl)
	if qbitrate is not None:
		item.setThumbnailImage(common.args.thumb)
		item.setInfo('Video', {	'title' : common.args.name,
								'season' : common.args.season_number,
								'episode' : common.args.episode_number,
								'TVShowTitle' : common.args.show_title })
	xbmcplugin.setResolvedUrl(pluginHandle, True, item)
	if (addon.getSetting('enablesubtitles') == 'true') and (closedcaption != ''):
		while not xbmc.Player().isPlaying():
			xbmc.sleep(100)
		xbmc.Player().setSubtitles(ustvpaths.SUBTITLE)

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
	subtitle_data = connection.getURL(closedcaption, connectiontype = 0)
	subtitle_data = BeautifulSoup(subtitle_data, 'html.parser', parse_only = SoupStrainer('div'))
	srt_output = ''
	lines = subtitle_data.find_all('p')
	for i, line in enumerate(lines):
		if line is not None:
			sub = clean_subs(common.smart_utf8(line))
			start_time = common.smart_utf8(line['begin'].replace('.', ','))
			end_time = common.smart_utf8(line['end'].replace('.', ','))
			str_output += str(i + 1) + '\n' + start_time + ' --> ' + end_time + '\n' + sub + '\n\n'
	file = open(ustvpaths.SUBTITLE, 'w')
	file.write(str_output)
	file.close()
