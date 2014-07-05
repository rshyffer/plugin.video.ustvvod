#!/usr/bin/python
# -*- coding: utf-8 -*-
import _addoncompat
import _common
import _connection
import _m3u8
import _main_nbcu
import re
import simplejson
import sys
import urllib
import xbmc
import xbmcgui
import xbmcplugin
from bs4 import BeautifulSoup, SoupStrainer

pluginHandle = int(sys.argv[1])

SITE = 'syfy'
NAME = 'Syfy'
DESCRIPTION = "Syfy is a media destination for imagination-based entertainment. With year round acclaimed original series, events, blockbuster movies, classic science fiction and fantasy programming, a dynamic Web site (www.Syfy.com), and a portfolio of adjacent business (Syfy Ventures), Syfy is a passport to limitless possibilities. Originally launched in 1992 as SCI FI Channel, and currently in 95 million homes, Syfy is a network of NBC Universal, one of the world's leading media and entertainment companies. Syfy. Imagine greater."
SHOWS = 'http://feed.theplatform.com/f/hQNl-B/sgM5DlyXAfwt/categories?form=json&sort=order'
CLIPS = 'http://feed.theplatform.com/f/hQNl-B/2g1gkJT0urp6?count=true&form=json&byCustomValue={fullEpisode}{false}&byCategories=%s'
FULLEPISODES = 'http://feed.theplatform.com/f/hQNl-B/2g1gkJT0urp6?count=true&form=json&byCustomValue={fullEpisode}{true}&byCategories=%s'
SWFURL = 'http://www.syfy.com/_utils/video/codebase/pdk/swf/flvPlayer.swf'

def masterlist():
	return _main_nbcu.masterlist(SITE, SHOWS)

def seasons():
	_main_nbcu.seasons(SITE, FULLEPISODES, CLIPS)

def episodes():
	_main_nbcu.episodes(SITE)

	
def list_qualities():
	return _main_nbcu.list_qualities()
	
def play_video():
	_main_nbcu.play_video()
	