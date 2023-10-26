RACINE_VERSION="v0.1.0"
RACINE_API_VERSION="0.1.0"

# TODO: for now, if you want to add an include, do not forget to update the Dockerfile
include .github/workflows/module.mk
include app/static/module.mk
include docker/module.mk
include docs/module.mk
include site/module.mk

.PHONY: version
version:
	@echo ${RACINE_VERSION}

.PHONY: api-version
api-version:
	@echo ${RACINE_API_VERSION}

install-dependencies:
	python -m pip install ${PIP_OPTIONS} --upgrade pip
	pip install ${PIP_OPTIONS} -r requirements-dev.txt
	pip install ${PIP_OPTIONS} -r requirements.txt

api-spec:
	python patches/generate-api-spec.py
	cat patches/api.yaml >> docs/api.yaml

api-client: api-spec
	rm -rf js/src/api
	mkdir -p build
	wget https://repo1.maven.org/maven2/org/openapitools/openapi-generator-cli/6.2.1/openapi-generator-cli-6.2.1.jar \
		-O build/openapi-generator-cli.jar
	
	java -jar build/openapi-generator-cli.jar generate \
		-i docs/api.yaml -g javascript -p modelPropertyNaming=original -o js/src/api

install-mathjax:
	rm -rf app/static/mathjax

	git clone -b 2.7.1 --depth 1 \
		https://github.com/mathjax/MathJax.git \
		app/static/mathjax

	rm -rf app/static/mathjax/.git

install-js-dependencies: install-mathjax api-client
	mkdir -p app/static/css
	mkdir -p app/static/fonts

	# install typeahead.js
	wget -O js/src/typeahead/typeahead.bundle.js \
		https://raw.githubusercontent.com/twitter/typeahead.js/v0.11.1/dist/typeahead.bundle.js
	wget -O js/src/typeahead/bloodhound.js \
		https://raw.githubusercontent.com/twitter/typeahead.js/v0.11.1/dist/bloodhound.js
	wget -O app/static/css/typeahead.css \
		https://raw.githubusercontent.com/hyspace/typeahead.js-bootstrap3.less/v0.2.3/typeahead.css
	# c.f. https://github.com/hgrf/racine/commit/19fc41b1797112d2980b08ad53d1f945d9e36b17
	#      https://github.com/twitter/typeahead.js/issues/1218
	#      https://github.com/hgrf/racine/commit/2d892a4a2f6a9bdb9465730a64670277e35698a8
	git apply patches/typeahead.patch

	# install jeditable
	wget -O js/src/jquery-plugins/jquery.jeditable.js \
		https://sscdn.net/js/jquery/latest/jeditable/1.7.1/jeditable.js
	# c.f. https://github.com/hgrf/racine/commit/89d8b57e795ccfbeb73dc18faecc1d0016a8a008#diff-5f8e3a2bd35e7f0079090b176e06d0568d5c8e4468c0febbfa61014d72b16246
	git apply patches/jquery.jeditable.patch

	cd js && npm version --allow-same-version ${RACINE_VERSION}
	cd js && npm install && npx rollup -c

	cp js/node_modules/bootstrap/dist/css/bootstrap.min.css app/static/css/bootstrap.min.css
	cp js/node_modules/bootstrap/dist/fonts/* app/static/fonts/

	cp js/node_modules/tocbot/dist/tocbot.css app/static/css/tocbot.css

	cp js/node_modules/lightbox2/dist/css/lightbox.css app/static/css/lightbox.css
	cp js/node_modules/lightbox2/dist/images/* app/static/images/

run-no-docker:
	flask run --debug

test:
	coverage run -m pytest

coverage-report: test
	coverage html

black:
	black .

black-check:
	black . --check

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

eslint:
	cd js && npx eslint .
