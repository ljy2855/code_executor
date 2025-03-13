## C worker
FROM gcc:14.2.0 AS c-worker

RUN apt-get update && apt-get install -y python3 python3-pip
WORKDIR /app
COPY ./c/worker.py /app
RUN pip install --no-cache-dir --break-system-packages redis
CMD ["python3", "/app/worker.py"]

## C++ worker
FROM gcc:14.2.0 AS cpp-worker

RUN apt-get update && apt-get install -y python3 python3-pip
WORKDIR /app
COPY ./cpp/worker.py /app
RUN pip install --no-cache-dir --break-system-packages redis
CMD ["python3", "/app/worker.py"]

## Java worker
FROM openjdk:21-slim-bullseye AS java-worker

RUN apt-get update && apt-get install -y python3 python3-pip
WORKDIR /app
COPY ./java/worker.py /app
RUN pip install --no-cache-dir redis
CMD ["python3", "/app/worker.py"]

## Python worker
FROM python:3.9-slim AS python-worker

RUN apt-get update && apt-get install -y redis-tools
WORKDIR /app
COPY ./python/* /app
RUN pip install --no-cache-dir -r requirements.txt
CMD ["python", "worker.py"]
