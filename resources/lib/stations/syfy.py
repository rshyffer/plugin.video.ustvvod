#!/usr/bin/python
# -*- coding: utf-8 -*-
import common
import main_nbcu

SITE = "syfy"
NAME = "Syfy"
ALIAS = ["SciFi"]
DESCRIPTION = "Syfy is a media destination for imagination-based entertainment. With year round acclaimed original series, events, blockbuster movies, classic science fiction and fantasy programming, a dynamic Web site (www.Syfy.com), and a portfolio of adjacent business (Syfy Ventures), Syfy is a passport to limitless possibilities. Originally launched in 1992 as SCI FI Channel, and currently in 95 million homes, Syfy is a network of NBC Universal, one of the world's leading media and entertainment companies. Syfy. Imagine greater."
SHOWS = "http://feed.theplatform.com/f/hQNl-B/sgM5DlyXAfwt/categories?form=json&sort=order"
CLIPS = "http://feed.theplatform.com/f/hQNl-B/2g1gkJT0urp6?count=true&form=json&byCustomValue={fullEpisode}{false}&byCategories=%s"
FULLEPISODES = "http://feed.theplatform.com/f/hQNl-B/2g1gkJT0urp6?count=true&form=json&byCustomValue={fullEpisode}{true}&byCategories=%s"
SWFURL = "http://www.syfy.com/_utils/video/codebase/pdk/swf/flvPlayer.swf"

def masterlist():
	return main_nbcu.masterlist(SITE, SHOWS)

def seasons(season_url = common.args.url):
	return main_nbcu.seasons(SITE, FULLEPISODES, CLIPS, None, season_url)

def episodes(episode_url = common.args.url):
	return main_nbcu.episodes(SITE, episode_url)

def list_qualities():
	return main_nbcu.list_qualities()

def play_video():
	main_nbcu.play_video()
