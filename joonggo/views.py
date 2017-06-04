# -*- coding: utf-8 -*-
import datetime
from django_pandas.io import read_frame
from django.http import HttpResponse
from django.shortcuts import render
from django.shortcuts import render, render_to_response
from rest_framework.decorators import list_route
from rest_framework import viewsets
from joonggo.models import Article, Alarm, ChatProfile
from joonggo.serializers import ArticleSerializer, AlarmSerializer
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
import collections

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
    return HttpResponse('Testing!!!')

class PaginationClass(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'limit'

class ArticleViewSet(viewsets.ModelViewSet):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
    pagination_class = PaginationClass

    @list_route()
    def retrieve_item(self, request):
        #최근 2주일 데이터만 조회
        end_date = datetime.date.today()  # 현재 날짜 가져오기
        period = datetime.timedelta(days=13)
        start_date = end_date - period
        queryset = Article.objects.filter(created__gte=start_date).order_by('-created')
        get = request.GET.copy()
        if 'item_id' in get:
            queryset = queryset.filter(title__contains=get['item_id'])
            title_exclude = ['삽니다', '구합니다', '배터리']
            for t in title_exclude:
                queryset = queryset.exclude(title__contains=t)
            if(queryset.count() > 0):
                article_data = read_frame(queryset,
                                          fieldnames=['id','uid', 'title','price','url', 'created', 'source_id'])
                #title 중복 제거
                article_data = article_data.sort_values('price', ascending=True).drop_duplicates('title')

                #날짜 형식 변환 및 trend date 생성
                article_data['trend_date'] = article_data['created'].apply(lambda x: x.strftime('%Y-%m-%d'))
                article_data['created'] = article_data['created'].apply(lambda x: x.strftime('%Y-%m-%d %hh:%mm:%ss'))

                #평균값의 20%의 가격으로 최저가 책정/ 평균값의 3배 가격으로 최고가 책정
                avg = article_data['price'].mean()
                article_data = article_data[article_data['price'] >= avg*0.2]
                article_data = article_data[article_data['price'] < avg * 3]
                article_data = article_data.reset_index(drop=True)

                # 일별 최저가, 평균가
                avg = article_data.groupby(['trend_date'])['price'].mean()
                min = article_data.groupby(['trend_date'])['price'].min()

                #dictionary 변경
                article_data = article_data.T
                dict_article_data = article_data.to_dict('list')
                dict_article_data = collections.OrderedDict(sorted(dict_article_data.items()))
                dict_article_data = check_key_type(dict_article_data)
                dict_trend_avg = avg.to_dict()
                dict_trend_min = min.to_dict()
                dict_trend_avg = collections.OrderedDict(sorted(dict_trend_avg.items()))
                dict_trend_min = collections.OrderedDict(sorted(dict_trend_min.items()))

                content = {'rsltCd': 'Y',
                           'rsltNsg': '정상',
                           'article_data': dict_article_data,
                           'trend_avg' : dict_trend_avg,
                           'trend_min' : dict_trend_min
                           }

            else:
                content = {'rsltCd': 'N', 'rsltNsg': '데이터가 없음'}
        else:
            content = {'rsltCd': 'N', 'rsltNsg': 'item_id가 없음'}
            
        return Response(content)

    ##사용 안할 예정..
    @list_route()
    def trend(self, request):
        end_date = datetime.date.today()  # 현재 날짜 가져오기
        period = datetime.timedelta(days=13)
        start_date = end_date - period
        queryset = Article.objects.filter(created__gte=start_date).order_by('-created')
        get = request.GET.copy()
        if 'item_id' in get:
            queryset = queryset.filter(title__contains=get['item_id'])
            title_exclude = ['삽니다', '구합니다', '배터리']
            for t in title_exclude:
                queryset = queryset.exclude(title__contains=t)
            if queryset.count() > 0:
                trend_data = read_frame(queryset, fieldnames=['title', 'price', 'created'])
                trend_data['trend_date'] = trend_data['created'].apply(lambda x:x.strftime('%Y-%m-%d'))
                
                # title 중복 제거
                trend_data = trend_data.sort_values('price', ascending=True).drop_duplicates('title')
                trend_data = trend_data.reset_index(drop=True)
                # 평균값의 20%의 가격으로 최저가 책정/ 평균값의 3배 가격으로 최고가 책정
                avg_all = trend_data['price'].mean()
                trend_data = trend_data[trend_data['price'] >= avg_all * 0.2]
                trend_data = trend_data[trend_data['price'] < avg_all * 3]
                #일별 최저가, 평균가
                avg = trend_data.groupby(['trend_date'])['price'].mean()
                min = trend_data.groupby(['trend_date'])['price'].min()
                dict_trend_avg= avg.to_dict()
                dict_trend_min =min.to_dict()
                dict_trend_avg = collections.OrderedDict(sorted(dict_trend_avg.items()))
                dict_trend_min = collections.OrderedDict(sorted(dict_trend_min.items()))

                content = {'rsltCd': 'Y',
                           'rsltNsg' : '정상',
                           'count' : len(avg),
                           'trend_avg' : dict_trend_avg,
                           'trend_min' : dict_trend_min}
            else:
                content = {'rsltCd': 'N', 'rsltNsg' : '데이터가 없음'}
        else:
            content = {'rsltCd': 'N', 'rsltNsg' : 'item_id가 없음'}
        return Response(content)


class AlarmViewSet(viewsets.ModelViewSet):
    queryset = Alarm.objects.all()
    serializer_class = AlarmSerializer
    pagination_class = PaginationClass

    @list_route()
    def retrieve_alarm(self, request):
        queryset = ChatProfile.objects.all()
        get = request.GET.copy()
        if 'chat_id' in get:
            queryset = queryset.filter(chat=get['chat_id'])
            if queryset.count() > 0 :
                df = read_frame(queryset, fieldnames=['id', 'chat', 'user'])
                id = df.ix[0]['id']
                print(id)
                qs = Alarm.objects.filter(profile=id)
                alarm_data = read_frame(qs, fieldnames=['id', 'keyword', 'price', 'created'])
                alarm_data['created'] = alarm_data['created'].apply(lambda x: x.strftime('%Y-%m-%d %hh:%mm:%ss'))
                alarm_data = alarm_data.T
                dict_alarm_data = alarm_data.to_dict()
                dict_alarm_data = check_key_type(dict_alarm_data)
                content = {'rsltCd': 'Y', 'rsltNsg': '정상', 'alarmData': dict_alarm_data }
            else:
                content = {'rsltCd': 'N', 'rsltNsg': '사용자 아이디가 없음'}

        return Response(content)

#dictionary key type을 String으로 변환
def check_key_type(dict):
    for key in dict.keys():
        if type(key) is not str:
            try:
                dict[str(key)] = dict[key]
            except:
                try:
                    dict[repr(key)] = dict[key]
                except:
                    pass
            del dict[key]
    return  dict