#!/usr/bin/python
# -*- coding: utf-8 -*-
import _addoncompat
import _common
import _connection
import HTMLParser
import simplejson
import sys
import re
import urllib
import xbmcgui
import xbmcplugin
from bs4 import BeautifulSoup, SoupStrainer

pluginHandle = int(sys.argv[1])

SITE = 'aetv'
NAME = 'A&E'
DESCRIPTION = "A&E is Real Life. Drama.  Now reaching more than 99 million homes, A&E is television that you can't turn away from; where unscripted shows are dramatic and scripted dramas are authentic.  A&E offers a diverse mix of high quality entertainment ranging from the network's original scripted series to signature non-fiction franchises, including the Emmy-winning \'Intervention,\' \'Dog The Bounty Hunter,\' \'Hoarders,\' \'Paranormal State\' and \'Criss Angel Mindfreak,\' and the most successful justice shows on cable, including \'The First 48\' and \'Manhunters.\'  The A&E website is located at www.aetv.com."
SHOWS = 'http://www.aetv.com/allshows.jsp'
BASE  = 'http://www.aetv.com'
SEASONSCLIPS = 'http://www.aetv.com/minisite/videoajx.jsp?homedir=%s&pfilter=CLIPS'
SEASONSEPISODES = 'http://www.aetv.com/minisite/videoajx.jsp?homedir=%s&pfilter=FULL%%20EPISODES'
CLIPS = 'http://www.aetv.com/minisite/videoajx.jsp?homedir=%s&pfilter=CLIPS&sfilter=%s'
FULLEPISODES = 'http://www.aetv.com/views/ajax?view_name=video_playlist_view&view_display_id=block&view_args=%s&view_path=&view_base_path=&view_dom_id=1&pager_element='

def masterlist():
	master_db = []
	master_data = _connection.getURL(SHOWS)
	master_tree = BeautifulSoup(master_data, 'html5lib')
	master_menu = master_tree.find('div', id= 'shows-list').find_all('a')
	for master_item in master_menu:
		master_name = _common.smart_utf8(master_item.text)
		master_db.append((master_name, SITE, 'seasons', master_item['href']))
	return master_db

def rootlist():
	show_data = _connection.getURL(SHOWS)
	show_tree = BeautifulSoup(show_data, 'html5lib')
	show_menu = show_tree.find('div', id='shows-list').find_all('a')
	for show_item in show_menu:
		show_name = _common.smart_utf8(show_item.text)
		_common.add_show(show_name,  SITE, 'seasons', show_item['href'])
	_common.set_view('tvshows')

def seasons(url = _common.args.url):
	homedir = url.split('/')[-1].replace('-','+')
	print homedir
	season_url = FULLEPISODES % homedir
	season_data = _connection.getURL(season_url)
	season_menu = simplejson.loads(season_data)[2]['data']
	season_tree = BeautifulSoup(season_menu, 'html.parser', parse_only = SoupStrainer('ul', id= 'full-episode-ul'))
	season_db = []
	for season in season_tree.find('ul', id= 'full-episode-ul').find_all('li'):
		primary = season['data-field_primary_filter_value']
		secondary = season['data-field_season_value']
		if (primary, secondary) not in season_db:
			season_db.append((primary, secondary))
			_common.add_directory(primary + ' ' + secondary,  SITE, 'episodes', season_url + '#' + primary + '#' + secondary)
	_common.set_view('seasons')

def episodes(episode_url = _common.args.url):
	filter = episode_url.split('#')[1]
	season = episode_url.split('#')[2]
	episode_url = episode_url.split('#')[0]
	episode_data = _connection.getURL(episode_url)
	episode_tree = simplejson.loads(episode_data)[2]['data']
	episode_menu = BeautifulSoup(episode_tree, 'html.parser', parse_only = SoupStrainer('ul', id= 'full-episode-ul'))
	for episode_item in episode_menu.find_all('li', {'data-field_primary_filter_value' : filter , 'data-field_season_value' : season}):
		if 'locked' not in episode_item['class']:
			url = episode_item['data-public-url']
			episode_duration = episode_item['data-duration']
			episode_duration = int(_common.format_seconds(episode_duration))
			try:
				episode_airdate = _common.format_date(episode_item['data-date'].split(': ')[1],'%m/%d/%Y')
			except:
				episode_airdate = -1
			episode_name = HTMLParser.HTMLParser().unescape(episode_item['data-title'])
			try:
				season_number = int(episode_item['data-season'])
			except:
				season_number = -1
			try:
				episode_number = int(episode_item['data-episode'])
			except:
				episode_number = -1
			try:
				episode_thumb = episode_item.find('img')['data-src']
			except:
				try:
					episode_thumb = episode_item.find('img')['src']
				except:
					episode_thumb = None
			episode_plot = HTMLParser.HTMLParser().unescape(episode_item['data-description'])
			episode_showtitle = episode_item['data-page-title'].split('-')[1].strip()
			episode_MPAA = episode_item['data-rating']
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
							'MPAA' : episode_MPAA}
			_common.add_video(u, episode_name, episode_thumb, infoLabels = infoLabels)
	_common.set_view('episodes')

def play_video(video_url = _common.args.url):
	sig = sign_url(video_url)
	smil_url = video_url + '?sig=' + sig
	smil_data = _connection.getURL(smil_url)
	video_tree = BeautifulSoup(smil_data, 'html.parser')
	video_url2 = video_tree.seq.find_all('video')
	stacked_url = 'stack://'
	for segment in video_url2:
			stacked_url = segment['src'] + ' , '
	finalurl = stacked_url[:-3]
	xbmcplugin.setResolvedUrl(pluginHandle, True, xbmcgui.ListItem(path = finalurl))

def sign_url(url):
	sig = _connection.getURL('http://www.history.com/components/get-signed-signature?url=' + re.compile('/[sz]/(.+)\??').findall(url)[0])
	return sig
