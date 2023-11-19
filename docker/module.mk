down:
	docker compose -f docker/docker-compose.yml down

build: down
	docker compose -f docker/docker-compose.yml build web

run:
	docker compose -f docker/docker-compose.yml up

down-dev:
	docker compose -f docker/docker-compose-dev.yml down

build-dev: down-dev
	docker compose -f docker/docker-compose-dev.yml build web-dev

test-dev:
	docker compose -f docker/docker-compose-dev.yml exec web-dev python -m pytest

watchman-rule:
	watchman --logfile=/tmp/watchman.log watch-del-all
	watchman watch ./app
	watchman watch ./js/src
	cat docker/watchman-py.json | watchman -j
	cat docker/watchman-js.json | watchman -j
	tail -F /tmp/watchman.log

watchman-rules:
	watchman trigger-list ./app
	watchman trigger-list ./js/src

run-dev:
	docker compose -f docker/docker-compose-dev.yml up

shell-dev:
	docker compose -f docker/docker-compose-dev.yml exec web-dev bash

logs:
	docker compose -f docker/docker-compose.yml logs -f
