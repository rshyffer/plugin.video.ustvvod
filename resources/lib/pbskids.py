#!/usr/bin/python
# -*- coding: utf-8 -*-
import _common
import _connection
import _m3u8
import re
import simplejson
import sys
import urllib
import xbmc
import xbmcaddon
import xbmcgui
import xbmcplugin

addon = xbmcaddon.Addon()
pluginHandle = int (sys.argv[1])

SITE = 'pbskids'
NAME = 'PBS Kids'
DESCRIPTION = 'PBS Kids is the brand for children\'s programming aired by the Public Broadcasting Service (PBS) in the United States founded in 1993. It is aimed at children ages 2 to 13.'
SHOWS = 'http://pbskids.org/pbsk/video/api/getShows'
SWFURL = 'http://www-tc.pbs.org/video/media/swf/PBSPlayer.swf?video=%s&player=viral'
TYPES = ['Episode', 'Segment', 'Clip', 'Promotion', 'Interstitial', 'Other']
SEASON = 'http://pbskids.org/pbsk/video/api/getVideos/?program=%s&endindex=1&encoding=&orderby=-airdate&status=available&category=&type=%s'
EPISODES = 'http://pbskids.org/pbsk/video/api/getVideos/?program=%s&endindex=100&encoding=&orderby=-airdate&status=available&category=&type=%s&return=type,airdate,images'
VIDEO = 'http://pbskids.org/pbsk/video/api/getVideos/?guid=%s&endindex=1&encoding=&return=captions'

def masterlist():
	master_db = []
	master_menu = simplejson.loads(_connection.getURL(SHOWS))
	for master_item in master_menu['items']:
		master_name = _common.smart_utf8(master_item['title'])
		master_db.append((master_name, SITE, 'seasons', urllib.quote_plus(master_name)))
	return master_db

def seasons(show_name = _common.args.url):
	for type in TYPES:
		season_data = _connection.getURL(SEASON % (show_name, type))
		season_menu = simplejson.loads(season_data)
		try:
			season_count = int(season_menu['matched'])
		except:
			season_count = 0
		if season_count > 0:
			_common.add_directory(type + 's',  SITE, 'episodes', EPISODES % (show_name, type))
		_common.set_view('seasons')

def episodes(episode_url = _common.args.url):
	episode_data = _connection.getURL(episode_url)
	episode_menu = simplejson.loads(episode_data)
	for episode_item in episode_menu['items']:
		if episode_item['videos']:
			url = episode_item['guid']
			episode_name = episode_item['title']
			episode_plot = episode_item['description']
			episode_airdate = _common.format_date(episode_item['airdate'], '%Y-%m-%d %H:%M:%S', '%d.%m.%Y')
			episode_duration = int(episode_item['videos'].itervalues().next()['length']) / 1000
			try:
				episode_thumb = episode_item['images']['kids-mezzannine-16x9']['url']
			except:
				try:
					episode_thumb = episode_item['images']['kids-mezzannine-4x3']['url']
				except:
					episode_thumb = episode_item['images']['mezzanine']['url']
			HD = False
			for video in episode_item['videos']['flash'].itervalues():
				try:
					if video['bitrate'] > 2000:
						HD = True
				except:
					pass
			u = sys.argv[0]
			u += '?url="' + urllib.quote_plus(url) + '"'
			u += '&mode="' + SITE + '"'
			u += '&sitemode="play_video"'
			infoLabels={	'title' : episode_name,
							'durationinseconds' : episode_duration,
							'plot' : episode_plot,
							'premiered' : episode_airdate }
			_common.add_video(u, episode_name, episode_thumb, infoLabels = infoLabels, HD = HD, quality_mode = 'select_quailty')
	_common.set_view('episodes')

