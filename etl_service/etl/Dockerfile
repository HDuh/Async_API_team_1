FROM python:3.9.6-slim as builder

WORKDIR /etl

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY requirements.txt /etl
RUN pip install -r /etl/requirements.txt --no-cache-dir
COPY . /etl

CMD python /etl/main_etl_process.py
