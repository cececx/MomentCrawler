#-*- coding: utf-8 -*-
from datetime import datetime
import itertools
import matplotlib.pyplot as plt
import numpy
from operator import itemgetter
import re

from wordcloud import WordCloud, STOPWORDS
import jieba

DATA_PATH = 'output_backup.txt'
DATETIME_PATTERN = '%Y-%m-%d %H:%M'
FONT_PATH = 'data/font.ttf'
STOPWORDS_PATH = 'data/stopwords'
HEIGHT = 800
WIDTH = 400


def load_data(filepath):
  data = []
  with open(filepath, 'r') as f:
    for line in f.readlines():
      line = line.split('\t', 1)
      item = {}
      item['datetime'] = datetime.strptime(line[0].strip(), DATETIME_PATTERN)
      item['content'] = line[1].strip()
      data.append(item)
  return data


def get_stopwords():
  stopwords = STOPWORDS
  with open(STOPWORDS_PATH, 'r') as f:
      for line in f.readlines():
        stopwords.add(line.strip())
  return stopwords


def display_image(img):
  plt.imshow(img, interpolation='bilinear')
  plt.axis('off')
  plt.show()


class MomentCloud:
  def __init__(self, data, stopwords):
    self.data = data
    self.stopwords = stopwords

  def reshard_data_by_year(self):
    for item in self.data:
      item['year'] = item['datetime'].year
    shards = {}
    for key, value in itertools.groupby(self.data, key=itemgetter('year')):
      shards[key] = ' '.join([i.get('content') for i in value])
    return [shards[key] for key in sorted(shards)]

  def get_image(self, shards):
    args = {
      'font_path': FONT_PATH,
      'stopwords': self.stopwords,
      'max_words': 1000,
      'max_font_size': 200,
      'width': WIDTH,
      'height': HEIGHT
    }
    pic = numpy.zeros((HEIGHT, WIDTH*len(shards), 3), dtype=numpy.uint8)
    for i in range(len(shards)):
      wc = WordCloud(**args).generate(shards[i]).to_array()
      pic[0:HEIGHT, WIDTH*i:WIDTH*(i+1)] = wc
    return pic


if __name__ == '__main__':
  moment_cloud = MomentCloud(load_data(DATA_PATH), get_stopwords())
  display_image(moment_cloud.get_image(moment_cloud.reshard_data_by_year()))

