#!/usr/bin/python
# -*- coding: utf-8 -*-
import _addoncompat
import _common
import _connection
import _m3u8
import os
import base64
import re
import sys
import urllib
import datetime
import time
import xbmc
import xbmcgui
import xbmcplugin
from bs4 import BeautifulSoup, SoupStrainer

pluginHandle = int(sys.argv[1])

VIDEOURL = 'http://media.mtvnservices.com/'
DEVICE = 'Xbox'
BITRATERANGE = 10

class XBMCPlayer( xbmc.Player ):
	_counter = 0
	_segments = 1
	_subtitles_Enabled = False
	_subtitles_Type = "SRT"
	_localHTTPServer = True

	def __init__( self, *args, **kwargs  ):
		xbmc.Player.__init__( self )
		self.is_active = True

	def onPlayBackStarted( self ):
		# Will be called when xbmc starts playing a segment
		self._counter = self._counter + 1
		if self._subtitles_Enabled:
			if self._segments > 1:
				if self._subtitles_Type == "SRT":
					self.setSubtitles(os.path.join(_common.CACHEPATH, 'subtitle-%s.srt' % str(self._counter)))
				else:
					self.setSubtitles(os.path.join(_common.CACHEPATH, 'subtitle-%s.smi' % str(self._counter)))
			else:
				if self._subtitles_Type == "SRT":
					self.setSubtitles(_common.SUBTITLE)
				else:
					self.setSubtitles(_common.SUBTITLESMI)

	def onPlayBackEnded( self ):
		# Will be called when xbmc stops playing a segment
		print "**************************** End Event *****************************"
		if self._counter == self._segments:
			print "**************************** End Event -- Stopping Server *****************************"
			self.is_active = False
			if _self._localHTTPServer:
				_connection.getURL('http://localhost:12345/stop', connectiontype = 0)
			

	def onPlayBackStopped( self ):
		# Will be called when user stops xbmc playing a file
		print "**************************** Stop Event -- Stopping Server *****************************"
		self.is_active = False
		if self._localHTTPServer:
			_connection.getURL('http://localhost:12345/stop', connectiontype = 0)
		
	
	def sleep(self, s):
		xbmc.sleep(s) 

player = XBMCPlayer()

