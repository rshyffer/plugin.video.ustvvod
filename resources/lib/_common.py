#!/usr/bin/python
# -*- coding: utf-8 -*-
import _addoncompat
import _connection
import _database
import base64
import os
import sys
import time
import urllib
import xbmc
import xbmcaddon
import xbmcgui
import xbmcplugin
from bs4 import BeautifulSoup

pluginHandle = int(sys.argv[1])

PLUGINPATH = xbmc.translatePath(_addoncompat.get_path())
RESOURCESPATH = os.path.join(PLUGINPATH,'resources')
CACHEPATH = os.path.join(RESOURCESPATH,'cache')
IMAGEPATH = os.path.join(RESOURCESPATH,'images')
LIBPATH = os.path.join(RESOURCESPATH,'lib')
PLUGINFANART = os.path.join(PLUGINPATH,'fanart.jpg')
FAVICON = os.path.join(PLUGINPATH,'fav.png')
ALLICON = os.path.join(PLUGINPATH,'allshows.png')
PLAYFILE = os.path.join(CACHEPATH,'play.m3u8')
KEYFILE = os.path.join(CACHEPATH,'play.key')
SUBTITLE = os.path.join(CACHEPATH,'subtitle.srt')
SUBTITLESMI = os.path.join(CACHEPATH,'subtitle.smi')
COOKIE = os.path.join(CACHEPATH,'cookie.txt')

ADDONID = 'plugin.video.ustvvod'
TVDBAPIKEY = '03B8C17597ECBD64'
TVDBURL = 'http://thetvdb.com'
TVDBBANNERS = 'http://thetvdb.com/banners/'
TVDBSERIESLOOKUP = 'http://www.thetvdb.com/api/GetSeries.php?seriesname='

class _Info:
	def __init__(self, s):
		args = urllib.unquote_plus(s).split(' , ')
		for x in args:
			try:
				(k, v) = x.split('=', 1)
				setattr(self, k, v.strip('"\''))
			except:
				pass

args = _Info(sys.argv[2][1:].replace('&', ' , '))

site_dict= {'abc': 'ABC',
			'abcfamily': 'ABC Family',
			'abcnews': 'ABC News',
			'adultswim': 'Adult Swim',
			'aetv':'A&E',
			'amc': 'AMC',
			'bravo': 'Bravo',
			'cbs': 'CBS',
			'comedy': 'Comedy Central',
			'crackle': 'Crackle',
			'disney':'Disney',
			'disneyjunior':'Disney Junior',
			'disneyxd':'Disney XD',
			'fox': 'FOX',
			'marvelkids': 'Marvel Kids',
			'msnbc': 'MSNBC',
			'mtv': 'MTV',
			'natgeo': 'National Geographic',
			'natgeowild': 'Nat Geo Wild',
			'nbc': 'NBC',
			'nick': 'Nickelodeon',
			'nickteen': 'Nick Teen',
			'nicktoons': 'Nick Toons',
			'oxygen': 'Oxygen',
			'pbs': 'PBS',
			'pbskids': 'PBS Kids',
			'spike': 'Spike TV',
			'syfy': 'SyFy',
			'thecw': 'CW, The',
			'thewbkids': 'WB Kids, The',
			'tvland': 'TV Land',
			'usa': 'USA Network',
			'vh1': 'VH1',
			}
