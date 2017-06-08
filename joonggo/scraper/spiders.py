# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import importlib

from dynamic_scraper.spiders.django_spider import DjangoSpider
from scrapy.http import Request, FormRequest
from dynamic_scraper.utils import processors
from scrapy.loader.processors import Join

from joonggo.models import Article, ArticleItem, Source
from scrapy.utils.spider import iterate_spider_output
from scrapy import Selector
import json, logging


class ArticleSpider(DjangoSpider):
    name = 'article_spider'

    def __init__(self, *args, **kwargs):
        self._set_ref_object(Source, **kwargs)
        self.scraper = self.ref_object.scraper
        self.scrape_url = self.ref_object.url
        self.login_page = self.ref_object.login_url
        self.scheduler_runtime = self.ref_object.scraper_runtime
        self.scraped_obj_class = Article
        self.scraped_obj_item_class = ArticleItem

        super(ArticleSpider, self).__init__(self, *args, **kwargs)

    def start_requests(self):
        index = 0
        start_urls = ['https://nid.naver.com/nidlogin.login'] + self.start_urls

        print('start_requests')
        for url in start_urls:
            if index == 0 and 'login' in url:
                yield Request(
                    url=self.login_page,
                    callback=self.login,
                    dont_filter=True
                )
                continue

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

            print('end start_requests')

            index += 1
            if rpt.request_type == 'R':
                yield Request(url, callback=self.parse, method=rpt.method, dont_filter=rpt.dont_filter, **kwargs)
            else:
                yield FormRequest(url, callback=self.parse, method=rpt.method, formdata=form_data,
                                  dont_filter=rpt.dont_filter, **kwargs)

    def login(self, response):
        print('login try')

        login_data = {'id': 'sep521', 'pw': 'sep521sep521'}

        return FormRequest.from_response(response,
                                         formdata=login_data,
                                         callback=self.check_login_response)

    def check_login_response(self, response):
        print('check_login_response')
        selector = Selector(response)
        error_element = selector.xpath('//div[@id="err_common"]')

        # 에러가 없으면 로그인이 성공하였다는 말이므로..
        if len(error_element) == 0:
            self.log('Login sucesss!')
        else:
            self.log("Login fail")

    def _get_processors(self, procs_str):
        procs = [Join(), processors.string_strip, ]
        if not procs_str:
            return procs
        procs_tmp = list(procs_str.split(','))
        for p in procs_tmp:
            p = p.strip()
            added = False
            if hasattr(processors, p):
                procs.append(getattr(processors, p))
                added = True
            for cp_path in self.conf['CUSTOM_PROCESSORS']:
                try:
                    custom_processors = importlib.import_module(cp_path)
                    if hasattr(custom_processors, p):
                        procs.append(getattr(custom_processors, p))
                        added = True
                except ImportError:
                    pass
            if not added:
                self.log("Processor '{p}' is not defined!".format(p=p), logging.ERROR)
        procs = tuple(procs)
        return procs
