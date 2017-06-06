# -*- coding: utf-8 -*-

from rest_framework import serializers
from joonggo.models import Article, Alarm


class ArticleSerializer(serializers.ModelSerializer):

    class Meta:
        model = Article
        fields = ('id', 'uid', 'title', 'price', 'url', 'created', 'source_id')


class AlarmSerializer(serializers.ModelSerializer):

    class Meta:
        model = Alarm
        fields = '__all__'