site_descriptions= {'abc': "ABC Television Network provides broadcast programming to more than 220 affiliated stations across the U.S. The Network encompasses ABC News, which is responsible for news programming on television and other digital platforms; ABC Entertainment Group, a partnership between ABC Studios and ABC Entertainment responsible for the network's primetime and late-night entertainment programming; ABC Daytime, producer of the network's successful cache of daytime programming; as well as ABC Kids, the Network's children's programming platform. ABC's multiplatform business initiative includes the Interactive Emmy Award-winning broadband player on ABC.com.",
					'abcfamily': "ABC Family's programming is a combination of network-defining original series and original movies, quality acquired series and blockbuster theatricals. ABC Family features programming reflecting today's families, entertaining and connecting with adults through relatable stories about today's relationships, told with a mix of diversity, passion, humor and heart. Targeting Millennial viewers ages 14-34, ABC Family is advertiser supported.",
					'abcnews': "ABC News is responsible for all of the ABC Television Network's news programming on a variety of platforms: TV, radio and the Internet.",
					'adultswim': "Cartoon Network (CartoonNetwork.com), currently seen in more than 97 million U.S. homes and 166 countries around the world, is Turner Broadcasting System, Inc.'s ad-supported cable service now available in HD offering the best in original, acquired and classic entertainment for youth and families.  Nightly from 10 p.m. to 6 a.m. (ET, PT), Cartoon Network shares its channel space with Adult Swim, a late-night destination showcasing original and acquired animated and live-action programming for young adults 18-34 ",
					'aetv': "A&E is Real Life. Drama.  Now reaching more than 99 million homes, A&E is television that you can't turn away from; where unscripted shows are dramatic and scripted dramas are authentic.  A&E offers a diverse mix of high quality entertainment ranging from the network's original scripted series to signature non-fiction franchises, including the Emmy-winning \'Intervention,\' \'Dog The Bounty Hunter,\' \'Hoarders,\' \'Paranormal State\' and \'Criss Angel Mindfreak,\' and the most successful justice shows on cable, including \'The First 48\' and \'Manhunters.\'  The A&E website is located at www.aetv.com.",
					'amc': "AMC reigns as the only cable network in history to ever win the Emmy' Award for Outstanding Drama Series three years in a row, as well as the Golden Globe' Award for Best Television Series - Drama for three consecutive years.  Whether commemorating favorite films from every genre and decade or creating acclaimed original programming, the AMC experience is an uncompromising celebration of great stories.  AMC's original stories include 'Mad Men,' 'Breaking Bad,' 'The Walking Dead,' 'The Killing' and 'Hell on Wheels.'  AMC further demonstrates its commitment to the art of storytelling with AMC's Docu-Stories, a slate of unscripted original series, as well as curated movie franchises like AMC's Can't Get Enough and AMC's Crazy About.  Available in more than 97 million homes (Source: Nielsen Media Research), AMC is owned and operated by AMC Networks Inc. and its sister networks include IFC, Sundance Channel and WE tv.  AMC is available across all platforms, including on-air, online, on demand and mobile.  AMC: Story Matters HereSM.",
					'bravo': "With more breakout stars and critically-acclaimed original series than any other network on cable, Bravo's original programming - from hot cuisine to haute couture - delivers the best in food, fashion, beauty, design and pop culture to the most engaged and upscale audience in cable. Consistently one of the fastest growing top 20 ad-supported cable entertainment networks, Bravo continues to translate buzz into reality with critically-acclaimed breakout creative competition and docu-series, including the Emmy and James Beard Award-winning No. 1 food show on cable \"Top Chef,\" two-time Emmy Award winner \"Kathy Griffin: My Life on the D-List,\" the 14-time Emmy nominated \"Inside the Actors Studio,\" the hit series \"Shear Genius,\" \"Top Chef Masters,\" \"Flipping Out,\" \"The Rachel Zoe Project,\" \"Tabatha's Salon Takeover,\" \"Million Dollar Listing,\" \"The Millionaire Matchmaker,\" and the watercooler sensation that is \"The Real Housewives\" franchise. Bravo reaches its incredibly unique audience through every consumer touch point and across all platforms on-air, online and on the go, providing the network\'s highly-engaged fans with a menu of options to experience the network in a four-dimensional manner. Bravo is a program service of NBC Universal Cable Entertainment, a division of NBC Universal one of the world\'s leading media and entertainment companies in the development, production, and marketing of entertainment, news and information to a global audience. Bravo has been an NBC Universal cable network since December 2002 and was the first television service dedicated to film and the performing arts when it launched in December 1980. For more information visit www.bravotv.com",
					'cbs': "CBS was established in 1928, when founder William Paley purchased 16 independent radio stations and christened them the Columbia Broadcast System. Today, with more than 200 television stations and affiliates reaching virtually every home in the United States, CBS's total primetime network lineup is watched by more than 130 million people a week during the 2010/2011 season. The Network has the #1 drama/scripted program, NCIS; #1 sitcom, TWO AND A HALF MEN; #1 newsmagazine, 60 MINUTES; and #1 daytime drama, THE YOUNG AND THE RESTLESS. Its programming arms include CBS Entertainment, CBS News and CBS Sports.",
					'comedy': "COMEDY CENTRAL, the #1 brand in comedy, is available to over 99 million viewers nationwide and is a top-rated network among men ages 18-24 and 18-34 and adults ages 18-49.  With on-air, online and on-the-go mobile technology, COMEDY CENTRAL gives its audience access to the cutting-edge, laugh-out-loud world of comedy wherever they go.  Hit series include Tosh.0, Workaholics, Futurama, Key & Peele, Ugly Americans and the Emmy' and Peabody' Award-winning series The Daily Show with Jon Stewart, The Colbert Report and South Park.  COMEDY CENTRAL is also involved in producing nationwide stand-up tours, boasts its own record label and operates one of the most successful home entertainment divisions in the industry.  COMEDY CENTRAL is owned by, and is a registered trademark of Comedy Partners, a wholly-owned unit of Viacom Inc. (NASDAQ: VIA and VIAB).  For more information visit COMEDY CENTRAL's press Web site at www.cc.com/press or the network's consumer site at www.comedycentral.com and follow us on Twitter @ComedyCentralPR for the latest in breaking news updates, behind-the-scenes information and photos.",
					'crackle': "Crackle, Inc. is a multi-platform video entertainment network and studio that distributes full length, uncut, movies, TV shows and original programming in our users favorite genres ï¿½ like comedy, action, crime, horror, Sci-Fi, and thriller. Crackles channels and shows reach a global audience across the Internet, in the living room, and on devices including a broad range of Sony electronics.",
					'disney': "Disney Channel is a 24-hour kid-driven, family inclusive television network that taps into the world of kids and families through original series and movies. It is currently available on basic cable and satellite in more than 98 million U.S. homes and in nearly 400 million households via 42 Disney Channels and free-to-air broadcast partners around the world.",
					'disneyjunior': "Disney Junior, part of Disney Channels Worldwide, is a global television and online brand expressly for kids age 2-7. Disney Junior invites mom and dad to join their child in the Disney experience of magical, musical and heartfelt stories and characters, both classic and new, while incorporating specific learning and development themes designed for young children",
					'disneyxd': "Disney XD is a basic cable channel and multi-platform brand showcasing a compelling mix of live-action and animated programming for kids aged 6-14, hyper-targeting boys (while still including girls) and their quest for discovery, accomplishment, sports, adventure and humor. Disney XD branded content spans television, online, mobile and VOD platforms. The programming includes series, movies and short-form, as well as sports-themed programming developed with ESPN.",
					'fox': "Fox Broadcasting Company is a unit of News Corporation and the leading broadcast television network among Adults 18-49. FOX finished the 2010-2011 season at No. 1 in the key adult demographic for the seventh consecutive year ' a feat that has never been achieved in broadcast history ' while continuing to dominate all network competition in the more targeted Adults 18-34 and Teen demographics. FOX airs 15 hours of primetime programming a week as well as late-night entertainment programming, major sports and Sunday morning news.",
					'marvelkids': 'Marvel started in 1939 as Timely Publications, and by the early 1950s had generally become known as Atlas Comics. Marvel\'s modern incarnation dates from 1961, the year that the company launched Fantastic Four and other superhero titles created by Stan Lee, Jack Kirby, Steve Ditko, and others. Marvel counts among its characters such well-known properties as Spider-Man, the X-Men, the Fantastic Four, Iron Man, the Hulk, Thor, Captain America and Daredevil; antagonists such as the Green Goblin, Magneto, Doctor Doom, Galactus, and the Red Skull. Most of Marvel\'s fictional characters operate in a single reality known as the Marvel Universe, with locations that mirror real-life cities such as New York, Los Angeles and Chicago.',
					'msnbc': "MSNBC is an American basic cable and satellite news television channel that is owned by the NBCUniversal News Group, a unit of the NBCUniversal Television Group division of NBCUniversal. The channel features news, information, and political opinion programming. Its name was derived from the most common abbreviations for Microsoft and the National Broadcasting Company.\nMSNBC and msnbc.com were founded in 1996 as partnerships of Microsoft and General Electric's NBC unit, which is now NBCUniversal. The online partnership of msnbc.com ended on July 16, 2012 and the site was rebranded as NBCNews.com. MSNBC shares the NBC logo of a rainbow peacock with its sister channels NBC, CNBC, and NBC Sports Network.\nBeginning in the mid-2000s, MSNBC assumed an increasingly liberal stance in its opinion programming. In October 2010, it publicly acknowledged this with a marketing campaign it called \"Lean Forward\". Further, in September of 2013, MSNBC launched its revamped official website under the tagline, \"What Progressives Have Been Waiting For.\"\nAs of August 2013, approximately 94,519,000 American households (82.77% of households with television) receive MSNBC",
					'mtv': "MTV is Music Television. It is the music authority where young adults turn to find out what's happening and what's next in music and popular culture. MTV reaches 412 million households worldwide, and is the #1 Media Brand in the world. Only MTV can offer the consistently fresh, honest, groundbreaking, fun and inclusive youth-oriented programming found nowhere else in the world. MTV is a network that transcends all the clutter, reaching out beyond barriers to everyone who's got eyes, ears and a television set.",
					'natgeo': "Critically acclaimed non-fiction. Network providing info-rich entertainment that changes the way you see the world.  A trusted source for more than 100 years, National Geographic provides NGC with unique access to the most respected scientists, journalists and filmmakers, resulting in innovative and contemporary programming of unparalleled quality.  NGC HD continues to provide spectacular imagery that National Geographic is known for in stunning high-definition.  A leader on the digital landscape, NGC HD is one of the top five HD networks and is the #1 channel viewers would most like to see in high definition for the fourth year in a row.  Additionally, the channel received some of the highest ratings in key categories, such as 'high quality,' 'information' and 'favorite' in the prestigious benchmark study among all 55 measured cable and broadcast networks. In addition, NGC VOD is a category leader. Building on its success as one of the fastest-growing cable networks year-to-year in ratings and distribution since launching in January 2001, NGC now reaches more than 70 million homes, with carriage on all major cable and satellite television providers.  Highlighted programming in 2010 includes: New episodes of Expedition Great White, the popular series, Taboo and Border Wars.  In addition, new seasons of series' WORLD'S TOUGHEST FIXES and LOCKED UP ABROAD.  2010 specials include DRUGS, INC., LOST GOLD OF THE DARK AGES and GREAT MIGRATIONS  For more information, please visit www.natgeotv.com.",
					'natgeowild': "Experience the best, most intimate encounters with wildlife ever seen on television.  Backed by its unparallel reputation and blue chip programming, Nat Geo Wild brings viewers documentaries entirely focused on the animal kingdom and the world it inhabits.  From the most remote environments, to the forbidding depths of our oceans, to the protected parks in our backyards, Nat Geo Wild uses spectacular cinematography and intimate storytelling to take viewers on unforgettable journeys into the wild world.  Nat Geo Wild launched in August 2006 and is now available in Hong Kong, Singapore, the U.K., Australia, Latin America, France, Italy, Portugal, Turkey and other territories in Europe.  Nat Geo Wild HD launched in the U.K. in March 2009 and is also available in Poland.  Additional launches are expected globally.",
					'nbc': "NBC Entertainment develops and schedules programming for the network's primetime, late-night, and daytime schedules. NBC's quality programs and balanced lineup have earned the network critical acclaim, numerous awards, and ratings success. The network has earned more Emmy Awards than any network in television history. NBC's roster of popular scripted series includes critically acclaimed comedies like Emmy winners The Office, starring Steve Carell, and 30 Rock, starring Alec Baldwin and Tina Fey. Veteran, award-winning dramas on NBC include Law & Order: SVU, Chuck, and Friday Night Lights. Unscripted series for NBC include the hits The Biggest Loser, Celebrity Apprentice, and America's Got Talent. NBC's late-night story is highlighted by The Tonight Show with Jay Leno, Late Night with Jimmy Fallon, Last Call with Carson Daly, and Saturday Night Live. NBC Daytime's Days of Our Lives consistently finishes among daytime's top programs in the valuable women 18-34 category. Saturday mornings the network broadcasts Qubo on NBC, a three-hour block that features fun, entertaining, and educational programming for kids, including the award-winning, 3-D animated series Veggie Tales.",
					'nick': "Nickelodeon, now in its 31st year, is the number-one entertainment brand for kids. It has built a diverse, global business by putting kids first in everything it does. The company includes television programming and production in the United States and around the world, plus consumer products, online, recreation, books and feature films. Nickelodeon's U.S. television network is seen in more than 100 million households and has been the number-one-rated basic cable network for 16 consecutive years.",
					'nickteen': "Launched in April 2002, TeenNick (formerly named The N) features 24-hours of teen programming. Our award-winning and original programming, including Degrassi: The Next Generation, Beyond the Break, The Best Years and The Assistants, presents sharp and thoughtful content that focuses on the real life issues teens face every day. On our Emmy winning website, www.Teennick.com, fans get complete access to behind-the-scenes interviews, pictures and videos, plus a robust community of 2 million members who interact with message boards, user profiles and blogs. TeenNick'Ûªs broadband channel, The Click, features full-length episodes of the network'Ûªs hit original series along with outtakes, sneak peeks and webisodes of TeenNick series created exclusively for broadband. The Click provides teens with the ability to create video mash-ups and watch, comment on and share content from their favorite TeenNick shows with all of their friends, wherever they go.",
					'nicktoons': "Nicktoons offers 24 hours of animated programming that includes Wolverine and the X-Men, Iron Man: Armored Adventures, Fantastic Four: World's Greatest Heroes, Speed Racer: The Next Generation, Kappa Mikey and the Nickelodeon Animation Festival, as well as a roster of hits that have defined kids' and animation lovers' TV, including Avatar: The Last Airbender, Danny Phantom, SpongeBob SquarePants, The Fairly OddParents and The Adventures of Jimmy Neutron, Boy Genius.  It currently reaches 54 million homes via cable, digital cable and satellite, and can be seen on Cablevision, Charter Communications, Comcast Cable, Cox Communications, DirecTV, DISH Network and Time Warner Cable.  Nicktoons is part of the MTV Networks expanded suite of channels available for digital distribution.",
					'oxygen': "Oxygen Media is a multiplatform lifestyle brand that delivers relevant and engaging content to young women who like to \"live out loud.\" Oxygen is rewriting the rulebook for women's media by changing how the world sees entertainment from a young woman's point of view.  Through a vast array of unconventional and original content including \"Bad Girls Club,\" \"Dance Your Ass Off\" and \"Tori & Dean: Home Sweet Hollywood,\" the growing cable network is the premier destination to find unique and groundbreaking unscripted programming.   A social media trendsetter, Oxygen is a leading force in engaging the modern young woman, wherever they are, with popular features online including OxygenLive, shopOholic, makeOvermatic, tweetOverse and hormoneOscope.  Oxygen is available in 76 million homes and online at www.oxygen.com, or on mobile devices at wap.oxygen.com.  Oxygen Media is a service of NBC Universal.",
					'pbs': "PBS and our member stations are America\'s largest classroom, the nation\'s largest stage for the arts and a trusted window to the world. In addition, PBS's educational media helps prepare children for success in school and opens up the world to them in an age-appropriate way.",
					'pbskids': 'PBS Kids is the brand for children\'s programming aired by the Public Broadcasting Service (PBS) in the United States founded in 1993. It is aimed at children ages 2 to 13.',
					'spike': "Spike TV knows what guys like. The brand speaks to the bold, adventuresome side of men with action-packed entertainment, including a mix of comedy, blockbuster movies, sports, innovative originals and live events. Popular shows like The Ultimate Fighter, TNA iMPACT!, Video Game Awards, DEA, MANswers, MXC, and CSI: Crime Scene Investigation, plus the Star Wars and James Bond movie franchises, position Spike TV as the leader in entertainment for men.",
					'syfy': "Syfy is a media destination for imagination-based entertainment. With year round acclaimed original series, events, blockbuster movies, classic science fiction and fantasy programming, a dynamic Web site (www.Syfy.com), and a portfolio of adjacent business (Syfy Ventures), Syfy is a passport to limitless possibilities. Originally launched in 1992 as SCI FI Channel, and currently in 95 million homes, Syfy is a network of NBC Universal, one of the world's leading media and entertainment companies. Syfy. Imagine greater.",
					'thecw': "The CW Network was formed as a joint venture between Warner Bros. Entertainment and CBS Corporation. The CW is America's fifth broadcast network and the only network targeting women 18-34. The network's primetime schedule includes such popular series as America's Next Top Model, Gossip Girl, Hart of Dixie, 90210, The Secret Circle, Supernatural, Ringer, Nikita, One Tree Hill and The Vampire Diaries.",
					'thewbkids': 'The KidsWB Collection of Scooby-Doo, Looney Toons, Batman: The Brave and the Bold, Hanna-Barbera, DC and Warner stars under one roof.',
					'tvland': "TV Land is dedicated to presenting the best in entertainment on all platforms for consumers in their 40s. Armed with a slate of original programming, acquired classic shows, hit movies and fullservice website, TV Land is now seen in over 98 million U.S. homes. TV Land PRIME is TV Land's prime time programming destination designed for people in their mid-forties and the exclusive home to the premieres of the network's original programming, contemporary television series acquisitions and movies.",
					'usa': "USA Network is cable television's leading provider of original series and feature movies, sports events, off-net television shows, and blockbuster theatrical films. USA Network is seen in over 88 million U.S. homes. The USA Network web site is located at www.usanetwork.com. USA Network is a program service of NBC Universal Cable a division of NBC Universal, one of the world's leading media and entertainment companies in the development, production and marketing of entertainment, news and information to a global audience.",
					'vh1': "VH1 connects viewers to the music, artists and pop culture that matter to them most with series, specials, live events, exclusive online content and public affairs initiatives. VH1 is available in 90 million households in the U.S. VH1 also has an array of digital services including VH1 Classic, VH1 Soul and VSPOT, VH1's broadband channel. Connect with VH1 at www.VH1.com.",
					}

