#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
import urllib
from .. import common
from .. import connection
from .. import main_nbcu
from bs4 import BeautifulSoup

SITE = 'usa'
NAME = 'USA Network'
DESCRIPTION = "USA Network is cable television's leading provider of original series and feature movies, sports events, off-net television shows, and blockbuster theatrical films. USA Network is seen in over 88 million U.S. homes. The USA Network web site is located at www.usanetwork.com. USA Network is a program service of NBC Universal Cable a division of NBC Universal, one of the world's leading media and entertainment companies in the development, production and marketing of entertainment, news and information to a global audience."
SHOWS = 'http://feed.theplatform.com/f/OyMl-B/8IyhuVgUXDd_/categories?form=json&sort=order'
CLIPS = 'http://feed.theplatform.com/f/OyMl-B/8IyhuVgUXDd_?count=true&form=json&byCustomValue={fullEpisode}{false}&byCategories=%s'
FULLEPISODES = 'http://feed.theplatform.com/f/OyMl-B/8IyhuVgUXDd_?count=true&form=json&byCustomValue={fullEpisode}{true}&byCategories=%s'
SWFURL = 'http://www.usanetwork.com/videos/pdk/swf/flvPlayer.swf'
FULLEPISODESWEB ='http://www.usanetwork.com/%s/video-categories/full-episodes'
BASE = 'http://www.usanetwork.com'

def masterlist():
	return main_nbcu.masterlist(SITE, SHOWS)

def seasons():
	main_nbcu.seasons(SITE, FULLEPISODES, CLIPS, FULLEPISODESWEB)

def episodes():
	main_nbcu.episodes(SITE)

def webepisodes():
	episode_url = common.args.url
	episode_data = connection.getURL(episode_url)
	web_tree = BeautifulSoup(episode_data, 'html.parser')
	episode_menu = web_tree.find_all('div', class_ = 'view-mode-vid_teaser_show_episode')
	for i, episode_item in enumerate(episode_menu):
		if 'tve-video-auth' not in episode_item['class']:
			episode_name = episode_item['omniture-title']
			try:
				season_number = int(re.compile('Season (\d+)').findall(episode_item.find(class_ = 'caption'))[0])
			except:
				season_number = -1
			try:
				episode_number = int(re.compile('Episode (\d+)').findall(episode_item.find(class_ = 'caption'))[0])
			except:
				episode_number = -1
			try:
				episode_thumb = episode_item.img['src']
			except:
				episode_thumb = None
			url = BASE + episode_item['omniture-id']
			u = sys.argv[0]
			u += '?url="' + urllib.quote_plus(url) + '"'
			u += '&mode="' + SITE + '"'
			u += '&sitemode="play_video"'
			infoLabels={	'title' : episode_name,
						 'season' : season_number,
						 'episode' : episode_number,
						}
			common.add_video(u, episode_name, episode_thumb, infoLabels = infoLabels, quality_mode  = 'list_qualities')
	common.set_view('episodes')

def list_qualities():
	return main_nbcu.list_qualities()

def play_video():
	main_nbcu.play_video()
