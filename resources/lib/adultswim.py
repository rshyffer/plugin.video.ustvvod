#!/usr/bin/python
# -*- coding: utf-8 -*-
import _addoncompat
import _common
import _connection
import sys
import urllib
import xbmcgui
import xbmcplugin
from bs4 import BeautifulSoup

pluginHandle = int(sys.argv[1])

SITE = 'adultswim'
NAME = "Adult Swim"
DESCRIPTION = "Cartoon Network (CartoonNetwork.com), currently seen in more than 97 million U.S. homes and 166 countries around the world, is Turner Broadcasting System, Inc.'s ad-supported cable service now available in HD offering the best in original, acquired and classic entertainment for youth and families.  Nightly from 10 p.m. to 6 a.m. (ET, PT), Cartoon Network shares its channel space with Adult Swim, a late-night destination showcasing original and acquired animated and live-action programming for young adults 18-34 "
SHOWS = 'http://asfix.adultswim.com/staged/AS.configuration.xml?cacheID=1382732985626'
SEASONSCLIPS = 'http://video.adultswim.com/adultswimdynamic/asfix-svc/episodeSearch/getAllEpisodes?limit=0&offset=0&sortByDate=DESC&filterByEpisodeType=PRE,CLI&filterByCollectionId=%s&networkName=AS&filterByAuthType=true'
SEASONSEPISODES = 'http://video.adultswim.com/adultswimdynamic/asfix-svc/episodeSearch/getAllEpisodes?limit=0&offset=0&sortByDate=DESC&filterByEpisodeType=EPI&filterByCollectionId=%s&networkName=AS&filterByAuthType=true'
SEASONSCLIPSEXTRA = 'http://video.adultswim.com/adultswimdynamic/asfix-svc/episodeSearch/getAllEpisodes?limit=1&offset=0&sortByDate=DESC&filterByEpisodeType=PRE,CLI&filterByCollectionId=%s&networkName=AS&filterByAuthType=true'
SEASONSEPISODESEXTRA = 'http://video.adultswim.com/adultswimdynamic/asfix-svc/episodeSearch/getAllEpisodes?limit=1&offset=0&sortByDate=DESC&filterByEpisodeType=EPI&filterByCollectionId=%s&networkName=AS&filterByAuthType=true'
CLIPS = 'http://video.adultswim.com/adultswimdynamic/asfix-svc/episodeSearch/getAllEpisodes?limit=50&offset=0&sortByDate=DESC&filterByEpisodeType=CLI&filterByCollectionId=%s&filterByAuthType=true&networkName=AS'
FULLEPISODES = 'http://video.adultswim.com/adultswimdynamic/asfix-svc/episodeSearch/getAllEpisodes?limit=50&offset=0&sortByDate=DESC&filterByEpisodeType=EPI&filterByCollectionId=%s&filterByAuthType=true&networkName=AS'
EPISODE = 'http://video.adultswim.com/adultswimdynamic/asfix-svc/episodeSearch/getEpisodesByIDs?ids=%s&networkName=AS'
VIDEOINFO = 'http://asfix.adultswim.com/asfix-svc/episodeservices/getCvpPlaylist?networkName=AS&id=%s'

def masterlist():
	master_db = []
	master_dict = {}
	master_data = _connection.getURL(SHOWS)
	master_tree = BeautifulSoup(master_data, 'html5lib')
	master_menu = master_tree.allcollections.find_all('collection')
	for master_item in master_menu:
		master_name = _common.smart_utf8(master_item['name'])
		tvdb_name = _common.get_show_data(master_name, SITE, 'seasons')[-1]
		if tvdb_name not in master_dict.keys():
			master_dict[tvdb_name] = master_item['id']
		else:
			master_dict[tvdb_name] = master_dict[tvdb_name] + ',' + master_item['id']
	for master_name in master_dict:
		season_url = master_dict[master_name]
		master_db.append((master_name,  SITE, 'seasons', season_url))
	return master_db

def rootlist():
	root_dict = {}
	root_data = _connection.getURL(SHOWS)
	root_tree = BeautifulSoup(root_data, 'html5lib')
	root_menu = root_tree.allcollections.find_all('collection')
	for root_item in root_menu:
		root_name = _common.smart_utf8(root_item['name'])
		tvdb_name = _common.get_show_data(root_name, SITE, 'seasons')[-1]
		if tvdb_name not in root_dict.keys():
			root_dict[tvdb_name] = root_item['id']
		else:
			root_dict[tvdb_name] = root_dict[tvdb_name] + ',' + root_item['id']
	for root_name in root_dict:
		season_url = root_dict[root_name]
		_common.add_show(root_name,  SITE, 'seasons', season_url)
	_common.set_view('tvshows')

