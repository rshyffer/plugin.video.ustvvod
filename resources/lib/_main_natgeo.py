#!/usr/bin/python
# -*- coding: utf-8 -*-
import _addoncompat
import _common
import _connection
import _m3u8
import re
import sys
import urllib
import xbmcgui
import xbmcplugin
from bs4 import BeautifulSoup, SoupStrainer

pluginHandle = int(sys.argv[1])

BASE = 'http://video.nationalgeographic.com'

def masterlist(SITE, SHOWS, SPECIALS):
	master_dict = {}
	master_db = []
	for master_url in (SHOWS, SPECIALS):
		master_data = _connection.getURL(master_url)
		master_tree = BeautifulSoup(master_data, 'html.parser', parse_only = SoupStrainer('div', id = 'content'))
		master_menu = master_tree.find_all('div', class_ = 'natgeov-cat-group')
		for master_item in master_menu:
			secured_episodes = len(master_item.find_all('img', src = re.compile('AUTH')))
			total_episodes = len(master_item.find_all('img'))
			if secured_episodes != total_episodes:
				master_name = master_item.h3.text.split('(')[0].strip()
				season_url = BASE + master_item.a['href']
				master_dict[master_name] = season_url
	for master_name, season_url in master_dict.iteritems():
		master_db.append((master_name, SITE, 'episodes', season_url))
	return master_db

def rootlist(SITE, SHOWS, SPECIALS):
	root_dict = {}
	for root_url in (SHOWS, SPECIALS):
		root_data = _connection.getURL(root_url)
		root_tree = BeautifulSoup(root_data, 'html.parser', parse_only = SoupStrainer('div', id = 'content'))
		root_menu = root_tree.find_all('div', class_ = 'natgeov-cat-group')
		for root_item in root_menu:
			secured_episodes = len(root_item.find_all('img', src = re.compile('AUTH')))
			total_episodes = len(root_item.find_all('img'))
			if secured_episodes != total_episodes:
				root_name = root_item.h3.text.split('(')[0].strip()
				season_url = BASE + root_item.a['href']
				root_dict[root_name] = season_url
	for root_name, season_url in root_dict.iteritems():
		_common.add_show(root_name, SITE, 'episodes', season_url)
	_common.set_view('tvshows')

def episodes(SITE):
	episode_url = _common.args.url
	episode_data = _connection.getURL(episode_url)
	episode_tree = BeautifulSoup(episode_data)
	add_videos(episode_tree, SITE)
	pagedata = re.compile('new Paginator\((.+?),(.+?)\)').findall(episode_data)
	if pagedata:
		total   = int(pagedata[0][0])
		current = int(pagedata[0][1])
		if total > 1:
			for page in range(1,total):
				episode_data = _connection.getURL(episode_url + '/' + str(page) + '/')
				episode_tree = BeautifulSoup(episode_data)
				add_videos(episode_tree, SITE)
	_common.set_view('episodes')

def add_videos(episode_tree, SITE):
	episode_menu = episode_tree.find_all('div', class_ = 'vidthumb')
	show_name = episode_tree.find('h3', id = 'natgeov-section-title').text
	show_name = show_name.split('(')[0].strip()
	for episode_item in episode_menu:
		if episode_item.find(class_ = 'video-locked') is None:
			episode_name = episode_item.a['title']
			episode_thumb = episode_item.img['src'].split('url=')[1]
			try:
				episode_duration = _common.format_seconds(episode_item.span.text.strip())
			except:
				episode_duration = -1
			url = BASE + episode_item.a['href']
			u = sys.argv[0]
			u += '?url="'+urllib.quote_plus(url)+'"'
			u += '&mode="' + SITE + '"'
			u += '&sitemode="play_video"'
			infoLabels = {	'title' : episode_name,
							'durationinseconds' : episode_duration,
							'TVShowTitle' : show_name }
			_common.add_video(u, episode_name, episode_thumb, infoLabels = infoLabels, quality_mode = 'list_qualities')

def play_video(SITE):
	video_url = _common.args.url
	try:
		qbitrate = _common.args.quality
	except:
		qbitrate = None
	hbitrate = -1
	lbitrate = -1
	sbitrate = int(_addoncompat.get_setting('quality'))
	video_data = _connection.getURL(video_url)
	smil_url =  re.compile("window.video_auth_playlist_url = '(.*)'").findall(video_data)[0]
	smil_data = _connection.getURL(smil_url + '&manifest=m3u')
	video_tree2 = BeautifulSoup(smil_data)
	video_url3 = video_tree2.video['src']
	video_data3 = _connection.getURL(video_url3)
	video_url4 = _m3u8.parse(video_data3)
	video_url5 = None
	for video_index in video_url4.get('playlists'):
		bitrate = int(video_index.get('stream_info')['bandwidth'])
		if qbitrate is None:
			try:
				codecs =  video_index.get('stream_info')['codecs']
			except:
				codecs = ''
			if (bitrate < lbitrate or lbitrate == -1) and 'mp4a.40.2' != codecs:
						lbitrate = bitrate
						lvideo_url5 = video_index.get('uri')
			if bitrate > hbitrate and bitrate <= (sbitrate * 1000) and codecs != 'mp4a.40.2':
				hbitrate = bitrate
				video_url5 = video_index.get('uri')
		elif  bitrate == qbitrate:
				video_url5 = video_index.get('uri')
	if video_url5 is None:
		video_url5 = lvideo_url5
	finalurl = video_url3.rsplit('/',1)[0] + '/' + video_url5
	item = xbmcgui.ListItem(path = finalurl)
	if qbitrate is not None:
		item.setThumbnailImage(_common.args.thumb)
		item.setInfo('Video', {	'title' : _common.args.name,
						'season' : _common.args.season_number,
						'episode' : _common.args.episode_number,
						'TVShowTitle' : _common.args.show_title})
	xbmcplugin.setResolvedUrl(pluginHandle, True, item)

def list_qualities(SITE):
	video_url = _common.args.url
	bitrates = []
	video_data = _connection.getURL(video_url)
	smil_url =  re.compile("window.video_auth_playlist_url = '(.*)'").findall(video_data)[0]
	smil_data = _connection.getURL(smil_url + '&manifest=m3u')
	video_tree2 = BeautifulSoup(smil_data)
	video_url3 = video_tree2.video['src']
	video_data3 = _connection.getURL(video_url3)
	video_url4 = _m3u8.parse(video_data3)
	for video_index in video_url4.get('playlists'):
		try:
			codecs =  video_index.get('stream_info')['codecs']
		except:
			codecs = ''
		if  codecs != 'mp4a.40.2':
			bitrate = int(video_index.get('stream_info')['bandwidth'])
			display = int(bitrate) / 1000
			bitrates.append((display, bitrate))
	return bitrates
