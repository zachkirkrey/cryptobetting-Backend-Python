FROM ubuntu:20.04

RUN apt clean && apt-get update && \
    apt-get install -y python3 python3-pip python3-venv && \
    apt-get install -y cron  && apt-get install -y vim 

RUN python3 -m venv /home/ubuntu/boTrading
# This is wrong!
RUN . /home/ubuntu/boTrading/bin/activate

WORKDIR /home/ubuntu/boTrading/

RUN mkdir backend/

WORKDIR /home/ubuntu/boTrading/backend/

COPY . .

RUN pip install -r requirements.txt

EXPOSE 9000

ENV BO_DB_URL='root,root12345,bo-mysql,3306,amidoribo'
ENV OWAPI_SECRET_KEY='8sxy54vjd3ks5cge'
ENV OWAPI_HOST='http://btcuat.edge2cast.com'

RUN pip install gunicorn

# RUN gunicorn -b 0.0.0.0:9000 -w 2 -t 4 --max-requests 500 --timeout 300 app:app --daemon
# RUN DEBIAN_FRONTEND=noninteractive apt-get install -y nano

COPY ./files/cronjob /etc/cron.d/container_cronjob

RUN chmod 644 /etc/cron.d/container_cronjob

# Script file copied into container.
COPY ./files/script.sh /script.sh

# Giving executable permission to script file.
RUN chmod +x /script.sh

# Running commands for the startup of a container.
RUN /bin/bash -c /script.sh

CMD ["gunicorn", "-b", "0.0.0.0:7000", "-w", "2", "-t", "4", "--max-requests" ,"500", "--timeout", "300", "app:app"]

# Pulling ubuntu image with a specific tag from the docker hub.

# # Updating the packages and installing cron and vim editor if you later want to edit your script from inside your container.
# # RUN apt-get update \
# #     && apt-get install cron -y && apt-get install vim -y
# # Crontab file copied to cron.d directory.
# COPY ./files/cronjob /etc/cron.d/container_cronjob
# # Script file copied into container.
# COPY ./files/script.sh /script.sh
# # Giving executable permission to script file.
# RUN chmod +x /script.sh
# # Running commands for the startup of a container.
# CMD ["/bin/bash", "-c", "/script.sh && chmod 644 /etc/cron.d/container_cronjob && cron && tail -f /var/log/cron.log"]