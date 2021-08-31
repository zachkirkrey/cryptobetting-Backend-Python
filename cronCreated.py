from datetime import datetime, timedelta
import json
import math
import asyncio
import requests
import redis
import os
import ast
from db import db_get_fixture, db_set_fixture_status
import uuid
import hashlib
import pytz
import logging
from logging.handlers import TimedRotatingFileHandler

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

CURR_TIME = datetime.now()

FIXTURE_TIME = CURR_TIME + timedelta(minutes=15)
print(FIXTURE_TIME)

fixtures = db_get_fixture(FIXTURE_TIME)
print(fixtures)
if(fixtures != None):
    fixtures = json.loads(fixtures)
    print(fixtures)
    print(type(fixtures))
    for fixture in fixtures:
        print(fixture['marketEndTime'])
        print(type(fixture['marketEndTime']))
        print(fixture['id'])
        print('STATUS: ', fixture['status'])

        if(fixture['status'] != 'CREATED'):
            fixtureCreated = rclient.get('fixtureCreated')
            print(fixtureCreated)
            if (fixtureCreated):
                fixtureId = ast.literal_eval(fixtureCreated)
            else:
                fixtureId = None

            if(fixtureId == None or fixtureId != fixture['id']):
                res = {}

                seq = str(uuid.uuid4())
                print(seq)

                res['Timestamp'] = (
                    datetime.now() + timedelta(hours=8)).strftime('%Y/%m/%d %H:%M:%S.%f')[:-3]
                res['Seq'] = seq
                res['Fixture'] = {
                    "Id": fixture['id'],
                    "StartTime":  datetime.utcfromtimestamp(fixture['startTime']/1000).astimezone(pytz.timezone('America/Antigua')).strftime('%Y/%m/%d %H:%M:%S'),
                    "MarketEndTime": datetime.utcfromtimestamp(fixture['marketEndTime']/1000).astimezone(pytz.timezone('America/Antigua')).strftime('%Y/%m/%d %H:%M:%S'),
                    "EndTime": datetime.utcfromtimestamp(fixture['endTime']/1000).astimezone(pytz.timezone('America/Antigua')).strftime('%Y/%m/%d %H:%M:%S')
                }
                print(res)
                try:
                    SECRET_KEY = os.getenv('OWAPI_SECRET_KEY')
                    access_key = hashlib.md5(
                        (SECRET_KEY+json.dumps(res)).encode('utf-8')).hexdigest()
                    print('ACCESS KEY: ', access_key)
                    headers = {"content-type": "application/json",
                               "oneworks-access-key": access_key}
                    print(headers)
                    response = requests.post(
                        "http://owapi1.playthefun.com:9130/api/CryptoCurrency/CreateFixture", json=res, headers=headers)
                    print(response)
                    logger.info(str(CURR_TIME.strftime("%m/%d/%Y, %H:%M:%S"))+" - CreateFixture - "+str(
                        fixture['id'])+" - Request - "+str(res)+" - Response - "+str(response)+" - " + str(response.text))
                    print(type(response))
                    if(response.status_code == 200 and 'ErrorCode' not in response):
                        db_set_fixture_status(fixture['id'], "CREATED")
                        rclient.set("fixtureCreated", str(fixture['id']))
                except Exception as e:
                    logger.info(str(CURR_TIME.strftime("%m/%d/%Y, %H:%M:%S"))+" - CreateFixture - "+str(
                        fixture['id'])+" - Request - "+str(res)+" - Response - "+str(e))
