# -*- coding: utf-8 -*-
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage


def paginate_list(request, object_list):
    if 'p' in request.GET:
        page = request.GET['p']
    else:
        page = 1

    per_page = 40
    page_per_section = 5  # 한번에 몇개의 페이지를 출력할 것인가?

    paginator = Paginator(object_list, per_page)

    try:
        page_objects = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        page = 1
        page_objects = paginator.page(page)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        page_objects = paginator.page(paginator.num_pages)

    page = int(page)

    # 페이지 섹션 구하기
    start_page_section_num = int((page - 1) / page_per_section) * page_per_section + 1

    page_objects.previous_page_section = start_page_section_num - page_per_section
    if page_objects.previous_page_section < 0:
        page_objects.previous_page_section = 0
        page_objects.has_previous_section = False
    else:
        page_objects.has_previous_section = True

    page_objects.next_page_section = start_page_section_num + page_per_section
    if page_objects.next_page_section >= page_objects.paginator.num_pages:
        page_objects.next_page_section = page_objects.paginator.num_pages + 1
        page_objects.has_next_section = False
    else:
        page_objects.has_next_section = True

    page_objects.page_range = range(start_page_section_num, page_objects.next_page_section)

    return page_objects
