# -*- coding: utf-8 -*-
from django.db.models.signals import post_save
from django.dispatch import receiver
from joonggo.models import Article, Alarm
from joonggobot.joonggobot_main import JoonggoBot


@receiver(post_save, sender=Article)
def create_crawler_item(sender, instance, created, **kwargs):
    if created:
        for alarm in Alarm.objects.all():
            keyword_list = alarm.keyword.split()

            full_contents = instance.title + ' ' + instance.content + ' ' + instance.tags
            if all(keyword in full_contents for keyword in keyword_list):
                send_message = u"사용자 게시글 등록 알림\n"
                send_message += u"가격 : %s\n" % (instance.price)
                send_message += u"제목 : %s\n" % (' '.join(instance.title.split()))
                send_message += u"%s%s\n" % (instance.source.mobile_base_url, instance.uid)

                bot = JoonggoBot()
                bot.send_message(alarm.profile.chat, send_message)
            else:
                pass

