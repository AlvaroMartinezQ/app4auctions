#!/bin/sh

sleep 5 # give some time for the database to init

alembic upgrade head

celery -A executor worker --loglevel=INFO &
celery -A executor flower --port=5555 &

exec "$@"
