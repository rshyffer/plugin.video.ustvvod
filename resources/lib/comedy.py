#!/usr/bin/python
# -*- coding: utf-8 -*-
import _addoncompat
import _common
import _connection
import _main_viacom
import re
import sys
import urllib
import simplejson
from  itertools import izip
from bs4 import BeautifulSoup, SoupStrainer

pluginHandle = int(sys.argv[1])

SITE = 'comedy'
NAME = 'Comedy Central'
DESCRIPTION = "COMEDY CENTRAL, the #1 brand in comedy, is available to over 99 million viewers nationwide and is a top-rated network among men ages 18-24 and 18-34 and adults ages 18-49.  With on-air, online and on-the-go mobile technology, COMEDY CENTRAL gives its audience access to the cutting-edge, laugh-out-loud world of comedy wherever they go.  Hit series include Tosh.0, Workaholics, Futurama, Key & Peele, Ugly Americans and the Emmy' and Peabody' Award-winning series The Daily Show with Jon Stewart, The Colbert Report and South Park.  COMEDY CENTRAL is also involved in producing nationwide stand-up tours, boasts its own record label and operates one of the most successful home entertainment divisions in the industry.  COMEDY CENTRAL is owned by, and is a registered trademark of Comedy Partners, a wholly-owned unit of Viacom Inc. (NASDAQ: VIA and VIAB).  For more information visit COMEDY CENTRAL's press Web site at www.cc.com/press or the network's consumer site at www.comedycentral.com and follow us on Twitter @ComedyCentralPR for the latest in breaking news updates, behind-the-scenes information and photos."
BASE = 'http://www.cc.com'
SHOWS = 'http://www.cc.com/shows'
VIDEOURL = 'http://media.mtvnservices.com/'
MP4URL = 'http://mtvnmobile.vo.llnwd.net/kip0/_pxn=0+_pxK=18639/44620/mtvnorigin'

def masterlist():
	master_dict = {}
	master_db = []
	master_doubles = []
	master_data = _connection.getURL(SHOWS)
	master_tree = BeautifulSoup(master_data, 'html5lib')
	master_menu = master_tree.find('div', class_ = 'full_episodes').find_all('a', href = re.compile('[^#]+'))
	for master_item in master_menu:
		if master_item['href'] == "/":
			continue
		master_name = master_item.string
		if master_name not in master_doubles and master_name.split(' with ')[0] not in master_doubles:
			season_url = master_item['href']
			master_db.append((master_name, SITE, 'seasons', season_url))
	return master_db

def rootlist():
	root_dict = {}
	root_doubles = []
	root_url = SHOWS
	root_data = _connection.getURL(root_url)
	root_tree = BeautifulSoup(root_data, 'html5lib')
	root_menu = root_tree.find('div', class_ = 'full_episodes').find_all('a', href = re.compile('[^#]+'))
	for root_item in root_menu:
		if root_item['href'] == "/":
			continue
		root_name = root_item.string
		if root_name not in root_doubles and root_name.split(' with ')[0] not in root_doubles:
			season_url = root_item['href']
			_common.add_show(root_name, SITE, 'seasons', season_url)
	_common.set_view('tvshows')

