FROM python:3.10

WORKDIR /test_service

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY ./requirements.txt .

RUN pip install --upgrade pip --no-cache-dir \
    && pip install -r requirements.txt --no-cache-dir

COPY . /test_service

ENTRYPOINT python utils/waiters.py && pytest --disable-pytest-warnings src
