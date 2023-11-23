all: update build up

update:
	git pull

build:
	docker-compose -f docker-compose.prod.yml down
	docker-compose -f docker-compose.prod.yml build

up:
	docker-compose -f docker-compose.prod.yml up
	docker-compose -f docker-compose.prod.yml stop
	docker-compose -f docker-compose.prod.yml up
