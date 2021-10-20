import requests
import json
import redis
import os
from datetime import datetime
from db import db_add_pnldata, db_add_bids

USERPOOL = redis.ConnectionPool(
	host='localhost', port=6379, db=0, decode_responses=True)
rclient = redis.StrictRedis(connection_pool=USERPOOL, decode_responses=True)

BOT_TOKEN = os.getenv('BO_TELEGRAM_BOT_TOKEN')
CHAT_ID = os.getenv('BO_TELEGRAM_CHAT_ID')

def sendThreadedText(bot_token, bot_chatID, bot_message):
    send_text = 'https://api.telegram.org/bot' + bot_token + \
        '/sendMessage?chat_id=' + bot_chatID + '&parse_mode=Markdown&text='+bot_message
    requests.get(send_text)

fixtures = rclient.get('check_fixtures')

if(fixtures == None):
    # print('No Fixtues')
    ENV = os.getenv('ENV')
    if(ENV == 'prod'):
        MESSAGE = 'Error: Not receiving Fixture Data on Prod'
    else:
        MESSAGE = 'Error: Not receiving Fixture Data on Dev'

    sendThreadedText(BOT_TOKEN, CHAT_ID, MESSAGE)