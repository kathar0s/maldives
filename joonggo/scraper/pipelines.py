# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from builtins import str
from builtins import object
import logging
import re
from django.db.utils import IntegrityError
from scrapy.exceptions import DropItem
from dynamic_scraper.models import SchedulerRuntime


class DjangoWriterPipeline(object):

    def process_item(self, item, spider):
        if spider.conf['DO_ACTION']:
            try:
                item['source'] = spider.ref_object

                checker_rt = SchedulerRuntime(runtime_type='C')
                checker_rt.save()
                item['checker_runtime'] = checker_rt
                item['price'] = self.adjust_price(item, spider)

                item.save()
                spider.action_successful = True
                dds_id_str = str(item._dds_item_page) + '-' + str(item._dds_item_id)
                spider.log("{cs}Item {id} saved to Django DB.{ce}".format(
                    id=dds_id_str,
                    cs=spider.bcolors['OK'],
                    ce=spider.bcolors['ENDC']), logging.INFO)

            except IntegrityError as e:
                spider.log(str(e), logging.ERROR)
                raise DropItem("Missing attribute.")

        return item


    def adjust_price(self, item, spider):
        price_candidate = []
        price_search = [item['title'], item['content']]
        for target in price_search:
            price_candidate += re.findall('(\d+[원|만원]+)', target.replace(',', ''))

        price = item['price']
        if len(price_candidate) > 0:
            price = price_candidate[0].replace('만', '0000').replace('원', '')
            if price != item['price']:
                spider.log("price mismatch, {content_price} != {crawl_price}".format(
                    content_price=price, crawl_price=item['price']), logging.ERROR)

        return price
