# -*- coding: utf-8 -*-
from urllib.request import urlopen
import scrapy


class Crawler(object):
    url = ''
    html = ''
    rating = None
    categories = None

    def __init__(self, url=""):
        self.url = url
        self.rating = dict()
        self.categories = ['종합', '지역별', '연령별', '성별']

        # url이 존재하는 경우에는 html을 먼저 읽어온다.
        if self.url != "":
            self.get_html()

    def get_html(self):
        f = urlopen(self.url)
        self.html = f.read()
        f.close()
        return self.html

    def set_url(self, url):
        self.url = url

    def get_url(self):
        return self.url

    def get_json(self):
        pass