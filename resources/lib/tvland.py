#!/usr/bin/python
# -*- coding: utf-8 -*-
import _addoncompat
import _common
import _connection
import _main_viacom
import os
import re
import sys
import urllib
import xbmc
import xbmcgui
import xbmcplugin
from bs4 import BeautifulSoup, SoupStrainer

pluginHandle = int(sys.argv[1])

SITE = 'tvland'
NAME = 'TV Land'
DESCRIPTION = "TV Land is dedicated to presenting the best in entertainment on all platforms for consumers in their 40s. Armed with a slate of original programming, acquired classic shows, hit movies and fullservice website, TV Land is now seen in over 98 million U.S. homes. TV Land PRIME is TV Land's prime time programming destination designed for people in their mid-forties and the exclusive home to the premieres of the network's original programming, contemporary television series acquisitions and movies."
BASE = 'http://www.tvland.com'
SHOWS = 'http://www.tvland.com/full-episodes'
CLIPS = 'http://www.tvland.com/video-clips'
SEASONURL = 'http://www.tvland.com/fragments/search_results/related_episodes_seasons?showId=%s&seasonId=%s&episodeId=%s'
VIDEOURL = 'http://www.tvland.com/feeds/video_player/mrss?uri='
MP4URL = 'http://mtvnmobile.vo.llnwd.net/kip0/_pxn=0+_pxK=18639/44620/mtvnorigin'

def masterlist():
	master_dict = {}
	master_db = []
	for master_url in (CLIPS, SHOWS):
		master_data = _connection.getURL(master_url)
		master_tree = BeautifulSoup(master_data, 'html.parser')
		master_menu = master_tree.find('div', class_ = 'showsList').find_all('a')
		for master_item in master_menu:
			master_name = master_item.contents[0].strip()
			season_url = master_item['href'].rsplit('/', 1)[0]
			master_dict[master_name] = season_url
	for master_name, season_url in master_dict.iteritems():	
		master_db.append((master_name, SITE, 'seasons', season_url))
	return master_db

def seasons(season_url = _common.args.url):
	season_data = _connection.getURL(season_url)
	season_menu = BeautifulSoup(season_data, 'html.parser').find('a', class_ = 'full_episodes')
	season_menu2 = BeautifulSoup(season_data, 'html.parser').find('a', class_ = 'video_clips')
	if season_menu is not None:
		season_url2 = BASE + season_menu['href']
		_common.add_directory('Full Episodes',  SITE, 'episodes', season_url2)
	if season_menu2 is not None:
		season_url3 = BASE + season_menu2['href']
		_common.add_directory('Clips',  SITE, 'episodes', season_url3)
	_common.set_view('seasons')

def episodes(episode_url = _common.args.url):
	episode_data = _connection.getURL(episode_url)
	episode_tree = BeautifulSoup(episode_data.replace('\'+\'', ''), 'html.parser')
	if _common.args.name == 'Clips':
		if episode_tree.find('a', class_ = 'next') is not None:
			add_clips(episode_tree)
			try:
				episodes(episode_url.split('?')[0] + episode_tree.find('a', class_ = 'next')['href'])
			except:
				pass
		else:
			add_clips(episode_tree)
	else:
		if episode_tree.find('a', class_ = 'season_menu') is not None:
			show_id = re.compile('var showId = "(.+?)";').findall(episode_data)[0]
			episode_id = re.compile('var episodeId = "(.+?)";').findall(episode_data)[0]
			episode_menu = episode_tree.find_all('a', class_ = 'season')
			for episode_item in episode_menu:
				episode_data2 = _connection.getURL(SEASONURL %(show_id, episode_item['id'], episode_id))
				episode_tree2 = BeautifulSoup(episode_data2)
				add_fullepisodes(episode_tree2, episode_item.text.split(' ')[1])
		else:
			add_fullepisodes(episode_tree)
	_common.set_view('episodes')

