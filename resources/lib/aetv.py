#!/usr/bin/python
# -*- coding: utf-8 -*-
import _main_aenetwork
import sys

pluginHandle = int(sys.argv[1])

SITE = 'aetv'
NAME = 'A&E'
DESCRIPTION = "A&E is Real Life. Drama.  Now reaching more than 99 million homes, A&E is television that you can't turn away from; where unscripted shows are dramatic and scripted dramas are authentic.  A&E offers a diverse mix of high quality entertainment ranging from the network's original scripted series to signature non-fiction franchises, including the Emmy-winning \'Intervention,\' \'Dog The Bounty Hunter,\' \'Hoarders,\' \'Paranormal State\' and \'Criss Angel Mindfreak,\' and the most successful justice shows on cable, including \'The First 48\' and \'Manhunters.\'  The A&E website is located at www.aetv.com."
SHOWS = 'http://wombatapi.aetv.com/shows2/ae'
SEASONSEPISODE = 'https://mobileservices-a.akamaihd.net/jservice/wombattpservice/show_titles2/episode/ae?show_name=%s&get_season'
SEASONSCLIPS = 'https://mobileservices-a.akamaihd.net/jservice/wombattpservice/show_titles2/clip/ae?show_name=%s&get_season'
EPISODES = 'https://mobileservices-a.akamaihd.net/jservice/wombattpservice/show_titles2/episode/ae?show_name=%s&filter_by=season&filter_value=%d'
CLIPS = 'https://mobileservices-a.akamaihd.net/jservice/wombattpservice/show_titles2/clip/ae?show_name=%s&filter_by=season&filter_value=%d'

def masterlist():
	return _main_aenetwork.masterlist(SITE, SHOWS)

def seasons():
	_main_aenetwork.seasons(SITE, SEASONSEPISODE, SEASONSCLIPS, EPISODES, CLIPS)

def episodes():
	_main_aenetwork.episodes(SITE)

def play_video():
	_main_aenetwork.play_video()

def list_qualities():
	_main_aenetwork.list_qualities()
