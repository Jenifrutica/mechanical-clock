FROM python:3.12-alpine

RUN apk add --no-cache ttyd

RUN adduser -D -H -u 10001 clockuser

WORKDIR /app

COPY *.py ./

ENV PORT=8080
EXPOSE 8080

USER clockuser

CMD ["sh", "-c", "exec ttyd -W -p ${PORT} -i 0.0.0.0 -m 4 -O -t fontSize=24 python3 main.py"]
