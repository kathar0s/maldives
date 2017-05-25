# -*- coding: utf-8 -*-
#!/usr/bin/env python

from joonggo.models import ChatProfile, Article, Alarm
from django.contrib.auth.models import User
from django.db.models import Q
from functools import reduce
import operator
import telegram

class JoonggoBot:
    WEBHOOK_URL = 'http://52.78.186.61/joonggobot/webhook_polling'
    TELEGRAM_TOKEN = '369457948:AAG0fIhoWTVEp4h38DG-bAkY0lDuDe7YNpc'

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
        self.token =  JoonggoBot.TELEGRAM_TOKEN
        self.telegram_bot = telegram.Bot(JoonggoBot.TELEGRAM_TOKEN)
        self.handler = {'시작하기' : self.handle_start,
                        '종료하기': self.handle_stop,
                        '도움말': self.handle_help,
                        '검색하기': self.handle_search,
                        '알림등록': self.handle_add_alarm,
                        '알림보기': self.handle_list_alarm,
                        '알림삭제': self.handle_remove_alarm,}

    def handle_start(self, id, message):

        profile = self.get_chat_profile(id)
        if profile is None:
            name = "bot_%s" % (id)
            user = User.objects.create_user(name, "", "")
            user.profile = ChatProfile.objects.create(user=user, chat=id)
            user.save()

        send_message = "환영합니다.\n웹에서 알림 등록 시 아래 토큰을 활용해주세요\n%d" % (id)
        self.send_message(id, send_message)

    def handle_stop(self, id, message):
        send_message = "봇과의 연결을 종료합니다"
        profile = self.get_chat_profile(id)
        if profile is not None:
            profile.user.delete()
            profile.delete()

        self.send_message(id, send_message)

    def handle_help(self, id, message):
        send_message = "지원 명령어 모음\n\n종고 물품 키워드 검색\n/알림등록 키워드\n/알림보기\n/알림삭제 키워드"
        self.send_message(id, send_message)

    def handle_add_alarm(self, id, message):
        keyword = message.split("/알림등록")[1]

        profile = self.get_chat_profile(id)
        if profile is not None:
            alarm = Alarm.objects.create(profile=profile, keyword=keyword)
            alarm.save()
            send_message = "%d 토큰에 알림을 등록하였습니다\n키워드=%s" % (id, keyword)
        else:
            send_message = "%d 토큰의 사용자 정보가 존재하지 않습니다\n다시 봇을 시작해주세요" % (id)

        self.send_message(id, send_message)

    def handle_list_alarm(self, id, message):

        profile = self.get_chat_profile(id)
        if profile is None:
            send_message = "%d 토큰의 사용자 정보가 존재하지 않습니다\n다시 봇을 시작해주세요" % (id)
        else:
            alarms = Alarm.objects.filter(profile=profile)
            send_message = "알림등록 목록(%d) = %d 개\n\n" % (id, len(alarms))
            for alarm in alarms:
                send_message += "등록 키워드 : %s\n" % (alarm.keyword)
                send_message += "가격 기준 : %s\n\n" % (alarm.price)

        self.send_message(id, send_message)

    def handle_remove_alarm(self, id, message):

        profile = self.get_chat_profile(id)
        if profile is None:
            send_message = "%d 토큰의 사용자 정보가 존재하지 않습니다\n다시 봇을 시작해주세요" % (id)
        else:
            keyword = message.split("/알림삭제")
            if len(keyword) < 2:
                Alarm.objects.filter(profile=profile).delete()
                send_message = "%d 토큰의 모든 알림을 삭제하였습니다" % (id)
            else:
                Alarm.objects.filter(profile=profile, keyword=keyword[1]).delete()
                send_message = "%d 토큰의 \"%s\" 알림을 삭제하였습니다" % (id, keyword[1])

        self.send_message(id, send_message)


    def handle_search(self, id, message):
        keyword_list = message.split()
        query = reduce(operator.and_, (Q(title__contains=item) | Q(content__contains=item) | Q(tags__contains=item)\
                     for item in keyword_list))
        item_list = Article.objects.filter(query).order_by('created')[:10]

        query_result = "검색 결과 = %d 개\n\n" % (len(item_list))
        for item in item_list:
            query_result += "가격 : %s\n" % (item.price)
            query_result += "제목 : %s\n" % (item.title)
            query_result += "%s\n\n" % (item.url)

        self.send_message(id, query_result)


    def send_message(self, id, message):
        self.telegram_bot.sendMessage(id, message)

    def handle(self, id, type, message):
        if type in self.handler:
            self.handler[type](id, message)