def seasons(season_url = _common.args.url):
	season_data = _connection.getURL(season_url)
	season_tree = BeautifulSoup(season_data, 'html.parser', parse_only = SoupStrainer('div'))
	if 'dailyshow'in season_url or 'colbertreport' in season_url:
		season_menu = dict()
		season_menu['href'] = season_url
		season_menu2 = dict()
		season_menu2['href'] = season_url
	else:
		season_menu = season_tree.find('a', text = re.compile('full episodes', re.IGNORECASE))
		season_menu2 = season_tree.find('a', href = re.compile('(?<!stand-up)/(video|clips)'))
	if season_menu is not None:
		season_url2 = season_menu['href']
		if 'http' not in season_url2:
			season_url2 = season_url + season_url2
		_common.add_directory('Full Episodes',  SITE, 'episodes', season_url2)
	elif 'episode' in season_url:
		if 'South Park' in _common.args.name:
			seasons = BeautifulSoup(season_data, 'html5lib').find_all('a',class_='seasonbtn')
			if seasons:
				for season in seasons:
					try:
						display = 'Season %s' %str(int(season.string))
					except:
						display = 'Special %s' %season.string
					_common.add_directory(display,  SITE, 'episodes', season['href'] )
		else:
			_common.add_directory('Full Episodes',  SITE, 'episodes', season_url)
	print season_url
	if season_menu2 is not None:
		season_url3 = season_menu2['href']
		if 'http' not in season_url3:
			season_url3 = season_url + season_url3
		_common.add_directory('Clips',  SITE, 'episodes', season_url3)
	_common.set_view('seasons')

def episodes(episode_url = _common.args.url, page = 1):
	episode_data = _connection.getURL(episode_url)
	episode_tree = None
	if page == 1:
		try:
			episode_url = re.compile("var .*Showcase.* = '(.*)'").findall(episode_data)[0]
			if 'http' not in episode_url:
				episode_url = BASE + episode_url
			episode_data = _connection.getURL(episode_url)
		except:
			try:
				episode_tree = BeautifulSoup(episode_data, 'html5lib')
				episode_url = episode_tree.find('div', class_ = 'content')['data-feed']
				episode_data = _connection.getURL(episode_url)
				episode_tree = BeautifulSoup(episode_data, 'html5lib')
			except:
				pass
	if episode_tree is  None:
		episode_tree = BeautifulSoup(episode_data, 'html5lib')
	if 'Clips' in _common.args.name  :
		if 'colbertreport' in episode_url:
			add_videos_colbertnation(episode_tree, 'videos', ['t6_lc_promo4'])
		elif 'dailyshow' in episode_url:
			add_videos_colbertnation(episode_tree, 'videos', ['t6_lc_promo5'])
		elif 'southpark' in episode_url:
			add_clips_southpark(episode_tree)
		else:
			next = episode_tree.find('a', class_ = re.compile('next'))		    
			add_video(episode_tree)
			if next is not None:
				try:
					if 'href' in next.attrs:
						nexturl = next['href'].replace(' ', '+')
					else:
						nexturl = next['onclick'].split(';')[0].replace("loadContent('", "").replace("')", "")
					if 'http' not in nexturl:
						nexturl = BASE + nexturl
					if page < int(_addoncompat.get_setting('maxpages')):
						episodes(nexturl, page + 1)
				except:
					pass
	else:
		if 'colbertreport' in episode_url:
			add_videos_colbertnation(episode_tree, 'episodes', ['t6_lc_promo1'])
		elif  'dailyshow' in episode_url:
			add_videos_colbertnation(episode_tree, 'episodes', ['t4_lc_promo1', 't6_lc_promo4'])
		elif 'southpark' in episode_url:
			add_fullepisodes_southpark(episode_tree)
		else:
			next = episode_tree.find('a', class_ = re.compile('next'))		    
			add_video(episode_tree, True)
			if next is not None:
				try:
					nexturl = next['href']
					if nexturl[0] == '?': 
						nexturl = episode_url.split('?')[0] + nexturl				
					elif 'http' not in nexturl: 
						nexturl = BASE + nexturl
					episodes(nexturl, page + 1)
				except:
					pass
	_common.set_view('episodes')

