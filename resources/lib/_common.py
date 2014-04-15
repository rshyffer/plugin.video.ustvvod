#!/usr/bin/python
# -*- coding: utf-8 -*-
import _addoncompat
import _connection
import _database
import _importlib
import base64
import os
import sys
import time
import urllib
import xbmc
import xbmcaddon
import xbmcgui
import xbmcplugin
from bs4 import BeautifulSoup

pluginHandle = int(sys.argv[1])

PLUGINPATH = xbmc.translatePath(_addoncompat.get_path())
RESOURCESPATH = os.path.join(PLUGINPATH,'resources')
CACHEPATH = os.path.join(RESOURCESPATH,'cache')
IMAGEPATH = os.path.join(RESOURCESPATH,'images')
LIBPATH = os.path.join(RESOURCESPATH,'lib')
PLUGINFANART = os.path.join(PLUGINPATH,'fanart.jpg')
FAVICON = os.path.join(PLUGINPATH,'fav.png')
ALLICON = os.path.join(PLUGINPATH,'allshows.png')
PLAYFILE = os.path.join(CACHEPATH,'play.m3u8')
KEYFILE = os.path.join(CACHEPATH,'play.key')
SUBTITLE = os.path.join(CACHEPATH,'subtitle.srt')
SUBTITLESMI = os.path.join(CACHEPATH,'subtitle.smi')
COOKIE = os.path.join(CACHEPATH,'cookie.txt')

ADDONID = 'plugin.video.ustvvod'
TVDBAPIKEY = '03B8C17597ECBD64'
TVDBURL = 'http://thetvdb.com'
TVDBBANNERS = 'http://thetvdb.com/banners/'
TVDBSERIESLOOKUP = 'http://www.thetvdb.com/api/GetSeries.php?seriesname='

class _Info:
	def __init__(self, s):
		args = urllib.unquote_plus(s).split(' , ')
		for x in args:
			try:
				(k, v) = x.split('=', 1)
				setattr(self, k, v.strip('"\''))
			except:
				pass
		if not hasattr(self, 'url'):
			setattr(self, 'url', '')

args = _Info(sys.argv[2][1:].replace('&', ' , '))
network_module_cache = {}

def get_network(module_name):
	""" 
	Loads network using a quick and dirty plugin method
	"""
	if module_name in network_module_cache:
		return network_module_cache[module_name]

	print "!!! plugin loading of site : " + module_name 
	try:
		module = _importlib.import_module('resources.lib.%s' % (module_name))

		# module must at least have site and rootlist defined
		if hasattr(module, 'SITE') and hasattr(module, 'rootlist'):

			# patch modules with missing meta data
			if not hasattr(module, 'NAME'):
				setattr(module, 'NAME', module_name)
			if not hasattr(module, 'DESCRIPTION'):
				setattr(module, 'DESCRIPTION', module_name)

			network_module_cache[module_name] = module
			return module
		else:
			print "error loading site, SITE and rootlist must be defined"

	except Exception, e:
		print str(e)
		
def get_networks():
	""" 
	Loads all networks using a quick and dirty plugin method
	"""
	networks = []
	for filename in os.listdir(LIBPATH):
		if filename.endswith('.py') and not filename.startswith('_'):
			module_name = os.path.splitext(filename)[0]
			network = get_network(module_name)
			if network:
				networks.append(network)
	return networks

def get_quality_method():
	val = _addoncompat.get_setting('qualityMethod')
	if val == "Lowest":
		return "LOW"
	return "HIGH"
	
def set_view(type = 'root'):
	confluence_views = [500,501,502,503,504,508]
	if type == 'root':
		xbmcplugin.setContent(pluginHandle, 'movies')
	elif type == 'seasons':
		xbmcplugin.setContent(pluginHandle, 'movies')
	else:
		if type == 'tvshows':
			xbmcplugin.addSortMethod(pluginHandle, xbmcplugin.SORT_METHOD_LABEL)
		xbmcplugin.setContent(pluginHandle, type)
	viewenable = _addoncompat.get_setting('viewenable')
	if viewenable == 'true':
		view = int(_addoncompat.get_setting(type + 'view'))
		xbmc.executebuiltin('Container.SetViewMode(' + str(confluence_views[view]) + ')')

