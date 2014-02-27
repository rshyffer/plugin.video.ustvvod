#!/usr/bin/python
# -*- coding: utf-8 -*-
import _addoncompat
import _common
import _connection
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
SHOWS = 'http://www.nbc.com/shows'
SEASONS = 'http://www.nbc.com/assets/esp/video/playerfeed/getRelatedDetail/.json?showCode=%s&contentType=%s&perPage=20&page=1'
TYPES = ['Full Episode', 'Web Exclusive', 'Current Preview', 'Highlight', 'Interview', 'Sneak Peek', 'Behind the Scenes']
EPISODES = 'http://www.nbc.com/assets/esp/video/playerfeed/getRelatedDetail/.json?showCode=%s&perPage=100&page=1&contentType=%s'
VIDEOPAGE = 'http://videoservices.nbcuni.com/player/clip?clear=true&domainReq=www.nbc.com&geoIP=US&clipId=%s'
SMIL_BASE = 'http://video.nbcuni.com/'
RTMP = 'cp37307.edgefcs.net'
APP = 'ondemand'
IDENTURL = 'http://%s/fcs/ident' % RTMP
SWFURL = 'http://video.nbcuni.com/core/6.6.1/OSMFPlayer.swf'

def masterlist():
	master_db = []
	master_data = _connection.getURL(SHOWS)
	master_tree = BeautifulSoup(master_data, 'html5lib')
	master_menu = master_tree.footer.find_all('li', class_ = 'views-row')
	for master_item in master_menu:
		master_name = master_item.text
		season_url = master_item.a['href']
		master_db.append((master_name, SITE, 'seasons', season_url))
	return master_db

def rootlist():
	root_data = _connection.getURL(SHOWS)
	root_tree = BeautifulSoup(root_data, 'html5lib')
	root_menu = root_tree.footer.find_all('li', class_ = 'views-row')
	for root_item in root_menu:
		root_name = root_item.text
		season_url = root_item.a['href']
		_common.add_show(root_name, SITE, 'seasons', season_url)
	_common.set_view('tvshows')

def seasons(season_url = _common.args.url):
	season_data = _connection.getURL(season_url)
	show_code = re.compile("sect=([a-z]{3,});").findall(season_data)[0]
	for type in TYPES:
		type_data = _connection.getURL(SEASONS % (show_code, urllib.quote_plus(type)))
		season_menu = simplejson.loads(type_data)
		if season_menu is not None:
			correct_type = False
			for season_item in season_menu['pageRecords']:
				if type == season_item['contentType']:
					correct_type = True
			if correct_type:
				if type[-1] != 's':
					display_name = type + 's'
				else:
					display_name = type
				_common.add_directory(display_name, SITE, 'episodes', EPISODES % (show_code, urllib.quote_plus(type)))
	_common.set_view('seasons')

def episodes(episode_url = _common.args.url):
	try:
		episode_data = _connection.getURL(episode_url)
		type = urllib.unquote_plus(episode_url.split('contentType=')[1])
		episode_json = simplejson.loads(episode_data)
		page = int(episode_json['page'])
		total_pages = int(episode_json['totalPages'])
		episode_menu = episode_json['pageRecords']
		for episode_item in episode_menu:
			if episode_item['contentType'] == type:
				url = VIDEOPAGE % episode_item['id']
				try:
					episode_duration = int(_common.format_seconds(episode_item['duration']))
				except:
					episode_duration = -1
				episode_plot = episode_item['description']
				episode_airdate = episode_item['airDate']
				episode_name = episode_item['title']
				try:
					season_number = int(episode_item['season'])
				except:
					season_number = -1
				try:
					episode_number = int(episode_item['episodeNumber'])
				except:
					episode_number = -1
				try:
					episode_thumb = episode_item['editorialThumbnailUrl'].replace('/129x72xR', '')
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
				_common.add_video(u, episode_name, episode_thumb, infoLabels = infoLabels, quality_mode  = 'list_qualities')
		if page < total_pages and page < int(_addoncompat.get_setting('maxpages')):
			episode_url = episode_url.replace('page=' + str(page), 'page=' + str(page + 1))
			episodes(episode_url)
	except:
		pass
	_common.set_view('episodes')

def play_video(video_url = _common.args.url):
	try:
		qbitrate = _common.args.quality
	except:
		qbitrate = None
	closedcaption = None
	video_data = _connection.getURL(video_url)
	video_tree = BeautifulSoup(video_data, 'html.parser')
	clip_url = SMIL_BASE + video_tree.clipurl.string
	try:
		closedcaption = video_tree.find('fileurl').string
	except:
		pass
	smil_data = _connection.getURL(clip_url)
	smil_tree = BeautifulSoup(smil_data, 'html.parser')
	base_url = get_rtmp()
	print "TREE",smil_tree
	video_url2 = smil_tree.switch.find_all('video')
	hbitrate = -1
	sbitrate = int(_addoncompat.get_setting('quality')) * 1024
	if qbitrate is None:
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
	if (_addoncompat.get_setting('enablesubtitles') == 'true') and (closedcaption is not None):
				convert_subtitles(closedcaption)
	finalurl = base_url + ' playpath=' + playpath_url + ' swfurl=' + SWFURL + ' swfvfy=true'
	item = xbmcgui.ListItem(path = finalurl)
	if qbitrate is not None:
		item.setThumbnailImage(_common.args.thumb)
		item.setInfo('Video', {	'title' : _common.args.name,
						'season' : _common.args.season_number,
						'episode' : _common.args.episode_number})
	xbmcplugin.setResolvedUrl(pluginHandle, True, item)
	if (_addoncompat.get_setting('enablesubtitles') == 'true') and (closedcaption is not None):
		while not xbmc.Player().isPlaying():
			xbmc.sleep(100)
		xbmc.Player().setSubtitles(_common.SUBTITLE)

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
	for i, line in enumerate(lines):
		try:
			if line is not None:
				sub = clean_subs(_common.smart_utf8(line))
				start_time = _common.smart_utf8(line['begin'].replace('.', ','))
				end_time = _common.smart_utf8(line['end'].replace('.', ','))
				str_output += str(i + 1) + '\n' + start_time + ' --> ' + end_time + '\n' + sub + '\n\n'
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
	video_tree = BeautifulSoup(video_data, 'html.parser')
	clip_url = SMIL_BASE + video_tree.clipurl.string
	smil_data = _connection.getURL(clip_url)
	smil_tree = BeautifulSoup(smil_data, 'html.parser')
	video_url2 = smil_tree.switch.find_all('video')
	for video_index in video_url2:
		bitrate = int(video_index['system-bitrate'])
		display = int(bitrate)/1024
		bitrates.append((display, bitrate))
	return bitrates
