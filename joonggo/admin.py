# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib import admin
from reversion.admin import VersionAdmin
from joonggo.models import Source, Article


class SourceAdmin(VersionAdmin):
    list_display = ('name', 'category', 'url_')
    ordering = ('-id',)

    def url_(self, instance):
        return '<a href="{url}" target="_blank">{title}</a>'.format(
            url=instance.url, title=instance.url)
    url_.allow_tags = True
admin.site.register(Source, SourceAdmin)


class ArticleAdmin(VersionAdmin):
    list_display = ('title', 'price', 'url_', 'created')
    ordering = ('-id', )

    def url_(self, instance):
        return '<a href="{url}" target="_blank">{title}</a>'.format(
            url=instance.url, title=instance.url)
    url_.allow_tags = True
admin.site.register(Article, ArticleAdmin)