def format_date(inputDate = '', inputFormat = '', outputFormat = '%Y-%m-%d', epoch = False):
	if epoch:
		return time.strftime(outputFormat, time.localtime(epoch))
	else:
		return time.strftime(outputFormat, time.strptime(inputDate, inputFormat))

def convert_to_timezone(inputDate = '', inputFormat = '', timezone = 0, epoch = False):
	if epoch:
		return epoch + (timezone*3600 + time.timezone)
	else:
		return time.strftime(inputFormat, time.localtime(time.mktime(time.strptime(inputDate, inputFormat)) + (timezone*3600 + time.timezone)))

def format_seconds(timestring):
	if timestring[0] == ':':
		timestring = '0' + timestring
	timestring2 = 0
	if len(timestring.split(':')) == 1:
		ftr = [1]
	elif len(timestring.split(':')) == 2:
		ftr = [60,1]
	else:
		ftr = [3600,60,1]
	timestring2 = sum([a*b for a,b in zip(ftr, map(int,timestring.split(':')))])
	return int(timestring2)

def smart_unicode(s):
	"""credit : sfaxman"""
	if not s:
		return ''
	try:
		if not isinstance(s, basestring):
			if hasattr(s, '__unicode__'):
				s = unicode(s)
			else:
				s = unicode(str(s), 'UTF-8')
		elif not isinstance(s, unicode):
			s = unicode(s, 'UTF-8')
	except:
		if not isinstance(s, basestring):
			if hasattr(s, '__unicode__'):
				s = unicode(s)
			else:
				s = unicode(str(s), 'ISO-8859-1')
		elif not isinstance(s, unicode):
			s = unicode(s, 'ISO-8859-1')
	return s

def smart_utf8(s):
	return smart_unicode(s).encode('utf-8')

def replace_signs(text):
	dic = {	'â€™'	: '\'',
			'�'		: '\'',
			'â„¢' 	: '',
			'â€œ'	: '',
			'â€"'	: '-',
			'â€“'	: '-',
			'â€”'	: '-',
			'Â²'	: '²',
			'â€�'	: '"',
			'â€˜N'	: '\'N',
			'Ã¡'	: 'á',
			'Ã©'	: 'é',
			'â€˜'	: '\''}
	for i, j in dic.iteritems():
		text = smart_utf8(text).replace(i, j).strip()
	return text

def refresh_db():
	networks = get_networks()
	dialog = xbmcgui.DialogProgress()
	dialog.create(smart_utf8(xbmcaddon.Addon(id = ADDONID).getLocalizedString(39016)))
	total_stations = len(networks)
	current = 0
	increment = 100.0 / total_stations
	for network in networks:
		network_name = network.NAME
		if _addoncompat.get_setting(network.SITE) == 'true':
			percent = int(increment * current)
			dialog.update(percent, smart_utf8(xbmcaddon.Addon(id = ADDONID).getLocalizedString(39017)) + network.NAME, smart_utf8(xbmcaddon.Addon(id = ADDONID).getLocalizedString(39018)))
			showdata = network.masterlist()
			total_shows = len(showdata)
			current_show = 0
			for show in showdata:
				percent = int((increment * current) + (float(current_show) / total_shows) * increment)
				dialog.update(percent, smart_utf8(xbmcaddon.Addon(id = ADDONID).getLocalizedString(39017)) + network.NAME, smart_utf8(xbmcaddon.Addon(id = ADDONID).getLocalizedString(39005)) + show[0])
				get_serie(show[0], show[1], show[2], show[3])
				current_show += 1
				if (dialog.iscanceled()):
					return False
		current += 1