def play_video(BASE, video_url = _common.args.url, media_base = VIDEOURL):
	if media_base not in video_url:
		video_url = media_base + video_url
	try:
		qbitrate = _common.args.quality
	except:
		qbitrate = None
	video_url6 = 'stack://'
	sbitrate = int(_addoncompat.get_setting('quality'))
	closedcaption = []
	exception = False
	if 'feed' not in video_url:
		swf_url = _connection.getRedirect(video_url, header = {'Referer' : BASE})
		params = dict(item.split("=") for item in swf_url.split('?')[1].split("&"))
		uri = urllib.unquote_plus(params['uri'])
		config_url = urllib.unquote_plus(params['CONFIG_URL'].replace('Other', DEVICE))
		config_data = _connection.getURL(config_url, header = {'Referer' : video_url, 'X-Forwarded-For' : '12.13.14.15'})
		config_tree = BeautifulSoup(config_data, 'html5lib')
		if not config_tree.error:
			feed_url = config_tree.feed.string
			feed_url = feed_url.replace('{uri}', uri).replace('&amp;', '&').replace('{device}', DEVICE).replace('{ref}', 'None').strip()
		else:
			exception = True
			error_text = config_tree.error.string.split('/')[-1].split('_') 
			dialog = xbmcgui.Dialog()
			dialog.ok("Exception", error_text[1], error_text[2])
	else:
		feed_url = video_url

	if not exception:
		feed_data = _connection.getURL(feed_url)
		video_tree = BeautifulSoup(feed_data, 'html.parser', parse_only = SoupStrainer('media:group'))
		video_segments = video_tree.find_all('media:content')
		

		for act, video_segment in enumerate(video_segments):
			video_url3 = video_segment['url'].replace('{device}', DEVICE)
			video_data3 = _connection.getURL(video_url3, header = {'X-Forwarded-For' : '12.13.14.15'})
			video_tree3 = BeautifulSoup(video_data3, 'html5lib')
			try:
				duration = video_tree3.find('rendition')['duration']
				closedcaption.append((video_tree3.find('typographic', format = 'ttml'),duration))
			except:
				pass

			video_menu = video_tree3.find('src').string
			hbitrate = -1
			lbitrate = -1
			m3u8_url = None
			m3u_master_data = _connection.getURL(video_menu, savecookie = True)
			m3u_master = _m3u8.parse(m3u_master_data)
			sbitrate = int(_addoncompat.get_setting('quality')) * 1024
			for video_index in m3u_master.get('playlists'):
				bitrate = int(video_index.get('stream_info')['bandwidth'])
				if qbitrate is None:
					if bitrate < lbitrate or lbitrate == -1:
						lbitrate = bitrate
						lm3u8_url = video_index.get('uri')
					if bitrate > hbitrate and bitrate <= sbitrate:
						hbitrate = bitrate
						m3u8_url =  video_index.get('uri')
				elif  (qbitrate  * (100 - BITRATERANGE))/100 <  bitrate  and (qbitrate  * (100 + BITRATERANGE))/100 >  bitrate:
					m3u8_url =  video_index.get('uri')
			if 	m3u8_url is None and qbitrate is None:
				m3u8_url = lm3u8_url
			m3u_data = _connection.getURL(m3u8_url, loadcookie = True)
			key_url = re.compile('URI="(.*?)"').findall(m3u_data)[0]
			key_data = _connection.getURL(key_url, loadcookie = True)		
			key_file = open(_common.KEYFILE + str(act), 'wb')
			key_file.write(key_data)
			key_file.close()
			video_url5 = re.compile('(http:.*?)\n').findall(m3u_data)
			for i, video_item in enumerate(video_url5):
				newurl = base64.b64encode(video_item)
				newurl = urllib.quote_plus(newurl)
				m3u_data = m3u_data.replace(video_item, 'http://127.0.0.1:12345/foxstation/' + newurl)
			
			m3u_data = m3u_data.replace(key_url, 'http://127.0.0.1:12345/play.key' + str(act))


			playfile = open(_common.PLAYFILE.replace('.m3u8',  '_' + str(act)  + '.m3u8'), 'w')
			playfile.write(m3u_data)
			playfile.close()
			video_url6 +=  _common.PLAYFILE.replace('.m3u8',  '_' + str(act)  + '.m3u8') + ' , '
		player._segments = act + 1
		filestring = 'XBMC.RunScript(' + os.path.join(_common.LIBPATH,'_proxy.py') + ', 12345)'
		xbmc.executebuiltin(filestring)
		finalurl = video_url6[:-3]
		localhttpserver = True
		time.sleep(20)

		if (_addoncompat.get_setting('enablesubtitles') == 'true') and (closedcaption is not None):
			convert_subtitles(closedcaption)
			player._subtitles_Enabled = True
		item = xbmcgui.ListItem(path = finalurl)
		if qbitrate is not None:
			item.setThumbnailImage(_common.args.thumb)
			item.setInfo('Video', {	'title' : _common.args.name,
							'season' : _common.args.season_number,
							'episode' : _common.args.episode_number,
							'TVShowTitle' : _common.args.show_title})
		xbmcplugin.setResolvedUrl(pluginHandle, True, item)
		while player.is_active:
			player.sleep(250)


