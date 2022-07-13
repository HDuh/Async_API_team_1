THIS_FILE := $(lastword $(MAKEFILE_LIST))
.PHONY: help build up start down destroy stop restart logs logs-api ps login-timesc

help:
	make -pRrq  -f $(THIS_FILE) : 2>/dev/null | awk -v RS= -F: '/^# File/,/^# Finished Make data base/ {if ($$1 !~ "^[#.]") {print $$1}}' | sort | egrep -v -e '^[^[:alnum:]]' -e '^$@$$'

build:
	docker-compose build $(c)

up:
	docker-compose up -d $(c)

down:
	docker-compose down

run:
	docker-compose up -d --build

destroy:
	docker-compose down -v $(c)

stop:
	docker-compose stop

start:
	docker-compose start

logs:
	docker-compose logs --tail=100

tests_run:
	 docker-compose -f api_service/tests/functional/docker-compose.yml build\
 	&& docker-compose -f api_service/tests/functional/docker-compose.yml up --abort-on-container-exit tests\
 	&& docker-compose -f api_service/tests/functional/docker-compose.yml down

tests_up:
	docker-compose -f api_service/tests/functional/docker-compose.yml build\
 	&& docker-compose -f api_service/tests/functional/docker-compose.yml up --abort-on-container-exit tests

tests_down:
	docker-compose -f api_service/tests/functional/docker-compose.yml down

drop-state:
	docker-compose exec redis redis-cli FLUSHDB