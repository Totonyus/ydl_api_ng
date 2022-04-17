#!/bin/bash

cp -n /app/setup/* /app/params/

addgroup --gid $GID ydl_api_ng && useradd --uid $UID --gid ydl_api_ng ydl_api_ng

pip3 install yt-dlp --upgrade
pip3 install -r /app/params/hooks_requirements

mkdir -p /app/logs /app/downloads
chown $UID:$GID /app/logs /app/downloads
chown $UID:$GID /app/downloads

su ydl_api_ng -c "python3 main.py"
