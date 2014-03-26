#!/usr/bin/python
# -*- coding: utf-8 -*-
import _addoncompat
import _common
import _connection
import _m3u8
import base64
import coveapi
import simplejson
import sys
import re
import urllib
import xbmc
import xbmcgui
import xbmcplugin
from bs4 import BeautifulSoup, SoupStrainer

pluginHandle = int (sys.argv[1])

SITE = 'pbs'
NAME = 'PBS'
DESCRIPTION = "PBS and our member stations are America\'s largest classroom, the nation\'s largest stage for the arts and a trusted window to the world. In addition, PBS's educational media helps prepare children for success in school and opens up the world to them in an age-appropriate way."
SHOWS = 'http://video.pbs.org/programs/list'
SWFURL = 'http://www-tc.pbs.org/video/media/swf/PBSPlayer.swf?video=%s&player=viral'
CLOSEDCAPTION = 'http://video.pbs.org/videoInfo/%s/?format=jsonp&callback=video_info'
KEY = 'RnJlZUNhYmxlLTgxMzQyMmE5LTg0YWMtNDdjYy1iYzVhLTliMDZhY2NlM2I2YQ=='
SECRET = 'MDEyYzcxMDgtNWJiNS00YmFlLWI1MWYtMDRkMTIzNGZjZWRk'
TYPES = ['Episode', 'Segment', 'Clip', 'Promotion', 'Interstitial', 'Other']

cove = coveapi.connect(base64.b64decode(KEY), base64.b64decode(SECRET))

def masterlist():
	master_start = 0
	master_count = 200
	master_db = []
	master_check = []
	master_menu = simplejson.loads(_connection.getURL(SHOWS, header = {'X-Requested-With' : 'XMLHttpRequest'}))
	for master_item in master_menu.itervalues():
		for master_item in master_item:
			master_check.append(master_item['title'])
	while master_start < master_count:
		master_data = cove.programs.filter(fields = 'mediafiles', order_by = 'title', limit_start = master_start)
		master_menu = master_data['results']
		master_count = master_data['count']
		master_stop = master_data['stop']
		del master_data
		for master_item2 in master_menu:
			if master_item2['website'] is None:
				master_website = ''
			else:
				master_website = master_item2['website']
			if master_item2['title'] in master_check and ('pbskids.org' not in master_website):
				master_name = _common.smart_utf8(master_item2['title'])
				season_url = re.compile('/cove/v1/programs/(.*?)/').findall(master_item2['resource_uri'])[0]
				master_db.append((master_name, SITE, 'seasons', season_url))
		master_start = master_stop
	return master_db

def rootlist():
	root_start = 0
	root_count = 200
	root_check = []
	root_menu = simplejson.loads(_connection.getURL(SHOWS, header = {'X-Requested-With' : 'XMLHttpRequest'}))
	for root_item in root_menu.itervalues():
		for root_item in root_item:
			root_check.append(root_item['title'])
	while root_start < root_count:
		root_data = cove.programs.filter(fields = 'mediafiles', order_by = 'title', limit_start = root_start)
		root_menu = root_data['results']
		root_count = root_data['count']
		root_stop = root_data['stop']
		del root_data
		for root_item2 in root_menu:
			if root_item2['website'] is None:
				root_website = ''
			else:
				root_website = root_item2['website']
			if (root_item2['title'] in root_check) and ('pbskids.org' not in root_website):
				root_name = _common.smart_utf8(root_item2['title'])
				season_url = re.compile('/cove/v1/programs/(.*?)/').findall(root_item2['resource_uri'])[0]
				_common.add_show(root_name,  SITE, 'seasons', season_url)
		root_start = root_stop
	_common.set_view('tvshows')

def seasons(season_url = _common.args.url):
	for type in TYPES:
		season_data = cove.videos.filter(fields = 'mediafiles', filter_program = season_url, order_by = '-airdate', filter_availability_status = 'Available', limit_start = 0, filter_type = type)
		try:
			season_menu = int(season_data['count'])
		except:
			season_menu = 0
		if season_menu > 0:
			_common.add_directory(type+'s',  SITE, 'episodes', (season_url + '#'+type))
		_common.set_view('seasons')

