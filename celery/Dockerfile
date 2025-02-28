FROM python:3.11

WORKDIR /app

COPY ./app /app

RUN apt-get update && apt-get install -y chromium-driver && \
    pip install -r requirements.txt
