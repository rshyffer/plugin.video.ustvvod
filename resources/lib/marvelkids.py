#!/usr/bin/python
# -*- coding: utf-8 -*-
import _common
import _connection
import _main_brightcove
import re
import sys
import urllib
import xbmcgui
import xbmcplugin
from bs4 import BeautifulSoup

pluginHandle = int (sys.argv[1])

SITE = 'marvelkids'
NAME = 'Marvel Kids'
DESCRIPTION = "Marvel started in 1939 as Timely Publications, and by the early 1950s had generally become known as Atlas Comics. Marvel\'s modern incarnation dates from 1961, the year that the company launched Fantastic Four and other superhero titles created by Stan Lee, Jack Kirby, Steve Ditko, and others. Marvel counts among its characters such well-known properties as Spider-Man, the X-Men, the Fantastic Four, Iron Man, the Hulk, Thor, Captain America and Daredevil; antagonists such as the Green Goblin, Magneto, Doctor Doom, Galactus, and the Red Skull. Most of Marvel\'s fictional characters operate in a single reality known as the Marvel Universe, with locations that mirror real-life cities such as New York, Los Angeles and Chicago."
BASE = 'http://marvelkids.marvel.com'
SHOWS = 'http://marvelkids.marvel.com/shows'
CONST = '4c1b306cc23230173e7dfc04e68329d3c0c354cb'

def masterlist():
	master_db = []
	master_data = _connection.getURL(SHOWS)
	master_menu = BeautifulSoup(master_data, 'html.parser').find_all(href = re.compile('/shows/'))
	for master_item in master_menu:
		master_name = master_item['title']
		season_url = BASE + master_item['href']
		master_db.append((master_name, SITE, 'seasons', season_url))
	return master_db

def seasons(season_url = _common.args.url):
	season_data = _connection.getURL(season_url)
	season_tree = BeautifulSoup(season_data, 'html.parser')
	season_menu = season_tree.find_all('div', class_ = 'tab-wrap')
	for season_item in season_menu:
		season_name = season_item.h2.text
		_common.add_directory(season_name, SITE, 'episodes', season_url)
	_common.set_view('seasons')

def episodes(episode_url = _common.args.url):
	episode_data = _connection.getURL(episode_url)
	episode_tree = BeautifulSoup(episode_data, 'html.parser')
	episode_carousel = episode_tree.find_all('div', class_ = 'tab-wrap')
	for episode in episode_carousel:
		if _common.args.name == episode.h2.text:
			episode_menu = episode.find_all('li', class_ = 'result-item')
			for episode_item in episode_menu:
				episode_name = episode_item.img['title']
				episode_thumb = episode_item.img['src']
				episode_exp_id = episode_item.a['data-video']
				episode_plot = episode_item.find('p', class_ = 'description').text.strip()
				url = episode_url
				u = sys.argv[0]
				u += '?url="' + urllib.quote_plus(url) + '#' + urllib.quote_plus(episode_exp_id) + '"'
				u += '&mode="' + SITE + '"'
				u += '&sitemode="play_video"'
				infoLabels={	'title' : episode_name,
								'plot' : episode_plot }
				_common.add_video(u, episode_name, episode_thumb, infoLabels = infoLabels)
	_common.set_view('episodes')

def play_video(video_url = _common.args.url):
	stored_size = 0
	video_url, video_content_id = video_url.split('#')
	video_data = _connection.getURL(video_url)
	video_tree = BeautifulSoup(video_data, 'html.parser')
	video_player_key = video_tree.find('param', attrs = {'name' : 'playerKey'})['value']
	video_player_id = video_tree.find('param', attrs = {'name' : 'publisherID'})['value']
	renditions = _main_brightcove.get_episode_info(video_player_key, video_content_id, video_url, video_player_id, CONST)
	finalurl = renditions['programmedContent']['videoPlayer']['mediaDTO']['FLVFullLengthURL']
	for item in sorted(renditions['programmedContent']['videoPlayer']['mediaDTO']['renditions'], key = lambda item:item['frameHeight'], reverse = False):
		stream_size = item['size']
		if (int(stream_size) > stored_size):
			finalurl = item['defaultURL']
			stored_size = stream_size
	xbmcplugin.setResolvedUrl(pluginHandle, True, xbmcgui.ListItem(path = finalurl))
