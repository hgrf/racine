doc: api-spec
	mv docs/module.mk ./

	# generate markdown documentation
	cd docs && handsdown \
		--branch master \
		--external `git config --get remote.origin.url` \
		--cleanup \
		--create-configs \
		--theme material \
		--name "Racine" \
		--output-path docsmd \
		../app \
		--exclude ../app/api

	#rm requirements.mkdocs.txt
	sed -i 's/requirements.mkdocs.txt/requirements.txt\n   - requirements: requirements-dev.txt/g' docs/.readthedocs.yml
	sed -i 's/mkdocs.yml/docs\/mkdocs.yml/g' docs/.readthedocs.yml
	cat patches/readthedocs.yml >> docs/.readthedocs.yml

	# replace main page of documentation
	cp README.md docs/docsmd/README.md

	# add image for README.md
	mkdir -p docs/docsmd/app/static/images
	cp app/static/images/racine.svg docs/docsmd/app/static/images/racine.svg

	# enable code copy in documentation
	sed -i 's/- content.code.annotate/- content.code.annotate\n    - content.code.copy/g' docs/mkdocs.yml

	# add API page
	mv swagger.json docs/docsmd/swagger.json
	cp patches/api.md docs/docsmd/API.md

	# convert to HTML documentation
	echo -n "\nplugins:\n  - render_swagger" >> docs/mkdocs.yml
	cd docs && python -m mkdocs build

	rm api.yaml
	mv docs/.readthedocs.yml .

	mv module.mk docs/

doc-serve:
	cd docs && python -m http.server 8000
