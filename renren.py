#-*- coding: utf-8 -*-  
""" Renren status crawler.

Example:
    $ python3 renren.py

Todo:
  * Move ``get_soup`` function to a separate ``util`` module.
  * Replace debug information ``print`` with ``logger``.
  * Add python3 version check.

"""

from datetime import datetime
import json
import re
import sys
import urllib

from http.cookiejar import CookieJar
from bs4 import BeautifulSoup

DATETIME_INPUT_PATTERN = '%Y年%m月%d日 %H:%M'
DATETIME_OUTPUT_PATTERN = '%Y-%m-%d %H:%M'
MAX_PAGE = -1


def get_soup(url, data=None):
  encoded_data = urllib.parse.urlencode(data).encode("utf-8") if data else None
  request = urllib.request.Request(url, encoded_data)
  response = urllib.request.urlopen(request).read()
  soup = BeautifulSoup(response, 'html.parser')
  return soup


class RenrenCrawler:
  def __init__(self, email, password):
    self.email = email
    self.password = password
    self.domain = 'renren.com'
    self.id = ''
    self.sid = ''
    self.status = []
    try:
      self.cookie = CookieJar()
      self.cookie_proc = urllib.request.HTTPCookieProcessor(self.cookie)
    except:
      raise
    else:
      opener = urllib.request.build_opener(self.cookie_proc)
      urllib.request.install_opener(opener)

  def login(self):
    url='http://3g.renren.com/login.do'
    data = {'email':self.email, 'password':self.password}

    try:
      index = get_soup(url, data)
      href = str(index.select('.cur')[0].parent.contents[2]['href'])
      # Get user id.
      self.id = re.findall(r"\d{6,}", href)[0]
      # Get user sid.
      self.sid = re.findall(r"(?<=sid=).*?(?=&)", href)[0]
      return True
    except Exception as err:
      print('Login failed: ', err)
      return False

  def get_status(self, max_page=-1):
    # Get status url.
    url = 'http://3g.renren.com/profile.do'
    data = {'id':str(self.id), 'sid':self.sid}
    profile_soup = get_soup(url, data)
    url = profile_soup.select('.sec')[3].find_all('a')[3]['href']
    
    # Get total page count.
    status_soup = get_soup(url)
    page_content = str(status_soup.select('.gray')[0].contents)
    total_page = int(re.findall(r"(?<=/)\d+(?=[^\d])", page_content)[0])

    if max_page < total_page and max_page > 0:
      total_page = max_page

    # Iterate pages.
    current_page = 1
    while current_page <= total_page:
      print('Loading page:', current_page)
      status_list = status_soup.select('.list')[0].find_all('div')
      for status in status_list:
        if status.select('.time'):
          if not status.select('.forward'):
            obj = {}
            time_str = str(status.select(".time")[0].string).strip()
            time = datetime.strptime(time_str, DATETIME_INPUT_PATTERN)
            obj['datetime'] = time.strftime(DATETIME_OUTPUT_PATTERN)
            obj['content'] = (status.a.next_element).strip()
            self.status.append(obj)
            # print(obj['datetime'], '\t', obj['content'], '\n')
      current_page += 1
      if current_page > total_page:
        break

      # Get the next page.
      url = str(status_soup.select(".l")[0].a['href'])
      status_soup = get_soup(url)

  def write_json(self, filepath):
    with open(filepath, 'w') as file:
      json.dump(self.status, file, sort_keys=True, indent=2)

  def write_txt(self, filepath):
    with open(filepath, 'w') as file:
      for status in self.status:
        file.write('{}\t{}\n'.format(status['datetime'], status['content']))


if __name__ == '__main__':
  email = input("Input account/email: ")
  password = input("Input password: ")
  crawler = RenrenCrawler(email, password)
  if crawler.login():
    print('Login successful')
    crawler.get_status(MAX_PAGE)
    print('Writing result to output.txt...')
    crawler.write_txt('output.txt')
    print('Finished.')
 