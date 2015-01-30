#!/usr/bin/python
# -*- coding: utf-8 -*-
import _common
import _connection
import _m3u8
import base64
import os
import re
import simplejson
import sys
import time
import urllib
import xbmc
import xbmcaddon
import xbmcgui
import xbmcplugin
from bs4 import BeautifulSoup, SoupStrainer

addon = xbmcaddon.Addon()
player = _common.XBMCPlayer()
pluginHandle = int(sys.argv[1])

CATERGORIES = ['Series', 'Featured', 'Shows']

def masterlist(SITE, SHOWS):
	master_db = []
	master_data = _connection.getURL(SHOWS)
	master_menu = simplejson.loads(master_data)['entries']
	for master_item in master_menu:
		master_name = master_item['title']
		master_url = master_item['plcategory$fullTitle']
		if len(master_url.split('/')) == 2 and master_url.split('/')[0] in CATERGORIES:
			master_db.append((master_name, SITE, 'seasons', master_url))
	return master_db

def seasons(SITE, FULLEPISODES, CLIPS, FULLEPISODESWEB = None):
	season_urls = _common.args.url
	for season_url in season_urls.split(','):
		season_data = _connection.getURL(FULLEPISODES % urllib.quote_plus(season_url) + '&range=0-1')
		try:
			season_menu = int(simplejson.loads(season_data)['totalResults'])
		except:
			season_menu = 0
		if season_menu > 0:
			season_url2 = FULLEPISODES % urllib.quote_plus(season_url) + '&range=0-' + str(season_menu)
			_common.add_directory('Full Episodes',  SITE, 'episodes', season_url2)
		elif FULLEPISODESWEB:
			show = season_url.split('/')[-1].replace(' ', '')
			web_data = _connection.getURL(FULLEPISODESWEB % show)
			web_tree = BeautifulSoup(web_data, 'html.parser')
			all = len(web_tree.find_all('div', class_ = 'view-mode-vid_teaser_show_episode'))
			auth = len(web_tree.find_all('div', class_ = 'tve-video-auth'))
			if all > auth:
				_common.add_directory('Full Episodes',  SITE, 'webepisodes', FULLEPISODESWEB % show)
		season_data2 = _connection.getURL(CLIPS % urllib.quote_plus(season_url) + '&range=0-1')
		try:
			season_menu2 = int(simplejson.loads(season_data2)['totalResults'])
		except:
			season_menu2 = 0
		if season_menu2 > 0:
			season_url3 = CLIPS % urllib.quote_plus(season_url) + '&range=0-' + str(season_menu2)
			if ',' in season_urls:
				_common.add_directory('Clips %s'%season_url,  SITE, 'episodes', season_url3)
			else:
				_common.add_directory('Clips',  SITE, 'episodes', season_url3)
	_common.set_view('seasons')

def episodes(SITE, quality = True):
	episode_url = _common.args.url
	episode_data = _connection.getURL(episode_url)
	episode_menu = simplejson.loads(episode_data)['entries']
	for i, episode_item in enumerate(episode_menu):
		default_mediacontent = None
		for mediacontent in episode_item['media$content']:
			if (mediacontent['plfile$isDefault'] == True) and (mediacontent['plfile$format'] == 'MPEG4'):
				default_mediacontent = mediacontent
			elif (mediacontent['plfile$format'] == 'MPEG4'):
				mpeg4_mediacontent = mediacontent
		if default_mediacontent is None:
			default_mediacontent = mpeg4_mediacontent
		url = default_mediacontent['plfile$url']
		episode_duration = int(episode_item['media$content'][0]['plfile$duration'])
		episode_plot = episode_item['description']
		episode_airdate = _common.format_date(epoch = episode_item['pubDate']/1000)
		episode_name = episode_item['title']
		try:
			season_number = int(episode_item['pl' + str(i + 1) + '$season'][0])
		except:
			try:
				season_number = int(episode_item['nbcu$seasonNumber'])
			except:
				season_number = -1
		try:
			episode_number = int(episode_item['pl' + str(i + 1) + '$episode'][0])
		except:
			try:
				episode_number = int(episode_item['nbcu$episodeNumber'])
			except:
				episode_number = -1
		try:
			episode_thumb = episode_item['plmedia$defaultThumbnailUrl']
		except:
			episode_thumb = None
		u = sys.argv[0]
		u += '?url="' + urllib.quote_plus(url) + '"'
		u += '&mode="' + SITE + '"'
		u += '&sitemode="play_video"'
		infoLabels={	'title' : episode_name,
						'durationinseconds' : episode_duration,
						'season' : season_number,
						'episode' : episode_number,
						'plot' : episode_plot,
						'premiered' : episode_airdate }
		if quality:
			_common.add_video(u, episode_name, episode_thumb, infoLabels = infoLabels, quality_mode  = 'list_qualities')
		else:
			_common.add_video(u, episode_name, episode_thumb, infoLabels = infoLabels)
	_common.set_view('episodes')

