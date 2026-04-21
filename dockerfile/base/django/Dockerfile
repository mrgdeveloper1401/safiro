FROM docker.arvancloud.ir/python:3.14-alpine

COPY . .

RUN cp /dev/null /etc/apk/repositories && \
    echo "https://mirror.mobinhost.com/alpine/v3.22/main" >> /etc/apk/repositories && \
    echo "https://mirror.mobinhost.com/alpine/v3.22/community" >> /etc/apk/repositories && \
    apk update && \
    apk upgrade && \
    apk add --no-cache bash postgresql-client curl gcc python3-dev musl-dev linux-headers graphviz && \
    pip install --index-url https://package-mirror.liara.ir/repository/pypi/ --upgrade pip && \
    pip install --index-url https://package-mirror.liara.ir/repository/pypi/ -r requirements.txt