def add_videos_colbertnation(episode_tree, type, feeds):
	try:
		shows = []
		scripts = episode_tree.find_all('script')
		for script in scripts:
			if ('triforceManifestFeed') in script.string:
				triforceManifestFeed = script.string.split(' = ')[1]
				triforceManifestFeed = triforceManifestFeed.strip()[:-1] # remove last ; from string
				triforceManifestFeed = simplejson.loads(triforceManifestFeed)
				break
		for feed in feeds:
			url = triforceManifestFeed['manifest']['zones'][feed]['feed']
			data = _connection.getURL(url)
			menu = simplejson.loads(data)
			for item in menu['result'][type]:
				episode_name = item['title']
				epoch = float(item['airDate'])
				epoch = _common.convert_to_timezone(epoch, '', -5, epoch)  
				episode_airdate = _common.format_date(epoch , '', '%d.%m.%Y', epoch)
				episode_plot = item['shortDescription']
				episode_thumb = item['images'][0]['url']
				url = item['url']
				if not url:
					url = item['canonicalURL']
				try:
					season_number = item['season']['seasonNumber']
					episode_number = str(int(str(item['season']['episodeNumber'])[len(str(season_number)):]))
				except:
					season_number = -1
					episode_number = -1
				u = sys.argv[0]
				u += '?url="' + urllib.quote_plus(url) + '"'
				u += '&mode="' + SITE + '"'
				u += '&sitemode="play_video"'
				infoLabels={	'title' : episode_name,
								'season' : season_number,
								'episode' : episode_number,
								'plot' : episode_plot,
								'premiered' : episode_airdate }
				show = {'u': u, 'episode_name': episode_name, 'episode_thumb': episode_thumb, 'infoLabels': infoLabels, 'epoch': epoch}
				shows.append(show)
		if len(shows):
			shows = sorted(shows, key=lambda show: show['epoch'], reverse=True)
			for show in shows:
				_common.add_video(show['u'], show['episode_name'], show['episode_thumb'], infoLabels = show['infoLabels'], quality_mode  = 'list_qualities')
	except:
		pass

def add_fullepisodes_southpark(episode_tree):
	try:
		episode_menu = episode_tree.find('div', class_ = 'content_carouselwrap').ol.find_all('li', recursive = False)
		for episode_item in episode_menu:
			if not episode_item.find('a',class_ = 'unavailable'): 
				episode_name = episode_item.h5.string
				episode_airdate = episode_item.h6.string.replace('Original Air Date: ', '')
				episode_airdate = _common.format_date(episode_airdate , '%m.%d.%Y', '%d.%m.%Y')
				episode_plot = episode_item.p.string
				episode_thumb = episode_item.img['src'].split('?')[0]
				url = episode_item.a['href']
				try:
					season_number, episode_number = re.compile('s([0-9]{2})e([0-9]{2})').findall(url)[0]
				except:
					episode_number = -1
					season_number = -1
				u = sys.argv[0]
				u += '?url="' + urllib.quote_plus(url) + '"'
				u += '&mode="' + SITE + '"'
				u += '&sitemode="play_video"'
				infoLabels={	'title' : episode_name,
								'season' : season_number,
								'episode' : episode_number,
								'plot' : episode_plot,
								'premiered' : episode_airdate }
				_common.add_video(u, episode_name, episode_thumb, infoLabels = infoLabels, quality_mode  = 'list_qualities')
	except:
		pass

