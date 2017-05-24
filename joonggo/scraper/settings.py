# -*- coding: utf-8 -*-
import os
import sys

PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "maldives.settings.production")     # Changed in DDS v.0.3
# sys.path.insert(0, os.path.join(PROJECT_ROOT, "../../.."))  # only for example_project

BOT_NAME = 'maldives'

SPIDER_MODULES = ['dynamic_scraper.spiders', 'joonggo.scraper']
USER_AGENT = '%s/%s' % (BOT_NAME, '1.0')

# Scrapy 0.20+
ITEM_PIPELINES = {
    'dynamic_scraper.pipelines.DjangoImagesPipeline': 200,
    'dynamic_scraper.pipelines.ValidationPipeline': 400,
    'joonggo.scraper.pipelines.DjangoWriterPipeline': 800,
}


IMAGES_STORE = os.path.join(PROJECT_ROOT, '../static/thumbnails')

IMAGES_THUMBS = {
    'medium': (50, 50),
    'small': (25, 25),
}

DSCRAPER_IMAGES_STORE_FORMAT = 'ALL'

DSCRAPER_LOG_ENABLED = True
DSCRAPER_LOG_LEVEL = 'ERROR'
DSCRAPER_LOG_LIMIT = 5
