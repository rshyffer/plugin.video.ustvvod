#!/usr/bin/python
# -*- coding: utf-8 -*-
import common
import connection
import re
import simplejson
import sys
import urllib
import ustvpaths
import xbmc
import xbmcaddon
import xbmcgui
import traceback
import xbmcplugin
from bs4 import BeautifulSoup, SoupStrainer

addon = xbmcaddon.Addon()
pluginHandle = int(sys.argv[1])

SITE = "food"
NAME = "Food Network"
DESCRIPTION = "FOOD NETWORK (www.foodnetwork.com) is a unique lifestyle network and Web site that strives to be way more than cooking.  The network is committed to exploring new and different ways to approach food - through pop culture, competition, adventure, and travel - while also expanding its repertoire of technique-based information. Food Network is distributed to more than 96 million U.S. households and averages more than seven million Web site users monthly. With headquarters in New York City and offices in Atlanta, Los Angeles, Chicago, Detroit and Knoxville, Food Network can be seen internationally in Canada, Australia, Korea, Thailand, Singapore, the Philippines, Monaco, Andorra, Africa, France, and the French-speaking territories in the Caribbean and Polynesia. Scripps Networks Interactive (NYSE: SNI), which also owns and operates HGTV (www.hgtv.com), DIY Network (www.diynetwork.com), Great American Country (www.gactv.com) and FINE LIVING (www.fineliving.com), is the manager and general partner."
SHOWS = "http://www.foodnetwork.com/shows/a-z.html"
BASE  = "http://foodnetwork.com"

def masterlist():
	master_db = []
	master_dict = {}
	dupes = []
	master_data = connection.getURL(SHOWS)
	master_tree =  BeautifulSoup(master_data, 'html.parser')#, parse_only = SoupStrainer('shows-a-z'))
	master_menu = master_tree.find('div', class_ = 'shows-a-z').find_all('span', class_ = "arrow")
	for master_item in master_menu:
		try:
			master_name = master_item.a.string
			master_url = master_item.a['href']
			master_db.append((master_name, SITE, 'seasons', master_url))
		except Exception, e:
			print e
	return master_db

def seasons(season_urls = common.args.url):
	seasons = []
	root_url = season_urls
	season_urls = BASE + season_urls
	season_data = connection.getURL(season_urls)
	try:
		season_tree = BeautifulSoup(season_data)
		video_link = BASE + season_tree.find('a', text = re.compile('Videos? \(\d+\)'))['href']
		season_data = connection.getURL(video_link)
		video_tree = BeautifulSoup(season_data)
		season_menu = video_tree.find_all('option')
		print season_menu
		if season_menu:
			for season_item in season_menu:
				print season_item
				season_name = season_item.string
				season_url = BASE + season_item['value']
				seasons.append((season_name,  SITE, 'episodes', season_url, -1, -1))
		else:
			seasons.append(('Clips',  SITE, 'episodes', video_link, -1, -1))
	except:
		try:
			season_title = re.compile('"channels": \[\{\s+"title": "(.*?)",\s+"start": \d+,\s+"end": \d+,\s+"total": \d+,\s+"videos":', re.DOTALL).findall(season_data)[0]
			seasons.append((season_title,  SITE, 'episodes', season_urls, -1, -1))
		except:
			season_tree = BeautifulSoup(season_data)
			season_menu = season_tree.find_all(class_ = 'ss-play')
			for season_item in season_menu:
				season_grandparent = season_item.parent.parent.parent
				try:
					try:
						season_name = season_grandparent.img['title']
					except:
						season_name = season_grandparent.h6.string#img['title']
					print season_name
					try:
						season_url = BASE + season_grandparent['href']
					except:
						season_url = BASE + season_grandparent.a['href']
					print season_url
					if 'shows' in season_url or 'packages' in season_url or 'chef' in season_url:
						seasons.append((season_name,  SITE, 'episodes', season_url, -1, -1))
				except:
					print season_grandparent
	return seasons

def episodes(episode_url = common.args.url):
	episodes = []
	episode_data = connection.getURL(episode_url)
	episode_json = re.compile('"videos":\s+(\[.*?\])', re.DOTALL).findall(episode_data)[0]
	episode_menu = simplejson.loads(episode_json)
	for episode_item in episode_menu:
		HD = False
		url = episode_item['releaseUrl']
		episode_duration = int(episode_item['length_sss'])
		episode_name = episode_item['title']
		try:
			episode_cast = [episode_item['hostName']]
		except:
			episode_cast = []
		try:
			episode_thumb = episode_item['thumbnailUrl']
		except:
			episode_thumb = None
		episode_plot = episode_item['description']
		show_title = episode_item['showName']
		episode_type = 'Clip'
		if url is not None:
			u = sys.argv[0]
			u += '?url="' + urllib.quote_plus(url) + '"'
			u += '&mode="' + SITE + '"'
			u += '&sitemode="play_video"'
			infoLabels={	'title' : episode_name,
							'durationinseconds' : episode_duration,
							'plot' : episode_plot,
							'TVShowTitle': show_title,
							'cast' : episode_cast}
			episodes.append((u, episode_name, episode_thumb, infoLabels, None, HD, episode_type))
	return episodes


def play_video(video_url = common.args.url):
	try:
		qbitrate = common.args.quality
	except:
		qbitrate = None
	closedcaption = None
	#mp4 works but no bitrate selection
	video_url = video_url + '?manifest=m3u'
	video_data = connection.getURL(video_url)
	video_tree = BeautifulSoup(video_data, 'html.parser')
	if  video_tree.find('param', attrs = {'name' : 'isException', 'value' : 'true'}) is None:
		playpath_url = video_tree.video['src']
		
		try:
			closedcaption = video_tree.find('textstream', type = 'text/srt')['src']
		except:
			pass
		finalurl = playpath_url
		item = xbmcgui.ListItem( path = finalurl)
		
		try:
			item.setThumbnailImage(common.args.thumb)
		except:
			pass
		try:
			item.setInfo('Video', {	'title' : common.args.name,
							 'season' : common.args.season_number,
							 'episode' : common.args.episode_number})
		except:
			pass
		xbmcplugin.setResolvedUrl(pluginHandle, True, item)
		if (addon.getSetting('enablesubtitles') == 'true') and (closedcaption is not None):
			while not xbmc.Player().isPlaying():
				xbmc.sleep(100)
			xbmc.Player().setSubtitles(closedcaption)
	else:
		common.show_exception(video_tree.ref['title'], video_tree.ref['abstract'])

