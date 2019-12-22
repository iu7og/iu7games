# IU7Games Environment

FROM python:3.7-alpine

ENV PYTHONBUFFERED 1
ENV PATH $PATH:/scripts

RUN apk add --no-cache \
    linux-headers \
    git \
    gcc \
    musl-dev \
    lcov --repository=http://dl-cdn.alpinelinux.org/alpine/edge/testing \
    tzdata \
    python3-dev --repository=http://dl-cdn.alpinelinux.org/alpine/edge/main \
    \
    && cp /usr/share/zoneinfo/Europe/Moscow /etc/localtime \
    && echo "Europe/Moscow" > /etc/timezone

COPY image/requirements.txt /requirements.txt
RUN python -m pip install -r requirements.txt \
    && rm -f requirements.txt

COPY image/scripts /scripts
COPY image/libs/* /usr/lib/
COPY games/ /games

RUN mkdir /sandbox \
    && chmod -R o+w /sandbox

RUN adduser -D -h /deathstar imperialclone \
    && chmod -R o+x /scripts \
    && chmod -R o+x /games

WORKDIR /deathstar
USER imperialclone

CMD ["bash"]
