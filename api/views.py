# -*- coding: utf-8 -*-
import collections
from collections import OrderedDict
import json
import datetime

from django.contrib.auth import authenticate, login as django_login
from django.db.models import Avg, Min, Max, Q
from django.http import JsonResponse
from django_pandas.io import read_frame
from rest_framework import viewsets, filters
from rest_framework.decorators import list_route
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from joonggo.models import Article, Alarm
from joonggo.serializers import ArticleSerializer, AlarmSerializer


class PaginationClass(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'limit'


class ArticleViewSet(viewsets.ModelViewSet):
    queryset = Article.objects.all().select_related('source')
    serializer_class = ArticleSerializer
    pagination_class = PaginationClass

    info = {}

    # 키워드로 검색하는 경우에 대해서 처리한다.
    @list_route()
    def search(self, request):
        get = request.GET.copy()
        if 'q' in get and get['q'] != '':
            query = get['q']
            # template_data = retrieve_item(query)
            queryset = self.get_queryset()

            # 해당 검색어에 대해 평균가격을 구한다. (1만원 이상에 대해서만)
            # 현재 존재하는 글에 대해서만 구한다. (survival_count == 1)
            # 현재 판매중인 내용에 대해서만 찾는다.
            # queryset = queryset.filter(is_sold_out=False, survival_count__gte=1, price__gte=10000,
            #                            title__icontains=query).order_by('price')

            qs = (Q(is_sold_out=False) & Q(survival_count__gte=1) & Q(price__gte=10000))
            for kw in query.split(' '):
                qs &= Q(title__icontains=kw)
            queryset = queryset.filter(qs).order_by('price')

            # 검색이 된 경우에만 평균가격을 산출하고 진행한다.
            if queryset.count() > 0:
                result = queryset.aggregate(avg_price=Avg('price'))
                avg_price = result['avg_price']

                # 검색결과의 노이즈가 있을 수 있으니
                # 최저가격은 평균가격의 20%보다 작은 것들은 제외하고
                # 최고가격은 평균가격의 3배보다 큰 것들은 제외한다.
                queryset = queryset.filter(price__gte=avg_price * 0.2, price__lt=avg_price * 3)

                # 해당 검색결과에서 최대, 최소 가격을 구한다.
                result = queryset.aggregate(max_price=Max('price'), min_price=Min('price'))
                self.info = result
            else:
                info = None

            page = self.paginate_queryset(queryset)

            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return Response(OrderedDict([
                    ('count', self.paginator.page.paginator.count),
                    ('next', self.paginator.get_next_link()),
                    ('previous', self.paginator.get_previous_link()),
                    ('info', self.info),
                    ('results', serializer.data)
                ]))

            # 그 외의 경우에는 모든 값을 반환한다.
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)

        else:
            template_data = {
                'rsltCd': 'N',
                'rsltNsg': '조회 조건 없음'
            }

        return Response(template_data)

    @list_route()
    def trend(self, request):
        get = request.GET.copy()
        if 'q' in get and get['q'] != '':
            query = get['q']
            return Response(retrieve_item(query))


class AlarmViewSet(viewsets.ModelViewSet):
    queryset = Alarm.objects.all().select_related('profile').order_by('id')
    serializer_class = AlarmSerializer
    pagination_class = PaginationClass
    filter_backends = (filters.DjangoFilterBackend, )
    filter_fields = ('profile', 'id', 'profile__chat', 'profile__user')


def retrieve_item(keyword):
    # 최근 2주일 데이터만 조회
    end_date = datetime.date.today()  # 현재 날짜 가져오기
    period = datetime.timedelta(days=13)
    start_date = end_date - period
    queryset = Article.objects.filter(created__gte=start_date).order_by('-created')
    # queryset = Article.objects.all()
    queryset = queryset.filter(is_sold_out=False, survival_count__gte=1, price__gte=10000, title__icontains=keyword)

    # 판매 글만 조회 도도록 문구 제거
    title_exclude = ['삽니다', '구합니다', '배터리']
    exclude_query = Q(title__icontains=title_exclude[0])
    for t in title_exclude[1:]:
        exclude_query = exclude_query | Q(title__icontains=t)
    queryset = queryset.exclude(exclude_query)

    if queryset.count() > 0:
        df_article_data = read_frame(queryset,
                                     fieldnames=['id', 'uid', 'title', 'price', 'url', 'created', 'source_id'])
        # title 중복 제거
        df_article_data = df_article_data.sort_values('price', ascending=True).drop_duplicates('title')

        # 날짜 형식 변환 및 trend date 생성
        df_article_data['trend_date'] = df_article_data['created'].apply(lambda x: x.strftime('%m-%d'))
        df_article_data['created'] = df_article_data['created'].apply(lambda x: x.strftime('%Y-%m-%d %H:%M:%S'))

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
        # df_article_data = df_article_data.T
        # dict_article_data = df_article_data.to_dict()
        # dict_article_data = collections.OrderedDict(sorted(dict_article_data.items()))
        # dict_article_data = check_key_type(dict_article_data)

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

        content = {
            'rsltCd': 'Y',
            'rsltNsg': u'정상',
            # 'article_data': dict_article_data,    # 중고 물건 목록
            'trend_day': list_avg_date,             # 평균가/최저가 날짜 - List
            'trend_avg_price': list_avg_price,      # 평균가 추세 - List
            'trend_min_price': list_min_price,      # 최저가 추세 - List
            'min_price': min_price,                 # 최저가
            'max_price': max_price                  # 최고가
        }
    else:
        content = {'rsltCd': 'N', 'rsltNsg': u'데이터가 없음'}

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
    return dict


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
