.PHONY: api-spec
api-spec:
	python patches/generate-api-spec.py

build/openapi-generator-cli.jar:
	mkdir -p build
	wget https://repo1.maven.org/maven2/org/openapitools/openapi-generator-cli/6.2.1/openapi-generator-cli-6.2.1.jar \
		-O build/openapi-generator-cli.jar

.PHONY: api-client
api-client: api-spec build/openapi-generator-cli.jar
	rm -rf js/src/api	
	java -jar build/openapi-generator-cli.jar generate \
		-i docs/api.yaml -g javascript -p modelPropertyNaming=original -o js/src/api

	java -jar build/openapi-generator-cli.jar generate \
		-i docs/api.yaml -g dart -p modelPropertyNaming=original -o build/openapi
	# TODO: what about intl dependency?

js-deps: build/.js_deps_done
build/.js_deps_done:
	rm -rf app/static/mathjax

	git clone -b 2.7.1 --depth 1 \
		https://github.com/mathjax/MathJax.git \
		app/static/mathjax

	rm -rf app/static/mathjax/.git

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
		https://raw.githubusercontent.com/NicolasCARPi/jquery_jeditable/1.7.3/jquery.jeditable.js
	# c.f. https://github.com/hgrf/racine/commit/89d8b57e795ccfbeb73dc18faecc1d0016a8a008#diff-5f8e3a2bd35e7f0079090b176e06d0568d5c8e4468c0febbfa61014d72b16246
	git apply patches/jquery.jeditable.patch

	cd js && npm install

	touch build/.js_deps_done

js-assets: build/.js_assets_done build/.js_deps_done
build/.js_assets_done:
	mkdir -p app/static/fonts
	mkdir -p app/static/css/fonts
	mkdir -p app/static/webfonts

	cp js/node_modules/bootstrap/dist/css/bootstrap.min.css app/static/css/bootstrap.min.css
	cp js/node_modules/bootstrap/dist/fonts/* app/static/fonts/

	cp js/node_modules/bootstrap-icons/font/bootstrap-icons.css app/static/css/bootstrap-icons.css
	cp js/node_modules/bootstrap-icons/font/fonts/* app/static/css/fonts/

	cp js/node_modules/@fortawesome/fontawesome-free/css/fontawesome.min.css app/static/css/fontawesome.min.css
	cp js/node_modules/@fortawesome/fontawesome-free/css/regular.min.css app/static/css/regular.min.css
	cp js/node_modules/@fortawesome/fontawesome-free/css/solid.min.css app/static/css/solid.min.css
	cp js/node_modules/@fortawesome/fontawesome-free/css/brands.min.css app/static/css/brands.min.css
	cp js/node_modules/@fortawesome/fontawesome-free/webfonts/* app/static/webfonts/

	cp js/node_modules/tocbot/dist/tocbot.css app/static/css/tocbot.css

	cp js/node_modules/lightbox2/dist/css/lightbox.css app/static/css/lightbox.css
	cp js/node_modules/lightbox2/dist/images/* app/static/images/

	touch build/.js_assets_done

js-version:
	cd js && npm version --allow-same-version ${RACINE_VERSION}
	cd desktop && npm version --allow-same-version ${RACINE_VERSION}

.PHONY: js-build
js-build: js-deps js-assets api-client
	cd js && npx rollup -c
