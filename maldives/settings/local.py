# -*- coding: utf-8 -*-
from maldives.settings.production import *

DEBUG = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'maldives',
        'USER': 'maldives',
        'PASSWORD': 'sep521',
        'HOST': '52.198.6.89',
        'PORT': '',
    }
}

ALLOWED_HOSTS = ['*']

