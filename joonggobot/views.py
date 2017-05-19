import json
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from joonggobot.joonggobot_main import JoonggoBot
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
        bot = JoonggoBot()
        bot.handle(request.data['id'], request.data['type'], request.data['text'])
        return HttpResponse(json.dumps(request.data), content_type='application/json')
    else:
        return HttpResponse('Hello Maldives bot, webhook!')