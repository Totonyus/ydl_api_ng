# syntax=docker/dockerfile:1

FROM python:3.12.1-slim-bullseye
WORKDIR /app

ARG GIT_BRANCH=unknown GIT_REVISION=unknown DATE=unknown
ENV UID=1000 GID=1000 GIT_BRANCH=$GIT_BRANCH GIT_REVISION=$GIT_REVISION DATE=$DATE NB_WORKERS=5 LOG_LEVEL="info" DISABLE_REDIS='false'

RUN apt update && apt install ffmpeg dos2unix gcc g++ python3-dev -y rust cargo && apt-get autoremove && apt-get -y clean && rm -rf /var/lib/apt/lists/*

COPY *.py entrypoint.sh pip_requirements ./
COPY params/*.py params/*.ini params/userscript.js params/hooks_requirements ./setup/
COPY params/params_docker.ini ./setup/params.ini

RUN dos2unix * ./setup/*

RUN pip3 install -r pip_requirements

CMD ["bash", "/app/entrypoint.sh"]
