#!/bin/bash

echo ~~~ ydl_api_ng
echo ~~~ Revision : $GIT_BRANCH - $GIT_REVISION
echo ~~~ Docker image generated : $DATE

mkdir -p /app/logs /app/downloads /app/params /app/tmp /home/ydl_api_ng /app/data /root/yt-dlp-plugins /app/cookies/
cp -n /app/setup/* /app/params/
touch /app/data/database.json
ln -s /app/data/database.json ./database.json

if [ "$FORCE_YTDLP_VERSION" == "" ]; then
  echo --- Upgrade yt-dlp to the latest version ---
  pip3 install yt-dlp --upgrade
else
  echo --- Force yt-dlp version $FORCE_YTDLP_VERSION ---
  pip3 install yt-dlp==$FORCE_YTDLP_VERSION --force-reinstall
fi

pip3 install -r /app/params/hooks_requirements

addgroup --gid $GID ydl_api_ng && useradd --uid $UID --gid ydl_api_ng ydl_api_ng

chown $UID:$GID /app/logs /app/downloads /home/ydl_api_ng /app/tmp /app/data /app/data/database.json /app/cookies /root/yt-dlp-plugins
chmod a+x /root/ entrypoint.sh

if [ "$DISABLE_REDIS" == "false" ]; then
  cat <<EOT >>/app/supervisord_workers.conf
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

  supervisord -c /app/supervisord_workers.conf -l /app/logs/supervisord_workers.log -j /app/tmp/pid_api -u ydl_api_ng -e $LOG_LEVEL

  cat <<EOT >>/app/supervisord_programmation.conf
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
fi

if [ "$DEBUG" == "DEBUG" ]; then
  echo ~~~ Launching DEBUG mode ~~~
  su ydl_api_ng -c "uvicorn main:app --reload --port 80 --host 0.0.0.0"
else
  su ydl_api_ng -c "python3 main.py"
fi
