# -*- coding: utf-8 -*-
from django.http import HttpResponse
from django.shortcuts import render
from rest_framework.decorators import list_route
from rest_framework.generics import GenericAPIView
from rest_framework import serializers, mixins
from rest_framework import viewsets
from joonggo.models import Article, Alarm
from joonggo.serializers import ArticleSerializer, AlarmSerializer
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

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
