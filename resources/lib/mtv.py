#!/usr/bin/python
# -*- coding: utf-8 -*-
import _addoncompat
import _common
import _connection
import _main_viacom
import sys
import re
import urllib
from bs4 import BeautifulSoup, SoupStrainer

pluginHandle = int(sys.argv[1])

SITE = 'mtv'
NAME = 'MTV'
DESCRIPTION = "MTV is Music Television. It is the music authority where young adults turn to find out what's happening and what's next in music and popular culture. MTV reaches 412 million households worldwide, and is the #1 Media Brand in the world. Only MTV can offer the consistently fresh, honest, groundbreaking, fun and inclusive youth-oriented programming found nowhere else in the world. MTV is a network that transcends all the clutter, reaching out beyond barriers to everyone who's got eyes, ears and a television set."
BASE = 'http://www.mtv.com'
SHOWSAZ = 'http://www.mtv.com/shows/azfilter/?template=%%2Fshows%%2Fhome2%%2Fmodules%%2FazFilter&startingCharac=%s&resultSize=500'
SHOWS = 'http://www.mtv.com/shows/'
TYPES = [('fulleps' , 'Full Episodes'), ('bonusclips' , 'Bonus Clips'), ('aftershows', 'After Shows'), ('sneakpeaks' , 'Sneak Peeks'), ( 'showclips' , 'Show Clips'), ('recaps' , 'Recaps')]

def masterlist(master_url = SHOWS):
	master_db, doubles = add_master_shows(SHOWS)
	return master_db

def add_master_shows(url, doubles = [], master_db = []):
	master_dict = {}
	root_dict = {}
	for i in range(ord('a') - 1, ord('z') + 1):
		if i < ord('a'):
			url = SHOWS
		else:
			url = SHOWSAZ % chr(i)
		master_data = _connection.getURL(url)
		master_tree = BeautifulSoup(master_data, 'html5lib')
		master_menu = master_tree.find_all('a', attrs = {'data-report' : 'SHOWS_HUB:SHOWS_AZ:SHOW'})
		for master_item in master_menu:
			master_name = master_item.text
			season = re.compile(r' \(Season \d+\)')
			master_name = season.sub('', master_name).strip()
			season_url = master_item['href'].replace('series.jhtml', 'video.jhtml?sort=descend')
			if BASE not in season_url:
				season_url = BASE + season_url
			if season_url.split('season')[0].replace('video.jhtml?sort=descend','') not in doubles:
				tvdb_name = _common.get_show_data(master_name,SITE, 'seasons')[-1]
				if tvdb_name not in master_dict.keys():
					master_dict[tvdb_name] = season_url
				else:
					master_dict[tvdb_name] = master_dict[tvdb_name] + ',' + season_url
				doubles.append(season_url.split('season')[0].replace('video.jhtml?sort=descend',''))
	for master_name, season_url in master_dict.iteritems():
		master_db.append((master_name, SITE, 'seasons', season_url))
	next = master_tree.find('a', class_ = 'page-next')
	if next:
		master_db, doubles = add_master_shows(BASE + next['href'], doubles, master_db)
	return master_db, doubles
	
def seasons(url = _common.args.url):
	if 'shows' in url:
		for type in TYPES:
			for season_item in url.split(','):		
				show_cat_url = season_item + '&filter=' + type[0]
				show_cat_data = _connection.getURL(show_cat_url)
				show_cat_tree = BeautifulSoup(show_cat_data, 'html5lib')
				if show_cat_tree.div:
					if ',' in url:
						title = show_cat_tree.find('option', selected = True).string + ' ' + type[1]
					else:
						title = type[1]
					if 'season' in season_item:
						season_menu = show_cat_tree.find_all('option')
						for season_subitem in season_menu:
							season_name = season_subitem.string
							season_url = BASE + season_subitem['value'] 
							_common.add_directory(season_name + ' ' + title, SITE, 'episodes', season_url)
					else:
						_common.add_directory(title, SITE, 'episodes', show_cat_url)
	else:
		_common.add_directory('Specials', SITE, 'episodes', url)
		_common.set_view('seasons')

def episodes(url =_common.args.url, page = 1):
	episode_data = _connection.getURL(url)
	episode_tree = BeautifulSoup(episode_data, 'html5lib')
	next = episode_tree.find('div', id = 'loadMore')		    
	add_video(episode_tree)
	if next is not None:
		if 'prev' not in next.a['rel']:
			try:
				show = url.split('/')[4]
				if 'href' in next.a.attrs:
					nexturl = next.a['href'].replace('null', show)			
				if 'http' not in nexturl:
					nexturl = BASE + nexturl
				if page < int(_addoncompat.get_setting('maxpages')):
					episodes(nexturl, page + 1)
			except:
				pass
			