def set_view(type = 'root'):
	confluence_views = [500,501,502,503,504,508]
	if type == 'root':
		xbmcplugin.setContent(pluginHandle, 'movies')
	elif type == 'seasons':
		xbmcplugin.setContent(pluginHandle, 'movies')
	else:
		if type == 'tvshows':
			xbmcplugin.addSortMethod(pluginHandle, xbmcplugin.SORT_METHOD_LABEL)
		xbmcplugin.setContent(pluginHandle, type)
	viewenable = _addoncompat.get_setting('viewenable')
	if viewenable == 'true':
		view = int(_addoncompat.get_setting(type + 'view'))
		xbmc.executebuiltin('Container.SetViewMode(' + str(confluence_views[view]) + ')')

def format_date(inputDate = '', inputFormat = '', outputFormat = '%Y-%m-%d', epoch = False):
	if epoch:
		return time.strftime(outputFormat, time.localtime(epoch))
	else:
		return time.strftime(outputFormat, time.strptime(inputDate, inputFormat))

def format_seconds(timestring):
	if timestring[0] == ':':
		timestring = '0' + timestring
	timestring2 = 0
	if len(timestring.split(':')) == 1:
		ftr = [1]
	elif len(timestring.split(':')) == 2:
		ftr = [60,1]
	else:
		ftr = [3600,60,1]
	timestring2 = sum([a*b for a,b in zip(ftr, map(int,timestring.split(':')))])
	return int(timestring2)