def get_serie(series_title, mode, submode, url, forceRefresh = False):
	command = 'select * from shows where series_title = ? and mode = ? and submode = ?;'
	values = (series_title, mode, submode)
	checkdata = _database.execute_command(command, values, fetchone = True)
	if checkdata and not forceRefresh:
		if checkdata[3] is not url:
			command = 'update shows set url = ? where series_title = ? and mode = ? and submode = ?;'
			values = (url, series_title, mode, submode)
			_database.execute_command(command, values, commit = True)
			command = 'select * from shows where series_title = ? and mode = ? and submode = ?;'
			values = (series_title, mode, submode)
			return _database.execute_command(command, values, fetchone = True)
		else:
			return checkdata
	else:
		tvdb_data = get_tvdb_series(series_title, manualSearch = forceRefresh, site = get_network(mode).NAME)
		if tvdb_data:
			tvdb_id, imdb_id, tvdbbanner, tvdbposter, tvdbfanart, first_aired, date, year, actors, genres, network, plot, runtime, rating, airs_dayofweek, airs_time, status, tvdb_series_title = tvdb_data
			values = [series_title, mode, submode, url, tvdb_id, imdb_id, tvdbbanner, tvdbposter, tvdbfanart, first_aired, date, year, actors, genres, network, plot, runtime, rating, airs_dayofweek, airs_time, status, True, False, False, tvdb_series_title]
		else:
			values = [series_title, mode,submode, url, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, True, False, False, series_title]
		command = 'insert or replace into shows values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);'
		_database.execute_command(command, values, commit = True)
		command = 'select * from shows where series_title = ? and mode = ? and submode = ?;'
		values = (series_title, mode, submode)
		return _database.execute_command(command, values, fetchone = True)

def get_series_id(seriesdata, seriesname, site = '', allowManual = False):
	shows = BeautifulSoup(seriesdata).find_all('series')
	for show_item in shows:
		if  '**' in show_item.seriesname.string:
			show_item.clear()
	show_list = []
	if len(shows) > 1:
		ret = -1
		variantsExist = False
		lookup_name = seriesname.replace('%E2%84%A2', '').lower().replace("'", "").replace('?', '').replace('!', '').strip()
		lookup_network = site.replace('The', '').replace(',', '').strip()
		for i, show_item in enumerate(shows):
			item_name = show_item.seriesname.string.lower().replace("'", "").replace('!', '').strip()
			try:
				item_network = show_item.network.string.replace('The', '').replace(',', '').strip()
			except:
				item_network = ''
			if '(' in show_item.seriesname.string and item_network == lookup_network:
				variantsExist = True
			elif item_name == lookup_name and item_network == lookup_network:
				ret = i
		if allowManual == True and (variantsExist == True or ret == -1):
			select = xbmcgui.Dialog()
			for show_item in shows:
				try:
					show_list.append(show_item.seriesname.string + ' [' + show_item.network.string + ']')
				except:
					show_list.append(show_item.seriesname.string)
			if site.endswith(', The'):
				station = 'The ' + site.replace(', The', '')
			else:
				station = site
			ret = select.select(smart_utf8(xbmcaddon.Addon(id = ADDONID).getLocalizedString(39020)) + seriesname + ' [' + station.strip() + ']', show_list)
		if ret is not -1:
			seriesid = shows[ret].seriesid.string
	else:
		seriesid = shows[0].seriesid.string
	return seriesid