def list_qualities():
	exception = False
	video_url = _common.args.url
	bitrates = []
	video_data = _connection.getURL(video_url)
	video_tree = BeautifulSoup(video_data, 'html.parser')
	try:
		video_rtmp = video_tree.meta['base']
	except:
		video_rtmp = None
	if 'link.theplatform.com' not in video_url:
		video_tree =  BeautifulSoup(video_data, 'html.parser')
		player_url = 'http:' + video_tree.find('div', class_ = 'video-player-wrapper').iframe['src']
		player_data = _connection.getURL(player_url)
		player_tree =  BeautifulSoup(player_data, 'html.parser')
		video_url = player_tree.find('link', type = "application/smil+xml")['href']
		video_url = video_url + '&format=SMIL'
		video_data = _connection.getURL(video_url)
	if video_rtmp is not None:
		for video_index in video_rtmp:
			bitrate = int(video_index['system-bitrate'])
			display = int(bitrate)
			bitrates.append((display, bitrate))
	else:
		video_data = _connection.getURL(video_url + '&manifest=m3u')
		video_tree = BeautifulSoup(video_data, 'html.parser')
		if  video_tree.find('param', attrs = {'name' : 'isException', 'value' : 'true'}) is None:
			video_url2 = video_tree.seq.find_all('video')[0]
			video_url3 = video_url2['src']
			video_data2 = _connection.getURL(video_url3)
			video_url4 = _m3u8.parse(video_data2)
			for video_index in video_url4.get('playlists'):
				bitrate = int(video_index.get('stream_info')['bandwidth'])
				try:
					codecs =  video_index.get('stream_info')['codecs']
				except:
					codecs = ''
				display = int(bitrate) / 1024
				bitrates.append((display, bitrate))
		else:
			exception = True
	if  not exception:
		return bitrates
	else:
		_common.show_exception(video_tree.ref['title'], video_tree.ref['abstract'])

