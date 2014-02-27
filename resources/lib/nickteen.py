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

SITE = 'nickteen'
BASE = 'http://www.teennick.com'
BASE2 = 'http://media.nick.com/'
SHOWS = 'http://www.teennick.com/ajax/videos/all-videos?sort=date+desc&start=0&page=1&updateDropdown=true&viewType=collectionAll'
CLIPS = 'http://www.teennick.com/ajax/videos/all-videos/%s?type=videoItem'
FULLEPISODES = 'http://www.teennick.com/ajax/videos/all-videos/%s?type=fullEpisodeItem'

def masterlist():
	master_db = []
	master_data = _connection.getURL(SHOWS)
	master_tree = BeautifulSoup(master_data, 'html.parser')
	master_menu = master_tree.find_all('option')
	master_menu.pop(0)
	for master_item in master_menu:
		master_name = master_item.string
		season_url = master_item['value']
		master_db.append((master_name, SITE, 'seasons', season_url))
	return master_db

def rootlist():
	root_data = _connection.getURL(SHOWS)
	root_tree = BeautifulSoup(root_data, 'html.parser')
	root_menu = root_tree.find_all('option')
	root_menu.pop(0)
	for root_item in root_menu:
		root_name = root_item.string
		season_url = root_item['value']
		_common.add_show(root_name, SITE, 'seasons', season_url)
	_common.set_view('tvshows')

def seasons(season_url = _common.args.url):
	season_data = _connection.getURL(FULLEPISODES % season_url)
	try:
		season_menu = int(BeautifulSoup(season_data).find('div', class_ = 'total-videos').text.split(' ')[0])
	except:
		season_menu = 0
	if season_menu > 0:
		season_url2 = FULLEPISODES % season_url
		_common.add_directory('Full Episodes',  SITE, 'episodes', season_url2)
	season_data2 = _connection.getURL(CLIPS % season_url)
	try:
		season_menu2 = int(BeautifulSoup(season_data2).find('div', class_ = 'total-videos').text.split(' ')[0])
	except:
		season_menu2 = 0
	if season_menu2 > 0:
		season_url3 = CLIPS % season_url
		_common.add_directory('Clips',  SITE, 'episodes', season_url3)
	_common.set_view('seasons')

def episodes(episode_url = _common.args.url):
	episode_data = _connection.getURL(episode_url)
	episode_tree = BeautifulSoup(episode_data, 'html.parser')
	add_videos(episode_tree.find('ul', class_ = 'large-grid-list'))
	pagedata = episode_tree.find('span', class_ = 'pagination-next')
	if pagedata:
		try:
			episodes(episode_url.split('?')[0] + pagedata.a['href'] + '&type=' + episode_url.rsplit('=', 1)[1])
		except:
			pass
	_common.set_view('episodes')	

def add_videos(episode_tree):
	episode_menu = episode_tree.find_all('li', recursive = False)
	for episode_item in episode_menu:
		show_name = _common.args.name
		episode_link = episode_item.h4.a
		episode_name = episode_link.text
		url = BASE + episode_link['href']
		episode_thumb = episode_item.find('img')['src'].split('?')[0]
		episode_plot = episode_item.find('p', class_ = 'description').text
		u = sys.argv[0]
		u += '?url="' + urllib.quote_plus(url) + '"'
		u += '&mode="' + SITE + '"'
		u += '&sitemode="play_video"'
		infoLabels = {	'title' : episode_name,
						'plot' : episode_plot,
						'tvshowtitle' : show_name }
		_common.add_video(u, episode_name, episode_thumb, infoLabels = infoLabels, quality_mode  = 'list_qualities')
			
def play_video(video_url = _common.args.url):
	video_data = _connection.getURL(video_url, header = {'X-Forwarded-For' : '12.13.14.15'})
	try:
		video_url2 = re.compile('<meta content="http://media.mtvnservices.com/fb/(.+?).swf" property="og:video"/>').findall(video_data)[0]
	except:
		video_url2 = re.compile("NICK.unlock.uri = '(.+?)';").findall(video_data)[0]
	_main_viacom.play_video(BASE, video_url2, media_base = BASE2)	

def list_qualities(video_url = _common.args.url):
	video_data = _connection.getURL(video_url, header = {'X-Forwarded-For' : '12.13.14.15'})
	try:
		video_url2 = re.compile('<meta content="http://media.mtvnservices.com/fb/(.+?).swf" property="og:video"/>').findall(video_data)[0]
	except:
		video_url2 = re.compile("NICK.unlock.uri = '(.+?)';").findall(video_data)[0]
	return _main_viacom.list_qualities(BASE, video_url2, media_base = BASE2)

