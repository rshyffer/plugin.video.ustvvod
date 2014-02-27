#!/usr/bin/python
# -*- coding: utf-8 -*-
import _common
import _main_natgeo

SITE = 'natgeowild'
SHOWS = 'http://video.nationalgeographic.com/video/nat-geo-wild/shows-1/'
SPECIALS = 'http://video.nationalgeographic.com/video/nat-geo-wild/specials-2/'

def masterlist():
	return _main_natgeo.masterlist(SITE, SHOWS, SPECIALS)

def rootlist():
	_main_natgeo.rootlist(SITE, SHOWS, SPECIALS)

def episodes():
	_main_natgeo.episodes(SITE)

def play_video():
	_main_natgeo.play_video(SITE)

def list_qualities():
	return _main_natgeo.list_qualities(SITE)