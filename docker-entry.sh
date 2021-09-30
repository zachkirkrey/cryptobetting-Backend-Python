#!/bin/sh

service cron start
supervisord -c sup-docker.conf
gunicorn -w 3 -t 2 -b 0.0.0.0:$BACKEND_PORT --timeout 15000 --max-requests 1000 app:app
# /usr/bin/supervisord
