from datetime import datetime, timedelta
import json
import os
from db import db_add_fixture

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
        db_add_fixture(1, start_time, market_end_time, end_time)

        STARTTIME = STARTTIME + timedelta(minutes=start_diff)
