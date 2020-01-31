# IU7Games Environment

FROM python:3.8-alpine
LABEL maintainer="IU7OG"

ENV PYTHONBUFFERED 1
ENV PATH $PATH:/scripts

RUN apk add --no-cache tzdata \
    && cp /usr/share/zoneinfo/Europe/Moscow /etc/localtime \
    && echo "Europe/Moscow" > /etc/timezone
RUN apk add --no-cache --virtual .tmp-build-deps \
    linux-headers g++

COPY cfg/image_cfg/requirements.txt /requirements.txt
RUN python -m pip install -r requirements.txt

COPY cfg/image_cfg/scripts /scripts
COPY cfg/image_cfg/libs/* /usr/lib/
COPY games/ /games

RUN mkdir /sandbox \
    && chmod -R o+w /sandbox

RUN adduser -D -h /deathstar imperialclone \
    && chmod -R o+x /scripts \
    && chmod -R o+x /games

WORKDIR /deathstar
USER imperialclone
