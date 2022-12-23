install-dependencies:
	python -m pip install --upgrade pip
	pip install -r requirements.txt
	pip install -r requirements-dev.txt

test:
	coverage run -m pytest

coverage-report: test
	coverage html

black:
	black app --line-length=100 --check

flake8:
	# stop the build if there are Python syntax errors or undefined names
	flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
	# exit-zero treats all errors as warnings. The GitHub editor is 127 chars wide
	flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics

doc:
	# Generate documentation that points to main branch
	# do not use custom output location, as `GitHub Pages`
	# works only with `docs` directory
	handsdown --external `git config --get remote.origin.url` --create-configs app --theme material -n "Mercury Sample Manager" -o docsmd
	# generate html files to docs folder
	python -m mkdocs build