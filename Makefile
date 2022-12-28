install-dependencies:
	python -m pip install ${PIP_OPTIONS} --upgrade pip
	pip install ${PIP_OPTIONS} -r requirements-dev.txt
	pip install ${PIP_OPTIONS} -r requirements.txt

build-dev: down
	docker compose -f docker/docker-compose.yml build web-dev

test-dev:
	docker compose -f docker/docker-compose.yml exec web-dev python -m pytest

run-dev:
	docker compose -f docker/docker-compose.yml up web-dev -d
	watchman-make -p 'app/**/*.py' -s 1 --run 'touch uwsgi-reload'

shell-dev:
	docker compose -f docker/docker-compose.yml exec web-dev bash

down:
	docker compose -f docker/docker-compose.yml down

logs:
	docker compose -f docker/docker-compose.yml logs -f

test:
	coverage run -m pytest

coverage-report: test
	coverage html

black:
	# workaround for https://github.com/psf/black/issues/3111
	python -m pip install --upgrade -r requirements-dev.txt > /dev/null
	black .
	python -m pip install -r requirements.txt > /dev/null

black-check:
	# workaround for https://github.com/psf/black/issues/3111
	python -m pip install --upgrade -r requirements-dev.txt > /dev/null
	black . --check
	python -m pip install -r requirements.txt > /dev/null

flake8:
	# stop the build if there are Python syntax errors or undefined names
	flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics

	rm ./reports/flake8/flake8stats.txt || true
	flake8 . \
		--exit-zero \
		--format=html --htmldir ./reports/flake8/ \
		--tee --output-file ./reports/flake8/flake8stats.txt

flake8-badge:
	printf " \
		\rimport os\n \
		\rfrom genbadge.utils_flake8 import get_flake8_badge, get_flake8_stats\n \
		\rbadge = get_flake8_badge(get_flake8_stats('./reports/flake8/flake8stats.txt'))\n \
		\rprint(f'{badge.right_txt}@{badge.color}')\n \
		\r\n" | python

doc:
	# install dev requirements
	pip install --upgrade -r requirements-dev.txt > /dev/null

	# generate markdown documentation
	handsdown \
		--branch master \
		--external `git config --get remote.origin.url` \
		--cleanup \
		--create-configs \
		--theme material \
		--name "Mercury Sample Manager" \
		--output-path docsmd \
		app

	# replace main page of documentation
	cp README.md docsmd/README.md

	# convert to HTML documentation
	python -m mkdocs build

	# restore environment
	python -m pip install -r requirements.txt > /dev/null