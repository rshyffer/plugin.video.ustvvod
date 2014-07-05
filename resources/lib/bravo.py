#!/usr/bin/python
# -*- coding: utf-8 -*-
import _addoncompat
import _common
import _connection
import _m3u8
import simplejson
import sys
import re
import urllib
import xbmc
import xbmcgui
import xbmcplugin
from bs4 import BeautifulSoup, SoupStrainer

pluginHandle = int(sys.argv[1])

SITE = 'bravo'
NAME = 'Bravo'
DESCRIPTION = "With more breakout stars and critically-acclaimed original series than any other network on cable, Bravo's original programming - from hot cuisine to haute couture - delivers the best in food, fashion, beauty, design and pop culture to the most engaged and upscale audience in cable. Consistently one of the fastest growing top 20 ad-supported cable entertainment networks, Bravo continues to translate buzz into reality with critically-acclaimed breakout creative competition and docu-series, including the Emmy and James Beard Award-winning No. 1 food show on cable \"Top Chef,\" two-time Emmy Award winner \"Kathy Griffin: My Life on the D-List,\" the 14-time Emmy nominated \"Inside the Actors Studio,\" the hit series \"Shear Genius,\" \"Top Chef Masters,\" \"Flipping Out,\" \"The Rachel Zoe Project,\" \"Tabatha's Salon Takeover,\" \"Million Dollar Listing,\" \"The Millionaire Matchmaker,\" and the watercooler sensation that is \"The Real Housewives\" franchise. Bravo reaches its incredibly unique audience through every consumer touch point and across all platforms on-air, online and on the go, providing the network\'s highly-engaged fans with a menu of options to experience the network in a four-dimensional manner. Bravo is a program service of NBC Universal Cable Entertainment, a division of NBC Universal one of the world\'s leading media and entertainment companies in the development, production, and marketing of entertainment, news and information to a global audience. Bravo has been an NBC Universal cable network since December 2002 and was the first television service dedicated to film and the performing arts when it launched in December 1980. For more information visit www.bravotv.com"
SHOWS = 'http://www.bravotv.com/shows'
CLIPS = 'http://feed.theplatform.com/f/PHSl-B/QiuoTr7I1m13?count=true&form=json&byCustomValue={fullEpisode}{false},{show}{%s}'
FULLEPISODES = 'http://feed.theplatform.com/f/PHSl-B/QiuoTr7I1m13?count=true&form=json&byCustomValue={fullEpisode}{true},{show}{%s}'
SWFURL = 'http://www.bravotv.com/_tp/pdk/swf/flvPlayer.swf'

def masterlist():
	master_db = []
	master_doubles = []
	master_dict = {}
	master_data = _connection.getURL(SHOWS)
	master_menu = BeautifulSoup(master_data, 'html.parser').find_all('div', class_ = 'title')
	for master_item in master_menu:
		master_name = master_item.text.strip()
		if master_name not in master_doubles:
			tvdb_name = _common.get_show_data(master_name,SITE, 'seasons')[-1]
			if tvdb_name not in master_dict.keys():
				master_dict[tvdb_name] = master_name
			else:
				master_dict[tvdb_name] = master_dict[tvdb_name] + ',' + master_name
			master_doubles.append(master_name)
	for master_name in master_dict:
		season_url = master_dict[master_name]
		master_db.append((master_name, SITE, 'seasons', season_url))
	return master_db

def seasons(season_urls = _common.args.url):
	for season_url in season_urls.split(','):
		season_data = _connection.getURL(FULLEPISODES % urllib.quote_plus(season_url) + '&range=0-1')
		try:
			season_menu = int(simplejson.loads(season_data)['totalResults'])
		except:
			season_menu = 0
		if season_menu > 0:
			season_url2 = FULLEPISODES % urllib.quote_plus(season_url) + '&range=0-' + str(season_menu)
			_common.add_directory('Full Episodes',  SITE, 'episodes', season_url2)
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

def episodes(episode_url = _common.args.url):
	episode_data = _connection.getURL(episode_url)
	episode_menu = simplejson.loads(episode_data)['entries']
	for i, episode_item in enumerate(episode_menu):
		url = episode_item['media$content'][0]['plfile$url']
		episode_duration = int(episode_item['media$content'][0]['plfile$duration'])
		episode_plot = episode_item['description']
		episode_airdate = _common.format_date(epoch = episode_item['pubDate']/1000)
		episode_name = episode_item['title']
		try:
			season_number = int(episode_item['pl' + str(i + 1) + '$season'][0])
		except:
			season_number = -1
		try:
			episode_number = int(episode_item['pl' + str(i + 1) + '$episode'][0])
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
		_common.add_video(u, episode_name, episode_thumb, infoLabels = infoLabels)
	_common.set_view('episodes')

def play_video(video_url = _common.args.url):
	hbitrate = -1
	sbitrate = int(_addoncompat.get_setting('quality')) * 1024
	closedcaption = None
	video_data = _connection.getURL(video_url)
	video_tree = BeautifulSoup(video_data, 'html.parser')
	video_rtmp = video_tree.meta
	if video_rtmp is not None:
		base_url = video_rtmp['base']
		video_url2 = video_tree.switch.find_all('video')
		for video_index in video_url2:
			bitrate = int(video_index['system-bitrate'])
			if bitrate > hbitrate and bitrate <= sbitrate:
				hbitrate = bitrate
				playpath_url = video_index['src']	
				if '.mp4' in playpath_url:
					playpath_url = 'mp4:'+ playpath_url
				else:
					playpath_url = playpath_url.replace('.flv','')
				finalurl = base_url +' playpath=' + playpath_url + ' swfurl=' + SWFURL + ' swfvfy=true'
	else:
		video_data = _connection.getURL(video_url + '&manifest=m3u')
		video_tree = BeautifulSoup(video_data)
		try:
			closedcaption = video_tree.textstream['src']
		except:
			pass
		if (_addoncompat.get_setting('enablesubtitles') == 'true') and (closedcaption is not None):
				convert_subtitles(closedcaption)
		video_url2 = video_tree.seq.find_all('video')[0]
		video_url3 = video_url2['src'].replace('bravohls-f.','bravohls-i.')
		video_url4 = video_url3.split('/')[-1]
		video_data2 = _connection.getURL(video_url3)
		video_url5 = _m3u8.parse(video_data2)
		for video_index in video_url5.get('playlists'):
			bitrate = int(video_index.get('stream_info')['bandwidth'])
			if bitrate > hbitrate and bitrate <= sbitrate:
				hbitrate = bitrate
				finalurl = video_url3.replace(video_url4, video_index.get('uri'))
	xbmcplugin.setResolvedUrl(pluginHandle, True, xbmcgui.ListItem(path = finalurl))
	if (_addoncompat.get_setting('enablesubtitles') == 'true') and (closedcaption is not None):
		while not xbmc.Player().isPlaying():
			xbmc.sleep(100)
		xbmc.Player().setSubtitles(_common.SUBTITLE)

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