def seasons(collection_ids = _common.args.url):
	for collection_id in collection_ids.split(','):
		if ',' not in collection_ids:
			season_url = SEASONSEPISODES
		else:
			season_url = SEASONSEPISODESEXTRA
		season_data = _connection.getURL(season_url % collection_id)
		print BeautifulSoup(season_data, 'html.parser').episodes
		season_tree = BeautifulSoup(season_data, 'html.parser')
		episode_count = int(season_tree.episodes['totalitems'])
		if episode_count > 0:
			if ',' not in collection_ids:
				display = 'Episodes'
			else:
				display = 'Episodes - %s' % season_tree.episode['collectiontitle']
			_common.add_directory(display,  SITE, 'episodes', FULLEPISODES % collection_id)
	for collection_id in collection_ids.split(','):
		if ',' not in collection_ids:
			seasonclips_url = SEASONSCLIPS
		else:
			seasonclips_url = SEASONSCLIPSEXTRA
		season_data2 = _connection.getURL(seasonclips_url % collection_id)
		season_tree2 = BeautifulSoup(season_data2, 'html.parser')
		print BeautifulSoup(season_data2, 'html.parser').episodes
		episode_count = int(season_tree2.episodes['totalitems'])
		if episode_count > 0:
			if ',' not in collection_ids:
				display = 'Clips'
			else:
				display = 'Clips - %s' % season_tree2.episode['collectiontitle']
			_common.add_directory(display,  SITE, 'episodes', CLIPS % collection_id)
	_common.set_view('seasons')

def episodes(episode_url = _common.args.url):
	episode_data = _connection.getURL(episode_url)
	episode_tree = BeautifulSoup(episode_data, 'html.parser')
	episode_menu = episode_tree.find_all('episode')
	for episode_item in episode_menu:
		url = EPISODE % episode_item['id']
		try:
			episode_duration = episode_item['duration']
			episode_duration = int(_common.format_seconds(episode_duration))
		except:
			episode_duration = 0
			for segment_duration in episode_item.find_all('segment'):
				episode_duration += float(segment_duration['duration'])
		try:
			episode_airdate = _common.format_date(episode_item['originalpremieredate'].split(' ')[0],'%m/%d/%Y')
		except:
			try:
				episode_airdate = _common.format_date(episode_item['launchdate'].split(' ')[0],'%m/%d/%Y')
			except:
				episode_airdate = -1
		episode_name = episode_item['title']
		try:
			season_number = int(episode_item['episeasonnumber'])
		except:
			season_number = -1
		try:
			episode_number = int(episode_item['episodenumber'][:2])
		except:
			episode_number = -1
		try:
			episode_thumb = episode_item['thumbnailurl']
		except:
			episode_thumb = None
		episode_plot = episode_item.description.text
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
	_common.set_view('episodes')

def play_video(video_url = _common.args.url):
	stack_url = 'stack://'
	hbitrate = -1
	sbitrate = int(_addoncompat.get_setting('quality')) * 1024
	closedcaption = None
	video_data = _connection.getURL(video_url)
	video_tree = BeautifulSoup(video_data, 'html.parser')
	video_segments = video_tree.find_all('segment')
	for video_segment in video_segments:
		seg_url = VIDEOINFO % video_segment['id']
		seg_data = _connection.getURL(seg_url)
		seg_menu = BeautifulSoup(seg_data).find_all('file')
		hbitrate = -1
		file_url = None
		for video_index in seg_menu:
			try:
				bitrate = int(video_index['bitrate'])
				type = video_index['type']
				if bitrate > hbitrate and bitrate <= sbitrate:
					hbitrate = bitrate
					file_url = video_index.string
				elif bitrate == hbitrate and bitrate <= sbitrate and type == 'hd' :
					file_url = video_index.string
			except:
				pass
		if file_url is None:
			file_url = BeautifulSoup(seg_data).find_all('file',type = 'hd')[0].string
		stack_url += file_url.replace(',', ',,') + ' , '
	finalurl = stack_url[:-3]
	xbmcplugin.setResolvedUrl(pluginHandle, True, xbmcgui.ListItem(path = finalurl))

