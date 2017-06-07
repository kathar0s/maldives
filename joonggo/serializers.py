# -*- coding: utf-8 -*-

from rest_framework import serializers
from joonggo.models import Article, Alarm


class ArticleSerializer(serializers.ModelSerializer):
    
    source = serializers.SerializerMethodField(read_only=True)
    
    def get_source(self, obj):
        return obj.source.name
    
    class Meta:
        model = Article
        fields = ('id', 'uid', 'title', 'price', 'url', 'created', 'source', 'source_id')


class AlarmSerializer(serializers.ModelSerializer):

    class Meta:
        model = Alarm
        fields = '__all__'
