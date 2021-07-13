from datetime import datetime, timedelta
import json
import math
import asyncio
import requests
import redis
import os
import ast
from db import db_get_started_fixture
import uuid
import hashlib

USERPOOL = redis.ConnectionPool(
    host='localhost', port=6379, db=0, decode_responses=True)
rclient = redis.StrictRedis(connection_pool=USERPOOL, decode_responses=True)

CURR_TIME = datetime.now()

fixtures = db_get_started_fixture(CURR_TIME)
print(fixtures)
if(fixtures != None):
    fixtures = json.loads(fixtures)
    print(fixtures)
    print(type(fixtures))
    print(fixtures[0]['marketEndTime'])
    print(type(fixtures[0]['marketEndTime']))
    print(fixtures[0]['id'])

    fixtureStarted= rclient.get('fixtureStarted')
    print(fixtureStarted)
    if (fixtureStarted):
        fixtureId = ast.literal_eval(fixtureStarted)
    else:
        fixtureId = None

    if(fixtureId == None or fixtureId != fixtures[0]['id']):
        print('PUSH FIXTURE ID TO JSON')
        print(fixtures[0]['id'])
        rclient.set("fixtureStarted", str(fixtures[0]['id']))