def list_qualities(BASE, video_url = _common.args.url, media_base = VIDEOURL):
	bitrates = []
	if media_base not in video_url:
		video_url = media_base + video_url
	exception = False
	if 'feed' not in video_url:
		swf_url = _connection.getRedirect(video_url, header = {'Referer' : BASE})
		params = dict(item.split("=") for item in swf_url.split('?')[1].split("&"))
		uri = urllib.unquote_plus(params['uri'])
		config_url = urllib.unquote_plus(params['CONFIG_URL'].replace('Other', DEVICE))
		config_data = _connection.getURL(config_url, header = {'Referer' : video_url, 'X-Forwarded-For' : '12.13.14.15'})
		config_tree = BeautifulSoup(config_data, 'html5lib')
		if not config_tree.error:
			feed_url = config_tree.feed.string
			feed_url = feed_url.replace('{uri}', uri).replace('&amp;', '&').replace('{device}', DEVICE).replace('{ref}', 'None').strip()
		else:
			exception = True
			error_text = config_tree.error.string.split('/')[-1].split('_') 
			dialog = xbmcgui.Dialog()
			dialog.ok("Exception", error_text[1], error_text[2])
	else:
		feed_url = video_url

	if not exception:
		feed_data = _connection.getURL(feed_url)
		video_tree = BeautifulSoup(feed_data, 'html.parser', parse_only = SoupStrainer('media:group'))
		video_segments = video_tree.find_all('media:content')
		

		video_segment = video_segments[0]
		video_url3 = video_segment['url'].replace('{device}', DEVICE)
		video_data3 = _connection.getURL(video_url3, header = {'X-Forwarded-For' : '12.13.14.15'})
		video_tree3 = BeautifulSoup(video_data3, 'html5lib')
		video_menu = video_tree3.find('src').string
		m3u8_url = None
		m3u_master_data = _connection.getURL(video_menu, savecookie = True)
		m3u_master = _m3u8.parse(m3u_master_data)
		for video_index in m3u_master.get('playlists'):
			bitrate = int(video_index.get('stream_info')['bandwidth'])
			display = int(bitrate) / 1024
			bitrates.append((display, bitrate))
		return bitrates
				
def clean_subs(data):
	br = re.compile(r'<br.*?>')
	tag = re.compile(r'<.*?>')
	space = re.compile(r'\s\s\s+')
	apos = re.compile(r'&amp;apos;')
	gt = re.compile(r'&gt;+')
	sub = br.sub('\n', data)
	sub = tag.sub(' ', sub)
	sub = space.sub(' ', sub)
	sub = apos.sub('\'', sub)
	sub = gt.sub('>', sub)
	return sub

def convert_subtitles(closedcaption):
	str_output = ''
	j = 0
	count = 0
	for closedcaption_url, duration in closedcaption:
		count = count + 1
		if closedcaption_url is not None:
			subtitle_data = _connection.getURL(closedcaption_url['src'], connectiontype = 0)
			subtitle_data = BeautifulSoup(subtitle_data, 'html.parser', parse_only = SoupStrainer('div'))
			lines = subtitle_data.find_all('p')
			last_line = lines[-1]
			end_time = last_line['end'].split('.')[0].split(':')
			file_duration = int(end_time[0]) * 60 * 60 + int(end_time[1]) * 60 + int(end_time[2])
			delay = int(file_duration) - int(duration)
			for i, line in enumerate(lines):
				if line is not None:
					try:
						sub = clean_subs(_common.smart_utf8(line))
						start_time = _common.smart_utf8(datetime.datetime.strftime(datetime.datetime.strptime(line['begin'], '%H:%M:%S.%f') -  datetime.timedelta(seconds = int(delay)),'%H:%M:%S,%f'))[:-4]
						end_time = _common.smart_utf8(datetime.datetime.strftime(datetime.datetime.strptime(line['end'], '%H:%M:%S.%f') -  datetime.timedelta(seconds = int(delay)),'%H:%M:%S,%f'))[:-4]
						str_output += str(j + i + 1) + '\n' + start_time + ' --> ' + end_time + '\n' + sub + '\n\n'
					except:
						pass
			j = j + i + 1
			file = open(os.path.join(_common.CACHEPATH, 'subtitle-%s.srt' % str(count)), 'w')
			file.write(str_output)
			str_output=''
			file.close()