# IU7Games Environment

FROM python:3.7-alpine

ENV PYTHONBUFFERED 1

COPY ./requirements.txt /requirements.txt

RUN apk add --no-cache \
    git \
    gcc \
    musl-dev \
    lcov --repository=http://dl-cdn.alpinelinux.org/alpine/edge/testing \
    tzdata \
    \
    && cp /usr/share/zoneinfo/Europe/Moscow /etc/localtime \
    && echo "Europe/Moscow" > /etc/timezone
RUN python -m pip install -r requirements.txt \
    && rm -f requirements.txt

RUN adduser -D -h /deathstar imperialclone
WORKDIR /deathstar
USER imperialclone

CMD ["bash"]
