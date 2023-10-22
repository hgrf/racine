doc: api-spec
	mv docs/module.mk ./

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
	sed -i 's/requirements.mkdocs.txt/requirements.txt\n   - requirements: requirements-dev.txt/g' .readthedocs.yml
	sed -i 's/mkdocs.yml/docs\/mkdocs.yml/g' .readthedocs.yml
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

	rm api.yaml
	mv mkdocs.yml docs/

	mv module.mk docs/

doc-serve:
	cd docs && python -m http.server 8000
