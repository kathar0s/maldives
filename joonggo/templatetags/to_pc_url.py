# -*- coding: utf-8 -*-
from django import template
import re

register = template.Library()


@register.filter
def to_pc_url(value):
    return value.replace("/m.", "/")


@register.filter
def covert_to_write(value):
    ids = re.findall(r'clubid=(\d*).*menuid=(\d*)', value)

    # clubid와 menuid를 찾은 경우
    if len(ids) > 0:
        clubid, menuid = ids[0]
        return u'http://m.cafe.naver.com/ArticleWrite.nhn?clubid={clubid}&menuid={menuid}&m=write'.format(
            clubid=clubid, menuid=menuid
        )
    else:
        return value

