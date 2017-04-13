# -*- coding: utf-8 -*-
from django.shortcuts import render

from rest_framework import viewsets
from rest_framework.decorators import list_route

from joonggo.models import Item
from joonggo.serializers import ItemSerializer


class ItemViewSet(viewsets.ModelViewSet):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer

    @list_route()
    def search(self, request):
        pass

    @list_route()
    def top(self, request):
        pass
