from datetime import datetime, timedelta
import json
import math
import asyncio
import requests
import redis
import os
import ast
import traceback
import logging
from logging.handlers import RotatingFileHandler
logging.basicConfig(
  handlers=[
	RotatingFileHandler(
	  'mathModelData.log',
	  maxBytes=10240000,
	  backupCount=1
	)
  ],
  level=logging.INFO,
  format='%(asctime)s %(levelname)s %(message)s'
)

from unicorn_binance_websocket_api.unicorn_binance_websocket_api_manager import BinanceWebSocketApiManager
# from db import db_add_expiries, db_add_probabilities

USERPOOL = redis.ConnectionPool(
	host='localhost', port=6379, db=0, decode_responses=True)
rclient = redis.StrictRedis(connection_pool=USERPOOL, decode_responses=True)


def nearest(list, timestamp):
	return min([t for t in list if t > timestamp])


def findNearest(min_time_exp, time_roundings, curr_datetime):
	min_time_rounding = min(time_roundings)

	print("TIME ROUNDING: ", min_time_rounding)

	min_minutes_diff = (min_time_rounding -
						curr_datetime).total_seconds() / 60.0
	print("TIME DIFF: ", min_minutes_diff)

	if(len(time_roundings) > 1):
		while(min_time_exp > min_minutes_diff):
			min_time_rounding = nearest(time_roundings, min_time_rounding)
			print('NEXT TIME ROUNDING: ', min_time_rounding)
			min_minutes_diff = (min_time_rounding -
								curr_datetime).total_seconds() / 60.0
			print("TIME DIFF: ", min_minutes_diff)
			if(min_time_exp > min_minutes_diff):
				break

	return min_time_rounding


def get_config_data():
	dir_path = os.path.dirname(os.path.realpath(__file__))
	path = dir_path + '/input.json'
	#print(path)
	f = open(path)
	data = json.load(f)
	return data

def get_math_model_data(URL, finalJson):
	try:
		print('------- Calling Math Model --------')
		print(URL)
		response = requests.post(URL, data=finalJson)
		return response
	except Exception as e:
		return None

