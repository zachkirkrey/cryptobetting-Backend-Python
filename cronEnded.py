from datetime import datetime, timedelta
import json
import math
import asyncio
import requests
import redis
import os
import ast
from db import db_get_ended_fixture, db_set_fixture_status, db_set_fixture_price
import uuid
import hashlib

USERPOOL = redis.ConnectionPool(
    host='localhost', port=6379, db=0, decode_responses=True)
rclient = redis.StrictRedis(connection_pool=USERPOOL, decode_responses=True)

CURR_TIME = datetime.now()

FIXTURE_TIME = CURR_TIME - timedelta(minutes=10)
print(FIXTURE_TIME)

fixtures = db_get_ended_fixture(CURR_TIME)
fixtures = json.loads(fixtures)
print(fixtures)
print(type(fixtures))
print(fixtures[0]['marketEndTime'])
print(type(fixtures[0]['marketEndTime']))
print(fixtures[0]['id'])
print(fixtures[0]['status'])

if(fixtures[0]['status'] == 'STARTED'):

    fixtureEnded = rclient.get('fixtureEnded')
    print(fixtureEnded)
    if (fixtureEnded):
        fixtureId = ast.literal_eval(fixtureEnded)
    else:
        fixtureId = None

    if(fixtureId == None or fixtureId != fixtures[0]['id']):
        print('CALL END FIXTURE API AND COMMUNICATE THE RESULT')
        print(fixtures[0]['id'])

        res = {}

        seq = str(uuid.uuid4())
        print(seq)

        resdisdata = rclient.get('BTC_PRICE')
        if (resdisdata):
            price = ast.literal_eval(resdisdata)

        if(price > 0):
            res['Timestamp'] = (datetime.now() + timedelta(hours=8)).strftime('%Y/%m/%d %H:%M:%S.%f')[:-3]
            res['Seq'] = seq

            res['Fixture'] = {
                "Id": fixtures[0]['id'],
                "Price": price,
                "Status": 0
            }

            print(res)

            SECRET_KEY = os.getenv('OWAPI_SECRET_KEY')
            access_key = hashlib.md5(
                (SECRET_KEY+json.dumps(res)).encode('utf-8')).hexdigest()
            print('ACCESS KEY: ', access_key)
            headers = {"content-type": "application/json",
                        "oneworks-access-key": access_key}
            print(headers)
            response = requests.post(
                "http://owapi1.playthefun.com:9130/api/CryptoCurrency/EndFixture", json=res, headers=headers)
            print(response)
            if(response.status_code == 200):
                db_set_fixture_price(fixtures[0]['id'], price)
                db_set_fixture_status(fixtures[0]['id'], "ENDED")
                rclient.set("fixtureEnded", str(fixtures[0]['id']))
                # rclient.delete("fixtureId")