def get_tvdb_series(seriesname, manualSearch = False, site = ''):
	seriesdata = _connection.getURL(TVDBSERIESLOOKUP + urllib.quote_plus(smart_utf8(seriesname)), connectiontype = 0)
	try:
		tvdb_id = get_series_id(seriesdata, seriesname, site)
	except:
		if manualSearch:
			keyb = xbmc.Keyboard(seriesname, smart_utf8(xbmcaddon.Addon(id = ADDONID).getLocalizedString(39004)))
			keyb.doModal()
			if (keyb.isConfirmed()):
					seriesname_custom = keyb.getText()
					searchurl = TVDBSERIESLOOKUP + urllib.quote_plus(seriesname_custom)
					tvdbid_url = _connection.getURL(searchurl, connectiontype = 0)
					try:
						tvdb_id = get_series_id(tvdbid_url, seriesname_custom, site, True)
					except:
						print '_common :: get_tvdb_series :: Manual Search failed'
						return False
			else:
				return False
		else:
			return False
	series_xml = TVDBURL + ('/api/%s/series/%s/en.xml' % (TVDBAPIKEY, tvdb_id))
	series_xml = _connection.getURL(series_xml, connectiontype = 0)
	series_tree = BeautifulSoup(series_xml).find('series')
	try:
		if smart_unicode(series_tree.firstaired.text) is not '':
			first_aired = smart_unicode(series_tree.firstaired.text)
			date = first_aired
			year = first_aired.split('-')[0]
		else:
			first_aired = None
			date = None
			year = None
	except:
		print '_common :: get_tvdb_series :: %s - Air Date Failed' % seriesname
		first_aired = None
		date = None
		year = None
	try:
		if smart_unicode(series_tree.genre.text) is not '':
			genres = smart_unicode(series_tree.genre.text)
		else:
			genres = None
	except:
		print '_common :: get_tvdb_series :: %s - Genre Failed' % seriesname
		genres = None
	try:
		if smart_unicode(series_tree.overview.text) is not '':
			plot = smart_unicode(series_tree.overview.text)
		else:
			plot = None
	except:
		print '_common :: get_tvdb_series :: %s - Plot Failed' % seriesname
		plot = None
	try:
		if smart_unicode(series_tree.actors.text) is not '':
			actors = smart_unicode(series_tree.actors.text)
		else:
			actors = None
	except:
		print '_common :: get_tvdb_series :: %s - Actors Failed' % seriesname
		actors = None
	try:
		if smart_unicode(series_tree.rating.text) is not '':
			rating = smart_unicode(series_tree.rating.text)
		else:
			rating = None
	except:
		print '_common :: get_tvdb_series :: %s - Rating Failed' % seriesname
		rating = None
	try:
		if smart_unicode(series_tree.banner.text) is not '':
			tvdbbanner = smart_unicode(TVDBBANNERS + series_tree.banner.text)
		else:
			tvdbbanner = None
	except:
		print '_common :: get_tvdb_series :: %s - Banner Failed' % seriesname
		tvdbbanner = None
	try:
		if smart_unicode(series_tree.fanart.text) is not '':
			tvdbfanart = smart_unicode(TVDBBANNERS + series_tree.fanart.text)
		else:
			tvdbfanart = None
	except:
		print '_common :: get_tvdb_series :: %s - Fanart Failed' % seriesname
		tvdbfanart = None
	try:
		if smart_unicode(series_tree.poster.text) is not '':
			tvdbposter = smart_unicode(TVDBBANNERS + series_tree.poster.text)
		else:
			tvdbposter = None
	except:
		print '_common :: get_tvdb_series :: %s - Poster Failed' % seriesname
		tvdbposter = None
	try:
		if smart_unicode(series_tree.imdb_id.text) is not '':
			imdb_id = smart_unicode(series_tree.imdb_id.text)
		else:
			imdb_id = None
	except:
		print '_common :: get_tvdb_series :: %s - IMDB_ID Failed' % seriesname
		imdb_id = None
	try:
		if smart_unicode(series_tree.runtime.text) is not '':
			runtime = smart_unicode(series_tree.runtime.text)
		else:
			runtime = None
	except:
		print '_common :: get_tvdb_series :: %s - Runtime Failed' % seriesname
		runtime = None
	try:
		if smart_unicode(series_tree.airs_dayofweek.text) is not '':
			airs_dayofweek = smart_unicode(series_tree.airs_dayofweek.text)
		else:
			airs_dayofweek = None
	except:
		print '_common :: get_tvdb_series :: %s - Airs_DayOfWeek Failed' % seriesname
		airs_dayofweek = None
	try:
		if smart_unicode(series_tree.airs_time.text) is not '':
			airs_time = smart_unicode(series_tree.airs_time.text)
		else:
			airs_time = None
	except:
		print '_common :: get_tvdb_series :: %s - Airs_Time Failed' % seriesname
		airs_time = None
	try:
		if smart_unicode(series_tree.status.text) is not '':
			status = smart_unicode(series_tree.status.text)
		else:
			status = None
	except:
		print '_common :: get_tvdb_series :: %s - Status Failed' % seriesname
		status = None
	try:
		if smart_unicode(series_tree.network.text) is not '':
			network = smart_unicode(series_tree.network.text)
		else:
			network = None
	except:
		print '_common :: get_tvdb_series :: %s - Network Failed' % seriesname
		network = None
	try:
		if smart_unicode(series_tree.seriesname.text) is not '':
			seriesname = smart_unicode(series_tree.seriesname.text)
		else:
			seriesname = None
	except:
		print '_common :: get_tvdb_series :: %s - TVDB SeriesName Failed' % seriesname
		seriesname = None
	return [tvdb_id, imdb_id, tvdbbanner, tvdbposter, tvdbfanart, first_aired, date, year, actors, genres, network, plot, runtime, rating, airs_dayofweek, airs_time, status, seriesname]

