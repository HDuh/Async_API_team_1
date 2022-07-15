FROM python:3.10-buster

WORKDIR /usr/src/api_service

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1


COPY ./requirements.txt .

RUN pip install --upgrade pip --no-cache-dir\
    && pip install -r requirements.txt --no-cache-dir

COPY . .

ENTRYPOINT python src/waiter_elastic.py\
    && python src/waiter_redis.py\
    && gunicorn src.main:app -w 9 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000