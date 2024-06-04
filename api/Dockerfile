FROM python:3.10.3

ENV TZ="Europe/Madrid"
ENV TIME_ZONE="Europe/Madrid"
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

WORKDIR /app

COPY requirements.txt /app/requirements.txt

RUN pip3 install --no-cache-dir --upgrade -r /app/requirements.txt && rm /app/requirements.txt

EXPOSE 5000

ADD . /app/

RUN mkdir /pics

ADD docker-entrypoint.sh /app
RUN chmod +x docker-entrypoint.sh

ENTRYPOINT ["/bin/bash", "./docker-entrypoint.sh"]

# One worker
CMD ["uvicorn", "main:app", "--proxy-headers", "--host", "0.0.0.0", "--port", "5000"]

# Multiple workers could be defined in a file called like `gunicorn_conf.py`
# CMD ["gunicorn", "-k", "uvicorn.workers.UvicornWorker", "-c", "gunicorn_conf.py", "main:app"]
