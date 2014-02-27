#!/usr/bin/python
# -*- coding: utf-8 -*-
import _common
import _main_natgeo

SITE = 'natgeo'
SHOWS = 'http://video.nationalgeographic.com/video/national-geographic-channel/shows/'
SPECIALS = 'http://video.nationalgeographic.com/video/national-geographic-channel/specials-1/'

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