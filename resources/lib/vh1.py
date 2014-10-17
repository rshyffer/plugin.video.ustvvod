#!/usr/bin/python
# -*- coding: utf-8 -*-
import _common
import _connection
import _main_viacom
import sys
import urllib
from bs4 import BeautifulSoup, SoupStrainer

pluginHandle = int(sys.argv[1])

SITE = 'vh1'
NAME = 'VH1'
DESCRIPTION = "VH1 connects viewers to the music, artists and pop culture that matter to them most with series, specials, live events, exclusive online content and public affairs initiatives. VH1 is available in 90 million households in the U.S. VH1 also has an array of digital services including VH1 Classic, VH1 Soul and VSPOT, VH1's broadband channel. Connect with VH1 at www.VH1.com."
BASE = 'http://www.vh1.com'
SHOWS = 'http://www.vh1.com/shows/all_vh1_shows.jhtml'

blacklist = [   "14th Annual Critics' Choice Awards (2009)",
                "17th Annual Critics' Choice Movie Awards",
                "40 Winningest Winners of 2011 (Hour 2)",
                '2009 Hip Hop Honors',
                '2010 Hip Hop Honors',
                "America's Most Smartest Model",
                'Behind the Crime Scene: Tupac Shakur',
                'Top 40 Videos of 2009 Hour 2 (20-1)',
                'Top 40 Videos of 2009 Hour 1 (40-21)',
                "Critics' Choice Movie Awards (2010)",
                "Critics' Choice Movie Awards (2011)",
                'DIVAS (2010)',
                'Do Something Awards 2010',
                'Do Something Awards 2011',
                'Do Something Awards 2012',
                'Do Something Awards 2013',
                'Front Row',
                'Movies That Rock!',
                'Pop Up Video',
                'Posted',
                'Rock Honors: The Who',
                'Stand Up To Cancer',
                'Top 40 Videos of 2009 Hour 1',
                'Top 40 Videos of 2009 Hour 2',
                'VH1 Big In 2006 Awards',
                'VH1 Divas (2009)',
                'VH1 Divas Celebrates Soul',
                'VH1 Pop Up Video'
                ]

multiseason = [ ['Basketball Wives', 'Basketball Wives'],
                ['Brandy & Ray J: A Family Business','Brandy & Ray J: A Family Business 2'],
                ['Celebrity Rehab','Celebrity Rehab 5'],
                ['Fantasia For Real','Fantasia For Real 2'],
                ["La La's Full Court Life","La La's Full Court Life"],
                ['Love & Hip Hop','Love & Hip Hop'],
                ['Mob Wives','Mob Wives'],
                ["Rock N' Roll Fantasy Camp","Rock N' Roll Fantasy Camp -  2"],
                ["RuPaul's Drag Race","RuPaul's Drag Race 3"],
                ['Scream Queens','Scream Queens 2'],
                ['Single Ladies','Single Ladies'],
                ['The T.O. Show','The T.O. Show 3'],
                ['Tough Love','Tough Love New Orleans'],
                ['What Chilli Wants','What Chilli Wants 2'],
                ["You're Cut Off!","You're Cut Off!"]
                ]

def masterlist():
	master_db = []
	master_data = _connection.getURL(SHOWS)
	master_tree = BeautifulSoup(master_data, 'html.parser', parse_only = SoupStrainer('div', id = 'inner'))
	master_menu = master_tree.find_all('div', class_ = 'alpha-group')
	for master_tree2 in master_menu:
		for master_item in master_tree2.find_all('a'):
			master_name = master_item.text.replace('Season','').strip()
			season_url = master_item['href'].replace('series.jhtml','video.jhtml?sort=descend')
			mode = 'show_subcats'
			if BASE not in season_url:
				season_url = BASE + season_url
			if master_name in blacklist:
				continue
			elif '/shows/events' in season_url:
				continue
			docontinue = False
			for series_name, choosen in multiseason:
				if series_name in master_name:
					if choosen is not master_name:
						docontinue = True
					elif choosen == master_name:
						master_name = series_name
						mode = 'seasons'
			if docontinue is True:
				continue
			if '(' in master_name:
				master_name = master_name.split('(')[0].strip()
			master_db.append((master_name, SITE, mode, season_url))
	return master_db

