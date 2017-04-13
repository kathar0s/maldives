# -*- coding: utf-8 -*-
from maldives.settings.production import *

DEBUG = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'maldives',
        'USER': 'maldives',
        'PASSWORD': 'havefun2mrow',
        'HOST': '',
        'PORT': '',
    }
}
