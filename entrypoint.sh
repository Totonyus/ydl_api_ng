#!/bin/bash

echo ~~~ ydl_api_ng
echo ~~~ Revision : $GIT_BRANCH - $GIT_REVISION
echo ~~~ Docker image generated : $DATE

mkdir -p /app/logs /app/downloads /app/params /app/tmp /app/data /root/yt-dlp-plugins /app/cookies/ /home/ydl_api_ng

getent group $GID >/dev/null
if [ ! $? -eq 0 ]; then
  addgroup --gid $GID ydl_api_ng
fi

getent passwd $UID >/dev/null
if [ ! $? -eq 0 ]; then
  useradd --uid $UID --gid $GID ydl_api_ng -b /home/ydl_api_ng
fi

# If params.ini exists, assume setup has been run. Don't copy extra files the user may have removed.
if [ ! -e '/app/params/params.ini' ]; then
  cp -n /app/setup/params.ini /app/params/
fi

if [ ! -e /app/data/database.json ]; then
  touch /app/data/database.json
fi

if [ "$FORCE_YTDLP_VERSION" == "" ]; then
  echo --- Upgrade yt-dlp to the latest version ---
  pip3 install yt-dlp[default,curl-cffi] yt-dlp-ejs --upgrade --disable-pip-version-check -q --root-user-action=ignore
else
  echo --- Force yt-dlp version $FORCE_YTDLP_VERSION ---
  pip3 install --disable-pip-version-check -q --root-user-action=ignore yt-dlp-ejs yt-dlp[default,curl-cffi]==$FORCE_YTDLP_VERSION --force-reinstall
fi

echo --- Installing hooks requirements ---
if [ -e /app/params/hooks_requirements ]; then
  pip3 install --disable-pip-version-check -q --root-user-action=ignore -r /app/params/hooks_requirements
else
  pip3 install --disable-pip-version-check -q --root-user-action=ignore -r /app/setup/hooks_requirements
fi

chown -R $UID:$GID /app
chown $UID:$GID /home/ydl_api_ng /root/yt-dlp-plugins
chmod a+x /root/ entrypoint.sh

if [ "$DISABLE_REDIS" == "false" ]; then
  if [ -e /app/params/workers.ini ]; then
    supervisord -c /app/params/workers.ini
  else
    supervisord -c /app/setup/workers.ini
  fi
fi

if [ "$DEBUG" == "DEBUG" ]; then
  echo ~~~ Launching DEBUG mode ~~~
  su "$(id -un $UID)" -c "uvicorn main:app --reload --port 80 --host 0.0.0.0"
else
  su "$(id -un $UID)" -c "python3 main.py"
fi
