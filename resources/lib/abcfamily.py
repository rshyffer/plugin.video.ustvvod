#!/usr/bin/python
# -*- coding: utf-8 -*-
import _main_abcdisney

BRANDID = '002'
PARTNERID = '585231'
SITE = 'abcfamily'

def masterlist():
	_main_abcdisney.masterlist(SITE, BRANDID)

def rootlist():
	_main_abcdisney.rootlist(SITE, BRANDID)

def seasons():
	_main_abcdisney.seasons(SITE, BRANDID)

def episodes():
	_main_abcdisney.episodes(SITE)

def play_video():
	_main_abcdisney.play_video(SITE, BRANDID, PARTNERID)