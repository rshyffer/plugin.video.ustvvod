#!/usr/bin/python
# -*- coding: utf-8 -*-
import _main_turner
import _addoncompat
import _common
import _connection
import re
import simplejson
import sys
import urllib


SITE = 'tcm'
NAME = "TCM"
DESCRIPTION = "Turner Classic Movies (TCM) is an American movie-oriented basic cable and satellite television network that is owned by the Turner Broadcasting System subsidiary of Time Warner. TCM is headquartered at the Techwood Campus in Atlanta, Georgia's Midtown business district. Historically, the channel's programming consisted mainly of featured classic theatrically released feature films from the Turner Entertainment film library – which comprises films from Warner Bros. Pictures (covering films released before 1950) and Metro-Goldwyn-Mayer (covering films released before May 1986). However, TCM now has licensing deals with other Hollywood film studios as well as its Time Warner sister company Warner Bros. (which now controls the Turner Entertainment library and its own later films), and occasionally shows somewhat more recent films."
SHOWS = ''
MOVIES = 'http://api.tcm.com//tcmws/v1/vod/tablet/catalog/orderBy/title.jsonp'
CLIPSSEASON = ''
CLIPS = ''
FULLEPISODES = ''
EPISODE = 'http://www.tcm.com/tveverywhere/services/videoXML.do?id=%s'

def masterlist():
	master_db = []
	master_dict = {}
	master_db.append(('--' + NAME + ' Movies',  SITE, 'episodes', 'Movie#' + MOVIES))
	return master_db

def seasons():
	_main_turner.seasons(SITE, FULLEPISODES, CLIPSSEASON, CLIPS)

def episodes():
	episode_data = _connection.getURL(MOVIES)
	episode_list = simplejson.loads(episode_data)
	episode_menu = episode_list['tcm']['titles']
	for episode_item in episode_menu:
		url = episode_item['vod']['contentId']
		try:
			episode_duration = str(int(episode_item['runtimeMinutes'])*60)
		except:
			episode_duration = -1
		episode_year = episode_item['releaseYear']
		episode_plot = episode_item['description']
		episode_name = episode_item['name']
		try:
			episode_genre = episode_item['tvGenres']
		except:
			episode_genre = ''
		try:
			episode_rating = 'Rated: %s' % episode_item['tvRating']
		except:
			isode_rating = ''
		try:
			episode_director = episode_item['tvDirectors']
		except:
			episode_director = ''
		season_number = -1
		episode_number = -1
		try:
			episode_thumb = episode_item['imageProfiles'][1]['url']
		except:
			episode_thumb = None
		u = sys.argv[0]
		u += '?url="' + urllib.quote_plus(url) + '"'
		u += '&mode="' + SITE + '"'
		u += '&sitemode="play_video"'
		infoLabels={    'title' : episode_name,
						'durationinseconds' : episode_duration,
						'season' : season_number,
						'episode' : episode_number,
						'plot' : episode_plot,
						'year' : episode_year,
						'genre' : episode_genre, 
						'mpaa'  : episode_rating,
						'director' : episode_director}
		_common.add_video(u, episode_name, episode_thumb, infoLabels = infoLabels, quality_mode  = 'list_qualities')
	_common.set_view('episodes')


def play_video():
	_main_turner.play_video(SITE, EPISODE)

def list_qualities():
	return _main_turner.list_qualities(SITE, EPISODE)