# -*- coding: utf-8 -*-
import datetime
from time import strftime, strptime
from pandas import json
from django.db.models import Avg
from django_pandas.io import read_frame
from django.http import HttpResponse
from django.shortcuts import render
from django.shortcuts import render, render_to_response
from rest_framework.decorators import list_route
from rest_framework.generics import GenericAPIView
from rest_framework import serializers, mixins
from rest_framework import viewsets
from joonggo.models import Article, Alarm, ChatProfile
from joonggo.serializers import ArticleSerializer, AlarmSerializer, TrendSerializer
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
import pandas as pd
import numpy as np

# Create your views here.
def index(request):

    counter = {
        'joonggonara': Article.objects.filter(source__name='중고나라').count()
    }

    template_data = {
        'counter': counter
    }

    return render(request, 'index.html', template_data)


def search(request):
    template_data = {}
    return render(request, 'search.html', template_data)


def alarm(request):
    template_data = {}
    return render(request, 'alarm.html', template_data)


def sell(request):
    template_data = {}
    return render(request, 'sell.html', template_data)


def write(request):
    if request.session.get('naverTokenId') is None:
        print('naverTokenId : None')
        return render_to_response('write_test.html')
    else:
        return HttpResponse('글쓰기로 이동!!')


def getNaverLoginResult(request):
    prin("1111")
    return HttpResponse('Testing!!!')

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

    def get_queryset(self):
        chatting_id = self.request.query_params.get('chatting_id', None)
        print(chatting_id)
        if chatting_id is not None:
            qs = ChatProfile.objects.filter(chat=chatting_id)
            print(qs)
            #queryset = Alarm.objects.filter(profile=)
        return qs

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

