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
from bs4 import BeautifulSoup, SoupStrainer

pluginHandle = int(sys.argv[1])

SITE = 'nick'
NAME = 'Nickelodeon'
DESCRIPTION = "Nickelodeon, now in its 31st year, is the number-one entertainment brand for kids. It has built a diverse, global business by putting kids first in everything it does. The company includes television programming and production in the United States and around the world, plus consumer products, online, recreation, books and feature films. Nickelodeon's U.S. television network is seen in more than 100 million households and has been the number-one-rated basic cable network for 16 consecutive years."
BASE = 'http://www.nick.com'
SHOWS = 'http://www.nick.com/videos/all-videos'
CLIPS = 'http://www.nick.com/ajax/all-videos-list/all-videos?type=showvideo&tag=%s'
FULLEPISODES = 'http://www.nick.com/ajax/all-videos-list/all-videos?type=videoplaylist-segmented&tag=%s'

def masterlist():
	master_db = []
	master_data = _connection.getURL(SHOWS, header = {'X-Forwarded-For' : '12.13.14.15'})
	master_tree = BeautifulSoup(master_data, 'html5lib')
	master_menu = master_tree.find_all('div', class_ = 'filter-category right')[0].find_all('li')
	for master_item in master_menu:
		master_name = master_item.find('span', class_ = 'filter-name').text.replace('&','and')
		season_url = master_item['data-value'] 
		master_db.append((master_name, SITE, 'seasons', season_url))
	return master_db

def rootlist():
	root_data = _connection.getURL(SHOWS, header = {'X-Forwarded-For' : '12.13.14.15'})
	root_tree = BeautifulSoup(root_data, 'html5lib')
	root_menu = root_tree.find_all('div', class_ = 'filter-category right')[0].find_all('li')
	for root_item in root_menu:
		root_name = root_item.find('span', class_ = 'filter-name').text.replace('&','and')
		season_url = root_item['data-value'] 
		_common.add_show(root_name, SITE, 'seasons', season_url)
	_common.set_view('tvshows')

def seasons(season_url = _common.args.url):
	season_data = _connection.getURL(FULLEPISODES % season_url + '&start=0&rows=1', header = {'X-Forwarded-For' : '12.13.14.15'})
	try:
		season_menu = int(BeautifulSoup(season_data).find('section', class_ = 'video-content-list')['data-numfound'])
	except:
		season_menu = 0
	if season_menu > 0:
		season_url2 = FULLEPISODES % season_url + '&start=0&rows=' + str(season_menu)
		_common.add_directory('Full Episodes',  SITE, 'episodes', season_url2)
	season_data2 = _connection.getURL(CLIPS % season_url + '&start=0&rows=1', header = {'X-Forwarded-For' : '12.13.14.15'})
	try:
		season_menu2 = int(BeautifulSoup(season_data2).find('section', class_ = 'video-content-list')['data-numfound'])
	except:
		season_menu2 = 0
	if season_menu2 > 0:
		season_url3 = CLIPS % season_url + '&start=0&rows=' + str(season_menu2)
		_common.add_directory('Clips',  SITE, 'episodes', season_url3)
	_common.set_view('seasons')

def episodes(episode_url = _common.args.url):
	episode_data = _connection.getURL(episode_url, header = {'X-Forwarded-For' : '12.13.14.15'})
	episode_tree = BeautifulSoup(episode_data)
	episode_menu = episode_tree.find_all('article')
	for episode_item in episode_menu:
		show_name = episode_item.find('p', class_ = 'show-name').text
		episode_name = episode_item.find('p', class_ = 'short-title').text
		url = BASE + episode_item.find('a')['href']
		episode_plot = _common.replace_signs(episode_item.find('p', class_ = 'description').text)
		try:
			episode_thumb = episode_item.find('img', class_ = 'thumbnail')['src']
		except:
			episode_thumb = None
		try:
			episode_duration = _common.format_seconds(episode_item.find('span', class_ = 'duration').text.replace('Duration:', ''))
		except:
			episode_duration = -1
		u = sys.argv[0]
		u += '?url="' + urllib.quote_plus(url) + '"'
		u += '&mode="' + SITE + '"'
		u += '&sitemode="play_video"'
		infoLabels = {	'title' : episode_name,
						'plot' : episode_plot,
						'durationinseconds' : episode_duration,
						'tvshowtitle' : show_name }
		_common.add_video(u, episode_name, episode_thumb, infoLabels = infoLabels, quality_mode  = 'list_qualities')
	_common.set_view('episodes')
			
def play_video(video_url = _common.args.url):
	video_data = _connection.getURL(video_url, header = {'X-Forwarded-For' : '12.13.14.15'})
	try:
		video_url2 = re.compile('<meta content="http://media.mtvnservices.com/fb/(.+?).swf" property="og:video"/>').findall(video_data)[0]
	except:
		video_url2 = re.compile("NICK.unlock.uri = '(.+?)';").findall(video_data)[0]
	_main_viacom.play_video(BASE, video_url2)	

def list_qualities(video_url = _common.args.url):
	video_data = _connection.getURL(video_url, header = {'X-Forwarded-For' : '12.13.14.15'})
	try:
		video_url2 = re.compile('<meta content="http://media.mtvnservices.com/fb/(.+?).swf" property="og:video"/>').findall(video_data)[0]
	except:
		video_url2 = re.compile("NICK.unlock.uri = '(.+?)';").findall(video_data)[0]
	return _main_viacom.list_qualities(BASE, video_url2)
