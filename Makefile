install-dependencies:
	python -m pip install ${PIP_OPTIONS} --upgrade pip
	pip install ${PIP_OPTIONS} -r requirements-dev.txt
	pip install ${PIP_OPTIONS} -r requirements.txt

api-spec:
	python patches/generate-api-spec.py
	cat patches/api.yaml >> api.yaml

api-client: api-spec
	rm -rf js/src/api
	mkdir -p build
	wget https://repo1.maven.org/maven2/org/openapitools/openapi-generator-cli/6.2.1/openapi-generator-cli-6.2.1.jar \
		-O build/openapi-generator-cli.jar
	
	java -jar build/openapi-generator-cli.jar generate \
		-i api.yaml -g javascript -p modelPropertyNaming=original -o js/src/api

website:
	# clone bootstrap
	rm -rf build/bootstrap
	git clone -b v5.2.3 --depth 1 https://github.com/twbs/bootstrap.git build/bootstrap
	rm -rf build/bootstrap/.git

	rm -rf build/bootstrap/site/content/docs
	rm -rf build/bootstrap/site/static/docs
	rm build/bootstrap/site/.eslintrc.json
	rm build/bootstrap/site/static/CNAME
	rm build/bootstrap/site/layouts/partials/docs-versions.html

	cd build/bootstrap && npm install
	cd build/bootstrap && npm install hugo-extended --save-dev

	cp site/config.yml build/bootstrap/config.yml
	cp site/linkedin.svg build/bootstrap/site/layouts/partials/icons/linkedin.svg
	cp site/piggy-bank-fill.svg build/bootstrap/site/layouts/partials/icons/piggy-bank-fill.svg
	cp site/docs-navbar.html build/bootstrap/site/layouts/partials/docs-navbar.html
	cp site/favicons.html build/bootstrap/site/layouts/partials/favicons.html
	cp site/footer.html build/bootstrap/site/layouts/partials/footer.html
	cp site/header.html build/bootstrap/site/layouts/partials/header.html
	cp site/masthead.html build/bootstrap/site/layouts/partials/home/masthead.html
	cp site/masthead-followup.html \
		build/bootstrap/site/layouts/partials/home/masthead-followup.html
	mkdir -p build/bootstrap/site/static/images
	cp app/static/images/racine.svg build/bootstrap/site/static/images/racine.svg
	cp app/static/images/racine-icon.svg build/bootstrap/site/static/images/racine-icon.svg
	cp app/static/images/racine-icon.png build/bootstrap/site/static/images/racine-icon.png
	cp site/IMGP8279.JPG build/bootstrap/site/static/images/IMGP8279.JPG
	cp site/EB-FDP3_v3.jpeg build/bootstrap/site/static/images/EB-FDP3_v3.jpeg
	cp site/IMG_7415_portrait.jpg build/bootstrap/site/static/images/IMG_7415_portrait.jpg
	cp site/IMG_20230201_133822_575.jpg build/bootstrap/site/static/images/IMG_20230201_133822_575.jpg
	cp site/emmanuel_baudin.png build/bootstrap/site/static/images/emmanuel_baudin.png
	cp site/icons.html build/bootstrap/site/layouts/partials/icons.html
	cp site/scripts.html build/bootstrap/site/layouts/partials/scripts.html
	cp site/_navbar.scss build/bootstrap/site/assets/scss/_navbar.scss
	cp site/_variables.scss build/bootstrap/site/assets/scss/_variables.scss

	# build website
	cd build/bootstrap && npx hugo --cleanDestinationDir

	# copy build to Racine
	rm -rf ./_site
	cp -r build/bootstrap/_site ./_site

	# add docker-compose.yml
	cp docker/docker-compose-dist.yml ./_site/docker-compose.yml

website-prepare-deploy: website
	pre-commit uninstall
	git stash
	git checkout gh-pages
	mv docs/.gitignore docs.gitignore
	rm -rf docs
	mv _site docs
	mv docs.gitignore docs/.gitignore
	git add docs

hugo-serve:
	cd build/bootstrap && npx hugo server --port 9001 --disableFastRender --verbose

