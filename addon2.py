#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import sys
import urllib
import xbmcaddon
import xbmcgui
import xbmcplugin
import xbmcvfs

action              = None
language            = xbmcaddon.Addon().getLocalizedString
getSetting          = xbmcaddon.Addon().getSetting
addonPath           = xbmcaddon.Addon().getAddonInfo("path")
addonLibs           = os.path.join(addonPath,'resources/lib')
addonImages         = os.path.join(addonPath,'resources/images')
addonStations       = os.path.join(addonLibs,'stations')

'''
add addon specific paths to sys.path
'''
sys.path.append(addonLibs)
sys.path.append(addonStations)

'''
import addon specific libs
'''
import common

'''
start of classes
'''
class main:
    def __init__(self):
        params = {}
        splitparams = sys.argv[2][sys.argv[2].find('?') + 1:].split('&')
        for param in splitparams:
            if (len(param) > 0):
                splitparam = param.split('=')
                key = splitparam[0]
                try:    value = splitparam[1].encode("utf-8")
                except: value = splitparam[1]
                params[key] = value

        try:        action = urllib.unquote_plus(params["action"])
        except:     action = None
        try:        channel = urllib.unquote_plus(params["channel"])
        except:     channel = None
        try:        subclass = urllib.unquote_plus(params["subclass"])
        except:     subclass = None
        try:        name = urllib.unquote_plus(params["name"])
        except:     name = None
        try:        url = urllib.unquote_plus(params["url"])
        except:     url = None
        try:        image = urllib.unquote_plus(params["image"])
        except:     image = None
        
        if action == None:                            root().get()
        elif action == 'tv':                          root().tv(channel, subclass, name, url, image)
        elif action == 'masterliste':                 root().masterliste()
        elif action == 'favorlist':                   root().favorlist()

class root():
    def get(self):
        rootList = []
        rootList.append({'name': 39000, 'image': 'fav.png', 'action': 'masterliste'})
        rootList.append({'name': 39002, 'image': 'allshows.png', 'action': 'favorlist'})
        for channel in station().getList():
            if getSetting(channel) == 'true':
                stationModule = __import__(channel)
                stationName = station().getInfo(channel, stationModule, 'NAME')
                stationDesc = station().getInfo(channel, stationModule, 'DESCRIPTION')
                rootList.append({'name': stationName, 'desc': stationDesc, 'image': channel+'.png', 'action': 'tv', 'channel': channel})
        index().rootList(rootList)

    def tv(self, channel, subclass, name, url, image):
        if subclass == None:
            common.root_list(channel)

    def masterliste():
        xbmcplugin.addSortMethod(pluginHandle, xbmcplugin.SORT_METHOD_LABEL)
        common.load_showlist()
        common.set_view('tvshows')
        xbmcplugin.endOfDirectory(pluginHandle)

    def favorlist():   
        xbmcplugin.addSortMethod(pluginHandle, xbmcplugin.SORT_METHOD_LABEL)
        common.load_showlist(favored = 1)
        common.set_view('tvshows')
        xbmcplugin.endOfDirectory(pluginHandle)

class station():
    def getList(self):
        stationList = []
        dirs, files = xbmcvfs.listdir(addonStations)
        for file in files:
            if file.endswith('.py'):
                stationName = file.split('.')[0]
                stationList.append(stationName)
        return stationList  

    def getInfo(self, channel, stationModule, item):
        returnValue = ''
        if hasattr(stationModule, 'SITE') and hasattr(stationModule, 'masterlist'):
            if not hasattr(stationModule, item):
                setattr(stationModule, item, channel)
            return eval('stationModule.'+item)
        else:
            print "error loading site, SITE and masterlist must be defined!"

