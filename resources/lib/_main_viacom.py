#!/usr/bin/python
# -*- coding: utf-8 -*-
import _addoncompat
import _common
import _connection
import _m3u8
import base64
import datetime
import os
import Queue
import re
import simplejson
import sys
import threading
import time
import urllib
import xbmc
import xbmcgui
import xbmcplugin
from bs4 import BeautifulSoup, SoupStrainer

pluginHandle = int(sys.argv[1])
player = _common.XBMCPlayer()

VIDEOURL = 'http://media.mtvnservices.com/'
VIDEOURLAPI = 'http://media-utils.mtvnservices.com/services/MediaGenerator/%s?device=Xbox'
TYPES = [('fullEpisodes' , 'Full Episodes'), ('bonusClips,afterShowsClips,recapsClips,sneakPeeksClips,dailies,showClips' , 'Extras')]
DEVICE = 'Xbox'
BITRATERANGE = 10

def masterlist(SITE, SHOWS):
	master_db = []
	master_data = _connection.getURL(SHOWS)
	master_tree = simplejson.loads(master_data)
	for master_item in master_tree['promoList']['promos']:
		master_item = master_item['promo']['associatedContent']['series']
		master_name = master_item['title']
		master_id = master_item['seriesId']
		if master_id is not None:
			master_db.append((master_name, SITE, 'seasons', master_id))
		else:
			pass
	return master_db

def seasons(SITE, API):
	season_id = _common.args.url
	count = 0
	for type in TYPES:
		season_url = API + 'series/' + season_id + '/playlists.json?page=0&pageSize=500&type=' + type[0]
		season_data = _connection.getURL(season_url)
		try:
			season_tree = simplejson.loads(season_data)['series']['playlists']
			for season_item in season_tree:
				try:
					if (season_item['playlist']['distributionPolicies'][0]['distributionPolicy']['policyType'] == 'playable'):
						count = count + 1
				except:
					if (season_item['playlist']['distributionPolicies'][0]['policyType'] == 'playable'):
						count = count + 1
				else:
					count = count
			if count > 0:
				_common.add_directory(type[1], SITE, 'videos', season_url)
		except:
			pass
	_common.set_view('seasons')

def videos(SITE):
	episode_url = _common.args.url
	episode_data = _connection.getURL(episode_url)
	episode_tree = simplejson.loads(episode_data)
	for episode_item in episode_tree['series']['playlists']:
		show_name = episode_tree['series']['title']
		episode_item = episode_item['playlist']
		episode_name = episode_item['headline'].split('|')[-1].strip()
		try:
			episode_info = re.compile('s([0-9]).e?([0-9]{0,2}).*').findall(episode_item['title'])
			try:
				episode_season, episode_number = episode_info[0]
			except:
				episode_season = episode_info
				episode_number = -1
		except:
			episode_season = -1
			episode_number = -1
		url = episode_item['id']
		try:
			episode_plot = episode_item['subhead']
		except:
			episode_plot = ''
		episode_thumb = episode_item['image']
		episode_duration = _common.format_seconds(episode_item['duration']['timecode'])
		u = sys.argv[0]
		u += '?url="' + urllib.quote_plus(url) + '"'
		u += '&mode="' + SITE + '"'
		u += '&sitemode="play"'
		infoLabels = {	'title' : episode_name,
						'plot' : episode_plot,
						'durationinseconds' : episode_duration,
						'tvshowtitle' : show_name,
						'season' : episode_season,
						'episode' : episode_number }
		try:
			if (episode_item['distributionPolicies'][0]['distributionPolicy']['policyType'] == 'playable'):
				_common.add_video(u, episode_name, episode_thumb, infoLabels = infoLabels, quality_mode = 'list_qualities')
		except:
			if (episode_item['distributionPolicies'][0]['policyType'] == 'playable'):
				_common.add_video(u, episode_name, episode_thumb, infoLabels = infoLabels, quality_mode = 'list_qualities')
		else:
			pass
	_common.set_view('episodes')

