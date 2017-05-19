# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import User
from django.conf import settings


# 중고 물건 내용
class Item(models.Model):

    # 필수 항목
    uid = models.CharField('고유번호', max_length=20, default='', unique=True, db_index=True,
                           help_text='고유번호를 말함')

    title = models.CharField('제목', db_index=True, max_length=50, default='')
    content = models.TextField('내용', default='')
    price = models.PositiveIntegerField('가격', default=0)
    site = models.CharField('사이트', db_index=True, max_length=20, default='', )
    url = models.CharField('링크', max_length=150, default='', help_text='해당 글 주소')

    # 옵션 항목
    tags = models.TextField('태그', default='', blank=True, help_text='콤마로 구분')

    is_include_parcel = models.BooleanField('택배포함여부', default=False, blank=True)
    is_sold_out = models.BooleanField('판매여부', default=False, blank=True)

    created = models.DateTimeField('등록일', auto_now_add=True)

    @property
    def search(self, keyword):
        pass

    class Meta:
        verbose_name = '물건'
        verbose_name_plural = '물건 목록'


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

