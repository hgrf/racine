RACINE_VERSION := $(shell							\
	while IFS=, read key value;						\
		do export $$key=$$value; 					\
	done < version.csv && echo $$RACINE_VERSION		\
)
RACINE_API_VERSION := $(shell						\
	while IFS=, read key value;						\
		do export $$key=$$value;					\
	done < version.csv && echo $$RACINE_API_VERSION	\
)

-include .github/workflows/module.mk
-include app/static/module.mk
-include js/module.mk
-include desktop/module.mk
-include docker/module.mk
-include docs/module.mk
-include site/module.mk

.PHONY: version
version:
	@echo ${RACINE_VERSION}

.PHONY: api-version
api-version:
	@echo ${RACINE_API_VERSION}

app-deps: build/.app_deps_done
build/.app_deps_done: requirements.txt
	python -m pip install ${PIP_OPTIONS} --upgrade pip
	pip install ${PIP_OPTIONS} -r requirements.txt
	mkdir -p build
	touch build/.app_deps_done

app-dev-deps: build/.app_dev_deps_done
build/.app_dev_deps_done: requirements-dev.txt
	pip install ${PIP_OPTIONS} -r requirements-dev.txt
	mkdir -p build
	touch build/.app_dev_deps_done

run-no-docker:
	flask run --debug

.PHONY: test
test:
	coverage run -m pytest

.PHONY: coverage-report
coverage-report: test
	coverage html

.PHONY: black
black:
	black .

.PHONY: black-check
black-check:
	black . --check

.PHONY: flake8
FLAKE_EXTRA_ARGS ?=	--exit-zero
flake8:
	# stop the build if there are Python syntax errors or undefined names
	flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics

	# make sure flake8 report folder exists
	mkdir -p ./reports/flake8

	# make sure no previous report exists (otherwise flake8 will append to it)
	rm ./reports/flake8/flake8stats.txt || true

	# run flake8 and generate report
	flake8 . \
		--format=html --htmldir ./reports/flake8/ \
		--tee --output-file ./reports/flake8/flake8stats.txt \
		${FLAKE_EXTRA_ARGS}

.PHONY: flake8-check
flake8-check:
	FLAKE_EXTRA_ARGS= make flake8

.PHONY: eslint
eslint:
	cd js && npx eslint --max-warnings 0 .
