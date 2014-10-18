#!/usr/bin/python
# -*- coding: utf-8 -*-
import _common
import _main_viacom

SITE = 'cmt'
NAME = 'CMT'
DESCRIPTION = "CMT's current programming features country music-oriented shows (including country music videos and taped concerts), country lifestyle-oriented shows, older shows and movies that prominently feature country or Southern-rock music, and (especially since the late 2000s) some general entertainment programming, mainly dealing with Southern culture and life."
API = 'http://api.mtv.com/api/lsfHZN1SU1bu/'
SHOWS = API + 'promolist/10394940.json'

def masterlist():
	return _main_viacom.masterlist(SITE, SHOWS)

def seasons():
	_main_viacom.seasons(SITE, API)

def videos():
	_main_viacom.videos(SITE)

def play():
	_main_viacom.play_video2(API, _common.args.url)

def list_qualities():
	return _main_viacom.list_qualities2(API, _common.args.url)
