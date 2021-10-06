from datetime import datetime, timedelta
import json
import math
import asyncio
from typing import Match
import requests
import redis
import os
import ast
from db import db_get_started_fixtures
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
    fixtures = db_get_started_fixtures()
    print(fixtures)
    if(fixtures != None):
        fixtures = json.loads(fixtures)
        for fixture in fixtures:
            print(fixture)
            print(type(fixture))
            print(fixture['endTime'])
            print(type(fixture['endTime']))
            print(fixture['id'])
            print(fixture['status'])

            rclient.set("fixtureExpiry_"+str(fixture['id']), fixture['endTime'])
except Exception as e:
    print(e)
