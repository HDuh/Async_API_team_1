THIS_FILE := $(lastword $(MAKEFILE_LIST))

build:
	docker-compose -f docker-compose.yml build $(c)

up:
	docker-compose -f docker-compose.yml up -d

down:
	docker-compose -f docker-compose.yml down

run:
	docker-compose -f docker-compose.yml up -d --build

stop:
	docker-compose -f docker-compose.yml stop

start:
	docker-compose -f docker-compose.yml start

logs:
	docker-compose -f docker-compose.yml logs --tail=100

drop-state:
	docker-compose -f docker-compose.yml exec redis redis-cli FLUSHDB