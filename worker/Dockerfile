## C worker 
FROM debian:bookworm-slim AS c-worker

RUN apt-get update && apt-get install -y gcc python3 python3-pip && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY ./c/worker.py /app
RUN python3 -m pip install --break-system-packages --no-cache-dir redis
CMD ["python3", "/app/worker.py"]

## C++ worker 
FROM debian:bookworm-slim AS cpp-worker

RUN apt-get update && apt-get install -y g++ python3 python3-pip && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY ./cpp/worker.py /app
RUN python3 -m pip install --break-system-packages --no-cache-dir redis
CMD ["python3", "/app/worker.py"]

## Java worker 
FROM eclipse-temurin:21-jdk AS java-worker 

RUN apt-get update && apt-get install -y python3 python3-pip && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY ./java/worker.py /app
RUN python3 -m pip install --break-system-packages --no-cache-dir redis
CMD ["python3", "/app/worker.py"]

## Python worker
FROM python:3.9-alpine AS python-worker 

RUN apk add --no-cache redis
WORKDIR /app
COPY ./python/worker.py /app
RUN pip install --no-cache-dir redis aioredis
CMD ["python3", "worker.py"]
