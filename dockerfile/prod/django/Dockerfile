FROM safiro:2.0.0

WORKDIR /home/app

COPY .. .

RUN chmod +x ./scripts/*

EXPOSE 8000

ENTRYPOINT ["./scripts/start.sh"]