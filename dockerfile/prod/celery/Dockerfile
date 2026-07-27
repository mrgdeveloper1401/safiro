FROM dj_safiro:1.0.0

WORKDIR /home/app

COPY . .

ENTRYPOINT ["celery", "-A", "base", "worker", "-l", "INFO"]