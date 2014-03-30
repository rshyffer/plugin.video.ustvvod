#!/usr/bin/python
# -*- coding: utf-8 -*-
import _addoncompat
import _common
import _connection
import os
import re
import sys
import urllib
from  itertools import izip
import xbmc
import xbmcgui
import xbmcplugin
from bs4 import BeautifulSoup, SoupStrainer

pluginHandle = int(sys.argv[1])

VIDEOURL = 'http://media.mtvnservices.com/'
MP4URL = 'http://mtvnmobile.vo.llnwd.net/kip0/_pxn=0+_pxK=18639/44620/mtvnorigin'

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
	if 'southparkstudios' in video_url:
		sp_id = video_url.split(':')
		sp_id = sp_id[len(sp_id)-1]
		feed_url = 'http://www.southparkstudios.com/feeds/video-player/mrss/mgid%3Aarc%3Aepisode%3Asouthparkstudios.com"%3A' + sp_id
	elif 'feed' not in video_url:
		swf_url = _connection.getRedirect(video_url, header = {'Referer' : BASE})
		params = dict(item.split("=") for item in swf_url.split('?')[1].split("&"))
		uri = urllib.unquote_plus(params['uri'])
		config_url = urllib.unquote_plus(params['CONFIG_URL'])
		config_data = _connection.getURL(config_url, header = {'Referer' : video_url, 'X-Forwarded-For' : '12.13.14.15'})
		feed_url = BeautifulSoup(config_data, 'html.parser', parse_only = SoupStrainer('feed')).feed.string
		feed_url = feed_url.replace('{uri}', uri).replace('&amp;', '&').replace('{device}', 'Other').replace('{ref}', 'None').strip()
	else:
		feed_url = video_url
	feed_data = _connection.getURL(feed_url)
	video_tree = BeautifulSoup(feed_data, 'html.parser', parse_only = SoupStrainer('media:group'))
	video_segments = video_tree.find_all('media:content')
	for video_segment in video_segments:
		video_url3 = video_segment['url'].replace('{device}', 'Other')
		video_data3 = _connection.getURL(video_url3, header = {'X-Forwarded-For' : '12.13.14.15'})
		video_tree3 = BeautifulSoup(video_data3)
		try:
			closedcaption.append(video_tree3.find('typographic', format = 'ttml'))
		except:
			pass
		if qbitrate is None:
			video_menu = video_tree3.findAll('rendition')
			hbitrate = -1
			lbitrate = -1
			video_url4 = None
			for video_index in video_menu:
				bitrate = int(video_index['bitrate'])
				if bitrate < lbitrate or lbitrate == -1:
					lbitrate = bitrate
					video_url4 = video_index.find('src').string
				if bitrate > hbitrate and bitrate <= sbitrate:
					hbitrate = bitrate
					video_url4 = video_index.find('src').string
					
			if video_url4 is None:
				video_url4 = lvideo_url4
		else:
			video_url4 = video_tree3.find('rendition', attrs = {'bitrate' : qbitrate}).src.string
	
		video_url5 =  MP4URL + '/gsp.' + video_url4.split('/gsp.')[1] 
		print video_url5
		video_url6 += video_url5.replace(',', ',,') + ' , '
	finalurl = video_url6[:-3]
	if not closedcaption:
		try:
			closedcaption = video_tree.find_all('media:text')
		except:
			pass
	if (_addoncompat.get_setting('enablesubtitles') == 'true') and (closedcaption is not None ) and closedcaption !=[]:
		convert_subtitles(closedcaption)
	item = xbmcgui.ListItem(path = finalurl)
	if qbitrate is not None:
		item.setThumbnailImage(_common.args.thumb)
		item.setInfo('Video', {	'title' : _common.args.name,
						'season' : _common.args.season_number,
						'episode' : _common.args.episode_number})
	xbmcplugin.setResolvedUrl(pluginHandle, True, item)
	if (_addoncompat.get_setting('enablesubtitles') == 'true') and (closedcaption is not None) and closedcaption !=[]:
		while not xbmc.Player().isPlaying():
			xbmc.sleep(200)
		for count in range(1, len(closedcaption)):
			xbmc.Player().setSubtitles(os.path.join(_common.CACHEPATH, 'subtitle-%s.srt' % str(count)))
			while xbmc.Player().isPlaying():
				xbmc.sleep(10)

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
		feed_url = feed_url.replace('{uri}', uri).replace('&amp;', '&').replace('{device}', 'Other').replace('{ref}', 'None').strip()
	else:
		feed_url = video_url
	feed_data = _connection.getURL(feed_url)
	video_tree = BeautifulSoup(feed_data, 'html.parser', parse_only = SoupStrainer('media:group'))
	video_segments = video_tree.find_all('media:content')
	srates = []
	for video_segment in video_segments:
		video_url3 = video_segment['url'].replace('{device}', 'Other')
		video_data3 = _connection.getURL(video_url3, header = {'X-Forwarded-For' : '12.13.14.15'})
		video_menu = BeautifulSoup(video_data3).findAll('rendition')
		orates = srates
		srates = []	
		for video_index in video_menu:
			bitrate = int(video_index['bitrate'])
			print bitrate
			srates.append((bitrate, bitrate))
		print srates
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
