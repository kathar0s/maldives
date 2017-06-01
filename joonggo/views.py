# -*- coding: utf-8 -*-
import datetime
from time import strftime, strptime
from pandas import json
from django.db.models import Avg
from django_pandas.io import read_frame
from django.http import HttpResponse
from django.shortcuts import render
from rest_framework.decorators import list_route
from rest_framework.generics import GenericAPIView
from rest_framework import serializers, mixins
from rest_framework import viewsets
from joonggo.models import Article, Alarm
from joonggo.serializers import ArticleSerializer, AlarmSerializer, TrendSerializer
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
import pandas as pd
import numpy as np

# Create your views here.
def index(request):
    return HttpResponse('Hello Maldives!')

class PaginationClass(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'limit'

class ArticleViewSet(viewsets.ModelViewSet):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
    pagination_class = PaginationClass

    def get_queryset(self):
        queryset = Article.objects.all()
        item_id = self.request.query_params.get('item_id', None)
        if item_id is not None:
            queryset = queryset.filter(title__contains=item_id)
        return queryset

class AlarmViewSet(viewsets.ModelViewSet):
    queryset = Alarm.objects.all()
    serializer_class = AlarmSerializer
    pagination_class = PaginationClass

class TrendViewSet(viewsets.ModelViewSet):
    queryset = Article.objects.all()
    serializer_class = TrendSerializer

    #@list_route()
    def list(self, request):
        end_date = datetime.date.today()  # 현재 날짜 가져오기
        period = datetime.timedelta(days=14)
        start_date = end_date - period
        queryset = Article.objects.filter(created__range=(start_date, end_date)).order_by('-created')
        get = request.GET.copy()
        print(get)
        if 'item_id' in get:
            queryset = queryset.filter(title__contains=get['item_id']).exclude(title__contains='삽니다')
            queryset = queryset.filter(price__gte=10000)
            df = read_frame(queryset, fieldnames=['title', 'price', 'created'])
            df['trend_date'] = df['created'].apply(lambda x:x.strftime('%Y-%m-%d'))
            if len(queryset) > 0 :
                avg = df.groupby(['trend_date'])['price'].mean()
                min = df.groupby(['trend_date'])['price'].min()
                trend_avg= avg.to_dict()
                trend_min =min.to_dict()
                print(json.dumps(trend_avg))
                print(json.dumps(trend_min))
                content = {'rsltCd': 'Y',
                           'rsltNsg' : len(avg),
                           'trend_avg' : trend_avg,
                           'trend_min' : trend_min}
            else:
                content = {'rsltCd': 'N', 'rsltNsg' : 'item_id가 없음'}
        else:
            content = {'rsltCd': 'N', 'rsltNsg' : 'item_id가 없음'}
        return Response(content)

