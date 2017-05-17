import json
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
import telegram


# Create your views here.

@api_view(['POST'])
@csrf_exempt
def webhook(request):
    return HttpResponse('Hello Maldives bot, webhook!')


# Create your views here.

@api_view(['POST'])
@csrf_exempt
def webhook_polling(request):
    if request.method == 'POST':
        data = request.data
        bot = telegram.Bot(token='369457948:AAG0fIhoWTVEp4h38DG-bAkY0lDuDe7YNpc')
        bot.sendMessage(340859851, json.dumps(data, ensure_ascii=False))
        return HttpResponse(json.dumps(data), content_type='application/json')
    else:
        return HttpResponse('Hello Maldives bot, webhook!')