async def calculate(data, PRICE, fixtureIds):
	SLOTS = 2
	
	last_timeline = None
	
	print('INPUT DATA: ', data)
	print('\n\n')

	print('PRICE: ', PRICE)
	print('\n')
	
	try:
		finalOutput = {}

		expriries = []
		for fixtureId in fixtureIds:
			EXPIRIES = []
			print("EXP: fixureExpiry_"+str(fixtureId))
			fixtureExpiry = rclient.get("fixtureExpiry_"+str(fixtureId))
			fixtureExpiry = int(int(fixtureExpiry)/1000)
			
			for i in range(1, SLOTS+1):
				try:
					exp = {}

					print('-------------------SLOT-' +str(i)+'-------------------------')
					slot_left = data['Slots_left_'+str(i)]
					slot_right = data['Slots_right_'+str(i)]
					slot_rounding = data['Slot_Rounding_'+str(i)]
					# print(slot_left, slot_right, slot_rounding)

					rounding_left = []
					rounding_right = []
					rounding_min = min(slot_rounding)
					# print(rounding_min)

					# val = PRICE - res
					if rounding_min in slot_rounding:
						round_to = rounding_min
					else:
						round_to = 1000

					nearest_under = round_to * math.floor((PRICE/round_to))
					nearest_over = round_to * math.ceil((PRICE/round_to))
					# print(nearest_under)
					# print(nearest_over)
					rounding_left.append(nearest_under)
					rounding_right.append(nearest_over)

					for j in range(0, slot_left-1):
						last_under = rounding_left[-1]
						next_under = last_under - rounding_min
						rounding_left.append(next_under)

					rounding_left = sorted(rounding_left, key=int)
					print("ROUNDING LEFT: ", rounding_left)

					for j in range(0, slot_right-1):
						last_over = rounding_right[-1]
						next_over = last_over + rounding_min
						rounding_right.append(next_over)

					print("ROUNDING RIGHT: ", rounding_right)

					strike_prices = rounding_left + rounding_right
					print("STRIKING PRICES: ", strike_prices)

					if(i == 1):
						curr_datetime = datetime.now()
						print(curr_datetime)

						curr_hour = curr_datetime.hour
						curr_minute = curr_datetime.minute
						print(curr_hour, curr_minute)

						ct = datetime.now().strftime("%H:%M")
						# print(ct)
						# print(type(ct))

						timezone_rounding = data['Timezone_Rounding_'+str(i)]

						timestamps = []
						time_roundings = []

						for res in timezone_rounding:
							print(res)
							if(curr_minute < res):
								hour = curr_hour
								minute = res
								min_diff = res - curr_minute
								print("MIN DIFF: ", min_diff)
								next_datetime = curr_datetime + \
									timedelta(minutes=min_diff)
							elif(curr_minute > res):
								hour = curr_hour + 1
								minute = res

								min_diff = res - curr_minute
								print("MIN DIFF: ", min_diff)
								total_diff = 60 + min_diff
								print("MIN DIFF: ", total_diff)
								next_datetime = curr_datetime + \
									timedelta(minutes=total_diff)

							# print(hour, minute)
							next_time = str(hour)+":"+str(minute)
							timestamps.append(next_time)
							time_roundings.append(next_datetime)

						print("Time Rounding: ", timestamps)
						print("Time Rounding: ", time_roundings)

						min_time_exp = data['Minimum_time_expiration_'+str(i)]
						print("MIN TIME EXPIRY: ", min_time_exp)

						min_time_rounding = findNearest(
							min_time_exp, time_roundings, curr_datetime)
						print("MIN TIMESTAMP: ", min_time_rounding)
						# min_hour = min_time_rounding.hour
						# min_minute = min_time_rounding.minute
						# min_hour_minute = str(min_hour)+":"+str(min_minute)
						# print("MIN TIMESTAMP: ", min_hour_minute)
						print('\n\n')

						total_timelines = data['Timelines_'+str(i)]
						timelines_gap = data['Timezone_Gap_'+str(i)]
						print(timelines_gap)

						if(total_timelines > 0):

							exp['expiry'] = fixtureExpiry
							exp['strikes'] = strike_prices

							EXPIRIES.append(exp)

							last_timeline = min_time_rounding

							for k in range(0, total_timelines-1):
								exp = {}
								next_min_time_rounding = min_time_rounding + \
									timedelta(minutes=timelines_gap)
								print("NEXT MIN TIMESTAMP: ", next_min_time_rounding)
								# next_min_hour = next_min_time_rounding.hour
								# next_min_minute = next_min_time_rounding.minute
								# next_min_hour_minute = str(next_min_hour)+":"+str(next_min_minute)
								# print("NEXT MIN TIMESTAMP: ", next_min_hour_minute)
								min_time_rounding = next_min_time_rounding
								print('\n\n')

								exp['expiry'] = fixtureExpiry
								exp['strikes'] = strike_prices

								EXPIRIES.append(exp)

								last_timeline = next_min_time_rounding
					else:
						if(last_timeline != None):
							print("LAST TIMELINE OF SLOT " + str(i-1)+": ", last_timeline)

							total_timelines = data['Timelines_'+str(i)]
							timelines_gap = data['Timezone_Gap_'+str(i)]
							print(timelines_gap)

							if(total_timelines > 0):
								next_min_time_rounding = last_timeline + timedelta(minutes=timelines_gap)
								exp['expiry'] = int(next_min_time_rounding.timestamp())
								exp['strikes'] = strike_prices

								EXPIRIES.append(exp)

								for k in range(0, total_timelines-1):
									exp = {}
									next_min_time_rounding = next_min_time_rounding + timedelta(minutes=timelines_gap)
									print("NEXT MIN TIMESTAMP: ", next_min_time_rounding)
									# next_min_hour = next_min_time_rounding.hour
									# next_min_minute = next_min_time_rounding.minute
									# next_min_hour_minute = str(next_min_hour)+":"+str(next_min_minute)
									# print("NEXT MIN TIMESTAMP: ", next_min_hour_minute)
									# last_timeline = next_min_time_rounding
									print('\n\n')

									exp['expiry'] = fixtureExpiry
									exp['strikes'] = strike_prices

									EXPIRIES.append(exp)

				except Exception as e:
					traceback.print_exc()
					print(e)

			
			
			# print(fixtureId)
			result = {}
			result['asset_price'] = PRICE
			result['time_stamp'] = int(curr_datetime.timestamp())

			result['expiries'] = EXPIRIES

			finalJson = json.dumps(result)
			logging.info('FIXTURE ID: '+str(fixtureId)+" Fixture Expiry: "+str(fixtureExpiry))
			logging.info(json.dumps(finalJson))
			
			# with open('output.json', "w+") as f:
			#     f.write(finalJson)  
			response = None
			try:
				URL = os.getenv('MATH_MODEL_URL')
				response = get_math_model_data(URL, finalJson)
				print(response)
				if(response == None and response.status_code != 200):
					URL = os.getenv('MATH_MODEL_URL_NEW')
					response = get_math_model_data(URL, finalJson)
			except Exception as e:
				print(e)
				continue
			
			# print(response)
			# print(response.json())
			# print("FIXTURE ID: ", fixtureId)
			# print("Fixture Expiry: ",fixtureExpiry)
			if(response != None and response.status_code == 200):
				logging.info(json.dumps(response.json()))
				logging.info('________________________________________')
				if "error" in response.json():
					continue
				
				for j in response.json()['expiries']:
					odds_id = 1
					expiry = {}
					expiry['id'] = fixtureId
					# expiry['expiry'] = j['expiry']
					probabilities = []
					# idexpiries = db_add_expiries(j['expiry'], PRICE, data['Rake_over'], data['Rake_under'])
					# print(idexpiries)
					# print(j)
					for prob in j['probabilities']:
						probability = {}
						# print(prob)
						over_prob = prob['probability']
						under_prob = (1 - over_prob)
						rake_over_val = 0.94
						rake_under_val = 0.94
