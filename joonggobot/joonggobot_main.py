# -*- coding: utf-8 -*-

#!/usr/bin/env python
from django_pandas.io import read_frame

from joonggo.models import ChatProfile, Article, Alarm, Source
from django.contrib.auth.models import User
from django.db.models import Q
from functools import reduce
import operator
import telegram
import sys
import datetime
import re

class JoonggoBot:
    WEBHOOK_URL = 'http://52.78.186.61/joonggobot/webhook_polling'
    TELEGRAM_TOKEN = '373562267:AAGVYqG7JFud4tCePUdq-Bkd-Y6-dZsP568'

    @staticmethod
    def get_token():
        return JoonggoBot.TELEGRAM_TOKEN

    @staticmethod
    def get_webhookurl():
        return JoonggoBot.WEBHOOK_URL

    def get_chat_profile(self, id):
        try:
            profile = ChatProfile.objects.get(chat=id)
        except ChatProfile.DoesNotExist:
            profile = None
        return profile

    def __init__(self):
        reload(sys)
        sys.setdefaultencoding('utf-8')
        self.token =  JoonggoBot.TELEGRAM_TOKEN
        self.telegram_bot = telegram.Bot(JoonggoBot.TELEGRAM_TOKEN)
        self.handler = {'start' : self.handle_start,
                        'stop': self.handle_stop,
                        'help': self.handle_help,
                        'search': self.handle_search,
                        'register_alarm': self.handle_add_alarm,
                        'list_alarm': self.handle_list_alarm,
                        'remove_alarm': self.handle_remove_alarm,}

    def handle_start(self, id, message):

        profile = self.get_chat_profile(id)
        if profile is None:
            name = u"bot_%s" % (id)
            user = User.objects.create_user(name, "", "")
            user.profile = ChatProfile.objects.create(user=user, chat=id)
            user.save()

        send_message = u"환영합니다.\n웹에서 알림 등록 시 아래 토큰을 활용해주세요\n%d" % (id)
        self.send_message(id, send_message)

    def handle_stop(self, id, message):
        send_message = u"봇과의 연결을 종료합니다"
        profile = self.get_chat_profile(id)
        if profile is not None:
            profile.user.delete()
            profile.delete()

        self.send_message(id, send_message)

    def handle_help(self, id, message):
        send_message = u"지원 명령어 모음\n\n종고 물품 키워드 검색\n/알림등록 키워드\n/알림보기\n/알림삭제 키워드"
        self.send_message(id, send_message)

    def handle_add_alarm(self, id, message):
        keyword = message.split(u"/알림등록")[1]

        profile = self.get_chat_profile(id)
        if profile is not None:
            alarm = Alarm.objects.create(profile=profile, keyword=keyword)
            alarm.save()
            send_message = u"%d 토큰에 알림을 등록하였습니다\n키워드=%s" % (id, keyword)
        else:
            send_message = u"%d 토큰의 사용자 정보가 존재하지 않습니다\n다시 봇을 시작해주세요" % (id)

        self.send_message(id, send_message)

    def handle_list_alarm(self, id, message):

        profile = self.get_chat_profile(id)
        if profile is None:
            send_message = u"%d 토큰의 사용자 정보가 존재하지 않습니다\n다시 봇을 시작해주세요" % (id)
        else:
            alarms = Alarm.objects.filter(profile=profile)
            send_message = u"알림등록 목록(%d) = %d 개\n\n" % (id, len(alarms))
            for alarm in alarms:
                send_message += u"등록 키워드 : %s\n" % (alarm.keyword)
                send_message += u"가격 기준 : %s\n\n" % (alarm.price)

        self.send_message(id, send_message)

    def handle_remove_alarm(self, id, message):

        profile = self.get_chat_profile(id)
        if profile is None:
            send_message = u"%d 토큰의 사용자 정보가 존재하지 않습니다\n다시 봇을 시작해주세요" % (id)
        else:
            keyword = message.split(u"/알림삭제")
            if len(keyword) < 2:
                Alarm.objects.filter(profile=profile).delete()
                send_message = u"%d 토큰의 모든 알림을 삭제하였습니다" % (id)
            else:
                Alarm.objects.filter(profile=profile, keyword=keyword[1]).delete()
                send_message = u"%d 토큰의 \"%s\" 알림을 삭제하였습니다" % (id, keyword[1])

        self.send_message(id, send_message)


    def handle_search(self, id, message):
        end_date = datetime.date.today()  # 현재 날짜 가져오기
        period = datetime.timedelta(days=13)
        start_date = end_date - period
        queryset = Article.objects.filter(created__gte=start_date).order_by('-created')
        queryset = queryset.filter(title__contains=message)
        title_exclude = ['삽니다', '구합니다', '배터리']
        for t in title_exclude:
            queryset = queryset.exclude(title__contains=t)
        if (queryset.count() > 0):
            article_data = read_frame(queryset,
                                      fieldnames=['title', 'price', 'url', 'created', 'source_id', 'uid'])
            # title 중복 제거
            article_data = article_data.sort_values('price', ascending=True).drop_duplicates('title')

            # 평균값의 20%의 가격으로 최저가 책정/ 평균값의 3배 가격으로 최고가 책정
            avg = article_data['price'].mean()
            article_data = article_data[article_data['price'] >= avg * 0.2]
            article_data = article_data[article_data['price'] < avg * 3]
            article_data = article_data.reset_index(drop=True)
            item_list = article_data[:10]
            query_result = u"검색 결과 = %d 개\n\n" % (len(item_list))
            for index, row in item_list.iterrows():
                query_result += u"가격 : %s\n" % (row['price'])
                query_result += u"날짜 : %s\n" % (row['created']).split('.')[0]
                query_result += u"제목 : %s\n" % (row['title'])

                default_url = u"%s\n\n" % (row['url'])
                words = re.search(r"\[(\w+)\]", row['source_id'])
                if words:
                    source = Source.objects.filter(name=words.group(0)).first()
                    if source is not None:
                        default_url = u"%s%s\n" % (source.source.mobile_base_url, row['uid'])
                query_result += default_url

        self.send_message(id, query_result)



    def send_message(self, id, message):
        self.telegram_bot.sendMessage(id, message)

    def handle(self, id, type, message):
        if type in self.handler:
            self.handler[type](id, message)
        else:
            print("handler error")
