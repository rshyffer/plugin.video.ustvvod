#!/usr/bin/python
# -*- coding: utf-8 -*-
import _addoncompat
import cookielib
import BaseHTTPServer
import os
import sys
import xbmc
import re
import base64
import socket
import traceback
import time
import urllib
import urllib2

PLUGINPATH = xbmc.translatePath(_addoncompat.get_path())
RESOURCESPATH = os.path.join(PLUGINPATH,'resources')
CACHEPATH = os.path.join(RESOURCESPATH,'cache')
VIDEOPATH = os.path.join(CACHEPATH,'videos')
KEYFILE = os.path.join(CACHEPATH,'play.key')
COOKIE = os.path.join(CACHEPATH,'cookie.txt')

HOST_NAME = 'localhost'
PORT_NUMBER = int(sys.argv[1])

class StoppableHTTPServer(BaseHTTPServer.HTTPServer):
	def serve_forever(self):
		self.stop = False
		while not self.stop:
			self.handle_request()

class StoppableHttpRequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):
	def _writeheaders(self):
		self.send_response(200)
		self.send_header('Content-type', 'text/html')
		self.end_headers()

	def do_HEAD(self):
		self._writeheaders()

	def do_GET(self):
		print 'XBMCLocalProxy: Serving GET request...'
		self.answer_request(1)

	def answer_request(self, sendData):
		request_path = self.path[1:]
		request_path = re.sub(r'\?.*', '', request_path)
		if 'stop' in self.path:
			self._writeheaders()
			self.server.stop = True
			print 'Server stopped'
		elif 'play.key' in self.path:
			try:
				self._writeheaders()
				file = open(KEYFILE.replace('play.key', request_path), 'r')
				data = file.read()
				self.wfile.write(data)
				file.close()
			except IOError:
				self.send_error(404, 'File Not Found: %s' % self.path)
			return
		elif 'foxstation' in self.path:
			realpath = urllib.unquote_plus(request_path[11:])
			fURL = base64.b64decode(realpath)
			self.serveFile(fURL, sendData)

	def serveFile(self, fURL, sendData):
		cj = cookielib.LWPCookieJar(COOKIE) 
		opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
		request = urllib2.Request(url = fURL)
		opener.addheaders = []
		d = {}
		sheaders = self.decodeHeaderString(''.join(self.headers.headers))
		for key in sheaders:
			d[key] = sheaders[key]
			if (key != 'Host'):
				opener.addheaders = [(key, sheaders[key])]
			if (key == 'User-Agent'):
				opener.addheaders = [('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:25.0) Gecko/20100101 Firefox/25.0')]
		if os.path.isfile(COOKIE):
			cj.load(ignore_discard = True)
			cj.add_cookie_header(request)
		response = opener.open(request)
		self.send_response(200)
		print 'XBMCLocalProxy: Sending headers...'
		headers = response.info()
		for key in headers:
			try:
				val = headers[key]
				self.send_header(key, val)
			except Exception, e:
				print e
				pass
		self.end_headers()
		if (sendData):
			print 'XBMCLocalProxy: Sending data...'
			fileout = self.wfile
			try:
				buf = 'INIT'
				try:
					while ((buf != None) and (len(buf) > 0)):
						buf = response.read(8 * 1024)
						fileout.write(buf)
						fileout.flush()
					response.close()
					fileout.close()
					print time.asctime(), 'Closing connection'
				except socket.error, e:
					print time.asctime(), 'Client closed the connection.'
					try:
						response.close()
						fileout.close()
					except Exception, e:
						return
				except Exception, e:
					traceback.print_exc(file = sys.stdout)
					response.close()
					fileout.close()
			except:
				traceback.print_exc()
				fileout.close()
				return
		try:
			fileout.close()
		except:
			pass
			
	def decodeHeaderString(self, hs):
		di = {}
		hss = hs.replace('\r', '').split('\n')
		for line in hss:
			u = line.split(': ')
			try:
				di[u[0]] = u[1]
			except:
				pass
		return di

def runserver(server_class = StoppableHTTPServer,
		handler_class = StoppableHttpRequestHandler):
	server_address = (HOST_NAME, PORT_NUMBER)
	httpd = server_class(server_address, handler_class)
	httpd.serve_forever()
		
if __name__ == '__main__':
	runserver()