def smart_unicode(s):
	"""credit : sfaxman"""
	if not s:
		return ''
	try:
		if not isinstance(s, basestring):
			if hasattr(s, '__unicode__'):
				s = unicode(s)
			else:
				s = unicode(str(s), 'UTF-8')
		elif not isinstance(s, unicode):
			s = unicode(s, 'UTF-8')
	except:
		if not isinstance(s, basestring):
			if hasattr(s, '__unicode__'):
				s = unicode(s)
			else:
				s = unicode(str(s), 'ISO-8859-1')
		elif not isinstance(s, unicode):
			s = unicode(s, 'ISO-8859-1')
	return s

def smart_utf8(s):
	return smart_unicode(s).encode('utf-8')

def replace_signs(text):
	dic = {	'â€™'	: '\'',
			'�'		: '\'',
			'â„¢' 	: '',
			'â€œ'	: '',
			'â€"'	: '-',
			'â€“'	: '-',
			'â€”'	: '-',
			'Â²'	: '²',
			'â€�'	: '"',
			'â€˜N'	: '\'N',
			'Ã¡'	: 'á',
			'Ã©'	: 'é',
			'â€˜'	: '\''}
	for i, j in dic.iteritems():
		text = smart_utf8(text).replace(i, j).strip()
	return text

