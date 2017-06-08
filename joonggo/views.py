# -*- coding: utf-8 -*-
from django.http import HttpResponse
from django.shortcuts import render, render_to_response
from joonggo.models import Article, Source


def index(request):

    counter = {
        'joonggonara': Article.objects.filter(source__name='중고나라').count(),
        'momsholic': Article.objects.filter(source__name='맘스홀릭').count(),
        'cetizen': Article.objects.filter(source__name='세티즌').count()
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
    get = request.GET.copy()

    if 'token' in get:
        html_file = 'sell.html'
        source = Source.objects.all()
        template_data = {'source': source}
    else:
        html_file = 'naverlogin.html'
        template_data = {}
    return render(request, html_file,  template_data)


def callback(request):
    template_data = {}
    return render(request, 'callback.html', template_data)
