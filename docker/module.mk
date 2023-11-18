build: down
	docker compose -f docker/docker-compose.yml build web

run:
	docker compose -f docker/docker-compose.yml up

build-dev: down
	docker compose -f docker/docker-compose-dev.yml build web-dev

test-dev:
	docker compose -f docker/docker-compose-dev.yml exec web-dev python -m pytest

watchman-rule:
	watchman watch ./app
	cat docker/watchman.json | watchman -j
	tail -F /dev/null

run-dev:
	docker compose -f docker/docker-compose-dev.yml up

shell-dev:
	docker compose -f docker/docker-compose-dev.yml exec web-dev bash

down:
	docker compose -f docker/docker-compose.yml down

logs:
	docker compose -f docker/docker-compose.yml logs -f
