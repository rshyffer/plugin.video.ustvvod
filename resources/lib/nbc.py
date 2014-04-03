#!/usr/bin/python
# -*- coding: utf-8 -*-
import _addoncompat
import _common
import _connection
import _m3u8
import os
import base64
import HTMLParser
import time
import re
import simplejson
import sys
import urllib
import xbmc
import xbmcgui
import xbmcplugin

from bs4 import BeautifulSoup, SoupStrainer

pluginHandle = int(sys.argv[1])

SITE = 'nbc'
NAME = 'NBC'
DESCRIPTION = "NBC Entertainment develops and schedules programming for the network's primetime, late-night, and daytime schedules. NBC's quality programs and balanced lineup have earned the network critical acclaim, numerous awards, and ratings success. The network has earned more Emmy Awards than any network in television history. NBC's roster of popular scripted series includes critically acclaimed comedies like Emmy winners The Office, starring Steve Carell, and 30 Rock, starring Alec Baldwin and Tina Fey. Veteran, award-winning dramas on NBC include Law & Order: SVU, Chuck, and Friday Night Lights. Unscripted series for NBC include the hits The Biggest Loser, Celebrity Apprentice, and America's Got Talent. NBC's late-night story is highlighted by The Tonight Show with Jay Leno, Late Night with Jimmy Fallon, Last Call with Carson Daly, and Saturday Night Live. NBC Daytime's Days of Our Lives consistently finishes among daytime's top programs in the valuable women 18-34 category. Saturday mornings the network broadcasts Qubo on NBC, a three-hour block that features fun, entertaining, and educational programming for kids, including the award-winning, 3-D animated series Veggie Tales."
SHOWS = 'http://www.nbc.com/shows'
EPISODES = 'http://www.nbc.com/data/node/%s/video_carousel'
VIDEOPAGE = 'http://videoservices.nbcuni.com/player/clip?clear=true&domainReq=www.nbc.com&geoIP=US&clipId=%s'
SMIL_BASE = 'http://video.nbcuni.com/'
RTMP = 'cp37307.edgefcs.net'
APP = 'ondemand'
IDENTURL = 'http://%s/fcs/ident' % RTMP
SWFURL = 'http://video.nbcuni.com/core/6.6.1/OSMFPlayer.swf'
SMIL = 'http://link.theplatform.com/s/NnzsPC/%s?mbr=true&player=Onsite%%20Player&policy=43674&manifest=m3u&format=SMIL&Tracking=true&Embedded=true'
TONIGHT_SHOW_FEED = '%s/content/a/filter-items/?type=video'

def masterlist():
	master_db = []
	master_data = _connection.getURL(SHOWS)
	master_tree = BeautifulSoup(master_data, 'html5lib')
	master_menu = master_tree.footer.find_all('li', class_ = 'views-row')
	for master_item in master_menu:
		master_name = _common.smart_utf8(master_item.text.strip())
		season_url = master_item.a['href']
		master_db.append((master_name, SITE, 'seasons', season_url))
	return master_db

def rootlist():
	root_data = _connection.getURL(SHOWS)
	root_tree = BeautifulSoup(root_data, 'html5lib')
	root_menu = root_tree.footer.find_all('li', class_ = 'views-row')
	for root_item in root_menu:
		root_name = _common.smart_utf8(root_item.text.strip())
		season_url = root_item.a['href']
		_common.add_show(root_name, SITE, 'seasons', season_url)
	_common.set_view('tvshows')

def seasons(season_url = _common.args.url):
	if 'the-tonight-show' in season_url:
		add_show_thetonightshow(season_url)
		return
	season_url = season_url + '/video'
	season_data = _connection.getURL(season_url)
	season_tree  = BeautifulSoup(season_data, 'html5lib')
	season_menu = season_tree.find_all('div', class_ = 'nbc_mpx_carousel')
	for season in season_menu:
		season_title = season.h2.text.strip()
		season_title = re.sub(' +',' ', season_title)
		season_id = season['id']
		season_node = season_id.split('_')[-1]
		_common.add_directory(season_title, SITE, 'episodes',  EPISODES % season_node)
	_common.set_view('seasons')

def episodes(episode_url = _common.args.url):
	if 'the-tonight-show' in episode_url:
		if 'Clips' in _common.args.name:
			add_videos_thetonightshow(episode_url, 'segment')
		else:
			add_videos_thetonightshow(episode_url, 'episode')
		return
	episode_data = _connection.getURL(episode_url)
	episode_json = simplejson.loads(episode_data)
	episode_menu = episode_json['entries']
	for episode_item in episode_menu:
		pid = episode_item['media$content'][0]['plfile$releases'][0]['plrelease$pid']	
		url = SMIL % pid	
		try:
			episode_duration = int(episode_item['plfile$duration'].replace(' min','')) * 60
		except:
			episode_duration = -1
		episode_plot = HTMLParser.HTMLParser().unescape(episode_item['description'])
		epoch = int(episode_item['pubDate']) / 1000
		episode_airdate = _common.format_date(epoch = epoch)
		episode_name = HTMLParser.HTMLParser().unescape(episode_item['title'])
		show_title = episode_item['showShortName']
		try:
			season_number = int(episode_item['pl1$seasonNumber'])
		except:
			season_number = -1
		try:
			episode_number = int(episode_item['pl1$episodeNumber'])
		except:
			episode_number = -1
		try:
			episode_thumb = episode_item['plmedia$defaultThumbnailUrl']['big']
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
						'premiered' : episode_airdate,
						'TVShowTitle' : show_title}
		_common.add_video(u, episode_name, episode_thumb, infoLabels = infoLabels, quality_mode  = 'list_qualities')
	_common.set_view('episodes')

