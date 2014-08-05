#!/usr/bin/python
# -*- coding: utf-8 -*-
import _addoncompat
import _common
import _connection
import _main_turner
import sys
import urllib
import xbmcgui
import xbmcplugin
import re
from bs4 import BeautifulSoup

pluginHandle = int(sys.argv[1])

SITE = 'cartoon'
NAME = "Cartoon Network"
DESCRIPTION = "Cartoon Network (CartoonNetwork.com), currently seen in more than 97 million U.S. homes and 166 countries around the world, is Turner Broadcasting System, Inc.'s ad-supported cable service now available in HD offering the best in original, acquired and classic entertainment for youth and families.  Nightly from 10 p.m. to 6 a.m. (ET, PT), Cartoon Network shares its channel space with Adult Swim, a late-night destination showcasing original and acquired animated and live-action programming for young adults 18-34 "
SHOWS = 'http://www.cartoonnetwork.com/video/staged/CN2.mobile.configuration.xml'
CLIPS = 'http://cnvideosvc2.cartoonnetwork.com/svc/episodeSearch/getAllEpisodes?networkName=CN2?limit=400&offset=0&sortByDate=DESC&filterByEpisodeType=CLI-CLI&filterByCollectionId=%s&filterBySeasonNumber=%s'
FULLEPISODES = 'http://cnvideosvc2.cartoonnetwork.com/svc/episodeSearch/getAllEpisodes?networkName=CN2?limit=400&offset=0&sortByDate=DESC&filterByEpisodeType=TVE&filterByCollectionId=%s&filterBySeasonNumber=%s'
EPISODE = 'http://www.cartoonnetwork.com/video-seo-svc/episodeservices/getCvpPlaylist?networkName=CN2&id=%s'

def masterlist():
	master_db = []
	master_dict = {}
	master_data = _connection.getURL(SHOWS)
	master_tree = BeautifulSoup(master_data, 'html.parser')
	master_menu = master_tree.allcollections.find_all('collection')
	for master_item in master_menu:
		master_name = _common.smart_utf8(master_item['name'])
		if '[AD]' not in master_name:
			tvdb_name = _common.get_show_data(master_name, SITE, 'seasons')[-1]
			season_url = master_item['id'] 
			season_url = season_url + '#tveepisodes='
			try:
				for season in master_item.tveepisodes.find_all('season'):
					season_url = season_url + '-' + season['number']
			except:
				pass
			season_url = season_url + '#clips='
			try:
				for season in master_item.clips.find_all('season'):
					if season['number'] != '':
						season_url = season_url + '-' + season['number']
				else:
					season_url = season_url + '-' + '*'
			except:
				pass
			master_db.append((master_name,  SITE, 'seasons', season_url))
	return master_db

def seasons(season_string = _common.args.url):
	collection_id = season_string.split('#')[0]
	tve = season_string.split('#')[1].split('=')[1][1:]
	clips = season_string.split('#')[2].split('=')[1][1:]
	for season in tve.split('-'):
		if season:
			_common.add_directory('Season ' + season,  SITE, 'episodes', FULLEPISODES % (collection_id, season))
	for season in clips.split('-'):
		if season:
			if season != '*':
				display = 'Clips Season ' + season
			else:
				display = 'Specials'
			_common.add_directory(display,  SITE, 'episodes', CLIPS % (collection_id, season.replace('*', '')))
	_common.set_view('seasons')

def episodes():
	_main_turner.episodes(SITE)

def play_video(video_id = _common.args.url):
	_main_turner.play_video(SITE, EPISODE)

def list_qualities():
	return _main_turner.list_qualities(SITE, EPISODE)