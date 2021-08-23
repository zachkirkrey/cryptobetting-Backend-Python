# BackEnd

- Install Python3

```
sudo apt-get update

sudo apt-get install python3.8

```

- Install Redis

```
sudo apt install redis-server

sudo nano /etc/redis/redis.conf

# change "supervised no" to "supervised systemd" 
supervised systemd

sudo systemctl restart redis.service

sudo systemctl status redis

```

- Create virtual environment

```
python3 -m venv boTrading

cd boTrading/

source bin/activate

```

- Clone git respository 

```
git clone https://github.com/Cryptobetting/backend.git

cd backend\

```
- Install Requirements

```
pip install -r requirements.txt

```

- Add cronjobs 
  - cronCreated.sh, cronStarted.sh and cronEnded.sh file runs every minute, where cronFixture runs once a day.

```
crontab -e

###### add following code to cron file

* * * * * bash /home/ubuntu/boTrading/backend/cronCreated.sh > /dev/null 2>&1
* * * * * bash /home/ubuntu/boTrading/backend/cronStarted.sh > /dev/null 2>&1
* * * * * bash /home/ubuntu/boTrading/backend/cronEnded.sh > /dev/null 2>&1
0 0 * * * bash /home/ubuntu/boTrading/backend/cronFixture.sh > /dev/null 2>&1

```

- Install Supervisor

```
pip install supervisor

supervisord -c supervisord.conf

```


- Run the API App

```
pip install gunicorn

gunicorn -w 3 -t 2 -b 0.0.0.0:7000 --timeout 15000 --max-requests 1000 app:app --daemon

```

- To Kill Gunicorn Process of App

```
pkill gunicorn

```

- Run Websocket Server (Node.js)

```
npm install ws -g

npm install redis -g

npm install pm2 -g

pm2 start "node server.js" --name "websocket server"

```