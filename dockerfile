# syntax=docker/dockerfile:1

FROM python:3.12-slim-bullseye
WORKDIR /app

ARG GIT_BRANCH=unknown GIT_REVISION=unknown DATE=unknown TARGET_ARCH='amd'
ENV UID=1000 GID=1000 GIT_BRANCH=$GIT_BRANCH GIT_REVISION=$GIT_REVISION DATE=$DATE NB_WORKERS=5 LOG_LEVEL="info" DISABLE_REDIS='false' TARGET_ARCH=$TARGET_ARCH
VOLUME ["/app/params", "/app/data", "/app/downloads", "/app/logs"]
EXPOSE 80

COPY --chmod=755 entrypoint.sh ./
COPY *.py pip_requirements_$TARGET_ARCH ./
COPY params/*.py params/*.ini params/userscript.js params/hooks_requirements ./setup/
COPY params/params_docker.ini ./setup/params.ini

RUN if [ "$TARGET_ARCH" = "arm" ] ; then apt update && apt install gcc python3-dev -y && apt-get autoremove && apt-get -y clean && rm -rf /var/lib/apt/lists/*; fi

RUN apt update && apt install wget xz-utils -y

RUN ARCH=$(arch | sed s/aarch64/arm64/ | sed s/x86_64/amd64/) && \
wget https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-${ARCH}-static.tar.xz -O /ffmpeg.tar.xz && \
tar -xf /ffmpeg.tar.xz -C /tmp && \
install --mode=777 /tmp/ffmpeg-*-static/ffmpeg /usr/bin && \
install --mode=777 /tmp/ffmpeg-*-static/ffprobe /usr/bin && \
rm /ffmpeg.tar.xz /tmp/ffmpeg-*-static -rf && \
pip3 install --disable-pip-version-check -q --root-user-action=ignore -r pip_requirements_$TARGET_ARCH

ENTRYPOINT ["/app/entrypoint.sh"]
