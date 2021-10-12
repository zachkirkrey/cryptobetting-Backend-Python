import asyncio
import asyncio_redis
import json
import redis
import os
from datetime import datetime
from db import db_add_pnldata, db_add_bids

USERPOOL = redis.ConnectionPool(
	host='localhost', port=6379, db=0, decode_responses=True)
rclient = redis.StrictRedis(connection_pool=USERPOOL, decode_responses=True)


def get_config_data():
	dir_path = os.path.dirname(os.path.realpath(__file__))
	path = dir_path + '/input.json'
	#print(path)
	f = open(path)
	data = json.load(f)
	return data

async def main():
    try:
        # Create connection
        connection = await asyncio_redis.Connection.create(host='localhost', port=6379)

        # Create subscriber.
        subscriber = await connection.start_subscribe()

        # Subscribe to channel.
        await subscriber.subscribe(['BO-DATA'])

        # Inside a while loop, wait for incoming events.
        while True:
            reply = await subscriber.next_published()
            # print('Received: ', repr(reply.value), 'BO-DATA', reply.channel)
            data = json.loads(reply.value)
            # print(data)
            # print(type(data))
            if 'fixtures' in data:
                fixtures = data['fixtures']
                # print(fixtures)
                timestamp = data['timestamp']
                price = data['price']
                for fixture in fixtures:
                    # print(fixture)
                    fixtureId = fixture['id']
                    # print("EXP: fixureExpiry_"+str(fixtureId))
                    fixtureExpiry = rclient.get("fixtureExpiry_"+str(fixtureId))
                    fixtureExpiry = int(int(fixtureExpiry)/ 1000)
                    for prob in fixture['probabilities']:
                        strike = prob['strike']
                        over = prob['over']
                        under = prob['under']

                        prob = rclient.get("fixtureProb_"+str(fixtureId)+"_"+str(strike))

                        # print('Fixture Id :', fixtureId)
                        # print('Timestamp :', timestamp)
                        # print('ExpiryTime :', fixtureExpiry)
                        # print('BTC price :', price)
                        # print('Strike price :', strike)
                        # print('Probability :', prob)
                        # print('Over :', over)
                        # print('Under :', under)

                        endTime = datetime.utcfromtimestamp(fixtureExpiry).strftime('%Y-%m-%d %H:%M:%S')

                        db_add_pnldata(fixtureId, price, strike, prob, over, under, timestamp, endTime)
                        
                        input_data = get_config_data()
                        bid_prob = input_data['bid_probability']

                        if(over <= bid_prob or under <= bid_prob):
                            db_add_bids(fixtureId, price, strike, prob, over, under, timestamp, endTime)

        # When finished, close the connection.
        connection.close()
    except Exception as e:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(main())

if __name__ == "__main__":

	loop = asyncio.get_event_loop()
	loop.run_until_complete(main())