def refresh_db():
	dialog = xbmcgui.DialogProgress()
	dialog.create(smart_utf8(xbmcaddon.Addon(id = ADDONID).getLocalizedString(39016)))
	total_stations = len(site_dict)
	current = 0
	increment = 100.0 / total_stations
	for network, name in site_dict.iteritems():
		if _addoncompat.get_setting(network) == 'true':
			percent = int(increment * current)
			dialog.update(percent, smart_utf8(xbmcaddon.Addon(id = ADDONID).getLocalizedString(39017)) + name, smart_utf8(xbmcaddon.Addon(id = ADDONID).getLocalizedString(39018)))
			exec 'import %s' % network
			exec 'showdata = %s.masterlist()' % network
			total_shows = len(showdata)
			current_show = 0
			for show in showdata:
				percent = int((increment * current) + (float(current_show) / total_shows) * increment)
				dialog.update(percent, smart_utf8(xbmcaddon.Addon(id = ADDONID).getLocalizedString(39017)) + name, smart_utf8(xbmcaddon.Addon(id = ADDONID).getLocalizedString(39005)) + show[0])
				get_serie(show[0], show[1], show[2], show[3])
				current_show += 1
				if (dialog.iscanceled()):
					return False
		current += 1

def get_serie(series_title, mode, submode, url, forceRefresh = False):
	command = 'select * from shows where series_title = ? and mode = ? and submode = ?;'
	values = (series_title, mode, submode)
	checkdata = _database.execute_command(command, values, fetchone = True)
	if checkdata and not forceRefresh:
		if checkdata[3] is not url:
			command = 'update shows set url = ? where series_title = ? and mode = ? and submode = ?;'
			values = (url, series_title, mode, submode)
			_database.execute_command(command, values, commit = True)
			command = 'select * from shows where series_title = ? and mode = ? and submode = ?;'
			values = (series_title, mode, submode)
			return _database.execute_command(command, values, fetchone = True)
		else:
			return checkdata
	else:
		tvdb_data = get_tvdb_series(series_title, manualSearch = forceRefresh, site = site_dict[mode])
		if tvdb_data:
			tvdb_id, imdb_id, tvdbbanner, tvdbposter, tvdbfanart, first_aired, date, year, actors, genres, network, plot, runtime, rating, airs_dayofweek, airs_time, status, tvdb_series_title = tvdb_data
			values = [series_title, mode, submode, url, tvdb_id, imdb_id, tvdbbanner, tvdbposter, tvdbfanart, first_aired, date, year, actors, genres, network, plot, runtime, rating, airs_dayofweek, airs_time, status, True, False, False, tvdb_series_title]
		else:
			values = [series_title, mode,submode, url, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, True, False, False, series_title]
		command = 'insert or replace into shows values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);'
		_database.execute_command(command, values, commit = True)
		command = 'select * from shows where series_title = ? and mode = ? and submode = ?;'
		values = (series_title, mode, submode)
		return _database.execute_command(command, values, fetchone = True)

def get_series_id(seriesdata, seriesname, site = ''):
	shows = BeautifulSoup(seriesdata).find_all('series')
	for show_item in shows:
		if  '**' in show_item.seriesname.string:
			show_item.clear()
	show_list = []
	if len(shows) > 1:
		ret = -1
		variantsExist = False
		lookup_name = seriesname.replace('%E2%84%A2', '').lower().replace("'", "").replace('?', '').replace('!', '').strip()
		lookup_network = site.replace('The', '').replace(',', '').strip()
		for i, show_item in enumerate(shows):
			item_name = show_item.seriesname.string.lower().replace("'", "").replace('!', '').strip()
			try:
				item_network = show_item.network.string.replace('The', '').replace(',', '').strip()
			except:
				item_network = ''
			if '(' in show_item.seriesname.string and  item_network == lookup_network:
				variantsExist = True
			elif item_name == lookup_name and item_network == lookup_network:
				ret = i
		if  variantsExist == True or ret == -1:
			select = xbmcgui.Dialog()
			for show_item in shows:
				try:
					show_list.append(show_item.seriesname.string + ' [' + show_item.network.string + ']')
				except:
					show_list.append(show_item.seriesname.string)
			if site.endswith(', The'):
				station = 'The ' + site.replace(', The', '')
			ret = select.select(xbmcaddon.Addon(id = ADDONID).getLocalizedString(39020) + seriesname + '\n[' + station.strip() + ']', show_list)
		if ret is not -1:
			seriesid = shows[ret].seriesid.string
	else:
		seriesid = shows[0].seriesid.string
	return seriesid

