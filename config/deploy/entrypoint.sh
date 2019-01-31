#!/bin/bash

cp -rf /shared/config/.env /code/config/

/usr/bin/supervisord --configuration config/deploy/supervisord.conf

tail -f logs/*.log