def add_video(episode_tree, episode = False):
	try:
		episode_menu = episode_tree.find_all(itemtype = 'http://schema.org/TVEpisode')
		if not episode_menu:
			episode_menu = episode_tree.find_all(itemtype = 'http://schema.org/VideoObject')
		for episode_item in episode_menu:
			if episode == False or episode_item.find(class_ = 'episode'):
				episode_name = episode_item.find('meta', itemprop = 'name')['content']
				episode_plot = episode_item.find('meta', itemprop = 'description')['content']
				url = episode_item.find('meta', itemprop = 'url')['content']
				try:
					episode_thumb = episode_item.find('meta', itemprop = 'image')['content'].split('?')[0]
					print episode_thumb
				except:
					try:
						episode_thumb = episode_item.find('meta', itemprop = 'thumbnailUrl')['content'].split('?')[0]
					except:
						episode_thumb = episode_item.find('img')['src'].split('?')[0]
				try:
					episode_airdate = episode_item.find('meta', itemprop = 'uploadDate')['content']
				except:
					try:
						episode_airdate = episode_item.find('meta', itemprop = 'datePublished')['content']
						print episode_airdate
						try:
							episode_airdate = _common.format_date(episode_airdate, '%B %d, %Y')
						except:
							episode_airdate = _common.format_date(episode_airdate, '%b %d, %Y')
						print episode_airdate
					except:
						episode_airdate = -1
				try:
					episode_duration = episode_item.find('meta', itemprop = 'duration')['content']
					try:
						duration_mins, duration_seconds = re.compile('([0-9]*)M([0-9]*)S').findall(episode_duration)[0]
						episode_duration_seconds = int(duration_mins) * 60 + int(duration_seconds)
					except:
						episode_duration_seconds = int(episode_duration.replace('S', '').replace('T',''))
				except:
					episode_duration_seconds = -1
				try:
					episode_meta = episode_item.find('div', class_ = 'video_meta').text.split('|')[0]
					season_number = int(episode_meta.split('-')[0].replace('Season', '').strip())
					episode_number = int(episode_meta.split('-')[1].replace('Episode', '').strip()[1:])
				except:
					season_number = -1
					episode_number = -1
				u = sys.argv[0]
				u += '?url="' + urllib.quote_plus(url) + '"'
				u += '&mode="' + SITE + '"'
				u += '&sitemode="play_video"'
				infoLabels={	'title' : episode_name,
								'durationinseconds' : episode_duration_seconds,
								'season' : season_number,
								'episode' : episode_number,
								'plot' : episode_plot,
								'premiered' : episode_airdate }
				_common.add_video(u, episode_name, episode_thumb, infoLabels = infoLabels, quality_mode  = 'list_qualities')
	except:
		pass

def add_clips_southpark(episode_tree):
	try:
		episode_menu = episode_tree.find_all('li', class_ = 'clips_thumb')
		clip_titles = []
		for episode_item in episode_menu:
			episode_name = episode_item.find('a', class_ = 'clips_thumb_link', text = True).string
			if episode_name not in clip_titles:
				clip_titles.append(episode_name)
				episode_plot = episode_item.find('h6').string.replace('"', '')
				url = episode_item.find('a')['href']
				episode_thumb = episode_item.find('img')['src'].split('?')[0]
				try:
					episode_duration_seconds = _common.format_seconds(episode_item.find('span', class_ = 'clips_duration').string)
				except:
					episode_duration_seconds = -1
				try:
					episode_season = int(episode_item.find('h5', class_ = 'clips_thumb_season').string.replace('Season ', ''))
				except:
					episode_season = -1
				u = sys.argv[0]
				u += '?url="' + urllib.quote_plus(url) + '"'
				u += '&mode="' + SITE + '"'
				u += '&sitemode="play_video"'
				infoLabels={	'title' : episode_name,
								'duration' : episode_duration_seconds,
								'season' : episode_season,
								'plot' : episode_plot,
								'tvshowtitle' : 'South Park'}
				_common.add_video(u, episode_name, episode_thumb, infoLabels = infoLabels, quality_mode  = 'list_qualities')
	except:
		pass

def play_video(video_url = _common.args.url):
	video_data = _connection.getURL(video_url)
	try:
		mgid = BeautifulSoup(video_data, 'html5lib').find('div', attrs = {'data-mgid' : True})['data-mgid']
		video_url2 = mgid
	except:
		video_url2 = re.compile('swfobject\.embedSWF\("(.*?)"').findall(video_data)[0]
	_main_viacom.play_video(BASE, video_url2)

def list_qualities(video_url = _common.args.url):
	video_data = _connection.getURL(video_url)
	try:
		mgid = BeautifulSoup(video_data, 'html5lib').find('div', attrs = {'data-mgid' : True})['data-mgid']
		video_url2 = VIDEOURL + mgid
	except:
		video_url2 = re.compile('swfobject\.embedSWF\("(.*?)"').findall(video_data)[0]
	return _main_viacom.list_qualities(BASE, video_url2)
