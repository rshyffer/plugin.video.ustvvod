#!/usr/bin/python
# -*- coding: utf-8 -*-
import common
import connection
import main_turner
import plistlib
import json
import sys
import urllib
from bs4 import BeautifulSoup

SITE = "adultswim"
NAME = "Adult Swim"
DESCRIPTION = "Cartoon Network (CartoonNetwork.com), currently seen in more than 97 million U.S. homes and 166 countries around the world, is Turner Broadcasting System, Inc.'s ad-supported cable service now available in HD offering the best in original, acquired and classic entertainment for youth and families.  Nightly from 10 p.m. to 6 a.m. (ET, PT), Cartoon Network shares its channel space with Adult Swim, a late-night destination showcasing original and acquired animated and live-action programming for young adults 18-34 "
SHOWS = "http://www.adultswim.com/mobile/tools/feeds/shows.plist"
S = "http://www.adultswim.com/videos/app/show/%s?filterByPlatform=mobile"
SEASONSCLIPS = "http://www.adultswim.com/videos/api/v1/videos?limit=0&offset=0&sortByDate=DESC&filterByEpisodeType=PRE,CLI&filterByCollectionId=%s&networkName=AS&filterByAuthType=true"
SEASONSEPISODES = "http://www.adultswim.com/videos/api/v1/videos?limit=0&offset=0&sortByDate=DESC&filterByEpisodeType=EPI,TVE&filterByCollectionId=%s&networkName=AS&filterByAuthType=true"
SEASONSCLIPSEXTRA = "http://www.adultswim.com/videos/api/v1/videos?limit=1&offset=0&sortByDate=DESC&filterByEpisodeType=PRE,CLI&filterByCollectionId=%s&networkName=AS&filterByAuthType=true"
SEASONSEPISODESEXTRA = "http://www.adultswim.com/videos/api/v1/videos?limit=1&offset=0&sortByDate=DESC&filterByEpisodeType=EPI&filterByCollectionId=%s&networkName=AS&filterByAuthType=true"
CLIPS = "http://www.adultswim.com/videos/api/v1/videos?limit=50&offset=0&sortByDate=DESC&filterByEpisodeType=CLI&filterByCollectionId=%s&filterByAuthType=true&networkName=AS"
FULLEPISODES = "http://www.adultswim.com/videos/api/v1/videos?limit=50&offset=0&sortByDate=DESC&filterByEpisodeType=EPI,TVE&filterByCollectionId=%s&filterByAuthType=true&networkName=AS&filterByPlatform=mobile"
EPISODE = "http://www.adultswim.com/videos/api/v0/assets?id=%s&networkName=AS"
HLSPATH = "adultswim"

def masterlist():
	master_db = []
	master_dict = {}
	master_data = connection.getURL(SHOWS)
	master_tree = plistlib.readPlistFromString(master_data)
	for master_item in master_tree:
		master_name = common.smart_utf8(master_item['name'])
		tvdb_name = common.get_show_data(master_name, SITE, 'seasons')[-1]
		if tvdb_name not in master_dict.keys():
			master_dict[tvdb_name] = master_item['show-id']
		else:
			master_dict[tvdb_name] = master_dict[tvdb_name] + ',' + master_item['show-id']
	for master_name in master_dict:
		season_url = master_dict[master_name]
		master_db.append((master_name,  SITE, 'seasons', season_url))
	return master_db

def seasons(collection_ids = common.args.url):
	seasons = []
	for collection_id in collection_ids.split(','):
		if ',' not in collection_ids:
			season_url = S
		else:
			season_url = S
		season_data = connection.getURL(season_url % collection_id)
		episode_json = json.loads(season_data)
		for season in  episode_json['show']['collections']:
			seasons.append((season['title'],  SITE, 'episodes', season_url % collection_id + '#' + str(season['id']), -1, -1))

	return seasons

def episodes(url = common.args.url):
	

	episodes = []
	episode_url = url.split('#')[0]
	season = url.split('#')[1]
	print episode_url
	episode_data = connection.getURL(episode_url)
	episode_menu = json.loads(episode_data)['show']['collections']
	for episode_season in episode_menu:
		if episode_season['id'] == int(season):

			for episode_item in episode_season['videos']:
				url = episode_item['id']
				try:

					episode_duration = episode_item['duration']
				except:
					episode_duration = -1
				try:

					episode_airdate = common.format_date(episode_item['1446015600'], epoch = True)
				except:
					episode_airdate = -1
				try:

					episode_plot = episode_item['description']
				except:
					episode_plot = ''
				episode_name = episode_item['title']

				try:

					season_number = int(episode_item['season_number'])
				except:
					season_number = -1
				try:

					episode_number =  int(episode_item['episode_number'])
				except:
					episode_number = -1
				try:

					episode_thumb = episode_item['images'][1]['url']
				except:
					episode_thumb = None
				episode_mpaa = episode_item['tv_rating']
				print episode_mpaa
				try:
					episode_type = episode_item['type']
				except:
					episode_type = None
				show_title = episode_item['collectionSlug'].replace('-', ' ').title()

				try:
					u = sys.argv[0]
					u += '?url="' + urllib.quote_plus(url) + '"'
					u += '&mode="' + SITE + '"'
					u += '&sitemode="play_video"'
					infoLabels={    'title' : episode_name,
									'durationinseconds' : episode_duration,
									'season' : season_number,
									'episode' : episode_number,
									'plot' : episode_plot,
									'premiered' : episode_airdate ,
									'mpaa' : episode_mpaa,
									'TVShowTitle': show_title}
					print infoLabels
				except Exception, e:
					print e
				episodes.append((u, episode_name, episode_thumb, infoLabels, 'list_qualities', False, type ))
	return episodes

def play_video():
	main_turner.play_video(SITE, EPISODE, HLSPATH)

def list_qualities():
	return main_turner.list_qualities(SITE, EPISODE)
