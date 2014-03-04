#!/usr/bin/python
# -*- coding: utf-8 -*-
import _addoncompat
import cookielib
import os
import simplejson
import urllib
import urllib2
import socks
import socket
import time
import xbmc
from dns.resolver import Resolver
from httplib import HTTPConnection

PLUGINPATH = xbmc.translatePath(_addoncompat.get_path())
RESOURCESPATH = os.path.join(PLUGINPATH,'resources')
CACHEPATH = os.path.join(RESOURCESPATH,'cache')
COOKIE = os.path.join(CACHEPATH,'cookie.txt')
DNS_REFESH_DELAY = 10
IPURL = 'http://icanhazip.com'
IPFILE = os.path.join(CACHEPATH,'ip.txt')

class MyHTTPConnection(HTTPConnection):
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

class SocksiPyConnection(HTTPConnection):
    def __init__(self, proxytype, proxyaddr, proxyport = None, rdns = True, username = None, password = None, *args, **kwargs):
        self.proxyargs = (proxytype, proxyaddr, proxyport, rdns, username, password)
        HTTPConnection.__init__(self, *args, **kwargs)
 
    def connect(self):
        self.sock = socks.socksocket()
        self.sock.setproxy(*self.proxyargs)
        if isinstance(self.timeout, float):
            self.sock.settimeout(self.timeout)
        self.sock.connect((self.host, self.port))
            
class SocksiPyHandler(urllib2.HTTPHandler):
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kw = kwargs
        urllib2.HTTPHandler.__init__(self)
 
    def http_open(self, req):
        def build(host, port=None, strict=None, timeout=0):    
            conn = SocksiPyConnection(*self.args, host = host, port = port, strict = strict, timeout = timeout, **self.kw)
            return conn
        return self.do_open(build, req)

def prepare_dns_proxy(cj):
	update_url = _addoncompat.get_setting('dns_update_url')
	if update_url:
		try:
			t = os.path.getmtime(IPFILE)
			now = time.time()
			elapsed = now - t
		except:
			elapsed = -1
		try:
			file = open(IPFILE, 'r')
			oldip = file.read()
			file.close()
		except:
			oldip = ''
		if elapsed > DNS_REFESH_DELAY or elapsed == -1:
			myip = getURL(IPURL, connectiontype = 0)
			if myip != oldip:
				oldip = myip
				getURL(update_url, connectiontype = 0)
		newfile = file = open(IPFILE, 'w')
		file.write(oldip)
		file.close()
	dnsproxy = []
	dnsproxy.append(_addoncompat.get_setting('dns_proxy'))
	dnsproxy.append(_addoncompat.get_setting('dns_proxy_2'))
	MyHTTPHandler._dnsproxy = dnsproxy
	opener = urllib2.build_opener(MyHTTPHandler, urllib2.HTTPCookieProcessor(cj))
	return opener