def episodes(episode_url = _common.args.url):
	episode_id, type = episode_url.split('#')
	episode_start = 0
	episode_count = 200
	while episode_start < episode_count:
		episode_data = cove.videos.filter(fields = 'associated_images,mediafiles', filter_program = episode_id, order_by = '-airdate', filter_availability_status = 'Available', limit_start = episode_start, filter_type = type)
		episode_menu = episode_data['results']
		episode_count = episode_data['count']
		episode_stop = episode_data['stop']
		del episode_data
		for episode_item in episode_menu:
			infoLabels={}
			if episode_item['mediafiles']:
				url = str(episode_item['tp_media_object_id'])
				episode_name = episode_item['title']
				episode_plot = episode_item['long_description']
				episode_airdate = _common.format_date(episode_item['airdate'], '%Y-%m-%d %H:%M:%S', '%d.%m.%Y')
				episode_duration = int(episode_item['mediafiles'][0]['length_mseconds'] / 1000)
				episode_thumb = episode_item['associated_images'][0]['url']
				for episode_thumbs in episode_item['associated_images']:
					if episode_thumbs['type']['eeid'] == 'iPad-Large':
						episode_thumb = episode_thumbs['url']
				u = sys.argv[0]
				u += '?url="' + urllib.quote_plus(url) + '"'
				u += '&mode="' + SITE + '"'
				u += '&sitemode="play_video"'
				infoLabels={	'title' : episode_name,
								'durationinseconds' : episode_duration,
								'plot' : episode_plot,
								'premiered' : episode_airdate }
				_common.add_video(u, episode_name, episode_thumb, infoLabels = infoLabels)
		episode_start = episode_stop
	_common.set_view('episodes')

def play_video(video_url = _common.args.url):
	hbitrate = -1
	sbitrate = int(_addoncompat.get_setting('quality')) * 1024
	closedcaption = None
	video_url2 = None
	finalurl = ''
	try:
		closedcaption = simplejson.loads(_connection.getURL(CLOSEDCAPTION % video_url).replace('video_info(', '').replace(')', ''))['closed_captions_url']
	except:
		pass
	if (_addoncompat.get_setting('enablesubtitles') == 'true') and (closedcaption is not None) and (closedcaption != ''):
		convert_subtitles(closedcaption.replace(' ', '+'))
	video_data = cove.videos.filter(fields = 'mediafiles', filter_tp_media_object_id = video_url)
	video_menu = video_data['results'][0]['mediafiles']
	for video_item in video_menu:
		if video_item['video_encoding']['eeid'] == 'ipad-16x9':
			video_url2 = video_item['video_data_url']
		elif video_item['video_encoding']['eeid'] == 'hls-2500k-16x9':
			video_url2 = video_item['video_data_url']
		else:
			pass
	if video_url2 is None:
		video_url2 = video_item['video_data_url']
	video_data2 = _connection.getURL(video_url2 + '?format=jsonp&callback=jQuery18303874830141490152_1377946043740')
	video_url3 = simplejson.loads(video_data2.replace('jQuery18303874830141490152_1377946043740(', '').replace(')', ''))['url']
	if '.mp4' in video_url3:
		base_url, playpath_url = video_url3.split('mp4:')
		finalurl = base_url +' playpath=mp4:' + playpath_url + '?player= swfurl=' + SWFURL % video_data['results'][0]['guid'] + ' swfvfy=true'
	else:
		video_data3 = _connection.getURL(video_url3)
		video_url4 = _m3u8.parse(video_data3)
		for video_index in video_url4.get('playlists'):
			bitrate = int(video_index.get('stream_info')['bandwidth'])
			if bitrate > hbitrate and bitrate <= sbitrate:
				hbitrate = bitrate
				finalurl = video_url3.rsplit('/', 1)[0] + '/' + video_index.get('uri')
	xbmcplugin.setResolvedUrl(pluginHandle, True, xbmcgui.ListItem(path = finalurl))
	if (_addoncompat.get_setting('enablesubtitles') == 'true') and (closedcaption is not None) and (closedcaption != ''):
		while not xbmc.Player().isPlaying():
			xbmc.sleep(100)
		xbmc.Player().setSubtitles(_common.SUBTITLE)

def clean_subs(data):
	br = re.compile(r'<br.*?>')
	tag = re.compile(r'<.*?>')
	space = re.compile(r'\s\s\s+')
	apos = re.compile(r'&amp;apos;')
	gt = re.compile(r'&gt;+')
	sub = br.sub('\n', data)
	sub = tag.sub(' ', sub)
	sub = space.sub(' ', sub)
	sub = apos.sub('\'', sub)
	sub = gt.sub('>', sub)
	return sub

def convert_subtitles(closedcaption):
	str_output = ''
	subtitle_data = _connection.getURL(closedcaption, connectiontype = 0)
	subtitle_data = BeautifulSoup(subtitle_data, 'html.parser', parse_only = SoupStrainer('div'))
	lines = subtitle_data.find_all('p')
	for i, line in enumerate(lines):
		if line is not None:
			sub = clean_subs(_common.smart_utf8(line))
			start_time = _common.smart_utf8(line['begin'].replace('.', ','))
			if ',' not in start_time:
				start_time = start_time + ',00'
			end_time = _common.smart_utf8(line['end'].replace('.', ','))
			if ',' not in end_time:
				end_time = end_time + ',00'
			str_output += str(i + 1) + '\n' + start_time[:11] + ' --> ' + end_time[:11] + '\n' + sub + '\n\n'
	file = open(_common.SUBTITLE, 'w')
	file.write(str_output)
	file.close()
