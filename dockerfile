# syntax=docker/dockerfile:1

FROM python:3.12-slim-bullseye
WORKDIR /app

ARG GIT_BRANCH=unknown GIT_REVISION=unknown DATE=unknown TARGET_ARCH='amd'
ENV UID=1000 GID=1000 GIT_BRANCH=$GIT_BRANCH GIT_REVISION=$GIT_REVISION DATE=$DATE NB_WORKERS=5 LOG_LEVEL="info" DISABLE_REDIS='false' TARGET_ARCH=$TARGET_ARCH
VOLUME ["/app/params", "/app/data", "/app/downloads", "/app/logs"]
EXPOSE 80

COPY --chmod=755 entrypoint.sh ./
COPY *.py pip_requirements ./
COPY params/*.py params/*.ini params/userscript.js params/hooks_requirements ./setup/
COPY params/params_docker.ini ./setup/params.ini

RUN if [ "$TARGET_ARCH" = "arm" ] ; then apt update && apt install gcc python3-dev -y; fi
RUN apt update && apt install wget unzip xz-utils -y && apt-get autoremove && apt-get -y clean && rm -rf /var/lib/apt/lists/*

RUN ARCH=$(arch | sed s/aarch64/linuxarm64/ | sed s/x86_64/linux64/) && \
wget https://github.com/yt-dlp/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-${ARCH}-gpl.tar.xz -O /ffmpeg.tar.xz && \
tar -xf /ffmpeg.tar.xz -C /tmp && \
install --mode=777 /tmp/ffmpeg-*/bin/ffmpeg /usr/bin && \
install --mode=777 /tmp/ffmpeg-*/bin/ffprobe /usr/bin && \
rm /ffmpeg.tar.xz /tmp/ffmpeg-* -rf

RUN wget https://github.com/denoland/deno/releases/latest/download/deno-x86_64-unknown-linux-gnu.zip -O /tmp/deno.zip && \
unzip /tmp/deno.zip -d /tmp && install --mode 777 /tmp/deno /usr/bin && \
rm /tmp/deno.zip -rf

RUN pip3 install --disable-pip-version-check -q --root-user-action=ignore -r pip_requirements

ENTRYPOINT ["/app/entrypoint.sh"]
