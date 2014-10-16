#!/usr/bin/python
# -*- coding: utf-8 -*-
import _addoncompat
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
import xbmcgui
import xbmcplugin
from bs4 import BeautifulSoup, SoupStrainer

pluginHandle = int(sys.argv[1])

SITE = 'aetv'
NAME = 'A&E'
DESCRIPTION = "A&E is Real Life. Drama.  Now reaching more than 99 million homes, A&E is television that you can't turn away from; where unscripted shows are dramatic and scripted dramas are authentic.  A&E offers a diverse mix of high quality entertainment ranging from the network's original scripted series to signature non-fiction franchises, including the Emmy-winning \'Intervention,\' \'Dog The Bounty Hunter,\' \'Hoarders,\' \'Paranormal State\' and \'Criss Angel Mindfreak,\' and the most successful justice shows on cable, including \'The First 48\' and \'Manhunters.\'  The A&E website is located at www.aetv.com."
SHOWS = 'http://wombatapi.aetv.com/shows2/ae'
SEASONSEPISODE = 'https://mobileservices-a.akamaihd.net/jservice/wombattpservice/show_titles2/episode/ae?show_name=%s&get_season'
SEASONSCLIPS = 'https://mobileservices-a.akamaihd.net/jservice/wombattpservice/show_titles2/clip/ae?show_name=%s&get_season'
EPISODES = 'https://mobileservices-a.akamaihd.net/jservice/wombattpservice/show_titles2/episode/ae?show_name=%s&filter_by=season&filter_value=%d'
CLIPS = 'https://mobileservices-a.akamaihd.net/jservice/wombattpservice/show_titles2/clip/ae?show_name=%s&filter_by=season&filter_value=%d'

def masterlist():
	master_db = []
	master_data = _connection.getURL(SHOWS)
	master_tree = simplejson.loads(master_data)
	for master_item in master_tree:
		if (master_item['hasNoVideo'] == 'false'):
			master_name = _common.smart_utf8(master_item['detailTitle'])
			master_db.append((master_name, SITE, 'seasons', urllib.quote_plus(master_item['showID'])))
	return master_db

def seasons(season_url = _common.args.url):
	season_data = _connection.getURL(SEASONSEPISODE % season_url)
	season_tree = simplejson.loads(season_data)['season']
	for season_item in season_tree:
		season_name = 'Season ' + str(season_item)
		_common.add_directory(season_name,  SITE, 'episodes', EPISODES % (season_url, season_item))
	season_url = _common.args.url
	season_data = _connection.getURL(SEASONSCLIPS % season_url)
	season_tree = simplejson.loads(season_data)['season']
	for season_item in season_tree:
		season_name = 'Season Clips ' + str(season_item)
		_common.add_directory(season_name,  SITE, 'episodes', CLIPS % (season_url, season_item))
	_common.set_view('seasons')

def episodes(episode_url = _common.args.url):
	episode_data = _connection.getURL(episode_url)
	episode_tree = simplejson.loads(episode_data)['Items']
	for episode_item in episode_tree:
			url = episode_item['playURL_HLS']
			episode_duration = int(episode_item['totalVideoDuration']) / 1000
			try:
				episode_airdate = _common.format_date(episode_item['airDate'].split('T')[0],'%Y-%m-%d')
			except:
				episode_airdate = -1
			episode_name = episode_item['title']
			try:
				season_number = int(episode_item['season'])
			except:
				season_number = -1
			try:
				episode_number = int(episode_item['episode'])
			except:
				episode_number = -1
			try:
				episode_thumb = episode_item['thumbnailImageURL']
			except:
				try:
					episode_thumb = episode_item['stillImageURL']
				except:
					try:
						episode_thumb = episode_item['modalImageURL']
					except:
						episode_thumb = None
			episode_plot = episode_item['description']
			episode_showtitle = episode_item['seriesName']
			episode_mpaa = episode_item['rating']
			u = sys.argv[0]
			u += '?url="' + urllib.quote_plus(url) + '"'
			u += '&mode="' + SITE + '"'
			u += '&sitemode="play_video"'
			infoLabels={	'title' : episode_name,
							'durationinseconds' : episode_duration,
							'season' : season_number,
							'episode' : episode_number,
							'plot' : episode_plot,
							'premiered' : episode_airdate,
							'TVShowTitle' : episode_showtitle,
							'MPAA' : episode_mpaa }
			_common.add_video(u, episode_name, episode_thumb, infoLabels = infoLabels, quality_mode = 'list_qualities')
	_common.set_view('episodes')

