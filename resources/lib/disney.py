#!/usr/bin/python
# -*- coding: utf-8 -*-
import _main_abcdisney

BRANDID = '004'
PARTNERID = '585231'
SITE = 'disney'
NAME = 'Disney'
DESCRIPTION = "Disney Channel is a 24-hour kid-driven, family inclusive television network that taps into the world of kids and families through original series and movies. It is currently available on basic cable and satellite in more than 98 million U.S. homes and in nearly 400 million households via 42 Disney Channels and free-to-air broadcast partners around the world."

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