def add_fullepisodes(episode_tree, season_number = -1):
	try:
		episode_menu = episode_tree.find_all('div', class_ = 'episodeContainer')
		for episode_item in episode_menu:
			episode_name = episode_item.find('div', class_ = 'episodeTitle').a.text
			episode_airdate = _common.format_date(episode_item.find('div', class_ = 'episodeAirDate').contents[1].strip(), '%b %d, %Y', '%d.%m.%Y')
			episode_plot = episode_item.find('div', class_ = 'episodeDescription').contents[0].strip()
			episode_thumb = episode_item.find('div', class_ = 'episodeImage').img['src'].split('?')[0]
			url = episode_item.find('div', class_ = 'episodeTitle').a['href']
			try:
				episode_duration = _common.format_seconds(episode_item.find('span', class_ = 'episodeDuration').text.replace(')', '').replace('(', ''))
			except:
				episode_duration = -1
			try:
				episode_number = int(episode_item.find('div', class_ = 'episodeIdentifier').text.split('#' + season_number)[1])
			except:
				episode_number = -1
			u = sys.argv[0]
			u += '?url="' + urllib.quote_plus(url) + '"'
			u += '&mode="' + SITE + '"'
			u += '&sitemode="play_video"'
			infoLabels = {	'title' : episode_name,
							'durationinseconds' : episode_duration,
							'season' : season_number,
							'episode' : episode_number,
							'plot' : episode_plot,
							'premiered' : episode_airdate }
			_common.add_video(u, episode_name, episode_thumb, infoLabels = infoLabels, quality_mode  = 'list_qualities')
	except:
		pass

def add_clips(episode_tree, season_number = -1):
	try:
		episode_menu = episode_tree.find_all('div', class_ = 'search_pad')
		for episode_item in episode_menu:
			show_name = episode_item.find('div', class_ = 'search_show').text
			episode_name = episode_item.find('div', class_ = 'search_text').a.text.strip()
			episode_plot = episode_item.find('div', class_ = 'search_text').contents[4].strip()
			url = episode_item.find('div', class_ = 'search_text').a['href']
			episode_thumb = episode_item.find('div', class_ = 'search_image').img['src'].split('?')[0]
			try:
				episode_airdate = episode_item.find('div', class_ = 'episode_meta').contents[5].text.replace('Aired: ', '').strip()
				episode_airdate = _common.format_date(episode_airdate, '%B %d, %Y', '%d.%m.%Y')
			except:
				episode_airdate = -1
			try:
				episode_duration = _common.format_seconds(episode_item.find('span', class_ = 'search_duration').text.replace(')', '').replace('(', ''))
			except:
				episode_duration = -1
			try:
				episode_number = int(episode_item.find('div', class_ = 'episode_meta').contents[1].text.split('#')[1])
			except:
				episode_number = -1
			u = sys.argv[0]
			u += '?url="' + urllib.quote_plus(url) + '"'
			u += '&mode="' + SITE + '"'
			u += '&sitemode="play_video"'
			infoLabels = {	'title' : episode_name,
							'durationinseconds' : episode_duration,
							'season' : season_number,
							'episode' : episode_number,
							'plot' : episode_plot,
							'premiered' : episode_airdate,
							'tvshowtitle': show_name }
			_common.add_video(u, episode_name, episode_thumb, infoLabels = infoLabels, quality_mode  = 'list_qualities')
	except:
		pass

def play_video(video_url = _common.args.url):
	video_data = _connection.getURL(video_url)
	video_url2 = BeautifulSoup(video_data, 'html.parser').find('div', class_ = 'videoShare')['data-unique-id']
	_main_viacom.play_video(BASE, video_url2, VIDEOURL)	

def list_qualities(video_url = _common.args.url):
	video_data = _connection.getURL(video_url)
	video_url2 = BeautifulSoup(video_data, 'html.parser').find('div', class_ = 'videoShare')['data-unique-id']
	return _main_viacom.list_qualities(BASE, video_url2, media_base = VIDEOURL)
