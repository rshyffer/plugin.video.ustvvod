#!/usr/bin/python
# -*- coding: utf-8 -*-
import _main_abcdisney

BRANDID = '009'
PARTNERID = '585231'
SITE = 'disneyxd'
NAME = 'Disney XD'
DESCRIPTION = "Disney XD is a basic cable channel and multi-platform brand showcasing a compelling mix of live-action and animated programming for kids aged 6-14, hyper-targeting boys (while still including girls) and their quest for discovery, accomplishment, sports, adventure and humor. Disney XD branded content spans television, online, mobile and VOD platforms. The programming includes series, movies and short-form, as well as sports-themed programming developed with ESPN."

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