def get_plot_by_tvdbid(tvdb_id):
	command = 'select * from shows where tvdb_id = ?;'
	values = (tvdb_id,)
	showdata = _database.execute_command(command, values, fetchone = True)
	prefixplot = ''
	if showdata:
		series_title, mode, sitemode, url, tvdb_id, imdb_id, tvdbbanner, tvdbposter, tvdbfanart, first_aired, date, year, actors, genres, network, plot, runtime, rating, airs_dayofweek, airs_time, status, has_full_episodes, favor, hide, tvdb_series_title = showdata
		if network is not None:
			prefixplot += smart_utf8(xbmcaddon.Addon(id = ADDONID).getLocalizedString(39013)) + network + '\n'
		if (airs_dayofweek is not None) and (airs_time is not None):
			prefixplot += smart_utf8(xbmcaddon.Addon(id = ADDONID).getLocalizedString(39014)) + airs_dayofweek + '@' + airs_time + '\n'
		if status is not None:
			prefixplot += smart_utf8(xbmcaddon.Addon(id = ADDONID).getLocalizedString(39015)) + status + '\n'
		if prefixplot is not '':
			prefixplot += '\n'
		if plot is not None:
			prefixplot = smart_unicode(prefixplot) + smart_unicode(replace_signs(plot))
	return prefixplot

def get_show_data(series_title, mode = '', sitemode = '', url = ''):
	series_title = replace_signs(smart_unicode(series_title))
	if not os.path.exists(_database.DBFILE):
		_database.create_db()
	_database.check_db_version()
	showdata = get_serie(series_title, mode, sitemode, url, forceRefresh = False)
	return showdata

def load_showlist(favored = 0):
	if not os.path.exists(_database.DBFILE):
		_database.create_db()
		refresh_db()
	elif not favored:
		refresh = False
		command = 'select distinct mode from shows order by mode'
		modes = _database.execute_command(command, fetchall = True)
		mode_list = [element[0] for element in modes]
		for network in get_networks():
			if _addoncompat.get_setting(network.SITE) == 'true' and network.SITE not in mode_list:
				refresh = True
		if refresh:
			refresh_db()
	_database.check_db_version()
	command = 'select series_title, mode, submode, url, favor, hide from shows order by series_title'
	shows = _database.execute_command(command, fetchall = True) 
	for series_title, mode, sitemode, url, favor, hide in shows:
		if _addoncompat.get_setting(mode) != 'true':
			continue
		elif hide is 1:
			continue
		elif favored and not favor:
			continue
		add_show(series_title, mode, sitemode, url, favor = favor, hide = hide)	