def add_show_thetonightshow(url):
	_common.add_directory('Full Episodes',  SITE, 'episodes', url)
	_common.add_directory('Clips',  SITE, 'episodes', url)
	_common.set_view('seasons')

def add_videos_thetonightshow(url, type_, page = 1, added_episodes = []):
	this_url = (TONIGHT_SHOW_FEED % url) + '&offset=' + str((page-1) * 10)
	root_data = _connection.getURL(this_url)
	data = simplejson.loads(root_data)
	for video in data['content']:
		if video['type'] == type_:
			if type_ == 'episode':
				episode_name = video['name']
				episode_id = video['episodeNumber']
			else:
				episode_name = video['title']
				episode_id = video['id']
			if episode_id in added_episodes:
				continue
			added_episodes.append(episode_id)
			pid = video['videos'][0]['mpxPublicId']
			episode_url = SMIL % pid
			episode_plot = BeautifulSoup(video['description']['value']).p.string
			try:
				episode_airdate = _common.format_date(video['airDate'][:-6],'%Y-%m-%dT%H:%M:%S','%d.%m.%Y')
			except:
				episode_airdate = -1
			try:
				season_number = int(video['season'])
			except:
				season_number = -1
			try:
				episode_number = int(video['episodeNumber'])
			except:
				episode_number = -1
			try:
				episode_thumb = video['images'][0]['bitImageSmall']
			except:
				episode_thumb = None
			u = sys.argv[0]
			u += '?url="' + urllib.quote_plus(episode_url) + '"'
			u += '&mode="' + SITE + '"'
			u += '&sitemode="play_video"'
			infoLabels={	'title' : episode_name,
							'season' : season_number,
							'episode' : episode_number,
							'plot' : episode_plot,
							'premiered' : episode_airdate}
			_common.add_video(u, episode_name, episode_thumb, infoLabels = infoLabels, quality_mode  = 'list_qualities')
	if page < int(_addoncompat.get_setting('maxpages')):
		add_videos_thetonightshow(url, type_, page + 1, added_episodes)
	_common.set_view('episodes')

def play_video(video_url = _common.args.url, tonightshow = False):
	try:
		qbitrate = _common.args.quality
	except:
		qbitrate = None
	closedcaption = None
	video_data = _connection.getURL(video_url)
	smil_tree = BeautifulSoup(video_data, 'html.parser')
	video_url2 = smil_tree.video['src']	
	try:
		closedcaption = smil_tree.textstream['src']
	except:
		pass
	clip_id = smil_tree.video.find('param', attrs = {'name' : 'clipId'})
	if clip_id is not None:
		clip_id = clip_id['value']
		video_url = VIDEOPAGE % clip_id
		video_data = _connection.getURL(video_url)
		video_tree = BeautifulSoup(video_data, 'html.parser')
		clip_url = SMIL_BASE + video_tree.clipurl.string
		smil_data = _connection.getURL(clip_url)
		smil_tree = BeautifulSoup(smil_data, 'html.parser')
		base_url = get_rtmp()
		hbitrate = -1
		sbitrate = int(_addoncompat.get_setting('quality')) * 1024
		if qbitrate is None:
			video_url2 = smil_tree.find_all('video')
			for video_index in video_url2:
				bitrate = int(video_index['system-bitrate'])
				if bitrate > hbitrate and bitrate <= sbitrate:
					hbitrate = bitrate
					playpath_url = video_index['src']
		else:
			playpath_url = smil_tree.switch.find('video', attrs = {'system-bitrate' : qbitrate})['src']
		if '.mp4' in playpath_url:
			playpath_url = 'mp4:' + playpath_url
		else:
			playpath_url = playpath_url.replace('.flv', '')
		finalurl = base_url + ' playpath=' + playpath_url + ' swfurl=' + SWFURL + ' swfvfy=true'
	else:
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

def get_rtmp():
	ident_data = _connection.getURL(IDENTURL)
	ident_tree = BeautifulSoup(ident_data, 'html.parser')
	ip = ident_tree.ip.string
	rtmpurl = 'rtmp://' + ip + ':1935/' + APP + '?_fcs_vhost=' + RTMP
	return str(rtmpurl)
	
def list_qualities(video_url = _common.args.url):
	bitrates = []
	video_data = _connection.getURL(video_url)
	smil_tree = BeautifulSoup(video_data, 'html.parser')
	video_url2 = smil_tree.video['src']
	clip_id = smil_tree.video.find('param', attrs = {'name' : 'clipId'})
	if clip_id is not None:
		clip_id = clip_id['value']
		video_url = VIDEOPAGE % clip_id
		video_data = _connection.getURL(video_url)
		video_tree = BeautifulSoup(video_data, 'html.parser')
		clip_url = SMIL_BASE + video_tree.clipurl.string	
		smil_data = _connection.getURL(clip_url)
		smil_tree = BeautifulSoup(smil_data, 'html.parser')
		video_url2 = smil_tree.find_all('video')
		for video_index in video_url2:
			bitrate = int(video_index['system-bitrate'])
			display = int(bitrate)/1024
			bitrates.append((display, bitrate))
	else:
		m3u_master_data = _connection.getURL(video_url2)
		m3u_master = _m3u8.parse(m3u_master_data)
		for video_index in m3u_master.get('playlists'):
			try:
				codecs =  video_index.get('stream_info')['codecs']
			except:
				codecs = ''
			if  codecs != 'mp4a.40.2':
				bitrate = int(video_index.get('stream_info')['bandwidth'])
				display = int(bitrate)/1024
				bitrates.append((display, bitrate))
	return bitrates
