﻿#!/usr/bin/python
# -*- coding: utf-8 -*-
from .. import _main_abcdisney

SITE = 'disneyjunior'
NAME = 'Disney Junior'
DESCRIPTION = "Disney Junior, part of Disney Channels Worldwide, is a global television and online brand expressly for kids age 2-7. Disney Junior invites mom and dad to join their child in the Disney experience of magical, musical and heartfelt stories and characters, both classic and new, while incorporating specific learning and development themes designed for young children"
BRANDID = '008'
PARTNERID = '585231'

def masterlist():
	return _main_abcdisney.masterlist(SITE, BRANDID)

def seasons():
	_main_abcdisney.seasons(SITE, BRANDID)

def episodes():
	_main_abcdisney.episodes(SITE)

def play_video():
	_main_abcdisney.play_video(SITE, BRANDID, PARTNERID)

def list_qualities():
	return _main_abcdisney.list_qualities(SITE, BRANDID, PARTNERID)