def add_show(series_title, mode = '', sitemode = '', url = '', favor = 0, hide = 0):
	#print "add show from ",mode, series_title
	infoLabels = {}
	tvdbfanart = None
	tvdbbanner = None
	tvdbposter = None
	tvdb_id = None
	thumb = ''
	fanart = ''
	prefixplot = ''
	actors2 = []
	showdata = get_show_data(series_title, mode, sitemode, url)
	series_title, mode, sitemode, url, tvdb_id, imdb_id, tvdbbanner, tvdbposter, tvdbfanart, first_aired, date, year, actors, genres, network, plot, runtime, rating, airs_dayofweek, airs_time, status, has_full_episodes, favor, hide, tvdb_series_title = showdata
	network_module = get_network(mode)
	if not network_module:
		return
		
	network_name = network_module.NAME
	network_description = network_module.DESCRIPTION
	if tvdbfanart is not None:
		fanart = tvdbfanart
	else:
		if args.__dict__.has_key('fanart'):
			fanart = args.fanart
		else:
			fanart = None
	if tvdbbanner is not None:
		thumb = tvdbbanner
	elif tvdbposter is not None:
		thumb = tvdbposter
	else:
		thumb = os.path.join(IMAGEPATH, mode + '.png')
	if tvdb_series_title is not None:
		series_title = smart_utf8(tvdb_series_title)
	infoLabels['title'] = series_title
	infoLabels['tvShowtitle'] = series_title
	
	if network_name.endswith(', The'):
		station = 'The ' + network_name.replace(', The', '')
	else:
		station = network_name
	if network is not None:
		if station == network:
			prefixplot += smart_utf8(xbmcaddon.Addon(id = ADDONID).getLocalizedString(39013)) + station + '\n'
		else:
			prefixplot += smart_utf8(xbmcaddon.Addon(id = ADDONID).getLocalizedString(39012)) + network + '\n'
			prefixplot += smart_utf8(xbmcaddon.Addon(id = ADDONID).getLocalizedString(39013)) + station + '\n'
	else:
		prefixplot += smart_utf8(xbmcaddon.Addon(id = ADDONID).getLocalizedString(39013)) + station + '\n'
	if (airs_dayofweek is not None) and (airs_time is not None):
		prefixplot += smart_utf8(xbmcaddon.Addon(id = ADDONID).getLocalizedString(39014)) + airs_dayofweek + '@' + airs_time + '\n'
	elif (airs_dayofweek is not None) and (airs_time is None):
		prefixplot += smart_utf8(xbmcaddon.Addon(id = ADDONID).getLocalizedString(39014)) + airs_dayofweek + '\n'
	elif  (airs_dayofweek is None) and (airs_time is not None):
		prefixplot += smart_utf8(xbmcaddon.Addon(id = ADDONID).getLocalizedString(39014)) + airs_time + '\n'
	else:
		pass
	if status is not None:
		prefixplot += smart_utf8(xbmcaddon.Addon(id = ADDONID).getLocalizedString(39015)) + status + '\n'
	if prefixplot is not None:
		prefixplot += '\n'
	if plot is not None:
		infoLabels['plot'] = smart_utf8(prefixplot) + smart_utf8(replace_signs(plot))
	else:
		infoLabels['plot'] = smart_utf8(prefixplot)
	if date is not None:
		infoLabels['date'] = smart_utf8(date)
	if first_aired is not None: 
		infoLabels['aired'] = smart_utf8(first_aired)
	if year is not None:
		infoLabels['year'] = smart_utf8(year)
	if actors is not None:
		actors = actors.strip('|').split('|')
		if actors[0] is not '':
			for actor in actors:
				actors2.append(smart_utf8(actor))
			infoLabels['cast'] = actors2
	if genres is not None:
		infoLabels['genre'] = smart_utf8(genres.replace('|',',').strip(','))
	if network is not None:
		infoLabels['studio'] = smart_utf8(network)
	if runtime is not None:
		infoLabels['duration'] = smart_utf8(runtime)
	if rating is not None:
		infoLabels['rating'] = smart_utf8(rating)
	name = smart_utf8(replace_signs(series_title))
	series_title = smart_utf8(replace_signs(series_title))
	u = sys.argv[0]
	u += '?url="' + urllib.quote_plus(url) + '"'
	u += '&mode="' + mode + '"'
	u += '&sitemode="' + sitemode + '"'
	u += '&thumb="' + urllib.quote_plus(thumb) + '"'
	if tvdb_id is not None:
		u += '&tvdb_id="' + urllib.quote_plus(tvdb_id) + '"'
	if PLUGINFANART is not fanart and fanart is not None:
		u += '&fanart="' + urllib.quote_plus(fanart) + '"'
	if tvdbposter is not None:
		u += '&poster="' + urllib.quote_plus(tvdbposter) + '"'
	u += '&name="' + urllib.quote_plus(series_title) + '"'
	contextmenu = []
	refresh_u = sys.argv[0] + '?url="' + urllib.quote_plus('<join>'.join([series_title, mode, sitemode,url])) + '&mode=_contextmenu' + '&sitemode=refresh_show'
	contextmenu.append((smart_utf8(xbmcaddon.Addon(id = ADDONID).getLocalizedString(39008)), 'XBMC.RunPlugin(%s)' % refresh_u))
	if favor is 1:
		fav_u = sys.argv[0] + '?url="' + urllib.quote_plus('<join>'.join([series_title, mode, sitemode,url])) + '&mode=_contextmenu' + '&sitemode=unfavor_show'
		contextmenu.append((smart_utf8(xbmcaddon.Addon(id = ADDONID).getLocalizedString(39006)), 'XBMC.RunPlugin(%s)' % fav_u))
	else:
		fav_u = sys.argv[0] + '?url="' + urllib.quote_plus('<join>'.join([series_title, mode, sitemode,url])) + '&mode=_contextmenu' + '&sitemode=favor_show'
		contextmenu.append((smart_utf8(xbmcaddon.Addon(id = ADDONID).getLocalizedString(39007)), 'XBMC.RunPlugin(%s)' % fav_u))
	if hide is 1:
		hide_u = sys.argv[0] + '?url="' + urllib.quote_plus('<join>'.join([series_title, mode, sitemode,url])) + '&mode=_contextmenu' + '&sitemode=unhide_show'
		contextmenu.append((smart_utf8(xbmcaddon.Addon(id = ADDONID).getLocalizedString(39009)), 'XBMC.RunPlugin(%s)' % hide_u))
	else: 
		hide_u = sys.argv[0] + '?url="' + urllib.quote_plus('<join>'.join([series_title, mode, sitemode,url])) + '&mode=_contextmenu' + '&sitemode=hide_show'
		contextmenu.append((smart_utf8(xbmcaddon.Addon(id = ADDONID).getLocalizedString(39010)), 'XBMC.RunPlugin(%s)' % hide_u))
	delete_u = sys.argv[0] + '?url="' + urllib.quote_plus('<join>'.join([series_title, mode, sitemode,url])) + '&mode=_contextmenu' + '&sitemode=delete_show'
	contextmenu.append((smart_utf8(xbmcaddon.Addon(id = ADDONID).getLocalizedString(39011)), 'XBMC.RunPlugin(%s)' % delete_u))
	item = xbmcgui.ListItem(name, iconImage = thumb, thumbnailImage = thumb)
	item.addContextMenuItems(contextmenu)
	item.setProperty('fanart_image', fanart)
	item.setInfo(type = 'Video', infoLabels = infoLabels)
	xbmcplugin.addDirectoryItem(pluginHandle, url = u, listitem = item, isFolder = True)

