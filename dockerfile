# syntax=docker/dockerfile:1

FROM python:3.12-slim-bullseye
WORKDIR /app

ARG GIT_BRANCH=unknown GIT_REVISION=unknown DATE=unknown TARGET_ARCH='amd'
ENV UID=1000 GID=1000 GIT_BRANCH=$GIT_BRANCH GIT_REVISION=$GIT_REVISION DATE=$DATE NB_WORKERS=5 LOG_LEVEL="info" DISABLE_REDIS='false' TARGET_ARCH=$TARGET_ARCH
VOLUME ["/app/params", "/app/data", "/app/downloads", "/app/logs"]
EXPOSE 80

RUN pip install static-ffmpeg && static_ffmpeg; ln -s /usr/local/lib/python3.12/site-packages/static_ffmpeg/bin/linux/ffmpeg /usr/bin/ffmpeg
RUN if [ "$TARGET_ARCH" = "arm" ] ; then apt install gcc python3-dev -y && apt-get autoremove && apt-get -y clean && rm -rf /var/lib/apt/lists/*; fi

COPY --chmod=755 entrypoint.sh ./
COPY *.py pip_requirements_$TARGET_ARCH ./
COPY params/*.py params/*.ini params/userscript.js params/hooks_requirements ./setup/
COPY params/params_docker.ini ./setup/params.ini

RUN pip3 install -r pip_requirements_$TARGET_ARCH

ENTRYPOINT ["/app/entrypoint.sh"]