def get_tvdb_series(seriesname, manualSearch = False, site = ''):
	seriesdata = _connection.getURL(TVDBSERIESLOOKUP + urllib.quote_plus(smart_utf8(seriesname)), connectiontype = 0)
	try:
		tvdb_id = get_series_id(seriesdata, seriesname, site)
	except:
		if manualSearch:
			keyb = xbmc.Keyboard(seriesname, smart_utf8(xbmcaddon.Addon(id = ADDONID).getLocalizedString(39004)))
			keyb.doModal()
			if (keyb.isConfirmed()):
					searchurl = TVDBSERIESLOOKUP + urllib.quote_plus(keyb.getText())
					tvdbid_url = _connection.getURL(searchurl, connectiontype = 0)
					try:
						tvdb_id = get_series_id(tvdbid_url, seriesname)
					except:
						print '_common :: get_tvdb_series :: Manual Search failed'
						return False
		else:
			return False
	series_xml = TVDBURL + ('/api/%s/series/%s/en.xml' % (TVDBAPIKEY, tvdb_id))
	series_xml = _connection.getURL(series_xml, connectiontype = 0)
	series_tree = BeautifulSoup(series_xml).find('series')
	try:
		if smart_unicode(series_tree.firstaired.text) is not '':
			first_aired = smart_unicode(series_tree.firstaired.text)
			date = first_aired
			year = first_aired.split('-')[0]
		else:
			first_aired = None
			date = None
			year = None
	except:
		print '_common :: get_tvdb_series :: %s - Air Date Failed' % seriesname
		first_aired = None
		date = None
		year = None
	try:
		if smart_unicode(series_tree.genre.text) is not '':
			genres = smart_unicode(series_tree.genre.text)
		else:
			genres = None
	except:
		print '_common :: get_tvdb_series :: %s - Genre Failed' % seriesname
		genres = None
	try:
		if smart_unicode(series_tree.overview.text) is not '':
			plot = smart_unicode(series_tree.overview.text)
		else:
			plot = None
	except:
		print '_common :: get_tvdb_series :: %s - Plot Failed' % seriesname
		plot = None
	try:
		if smart_unicode(series_tree.actors.text) is not '':
			actors = smart_unicode(series_tree.actors.text)
		else:
			actors = None
	except:
		print '_common :: get_tvdb_series :: %s - Actors Failed' % seriesname
		actors = None
	try:
		if smart_unicode(series_tree.rating.text) is not '':
			rating = smart_unicode(series_tree.rating.text)
		else:
			rating = None
	except:
		print '_common :: get_tvdb_series :: %s - Rating Failed' % seriesname
		rating = None
	try:
		if smart_unicode(series_tree.banner.text) is not '':
			tvdbbanner = smart_unicode(TVDBBANNERS + series_tree.banner.text)
		else:
			tvdbbanner = None
	except:
		print '_common :: get_tvdb_series :: %s - Banner Failed' % seriesname
		tvdbbanner = None
	try:
		if smart_unicode(series_tree.fanart.text) is not '':
			tvdbfanart = smart_unicode(TVDBBANNERS + series_tree.fanart.text)
		else:
			tvdbfanart = None
	except:
		print '_common :: get_tvdb_series :: %s - Fanart Failed' % seriesname
		tvdbfanart = None
	try:
		if smart_unicode(series_tree.poster.text) is not '':
			tvdbposter = smart_unicode(TVDBBANNERS + series_tree.poster.text)
		else:
			tvdbposter = None
	except:
		print '_common :: get_tvdb_series :: %s - Poster Failed' % seriesname
		tvdbposter = None
	try:
		if smart_unicode(series_tree.imdb_id.text) is not '':
			imdb_id = smart_unicode(series_tree.imdb_id.text)
		else:
			imdb_id = None
	except:
		print '_common :: get_tvdb_series :: %s - IMDB_ID Failed' % seriesname
		imdb_id = None
	try:
		if smart_unicode(series_tree.runtime.text) is not '':
			runtime = smart_unicode(series_tree.runtime.text)
		else:
			runtime = None
	except:
		print '_common :: get_tvdb_series :: %s - Runtime Failed' % seriesname
		runtime = None
	try:
		if smart_unicode(series_tree.airs_dayofweek.text) is not '':
			airs_dayofweek = smart_unicode(series_tree.airs_dayofweek.text)
		else:
			airs_dayofweek = None
	except:
		print '_common :: get_tvdb_series :: %s - Airs_DayOfWeek Failed' % seriesname
		airs_dayofweek = None
	try:
		if smart_unicode(series_tree.airs_time.text) is not '':
			airs_time = smart_unicode(series_tree.airs_time.text)
		else:
			airs_time = None
	except:
		print '_common :: get_tvdb_series :: %s - Airs_Time Failed' % seriesname
		airs_time = None
	try:
		if smart_unicode(series_tree.status.text) is not '':
			status = smart_unicode(series_tree.status.text)
		else:
			status = None
	except:
		print '_common :: get_tvdb_series :: %s - Status Failed' % seriesname
		status = None
	try:
		if smart_unicode(series_tree.network.text) is not '':
			network = smart_unicode(series_tree.network.text)
		else:
			network = None
	except:
		print '_common :: get_tvdb_series :: %s - Network Failed' % seriesname
		network = None
	try:
		if smart_unicode(series_tree.seriesname.text) is not '':
			seriesname = smart_unicode(series_tree.seriesname.text)
		else:
			seriesname = None
	except:
		print '_common :: get_tvdb_series :: %s - TVDB SeriesName Failed' % seriesname
		seriesname = None
	return [tvdb_id, imdb_id, tvdbbanner, tvdbposter, tvdbfanart, first_aired, date, year, actors, genres, network, plot, runtime, rating, airs_dayofweek, airs_time, status, seriesname]

def get_plot_by_tvdbid(tvdb_id):
	command = 'select * from shows where tvdb_id = ?;'
	values = (tvdb_id,)
	showdata = _database.execute_command(command, values, fetchone = True)
	prefixplot = ''
	if showdata:
		series_title, mode, sitemode, url, tvdb_id, imdb_id, tvdbbanner, tvdbposter, tvdbfanart, first_aired, date, year, actors, genres, network, plot, runtime, rating, airs_dayofweek, airs_time, status, has_full_episodes, favor, hide, tvdb_series_title = showdata
		if network is not None:
			prefixplot += smart_utf8(xbmcaddon.Addon(id = ADDONID).getLocalizedString(39013)) + network + '\n'
		if (airs_dayofweek is not None) and (airs_time is not None):
			prefixplot += smart_utf8(xbmcaddon.Addon(id = ADDONID).getLocalizedString(39014)) + airs_dayofweek + '@' + airs_time + '\n'
		if status is not None:
			prefixplot += smart_utf8(xbmcaddon.Addon(id = ADDONID).getLocalizedString(39015)) + status + '\n'
		if prefixplot is not '':
			prefixplot += '\n'
		if plot is not None:
			prefixplot = smart_unicode(prefixplot) + smart_unicode(replace_signs(plot))
	return prefixplot

def get_show_data(series_title, mode = '', sitemode = '', url = ''):
	series_title = replace_signs(smart_unicode(series_title))
	if not os.path.exists(_database.DBFILE):
		_database.create_db()
	_database.check_db_version()
	showdata = get_serie(series_title, mode, sitemode, url, forceRefresh = False)
	return showdata

