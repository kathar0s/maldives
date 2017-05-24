# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models
from django.contrib.auth.models import User
from dynamic_scraper.models import Scraper, SchedulerRuntime
from scrapy_djangoitem import DjangoItem
from django.db.models.signals import pre_delete
from django.dispatch import receiver
from django.conf import settings


class Source(models.Model):
    name = models.CharField('이름', max_length=20, default='')
    category = models.CharField('카테고리', max_length=20, default='', blank=True)
    url = models.URLField('URL')
    login_url = models.URLField('Login URL', blank=True, default='')
    scraper = models.ForeignKey(Scraper, blank=True, null=True, on_delete=models.SET_NULL)
    scraper_runtime = models.ForeignKey(SchedulerRuntime, blank=True, null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return '[{name}] {category}'.format(name=self.name, category=self.category)

    class Meta:
        verbose_name = '출처'
        verbose_name_plural = '출처 목록'


# 중고 물건 내용
class Article(models.Model):

    source = models.ForeignKey(Source, verbose_name='출처')

    # 필수 항목
    uid = models.CharField('고유번호', max_length=20, default='', unique=True, db_index=True,
                           help_text='고유번호를 말함')

    title = models.CharField('제목', db_index=True, max_length=200, default='')
    content = models.TextField('내용', default='', blank=True)
    price = models.PositiveIntegerField('가격', default=0, blank=True)
    url = models.URLField('링크', default='', blank=True, help_text='해당 글 주소')

    # 옵션 항목
    tags = models.TextField('태그', default='', blank=True, help_text='콤마로 구분')

    is_include_parcel = models.BooleanField('택배포함여부', default=False, blank=True)
    is_sold_out = models.BooleanField('판매여부', default=False, blank=True)

    created = models.DateTimeField('등록일', auto_now_add=True)

    checker_runtime = models.ForeignKey(SchedulerRuntime, blank=True, null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return '[{source}] {title}'.format(source=self.source, title=self.title)

    class Meta:
        verbose_name = '게시물'
        verbose_name_plural = '게시물 목록'


class ArticleItem(DjangoItem):
    django_model = Article


@receiver(pre_delete)
def pre_delete_handler(sender, instance, using, **kwargs):
    if isinstance(instance, Source):
        if instance.scraper_runtime:
            instance.scraper_runtime.delete()

    if isinstance(instance, Article):
        if instance.checker_runtime:
            instance.checker_runtime.delete()


pre_delete.connect(pre_delete_handler)


# 봇에서 시작한 사용자 Profile
class ChatProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    chat = models.PositiveIntegerField('채팅 아이디', default=0)


# 사용자별 / ID별 알림 내용
class Alarm(models.Model):
    profile = models.ForeignKey(ChatProfile, on_delete=models.CASCADE, default=None, null=True, blank=True, verbose_name='로그인')

    keyword = models.CharField('키워드', max_length=50, default='')
    price = models.PositiveIntegerField('가격', default=0)

    created = models.DateTimeField('등록일', auto_now_add=True)

    class Meta:
        verbose_name = '알림'
        verbose_name_plural = '알림 목록'


# 사용자들이 검색한 키워드들을 모아보고 싶은 용도
class SearchKeyword(models.Model):
    keyword = models.CharField('키워드', db_index=True, max_length=50, default='')

    created = models.DateTimeField('등록일', auto_now_add=True)

    class Meta:
        verbose_name = '검색 키워드'
        verbose_name_plural = '검색 키워드 목록'