def play_video(BASE, video_url = _common.args.url, media_base = VIDEOURL):
	if media_base not in video_url:
		video_url = media_base + video_url
	try:
		qbitrate = _common.args.quality
	except:
		qbitrate = None
	video_url6 = 'stack://'
	closedcaption = []
	exception = False
	if 'feed' not in video_url:
		swf_url = _connection.getRedirect(video_url, header = {'Referer' : BASE})
		try:
			params = dict(item.split("=") for item in swf_url.split('?')[1].split("&"))
			uri = urllib.unquote_plus(params['uri'])
			config_url = urllib.unquote_plus(params['CONFIG_URL'].replace('Other', DEVICE))
			config_data = _connection.getURL(config_url, header = {'Referer' : video_url, 'X-Forwarded-For' : '12.13.14.15'})
			config_tree = BeautifulSoup(config_data, 'html.parser')
			if not config_tree.error:
				feed_url = config_tree.feed.string
				feed_url = feed_url.replace('{uri}', uri).replace('&amp;', '&').replace('{device}', DEVICE).replace('{ref}', 'None').strip()
			else:
				exception = True
				error_text = config_tree.error.string.split('/')[-1].split('_') 
				_common.show_exception(error_text[1], error_text[2])
		except:
			_common.show_exception("", swf_url)
	else:
		feed_url = video_url
	if not exception:
		feed_data = _connection.getURL(feed_url)
		print feed_data
		video_tree = BeautifulSoup(feed_data, 'html.parser', parse_only = SoupStrainer('media:group'))
		print video_tree
		video_segments = video_tree.find_all('media:content')
		segments = []
		for act, video_segment in enumerate(video_segments):
			if 'device' in video_segment['url']:
				video_url3 = video_segment['url'].replace('{device}', DEVICE)
			else:
				video_url3 = video_segment['url'] + '&device=' + DEVICE
			video_data3 = _connection.getURL(video_url3, header = {'X-Forwarded-For' : '12.13.14.15'})
			video_tree3 = BeautifulSoup(video_data3, 'html.parser')
			try:
				duration = video_tree3.find('rendition')['duration']
				closedcaption.append((video_tree3.find('typographic', format = 'ttml'),duration))
				segments.append(duration)
			except:
				segments.append(0)
			try:
				video_menu = video_tree3.src.string
				hbitrate = -1
				lbitrate = -1
				m3u8_url = None
				m3u_master_data = _connection.getURL(video_menu, savecookie = True)
				m3u_master = _m3u8.parse(m3u_master_data)
				sbitrate = int(_addoncompat.get_setting('quality')) * 1024
				for video_index in m3u_master.get('playlists'):
					bitrate = int(video_index.get('stream_info')['bandwidth'])
					if qbitrate is None:
						if bitrate < lbitrate or lbitrate == -1:
							lbitrate = bitrate
							lm3u8_url = video_index.get('uri')
						if bitrate > hbitrate and bitrate <= sbitrate:
							hbitrate = bitrate
							m3u8_url = video_index.get('uri')
					elif (qbitrate * (100 - BITRATERANGE))/100 < bitrate and (qbitrate * (100 + BITRATERANGE))/100 > bitrate:
						m3u8_url = video_index.get('uri')
				if 	m3u8_url is None and qbitrate is None:
					m3u8_url = lm3u8_url
				m3u_data = _connection.getURL(m3u8_url, loadcookie = True)
				key_url = re.compile('URI="(.*?)"').findall(m3u_data)[0]
				key_data = _connection.getURL(key_url, loadcookie = True)		
				key_file = open(_common.KEYFILE + str(act), 'wb')
				key_file.write(key_data)
				key_file.close()
				video_url5 = re.compile('(http:.*?)\n').findall(m3u_data)
				for i, video_item in enumerate(video_url5):
					newurl = base64.b64encode(video_item)
					newurl = urllib.quote_plus(newurl)
					m3u_data = m3u_data.replace(video_item, 'http://127.0.0.1:12345/foxstation/' + newurl)
				m3u_data = m3u_data.replace(key_url, 'http://127.0.0.1:12345/play.key' + str(act))
				playfile = open(_common.PLAYFILE.replace('.m3u8', '_' + str(act) + '.m3u8'), 'w')
				playfile.write(m3u_data)
				playfile.close()
				video_url6 += _common.PLAYFILE.replace('.m3u8', '_' + str(act) + '.m3u8') + ' , '
			except:
				pass
		player._segments_array = segments
		filestring = 'XBMC.RunScript(' + os.path.join(_common.LIBPATH,'_proxy.py') + ', 12345)'
		xbmc.executebuiltin(filestring)
		finalurl = video_url6[:-3]
		localhttpserver = True
		time.sleep(20)
		if (_addoncompat.get_setting('enablesubtitles') == 'true') and (closedcaption is not None):
			convert_subtitles(closedcaption)
			player._subtitles_Enabled = True
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