def add_directory(name, mode = '', sitemode = '', directory_url = '', thumb = None, fanart = None, description = None, aired = '', genre = '', count = 0):
	if fanart is None:
		if args.__dict__.has_key('fanart'):
			fanart = args.fanart
		else:
			fanart = PLUGINFANART
	if thumb is None:
		if args.__dict__.has_key('poster'):
			thumb = args.poster
		elif args.__dict__.has_key('thumb'):
			thumb = args.thumb
		else:
			thumb = ''
	if args.__dict__.has_key('name'):
		showname = args.name
	else:
		showname = ''
	if description is None:
		if args.__dict__.has_key('tvdb_id'):
			description = get_plot_by_tvdbid(args.tvdb_id)
		else:
			network = get_network(mode)
			description = network.DESCRIPTION
	infoLabels = {	'title' : name,
					'tvshowtitle' : showname,
					'genre' : genre,
					'premiered' : aired,
					'plot' : description,
					'count' : count }
	u = sys.argv[0]
	u += '?url="' + urllib.quote_plus(directory_url) + '"'
	u += '&mode="' + mode + '"'
	u += '&sitemode="' + sitemode + '"'
	u += '&thumb="' + urllib.quote_plus(thumb) + '"'
	u += '&fanart="' + urllib.quote_plus(fanart) + '"'
	u += '&name="' + urllib.quote_plus(name) + '"'
	if args.__dict__.has_key('tvdb_id'):
		u += '&tvdb_id="' + urllib.quote_plus(args.tvdb_id) + '"'
	item=xbmcgui.ListItem(name, iconImage = thumb, thumbnailImage = thumb)
	item.setProperty('fanart_image', fanart)
	item.setInfo(type = 'Video', infoLabels = infoLabels)
	contextmenu = []
	refresh_u = sys.argv[0] + '?url="<join>"' + sys.argv[0] + '?url="' + '&mode=_contextmenu' + '&sitemode=refresh_db' 
	contextmenu.append((smart_utf8(xbmcaddon.Addon(id = ADDONID).getLocalizedString(39021)), 'XBMC.RunPlugin(%s)' % refresh_u))
	item.addContextMenuItems(contextmenu)
	xbmcplugin.addDirectoryItem(pluginHandle, url = u, listitem = item, isFolder = True)

