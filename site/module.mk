website-build-deps: site/.build-deps-done
site/.build-deps-done:
	cp app/static/images/racine.svg site/site/static/images/racine.svg
	cp app/static/images/racine-icon.svg site/site/static/images/racine-icon.svg
	cp app/static/images/racine-icon.png site/site/static/images/racine-icon.png

	# build website
	cd site && npm install
	cd site && npm install hugo-extended --save-dev

	touch site/.build-deps-done

website-build: website-build-deps
	cd site && npx hugo --cleanDestinationDir

	# add docker-compose.yml
	cp docker/docker-compose-dist.yml ./_site/docker-compose.yml

website-prepare-deploy: website
	# copy build to Racine
	rm -rf ./_site
	cp -r site/_site ./_site

	pre-commit uninstall
	git stash
	git checkout gh-pages
	mv docs/.gitignore docs.gitignore
	rm -rf docs
	mv _site docs
	mv docs.gitignore docs/.gitignore
	git add docs

website-serve:
	cd site && npx hugo server --port 9001 --disableFastRender --verbose