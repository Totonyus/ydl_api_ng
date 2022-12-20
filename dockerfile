# syntax=docker/dockerfile:1

FROM python:3.9-slim-buster
WORKDIR /app

ARG GIT_BRANCH=unknown GIT_REVISION=unknown DATE=unknown
ENV UID=1000 GID=1000 GIT_BRANCH=$GIT_BRANCH GIT_REVISION=$GIT_REVISION DATE=$DATE NB_WORKERS=5 LOG_LEVEL="info" DISABLE_REDIS='false'

RUN apt update && apt install ffmpeg dos2unix -y && apt-get autoremove && apt-get -y clean && rm -rf /var/lib/apt/lists/*

COPY config_manager.py download_manager.py main.py process_utils.py entrypoint.sh pip_requirements defaults.py programmation_class.py programmation_persistence_manager.py programmation_daemon.py ./
COPY params/ydl_api_hooks.py params/postprocessor_hooks.py params/progress_hooks.py params/params.ini params/params_metadata.ini params/params.sample.ini params/userscript.js params/hooks_requirements ./setup/
COPY params/params_docker.ini ./setup/params.ini

RUN dos2unix * ./setup/*

RUN pip3 install -r pip_requirements

CMD ["bash", "/app/entrypoint.sh"]
