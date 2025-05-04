FROM python:3.12-slim

RUN apt-get update && apt-get upgrade -y
ENV PYTHONUNBUFFERED True

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app
WORKDIR /app
RUN useradd webserver && \
    mkdir -p /home/webserver && \
    chown -R webserver. /app /home/webserver
USER webserver

ENTRYPOINT [ "executable", "argone", "argtwo", "src.main:app" ]