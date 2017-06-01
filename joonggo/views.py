# -*- coding: utf-8 -*-
from django.http import HttpResponse
from django.shortcuts import render
from rest_framework import viewsets
from joonggo.models import Article, Alarm
from joonggo.serializers import ArticleSerializer, AlarmSerializer
from rest_framework.pagination import PageNumberPagination


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
