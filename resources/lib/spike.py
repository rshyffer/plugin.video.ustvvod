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

SITE = 'spike'
NAME = 'Spike TV'
DESCRIPTION = "Spike TV knows what guys like. The brand speaks to the bold, adventuresome side of men with action-packed entertainment, including a mix of comedy, blockbuster movies, sports, innovative originals and live events. Popular shows like The Ultimate Fighter, TNA iMPACT!, Video Game Awards, DEA, MANswers, MXC, and CSI: Crime Scene Investigation, plus the Star Wars and James Bond movie franchises, position Spike TV as the leader in entertainment for men."
BASE = 'http://www.spike.com'
SHOWS = 'http://www.spike.com/shows/'
MP4URL = 'http://mtvnmobile.vo.llnwd.net/kip0/_pxn=0+_pxK=18639/44620/mtvnorigin'

def masterlist():
	master_dict = {}
	master_db = []
	master_data = _connection.getURL(SHOWS)
	master_tree = BeautifulSoup(master_data, 'html5lib')
	master_section = master_tree.find_all('div', class_ = 'primetime_and_originals')
	for section in master_section:
		master_menu = section.find_all('a', text = True)
		for master_item in master_menu:
			master_name = master_item.text
			tvdb_name = _common.get_show_data(master_name,SITE, 'seasons')[-1]
			season_url = BASE + master_item['href']
			if tvdb_name not in master_dict.keys():
				master_dict[tvdb_name] = season_url
			else:
				master_dict[tvdb_name] = master_dict[tvdb_name] + ',' + season_url
	for master_name, season_url in master_dict.iteritems():	
		master_db.append((master_name, SITE, 'seasons', season_url))
	return master_db

def seasons(season_url = _common.args.url):
	if ',' in season_url:
		multiSeason = True
	else:
		multiSeason = False
	for season_url in season_url.split(','):
		season_data = _connection.getURL(season_url)
		season_tree = BeautifulSoup(season_data, 'html5lib')
		season_item = season_tree.find('a', text = re.compile('Episode( Guide)?'))
		if season_item is not None:
			if BASE not in season_item['href']:
				season_data2 = _connection.getURL(BASE + season_item['href'])
			else:
				season_data2 = _connection.getURL(season_item['href'])
			season_tree = BeautifulSoup(season_data2, 'html5lib')
			try:
				season_menu2 = season_tree.find('ul', class_ = 'season_navigation').find_all('a')
				for season_item2 in season_menu2:
					season_name = season_item2.text
					season_url2 = season_item2['href']
					_common.add_directory(season_name, SITE, 'episodes', season_url2)
			except:
				pass	
		season_item = season_tree.find('a', text = 'Video Clips')	
		if season_item is not None:
			season_name2 = season_item.text
			if BASE not in season_item['href']:
				season_url3 = BASE + season_item['href']
			else:
				season_url3 = season_item['href']
			if not multiSeason:
				_common.add_directory(season_name2, SITE, 'episodes', season_url3)
			else:
				title = season_tree.find('title').string.split('|')[0].strip()
				_common.add_directory(title + ' ' + season_name2, SITE, 'episodes', season_url3)
	_common.set_view('seasons')

def episodes(episode_url = _common.args.url):
	episode_data = _connection.getURL(episode_url)
	episode_tree = BeautifulSoup(episode_data, 'html5lib')
	if 'Video Clips' in _common.args.name :
		episode_url2 = episode_tree.find('div', class_ = 'v_content')['data-url']
		if episode_tree.find('div', class_ = 'pagination') is not None:
			episode_count = int(episode_tree.find('div', class_ = 'result').text.rsplit(' ', 1)[1].strip())
			episode_items, episode_rest = divmod(episode_count, 10)
			if episode_rest > 0:
				episode_items = episode_items + 1
			if episode_items > int(_addoncompat.get_setting('maxpages')):
				episode_items = int(_addoncompat.get_setting('maxpages'))
			for episode_item in range(episode_items):
					episode_data2 = _connection.getURL(episode_url2 + '?page=' + str(episode_item + 1))
					episode_tree2 = BeautifulSoup(episode_data2)
					add_clips(episode_tree2)
		else:
			episode_data2 = _connection.getURL(episode_url2 + '?page=1')
			episode_tree2 = BeautifulSoup(episode_data2)
			add_clips(episode_tree2)
	else:
		try:
			add_fullepisodes(episode_tree, int(_common.args.name.split(' ')[1]))
		except:
			try:
				add_fullepisodes(episode_tree, int(_common.args.name))
			except:
				add_fullepisodes(episode_tree)
		if episode_tree.find('div', class_ = 'pagination') is not None:
			episode_items2 = episode_tree.find('div', class_ = 'pagination').find_all('a')
			for episode_item2 in episode_items2:
				if (episode_item2.text != 'Next'):
					episode_data3 = _connection.getURL(episode_item2['href'])
					episode_tree3 = BeautifulSoup(episode_data3)
					try:
						add_fullepisodes(episode_tree3, int(_common.args.name.split(' ')[1]))
					except:
						try:
							add_fullepisodes(episode_tree3, int(_common.args.name))
						except:
							add_fullepisodes(episode_tree3)
	_common.set_view('episodes')

