#!/usr/bin/python
# -*- coding: utf-8 -*-
import _main_turner

SITE = 'tnt'
NAME = "TNT"
DESCRIPTION = "TNT, one of cable's top-rated networks, is television's destination for drama. Seen in 99.6 million households, the network is home to such original series as The Closer, starring Kyra Sedgwick; Leverage, starring Timothy Hutton; and Dark Blue, starring Dylan McDermott; the upcoming Rizzoli & Isles, starring Angie Harmon and Sasha Alexander; Memphis Beat, with Jason Lee; Men of a Certain Age, with Ray Romano, Andre Braugher and Scott Bakula; and Southland, from Emmy'-winning producer John Wells (ER). TNT also presents such powerful dramas as Bones, Supernatural, Las Vegas, Law & Order, CSI: NY, Cold Case and Numb3rs; broadcast premiere movies; compelling primetime specials, such as the Screen Actors Guild Awards'; and championship sports coverage, including NASCAR and the NBA. The NCAA men's basketball tournament will appear on TNT beginning in 2011. TNT is available in high-definition."
SHOWS = 'http://www.tntdrama.com/mobile/smartphone/showList.jsp'
MOVIES = 'http://www.tntdrama.com/mobile/ipad/feeds/movies.jsp'
CLIPSSEASON = 'http://www.tntdrama.com/mobile/ipad/feeds/getFranchiseCollections.jsp?franchiseID=%s'
CLIPS = 'http://www.tntdrama.com/mobile/ipad/feeds/franchiseEpisode.jsp?franchiseID=%s&type=0&collectionId=%s'
FULLEPISODES = 'http://www.tntdrama.com/mobile/ipad/feeds/franchiseEpisode.jsp?franchiseID=%s&type=1'
EPISODE = 'http://www.tntdrama.com/video/content/services/cvpXML.do?id=%s'

def masterlist():
	return _main_turner.masterlist(NAME, MOVIES, SHOWS, SITE)

def seasons():
	_main_turner.seasons(SITE, FULLEPISODES, CLIPSSEASON, CLIPS)

def episodes():
	_main_turner.episodes_json(SITE)

def play_video():
	_main_turner.play_video(SITE, EPISODE)

def list_qualities():
	return _main_turner.list_qualities(SITE, EPISODE)
