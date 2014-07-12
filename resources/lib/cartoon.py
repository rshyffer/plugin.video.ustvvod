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
from bs4 import BeautifulSoup

pluginHandle = int(sys.argv[1])

SITE = 'cartoon'
NAME = "Cartoon Network"
DESCRIPTION = "Cartoon Network (CartoonNetwork.com), currently seen in more than 97 million U.S. homes and 166 countries around the world, is Turner Broadcasting System, Inc.'s ad-supported cable service now available in HD offering the best in original, acquired and classic entertainment for youth and families.  Nightly from 10 p.m. to 6 a.m. (ET, PT), Cartoon Network shares its channel space with Adult Swim, a late-night destination showcasing original and acquired animated and live-action programming for young adults 18-34 "
SHOWS = 'http://www.cartoonnetwork.com/video/staged/CN2.mobile.configuration.xml'
CLIPS = 'http://cnvideosvc2.cartoonnetwork.com/svc/episodeSearch/getAllEpisodes?networkName=CN2?limit=400&offset=0&sortByDate=DESC&filterByEpisodeType=CLI-CLI&filterByCollectionId=%s&filterBySeasonNumber=%s'
FULLEPISODES = 'http://cnvideosvc2.cartoonnetwork.com/svc/episodeSearch/getAllEpisodes?networkName=CN2?limit=400&offset=0&sortByDate=DESC&filterByEpisodeType=TVE&filterByCollectionId=%s&filterBySeasonNumber=%s'
EPISODE = 'http://www.cartoonnetwork.com/video-seo-svc/episodeservices/getCvpPlaylist?networkName=CN2&id=%s'
AUTHURL = 'http://www.tbs.com/processors/cvp/token.jsp'
SWFURL = 'http://z.cdn.turner.com/xslo/cvp/plugins/akamai/streaming/osmf1.6/2.10/AkamaiAdvancedStreamingPlugin.swf'

def masterlist():
	master_db = []
	master_dict = {}
	master_data = _connection.getURL(SHOWS)
	master_tree = BeautifulSoup(master_data, 'html.parser')
	master_menu = master_tree.allcollections.find_all('collection')
	for master_item in master_menu:
		master_name = _common.smart_utf8(master_item['name'])
		if '[AD]' not in master_name:
			tvdb_name = _common.get_show_data(master_name, SITE, 'seasons')[-1]
			season_url = master_item['id'] 
			season_url = season_url + '#tveepisodes='
			try:
				for season in master_item.tveepisodes.find_all('season'):
					season_url = season_url + '-' + season['number']
			except:
				pass
			season_url = season_url + '#clips='
			try:
				for season in master_item.clips.find_all('season'):
					if season['number'] != '':
						season_url = season_url + '-' + season['number']
				else:
					season_url = season_url + '-' + '*'
			except:
				pass
			master_db.append((master_name,  SITE, 'seasons', season_url))
	return master_db

def seasons(season_string = _common.args.url):
	collection_id = season_string.split('#')[0]
	tve = season_string.split('#')[1].split('=')[1][1:]
	clips = season_string.split('#')[2].split('=')[1][1:]
	for season in tve.split('-'):
		if season:
			_common.add_directory('Season ' + season,  SITE, 'episodes', FULLEPISODES % (collection_id, season))
	for season in clips.split('-'):
		if season:
			if season != '*':
				display = 'Clips Season ' + season
			else:
				display = 'Specials'
			_common.add_directory(display,  SITE, 'episodes', CLIPS % (collection_id, season.replace('*', '')))
	
	_common.set_view('seasons')

def episodes(episode_url = _common.args.url):
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
		if episode_season_number == season_number:
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

def play_video(video_id = _common.args.url):
	video_url = EPISODE % video_id
	hbitrate = -1
	sbitrate = int(_addoncompat.get_setting('quality')) * 1024
	closedcaption = None
	video_data = _connection.getURL(video_url)
	video_tree = BeautifulSoup(video_data, 'html.parser')
	video_tree = BeautifulSoup(video_data)
	video_menu = video_tree.find_all('file')
	hbitrate = -1
	file_url = None
	for video_index in video_menu:
		try:
			bitrate = int(video_index['bitrate'])
			type = video_index['type']
			if bitrate > hbitrate and bitrate <= sbitrate:
				hbitrate = bitrate
				file_url = video_index.string
			elif bitrate == hbitrate and bitrate <= sbitrate:
				file_url = video_index.string
		except:
			pass
	if file_url is None:
		file_url = BeautifulSoup(video_data).find_all('file')[0].string
	if 'http' not in file_url:
		filename = file_url[1:len(file_url)-4]
		serverDetails = video_tree.find('akamai')
		server = serverDetails.find('src').string.split('://')[1]
		tokentype = serverDetails.find('authtokentype').string
		window = serverDetails.find('window').string
		aifp = serverDetails.find('aifp').string
		auth=getAUTH(aifp,window,tokentype,video_id,filename.replace('mp4:',''))      
		rtmp = 'rtmpe://'+server+'?'+auth+' playpath='+filename + ' swfurl=' + SWFURL + ' swfvfy=true'# ' swfUrl=http://z.cdn.turner.com/xslo/cvp/plugins/akamai/streaming/osmf1.6/2.10/AkamaiAdvancedStreamingPlugin.swf'
		finalurl = rtmp
	else:
		finalurl = file_url
	xbmcplugin.setResolvedUrl(pluginHandle, True, xbmcgui.ListItem(path = finalurl))

def getAUTH(aifp,window,tokentype,vid,filename):
	parameters = {'aifp' : aifp,
				'window' : window,
				'authTokenType' : tokentype,
				'videoId' : vid,
				'profile' : 'cartoon',
				'path' : filename
				}
	link = _connection.getURL(AUTHURL, parameters)
	return re.compile('<token>(.+?)</token>').findall(link)[0]

