#!/usr/bin/python
# -*- coding: utf-8 -*-
import base64
import BaseHTTPServer
import cookielib
import httplib
import os
import ustvpaths
import re
import simplejson
import socket
import sys
import time
import urllib
import urllib2
from dns.resolver import Resolver

HOST_NAME = '127.0.0.1'
TIMEOUT = 50
PORT_NUMBER = int(sys.argv[1])

class MyHTTPConnection(httplib.HTTPConnection):
	_dnsproxy = []
	def connect(self):
		resolver = Resolver()
		resolver.nameservers = self._dnsproxy
		answer = resolver.query(self.host, 'A')
		self.host = answer.rrset.items[0].address
		self.sock = socket.create_connection((self.host, self.port))

class MyHTTPHandler(urllib2.HTTPHandler):
	_dnsproxy = []
	def http_open(self, req):
		MyHTTPConnection._dnsproxy = self._dnsproxy 
		return self.do_open(MyHTTPConnection, req)
		
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
		self.answer_request(1)

	def answer_request(self, sendData):
		request_path = self.path[1:]
		request_path = re.sub(r'\?.*', '', request_path)
		if 'stop' in self.path:
			self._writeheaders()
			self.server.stop = True
			print 'Server stopped'
		elif 'key' in self.path:
			try:
				self._writeheaders()
				file = open(ustvpaths.KEYFILE.replace('play%s.key', request_path), 'r')
				data = file.read()
				self.wfile.write(data)
				file.close()
			except IOError:
				self.send_error(404, 'File Not Found: %s' % self.path)
			return
		elif 'm3u8' in self.path:
			try:
				self._writeheaders()
				file = open(ustvpaths.PLAYFILE.replace('play.m3u8', request_path), 'r')
				data = file.read()
				self.wfile.write(data)
				file.close()
			except IOError:
				self.send_error(404, 'File Not Found: %s' % self.path)
			return
		elif 'foxstation' in self.path:
			i, request_path = request_path.split('/', 1)
			realpath = urllib.unquote_plus(request_path[11:])
			fURL = base64.b64decode(realpath)
			self.serveFile(fURL, sendData, cookienum = i)
		elif 'proxy' in self.path:
			realpath = urllib.unquote_plus(request_path)[6:]
			proxyconfig = realpath.split('/')[-1]
			proxy_object = simplejson.loads(proxyconfig)
			if int(proxy_object['connectiontype']) == 1:
				proxies = proxy_object['dns_proxy']
				MyHTTPHandler._dnsproxy = proxies
				handler = MyHTTPHandler
			elif int(proxy_object['connectiontype']) == 2:
				proxy = proxy_object['proxy']
				us_proxy = 'http://' + proxy['us_proxy'] + ':' + proxy['us_proxy_port']
				proxy_handler = urllib2.ProxyHandler({'http' : us_proxy})
				handler = proxy_handler
			realpath = realpath.replace('/' + proxyconfig, '')
			fURL = base64.b64decode(realpath)
			self.serveFile(fURL, sendData, handler)

	def serveFile(self, fURL, sendData, httphandler = None, cookienum = 0):
		cj = cookielib.LWPCookieJar(ustvpaths.COOKIE % str(cookienum))
		if httphandler is None:
			opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
		else:
			opener = urllib2.build_opener(httphandler, urllib2.HTTPCookieProcessor(cj))
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
		if os.path.isfile(ustvpaths.COOKIE % str(cookienum)):
			cj.load(ignore_discard = True)
			cj.add_cookie_header(request)
		response = opener.open(request, timeout = TIMEOUT)
		self.send_response(200)
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
			fileout = self.wfile
			try:
				buf = 'INIT'
				try:
					while ((buf != None) and (len(buf) > 0)):
						buf = response.read(1024 * 1024)
						fileout.write(buf)
						fileout.flush()
					response.close()
					fileout.close()
				except socket.error, e:
					print time.asctime(), 'Client closed the connection.'
					try:
						response.close()
						fileout.close()
					except Exception, e:
						return
				except Exception, e:
					print 'Exception: ' + e
					response.close()
					fileout.close()
			except:
				print 'Exception: ' + e
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

def runserver(server_class = StoppableHTTPServer, handler_class = StoppableHttpRequestHandler):
	server_address = (HOST_NAME, PORT_NUMBER)
	httpd = server_class(server_address, handler_class)
	httpd.serve_forever()

if __name__ == '__main__':
	runserver()