def add_video(video_url, displayname, thumb = None, fanart = None, infoLabels = False, HD = False, quality_mode = False):
	displayname = smart_utf8(replace_signs(smart_unicode(displayname)))
	if fanart is None:
		if args.__dict__.has_key('fanart'):
			fanart = args.fanart
		else:
			fanart = PLUGINFANART
	if thumb is None:
		if args.__dict__.has_key('thumb'):
			thumb = args.thumb
		else:
			thumb = ''
	item = xbmcgui.ListItem(displayname, iconImage = thumb, thumbnailImage = thumb)
	item.setInfo(type = 'Video', infoLabels = infoLabels)
	try:
		if 'durationinseconds' in infoLabels.keys():	
			duration = infoLabels['durationinseconds']
		else:
			duration = 0
		if HD is True:
			item.addStreamInfo('video', {'codec' : 'h264', 'width' : 1280, 'height' : 720, 'duration' : duration})
		else:
			item.addStreamInfo('video', {'codec' : 'h264', 'width' : 720, 'height' : 400, 'duration' : duration})
		item.addStreamInfo('audio', {'codec': 'aac', 'channels' : 2})
	except:
		pass
	item.setProperty('fanart_image', fanart)
	item.setProperty('IsPlayable', 'true')
	if quality_mode:
		contextmenu = []
		if 'episode' in infoLabels.keys():	
			episode = infoLabels['episode']
		else:
			episode = -1
		if 'season' in infoLabels.keys():	
			season = infoLabels['season']
		else:
			season = -1
		if 'TVShowTitle' in infoLabels.keys():
			show_title = infoLabels['TVShowTitle']
		else:
			show_title = ''
		quailty_u = sys.argv[0] + '?url='+ urllib.quote_plus('<join>'.join([show_title, str(season), str(episode), thumb, base64.b64encode(displayname), quality_mode, video_url])) +'&mode=_contextmenu' + '&sitemode=select_quality' 
		contextmenu.append((smart_utf8(xbmcaddon.Addon(id = ADDONID).getLocalizedString(39022)), 'XBMC.PlayMedia(%s)' % quailty_u))
		item.addContextMenuItems(contextmenu)
	xbmcplugin.addDirectoryItem(pluginHandle, url = video_url, listitem = item, isFolder = False)
