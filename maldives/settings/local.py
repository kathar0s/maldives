# -*- coding: utf-8 -*-
from maldives.settings.production import *

DEBUG = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'maldives',
        'USER': 'maldives',
        'PASSWORD': 'sep521',
        'HOST': '52.78.186.61',
        'PORT': '',
    }
}

ALLOWED_HOSTS = ['*']

