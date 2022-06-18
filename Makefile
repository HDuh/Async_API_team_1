THIS_FILE := $(lastword $(MAKEFILE_LIST))

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

drop-state:
	docker-compose exec redis redis-cli FLUSHDB