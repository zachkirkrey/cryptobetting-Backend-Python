from datetime import datetime, timedelta
import json
import math
import asyncio
from typing import Match
import requests
import redis
import os
import ast
from db import db_get_started_fixture, db_set_fixture_status, db_get_last_started_fixture
import uuid
import hashlib
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
print(CURR_TIME)

try:
    fixtures = db_get_started_fixture(CURR_TIME)
    print(fixtures)
    if(fixtures != None):
        fixtures = json.loads(fixtures)
        print(fixtures)
        print(type(fixtures))
        print(fixtures[0]['marketEndTime'])
        print(type(fixtures[0]['marketEndTime']))
        print(fixtures[0]['id'])
        print(fixtures[0]['status'])

        if(fixtures[0]['status'] == 'CREATED'):

            fixtureStarted = rclient.get('fixtureStarted')
            print(fixtureStarted)
            if (fixtureStarted):
                fixtureId = ast.literal_eval(fixtureStarted)
            else:
                fixtureId = None

            if(fixtureId == None or fixtureId != fixtures[0]['id']):
                print('PUSH FIXTURE ID TO JSON')
                print(fixtures[0]['id'])
                db_set_fixture_status(fixtures[0]['id'], "STARTED")
                rclient.set("fixtureStarted", str(fixtures[0]['id']))
                rclient.sadd("fixtureId", str(fixtures[0]['id']))
except Exception as e:
    print(e)

try:
    endfixtures = db_get_last_started_fixture(CURR_TIME)
    print(endfixtures)
    if(endfixtures != None):
        fixtures = json.loads(endfixtures)
        print(fixtures)
        print(type(fixtures))
        print(fixtures[0]['marketEndTime'])
        print(type(fixtures[0]['marketEndTime']))
        print(fixtures[0]['id'])


        fixtureId = fixtures[0]['id']

        if(fixtureId != None):
            print('STOP FIXTURE')
            print(fixtureId)
            print("Contents of the Redis set:")
            print(rclient.smembers("fixtureId"))
            fixtureIds = rclient.smembers('fixtureId')
            print(fixtureIds)
            for value in fixtureIds:
                print(value)
                val = int(value)
                if(val <= fixtureId):          
                    res = {}

                    seq = str(uuid.uuid4())
                    print(seq)

                    res['Timestamp'] = (
                        datetime.now() + timedelta(hours=8)).strftime('%Y/%m/%d %H:%M:%S.%f')[:-3]
                    res['Seq'] = seq
                    res['Fixture'] = {
                        "Id": val
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
                        URL = os.getenv('OWAPI_HOST') + "/api/CryptoCurrency/EndMarket"
                        print(URL)
                        response = requests.post(URL, json=res, headers=headers)
                        print(response)
                        logger.info(str(CURR_TIME.strftime("%m/%d/%Y, %H:%M:%S"))+" - EndMarket - "+str(
                            val)+" - Request - "+str(res)+" - Response - "+str(response)+" - " + str(response.text))
                        print(type(response))
                        if(response.status_code == 200 and 'ErrorCode' not in response):
                            rclient.srem("fixtureId", val)
                    except Exception as e:
                        logger.info(str(CURR_TIME.strftime("%m/%d/%Y, %H:%M:%S"))+" - EndMarket - "+str(
                            val)+" - Request - "+str(res)+" - Response - "+str(e))



except Exception as e:
    print(e)
