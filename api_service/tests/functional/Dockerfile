FROM python:3.10-buster

WORKDIR /api_service

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PYTEST_RUN_CONFIG True

COPY ./tests/functional/requirements.txt tests/functional/

RUN pip install --upgrade pip --no-cache-dir\
    && pip install -r tests/functional/requirements.txt --no-cache-dir

COPY ../../ .

ENTRYPOINT python src/waiter_elastic.py\
    && python src/waiter_redis.py\
    && python -m pytest -c tests/functional/pytest.ini
