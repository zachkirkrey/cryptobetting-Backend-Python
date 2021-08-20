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

USERPOOL = redis.ConnectionPool(
    host='localhost', port=6379, db=0, decode_responses=True)
rclient = redis.StrictRedis(connection_pool=USERPOOL, decode_responses=True)

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
                    rclient.srem("fixtureId", val)

except Exception as e:
    print(e)
