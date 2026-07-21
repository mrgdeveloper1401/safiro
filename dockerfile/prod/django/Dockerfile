FROM dj_safiro:1.0.0

WORKDIR /home/app

COPY .. .

RUN mkdir -p /home/app/static && \
    chmod +x ./scripts/*

EXPOSE 8000

ENTRYPOINT ["/bin/bash", "/home/app/scripts/start.sh"]