def play_video():
	try:
		qbitrate = _common.args.quality
	except:
		qbitrate = None
	exception = False
	video_url = _common.args.url
	hbitrate = -1
	lbitrate = -1
	sbitrate = int(addon.getSetting('quality')) * 1024
	closedcaption = None
	video_data = _connection.getURL(video_url)
	if 'link.theplatform.com' not in video_url:
		video_tree =  BeautifulSoup(video_data, 'html.parser')
		player_url = 'http:' + video_tree.find('div', class_ = 'video-player-wrapper').iframe['src']
		player_data = _connection.getURL(player_url)
		player_tree =  BeautifulSoup(player_data, 'html.parser')
		video_url = player_tree.find('link', type = "application/smil+xml")['href']
		video_url = video_url + '&format=SMIL'
		video_data = _connection.getURL(video_url)
	video_tree = BeautifulSoup(video_data, 'html.parser')
	video_rtmp = video_tree.meta
	playpath_url = None
	lplaypath_url = None
	try:
		base_url = video_rtmp['base']
	except:
		base_url = None
	if base_url is not None:
		if qbitrate is None:
			video_url2 = video_tree.switch.find_all('video')
			for video_index in video_url2:
				bitrate = int(video_index['system-bitrate'])
				if bitrate < lbitrate or lbitrate == -1:
					lbitrate = bitrate
					lplaypath_url = video_index['src']	
				if bitrate > hbitrate and bitrate <= sbitrate:
					hbitrate = bitrate
					playpath_url = video_index['src']	
			if playpath_url is None:
				playpath_url = lplaypath_url
		else:
			playpath_url = video_tree.switch.find('video', attrs = {'system-bitrate' : qbitrate})['src']
		if '.mp4' in playpath_url:
			playpath_url = 'mp4:'+ playpath_url
		else:
			playpath_url = playpath_url.replace('.flv','')
		finalurl = base_url +' playpath=' + playpath_url + ' swfurl=' + SWFURL + ' swfvfy=true'
		player._localHTTPServer = False
	else:
		video_data = _connection.getURL(video_url + '&manifest=m3u&Tracking=true&Embedded=true&formats=F4M,MPEG4')
		video_tree = BeautifulSoup(video_data, 'html.parser')
		try:
			closedcaption = video_tree.textstream['src']
			player._subtitles_Enabled = True
		except:
			pass
		if (addon.getSetting('enablesubtitles') == 'true') and (closedcaption is not None):
				convert_subtitles(closedcaption)
		if  video_tree.find('param', attrs = {'name' : 'isException', 'value' : 'true'}) is None:
			video_url2 = video_tree.seq.find_all('video')[0]
			video_url3 = video_url2['src']
			video_data2 = _connection.getURL(video_url3, savecookie = True)
			video_url5 = _m3u8.parse(video_data2)
			for video_index in video_url5.get('playlists'):
				bitrate = int(video_index.get('stream_info')['bandwidth'])
				try:
					codecs =  video_index.get('stream_info')['codecs']
				except:
					codecs = ''
				if qbitrate is None:
					if (bitrate < lbitrate or lbitrate == -1):
						lbitrate = bitrate
						lplaypath_url =  video_index.get('uri')
					if (bitrate > hbitrate and bitrate <= sbitrate):
						hbitrate = bitrate
						playpath_url = video_index.get('uri')
				elif  bitrate == qbitrate:
					playpath_url =  video_index.get('uri')
			if playpath_url is None:
				playpath_url = lplaypath_url
			if 'https' not in playpath_url:
				player._localHTTPServer = False
				finalurl = playpath_url
			else:
				m3u_data = _connection.getURL(playpath_url, loadcookie = True)
				key_url = re.compile('URI="(.*?)"').findall(m3u_data)[0]
				key_data = _connection.getURL(key_url, loadcookie = True)		
				key_file = open(_common.KEYFILE, 'wb')
				key_file.write(key_data)
				key_file.close()
				video_url5 = re.compile('(http:.*?)\n').findall(m3u_data)
				proxy_config = _common.proxyConfig()
				for i, video_item in enumerate(video_url5):
					newurl = base64.b64encode(video_item)
					newurl = urllib.quote_plus(newurl)
					m3u_data = m3u_data.replace(video_item, 'http://127.0.0.1:12345/proxy/' + newurl + '/' + proxy_config)
				filestring = 'XBMC.RunScript(' + os.path.join(_common.LIBPATH,'_proxy.py') + ', 12345)'
				xbmc.executebuiltin(filestring)
				time.sleep(20)
				m3u_data = m3u_data.replace(key_url, 'http://127.0.0.1:12345/play.key')
				playfile = open(_common.PLAYFILE, 'w')
				playfile.write(m3u_data)
				playfile.close()
				finalurl =  _common.PLAYFILE
		else:
			exception = True
	if  not exception:
		item = xbmcgui.ListItem(path = finalurl)
		if qbitrate is not None:
			item.setThumbnailImage(_common.args.thumb)
			item.setInfo('Video', {	'title' : _common.args.name,
							'season' : _common.args.season_number,
							'episode' : _common.args.episode_number,
							'TVShowTitle' : _common.args.show_title})
		xbmcplugin.setResolvedUrl(pluginHandle, True, item)
		while player.is_active:
			player.sleep(250)
	else:
		_common.show_exception(video_tree.ref['title'], video_tree.ref['abstract'])

def clean_subs(data):
	br = re.compile(r'<br.*?>')
	tag = re.compile(r'<.*?>')
	space = re.compile(r'\s\s\s+')
	apos = re.compile(r'&amp;apos;')
	sub = br.sub('\n', data)
	sub = tag.sub(' ', sub)
	sub = space.sub(' ', sub)
	sub = apos.sub('\'', sub)
	return sub

def convert_subtitles(closedcaption):
	str_output = ''
	subtitle_data = _connection.getURL(closedcaption, connectiontype = 0)
	subtitle_data = BeautifulSoup(subtitle_data, 'html.parser', parse_only = SoupStrainer('div'))
	lines = subtitle_data.find_all('p')
	for i, line in enumerate(lines):
		if line is not None:
			sub = clean_subs(_common.smart_utf8(line))
			start_time_rest, start_time_msec = line['begin'].rsplit(':',1)
			start_time = _common.smart_utf8(start_time_rest + ',' + start_time_msec)
			try:
				end_time_rest, end_time_msec = line['end'].rsplit(':',1)
				end_time = _common.smart_utf8(end_time_rest + ',' + end_time_msec)
			except:
				continue
			str_output += str(i + 1) + '\n' + start_time + ' --> ' + end_time + '\n' + sub + '\n\n'
	file = open(_common.SUBTITLE, 'w')
	file.write(str_output)
	file.close()