def prepare_us_proxy(cj):
	if (_addoncompat.get_setting('us_proxy_socks5') == 'true'):
		if ((_addoncompat.get_setting('us_proxy_pass') is not '') and (_addoncompat.get_setting('us_proxy_user') is not '')):
			print 'Using socks5 authenticated proxy: ' + _addoncompat.get_setting('us_proxy') + ':' + _addoncompat.get_setting('us_proxy_port')
			opener = urllib2.build_opener(SocksiPyHandler(socks.PROXY_TYPE_SOCKS5, _addoncompat.get_setting('us_proxy'), int(_addoncompat.get_setting('us_proxy_port')), True, _addoncompat.get_setting('us_proxy_user'), _addoncompat.get_setting('us_proxy_pass')))
		else:
			print 'Using socks5 proxy: ' + _addoncompat.get_setting('us_proxy') + ':' + _addoncompat.get_setting('us_proxy_port')
			opener = urllib2.build_opener(SocksiPyHandler(socks.PROXY_TYPE_SOCKS5, _addoncompat.get_setting('us_proxy'), int(_addoncompat.get_setting('us_proxy_port'))))
	elif (_addoncompat.get_setting('us_proxy_socks5') == 'false'):
		us_proxy = 'http://' + _addoncompat.get_setting('us_proxy') + ':' + _addoncompat.get_setting('us_proxy_port')
		proxy_handler = urllib2.ProxyHandler({'http' : us_proxy})
		if ((_addoncompat.get_setting('us_proxy_pass') is not '') and (_addoncompat.get_setting('us_proxy_user') is not '')):
			print 'Using authenticated proxy: ' + us_proxy
			password_mgr = urllib2.HTTPPasswordMgrWithDefaultRealm()
			password_mgr.add_password(None, us_proxy, _addoncompat.get_setting('us_proxy_user'), _addoncompat.get_setting('us_proxy_pass'))
			proxy_auth_handler = urllib2.ProxyBasicAuthHandler(password_mgr)
			opener = urllib2.build_opener(proxy_handler, proxy_auth_handler, urllib2.HTTPCookieProcessor(cj))
		else:
			print 'Using proxy: ' + us_proxy
			opener = urllib2.build_opener(proxy_handler, urllib2.HTTPCookieProcessor(cj))
	return opener

def getURL(url, values = None, header = {}, amf = False, savecookie = False, loadcookie = False, connectiontype = _addoncompat.get_setting('connectiontype')):
	try:
		old_opener = urllib2._opener
		cj = cookielib.LWPCookieJar(COOKIE) 
		if int(connectiontype) == 0:
			opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
			urllib2.install_opener(opener)
		if int(connectiontype) == 1:
			urllib2.install_opener(prepare_dns_proxy(cj))
		elif int(connectiontype) == 2:
			urllib2.install_opener(prepare_us_proxy(cj))
		print '_connection :: getURL :: url = ' + url
		if values is None:
			req = urllib2.Request(bytes(url))
		else:
			if amf == False:
				data = urllib.urlencode(values)
			elif amf == True:
				data = values
			req = urllib2.Request(bytes(url), data)
		header.update({'User-Agent' : 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:25.0) Gecko/20100101 Firefox/25.0'})
		for key, value in header.iteritems():
			req.add_header(key, value)
		if loadcookie is True:
			try:
				cj.load(ignore_discard = True)
				cj.add_cookie_header(req)
			except:
				print 'Cookie Loading Error'
				pass
		response = urllib2.urlopen(req)
		link = response.read()
		if savecookie is True:
			try:
				cj.save(ignore_discard = True)
			except:
				print 'Cookie Saving Error'
				pass	
		response.close()
		urllib2.install_opener(old_opener)
	except urllib2.HTTPError, error:
		print 'HTTP Error reason: ', error
		return error.read()
	else:
		return link

def getRedirect(url, values = None , header = {}, connectiontype = _addoncompat.get_setting('connectiontype')):
	try:
		old_opener = urllib2._opener
		cj = cookielib.LWPCookieJar(COOKIE)
		if int(connectiontype) == 1:
			urllib2.install_opener(prepare_dns_proxy(cj))
		elif int(connectiontype) == 2:
			urllib2.install_opener(prepare_us_proxy(cj))
		print '_connection :: getRedirect :: url = ' + url
		if values is None:
			req = urllib2.Request(bytes(url))
		else:
			data = urllib.urlencode(values)
			req = urllib2.Request(bytes(url), data)
		header.update({'User-Agent' : 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:25.0) Gecko/20100101 Firefox/25.0'})
		if connectiontype == 2:
			header.update({'X-Forwarded-For' : _addoncompat.get_setting('us_proxy')})
		for key, value in header.iteritems():
			req.add_header(key, value)
		response = urllib2.urlopen(req)
		finalurl = response.geturl()
		response.close()
		urllib2.install_opener(old_opener)
	except urllib2.HTTPError, error:
		print 'HTTP Error reason: ', error
		return error.read()
	else:
		return finalurl
