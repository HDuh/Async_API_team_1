FROM python:3.10

WORKDIR /api_service

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY ./requirements.txt .

RUN pip install --upgrade pip --no-cache-dir \
    && pip install -r requirements.txt --no-cache-dir

COPY . .

CMD python ./src/waiter_elastic.py\
    && python ./src/waiter_redis.py\
    && python ./src/main.py
