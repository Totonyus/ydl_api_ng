#!/bin/bash

echo ~~~ ydl_api_ng
echo ~~~ Revision : $GIT_BRANCH - $GIT_REVISION
echo ~~~ Docker image generated : $DATE

mkdir -p /app/logs /app/downloads /app/params /app/tmp
cp -n /app/setup/* /app/params/

pip3 install yt-dlp --upgrade
pip3 install -r /app/params/hooks_requirements

addgroup --gid $GID ydl_api_ng && useradd --uid $UID --gid ydl_api_ng ydl_api_ng

chown $UID:$GID /app/logs
chown $UID:$GID /app/downloads

cat <<EOT >> /app/supervisord.conf
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

supervisord -c /app/supervisord.conf -l /app/logs/supervisord.log -j /app/tmp/pid -u ydl_api_ng -e $LOG_LEVEL

su ydl_api_ng -c "python3 main.py"
