FROM docker.arvancloud.ir/python:3.14-slim

WORKDIR /home/app

COPY requirements.txt .
#COPY packages ./packages

RUN rm /etc/apt/sources.list.d/* && \
    echo "deb https://mirror.mobinhost.com/debian/ trixie main" > "/etc/apt/sources.list.d/debian.list" && \
    apt update &&  \
    apt upgrade -y && \
    apt install curl vim procps net-tools -y && \
    pip config --user set global.index https://mirror-pypi.runflare.com/simple && \
    pip config --user set global.index-url https://mirror-pypi.runflare.com/simple && \
    pip config --user set global.trusted-host mirror-pypi.runflare.com && \
    pip install  -r requirements.txt && \
    rm -rf /var/lib/apt/lists/*