def add_fullepisodes(episode_tree, season_number = -1):
	try:
		episode_menu = episode_tree.find_all('div', class_ = 'episode_guide')
		for episode_item in episode_menu:
			episode_name = _common.replace_signs(episode_item.find('img')['title'])
			episode_airdate = _common.format_date(episode_item.find('p', class_ = 'aired_available').contents[1].strip(), '%m/%d/%Y', '%d.%m.%Y')
			episode_plot = _common.replace_signs(episode_item.find('p', class_ = False).text)
			episode_thumb = episode_item.find('img')['src'].split('?')[0]
			url = episode_item.find('div', class_ = 'thumb_image').a['href']
			try:
				episode_number = int(episode_item.find('a', class_ = 'title').contents[1].split('Episode ' + season_number)[1])
			except:
				try:
					episode_number = int(url.split('-0')[1])
				except:
					episode_number = -1
			if season_number == -1:
				season_number = int(url.split('-')[-3])
			u = sys.argv[0]
			u += '?url="' + urllib.quote_plus(url) + '"'
			u += '&mode="' + SITE + '"'
			u += '&sitemode="play_video"'
			infoLabels = {	'title' : episode_name,
							'season' : season_number,
							'episode' : episode_number,
							'plot' : episode_plot,
							'premiered' : episode_airdate }
			_common.add_video(u, episode_name, episode_thumb, infoLabels = infoLabels, quality_mode  = 'list_qualities')
	except:
		pass

def add_clips(episode_tree):
	try:
		episode_menu = episode_tree.find_all('div', class_ = 'block')
		for episode_item in episode_menu:
			episode_name = _common.replace_signs(episode_item.find('h3').a.text)
			episode_plot = _common.replace_signs(episode_item.find('p', class_ = False).text)
			episode_thumb = episode_item.find('img')['src'].split('?')[0]
			url = episode_item.find('div', class_ = 'thumb_area').a['href']
			try:
				episode_airdate = episode_item.find('div', class_ = 'details').contents[0].split(' ', 1)[1].strip()
				episode_airdate = _common.format_date(episode_airdate, '%B %d, %Y', '%d.%m.%Y')
			except:
				episode_airdate = -1
			try:
				episode_duration = _common.format_seconds(episode_item.find('h3').small.text.replace(')', '').replace('(', ''))
			except:
				episode_duration = -1
			u = sys.argv[0]
			u += '?url="' + urllib.quote_plus(url) + '"'
			u += '&mode="' + SITE + '"'
			u += '&sitemode="play_video"'
			infoLabels = {	'title' : episode_name,
							'durationinseconds' : episode_duration,
							'plot' : episode_plot,
							'premiered' : episode_airdate }
			_common.add_video(u, episode_name, episode_thumb, infoLabels = infoLabels)
	except:
		pass
		
def play_video(video_uri = _common.args.url):
	video_data = _connection.getURL(video_uri)
	video_url = BeautifulSoup(video_data, 'html5lib').find('div', id = 'video_player_box')['data-mgid']
	_main_viacom.play_video(BASE, video_url)	
	
def list_qualities(video_url = _common.args.url):
	video_data = _connection.getURL(video_url)
	video_url = BeautifulSoup(video_data, 'html5lib').find('div', id = 'video_player_box')['data-mgid']
	return _main_viacom.list_qualities(BASE, video_url)