def play_video2(BASE, API, video_url = _common.args.url):
	try:
		qbitrate = _common.args.quality
	except:
		qbitrate = None
	video_url2 = 'stack://'
	threads = []
	video_queue = Queue.PriorityQueue()
	closedcaption_queue = Queue.PriorityQueue()
	segments_queue = Queue.PriorityQueue()
	video_data = _connection.getURL(API + 'playlists/%s/videos.json' % video_url)
	video_tree = simplejson.loads(video_data)
	for i, video_item in enumerate(video_tree['playlist']['videos']):
		t = threading.Thread(target = get_videos, args = (video_queue, closedcaption_queue, segments_queue, i, video_item, qbitrate))
		t.setDaemon(True)
		threads.append(t)
	[x.start() for x in threads]
	[x.join() for x in threads]
	while video_queue.qsize() > 0:
		video_url2 += video_queue.get() + ' , '
	player._segments_array = queue_to_list(segments_queue)
	filestring = 'XBMC.RunScript(' + os.path.join(_common.LIBPATH, '_proxy.py') + ', 12345)'
	xbmc.executebuiltin(filestring)
	finalurl = video_url2[:-3]
	localhttpserver = True
	time.sleep(20)
	if (_addoncompat.get_setting('enablesubtitles') == 'true') and (closedcaption_queue.qsize() > 0):
		convert_subtitles(closedcaption_queue)
		player._subtitles_Enabled = True
	item = xbmcgui.ListItem(path = finalurl)
	if qbitrate is not None:
		item.setThumbnailImage(_common.args.thumb)
		item.setInfo('Video', {	'title' : _common.args.name,
								'season' : _common.args.season_number,
								'episode' : _common.args.episode_number,
								'TVShowTitle' : _common.args.show_title })
	xbmcplugin.setResolvedUrl(pluginHandle, True, item)
	while player.is_active:
		player.sleep(250)	

def get_videos(video_queue, closedcaption_queue, segments_queue, i, video_item, qbitrate):
	lock = threading.Lock()
	video_mgid = video_item['video']['mgid']
	video_data = _connection.getURL(VIDEOURLAPI % video_mgid)
	video_tree = BeautifulSoup(video_data, 'html.parser')
	try:
		duration = video_tree.find('rendition')['duration']
		closedcaption_queue.put((video_tree.find('typographic', format = 'ttml'), duration))
		segments_queue.put(duration)
	except:
		segments_queue.put(0)
	try:
		video_menu = video_tree.src.string
		hbitrate = -1
		lbitrate = -1
		m3u8_url = None
		lock.acquire()
		m3u8_master_data = _connection.getURL(video_menu, savecookie = True)
		lock.release()
		m3u8_master = _m3u8.parse(m3u8_master_data)
		sbitrate = int(_addoncompat.get_setting('quality')) * 1024
		for video_index in m3u8_master.get('playlists'):
			bitrate = int(video_index.get('stream_info')['bandwidth'])
			if qbitrate is None:
				if bitrate < lbitrate or lbitrate == -1:
					lbitrate = bitrate
					lm3u8_url = video_index.get('uri')
				if bitrate > hbitrate and bitrate <= sbitrate:
					hbitrate = bitrate
					m3u8_url = video_index.get('uri')
			elif (qbitrate * (100 - BITRATERANGE)) / 100 < bitrate and (qbitrate * (100 + BITRATERANGE)) / 100 > bitrate:
				m3u8_url = video_index.get('uri')
		if 	((m3u8_url is None) and (qbitrate is None)):
			m3u8_url = lm3u8_url
		m3u8_data = _connection.getURL(m3u8_url, loadcookie = True)
		key_url = re.compile('URI="(.*?)"').findall(m3u8_data)[0]
		key_data = _connection.getURL(key_url, loadcookie = True)
		key_file = open(_common.KEYFILE + str(i), 'wb')
		key_file.write(key_data)
		key_file.close()
		video_url = re.compile('(http:.*?)\n').findall(m3u8_data)
		for video_item in video_url:
			newurl = base64.b64encode(video_item)
			newurl = urllib.quote_plus(newurl)
			m3u8_data = m3u8_data.replace(video_item, 'http://127.0.0.1:12345/foxstation/' + newurl)
		m3u8_data = m3u8_data.replace(key_url, 'http://127.0.0.1:12345/play.key' + str(i))
		playfile = open(_common.PLAYFILE.replace('.m3u8', '_' + str(i) + '.m3u8'), 'w')
		playfile.write(m3u8_data)
		playfile.close()
		video_queue.put(_common.PLAYFILE.replace('.m3u8', '_' + str(i) + '.m3u8'))
	except:
		pass

def queue_to_list(q):
	l = []
	while q.qsize() > 0:
		l.append(q.get())
	return l

