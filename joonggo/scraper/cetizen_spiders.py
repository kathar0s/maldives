# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import importlib

from dynamic_scraper.spiders.django_spider import DjangoSpider
from scrapy.http import Request, FormRequest
from dynamic_scraper.utils import processors
from scrapy.loader.processors import Join
from scrapy.loader.processors import TakeFirst

from joonggo.models import Article, ArticleItem, Source
from scrapy import Selector
import json, logging
import scrapy


class CetizenArticleSpider(DjangoSpider):
    name = 'cetizen_article_spider'
    start_urls = [
        'http://market.cetizen.com/market.php?auc_sale=1',
    ]

    def __init__(self, *args, **kwargs):
        self._set_ref_object(Source, **kwargs)
        self.scraper = self.ref_object.scraper
        self.scrape_url = self.ref_object.url
        self.login_page = self.ref_object.login_url
        self.scheduler_runtime = self.ref_object.scraper_runtime
        self.scraped_obj_class = Article
        self.scraped_obj_item_class = ArticleItem

        super(CetizenArticleSpider, self).__init__(self, *args, **kwargs)

    def start_requests(self):
        index = 0
        start_urls = self.start_urls

        print('start_requests')
        for url in start_urls:
            self._set_meta_splash_args()
            kwargs = self.mp_request_kwargs.copy()
            if self.mp_form_data:
                form_data = self.mp_form_data.copy()
            else:
                form_data = None
            if 'headers' in kwargs:
                kwargs['headers'] = json.loads(json.dumps(kwargs['headers']).replace('{page}', str(self.pages[index])))
            if 'body' in kwargs:
                kwargs['body'] = kwargs['body'].replace('{page}', str(self.pages[index]))
            if 'cookies' in kwargs:
                kwargs['cookies'] = json.loads(json.dumps(kwargs['cookies']).replace('{page}', str(self.pages[index])))
            if form_data:
                form_data = json.loads(json.dumps(form_data).replace('{page}', str(self.pages[index])))
            if 'meta' not in kwargs:
                kwargs['meta'] = {}
            kwargs['meta']['page'] = index + 1
            rpt = self.scraper.get_main_page_rpt()
            self.dds_logger.info('')
            self.dds_logger.info(self.bcolors['BOLD'] +
                                 '======================================================================================' +
                                 self.bcolors['ENDC'])
            self.log("{es}{es2}Scraping data from page {page}.{ec}{ec}".format(
                page=index + 1, es=self.bcolors['BOLD'], es2=self.bcolors['HEADER'], ec=self.bcolors['ENDC']),
                logging.INFO)
            self.log("URL: {url}".format(url=url), logging.INFO)
            self.dds_logger.info(self.bcolors['BOLD'] +
                                 '======================================================================================' +
                                 self.bcolors['ENDC'])

            yield Request(url, callback=self.parse, method=rpt.method, dont_filter=rpt.dont_filter, **kwargs)
        print('end start_requests')



    def main_parse(self, response):
        for sel in response.xpath("//span[@class=\"clr100\" or @class=\"clr01\"]/a"):
            link = sel.xpath('@href').extract()[0]
            full_url = u"http://market.cetizen.com" + link


            yield Request(full_url, callback=self.detail_parse)


    def detail_parse(self, response):
        # 고유 아이디, 물품번호
        uid = response.xpath("//div/span[@class=\"p14 clr02 ls-0\"]/text()").re_first(r'물품번호\s*:\s*(\d+)')
        ##날짜
        date = response.xpath("//div/span/span[@class=\"p12 ls-0\"]/text()").re_first(r'\((.*)\)')
        #제목
        title = response.xpath("//div/span[@class=\"p17 clr04\"]/text()").extract_first()
        #가격
        price = response.xpath("//div/span[@class=\"clr03 p21\"]/text()").re_first(r'(.*)').replace(',', '')
        #내용
        content = response.xpath("//div[@class=\"ln24 p14 clr01\"]//text()").extract()
        print(u"%s\n%s\n%s\n%s\n%s\n" % (uid, date, title, price, content))


