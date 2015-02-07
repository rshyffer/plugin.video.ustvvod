#!/usr/bin/python
# -*- coding: utf-8 -*-
from .. import _common
from .. import _main_viacom

SITE = 'logotv'
NAME = 'LogoTV'
ALIAS = ['Logo']
DESCRIPTION = "Logo TV is an American digital cable and satellite television channel that is owned by Viacom Media Networks. The channel focuses on lifestyle programming aimed primarily at lesbian, gay, bisexual, and transgender people."
API = 'http://api.mtv.com/api/hVqrnHigT6Rq/'
SHOWS = API + 'promolist/10394912.json'

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
