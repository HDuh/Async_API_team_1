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
	docker-compose -f docker-compose.yml stop

start:
	docker-compose -f docker-compose.yml start

logs:
	docker-compose -f docker-compose.yml logs --tail=100

drop-state:
	docker-compose exec redis redis-cli FLUSHDB