# -*- coding: utf-8 -*-
from django.conf.urls import url, include

from api.views import ArticleViewSet, AlarmViewSet, login
from rest_framework import routers


router = routers.DefaultRouter()
router.register(r'article', ArticleViewSet)
router.register(r'alarm', AlarmViewSet)

urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^login/$', login, name='login')
]
