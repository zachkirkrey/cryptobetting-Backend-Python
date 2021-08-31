from datetime import datetime, timedelta
import json
from models import Fixtures
import os
from db import db_add_fixture, db_get_fixture, db_set_fixture_status
import requests
import redis
import ast
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

def hour_rounder(t):
    # Rounds to nearest hour by adding a timedelta hour if minute >= 30
    return (t.replace(second=0, microsecond=0, minute=0, hour=t.hour)
            + timedelta(hours=t.minute//30))

dir_path = os.path.dirname(os.path.realpath(__file__))
path = dir_path + '/fixture.json'
#print(path)
f = open(path)
data = json.load(f)

start_diff = int(data['StartDiff'])
start_end_diff = int(data['StartEndDiff'])
start_market_diff = int(data['StartMarketDiff'])

if(start_end_diff and start_market_diff):

    STARTTIME = datetime.now()
    STARTTIME = hour_rounder(STARTTIME)
    print(STARTTIME)

    ENDTIME = STARTTIME + timedelta(hours=24)
    print(ENDTIME)

    now = datetime.now()

    #type 1
    while(STARTTIME < ENDTIME):
        start_time = STARTTIME
        end_time = start_time + timedelta(minutes=start_end_diff)
        market_end_time =  start_time + timedelta(minutes=start_market_diff)
        # print(end_time.minute)

        print(start_time, market_end_time, end_time)
        fixtureId = db_add_fixture(1, start_time, market_end_time, end_time)

        if(fixtureId != 0):
            res = {}

            seq = str(uuid.uuid4())
            print(seq)

            res['Timestamp'] = (datetime.now() + timedelta(hours=8)).strftime('%Y/%m/%d %H:%M:%S.%f')[:-3]
            res['Seq'] = seq
            res['Fixture'] = {
                "Id": fixtureId,
                "StartTime":  datetime.utcfromtimestamp(int(start_time.timestamp())).astimezone(pytz.timezone('America/Antigua')).strftime('%Y/%m/%d %H:%M:%S'),
                "MarketEndTime": datetime.utcfromtimestamp(int(market_end_time.timestamp())).astimezone(pytz.timezone('America/Antigua')).strftime('%Y/%m/%d %H:%M:%S'),
                "EndTime": datetime.utcfromtimestamp(int(end_time.timestamp())).astimezone(pytz.timezone('America/Antigua')).strftime('%Y/%m/%d %H:%M:%S')
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
                    fixtureId)+" - Request - "+str(res)+" - Response - "+str(response)+" - " + str(response.text))
                print(type(response))
                if(response.status_code == 200 and 'ErrorCode' not in response):
                    db_set_fixture_status(fixtureId, "CREATED")
                    # rclient.set("fixtureCreated", str(fixtureId))
            except Exception as e:
                logger.info(str(CURR_TIME.strftime("%m/%d/%Y, %H:%M:%S"))+" - CreateFixture - " +
                            str(fixtureId)+" - Request - "+str(res)+" - Response - "+str(e))


        STARTTIME = STARTTIME + timedelta(minutes=start_diff)
        print('\n----------------------------------------------------------------------------------------------------------\n')