def load_showlist(favored = 0):
	if not os.path.exists(_database.DBFILE):
		_database.create_db()
		refresh_db()
	else:
		refresh = False
		command = 'select distinct mode from shows order by mode'
		modes = _database.execute_command(command, fetchall = True)
		mode_list = [element[0] for element in modes]
		for network, name in site_dict.iteritems():
			if _addoncompat.get_setting(network) == 'true' and network not in mode_list:
				refresh = True
		if refresh:
			refresh_db()
	_database.check_db_version()
	command = 'select series_title, mode, submode, url, favor, hide from shows order by series_title'
	shows = _database.execute_command(command, fetchall = True) 
	for series_title, mode, sitemode, url, favor, hide in shows:
		if _addoncompat.get_setting(mode) == False:
			continue
		elif hide is 1:
			continue
		elif favored and not favor:
			continue
		add_show(series_title, mode, sitemode, url, favor = favor, hide = hide)	

def add_show(series_title, mode = '', sitemode = '', url = '', favor = 0, hide = 0):
	infoLabels = {}
	tvdbfanart = None
	tvdbbanner = None
	tvdbposter = None
	tvdb_id = None
	thumb = ''
	fanart = ''
	prefixplot = ''
	actors2 = []
	showdata = get_show_data(series_title, mode, sitemode, url)
	series_title, mode, sitemode, url, tvdb_id, imdb_id, tvdbbanner, tvdbposter, tvdbfanart, first_aired, date, year, actors, genres, network, plot, runtime, rating, airs_dayofweek, airs_time, status, has_full_episodes, favor, hide, tvdb_series_title = showdata
	if tvdbfanart is not None:
		fanart = tvdbfanart
	else:
		if args.__dict__.has_key('fanart'):
			fanart = args.fanart
		else:
			fanart = None
	if tvdbbanner is not None:
		thumb = tvdbbanner
	elif tvdbposter is not None:
		thumb = tvdbposter
	else:
		thumb = os.path.join(IMAGEPATH, mode + '.png')
	if tvdb_series_title is not None:
		series_title = smart_utf8(tvdb_series_title)
	infoLabels['title'] = series_title
	infoLabels['tvShowtitle'] = series_title
	if site_dict[mode].endswith(', The'):
		station = 'The ' + site_dict[mode].replace(', The', '')
	else:
		station = site_dict[mode]
	if network is not None:
		if station == network:
			prefixplot += smart_utf8(xbmcaddon.Addon(id = ADDONID).getLocalizedString(39013)) + station + '\n'
		else:
			prefixplot += smart_utf8(xbmcaddon.Addon(id = ADDONID).getLocalizedString(39012)) + network + '\n'
			prefixplot += smart_utf8(xbmcaddon.Addon(id = ADDONID).getLocalizedString(39013)) + station + '\n'
	else:
		prefixplot += smart_utf8(xbmcaddon.Addon(id = ADDONID).getLocalizedString(39013)) + station + '\n'
	if (airs_dayofweek is not None) and (airs_time is not None):
		prefixplot += smart_utf8(xbmcaddon.Addon(id = ADDONID).getLocalizedString(39014)) + airs_dayofweek + '@' + airs_time + '\n'
	elif (airs_dayofweek is not None) and (airs_time is None):
		prefixplot += smart_utf8(xbmcaddon.Addon(id = ADDONID).getLocalizedString(39014)) + airs_dayofweek + '\n'
	elif  (airs_dayofweek is None) and (airs_time is not None):
		prefixplot += smart_utf8(xbmcaddon.Addon(id = ADDONID).getLocalizedString(39014)) + airs_time + '\n'
	else:
		pass
	if status is not None:
		prefixplot += smart_utf8(xbmcaddon.Addon(id = ADDONID).getLocalizedString(39015)) + status + '\n'
	if prefixplot is not None:
		prefixplot += '\n'
	if plot is not None:
		infoLabels['plot'] = smart_utf8(prefixplot) + smart_utf8(replace_signs(plot))
	else:
		infoLabels['plot'] = smart_utf8(prefixplot)
	if date is not None:
		infoLabels['date'] = smart_utf8(date)
	if first_aired is not None: 
		infoLabels['aired'] = smart_utf8(first_aired)
	if year is not None:
		infoLabels['year'] = smart_utf8(year)
	if actors is not None:
		actors = actors.strip('|').split('|')
		if actors[0] is not '':
			for actor in actors:
				actors2.append(smart_utf8(actor))
			infoLabels['cast'] = actors2
	if genres is not None:
		infoLabels['genre'] = smart_utf8(genres.replace('|',',').strip(','))
	if network is not None:
		infoLabels['studio'] = smart_utf8(network)
	if runtime is not None:
		infoLabels['duration'] = smart_utf8(runtime)
	if rating is not None:
		infoLabels['rating'] = smart_utf8(rating)
	name = smart_utf8(replace_signs(series_title))
	series_title = smart_utf8(replace_signs(series_title))
	u = sys.argv[0]
	u += '?url="' + urllib.quote_plus(url) + '"'
	u += '&mode="' + mode + '"'
	u += '&sitemode="' + sitemode + '"'
	u += '&thumb="' + urllib.quote_plus(thumb) + '"'
	if tvdb_id is not None:
		u += '&tvdb_id="' + urllib.quote_plus(tvdb_id) + '"'
	if PLUGINFANART is not fanart:
		u += '&fanart="' + urllib.quote_plus(fanart) + '"'
	if tvdbposter is not None:
		u += '&poster="' + urllib.quote_plus(tvdbposter) + '"'
	u += '&name="' + urllib.quote_plus(series_title) + '"'
	contextmenu = []
	refresh_u = sys.argv[0] + '?url="' + urllib.quote_plus('<join>'.join([series_title, mode, sitemode,url])) + '&mode=_contextmenu' + '&sitemode=refresh_show'
	contextmenu.append((smart_utf8(xbmcaddon.Addon(id = ADDONID).getLocalizedString(39008)), 'XBMC.RunPlugin(%s)' % refresh_u))
	if favor is 1:
		fav_u = sys.argv[0] + '?url="' + urllib.quote_plus('<join>'.join([series_title, mode, sitemode,url])) + '&mode=_contextmenu' + '&sitemode=unfavor_show'
		contextmenu.append((smart_utf8(xbmcaddon.Addon(id = ADDONID).getLocalizedString(39006)), 'XBMC.RunPlugin(%s)' % fav_u))
	else:
		fav_u = sys.argv[0] + '?url="' + urllib.quote_plus('<join>'.join([series_title, mode, sitemode,url])) + '&mode=_contextmenu' + '&sitemode=favor_show'
		contextmenu.append((smart_utf8(xbmcaddon.Addon(id = ADDONID).getLocalizedString(39007)), 'XBMC.RunPlugin(%s)' % fav_u))
	if hide is 1:
		hide_u = sys.argv[0] + '?url="' + urllib.quote_plus('<join>'.join([series_title, mode, sitemode,url])) + '&mode=_contextmenu' + '&sitemode=unhide_show'
		contextmenu.append((smart_utf8(xbmcaddon.Addon(id = ADDONID).getLocalizedString(39009)), 'XBMC.RunPlugin(%s)' % hide_u))
	else: 
		hide_u = sys.argv[0] + '?url="' + urllib.quote_plus('<join>'.join([series_title, mode, sitemode,url])) + '&mode=_contextmenu' + '&sitemode=hide_show'
		contextmenu.append((smart_utf8(xbmcaddon.Addon(id = ADDONID).getLocalizedString(39010)), 'XBMC.RunPlugin(%s)' % hide_u))
	delete_u = sys.argv[0] + '?url="' + urllib.quote_plus('<join>'.join([series_title, mode, sitemode,url])) + '&mode=_contextmenu' + '&sitemode=delete_show'
	contextmenu.append((smart_utf8(xbmcaddon.Addon(id = ADDONID).getLocalizedString(39011)), 'XBMC.RunPlugin(%s)' % delete_u))
	item = xbmcgui.ListItem(name, iconImage = thumb, thumbnailImage = thumb)
	item.addContextMenuItems(contextmenu)
	item.setProperty('fanart_image', fanart)
	item.setInfo(type = 'Video', infoLabels = infoLabels)
	xbmcplugin.addDirectoryItem(pluginHandle, url = u, listitem = item, isFolder = True)

