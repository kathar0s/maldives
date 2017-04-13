# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from collections import OrderedDict

from dateutil.relativedelta import relativedelta
from filer.models import File
import ast
from rest_framework import serializers
from rest_framework.fields import SkipField

from admin_haezoom.admincore.models import Sales, Issues
from lease.apps.house.forms import CustomerForm
from lease.apps.installer.models import Installer
from models import Customer
from django.utils import timezone
from datetime import datetime
from haezoom.core.utils import logger, get_post_for_file, send_template_sms, template_notify

from joonggo.models import Item


class ItemSerializer(serializers.ModelSerializer):

    class Meta:
        model = Item
        fields = '__all__'
