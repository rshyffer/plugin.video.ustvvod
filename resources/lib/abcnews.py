#!/usr/bin/python
# -*- coding: utf-8 -*-
import _main_abcdisney

BRANDID = '003'
PARTNERID = '585231'
SITE = 'abcnews'
NAME = "ABC News"
DESCRIPTION = "ABC News is responsible for all of the ABC Television Network's news programming on a variety of platforms: TV, radio and the Internet."

def masterlist():
	return _main_abcdisney.masterlist(SITE, BRANDID)

def rootlist():
	_main_abcdisney.rootlist(SITE, BRANDID)

def seasons():
	_main_abcdisney.seasons(SITE, BRANDID)

def episodes():
	_main_abcdisney.episodes(SITE)

def play_video():
	_main_abcdisney.play_video(SITE, BRANDID, PARTNERID)

