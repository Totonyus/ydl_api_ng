#!/bin/bash

echo ~~~ ydl_api_ng
echo ~~~ Revision : $GIT_BRANCH - $GIT_REVISION
echo ~~~ Docker image generated : $DATE

mkdir -p /app/logs /app/downloads /app/params /app/tmp /home/ydl_api_ng /app/data
cp -n /app/setup/* /app/params/
touch /app/data/database.json
ln -s /app/data/database.json ./database.json


pip3 install yt-dlp --upgrade
pip3 install -r /app/params/hooks_requirements

addgroup --gid $GID ydl_api_ng && useradd --uid $UID --gid ydl_api_ng ydl_api_ng

chown $UID:$GID /app/logs /app/downloads /home/ydl_api_ng /app/data /app/data/database.json

if [ "$DISABLE_REDIS" == "false" ]; then
cat <<EOT >> /app/supervisord_api.conf
[supervisord]

[program:worker]
command=rq worker ydl_api_ng -u "redis://ydl_api_ng_redis:6379"
process_name=%(program_name)s-%(process_num)s
numprocs=$NB_WORKERS
directory=.
stopsignal=TERM
autostart=true
autorestart=true
user=$UID
EOT

supervisord -c /app/supervisord_api.conf -l /app/logs/supervisord_api.log -j /app/tmp/pid_api -u ydl_api_ng -e $LOG_LEVEL
fi

cat <<EOT >> /app/supervisord_programmation.conf
[supervisord]

[program:programmation]
command=python3 programmation_daemon.py
process_name=%(program_name)s-%(process_num)s
numprocs=1
directory=.
stopsignal=TERM
autostart=true
autorestart=true
user=$UID
EOT

supervisord -c /app/supervisord_programmation.conf -l /app/logs/supervisord_programmation.log -j /app/tmp/pid_programmation -u ydl_api_ng -e $LOG_LEVEL

su ydl_api_ng -c "python3 main.py"