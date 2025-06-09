FROM python:3.12-slim

RUN apt-get update && apt-get upgrade -y \
    && apt-get install -y gcc librrd-dev python3-dev libpango1.0-dev libxml2-dev

ENV PYTHONUNBUFFERED True

COPY . /app
WORKDIR /app

RUN pip install --no-cache-dir -r requirements.txt

RUN useradd ipfix-webserver \
    && mkdir -p /var/ipfix-webserver/service \
    && mkdir -p /var/ipfix-webserver/admin \
    && mkdir -p /var/ipfix-webserver/tenants \
    && chown -R ipfix-webserver: /app /var/ipfix-webserver
USER ipfix-webserver

ENTRYPOINT ["python", "src/cmd/main.py"]