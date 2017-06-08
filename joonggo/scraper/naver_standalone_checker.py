# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from dynamic_scraper.spiders.django_spider import DjangoSpider
from scrapy.http import Request
from joonggo.models import Article, ArticleItem, Source
from django.db.models import Q
from scrapy.http import Request, FormRequest
from scrapy import Selector


class NaverStandaloneChecker(DjangoSpider):
    name = 'naver_standalone_checker'
    start_urls = [
        'https://nid.naver.com/nidlogin.login',
    ]

    def __init__(self, *args, **kwargs):
        self._set_ref_object(Source, **kwargs)
        self.scraper = self.ref_object.scraper
        self.scrape_url = self.ref_object.url
        self.login_page = self.ref_object.login_url
        self.scheduler_runtime = self.ref_object.scraper_runtime
        self.scraped_obj_class = Article
        self.scraped_obj_item_class = ArticleItem

        super(NaverStandaloneChecker, self).__init__(self, *args, **kwargs)


    def start_requests(self):
        print(u'start_requests start')
        yield Request(url=self.login_page, callback=self.login, dont_filter=True)
        print(u'start_requests ends')


    def request_next_url(self):
        articles = Article.objects.filter(Q(source=self.ref_object) & Q(survival_count=1)).order_by("id")[:1]

        if len(articles) > 0:
            article = articles[0]
            #print(u"checking : %d %s %s %s\n" % (article.id, article.title, article.uid, article.url))
            return Request(article.url, callback=self.detail_parse, meta={'article': article})
        else:
            print(u"checking ended!\n")
            return None


    def detail_parse(self, response):

        article = response.meta['article']
        error_content = response.xpath("//div[@class=\"error_content_body\"]/h2/text()").extract_first()
        if error_content is None:
            article.survival_count += 1
            print("content is valid!, keep going\n")
        else:
            article.survival_count = 0
            article.is_sold_out = True
            print("content was removed : %s\n" % (error_content))
        article.save()

        yield self.request_next_url()


    def login(self, response):
        print('naver standalone checker login try')
        login_data = {'id': 'sep521', 'pw': 'sep521sep521'}

        return FormRequest.from_response(response,
                                         formdata=login_data,
                                         callback=self.check_login_response)

    def check_login_response(self, response):
        print('naver standalone checker response check')
        selector = Selector(response)
        error_element = selector.xpath('//div[@id="err_common"]')

        # 에러가 없으면 로그인이 성공하였다는 말이므로..
        if len(error_element) == 0:
            print('login success!!')
            yield self.request_next_url()
        else:
            print('login failed, abort checking!!')

