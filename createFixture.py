
from datetime import datetime, timedelta
import json
import requests
import hashlib
from db import db_add_fixture

# data = {"Timestamp": "2021/07/06 15:26:00.768","Seq": "d8382c1d-6ce0-433d-9233-e7358b10a70b","Fixture":{"Id": 1625559334,"StartTime": "2021/07/06 03:30:00","MarketEndTime": "2021/07/06 03:40:00","EndTime": "2021/07/06 03:45:00"}}

# SECRET_KEY = '8sxy54vjd3ks5cge'

# access_key = hashlib.md5((SECRET_KEY+str(data)).encode('utf-8')).hexdigest()

# print(access_key)

# headers = {"content-type": "application/json",
#            "oneworks-access-key": "a37a6a7e82779a3312b880bd5567cd73"}

# response = requests.post("http://owapi1.playthefun.com:9130/api/CryptoCurrency/CreateFixture", json=data, headers=headers)
# print(response)
# print(response.json())
# print(json.dumps(response.json()))
# print('\n\n')



# def createFixture():

#     db_add_fixture()


def hour_rounder(t):
    # Rounds to nearest hour by adding a timedelta hour if minute >= 30
    return (t.replace(second=0, microsecond=0, minute=0, hour=t.hour)
            + timedelta(hours=t.minute//30))

STARTTIME = datetime.now()
STARTTIME = hour_rounder(STARTTIME)
print(STARTTIME)


ENDTIME = STARTTIME + timedelta(hours=24)
print(ENDTIME)

now = datetime.now()

#type 1
while(STARTTIME < ENDTIME):
    start_time = STARTTIME
    end_time = start_time + timedelta(minutes=15)
    market_end_time =  end_time - timedelta(minutes=5)
    # print(end_time.minute)
    # if (end_time.minute != 0):
    print(start_time, market_end_time, end_time)
    db_add_fixture(1, start_time, market_end_time, end_time)

    STARTTIME = end_time

STARTTIME = datetime.now()
STARTTIME = hour_rounder(STARTTIME)
print(STARTTIME)

# # type 2
# while(STARTTIME < ENDTIME):
#     start_time = STARTTIME
#     end_time = start_time + timedelta(hours=1)
#     market_end_time = end_time - timedelta(minutes=5)
#     print(start_time, market_end_time, end_time)
#     db_add_fixture(2, start_time, market_end_time, end_time)

#     STARTTIME = end_time
