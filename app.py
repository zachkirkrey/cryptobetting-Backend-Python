
from datetime import datetime
import json
from typing import Dict
from urllib.parse import urlencode
import redis
import os
import random
import string
from flask import send_file, Flask, jsonify
from flask_restful import Api, Resource, reqparse, request
from db import (db_add_expiries, db_add_probabilities,
                db_get_expiry_data, db_get_fixtures_by_status, db_get_fixtures, db_get_fixtures_by_id)
from flask_cors import CORS
from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token,
    get_jwt_identity, get_jti
)
from flask_basicauth import BasicAuth


# SETUP THE ENV
jwt_secret_key = os.getenv('BO_JWT_SECRET')

USERS_REDIS_HOST = os.getenv('BO_REDIS_HOST')
USERPOOL = redis.ConnectionPool(host=USERS_REDIS_HOST, port=6379, db=0, decode_responses=True)
rclient = redis.StrictRedis(connection_pool=USERPOOL, decode_responses=True)


# ## config
ALLOWED_EXTENSIONS = ['csv']
FILE_CONTENT_TYPES = {'csv': 'text/csv'}
ACCESS_EXPIRES = 86400
MSG_ALL_FIELDS = "Please enter all fields"


app = Flask(__name__)
# csrf = CSRFProtect()
# csrf.init_app(app)
CORS(app, origins="*", max_age="3600")
app.config['WTF_CSRF_ENABLED'] = True
app.config['JWT_SECRET_KEY'] = jwt_secret_key
app.config['PROPAGATE_EXCEPTIONS'] = True
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = ACCESS_EXPIRES
app.config['BASIC_AUTH_REALM'] = 'realm'


jwt = JWTManager(app)
basic_auth = BasicAuth(app)
api = Api(app, prefix='/api')


##
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

# COMMONS 

# API REQUESTS
class Test(Resource):
    def get(self):
        return jsonify(message="OK", success=True)


class ExpiryData(Resource):
    def get(self):
        args = request.args
        expiry = args['expiry']
        odds_id = args['odds_id']

        if(expiry == "" or expiry is None or odds_id == "" or odds_id is None):
            return jsonify(success=False, message=MSG_ALL_FIELDS)

        pairs_data = []

        data = db_get_expiry_data(expiry, odds_id)
        data = json.loads(data)
        print(data)
        # for pair in pairs:
        #     pairs_data.append(pair['pairName'])

        return jsonify(data)


class Fixtures(Resource):
    def get(self):
        args = request.args
        if('status' in args):
            status = args['status']
        else:
            status = None

        if('from' in args):
            from_fixture = args['from']
        else:
            from_fixture = None
        
        if('to' in args):
            to_fixture = args['to']
        else:
            to_fixture = None

        
        if(status != None):
            data = db_get_fixtures_by_status(status.upper())
        elif(from_fixture != None and to_fixture != None):
            data = db_get_fixtures_by_id(from_fixture, to_fixture)
        elif(from_fixture != None and to_fixture == None):
            data = db_get_fixtures_by_id(from_fixture, None)
        elif(from_fixture == None and to_fixture != None):
            data = db_get_fixtures_by_id(None, to_fixture)
        else:
            data = db_get_fixtures()
        # print(data)
        if(data):
            data = json.loads(data)
            print(data)

            return jsonify(data)
        else:
            return []

# ENDPOINTS

api.add_resource(Test, '/test')
api.add_resource(ExpiryData, '/expiryData')
api.add_resource(Fixtures, '/fixtures')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=9000)
