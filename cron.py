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

FIXTURE_TIME = CURR_TIME - timedelta(minutes=10)
print(FIXTURE_TIME)

fixtures = rclient.get('fixtureCreated')
print(fixtures)


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

    SECRET_KEY = os.getenv('OWAPI_SECRET_KEY')
    access_key = hashlib.md5((SECRET_KEY+json.dumps(res)).encode('utf-8')).hexdigest()
    print('ACCESS KEY: ', access_key)
    headers = {"content-type": "application/json","oneworks-access-key": access_key}
    print(headers)
    response = requests.post("http://owapi1.playthefun.com:9130/api/CryptoCurrency/CreateFixture", json=res, headers=headers)
    print(response)
    if(response.status_code == 200):
        rclient.set("fixtureCreated", str(fixtures))


else:
    fixtures = rclient.get('fixtureCreated')
    if (fixtures):
        fixtures = ast.literal_eval(fixtures)
    
    print(fixtures)
    print(CURR_TIME.timestamp())

    curr_time = int(CURR_TIME.timestamp() * 1000)
    print(curr_time)

    if(curr_time < fixtures[0]['startTime']):
        print('WAIT 1')
        print(fixtures[0]['id'])
    if(curr_time > fixtures[0]['startTime'] and curr_time < fixtures[0]['marketEndTime']):
        print('WAIT 2')
        print(fixtures[0]['id'])
    if(curr_time > fixtures[0]['marketEndTime'] and curr_time < fixtures[0]['endTime']):
        print('PUSH FIXTURE ID TO JSON')
        print(fixtures[0]['id'])
        rclient.set('fixtureId', str(fixtures[0]['id']))

    if(curr_time > fixtures[0]['endTime']):
        print('CALL END FIXTURE API AND COMMUNICATE THE RESULT')
        print(fixtures[0]['id'])

        res = {}

        seq = str(uuid.uuid4())
        print(seq)

        resdisdata = rclient.get('last_sent_price')
        if (resdisdata):
            last_sent_price = ast.literal_eval(resdisdata)

        if(last_sent_price > 0):
            res['Timestamp'] = datetime.now().strftime('%Y/%m/%d %I:%M:%S')
            res['Seq'] = seq
        
            res['Fixture'] = {
                "Id": fixtures[0]['id'],
                "Price": last_sent_price,
                "Status": 0
            }

            print(res)

            SECRET_KEY = os.getenv('OWAPI_SECRET_KEY')
            access_key = hashlib.md5((SECRET_KEY+json.dumps(res)).encode('utf-8')).hexdigest()
            print('ACCESS KEY: ', access_key)
            headers = {"content-type": "application/json","oneworks-access-key": access_key}
            print(headers)
            response = requests.post("http://owapi1.playthefun.com:9130/api/CryptoCurrency/EndFixture", json=res, headers=headers)
            print(response)
            if(response.status_code == 200):
                rclient.delete("fixtureCreated")
                rclient.delete("fixtureId")
