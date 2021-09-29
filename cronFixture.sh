#!/bin/sh
. /home/ubuntu/.bashrc
#Prod

export BO_DB_URL="Cryptobetting,,localhost,3306,amidoribo"
export OWAPI_SECRET_KEY=''
export OWAPI_HOST="http://bitcoin.edge2cast.com"
export MATH_MODEL_URL="http://35.76.229.61:3000/odds"

cd /home/ubuntu/cryptobetting/backend
/home/ubuntu/cryptobetting/bin/python createFixture.py