def play_video(guid = _common.args.url):
	try:
		qbitrate = _common.args.quality
	except:
		qbitrate = None
	video_url =  VIDEO % guid
	hbitrate = -1
	lbitrate = -1
	sbitrate = int(addon.getSetting('quality')) 
	closedcaption = None
	video_url2 = None
	finalurl = ''
	video_data = _connection.getURL(video_url)
	video_menu = simplejson.loads(video_data)['items']
	video_item = video_menu[0] 
	try:
		closedcaption = video_item['captions']['sami']['url']
	except:
		pass
	if (addon.getSetting('enablesubtitles') == 'true') and (closedcaption is not None) and (closedcaption != ''):
		convert_subtitles(closedcaption.replace(' ', '+'))
	if addon.getSetting('preffered_stream_type') == 'RTMP':
		for video in video_item['videos']['flash'].itervalues():
			try:
				bitrate = video['bitrate']
				if qbitrate is  None:
					if bitrate < lbitrate or lbitrate == -1:
						lbitrate = bitrate
						luri = video['url']
					if bitrate > hbitrate and bitrate <= sbitrate:
						hbitrate = bitrate
						uri = video['url']
				else:
					if bitrate == qbitrate:
						uri = video['url']
			except:
				pass
		if uri is None:
			uri = luri
		video_data2 = _connection.getURL(uri + '?format=json')
		video_url3 = simplejson.loads(video_data2)['url']
		if '.mp4' in video_url3:
			base_url, playpath_url = video_url3.split('mp4:')
			playpath_url = ' playpath=mp4:' + playpath_url  
		elif 'flv' in video_url3:
			base_url, playpath_url = video_url3.split('flv:')
			playpath_url = ' playpath=' + playpath_url.replace('.flv','')
		finalurl = base_url + playpath_url + '?player= swfurl=' + SWFURL % guid + ' swfvfy=true'
	else:
		ipad_url = video_item['videos']['iphone']['url']
		video_data2 = _connection.getURL(ipad_url + '?format=json')
		video_url3 = simplejson.loads(video_data2)['url']
		video_data3 = _connection.getURL(video_url3)
		video_url4 = _m3u8.parse(video_data3)
		uri = None
		for video_index in video_url4.get('playlists'):
			try:
				codecs =  video_index.get('stream_info')['codecs']
			except:
				codecs = ''
			if  codecs != 'mp4a.40.5':
				if qbitrate is None:
					bitrate = int(video_index.get('stream_info')['bandwidth']) /1024
					if bitrate < lbitrate or lbitrate == -1:
						lbitrate = bitrate
						luri = video_index.get('uri')
					if bitrate > hbitrate and bitrate <= sbitrate:
						hbitrate = bitrate
						uri = video_index.get('uri')
				else:
					bitrate = int(video_index.get('stream_info')['bandwidth']) 
					if bitrate == qbitrate:
						uri = video_index.get('uri')
		if uri is None:
			uri = luri
		finalurl = video_url3.rsplit('/', 1)[0] + '/' + uri
	item = xbmcgui.ListItem(path = finalurl)
	if qbitrate is not None:
			item.setThumbnailImage(_common.args.thumb)
			item.setInfo('Video', {	'title' : _common.args.name,
							'season' : _common.args.season_number,
							'episode' : _common.args.episode_number})
	xbmcplugin.setResolvedUrl(pluginHandle, True, item)
	if (addon.getSetting('enablesubtitles') == 'true') and (closedcaption is not None) and (closedcaption != ''):
		while not xbmc.Player().isPlaying():
			xbmc.sleep(100)
		xbmc.Player().setSubtitles(_common.SUBTITLESMI)


def select_quailty(guid = _common.args.url):
	video_url =  VIDEO % guid
	#hbitrate = -1
	#lbitrate = -1
	sbitrate = int(addon.getSetting('quality')) * 1024
	closedcaption = None
	video_url2 = None
	#finalurl = ''
	video_data = _connection.getURL(video_url)
	video_menu = simplejson.loads(video_data)['items']
	video_item = video_menu[0] 
	#try:
	#	closedcaption = video_item['captions']['sami']['url']
	#except:
	#	pass
#	if (addon.getSetting('enablesubtitles') == 'true') and (closedcaption is not None) and (closedcaption != ''):
#		convert_subtitles(closedcaption.replace(' ', '+'))
	bitrates = []
	if addon.getSetting('preffered_stream_type') == 'RTMP':
		for video in video_item['videos']['flash'].itervalues():
			try:
				bitrate = video['bitrate']
				# if bitrate < lbitrate or lbitrate == -1:
					# lbitrate = bitrate
					# luri = video['url']
				# if bitrate > hbitrate and bitrate <= sbitrate:
					# hbitrate = bitrate
					# uri = video['url']
				# print video
				bitrates.append((bitrate,bitrate))
			except:
				pass
			#print uri,luri
	else:
		ipad_url = video_item['videos']['iphone']['url']
		video_data2 = _connection.getURL(ipad_url + '?format=json')
		video_url3 = simplejson.loads(video_data2)['url']
		video_data3 = _connection.getURL(video_url3)
		video_url4 = _m3u8.parse(video_data3)
		uri = None
		for video_index in video_url4.get('playlists'):
			try:
				codecs =  video_index.get('stream_info')['codecs']
			except:
				codecs = ''
			if  codecs != 'mp4a.40.5':
				bitrate = int(video_index.get('stream_info')['bandwidth'])
				bitrates.append((int(bitrate) / 1024 , bitrate))
	return bitrates

def clean_subs(data):
	sami = re.compile(r'sami')
	tag = re.compile(r' *<')
	quote = re.compile(r'"')
	sub = sami.sub('SAMI', data)
	sub = tag.sub('<', sub)
	sub = quote.sub('', sub)
	return sub

def convert_subtitles(closedcaption):
	str_output = ''
	subtitle_data = _connection.getURL(closedcaption, connectiontype = 0)
	subtitle_data = clean_subs(_common.smart_utf8(subtitle_data))
	file = open(_common.SUBTITLESMI, 'w')
	file.write(subtitle_data)
	file.close()