#						if(over_prob>0.5):
#							rake_over_val = 0.95
#							rake_under_val = 0.99
#						if(over_prob <= 0.5):
#							rake_over_val = 0.99
#							rake_under_val = 0.95

						rake_over = rake_over_val * (1 / over_prob)
						rake_under = rake_under_val * (1 / under_prob)

						if(rake_over > 15):
							rake_over = 15
						if(rake_over <= 1.01):
							rake_over = 1.01
						
						if(rake_under > 15):
							rake_under = 15
						if(rake_under <= 1.01):
							rake_under = 1.01
						


						# probability['odds_id'] = odds_id
						probability['strike'] = prob['strike']
						probability['over'] = float('{:.3g}'.format(rake_over))
						probability['under'] = float('{:.3g}'.format(rake_under))

						rclient.set("fixtureProb_"+str(fixtureId)+"_"+str(prob['strike']), float('{:.3g}'.format(prob['probability'])))

						# print('Timestamp :', int(curr_datetime.timestamp()))
						# print('ExpiryTime :', fixtureExpiry)
						# print('BTC price :', PRICE)
						# print('Strike price :', prob['strike'])
						# print('Over :', float('{:.3g}'.format(rake_over)))
						# print('Under :', float('{:.3g}'.format(rake_under)))
						
						# db_add_probabilities(idexpiries, odds_id, prob['strike'], float('{:.3g}'.format(over_prob)), float('{:.3g}'.format(under_prob)))

						probabilities.append(probability)
						odds_id = odds_id + 1

					expiry['probabilities'] = probabilities

					expriries.append(expiry)

		if(len(expriries) > 0):
			finalOutput['price'] = PRICE
			finalOutput['timestamp'] = (datetime.now() + timedelta(hours=8)).strftime('%Y/%m/%d %H:%M:%S.%f')[:-3]
			finalOutput['type'] = 2
			# finalOutput['rake_over'] = data['Rake_over']
			# finalOutput['rake_under'] = data['Rake_under']
			finalOutput['fixtures'] = expriries
			
			print(json.dumps(finalOutput))
			print('\n\n')

			rclient.set('BO-DATA', json.dumps(finalOutput))
			rclient.publish('BO-DATA', json.dumps(finalOutput))

	# refresh_rate = data['Refresh_rate']
	# await asyncio.sleep(refresh_rate)

	except Exception as e:
		print(e)
		traceback.print_exc()
		return {}


async def main():
	error = 0
	input_data = get_config_data()
	for k, v in input_data.items():
		if(type(v) == list):
			flag = 0
			for d in v:
				if(type(d) == int and d < 0):
					flag = 1

			if(flag == 1):
				print('Invaid '+k)
				error = 1

		if(type(v) == int and v < 0):
			print('Invaid '+k)
			error = 1

	if(error == 0):
		binance_websocket_api_manager = BinanceWebSocketApiManager(
			exchange="binance.com")
		binance_websocket_api_manager.create_stream(
			['miniTicker'], ['btcusdt'])
		while True:
			stream = binance_websocket_api_manager.pop_stream_data_from_stream_buffer()
			if stream:
				jsonstream = json.loads(stream)
				data = jsonstream.get('data')
				if data:
					
					resdisdata = rclient.get('last_sent_price')
					if (resdisdata):
						last_sent_price = ast.literal_eval(resdisdata)
					else:
						last_sent_price = -1
					# print(type(last_sent_price))
					# print(last_sent_price)

					mark_price = float(data['c'])
					print("Last Price; ", last_sent_price)
					print("Mark Price; ", mark_price)
					rclient.setex('BTC_PRICE', 30, str(mark_price))

					print(0.99*last_sent_price)
					print(1.01*last_sent_price)

					if rclient.get("sent_flag") == None:
						fixtureData = rclient.smembers('fixtureId')
						if (fixtureData):
							# fixtureId = ast.literal_eval(fixtureData)
							# print("Fixture Id; ", fixtureId)
							await calculate(input_data, mark_price, fixtureData)
							rclient.set('last_sent_price', str(mark_price))
							rclient.setex("sent_flag", 10, 1)
					elif (mark_price < ((1-float(input_data['Price_change']))*last_sent_price) or mark_price > ((1+float(input_data['Price_change']))*last_sent_price)):
						fixtureData = rclient.smembers('fixtureId')
						if (fixtureData and mark_price != last_sent_price):
							# print(fixtureData)
							# fixtureId = ast.literal_eval(fixtureData)
							# print("Fixture Id; ", fixtureId)
							await calculate(input_data, mark_price, fixtureData)
							rclient.set('last_sent_price', str(mark_price))
							rclient.setex("sent_flag", 10, 1)
					else:
						res = {}
						res['price'] = mark_price
						res['timestamp'] = (datetime.now() + timedelta(hours=8)).strftime('%Y/%m/%d %H:%M:%S.%f')[:-3] 
						res['type'] = 1
						rclient.publish('BO-DATA', json.dumps(res))


if __name__ == "__main__":

	loop = asyncio.get_event_loop()
	loop.run_until_complete(main())