def play_video(video_url = _common.args.url):
	try:
		qbitrate = _common.args.quality
	except:
		qbitrate = None
	closedcaption = None
	sig = sign_url(video_url)
	smil_url = re.compile('(.+)\?').findall(video_url)[0] + '?switch=hls&assetTypes=medium_video_s3&mbr=true&metafile=true&sig=' + sig
	smil_data = _connection.getURL(smil_url)
	smil_tree = BeautifulSoup(smil_data, 'html.parser')
	video_url2 = smil_tree.video['src']	
	try:
		closedcaption = smil_tree.textstream['src']
	except:
		pass
	m3u_master_data = _connection.getURL(video_url2, savecookie = True)
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
	key_file = open(_common.KEYFILE, 'wb')
	key_file.write(key_data)
	key_file.close()
	video_url5 = re.compile('(http:.*?)\n').findall(m3u_data)
	for i, video_item in enumerate(video_url5):
		newurl = base64.b64encode(video_item)
		newurl = urllib.quote_plus(newurl)
		m3u_data = m3u_data.replace(video_item, 'http://127.0.0.1:12345/foxstation/' + newurl)
	localhttpserver = True
	filestring = 'XBMC.RunScript(' + os.path.join(_common.LIBPATH,'_proxy.py') + ', 12345)'
	xbmc.executebuiltin(filestring)
	time.sleep(20)
	m3u_data = m3u_data.replace(key_url, 'http://127.0.0.1:12345/play.key')
	playfile = open(_common.PLAYFILE, 'w')
	playfile.write(m3u_data)
	playfile.close()
	finalurl = _common.PLAYFILE
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
			xbmc.sleep(100)
	if (_addoncompat.get_setting('enablesubtitles') == 'true') and (closedcaption is not None):
		xbmc.Player().setSubtitles(_common.SUBTITLE)
	if localhttpserver is True:
		while xbmc.Player().isPlaying():
			xbmc.sleep(1000)
		_connection.getURL('http://localhost:12345/stop', connectiontype = 0)

def clean_subs(data):
	br = re.compile(r'<br.*?>')
	tag = re.compile(r'<.*?>')
	space = re.compile(r'\s\s\s+')
	apos = re.compile(r'&amp;apos;')
	gt = re.compile(r'&gt;')
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
	srt_output = ''
	lines = subtitle_data.find_all('p')
	i = 0
	last_start_time = ''
	last_end_time = ''
	for line in lines:
		try:
			if line is not None:
				sub = clean_subs(_common.smart_utf8(line))
				start_time = _common.smart_utf8(line['begin'].replace('.', ','))
				end_time = _common.smart_utf8(line['end'].replace('.', ','))
				if start_time != last_start_time and end_time != last_end_time:
					str_output += '\n' + str(i + 1) + '\n' + start_time + ' --> ' + end_time + '\n' + sub + '\n'
					i = i + 1
					last_end_time = end_time
					last_start_time = start_time
				else:
					str_output +=  sub + '\n\n'
		except:
			pass
	file = open(_common.SUBTITLE, 'w')
	file.write(str_output)
	file.close()

def list_qualities(video_url = _common.args.url):
	bitrates = []
	sig = sign_url(video_url)
	smil_url = re.compile('(.+)\?').findall(video_url)[0] + '?switch=hls&assetTypes=medium_video_s3&mbr=true&metafile=true&sig=' + sig
	video_data = _connection.getURL(smil_url)
	smil_tree = BeautifulSoup(video_data, 'html.parser')
	video_url2 = smil_tree.video['src']
	m3u_master_data = _connection.getURL(video_url2)
	m3u_master = _m3u8.parse(m3u_master_data)
	for video_index in m3u_master.get('playlists'):
		bitrate = int(video_index.get('stream_info')['bandwidth'])
		display = int(bitrate) / 1024
		bitrates.append((display, bitrate))
	return bitrates

def sign_url(url):
	sig = _connection.getURL('http://www.history.com/components/get-signed-signature?url=' + re.compile('/[sz]/(.+)\?').findall(url)[0])
	return sig
