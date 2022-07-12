FROM python:3.10

WORKDIR /api_service

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY ./api_service/tests/functional/requirements.txt .

RUN pip install --upgrade pip --no-cache-dir \
    && pip install -r requirements.txt --no-cache-dir

COPY . /api_service

#ENTRYPOINT python src/waiters.py && pytest --disable-pytest-warnings tests
ENTRYPOINT python ./src/waiters.py && pytest --disable-pytest-warnings tests
