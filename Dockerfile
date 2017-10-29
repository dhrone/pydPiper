FROM hypriot/rpi-python

WORKDIR /app
ADD . /app
RUN apt-get update && apt-get install -y \
  python-dev \
  python-pip \
  python-smbus \
  libfreetype6-dev \
  libjpeg-dev \
  ttf-dejavu-core \
  build-essential \
  gcc \
  vim \
  iputils-ping \
  python-imaging && pip install --index-url=https://pypi.python.org/simple/ --upgrade pip && apt-get purge -y python-pip
RUN pip install -r requirements.txt
CMD /bin/bash