install-ckeditor:
	# clone CKEditor 4.9.2
	rm -rf /tmp/ckeditor4
	git clone -b 4.9.2 --depth 1 https://github.com/ckeditor/ckeditor4.git /tmp/ckeditor4

	# add scayt plugin
	git clone -b release.4.9.2.0 --depth 1 \
		https://github.com/WebSpellChecker/ckeditor-plugin-scayt.git \
		/tmp/ckeditor4/plugins/scayt
	cp patches/scayt.patch /tmp/ckeditor4/plugins/scayt/scayt.patch
	cd /tmp/ckeditor4/plugins/scayt && git apply scayt.patch
	rm /tmp/ckeditor4/plugins/scayt/scayt.patch

	# add wsc plugin
	git clone -b release.4.9.5 --depth 1 \
		https://github.com/WebSpellChecker/ckeditor-plugin-wsc.git \
		/tmp/ckeditor4/plugins/wsc

	# add pastefromexcel plugin
	git clone \
		https://github.com/devlog/pastefromexcel.git \
		/tmp/ckeditor4/plugins/pastefromexcel
	cd /tmp/ckeditor4/plugins/pastefromexcel && \
		git checkout 74c5b19d68c4d0f2a5e781e3d27208c5379d5195

	# add imagerotate plugin
	git clone \
		https://github.com/liias/imagerotate.git \
		/tmp/ckeditor4/plugins/imagerotate
	cd /tmp/ckeditor4/plugins/imagerotate && \
		git checkout f2ba8746bcf0b31df4791008f2bf37ba7e958aca

	# remove BOM from build.sh
	dos2unix /tmp/ckeditor4/dev/builder/build.sh

	# build CKEditor release
	cp patches/build-config.js /tmp/ckeditor4/dev/builder/build-config.js
	cd /tmp/ckeditor4 && \
		bash ./dev/builder/build.sh \
			-s --no-zip --no-tar --build-config build-config.js

	# java -jar /tmp/ckeditor4/dev/builder/ckbuilder/2.3.2/ckbuilder.jar \
	#	--build-skin --overwrite \
	#	/tmp/ckeditor4/skins/moono-lisa \
	#	/tmp/ckeditor4/dev/builder/release/ckeditor/skins/moono-lisa
	
	# apply patch to image plugin
	# c.f. https://github.com/hgrf/racine/commit/0cb962ec38ab3ea627bf2ed9f92d46f3ca2b27d2
	#      https://github.com/hgrf/racine/commit/7bebdfd730a61df0cdcbc04d9711e11ef3b80cbf
	#      https://github.com/hgrf/racine/commit/e98b8fa093778f0a1331f1d4b56619d669f9e8a5
	#      https://github.com/hgrf/racine/commit/cac9cf5bd1cba27551b3335998692a9ba072e29e
	#      https://github.com/hgrf/racine/commit/b2940d7d35fd2a725f88d394e815c1bc57f6d10f
	#      https://github.com/hgrf/racine/commit/276a495413d6654cad1695cd1ef33daa558f3fa7
	#      https://github.com/hgrf/racine/commit/3f33c7f58e41eec70f8749d756aaae5f5755a348
	#      https://github.com/hgrf/racine/commit/7791aa8db771323ed8a1997beb50ddc17583b460
	cp patches/image.patch /tmp/ckeditor4/plugins/image/plugin.patch
	cd /tmp/ckeditor4 && git apply plugins/image/plugin.patch
	rm /tmp/ckeditor4/plugins/image/plugin.patch

	# apply patch to imagerotate plugin
	# c.f. https://github.com/hgrf/racine/commit/627937daf81687278c8d339fa1bfaf0a1e71caa8
	#      https://github.com/hgrf/racine/commit/56471eaf168d4f34e930368f95e8b330b4bb8d90
	#      https://github.com/hgrf/racine/commit/109e8c57fbb0655245160cc42e0bc1d871c9dabd
	#      https://github.com/hgrf/racine/commit/e9af7953866a6f26fd30a96f3293f2be0d192ce3
	cp patches/imagerotate/plugin.patch /tmp/ckeditor4/plugins/imagerotate/plugin.patch
	cd /tmp/ckeditor4/plugins/imagerotate && git apply plugin.patch
	rm /tmp/ckeditor4/plugins/imagerotate/plugin.patch

	# apply patch to link plugin
	# c.f. https://github.com/hgrf/racine/commit/0cb962ec38ab3ea627bf2ed9f92d46f3ca2b27d2
	#      https://github.com/hgrf/racine/commit/7bebdfd730a61df0cdcbc04d9711e11ef3b80cbf
	#      https://github.com/hgrf/racine/commit/22e0ae16e74488dea63e59a69bb3d74aaac3b972
	#      https://github.com/hgrf/racine/commit/cac9cf5bd1cba27551b3335998692a9ba072e29e
	#      https://github.com/hgrf/racine/commit/b2940d7d35fd2a725f88d394e815c1bc57f6d10f
	#      https://github.com/hgrf/racine/commit/7791aa8db771323ed8a1997beb50ddc17583b460
	cp patches/link.patch /tmp/ckeditor4/plugins/link/plugin.patch
	cd /tmp/ckeditor4 && git apply plugins/link/plugin.patch
	rm /tmp/ckeditor4/plugins/link/plugin.patch

	# apply patch to save plugin
	# c.f. https://github.com/hgrf/racine/commit/e98b8fa093778f0a1331f1d4b56619d669f9e8a5
	#      https://github.com/hgrf/racine/commit/cac9cf5bd1cba27551b3335998692a9ba072e29e
	#      https://github.com/hgrf/racine/commit/0f6fe60cd646d7e95b0330b246ad7c7c1b968aae
	cp patches/save/plugin.patch /tmp/ckeditor4/plugins/save/plugin.patch
	cd /tmp/ckeditor4 && git apply plugins/save/plugin.patch
	rm /tmp/ckeditor4/plugins/save/plugin.patch

	# copy build to Racine
	rm -rf app/static/ckeditor
	cp -r /tmp/ckeditor4/dev/builder/release/ckeditor app/static/ckeditor

	# add unminified source of image plugin (dialog)
	cp app/static/ckeditor/plugins/image/dialogs/image.js \
		app/static/ckeditor/plugins/image/dialogs/image.js.old
	cp /tmp/ckeditor4/plugins/image/dialogs/image.js \
		app/static/ckeditor/plugins/image/dialogs/image.js

	# add unminified source of imagerotate plugin
	cp -r /tmp/ckeditor4/plugins/imagerotate \
		app/static/ckeditor/plugins/imagerotate

	# add unminified source of link plugin (dialog)
	cp app/static/ckeditor/plugins/link/dialogs/link.js \
		app/static/ckeditor/plugins/link/dialogs/link.js.old
	cp /tmp/ckeditor4/plugins/link/dialogs/link.js \
		app/static/ckeditor/plugins/link/dialogs/link.js

	# add unminified source of save plugin
	cp -r /tmp/ckeditor4/plugins/save app/static/ckeditor/plugins/save

	# add missing icons
	cp patches/save/icons/hidpi/closebtn.png \
		app/static/ckeditor/plugins/save/icons/hidpi/closebtn.png
	cp patches/save/icons/closebtn.png app/static/ckeditor/plugins/save/icons/closebtn.png
	cp patches/save/icons/loader.gif app/static/ckeditor/plugins/save/icons/loader.gif

	# add (superfluous) files
	cp /tmp/ckeditor4/plugins/pastefromexcel/.editorconfig \
		app/static/ckeditor/plugins/pastefromexcel/.editorconfig
	cp /tmp/ckeditor4/plugins/pastefromexcel/.gitignore \
		app/static/ckeditor/plugins/pastefromexcel/.gitignore
	cp /tmp/ckeditor4/plugins/pastefromexcel/.jscsrc \
		app/static/ckeditor/plugins/pastefromexcel/.jscsrc
	cp /tmp/ckeditor4/plugins/pastefromexcel/.jshintrc \
		app/static/ckeditor/plugins/pastefromexcel/.jshintrc
	mkdir app/static/ckeditor/plugins/pastefromexcel/tests
	cp /tmp/ckeditor4/plugins/pastefromexcel/tests/pastefromexcel.js \
		app/static/ckeditor/plugins/pastefromexcel/tests/pastefromexcel.js

	# install custom plugins
	cp -r patches/fb app/static/ckeditor/plugins/fb

	# apply various patches
	cp patches/README.md app/static/ckeditor/README.md
	cp patches/config.js app/static/ckeditor/config.js
	cp patches/build-config.js app/static/ckeditor/build-config.js
	cp patches/pastefromexcel.js app/static/ckeditor/plugins/pastefromexcel/tests/pastefromexcel.js
	cp patches/imagerotate/NOTES.md app/static/ckeditor/plugins/imagerotate/NOTES.md
	python patches/langorder.py
	python patches/timestamp.py

	# remove unneeded files
	rm -rf app/static/ckeditor/.github
	rm -rf app/static/ckeditor/samples
	rm -rf app/static/ckeditor/skins/kama
	rm -rf app/static/ckeditor/skins/moono
	rm app/static/ckeditor/lang/_translationstatus.txt
	rm app/static/ckeditor/plugins/imagerotate/README.md

	# replace strings
	sed -i 's/px!/px !/g' app/static/ckeditor/skins/moono-lisa/editor.css
	sed -i 's/:url/: url/g' app/static/ckeditor/skins/moono-lisa/editor.css
	sed -i 's/important}/important;}/g' app/static/ckeditor/skins/moono-lisa/editor.css
	sed -i 's/icon{/icon {/g' app/static/ckeditor/skins/moono-lisa/editor.css
	sed -i 's/cke_menubutton_icon {/cke_menubutton_icon{/g' app/static/ckeditor/skins/moono-lisa/editor.css

	# fix line endings
	find app/static/ckeditor -type f \
		\( \
			! -iname "CHANGES.md" \
			! -path "app/static/ckeditor/LICENSE.md" \
			! -iname "contents.css" \
			! -iname "styles.js" \
			! -iname "_translationstatus.txt" \
			! -path "app/static/ckeditor/plugins/scayt/*.md" \
			! -path "app/static/ckeditor/plugins/scayt/dialogs/toolbar.css" \
			! -path "app/static/ckeditor/plugins/wsc/*.md" \
			! -path "app/static/ckeditor/plugins/wsc/dialogs/*.html" \
			! -path "app/static/ckeditor/plugins/wsc/dialogs/wsc.css" \
			! -path "app/static/ckeditor/plugins/wsc/dialogs/wsc.js" \
		\) -print0 | xargs -0 dos2unix --keep-bom

	# clean up git repo
	rm -rf /tmp/ckeditor4

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

	cd js && npm install && npx rollup -c

	cp js/node_modules/bootstrap/dist/css/bootstrap.min.css app/static/css/bootstrap.min.css
	cp js/node_modules/bootstrap/dist/fonts/* app/static/fonts/

	cp js/node_modules/bootstrap-toc/dist/bootstrap-toc.min.css app/static/css/bootstrap-toc.min.css

	cp js/node_modules/lightbox2/dist/css/lightbox.css app/static/css/lightbox.css
	cp js/node_modules/lightbox2/dist/images/* app/static/images/

build: down
	docker compose -f docker/docker-compose.yml build web

run:
	docker compose -f docker/docker-compose.yml up web

run-no-docker:
	flask run --debug

build-dev: down
	docker compose -f docker/docker-compose.yml build web-dev

test-dev:
	docker compose -f docker/docker-compose.yml exec web-dev python -m pytest

run-dev:
	docker compose -f docker/docker-compose.yml up web-dev smb-dev & \
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

flake8-badge:
	printf " \
		\rimport os\n \
		\rfrom genbadge.utils_flake8 import get_flake8_badge, get_flake8_stats\n \
		\rbadge = get_flake8_badge(get_flake8_stats('./reports/flake8/flake8stats.txt'))\n \
		\rprint(f'{badge.right_txt}@{badge.color}')\n \
		\r\n" | python

eslint:
	cd js && npx eslint .

eslint-badge:
	OUTPUT=`cd js && npx eslint --max-warnings 0 .`; \
		if [ "$$?" -eq 0 ]; then \
			echo "pass@green"; \
		else \
			echo "$$OUTPUT" | \
				grep -E "problems? \(" | \
				(IFS='()' read _ SUMMARY; echo $$SUMMARY) | \
				(read ERRORS _ WARNINGS _; echo $$ERRORS C, $$WARNINGS W@\
					`if [ $$ERRORS -eq 0 ]; then echo orange; else echo red; fi`\
				); \
		fi

doc: api-spec
	# generate markdown documentation
	handsdown \
		--branch master \
		--external `git config --get remote.origin.url` \
		--cleanup \
		--create-configs \
		--theme material \
		--name "Racine" \
		--output-path docsmd \
		app \
		--exclude app/api

	rm requirements.mkdocs.txt
	sed -i 's/requirements.mkdocs.txt/requirements.txt/g' .readthedocs.yml
	cat patches/readthedocs.yml >> .readthedocs.yml

	# replace main page of documentation
	cp README.md docsmd/README.md

	# add image for README.md
	mkdir -p docsmd/app/static/images
	cp app/static/images/racine.svg docsmd/app/static/images/racine.svg

	# enable code copy in documentation
	sed -i 's/- content.code.annotate/- content.code.annotate\n    - content.code.copy/g' mkdocs.yml

	# add API page
	mv swagger.json docsmd/swagger.json
	cp patches/api.md docsmd/API.md

	# convert to HTML documentation
	echo -n "\nplugins:\n  - render_swagger" >> mkdocs.yml
	python -m mkdocs build

doc-serve:
	cd docs && python -m http.server 8000
