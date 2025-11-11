FROM docker.arvancloud.ir/nginx:1.29-alpine

RUN cp /dev/null /etc/apk/repositories && \
    echo "https://mirror.mobinhost.com/alpine/v3.22/main" >> /etc/apk/repositories && \
    echo "https://mirror.mobinhost.com/alpine/v3.22/community" >> /etc/apk/repositories && \
    apk update && \
    apk upgrade && \
    apk add bash curl openssl python3-certbot

RUN mkdir -p /var/www/static/ && \
    mkdir -p /etc/letsencrypt/live/servername.ir/

COPY /base_image/prod/nginx/nginx.conf /etc/nginx/nginx.conf