def list_qualities(BASE, video_url = _common.args.url, media_base = VIDEOURL):
	bitrates = []
	if media_base not in video_url:
		video_url = media_base + video_url
	exception = False
	if 'feed' not in video_url:
		swf_url = _connection.getRedirect(video_url, header = {'Referer' : BASE})
		params = dict(item.split("=") for item in swf_url.split('?')[1].split("&"))
		uri = urllib.unquote_plus(params['uri'])
		config_url = urllib.unquote_plus(params['CONFIG_URL'].replace('Other', DEVICE))
		config_data = _connection.getURL(config_url, header = {'Referer' : video_url, 'X-Forwarded-For' : '12.13.14.15'})
		config_tree = BeautifulSoup(config_data, 'html.parser')
		if not config_tree.error:
			feed_url = config_tree.feed.string
			feed_url = feed_url.replace('{uri}', uri).replace('&amp;', '&').replace('{device}', DEVICE).replace('{ref}', 'None').strip()
		else:
			exception = True
			error_text = config_tree.error.string.split('/')[-1].split('_') 
			_common.show_exception(error_text[1], error_text[2])
	else:
		feed_url = video_url
	if not exception:
		feed_data = _connection.getURL(feed_url)
		video_tree = BeautifulSoup(feed_data, 'html.parser', parse_only = SoupStrainer('media:group'))
		video_segments = video_tree.find_all('media:content')
		video_segment = video_segments[0]
		video_url3 = video_segment['url'].replace('{device}', DEVICE)
		video_data3 = _connection.getURL(video_url3, header = {'X-Forwarded-For' : '12.13.14.15'})
		video_tree3 = BeautifulSoup(video_data3, 'html.parser')
		video_menu = video_tree3.find('src').string
		m3u8_url = None
		m3u_master_data = _connection.getURL(video_menu, savecookie = True)
		m3u_master = _m3u8.parse(m3u_master_data)
		for video_index in m3u_master.get('playlists'):
			bitrate = int(video_index.get('stream_info')['bandwidth'])
			display = int(bitrate) / 1024
			bitrates.append((display, bitrate))
		return bitrates

def list_qualities2(BASE, API, video_url = _common.args.url):
	video_bitrates = []
	video_data = _connection.getURL(API + 'playlists/%s/videos.json' % video_url)
	video_tree = simplejson.loads(video_data)
	video_mgid = video_tree['playlist']['videos'][0]['video']['mgid']
	video_data2 = _connection.getURL(VIDEOURLAPI % video_mgid)
	video_tree2 = BeautifulSoup(video_data2, 'html.parser')
	video_menu = video_tree2.find('src').string
	m3u8_url = None
	m3u8_master_data = _connection.getURL(video_menu, savecookie = True)
	m3u8_master = _m3u8.parse(m3u8_master_data)
	for video_index in m3u8_master.get('playlists'):
		video_bitrate = int(video_index.get('stream_info')['bandwidth'])
		bitrate_display = int(video_bitrate) / 1024
		video_bitrates.append((bitrate_display, video_bitrate))
	return video_bitrates

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
	j = 0
	count = 0
	for closedcaption_url, duration in closedcaption:
		count = count + 1
		if closedcaption_url is not None:
			subtitle_data = _connection.getURL(closedcaption_url['src'], connectiontype = 0)
			subtitle_data = BeautifulSoup(subtitle_data, 'html.parser', parse_only = SoupStrainer('div'))
			lines = subtitle_data.find_all('p')
			last_line = lines[-1]
			end_time = last_line['end'].split('.')[0].split(':')
			file_duration = int(end_time[0]) * 60 * 60 + int(end_time[1]) * 60 + int(end_time[2])
			delay = int(file_duration) - int(duration)
			for i, line in enumerate(lines):
				if line is not None:
					try:
						sub = clean_subs(_common.smart_utf8(line))
						start_time = _common.smart_utf8(datetime.datetime.strftime(datetime.datetime.strptime(line['begin'], '%H:%M:%S.%f') - datetime.timedelta(seconds = int(delay)),'%H:%M:%S,%f'))[:-4]
						end_time = _common.smart_utf8(datetime.datetime.strftime(datetime.datetime.strptime(line['end'], '%H:%M:%S.%f') - datetime.timedelta(seconds = int(delay)),'%H:%M:%S,%f'))[:-4]
						str_output += str(j + i + 1) + '\n' + start_time + ' --> ' + end_time + '\n' + sub + '\n\n'
					except:
						pass
			j = j + i + 1
			file = open(os.path.join(_common.CACHEPATH, 'subtitle-%s.srt' % str(count)), 'w')
			file.write(str_output)
			str_output=''
			file.close()
