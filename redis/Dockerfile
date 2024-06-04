FROM redis:7.2-rc2-alpine
LABEL DESCIPTION="App4auctions Redis image"
LABEL MAINTAINER="alvaroo2302@gmail.com"

ARG REDIS_PASSWORD

ENV REDIS_PASSWORD=$REDIS_PASSWORD

EXPOSE 6379
CMD ["redis-server", "--loglevel", "debug", "--requirepass", "${REDIS_PASSWORD}"]
