test:
	python -m pip install --upgrade pip
	pip install -r requirements.txt
	pip install coverage
	coverage run -m pytest