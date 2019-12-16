FROM opendatacube/datacube-core:latest

# Install the heavy stuff first
RUN apt-get update && apt-get install -y gfortran \
    && rm -rf /var/lib/apt/lists/*
RUN pip3 install git+https://github.com/GeoscienceAustralia/fc --no-deps --global-option=build --global-option='--executable=/usr/bin/env python3'  \
    && rm -rf $HOME/.cache/pip

RUN pip3 install git+https://github.com/GeoscienceAustralia/wofs --no-deps --global-option=build --global-option='--executable=/usr/bin/env python3'

ENV APPDIR=/tmp/code/
RUN mkdir -p $APPDIR
COPY requirements.txt $APPDIR/
WORKDIR $APPDIR

RUN pip3 install --upgrade pip \
    && pip3 install -r requirements.txt \
    && rm -rf $HOME/.cache/pip

COPY . $APPDIR
RUN pip3 install . \
    && rm -rf $HOME/.cache/pip

# Set up an entrypoint that drops environment variables into the config file
ENTRYPOINT ["docker-entrypoint.sh"]

CMD ["datacube-alchemist", "--help"]
