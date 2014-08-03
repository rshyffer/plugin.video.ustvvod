#!/usr/bin/python
# -*- coding: utf-8 -*-
import _addoncompat
import _common
import _connection
import _m3u8
import os
import base64
import re
import sys
import urllib
import time
import xbmc
import xbmcgui
import xbmcplugin
from bs4 import BeautifulSoup, SoupStrainer

pluginHandle = int(sys.argv[1])

VIDEOURL = 'http://media.mtvnservices.com/'
DEVICE = 'Xbox'

def play_video(BASE, video_url = _common.args.url, media_base = VIDEOURL):
	if media_base not in video_url:
		video_url = media_base + video_url
	try:
		qbitrate = _common.args.quality
	except:
		qbitrate = None
	video_url6 = 'stack://'
	sbitrate = int(_addoncompat.get_setting('quality'))
	closedcaption = []
	if 'feed' not in video_url:
		swf_url = _connection.getRedirect(video_url, header = {'Referer' : BASE})
		params = dict(item.split("=") for item in swf_url.split('?')[1].split("&"))
		uri = urllib.unquote_plus(params['uri'])
		config_url = urllib.unquote_plus(params['CONFIG_URL'].replace('Other',DEVICE))
		config_data = _connection.getURL(config_url, header = {'Referer' : video_url, 'X-Forwarded-For' : '12.13.14.15'})
		feed_url = BeautifulSoup(config_data, 'html.parser', parse_only = SoupStrainer('feed')).feed.string
		feed_url = feed_url.replace('{uri}', uri).replace('&amp;', '&').replace('{device}', DEVICE).replace('{ref}', 'None').strip()
	else:
		feed_url = video_url
	feed_data = _connection.getURL(feed_url)
	video_tree = BeautifulSoup(feed_data, 'html.parser', parse_only = SoupStrainer('media:group'))
	video_segments = video_tree.find_all('media:content')
	

	for act, video_segment in enumerate(video_segments):
		video_url3 = video_segment['url'].replace('{device}', DEVICE)
		video_data3 = _connection.getURL(video_url3, header = {'X-Forwarded-For' : '12.13.14.15'})
		video_tree3 = BeautifulSoup(video_data3, 'html5lib')
		try:
			closedcaption.append(video_tree3.find('typographic', format = 'ttml'))
		except:
			pass

		video_menu = video_tree3.find('src').string
		hbitrate = -1
		lbitrate = -1

		m3u_master_data = _connection.getURL(video_menu, savecookie = True)
		m3u_master = _m3u8.parse(m3u_master_data)
		hbitrate = -1
		sbitrate = int(_addoncompat.get_setting('quality')) * 1024
		for video_index in m3u_master.get('playlists'):
			bitrate = int(video_index.get('stream_info')['bandwidth'])
			if qbitrate is None:
				if bitrate > hbitrate and bitrate <= sbitrate:
					hbitrate = bitrate
					m3u8_url =  video_index.get('uri')
			elif  bitrate == qbitrate:
				m3u8_url =  video_index.get('uri')
			
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


		playfile = open(_common.PLAYFILE.replace('.m3u8',  '_' + str(act)  + '.m3u8'), 'w')
		playfile.write(m3u_data)
		playfile.close()
		video_url6 +=  _common.PLAYFILE.replace('.m3u8',  '_' + str(act)  + '.m3u8') + ' , '
		
	filestring = 'XBMC.RunScript(' + os.path.join(_common.LIBPATH,'_proxy.py') + ', 12345)'
	xbmc.executebuiltin(filestring)
	finalurl = video_url6[:-3]
	localhttpserver = True
	time.sleep(20)

	if (_addoncompat.get_setting('enablesubtitles') == 'true') and (closedcaption is not None):
		convert_subtitles(closedcaption)
	item = xbmcgui.ListItem(path = finalurl)
	if qbitrate is not None:
		item.setThumbnailImage(_common.args.thumb)
		item.setInfo('Video', {	'title' : _common.args.name,
						'season' : _common.args.season_number,
						'episode' : _common.args.episode_number,
						'TVShowTitle' : _common.args.show_title})
	xbmcplugin.setResolvedUrl(pluginHandle, True, item)
	if ((_addoncompat.get_setting('enablesubtitles') == 'true') and (closedcaption is not None))  or localhttpserver is True:
		while not xbmc.Player().isPlaying():
			xbmc.sleep(200)
	if (_addoncompat.get_setting('enablesubtitles') == 'true') and (closedcaption is not None) and closedcaption !=[]:
		for count in range(1, len(closedcaption)):
			xbmc.Player().setSubtitles(os.path.join(_common.CACHEPATH, 'subtitle-%s.srt' % str(count)))
			while xbmc.Player().isPlaying():
				xbmc.sleep(10)
	if localhttpserver is True:
		while xbmc.Player().isPlaying():
			xbmc.sleep(10)
		_connection.getURL('http://localhost:12345/stop', connectiontype = 0)

