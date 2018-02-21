#! /usr/lib/python  
#-*- coding: utf-8 -*-  

import cookielib
import json
import re
import requests
import sys
import urllib
import urllib2

from datetime import datetime
from bs4 import BeautifulSoup

DATETIME_INPUT_PATTERN = '%Y年%m月%d日 %H:%M\xc2\xa0'
DATETIME_OUTPUT_PATTERN = '%Y-%m-%d %H:%M'


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
      self.cookie_proc = urllib2.HTTPCookieProcessor(self.cookie)
    except:
      raise
    else:
      opener = urllib2.build_opener(self.cookie_proc)
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

  def get_status(self):
    # Get status url.
    url = 'http://3g.renren.com/profile.do'
    data = {'id':str(self.id), 'sid':self.sid}
    request = urllib2.Request(url, urllib.urlencode(data))
    profile = BeautifulSoup(urllib2.urlopen(request).read(), 'html.parser')
    url = profile.select('.sec')[3].find_all('a')[3]['href']
    
    # Get total page count.
    request = urllib2.Request(url)
    status_page = BeautifulSoup(urllib2.urlopen(request).read(), 'html.parser')
    page_content = str(status_page.select('.gray')[0].contents)
    total_page = int(re.findall(r"(?<=/)\d+(?=[^\d])", page_content)[0])

    # Iterate pages.
    current_page = 1
    while current_page <= total_page:
      status_list = status_page.select('.list')[0].find_all('div')
      for status in status_list:
        if status.select('.time'):
          if not status.select('.forward'):
            obj = {}
            time_str = str(status.select(".time")[0].string).strip()
            time = datetime.strptime(time_str, DATETIME_INPUT_PATTERN)
            obj['datetime'] = time.strftime(DATETIME_OUTPUT_PATTERN)
            obj['content'] = (status.a.next_element).strip()
            self.status.append(obj)
            print obj['datetime']
            print obj['content'].encode('utf-8')
            print ''
      current_page += 1
      if current_page > total_page:
        break

      # Get the next page.
      url = str(status_page.select(".l")[0].a['href'])
      req = urllib2.Request(url)
      status_page = BeautifulSoup(urllib2.urlopen(req).read(), 'html.parser')

  def write_json(self, filepath):
    with open(filepath, 'w') as file:
      json.dump(self.status, file, sort_keys=True, indent=2)

  def write_txt(self, filepath):
    with open(filepath, 'w') as file:
      lines = ["{}\t{}\n".format(a['datetime'], a['content']) for a in self.status]
      file.writelines(lines)

  def write_csv(self, filepath):
    pass


if __name__ == '__main__':
  email = raw_input("Input account/email: ")
  password = raw_input("Input password: ")
  reload(sys)
  sys.setdefaultencoding('utf-8')
  crawler = RenrenCrawler(email, password)
  if crawler.login():
    crawler.get_status()
    print "Writing result to output.txt..."
    crawler.write_txt('output.txt')
 
