#!/bin/bash

echo ~~~ ydl_api_ng
echo ~~~ Revision : $GIT_BRANCH - $GIT_REVISION
echo ~~~ Docker image generated : $DATE

mkdir -p /app/logs /app/downloads /app/params /app/tmp /app/data /root/yt-dlp-plugins /app/cookies/ /home/ydl_api_ng

getent group $GID >/dev/null
if [ $? -eq 0 ]; then
  groupmod $(id --name --group $GID) -n ydl_api_ng
else
  addgroup --gid $GID ydl_api_ng
fi

getent passwd $UID >/dev/null
if [ $? -eq 0 ]; then
  usermod $(id --name --user $UID) -l ydl_api_ng
else
  useradd --uid $UID --gid ydl_api_ng ydl_api_ng
fi

chown -R $UID:$GID /app
chown $UID:$GID /home/ydl_api_ng /root/yt-dlp-plugins
chmod a+x /root/ entrypoint.sh

# If params.ini exists, assume setup has been run. Don't copy extra files the user may have removed.
if [ ! -e '/app/params/params.ini' ]; then
  cp -n /app/setup/* /app/params/
fi

if [ ! -e /app/data/database.json ]; then
  touch /app/data/database.json
fi

if [ "$FORCE_YTDLP_VERSION" == "" ]; then
  echo --- Upgrade yt-dlp to the latest version ---
  pip3 install yt-dlp --upgrade --disable-pip-version-check -q --root-user-action=ignore
else
  echo --- Force yt-dlp version $FORCE_YTDLP_VERSION ---
  pip3 install --disable-pip-version-check -q --root-user-action=ignore yt-dlp==$FORCE_YTDLP_VERSION --force-reinstall
fi

pip3 install --disable-pip-version-check -q --root-user-action=ignore -r /app/params/hooks_requirements

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

  cat <<EOT >>/app/supervisord_slow_workers.conf
[supervisord]

[program:worker]
command=rq worker ydl_api_ng_slow -u "redis://ydl_api_ng_redis:6379"
process_name=%(program_name)s-%(process_num)s
numprocs=1
directory=.
stopsignal=TERM
autostart=true
autorestart=true
user=$UID
EOT

  supervisord -c /app/supervisord_slow_workers.conf -l /app/logs/supervisord_slow_workers.log -j /app/tmp/pid_api -u ydl_api_ng -e $LOG_LEVEL

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
