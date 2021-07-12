from datetime import datetime, timedelta
import json
import math
import asyncio
import requests
import redis
import os
import ast
from db import db_get_fixture
import uuid
import hashlib

USERPOOL = redis.ConnectionPool(
    host='localhost', port=6379, db=0, decode_responses=True)
rclient = redis.StrictRedis(connection_pool=USERPOOL, decode_responses=True)

CURR_TIME = datetime.now()

FIXTURE_TIME = CURR_TIME + timedelta(seconds=18)
print(FIXTURE_TIME)

if rclient.get("fixtureCreated") == None:
    
    res = {}

    fixtures = db_get_fixture(FIXTURE_TIME)
    fixtures = json.loads(fixtures)
    print(fixtures)
    print(type(fixtures))
    print(fixtures[0]['marketEndTime'])
    print(type(fixtures[0]['marketEndTime']))

    print(fixtures[0]['id'])

    seq = str(uuid.uuid4())
    print(seq)

    res['Timestamp'] = datetime.now().strftime('%Y/%m/%d %I:%M:%S')
    res['Seq'] = seq
    res['Fixture'] = {
        "Id": fixtures[0]['id'],
        "StartTime":  datetime.utcfromtimestamp(fixtures[0]['startTime']/1000).strftime('%Y/%m/%d %I:%M:%S'),
        "MarketEndTime": datetime.utcfromtimestamp(fixtures[0]['marketEndTime']/1000).strftime('%Y/%m/%d %I:%M:%S'),
        "EndTime": datetime.utcfromtimestamp(fixtures[0]['endTime']/1000).strftime('%Y/%m/%d %I:%M:%S')
    }

    print(res)


    SECRET_KEY = '8sxy54vjd3ks5cge'

    access_key = hashlib.md5((SECRET_KEY+str(res)).encode('utf-8')).hexdigest()

    print('ACCESS KEY: ', access_key)

    headers = {"content-type": "application/json",
               "oneworks-access-key": access_key}

    print(headers)

    response = requests.post("http://owapi1.playthefun.com:9130/api/CryptoCurrency/CreateFixture", json=res, headers=headers)
    print(response)
    print(response.json())
    print(json.dumps(response.json()))
    print('\n\n')
 
    if(CURR_TIME.timestamp() < fixtures[0]['startTime']):
        print('WAIT 1')
        print(fixtures[0]['id'])
    if(CURR_TIME.timestamp() > fixtures[0]['startTime'] and CURR_TIME.timestamp() < fixtures[0]['marketEndTime']):
        print('WAIT 2')
        print(fixtures[0]['id'])
    if(CURR_TIME.timestamp() > fixtures[0]['marketEndTime'] and CURR_TIME.timestamp() < fixtures[0]['endTime']):
        print('PUSH FIXTURE ID TO JSON')
        print(fixtures[0]['id'])
    if(CURR_TIME.timestamp() > fixtures[0]['endTime']):
        print('CALL END FIXTURE API AND COMMUNICATE THE RESULT')
        print(fixtures[0]['id'])
    # rclient.set('last_sent_price', str(mark_price))
    # rclient.setex("fixtureCreated", 60, 1)


