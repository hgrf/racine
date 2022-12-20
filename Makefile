test-dependencies:
	python -m pip install --upgrade pip
	pip install -r requirements.txt
	pip install coverage pytest

test:
	coverage run -m pytest