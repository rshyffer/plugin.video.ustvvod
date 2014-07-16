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

SITE = 'tbs'
NAME = "TBS"
DESCRIPTION = "TBS, a division of Turner Broadcasting System, Inc., is television's top-rated comedy network and is available in 100.1 million households.  It serves as home to such original comedy series as My Boys, Neighbors from Hell, Are We There Yet? and Tyler Perry's House of Payne and Meet the Browns; the late-night hit Lopez Tonight, starring George Lopez, and the upcoming late-night series starring Conan O'Brien; hot contemporary comedies like Family Guy and The Office; specials like Funniest Commercials of the Year; special events, including star-studded comedy festivals in Chicago; blockbuster movies; and hosted movie showcases."
SHOWS = 'http://www.tbs.com/mobile/smartphone/android/showList.jsp'
MOVIES = 'http://www.tbs.com/mobile/ipad/feeds/movies.jsp'
CLIPSSEASON = 'http://www.tbs.com/mobile/ipad/feeds/getFranchiseCollections.jsp?franchiseID=%s'
CLIPS = 'http://www.tbs.com/mobile/ipad/feeds/franchiseEpisode.jsp?franchiseID=%s&type=0&collectionId=%s'
FULLEPISODES = 'http://www.tbs.com/mobile/ipad/feeds/franchiseEpisode.jsp?franchiseID=%s&type=1'
EPISODE = 'http://www.tbs.com/video/content/services/cvpXML.do?id=%s'
AUTHURL = 'http://www.tbs.com/processors/cvp/token.jsp'
SWFURL = 'http://z.cdn.turner.com/xslo/cvp/plugins/akamai/streaming/osmf1.6/2.10/AkamaiAdvancedStreamingPlugin.swf'

def masterlist():
	master_db = []
	master_dict = {}
	master_db.append(('--TBS Movies',  SITE, 'episodes', 'Movie#' + MOVIES))
	master_data = _connection.getURL(SHOWS)
	master_menu = simplejson.loads(master_data)
	for master_item in master_menu:
		master_name = _common.smart_utf8(master_item['title'])
		season_url = master_name + '#' + master_item['ID'] 
		master_db.append((master_name,  SITE, 'seasons', season_url))
	return master_db
	
def seasons(show_id = _common.args.url):
	master_name = show_id.split('#')[0]
	show_id = show_id.split('#')[1]
	_common.add_directory('Full Episodes',  SITE, 'episodes', master_name + '#' + FULLEPISODES % show_id)
	clips_data = _connection.getURL(CLIPSSEASON % show_id)
	clips_menu = simplejson.loads(clips_data)
	for season in clips_menu:
		clip_name = _common.smart_utf8(season['title'])
		_common.add_directory(clip_name,  SITE, 'episodes', master_name + '#' + CLIPS % (show_id, season['id']))
	_common.set_view('seasons')

def episodes(episode_url = _common.args.url):
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

def play_video(video_id = _common.args.url):
	video_url = EPISODE % video_id
	hbitrate = -1
	sbitrate = int(_addoncompat.get_setting('quality')) * 1024
	closedcaption = None
	video_data = _connection.getURL(video_url)
	video_tree = BeautifulSoup(video_data, 'html.parser')
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
	if 'mp4:'  in file_url:
		filename = file_url[1:len(file_url)-4]
		serverDetails = video_tree.find('akamai')
		server = serverDetails.find('src').string.split('://')[1]
		tokentype = serverDetails.find('authtokentype').string
		window = serverDetails.find('window').string
		aifp = serverDetails.find('aifp').string
		auth=getAUTH(aifp,window,tokentype,video_id,filename.replace('mp4:',''))      
		rtmp = 'rtmpe://'+server+'?'+auth+' playpath='+filename + ' swfurl=' + SWFURL + ' swfvfy=true'# ' swfUrl=http://z.cdn.turner.com/xslo/cvp/plugins/akamai/streaming/osmf1.6/2.10/AkamaiAdvancedStreamingPlugin.swf'
		finalurl = rtmp
	elif 'http' not in file_url:
		finalurl = "http://ht.cdn.turner.com/tbs/big/" + file_url
	else:
		finalurl = file_url
	xbmcplugin.setResolvedUrl(pluginHandle, True, xbmcgui.ListItem(path = finalurl))

def getAUTH(aifp,window,tokentype,vid,filename):
	parameters = {'aifp' : aifp,
				'window' : window,
				'authTokenType' : tokentype,
				'videoId' : vid,
				'profile' : 'tbs',
				'path' : filename
				}
	link = _connection.getURL(AUTHURL, parameters)
	return re.compile('<token>(.+?)</token>').findall(link)[0]

