#!/bin/bash

echo ~~~ ydl_api_ng
echo ~~~ Revision : $GIT_BRANCH - $GIT_REVISION
echo ~~~ Docker image generated : $DATE

mkdir -p /app/logs /app/downloads /app/params
cp -n /app/setup/* /app/params/

pip3 install yt-dlp --upgrade
pip3 install -r /app/params/hooks_requirements

addgroup --gid $GID ydl_api_ng && useradd --uid $UID --gid ydl_api_ng ydl_api_ng

chown $UID:$GID /app/logs
chown $UID:$GID /app/downloads

su ydl_api_ng -c "python3 main.py"
