FROM docker.arvancloud.ir/python:3.14-alpine

WORKDIR /home/app

COPY requirements.txt .
COPY packages ./packages

RUN cp /dev/null /etc/apk/repositories && \
    echo "https://mirror.mobinhost.com/alpine/v3.22/main" >> /etc/apk/repositories && \
    echo "https://mirror.mobinhost.com/alpine/v3.22/community" >> /etc/apk/repositories && \
    apk update && \
    apk upgrade && \
    apk add bash postgresql-client curl gcc python3-dev musl-dev linux-headers graphviz && \
    pip install --index-url https://mirror2.chabokan.net/pypi/simple --upgrade pip && \
    pip install --no-index --find-links=./packages -r requirements.txt
#    pip install --index-url https://mirror2.chabokan.net/pypi/simple -r requirements.txt
