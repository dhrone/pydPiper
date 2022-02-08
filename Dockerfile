FROM arm32v7/python:2-alpine

WORKDIR /app
ADD requirements.txt /app
RUN apk update && apk add \
  python-dev \
  py-pip \
  py-smbus \
  freetype-dev \
  jpeg-dev \
  ttf-dejavu \
  build-base \
  gcc \
  linux-headers \ 
  py-pillow && rm -rf /var/cache/apk/*
RUN pip install -r requirements.txt
CMD /bin/bash
