# -*- coding: utf-8 -*-
"""maldives URL Configuration
"""

from django.conf.urls import url
from joonggobot import views

urlpatterns = [
    url(r'webhook$', views.webhook, name='webhook'),
    url(r'webhook_polling$', views.webhook_polling, name='webhook_polling'),
]
