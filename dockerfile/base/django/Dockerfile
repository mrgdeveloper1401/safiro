FROM docker.arvancloud.ir/python:3.14-slim

WORKDIR /home/app

COPY requirements.txt .
COPY packages ./packages

RUN pip install --index-url https://mirror2.chabokan.net/pypi/simple --upgrade pip && \
    pip install --no-index --find-links=/home/app/packages -r /home/app/requirements.txt