def seasons(url = _common.args.url):
	show_data = _connection.getURL(url)
	show_tree = BeautifulSoup(show_data)
	season_menu = show_tree.find('select', id = 'videolist_id')
	if season_menu:
		season_menu2 = season_menu.find_all('option')
		for season_item in season_menu2:
			season_url = BASE + season_item['value']
			season_name = season_item.text
			_common.add_directory(season_name, SITE, 'season_options', season_url)
		_common.set_view('seasons')

def season_options(url = _common.args.url):
	_common.add_directory('All Videos', SITE,'add_videos',url)
	_common.add_directory('Full Episodes', SITE, 'add_videos', url + 'fulleps')
	_common.add_directory('Bonus Clips', SITE, 'add_videos', url + 'bonusclips')
	_common.add_directory('After Shows', SITE, 'add_videos', url + 'aftershows')
	_common.add_directory('Sneak Peeks', SITE, 'add_videos', url + 'sneakpeeks')
	_common.set_view('seasons')

def show_subcats(url = _common.args.url):
	show_data = _connection.getURL(url)
	show_tree = BeautifulSoup(show_data, 'html.parser', parse_only = SoupStrainer('div', class_ = 'group-a'))
	subs = show_tree.find_all('a')
	for sub in subs:
		name = sub.string
		url = sub['href']
		if BASE not in url:
			url = BASE + url
		if name is None:
			name = sub.contents[-1]
		if 'Episodes' in name or 'Clips' in name or 'Peeks' in name or 'Watch' in name or 'Video' in name:
			if 'id=' in url:
				u = sys.argv[0]
				u += '?url="' + urllib.quote_plus(url) + '"'
				u += '&mode="' + SITE + '"'
				u += '&sitemode="playurl"'
				item = xbmcgui.ListItem(name)
				item.setInfo(type = 'video', infoLabels = {'title' : name})
				item.setProperty('isplayable', 'true')
				xbmcplugin.addDirectoryItem(pluginHandle, url = u, listitem = item, isFolder = False)
			else:
				_common.add_directory(name, SITE, 'add_videos', url)
	_common.set_view('seasons')

def add_videos(url=_common.args.url):
	episode_data = _connection.getURL(url)
	episode_tree = BeautifulSoup(episode_data)
	episode_subs = episode_tree.find(class_ = 'group-b')
	try:
		try:
			finalsubs = episode_subs.find(class_ = 'video-list').find_all('tr', class_ = True)
		except:
			try:
				finalsubs = episode_subs.find(id = 'vid_mod_1').find_all(itemscope = True)
			except:
				finalsubs = tree.find(id = 'vid_mod_1').find_all(itemscope = True)
		for sub in finalsubs:
			sub = sub.find('a')
			name = sub.text
			url = sub['href']
			if BASE not in url:
				url = BASE + url
			u = sys.argv[0]
			u += '?url="' + urllib.quote_plus(url) + '"'
			u += '&mode="' + SITE + '"'
			u += '&sitemode="play_url"'
			_common.add_video(u, name, '', infoLabels = {'title' : name}, quality_mode  = 'list_qualities')
		_common.set_view('episodes')
	except:
		pass

def play_url(video_uri = _common.args.url):
	video_data = _connection.getURL(video_uri)
	video_tree = BeautifulSoup(video_data)
	video_uri = video_tree.find('link', rel = 'video_src')['href'].split('/')[-1]
	video_url = video_uri
	_main_viacom.play_video(BASE, video_url)	

def list_qualities(video_uri = _common.args.url):
	video_data = _connection.getURL(video_uri)
	video_tree = BeautifulSoup(video_data)
	video_uri = video_tree.find('link', rel = 'video_src')['href'].split('/')[-1]
	video_url = video_uri
	return _main_viacom.list_qualities(BASE, video_url)
