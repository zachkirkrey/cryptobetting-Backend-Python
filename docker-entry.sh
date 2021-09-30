#!/bin/sh

service cron start
gunicorn -w 3 -t 2 -b 0.0.0.0:$BACKEND_PORT --timeout 15000 --max-requests 1000 app:app
# /usr/bin/supervisord
# nohup supervisord -c sup-docker.conf &