FROM python:3.12-slim

RUN apt-get update && apt-get upgrade -y \
    && apt-get install -y gcc librrd-dev python3-dev libpango1.0-dev libxml2-dev

ENV PYTHONUNBUFFERED True

COPY . /app
WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements

RUN useradd ipfix-webserver \
    && mkdir -p /home/ipfix-webserver \
    && mkdir -p /var/ipfix-webserver/admin \
    && mkdir -p /var/ipfix-webserver/tenants \
    && chown -R ipfix-webserver: /app /home/ipfix-webserver /var/ipfix-webserver
USER ipfix-webserver

ENTRYPOINT [ "sh" ]