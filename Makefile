install-dependencies:
	python -m pip install ${PIP_OPTIONS} --upgrade pip
	pip install ${PIP_OPTIONS} -r requirements-dev.txt
	pip install ${PIP_OPTIONS} -r requirements.txt

build-dev: down
	docker compose -f misc/docker-compose.yml build web-dev

run-dev:
	docker compose -f misc/docker-compose.yml up web-dev -d
	watchman-make -p 'app/**/*.py' -s 1 --run 'touch uwsgi-reload'

down:
	docker compose -f misc/docker-compose.yml down

logs:
	docker compose -f misc/docker-compose.yml logs -f

copy-bootstrap:
	mkdir -p /static/
	git clone -b 3.3.7.1 --depth 1 https://github.com/mbr/flask-bootstrap.git
	ls -la ./flask-bootstrap
	mv ./flask-bootstrap/flask_bootstrap/static /static/bootstrap
	rm -rf flask-bootstrap

test:
	coverage run -m pytest

coverage-report: test
	coverage html

black:
	# workaround for https://github.com/psf/black/issues/3111
	pip uninstall -y black
	pip uninstall -y click
	pip install black
	pip install click
	black app migrations --line-length=100 --check
	pip install Click==7.0	# see requirements.txt

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
	pip install click
	
	pip uninstall -y mkdocs-material
	pip uninstall -y requests
	pip install mkdocs-material
	pip install requests

	# Generate documentation that points to main branch
	# do not use custom output location, as `GitHub Pages`
	# works only with `docs` directory
	handsdown --external `git config --get remote.origin.url` --create-configs app --theme material -n "Mercury Sample Manager" -o docsmd
	# generate html files to docs folder
	python -m mkdocs build

	pip install Click==7.0	# see requirements.txt
	pip install requests==2.22.0  # see requirements.txt