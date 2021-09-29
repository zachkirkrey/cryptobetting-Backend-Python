from datetime import datetime, timedelta
import json
import math
import asyncio
import requests
import redis
import os
import ast
from db import db_get_ended_fixture, db_get_fixture, db_set_fixture_status, db_set_fixture_price, db_get_fixture_end_price
import uuid
import hashlib
import logging
from logging.handlers import TimedRotatingFileHandler
import time

USERPOOL = redis.ConnectionPool(
    host='localhost', port=6379, db=0, decode_responses=True)
rclient = redis.StrictRedis(connection_pool=USERPOOL, decode_responses=True)

logger = logging.getLogger("Rotating Log")
logger.setLevel(logging.INFO)

handler = TimedRotatingFileHandler('./owapi1.log',
                                   when="d",
                                   interval=7,
                                   backupCount=3)
logger.addHandler(handler)

def getBinancePrice(endTimestamp):
    try:
        res = requests.get(
            "https://api3.binance.com/api/v3/klines?symbol=BTCUSDT&interval=1m&endTime="+str(endTimestamp)+"&limit=1")
        print(res.json())
        return float(res.json()[0][1])
    except Exception as e:
        print(e)
        print("Sleeping for 5s ....")
        time.sleep(5)
        return 0


print("Sleeping for 2s ....")
time.sleep(2)

CURR_TIME = datetime.now()

FIXTURE_TIME = CURR_TIME - timedelta(minutes=10)
print(FIXTURE_TIME)

fixtures = db_get_ended_fixture(CURR_TIME)
print(type(fixtures))
print(fixtures)
if(fixtures != None):
    fixtures = json.loads(fixtures)
    for fixture in fixtures:
        print(fixture)
        print(fixture['marketEndTime'])
        print(type(fixture['marketEndTime']))
        print(fixture['id'])
        print(fixture['status'])

        fixtureEnded = rclient.get('fixtureEnded')
        print(fixtureEnded)
        if (fixtureEnded):
            fixtureId = ast.literal_eval(fixtureEnded)
        else:
            fixtureId = None

        if(fixtureId == None or fixtureId != fixture['id']):
            print('CALL END FIXTURE API AND COMMUNICATE THE RESULT')
            print(fixture['id'])

            res = {}

            seq = str(uuid.uuid4())
            print(seq)

            price = 0
            # resdisdata = rclient.get('BTC_PRICE')
            # if (resdisdata):
            #     price = ast.literal_eval(resdisdata)
            
            price = getBinancePrice(fixture['marketEndTime'])
            print("BTCUSDT Prcie: ", price)

            if(price > 0):
                res['Timestamp'] = (datetime.now() + timedelta(hours=8)).strftime('%Y/%m/%d %H:%M:%S.%f')[:-3]
                res['Seq'] = seq

                res['Fixture'] = {
                    "Id": fixture['id'],
                    "Price": price,
                    "Status": 0
                }

                print(res)
            
                try:
                    fixture_end_price = db_get_fixture_end_price(
                        fixture['id'])
                    if(fixture_end_price == None):
                        db_set_fixture_price(fixture['id'], price)

                    SECRET_KEY = os.getenv('OWAPI_SECRET_KEY')
                    access_key = hashlib.md5(
                        (SECRET_KEY+json.dumps(res)).encode('utf-8')).hexdigest()
                    print('ACCESS KEY: ', access_key)
                    headers = {"content-type": "application/json",
                                "oneworks-access-key": access_key}
                    print(headers)
                    URL = os.getenv('OWAPI_HOST') + \
                        "/api/CryptoCurrency/EndFixture"
                    print(URL)
                    response = requests.post(
                        URL, json=res, headers=headers)
                    print(response)
                    logger.info(str(CURR_TIME.strftime("%m/%d/%Y, %H:%M:%S"))+" - EndFixture - "+str(
                        fixture['id'])+" - Request - "+str(res)+" - Response - "+str(response)+" - " + str(response.text))
                    if(response.status_code == 200):
                        db_set_fixture_status(fixture['id'], "ENDED")
                        rclient.set("fixtureEnded", str(fixture['id']))
                        # rclient.delete("fixtureId")             
                except Exception as e:
                    logger.info(str(CURR_TIME.strftime("%m/%d/%Y, %H:%M:%S"))+" - EndFixture - "+str(
                        fixture['id'])+" - Request - "+str(res)+" - Response - "+str(e))