def add_directory(name, mode = '', sitemode = '', directory_url = '', thumb = None, fanart = None, description = None, aired = '', genre = '', count = 0):
	if fanart is None:
		if args.__dict__.has_key('fanart'):
			fanart = args.fanart
		else:
			fanart = PLUGINFANART
	if thumb is None:
		if args.__dict__.has_key('poster'):
			thumb = args.poster
		elif args.__dict__.has_key('thumb'):
			thumb = args.thumb
		else:
			thumb = ''
	if args.__dict__.has_key('name'):
		showname = args.name
	else:
		showname = ''
	if description is None:
		if args.__dict__.has_key('tvdb_id'):
			description = get_plot_by_tvdbid(args.tvdb_id)
		elif site_descriptions.has_key(mode):
			description = site_descriptions[mode]
		else:
			description = ''
	infoLabels = {	'title' : name,
					'tvshowtitle' : showname,
					'genre' : genre,
					'premiered' : aired,
					'plot' : description,
					'count' : count }
	u = sys.argv[0]
	u += '?url="' + urllib.quote_plus(directory_url) + '"'
	u += '&mode="' + mode + '"'
	u += '&sitemode="' + sitemode + '"'
	u += '&thumb="' + urllib.quote_plus(thumb) + '"'
	u += '&fanart="' + urllib.quote_plus(fanart) + '"'
	u += '&name="' + urllib.quote_plus(name) + '"'
	if args.__dict__.has_key('tvdb_id'):
		u += '&tvdb_id="' + urllib.quote_plus(args.tvdb_id) + '"'
	item=xbmcgui.ListItem(name, iconImage = thumb, thumbnailImage = thumb)
	item.setProperty('fanart_image', fanart)
	item.setInfo(type = 'Video', infoLabels = infoLabels)
	contextmenu = []
	refresh_u = sys.argv[0] + '?url="<join>"' + sys.argv[0] + '?url="' + '&mode=_contextmenu' + '&sitemode=refresh_db' 
	contextmenu.append((smart_utf8(xbmcaddon.Addon(id = ADDONID).getLocalizedString(39021)), 'XBMC.RunPlugin(%s)' % refresh_u))
	item.addContextMenuItems(contextmenu)
	xbmcplugin.addDirectoryItem(pluginHandle, url = u, listitem = item, isFolder = True)

def add_video(video_url, displayname, thumb = None, fanart = None, infoLabels = False, HD = False, quality_mode = False):
	displayname = smart_utf8(replace_signs(smart_unicode(displayname)))
	if fanart is None:
		if args.__dict__.has_key('fanart'):
			fanart = args.fanart
		else:
			fanart = PLUGINFANART
	if thumb is None:
		if args.__dict__.has_key('thumb'):
			thumb = args.thumb
		else:
			thumb = ''
	item = xbmcgui.ListItem(displayname, iconImage = thumb, thumbnailImage = thumb)
	item.setInfo(type = 'Video', infoLabels = infoLabels)
	try:
		if 'durationinseconds' in infoLabels.keys():	
			duration = infoLabels['durationinseconds']
		else:
			duration = 0
		if HD is True:
			item.addStreamInfo('video', {'codec' : 'h264', 'width' : 1280, 'height' : 720, 'duration' : duration})
		else:
			item.addStreamInfo('video', {'codec' : 'h264', 'width' : 720, 'height' : 400, 'duration' : duration})
		item.addStreamInfo('audio', {'codec': 'aac', 'channels' : 2})
	except:
		pass
	item.setProperty('fanart_image', fanart)
	item.setProperty('IsPlayable', 'true')
	if quality_mode:
		contextmenu = []
		if 'episode' in infoLabels.keys():	
			episode = infoLabels['episode']
		else:
			episode = -1
		if 'season' in infoLabels.keys():	
			season = infoLabels['season']
		else:
			season = -1
		if 'TVShowTitle' in infoLabels.keys():
			show_title = infoLabels['TVShowTitle']
		else:
			show_title = ''
		quailty_u = sys.argv[0] + '?url='+ urllib.quote_plus('<join>'.join([show_title, str(season), str(episode), thumb, base64.b64encode(displayname), quality_mode, video_url])) +'&mode=_contextmenu' + '&sitemode=select_quality' 
		contextmenu.append((smart_utf8(xbmcaddon.Addon(id = ADDONID).getLocalizedString(39022)), 'XBMC.PlayMedia(%s)' % quailty_u))
		item.addContextMenuItems(contextmenu)
	xbmcplugin.addDirectoryItem(pluginHandle, url = video_url, listitem = item, isFolder = False)
