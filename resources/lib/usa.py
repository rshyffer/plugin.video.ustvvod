#!/usr/bin/python
# -*- coding: utf-8 -*-
import _main_nbcu

SITE = 'usa'
NAME = 'USA Network'
DESCRIPTION = "USA Network is cable television's leading provider of original series and feature movies, sports events, off-net television shows, and blockbuster theatrical films. USA Network is seen in over 88 million U.S. homes. The USA Network web site is located at www.usanetwork.com. USA Network is a program service of NBC Universal Cable a division of NBC Universal, one of the world's leading media and entertainment companies in the development, production and marketing of entertainment, news and information to a global audience."
#SHOWS = 'http://feed.theplatform.com/f/OyMl-B/PleQEkKucpUm/categories?form=json&sort=order'
SHOWS = 'http://feed.theplatform.com/f/OyMl-B/8IyhuVgUXDd_/categories?form=json&sort=order'
#http://www.usanetwork.com/sites/usanetwork/files/css/css_pbm0lsQQJ7A7WCCIMgxLho6mI_kBNgznNUWmTWcnfoE.css
#VIDEOS = 'http://feed.theplatform.com/f/OyMl-B/8IyhuVgUXDd_/categories?count=true&form=json&byParentId=%s'
CLIPS = 'http://feed.theplatform.com/f/OyMl-B/8IyhuVgUXDd_?count=true&form=json&byCustomValue={fullEpisode}{false}&byCategories=%s'
FULLEPISODES = 'http://feed.theplatform.com/f/OyMl-B/8IyhuVgUXDd_?count=true&form=json&byCustomValue={fullEpisode}{true}&byCategories=%s'
SWFURL = 'http://www.usanetwork.com/videos/pdk/swf/flvPlayer.swf'


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
