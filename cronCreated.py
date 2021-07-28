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

USERPOOL = redis.ConnectionPool(
    host='localhost', port=6379, db=0, decode_responses=True)
rclient = redis.StrictRedis(connection_pool=USERPOOL, decode_responses=True)

CURR_TIME = datetime.now()

FIXTURE_TIME = CURR_TIME + timedelta(seconds=18000)
print(FIXTURE_TIME)

fixtures = db_get_fixture(FIXTURE_TIME)
print(fixtures)
if(fixtures != None):
    fixtures = json.loads(fixtures)
    print(fixtures)
    print(type(fixtures))
    print(fixtures[0]['marketEndTime'])
    print(type(fixtures[0]['marketEndTime']))
    print(fixtures[0]['id'])
    print('STATUS: ', fixtures[0]['status'])

    if(fixtures[0]['status'] != 'CREATED'):
        fixtureCreated = rclient.get('fixtureCreated')
        print(fixtureCreated)
        if (fixtureCreated):
            fixtureId = ast.literal_eval(fixtureCreated)
        else:
            fixtureId = None

        if(fixtureId == None or fixtureId != fixtures[0]['id']):
            res = {}

            seq = str(uuid.uuid4())
            print(seq)

            res['Timestamp'] = (datetime.now() + timedelta(hours=8)).strftime('%Y/%m/%d %H:%M:%S.%f')[:-3]
            res['Seq'] = seq
            res['Fixture'] = {
                "Id": fixtures[0]['id'],
                "StartTime":  datetime.utcfromtimestamp(fixtures[0]['startTime']/1000).astimezone(pytz.timezone('America/Antigua')).strftime('%Y/%m/%d %H:%M:%S'),
                "MarketEndTime": datetime.utcfromtimestamp(fixtures[0]['marketEndTime']/1000).astimezone(pytz.timezone('America/Antigua')).strftime('%Y/%m/%d %H:%M:%S'),
                "EndTime": datetime.utcfromtimestamp(fixtures[0]['endTime']/1000).astimezone(pytz.timezone('America/Antigua')).strftime('%Y/%m/%d %H:%M:%S')
            }
            print(res)

            SECRET_KEY = os.getenv('OWAPI_SECRET_KEY')
            access_key = hashlib.md5((SECRET_KEY+json.dumps(res)).encode('utf-8')).hexdigest()
            print('ACCESS KEY: ', access_key)
            headers = {"content-type": "application/json","oneworks-access-key": access_key}
            print(headers)
            response = requests.post("http://owapi1.playthefun.com:9130/api/CryptoCurrency/CreateFixture", json=res, headers=headers)
            print(response)
            print(type(response))
            if(response.status_code == 200 and 'ErrorCode' not in response):
                db_set_fixture_status(fixtures[0]['id'], "CREATED")
                rclient.set("fixtureCreated", str(fixtures[0]['id']))
