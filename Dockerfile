FROM python:3.7-stretch

RUN apt-get update && apt-get install -y supervisor vim

WORKDIR /code

ADD . .

RUN mkdir -p logs && mkdir -p tmp && pip install -r requirements.txt

ENTRYPOINT ["/bin/bash", "config/deploy/entrypoint.sh"]

# /usr/bin/mongod --fork --config config/deploy/mongodb.conf
# /usr/bin/supervisord --nodaemon --configuration config/deploy/supervisord.conf
# /usr/bin/supervisord --configuration config/deploy/supervisord.conf