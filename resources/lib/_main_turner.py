#!/usr/bin/python
# -*- coding: utf-8 -*-
import _addoncompat
import _common
import _connection
import sys
import urllib
import xbmcgui
import xbmcplugin
import re
import simplejson
from bs4 import BeautifulSoup

pluginHandle = int(sys.argv[1])

AUTHURL = 'http://www.tbs.com/processors/cvp/token.jsp'
SWFURL = 'http://z.cdn.turner.com/xslo/cvp/plugins/akamai/streaming/osmf1.6/2.10/AkamaiAdvancedStreamingPlugin.swf'
BASE = 'http://ht.cdn.turner.com/tbs/big/'

def masterlist(NAME, MOVIES, SHOWS, SITE):
	master_db = []
	master_dict = {}
	master_db.append(('--' + NAME + ' Movies',  SITE, 'episodes', 'Movie#' + MOVIES))
	master_data = _connection.getURL(SHOWS)
	master_menu = simplejson.loads(master_data)
	for master_item in master_menu:
		master_name = _common.smart_utf8(master_item['title'])
		season_url = master_name + '#' + master_item['ID'] 
		master_db.append((master_name,  SITE, 'seasons', season_url))
	return master_db

def seasons(SITE, FULLEPISODES, CLIPSSEASON, CLIPS):
	show_id = _common.args.url
	master_name = show_id.split('#')[0]
	show_id = show_id.split('#')[1]
	_common.add_directory('Full Episodes',  SITE, 'episodes', master_name + '#' + FULLEPISODES % show_id)
	clips_data = _connection.getURL(CLIPSSEASON % show_id)
	clips_menu = simplejson.loads(clips_data)
	for season in clips_menu:
		clip_name = _common.smart_utf8(season['title'])
		_common.add_directory(clip_name,  SITE, 'episodes', master_name + '#' + CLIPS % (show_id, season['id']))
	_common.set_view('seasons')

def episodes_json(SITE):
	episode_url = _common.args.url
	master_name = episode_url.split('#')[0]
	episode_url = episode_url.split('#')[1]
	episode_data = _connection.getURL(episode_url)
	episode_menu = simplejson.loads(episode_data)
	for episode_item in episode_menu:
		url = episode_item['episodeID']
		try:
			episode_duration = episode_item['length']
		except:
			episode_duration = -1
		try:
			episode_airdate = _common.format_date(episode_item['airDate'].split('on ')[1],'%B %d, %Y')
		except:
			episode_airdate = -1
		try:
			episode_plot = episode_item['summary']
		except:
			episode_plot = episode_item['shortdescription']
		episode_name = episode_item['title']
		if episode_name == master_name:
			video_url = EPISODE % url
			video_data = _connection.getURL(video_url)
			video_tree = BeautifulSoup(video_data, 'html.parser')
			episode_name = video_tree.headline.string
		elif episode_name == "":
			episode_name = episode_plot
		try:
			season_number = int(episode_item['identifier'].split(',')[0].split(' ')[1])
		except:
			season_number = -1
		try:
			episode_number =  int(episode_item['identifier'].split(', ')[1].split(' ')[1][1:])
		except:
			try:
				episode_number =  int(episode_item['identifier'].split(', ')[1].split(' ')[1])
			except:
				episode_number = -1
		try:
			episode_thumb = episode_item['640x360_jpg']
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

def episodes(SITE):
	episode_url = _common.args.url
	try:
		season_number = int(episode_url.split('filterBySeasonNumber=')[1])
	except:
		season_number = 0 
	episode_data = _connection.getURL(episode_url)
	episode_tree = BeautifulSoup(episode_data, 'html.parser')
	episode_menu = episode_tree.find_all('episode')
	for episode_item in episode_menu:
		try:
			episode_season_number = int(episode_item['episeasonnumber'])
		except:
			episode_season_number = 0
		print "Es", episode_season_number
		if episode_season_number == season_number or 'filterBySeasonNumber'  not in episode_url:
			print "HRE"
			segments = episode_item.find_all('segment')
			if len(segments) == 0:
				url = episode_item['id']
			else:
				url = ''
				for segment in segments:
					url = url + ',' + segment['id']
				url = url[1:]
			try:
				episode_duration = episode_item['duration']
				episode_duration = int(_common.format_seconds(episode_duration))
			except:
				episode_duration = 0
				for segment_duration in segments:
					episode_duration += float(segment_duration['duration'])
			try:
				episode_airdate = _common.format_date(episode_item['originalpremieredate'].split(' ')[0],'%m/%d/%Y')
			except:
				try:
					episode_airdate = _common.format_date(episode_item['launchdate'].split(' ')[0],'%m/%d/%Y')
				except:
					episode_airdate = -1
			episode_name = episode_item['title']
			try:
				season_number = int(episode_item['episeasonnumber'])
			except:
				season_number = -1
			try:
				episode_number = int(episode_item['episodenumber'][:2])
			except:
				episode_number = -1
			try:
				episode_thumb = episode_item['thumbnailurl']
			except:
				episode_thumb = None
			episode_plot = episode_item.description.text
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
	
