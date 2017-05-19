from django.db.models.signals import post_save
from django.dispatch import receiver
from joonggo.models import Item, Alarm
from joonggobot.joonggobot_main import JoonggoBot

@receiver(post_save, sender = Item)
def create_crawler_item(sender, instance, created, **kwargs):
    if created:
        for alarm in Alarm.objects.all():
            keyword_list = alarm.keyword.split()

            full_contents = instance.title + ' ' + instance.content + ' ' + instance.tags
            if all(keyword in full_contents for keyword in keyword_list):
                send_message = "사용자 게시글 등록 알림\n"
                send_message += "가격 : %s\n" % (instance.price)
                send_message += "제목 : %s\n" % (instance.title)
                send_message += "%s\n" % (instance.url)

                bot = JoonggoBot()
                bot.send_message(alarm.profile.chat, send_message)
            else:
                pass

