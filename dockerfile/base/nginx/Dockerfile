FROM docker.arvancloud.ir/nginx:latest

RUN mkdir -p /var/www/static/ \
    /etc/letsencrypt/ \
    /var/lib/letsencrypt/ && \
    rm -f /etc/apt/sources.list.d/debian.sources && \
    printf "Types: deb\nURIs: https://mirror.mobinhost.com/debian\nSuites: trixie\nComponents: main\n" \
      > /etc/apt/sources.list.d/debian.sources && \
    apt update && \
    apt install -y bash curl openssl && \
    rm -rf /var/lib/apt/lists/*
