# -*- coding: utf-8 -*-
from django.http import HttpResponse
from django.shortcuts import render, render_to_response
from joonggo.models import Article


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
    get = request.GET.copy()

    template_data = {}

    if 'q' in get:
        pass
        # # 해당 검색어에 해당하는 글을 읽어온다, 판매중인 것들중에서만 내용을 찾는다.
        # articles = Article.objects.filter(title__icontains=get['q'], is_sold_out=False)
        #
        # # 해당 목록에서 평균가를 구한다.
        # article_data = articles.aggregate(avg_price=Avg('price'))
        #
        # if not article_data['avg_price']:
        #     avg_price = 0
        # else:
        #     avg_price = float(article_data['avg_price'])
        #
        # # 해당 평균가보다 20%낮은 가격이나, 3배 높은 가격은 제외한다.
        # articles = articles.filter(price__gte=avg_price*0.2,
        #                            price__lt=avg_price*3).order_by('price')
        #
        # # 그 중에서 최저가와 최고가를 구한다.
        # articles_data = articles.aggregate(max_price=Max('price'), min_price=Min('price'))
        # article_list = paginate_list(request, articles)
        #
        # template_data = {
        #     'articles_top10': articles[:10],
        #     'articles': articles,
        #     'max_price': articles_data['max_price'],
        #     'min_price': articles_data['min_price']
        # }

        # item_id = get['q']
        # template_data = retrieve_item(item_id)
    # else:
        # template_data = {'rsltCd': 'N',
        #                  'rsltNsg': '조회 조건 없음'
        #                  }

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