def play_video(SITE, EPISODE):
	try:
		qbitrate = _common.args.quality
	except:
		qbitrate = None
	stack_url = ''
	for video_id in _common.args.url.split(','):
		video_url = EPISODE % video_id
		hbitrate = -1
		sbitrate = int(_addoncompat.get_setting('quality'))
		closedcaption = None
		video_data = _connection.getURL(video_url)
		video_tree = BeautifulSoup(video_data, 'html.parser')
		hbitrate = -1
		lbitrate = -1
		file_url = None
		if qbitrate is  None:
			video_menu = video_tree.find_all('file')
			for video_index in video_menu:
				try:
					try:
						play_mode = video_index['play_mode']
					except:
						play_mode = ''
					if play_mode != 'window':
						bitrate = int(video_index['bitrate'])
						if bitrate < lbitrate or lbitrate == -1:
							lbitrate = bitrate,sbitrate
							lfile_url = video_index.string
						if bitrate > hbitrate and bitrate <= sbitrate:
							hbitrate = bitrate
							file_url = video_index.string
				except:
					pass
			if file_url is None:
				file_url = lfile_url 
		else:
			file_url = video_tree.find('file', attrs = {'bitrate' : qbitrate}).string
		
		print file_url
		if 'mp4:'  in file_url:
			filename = file_url[1:len(file_url)-4]
			serverDetails = video_tree.find('akamai')
			server = serverDetails.find('src').string.split('://')[1]
			tokentype = serverDetails.find('authtokentype').string
			window = serverDetails.find('window').string
			aifp = serverDetails.find('aifp').string
			auth=getAUTH(aifp,window,tokentype,video_id,filename.replace('mp4:',''), SITE)      
			rtmp = 'rtmpe://' + server + '?' + auth + ' playpath=' + filename + ' swfurl=' + SWFURL + ' swfvfy=true'
			segurl = rtmp
		elif 'http' not in file_url:
			segurl = BASE + file_url
		else:
			segurl = file_url
		stack_url += segurl.replace(',', ',,') + ' , '
	if ', ' in stack_url:
		stack_url = 'stack://' + stack_url
	finalurl = stack_url[:-3]
	print finalurl
	item = xbmcgui.ListItem(path = finalurl)
	if qbitrate is not None:
		item.setThumbnailImage(_common.args.thumb)
		item.setInfo('Video', {	'title' : _common.args.name,
						'season' : _common.args.season_number,
						'episode' : _common.args.episode_number,
						'TVShowTitle' : _common.args.show_title})
	xbmcplugin.setResolvedUrl(pluginHandle, True, item)

def list_qualities(SITE, EPISODE):
	try:
		video_id = _common.args.url.split(',')[0]
	except:
		video_id = _common.args.url
	video_url = EPISODE % video_id
	video_data = _connection.getURL(video_url)
	video_tree = BeautifulSoup(video_data, 'html.parser')
	video_menu = video_tree.find_all('file')
	bitrates = []
	for video_index in video_menu:
		print video_index
		try:
			if video_index['play_mode'] != 'window':
				bitrate = video_index['bitrate']
				display = int(bitrate)
				bitrates.append((display,int(bitrate)))
		except:
			pass
	print bitrates
	return bitrates
	
def getAUTH(aifp, window, tokentype, vid, filename, site):
	parameters = {'aifp' : aifp,
				'window' : window,
				'authTokenType' : tokentype,
				'videoId' : vid,
				'profile' : site,
				'path' : filename
				}
	link = _connection.getURL(AUTHURL, parameters)
	print link
	return re.compile('<token>(.+?)</token>').findall(link)[0]