def list_qualities(BASE, video_url = _common.args.url, media_base = VIDEOURL):
	if media_base not in video_url:
		video_url = media_base + video_url
	bitrates = []
	if 'feed' not in video_url:
		swf_url = _connection.getRedirect(video_url, header = {'Referer' : BASE})
		params = dict(item.split("=") for item in swf_url.split('?')[1].split("&"))
		uri = urllib.unquote_plus(params['uri'])
		config_url = urllib.unquote_plus(params['CONFIG_URL'])
		config_data = _connection.getURL(config_url, header = {'Referer' : video_url, 'X-Forwarded-For' : '12.13.14.15'})
		feed_url = BeautifulSoup(config_data, 'html.parser', parse_only = SoupStrainer('feed')).feed.string
		feed_url = feed_url.replace('{uri}', uri).replace('&amp;', '&').replace('{device}', DEVICE).replace('{ref}', 'None').strip()
	else:
		feed_url = video_url
	feed_data = _connection.getURL(feed_url)
	video_tree = BeautifulSoup(feed_data, 'html.parser', parse_only = SoupStrainer('media:group'))
	video_segments = video_tree.find_all('media:content')
	srates = []
	for video_segment in video_segments:
		video_url3 = video_segment['url'].replace('{device}', DEVICE)
		video_data3 = _connection.getURL(video_url3, header = {'X-Forwarded-For' : '12.13.14.15'})
		video_menu = BeautifulSoup(video_data3).findAll('rendition')
		orates = srates
		srates = []	
		for video_index in video_menu:
			bitrate = int(video_index['bitrate'])
			srates.append((bitrate, bitrate))
		if orates != []:
			srates = list(set(srates).intersection(orates))
	bitrates  =srates
	return bitrates
				
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

def convert_subtitles(closedcaption,durations=[]):
	str_output = ''
	j = 0
	count = 0
	for closedcaption_url in closedcaption:
		count = count + 1
		if closedcaption_url is not None:
			subtitle_data = _connection.getURL(closedcaption_url['src'], connectiontype = 0)
			subtitle_data = BeautifulSoup(subtitle_data, 'html.parser', parse_only = SoupStrainer('div'))
			lines = subtitle_data.find_all('p')
			for i, line in enumerate(lines):
				if line is not None:
					sub = clean_subs(_common.smart_utf8(line))
					try:
						start_time = _common.smart_utf8(line['begin'][:-1].replace('.', ','))
						end_time = _common.smart_utf8(line['end'][:-1].replace('.', ','))
						str_output += str(j + i + 1) + '\n' + start_time + ' --> ' + end_time + '\n' + sub + '\n\n'
					except:
						pass
			j = j + i + 1
			file = open(os.path.join(_common.CACHEPATH, 'subtitle-%s.srt' % int(count)), 'w')
			file.write(str_output)
			str_output=''
			file.close()
