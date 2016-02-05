#!/usr/bin/python
# -*- coding: utf-8 -*-
import common
import connection
import json
import main_brightcove
import simplejson
import sys
import urllib
import xbmcaddon
import xbmcgui
import xbmcplugin
from bs4 import BeautifulSoup

addon = xbmcaddon.Addon()
pluginHandle = int(sys.argv[1])

SITE = "ifc"
NAME = "IFC"
DESCRIPTION = "IFC is the home of offbeat, unexpected comedies.  Series like Portlandia, Documentary Now!, Maron and Comedy Bang! Bang! air alongside fan-favorite movies and comedic cult TV shows. IFC is owned and operated by AMC Networks Inc., and available across multiple platforms.  IFC is Always On Slightly Off."
APIBASE = "http://www.ifc.com/api/mobile-feeds/v1/"
#VIDEOURL = "http://link.theplatform.com/s/M_UwQC/media/"
VIDEOURL = "http://link.theplatform.com/s/M_UwQC/media/%s?mbr=true&player=IFC%%20Default%%20-%%20IMA%%20Update%%20-%%20Flash%%20-%%200.0.3&policy=47257419&mvpd=NonAuth&format=SMIL&Tracking=true&Embedded=true&formats=MPEG4,FLV,MP3&manifest=m3u"

def masterlist():
	master_db = []
	master_data = connection.getURL(APIBASE + "shows")
	show_json = json.loads(master_data)
	for show in show_json['data']['Shows']:
		show_name = show['Name']
		show_id = show['Id']
		master_db.append((show_name, SITE, 'seasons', show_id))
	return master_db

def seasons(show_id = common.args.url):
	seasons = []
	season_data = connection.getURL(APIBASE + "show-details?show_id=" + show_id)
	season_json = json.loads(season_data)
	for season_item in season_json['data']['Show']['Seasons']:
		season_number = season_item['Number']
		season_name = "Season " + season_item['Number']
		seasons.append((season_name, SITE, 'episodes', show_id + '|' + season_number, -1, -1))
	return seasons

def episodes(filter = common.args.url):
	episodes = []
	show_id, season_num = filter.split('|')

	season_data = connection.getURL(APIBASE + "show-details?show_id=" + show_id)
	season_json = json.loads(season_data)
	for season_item in season_json['data']['Show']['Seasons']:
		if season_item['Number'] == season_num:
			for episode_item in season_item['Episodes']:				
				episode_data = connection.getURL(APIBASE + 'episode-details?episode_id=' + str(episode_item['Id']))
				episode_json = json.loads(episode_data)
				if 'PID' in episode_json['data']['Episode']['FullEpisode']:
					episode_name = episode_item['Title']
					episode_plot = episode_item['Synopsis']
					episode_thumb = episode_item['ShowLogoUri']
					episode_id = episode_item['Id']
					episode_number = episode_item['EpisodeNumber']
					u = sys.argv[0]
					u += '?url="' + str(episode_id) + '"'
					u += '&mode="' + SITE + '"'
					u += '&sitemode="play_video"'
					infoLabels={	'title' : episode_name,
									'plot' : episode_plot, 
									'TVShowTitle' : season_json['data']['Show']['Name'],
									'season' : season_num,
									'episode' : episode_number}
					episodes.append((u, episode_name, episode_thumb, infoLabels, None, False, None))
	return episodes

def play_video(episode_url = common.args.url):
	episode_data = connection.getURL(APIBASE + 'episode-details?episode_id=' + episode_url)
	episode_json = json.loads(episode_data)
	video_url = VIDEOURL % episode_json['data']['Episode']['FullEpisode']['PID']
	print video_url
	video_data = connection.getURL(video_url)
	video_tree = BeautifulSoup(video_data)
	finalurl = video_tree.video['src']
	item = xbmcgui.ListItem(path = finalurl)
	try:
		item.setThumbnailImage(common.args.thumb)
	except:
		pass
	try:
		item.setInfo('Video', {	'title' : common.args.name,
								'season' : common.args.season_number,
								'episode' : common.args.episode_number,
								'TVShowTitle' : common.args.show_title})
	except:
		pass
	xbmcplugin.setResolvedUrl(pluginHandle, True, item)