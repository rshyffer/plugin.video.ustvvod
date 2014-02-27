#!/usr/bin/python
# -*- coding: utf-8 -*-
import _addoncompat
import cookielib
import os
import simplejson
import urllib
import urllib2
import socket
import xbmc
from dns.resolver import Resolver
from httplib import HTTPConnection

TUNLRURL = 'http://tunlr.net/tunapi.php?action=getdns&version=1&format=json'
TUNLRCHECK = 'http://gatekeeper-api.tunlr.net/api_v1/check_activation'
TUNLRUPDATE = 'http://gatekeeper-api.tunlr.net/api_v1/update_ip/%s'
PLUGINPATH = xbmc.translatePath(_addoncompat.get_path())
RESOURCESPATH = os.path.join(PLUGINPATH,'resources')
CACHEPATH = os.path.join(RESOURCESPATH,'cache')
COOKIE = os.path.join(CACHEPATH,'cookie.txt')

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

def prepare_dns_proxy(cj):
	dnsproxy = []
	dnsproxy.append(_addoncompat.get_setting('dns_proxy'))
	MyHTTPHandler._dnsproxy = dnsproxy
	opener = urllib2.build_opener(MyHTTPHandler, urllib2.HTTPCookieProcessor(cj))
	return opener

def prepare_tunlr_dns(cj):
	dnsproxy = []
	tunlr_key = _addoncompat.get_setting('tunlr_key')
	if tunlr_key != '':
		request = urllib2.Request(TUNLRCHECK)
		response = urllib2.urlopen(request)
		checkdata = response.read()
		response.close()
		tunlr_check = simplejson.loads(checkdata)
		if tunlr_check['success'] and not tunlr_check['activated']:
			request = urllib2.Request(TUNLRUPDATE % tunlr_key)
			response = urllib2.urlopen(request)
			response.close()
	request = urllib2.Request(TUNLRURL)
	response = urllib2.urlopen(request)
	dnsdata = response.read()
	response.close()
	tunlr_dns = simplejson.loads(dnsdata)
	dnsproxy.append(tunlr_dns['dns1'])
	dnsproxy.append(tunlr_dns['dns2'])
	MyHTTPHandler._dnsproxy = dnsproxy
	opener = urllib2.build_opener(MyHTTPHandler, urllib2.HTTPCookieProcessor(cj))
	return opener

def prepare_us_proxy(cj):
	us_proxy = 'http://' + _addoncompat.get_setting('us_proxy') + ':' + _addoncompat.get_setting('us_proxy_port')
	proxy_handler = urllib2.ProxyHandler({'http':us_proxy})
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
		elif int(connectiontype) == 3:
			urllib2.install_opener(prepare_tunlr_dns(cj))
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
		elif int(connectiontype) == 3:
			urllib2.install_opener(prepare_tunlr_dns(cj))
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
