# -*- coding: utf-8 -*-

from rest_framework import serializers
from joonggo.models import Article, Alarm

class ArticleSerializer(serializers.ModelSerializer):

    class Meta:
        model = Article
        fields = ('id','uid', 'title','price','url', 'created', 'source_id')
        #fields = '__all__'

class AlarmSerializer(serializers.ModelSerializer):

    class Meta:
        model = Alarm
        #fields = ('id','title','content','price','created')
        fields = '__all__'
