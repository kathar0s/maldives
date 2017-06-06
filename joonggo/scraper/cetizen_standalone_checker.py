# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from dynamic_scraper.spiders.django_spider import DjangoSpider
from scrapy.http import Request
from joonggo.models import Article, ArticleItem, Source
from django.db.models import Q
import time


class CetizenStandaloneChecker(DjangoSpider):
    name = 'cetizen_standalone_checker'
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
        self.check_article_ids = Article.objects.filter(
            Q(source=self.ref_object) & Q(survival_count=1)).order_by("id").values_list("id", flat=True)
        self.check_current_index = 0

        super(CetizenStandaloneChecker, self).__init__(self, *args, **kwargs)

    def request_next_url(self):
        #article = Article.objects.get(id=self.check_article_ids[self.check_current_index])
        articles = Article.objects.filter(Q(source=self.ref_object) & Q(survival_count=1)).order_by("id")[:10]

        article = articles[0]
        print(u"checking : %d %s %s %s\n" % (article.id, article.title, article.uid, article.url))
        self.check_current_index += 1
        return Request(article.url, callback=self.detail_parse, meta={'article': article})


    def start_requests(self):
        print(u'start_requests start')
        yield self.request_next_url()
        print(u'start_requests ends')


    def detail_parse(self, response):
        # 고유 아이디, 물품번호
        uid = response.xpath("//div/span[@class=\"p14 clr02 ls-0\"]/text()").re_first(r'물품번호\s*:\s*(\d+)')

        article = response.meta['article']
        print(u"title : %s, uid : %s" % (article.title, article.uid))
        print(u"response url : %s," % (response.url))
        if uid is None or uid not in article.uid:
            print(u"%s, %s mismatch\n%s" % (article.uid, uid, article.url))
            article.survival_count = 0
        else:
            print(u"%s, %s match\n%s" % (article.uid, uid, article.url))
            article.survival_count += 1
        article.save()

        yield self.request_next_url()




