#! /usr/lib/python  
#-*- coding: utf-8 -*-  

import cookielib
import re
import requests
import sys
import urllib
import urllib2

from datetime import datetime
from bs4 import BeautifulSoup


class RenrenCrawler:
	def __init__(self, email, password):
		self.email = email
		self.password = password
		self.domain = 'renren.com'
		self.id = ''
		self.sid = ''
		self.status = []
		try:
			self.cookie = cookielib.CookieJar()
			self.cookieProc = urllib2.HTTPCookieProcessor(self.cookie)
		except:
			raise
		else:
			opener = urllib2.build_opener(self.cookieProc)
			urllib2.install_opener(opener)

	def login(self):
		url='http://3g.renren.com/login.do'
		data = {'email':self.email, 'password':self.password}
		request = urllib2.Request(url, urllib.urlencode(data))

		try:
			index = BeautifulSoup(urllib2.urlopen(request).read(), 'html.parser')
			href = str(index.select('.cur')[0].parent.contents[2]['href'])
			# Get user id.
			self.id = re.findall(r"\d{6,}", href)[0]
			# Get user sid.
			self.sid = re.findall(r"(?<=sid=).*?(?=&)", href)[0]
			return True

		except Exception, e:
			print 'Login failed: ', e.message
			return False

	def getStatus(self):
		datetimePattern = '%Y年%m月%d日 %H:%M\xc2\xa0'
		# Get status url.
		url = 'http://3g.renren.com/profile.do'
		data = {'id':str(self.id), 'sid':self.sid}
		request = urllib2.Request(url, urllib.urlencode(data))
		profile = BeautifulSoup(urllib2.urlopen(request).read(), 'html.parser')
		url = profile.select('.sec')[3].find_all('a')[3]['href']
		
		# Get total page count.
		request = urllib2.Request(url)
		statusPage = BeautifulSoup(urllib2.urlopen(request).read(), 'html.parser')
		pageContent = str(statusPage.select('.gray')[0].contents)
		page = int(re.findall(r"(?<=/)\d+(?=[^\d])", pageContent)[0])
		page = 3

		# Iterate pages.
		i = 1
		while i <= page:
			print "Loading page " + str(i)
			statusList = statusPage.select('.list')[0].find_all('div')
			for status in statusList:
				if status.select('.time'):
					if not status.select('.forward'):
						item = {}
						time = str(status.select(".time")[0].string).strip()
						item['datetime'] = datetime.strptime(time, datetimePattern)
						item['content'] = (status.a.next_element).strip()
						self.status.append(item)
						print item['datetime'].strftime('%Y-%m-%d %H:%M')
						print item['content'].encode('utf-8')
						print ''
			i += 1
			if i > page:
				break
			# Get the next page.
			url = str(statusPage.select(".l")[0].a['href'])
			req = urllib2.Request(url)
			statusPage = BeautifulSoup(urllib2.urlopen(req).read(), 'html.parser')

	def WriteJson(self, output):
		pass

	def WriteText(self, output):
		pass

	def WriteCSV(self, output):
		pass

if __name__ == '__main__':
	email = raw_input("Input account/email: ")
	password = raw_input("Input password: ")
	reload(sys)
	sys.setdefaultencoding('utf-8')
	crawler = RenrenCrawler(email, password)
	if crawler.login():
		crawler.getStatus()
