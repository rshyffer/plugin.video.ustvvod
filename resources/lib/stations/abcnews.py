#!/usr/bin/python
# -*- coding: utf-8 -*-
from .. import main_abcdisney

BRANDID = '003'
PARTNERID = '585231'
SITE = 'abcnews'
NAME = "ABC News"
DESCRIPTION = "ABC News is responsible for all of the ABC Television Network's news programming on a variety of platforms: TV, radio and the Internet."

def masterlist():
	return main_abcdisney.masterlist(SITE, BRANDID)

def seasons():
	main_abcdisney.seasons(SITE, BRANDID)

def episodes():
	main_abcdisney.episodes(SITE)

def play_video():
	main_abcdisney.play_video(SITE, BRANDID, PARTNERID)
	
def list_qualities():
	return main_abcdisney.list_qualities(SITE, BRANDID, PARTNERID)