class index():
    def addonArt(self, image):
        if image.startswith('http://'):
            pass
        else:
            if image == 'fanart.jpg': image = '-'
            elif image == 'fav.png': image = os.path.join(addonImages,'fav.png')
            elif image == 'allshows.png': image = os.path.join(addonImages,'allshows.png')
            else: image = os.path.join(addonImages,image)
        return image

    def rootList(self, rootList):
        if rootList == None or len(rootList) == 0: return
        addonFanart = self.addonArt('fanart.jpg')
        total = len(rootList)
        for i in rootList:
            try:
                root = i['action']
                image = self.addonArt(i['image'])
                try: name = language(i['name']).encode("utf-8")
                except: name = i['name']
                try: desc = i['desc']
                except: desc = name
                u = '%s?action=%s' % (sys.argv[0], root)
                try: u += '&channel=%s' % urllib.quote_plus(i['channel'])
                except: pass
                try: u += '&subclass=%s' % urllib.quote_plus(i['subclass'])
                except: pass
                try: u += '&url=%s' % urllib.quote_plus(i['url'])
                except: pass
                item = xbmcgui.ListItem(name, iconImage='DefaultFolder.png', thumbnailImage=image)
                item.setInfo(type='video', infoLabels={'label': name, 'title': name, 'plotoutline': desc})
                item.setProperty('Fanart_Image', addonFanart)
                xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=item, isFolder=True, totalItems=total)
            except:
                pass
        xbmcplugin.endOfDirectory(int(sys.argv[1]), cacheToDisc=True)

def modes():
    if sys.argv[2] == '':
        all_description = ''
        networks = common.get_networks()
        networks.sort(key = lambda x: x.SITE.replace('the', ''))
        for network in networks:
            if getSetting(network.SITE) == 'true':
                if network.NAME.endswith(', The'):
                    name = 'The ' + network.NAME.replace(', The', '')
                all_description += network.NAME + ', '
        count = 0
        common.add_directory(language(39000), 'Favorlist', 'NoUrl', thumb = ustvpaths.FAVICON, count = count, description = language(39001) + '\n' + all_description)
        count += 1
        common.add_directory(language(39002), 'Masterlist', 'NoUrl', thumb = ustvpaths.ALLICON, count = count, description = language(39003) + '\n' + all_description)
        count += 1
        for network in networks:
            network_name = network.NAME
            station_icon = os.path.join(ustvpaths.IMAGEPATH, network.SITE + '.png')
            if network_name.endswith(', The'):
                network_name = 'The ' + network_name.replace(', The', '')
            if getSetting(network.SITE) == 'true':
                common.add_directory(network_name, network.SITE, 'rootlist', thumb = station_icon, fanart = ustvpaths.PLUGINFANART, description = network.DESCRIPTION, count = count)
            count += 1
        xbmcplugin.addSortMethod(pluginHandle, xbmcplugin.SORT_METHOD_PLAYLIST_ORDER)
        common.set_view()
        xbmcplugin.endOfDirectory(pluginHandle)
    elif common.args.mode == 'Masterlist':
        xbmcplugin.addSortMethod(pluginHandle, xbmcplugin.SORT_METHOD_LABEL)
        common.load_showlist()
        common.set_view('tvshows')
        xbmcplugin.endOfDirectory(pluginHandle)
    elif common.args.sitemode == 'rootlist':
        xbmcplugin.addSortMethod(pluginHandle, xbmcplugin.SORT_METHOD_LABEL)
        common.root_list(common.args.mode)
        xbmcplugin.endOfDirectory(pluginHandle)
    elif common.args.mode == 'Favorlist':   
        xbmcplugin.addSortMethod(pluginHandle, xbmcplugin.SORT_METHOD_LABEL)
        common.load_showlist(favored = 1)
        common.set_view('tvshows')
        xbmcplugin.endOfDirectory(pluginHandle)
    elif common.args.mode == 'contextmenu':
        getattr(contextmenu, common.args.sitemode)()
    elif common.args.mode == 'common':
        getattr(common, common.args.sitemode)()
    else:
        network = common.get_network(common.args.mode)
        if network:
            getattr(network, common.args.sitemode)()
            if 'episodes' in  common.args.sitemode and getSetting('add_episode_identifier') == 'false':
                try:
                    xbmcplugin.addSortMethod(pluginHandle, xbmcplugin.SORT_METHOD_DATEADDED)
                except:
                    pass
                xbmcplugin.addSortMethod(pluginHandle, xbmcplugin.SORT_METHOD_EPISODE)
                xbmcplugin.addSortMethod(pluginHandle, xbmcplugin.SORT_METHOD_UNSORTED)
            if not common.args.sitemode.startswith('play'):
                xbmcplugin.endOfDirectory(pluginHandle)

print '\n\n\n start of USTV VoD plugin'
main()
