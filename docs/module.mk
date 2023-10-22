doc: api-spec
	# generate markdown documentation
	cd docs && handsdown \
		--branch master \
		--external `git config --get remote.origin.url` \
		--cleanup \
		--create-configs \
		--theme material \
		--name "Racine" \
		--input-path $(PWD) \
		--output-path $(PWD)/docs/markdown \
		app \
		--exclude app/api

	sed -i 's/requirements.mkdocs.txt/requirements.txt\n   - requirements: requirements-dev.txt/g' docs/.readthedocs.yml
	sed -i 's/mkdocs.yml/docs\/mkdocs.yml/g' docs/.readthedocs.yml
	cat patches/readthedocs.yml >> docs/.readthedocs.yml

	# replace main page of documentation
	cp README.md docs/markdown/README.md

	# add image for README.md
	mkdir -p docs/markdown/app/static/images
	cp app/static/images/racine.svg docs/markdown/app/static/images/racine.svg

	# enable code copy in documentation
	sed -i 's/- content.code.annotate/- content.code.annotate\n    - content.code.copy/g' docs/mkdocs.yml

	# add API page
	mv swagger.json docs/markdown/swagger.json
	cp patches/api.md docs/markdown/API.md

	# convert to HTML documentation
	sed -i 's/site_dir: \"docs\"/site_dir: \"html\"/g' docs/mkdocs.yml
	sed -i 's/docs_dir: \"docs\/markdown\"/docs_dir: \"markdown\"/g' docs/mkdocs.yml
	echo -n "\nplugins:\n  - render_swagger" >> docs/mkdocs.yml
	cd docs && python -m mkdocs build

	mv docs/.readthedocs.yml .

doc-serve:
	cd docs/html && python -m http.server 8000
