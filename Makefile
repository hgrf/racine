install-dependencies:
	python -m pip install ${PIP_OPTIONS} --upgrade pip
	pip install ${PIP_OPTIONS} -r requirements-dev.txt
	pip install ${PIP_OPTIONS} -r requirements.txt

install-bootstrap-toc:
	rm -f app/static/bootstrap-toc.min.css
	rm -f app/static/bootstrap-toc.min.js

	rm -rf /tmp/bootstrap-toc
	git clone -b v0.4.1 --depth 1 \
		git@github.com:afeld/bootstrap-toc.git \
		/tmp/bootstrap-toc
	cp /tmp/bootstrap-toc/dist/bootstrap-toc.min.css app/static/bootstrap-toc.min.css
	cp /tmp/bootstrap-toc/dist/bootstrap-toc.min.js app/static/bootstrap-toc.min.js
	rm -rf /tmp/bootstrap-toc

install-jquery-ui:
	rm -f app/static/jquery-ui.min.css
	rm -f app/static/jquery-ui.min.js

	wget -O jquery-ui.zip https://jqueryui.com/resources/download/jquery-ui-1.11.4.zip
	rm -rf /tmp/jquery-ui-*
	unzip -d /tmp jquery-ui.zip
	rm jquery-ui.zip

	cp /tmp/jquery-ui-*/jquery-ui.min.css app/static/jquery-ui.min.css
	cp /tmp/jquery-ui-*/jquery-ui.min.js app/static/jquery-ui.min.js
	rm -rf /tmp/jquery-ui-*

install-lightbox:
	rm -rf app/static/lightbox2-master

	git clone -b v2.8.2 --depth 1 \
		git@github.com:lokesh/lightbox2.git \
		app/static/lightbox2-master

	rm -rf app/static/lightbox2-master/.git

install-mathjax:
	rm -rf app/static/mathjax

	git clone -b 2.7.1 --depth 1 \
		git@github.com:mathjax/MathJax.git \
		app/static/mathjax

	rm -rf app/static/mathjax/.git

install-typeahead:
	rm -rf app/static/typeahead.js

	rm -rf /tmp/typeahead.js
	git clone -b v0.11.1 --depth 1 \
		git@github.com:twitter/typeahead.js.git \
		/tmp/typeahead.js
	cp -r /tmp/typeahead.js/dist app/static/typeahead.js
	rm -rf /tmp/typeahead.js

	# c.f. https://github.com/HolgerGraef/MSM/commit/19fc41b1797112d2980b08ad53d1f945d9e36b17
	#      https://github.com/twitter/typeahead.js/issues/1218
	#      https://github.com/HolgerGraef/MSM/commit/2d892a4a2f6a9bdb9465730a64670277e35698a8
	git apply patches/typeahead.patch

	wget -O yuicompressor.jar https://github.com/yui/yuicompressor/releases/download/v2.4.8/yuicompressor-2.4.8.jar
	java -jar yuicompressor.jar \
		--type js \
		--charset utf-8 \
		app/static/typeahead.js/typeahead.bundle.js \
		> app/static/typeahead.js/typeahead.bundle.min.js
	rm yuicompressor.jar

install-js-dependencies: install-bootstrap-toc install-jquery-ui install-lightbox install-mathjax install-typeahead
	echo ""

clean-js-dependencies:
	rm -rf app/static/lightbox2-master
	rm -rf app/static/mathjax
	rm -rf app/static/typeahead.js

build: down
	docker compose -f docker/docker-compose.yml build web

run:
	docker compose -f docker/docker-compose.yml up web

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

	# make sure flake8 report folder exists
	mkdir -p ./reports/flake8

	# make sure no previous report exists (otherwise flake8 will append to it)
	rm ./reports/flake8/flake8stats.txt || true

	# run flake8 and generate report
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