#!/usr/bin/python
# -*- coding: utf-8 -*-
import _main_abcdisney

BRANDID = '002'
PARTNERID = '585231'
SITE = 'abcfamily'
NAME = "ABC Family"
DESCRIPTION = "ABC Family's programming is a combination of network-defining original series and original movies, quality acquired series and blockbuster theatricals. ABC Family features programming reflecting today's families, entertaining and connecting with adults through relatable stories about today's relationships, told with a mix of diversity, passion, humor and heart. Targeting Millennial viewers ages 14-34, ABC Family is advertiser supported."

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

