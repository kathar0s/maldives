# -*- coding: utf-8 -*-

#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Simple Bot to reply to Telegram messages
# This program is dedicated to the public domain under the CC0 license.
"""
This Bot uses the Updater class to handle the bot.
First, a few handler functions are defined. Then, those functions are passed to
the Dispatcher and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.
Usage:
Basic Echobot example, repeats messages.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""

import json
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import logging
import requests


# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

def sendToJoonggodives(message):
    url = 'http://52.78.186.61//joonggobot/webhook_polling'
    headers = {'Content-Type': 'application/json; charset=utf-8'}
    cookies = {'webhook_id': 'test'}
    response = requests.post(url, data=json.dumps(message), headers=headers, cookies=cookies)

def start(bot, update):
    sendToJoonggodives({'type' : "start", 'id' : update.message.chat_id, 'text' : update.message.text})

def stop(bot, update):
    sendToJoonggodives({'type' : "stop", 'id' : update.message.chat_id, 'text' : update.message.text})

def help(bot, update):
    sendToJoonggodives({'type': "help", 'id': update.message.chat_id, 'text': update.message.text})

def search(bot, update):
    sendToJoonggodives({'type': "search", 'id': update.message.chat_id, 'text': update.message.text})

def add_alarm(bot, update):
    sendToJoonggodives({'type': "register_alarm", 'id': update.message.chat_id, 'text': update.message.text})

def list_alarm(bot, update):
    sendToJoonggodives({'type': "list_alarm", 'id': update.message.chat_id, 'text': update.message.text})

def remove_alarm(bot, update):
    sendToJoonggodives({'type': "remove_alarm", 'id': update.message.chat_id, 'text': update.message.text})

def error(bot, update, error):
    logger.warn('Update "%s" caused error "%s"' % (update, error))


def main():
    # Create the EventHandler and pass it your bot's token.
    updater = Updater('369457948:AAG0fIhoWTVEp4h38DG-bAkY0lDuDe7YNpc')

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("stop", stop))
    dp.add_handler(CommandHandler("도움말", help))

    dp.add_handler(CommandHandler("알림등록", add_alarm))
    dp.add_handler(CommandHandler("알림목록", list_alarm))
    dp.add_handler(CommandHandler("알림삭제", remove_alarm))
    dp.add_handler(MessageHandler(Filters.text, search))

    # on noncommand i.e message - echo the message on Telegram
    #dp.add_handler(MessageHandler(Filters.text, echo))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()

if __name__ == '__main__':
    main()
