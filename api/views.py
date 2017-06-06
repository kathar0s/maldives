# -*- coding: utf-8 -*-
import collections
import json
import datetime

from django.contrib.auth import authenticate, login as django_login
from django.http import JsonResponse
from django_pandas.io import read_frame
from requests import Response
from rest_framework import viewsets, filters
from rest_framework.decorators import list_route
from rest_framework.pagination import PageNumberPagination

from joonggo.models import Article, Alarm
from joonggo.serializers import ArticleSerializer, AlarmSerializer


class PaginationClass(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'limit'


class ArticleViewSet(viewsets.ModelViewSet):
    queryset = Article.objects.all().select_related('source').order_by('price')
    serializer_class = ArticleSerializer
    pagination_class = PaginationClass

    @list_route()
    def search(self, request):
        get = request.GET.copy()
        if 'q' in get:
            query = get['q']
            # template_data = retrieve_item(query)
            results = self.queryset.filter(title__icontains=query, price__gte=10000).order_by('price')

            page = self.paginate_queryset(results)

            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)

            # 그 외의 경우에는 모든 값을 반환한다.
            serializer = self.get_serializer(results, many=True)
            return Response(serializer.data)

        else:
            template_data = {
                'rsltCd': 'N',
                'rsltNsg': '조회 조건 없음'
            }
        return Response(template_data)


class AlarmViewSet(viewsets.ModelViewSet):
    queryset = Alarm.objects.all().select_related('profile').order_by('id')
    serializer_class = AlarmSerializer
    pagination_class = PaginationClass
    filter_backends = (filters.DjangoFilterBackend, )
    filter_fields = ('profile', 'id', 'profile__chat', 'profile__user')


def retrieve_item(item_id):
    # 최근 2주일 데이터만 조회
    end_date = datetime.date.today()  # 현재 날짜 가져오기
    period = datetime.timedelta(days=13)
    start_date = end_date - period
    queryset = Article.objects.filter(created__gte=start_date).order_by('-created')
    queryset = queryset.filter(title__contains=item_id)

    # 판매 글만 조회 도도록 문구 제거
    title_exclude = ['삽니다', '구합니다', '배터리']
    for t in title_exclude:
        queryset = queryset.exclude(title__contains=t)

    if queryset.count() > 0:
        df_article_data = read_frame(queryset,
                                     fieldnames=['id', 'uid', 'title', 'price', 'url', 'created', 'source_id'])
        # title 중복 제거
        df_article_data = df_article_data.sort_values('price', ascending=True).drop_duplicates('title')

        # 날짜 형식 변환 및 trend date 생성
        df_article_data['trend_date'] = df_article_data['created'].apply(lambda x: x.strftime('%m-%d'))
        df_article_data['created'] = df_article_data['created'].apply(lambda x: x.strftime('%Y-%m-%d %hh:%mm:%ss'))

        # 평균값의 20%의 가격으로 최저가 책정/ 평균값의 3배 가격으로 최고가 책정
        avg_price = df_article_data['price'].mean()
        df_article_data = df_article_data[df_article_data['price'] >= avg_price * 0.2]
        df_article_data = df_article_data[df_article_data['price'] < avg_price * 3]
        df_article_data = df_article_data[df_article_data['price'] % 100 == 0]
        df_article_data = df_article_data.reset_index(drop=True)

        # 최저가, 최고가
        min_price = df_article_data['price'].min()
        max_price = df_article_data['price'].max()

        # 일별 최저가, 평균가
        avg_daily = df_article_data.groupby(['trend_date'])['price'].mean()
        min_daily = df_article_data.groupby(['trend_date'])['price'].min()

        # dictionary 변경
        df_article_data = df_article_data.T
        dict_article_data = df_article_data.to_dict()
        dict_article_data = collections.OrderedDict(sorted(dict_article_data.items()))
        dict_article_data = check_key_type(dict_article_data)

        dict_avg_daily = avg_daily.to_dict()
        dict_avg_daily = collections.OrderedDict(sorted(dict_avg_daily.items()))
        dict_min_daily = min_daily.to_dict()
        dict_min_daily = collections.OrderedDict(sorted(dict_min_daily.items()))

        # 그래프를 위한 list 변경
        list_avg_date = list()
        list_avg_price = list()
        list_min_price = list()
        for key in dict_avg_daily.keys():
            list_avg_date.append(key)
            list_avg_price.append(dict_avg_daily[key])
        for key in dict_min_daily.keys():
            list_min_price.append(dict_min_daily[key])

        content = {'rsltCd': 'Y',
                   'rsltNsg': '정상',
                   'article_data': dict_article_data,       # 중고 물건 목록
                   'trend_day': json.dumps(list_avg_date),  # 평균가/최저가 날짜 - List
                   'trend_avg_price': list_avg_price,       # 평균가 추세 - List
                   'trend_min_price': list_min_price,       # 최저가 추세 - List
                   'min_price': min_price,                  # 최저가
                   'max_price': max_price                   # 최고가
                   }
    else:
        content = {'rsltCd': 'N', 'rsltNsg': '데이터가 없음'}

    return content


# dictionary key type을 String으로 변환
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


def login(request):
    if request.method == 'POST':

        username = request.POST.get('id', '')
        password = request.POST.get('password', '')

        user = authenticate(username='bot_{username}'.format(username=username), password=password)
        response_data = {
            'error': True
        }

        if user is not None:
            if user.is_active:
                django_login(request, user)
                response_data['user'] = {
                    'id': user.id,
                    'username': user.username,
                    'profile': {
                        'id': user.chatprofile.id
                    }
                }
                response_data['error'] = False
                response_data['message'] = 'You"re logged in'
            else:
                response_data['message'] = 'Your id is disabled'
        else:
            response_data['message'] = 'You messed up'

        return JsonResponse(response_data)
