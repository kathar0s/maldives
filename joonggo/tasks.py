# -*- coding: utf-8 -*-
from celery.task import task
from dynamic_scraper.utils.task_utils import TaskUtils
from joonggo.models import Source, Article


@task()
def run_spiders():
    t = TaskUtils()

    t.run_spiders(Source, 'scraper', 'scraper_runtime', 'article_spider')
    t.run_spiders(Source, 'scraper', 'scraper_runtime', 'cetizen_article_spider')


@task()
def run_checkers():
    t = TaskUtils()

    t.run_checkers(Article, 'source__scraper', 'checker_runtime', 'article_checker')
