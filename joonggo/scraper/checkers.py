# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from dynamic_scraper.spiders.django_checker import DjangoChecker
from scrapy import Selector

from joonggo.models import Article
from scrapy.http import Request, FormRequest


class ArticleChecker(DjangoChecker):
    name = 'article_checker'

    def __init__(self, *args, **kwargs):
        self._set_ref_object(Article, **kwargs)
        self.scraper = self.ref_object.source.scraper
        self.scrape_url = self.ref_object.url
        self.scheduler_runtime = self.ref_object.checker_runtime

        super(ArticleChecker, self).__init__(self, *args, **kwargs)
