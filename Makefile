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
	pip uninstall -y black
	pip uninstall -y click
	pip install black
	black app migrations --line-length=100 --check
	python -m pip install -r requirements.txt

flake8:
	# stop the build if there are Python syntax errors or undefined names
	flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
	# exit-zero treats all errors as warnings. The GitHub editor is 127 chars wide
	flake8 . --count \
		--exit-zero \
		--max-complexity=10 \
		--max-line-length=127 \
		--statistics \
		--per-file-ignores="migrations/versions/*.py:E266,E402"


doc:
	pip uninstall -y black
	pip uninstall -y click
	pip install black
	
	pip uninstall -y mkdocs-material
	pip uninstall -y requests
	pip install mkdocs-material

	# generate markdown documentation
	handsdown \
		--external `git config --get remote.origin.url` \
		--create-configs app \
		--theme material \
		--name "Mercury Sample Manager" \
		--output-path docsmd

	# convert to HTML documentation
	python -m mkdocs build

	# clean up
	rm .readthedocs.yml
	rm mkdocs.yml
	rm requirements.mkdocs.txt
	rm -rf docsmd

	# restore environment
	python -m pip install -r requirements.txt