def add_video(episode_tree):
	episode_menu = episode_tree.find_all(itemtype = "http://schema.org/VideoObject", maincontent = re.compile('^((?!(quarantineDate|<b>)).)*$'))
	if not episode_menu:
		episode_menu = episode_tree.find_all(attrs = {'data-uri' : True, 'data-filter' : re.compile(_common.args.name.replace(' ', ''))})
	for episode_item in episode_menu:
		if not episode_item.find(class_ = "disabled-video"):
			try:
				episode_url = episode_item['mainuri']
			except:
				try:
					episode_url = BASE + episode_item.find(itemprop = "url")['href']
				except:
					episode_url = episode_item['data-uri']
			try:
				name =  episode_item.find(itemprop = "name")['content']
			except:
				try:
					name =  episode_item.find(itemprop = "name").string
				except:
					try:
						name =  episode_item.find(class_ = "sub-header").text.strip()
					except:
						try:
							name =  episode_item.find(class_ = "headline").text.strip()
						except:
							name =  episode_item.find(class_ = "header").text.strip()
			try:
				thumb =  episode_item.find(itemprop = "thumbnail")['content']
			except:
				try:
					thumb =  episode_item.find(itemprop = "thumbnail")['src']
				except:
					try:
						thumb =  episode_item.find(attrs ={'data-src' : True})['data-src']
					except:
						thumb = ''
			if 'http' not in thumb and thumb != '':
				thumb = BASE + thumb
			try: 
				plot = episode_item.find(itemprop = "description")['content']
			except:
				try: 
					plot = episode_item.find(class_ = "deck").text
				except:
					plot = ''
			plot = plot.replace('<i>', '').replace('</i>', '')
			try:
				episode_number = int(re.compile('s[0-9]/e([0-9]?[0-9])').findall(episode_item.find(class_ = "header").text.strip())[0])
			except:
				try:
					try:
						episode_number = episode_item.find('li', class_ ='list-ep').string
					except:
						episode_number = int(re.compile('[0-9]?([0-9]?[0-9])').findall(name)[0])
				except:
					episode_number = -1
			try:
				season_number = int(re.compile('Season ([0-9]+)').findall(_common.args.name + episode_item.a.string)[0])
			except:
				try:
					season_number = int(re.compile('([0-9])[0-9][0-9]').findall(name)[0])
				except:
					try:
						season_number = int(re.compile('s([0-9])/e[0-9]?[0-9]').findall(episode_item.find(class_ = "header").text.strip())[0])
					except:
						season_number = -1
			try:
				name = re.compile('\(([^0-9]+)\)').findall(name)[0]
			except: 
				try:
					name = re.compile('[\-:|(](.+?)(?: \(|$|\))').findall(name)[0]
				except: 
					pass
			try:
				airDate = episode_item.find(itemprop = "uploadDate")['content']
				airDate = _common.format_date(airDate, '%y-%m-%d') 
			except:
				try:
					airDate = episode_item.find(itemprop = "datePublished").string.split(' ')[0]
					airDate = _common.format_date(airDate, '%m/%d/%y') 
				except:
					try:
						airDate = episode_item.find(class_ = "meta").text.split(' ')[-1].strip()
						airDate = _common.format_date(airDate, '%m/%d/%y') 
					except:
						airDate = -1
			try:
				duration = episode_item.find(class_ = "meta").text.split('-')[0].strip()
				durationinseconds = _common.format_seconds(duration)
			except:
				durationinseconds = -1
			u = sys.argv[0]
			u += '?url="' + urllib.quote_plus(episode_url) + '"'
			u += '&mode="' + SITE + '"'
			u += '&sitemode="play"'
			_common.add_video(u, name, thumb, infoLabels = {'title' : name, "Episode" : episode_number, "Season" : season_number, "Plot" : plot, "premiered" : airDate, "durationinseconds" : durationinseconds}, quality_mode  = 'list_qualities')
			_common.set_view('episodes')
			
def play(video_uri = _common.args.url):
	if BASE in video_uri:
		video_data = _connection.getURL(video_uri)
		video_tree = BeautifulSoup(video_data)
		video_uri = video_tree.find('meta', {'name' : 'mtvn_uri'})['content']
	video_url = video_uri
	_main_viacom.play_video(BASE, video_url)	

def list_qualities(video_uri = _common.args.url):
	if BASE in video_uri:
		video_data = _connection.getURL(video_uri)
		video_tree = BeautifulSoup(video_data)
		video_uri = video_tree.find('meta', {'name' : 'mtvn_uri'})['content']
	video_url = video_uri
	return _main_viacom.list_qualities(BASE, video_url)
